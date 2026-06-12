#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""AuditReady — AWS evidence puller.

Collects SOC 2 evidence from CloudTrail, IAM, GuardDuty, Security Hub and
AWS Config into one CSV per service inside evidence-output/YYYY-MM-DD/aws/.

Credentials: BYOK via standard AWS env vars (see scripts/.env.example).
Read-only: every call is a List*/Get*/Describe* operation.

Usage:
    set -a; source .env; set +a
    python3 scripts/aws-evidence-puller.py [--days 90]
"""

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

try:
    import boto3
    from botocore.config import Config
except ImportError:
    sys.exit("boto3 is required: pip install -r scripts/requirements.txt")
try:
    from tqdm import tqdm
except ImportError:
    sys.exit("tqdm is required: pip install -r scripts/requirements.txt")

from _common import CallCounter, evidence_dir, require_env, setup_logging, with_retries, write_csv

LOG = setup_logging("aws-evidence")
COUNTER = CallCounter()
MAX_WORKERS = 5  # concurrency cap
BOTO_CFG = Config(retries={"max_attempts": 8, "mode": "adaptive"})


def session():
    require_env("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_DEFAULT_REGION")
    return boto3.session.Session()


def pull_cloudtrail(sess, days: int) -> list[dict]:
    """Management events: who did what, when — the core CC7.2/CC8.1 evidence."""
    ct = sess.client("cloudtrail", config=BOTO_CFG)
    start = datetime.now(timezone.utc) - timedelta(days=days)
    rows, token = [], None
    while True:
        kwargs = {"StartTime": start, "MaxResults": 50}
        if token:
            kwargs["NextToken"] = token
        resp = with_retries(lambda: ct.lookup_events(**kwargs), LOG)
        COUNTER.tick()
        for ev in resp.get("Events", []):
            rows.append({
                "event_time": str(ev.get("EventTime", "")),
                "event_name": ev.get("EventName", ""),
                "username": ev.get("Username", ""),
                "event_source": ev.get("EventSource", ""),
                "resources": ";".join(r.get("ResourceName", "") for r in ev.get("Resources", [])),
                "event_id": ev.get("EventId", ""),
            })
        token = resp.get("NextToken")
        if not token or len(rows) >= 10_000:  # safety cap for huge accounts
            break
    return rows


def pull_iam(sess, days: int) -> list[dict]:
    """User inventory + credential report fields (MFA, key age, last used)."""
    iam = sess.client("iam", config=BOTO_CFG)
    rows = []
    paginator = iam.get_paginator("list_users")
    for page in paginator.paginate():
        COUNTER.tick()
        for user in page["Users"]:
            name = user["UserName"]
            mfa = with_retries(lambda n=name: iam.list_mfa_devices(UserName=n), LOG)
            keys = with_retries(lambda n=name: iam.list_access_keys(UserName=n), LOG)
            COUNTER.tick(2)
            rows.append({
                "user": name,
                "created": str(user.get("CreateDate", "")),
                "password_last_used": str(user.get("PasswordLastUsed", "never")),
                "mfa_enabled": bool(mfa["MFADevices"]),
                "access_keys": len(keys["AccessKeyMetadata"]),
                "oldest_key_created": str(min(
                    (k["CreateDate"] for k in keys["AccessKeyMetadata"]), default="",
                )),
            })
    return rows


def pull_guardduty(sess, days: int) -> list[dict]:
    """GuardDuty findings — vulnerability/threat management evidence (CC7.1)."""
    gd = sess.client("guardduty", config=BOTO_CFG)
    rows = []
    dets = with_retries(lambda: gd.list_detectors(), LOG)
    COUNTER.tick()
    for det in dets.get("DetectorIds", []):
        token = None
        while True:
            kwargs = {"DetectorId": det, "MaxResults": 50,
                      "FindingCriteria": {"Criterion": {"updatedAt": {
                          "Gte": int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp() * 1000)}}}}
            if token:
                kwargs["NextToken"] = token
            ids = with_retries(lambda k=kwargs: gd.list_findings(**k), LOG)
            COUNTER.tick()
            if ids.get("FindingIds"):
                detail = with_retries(
                    lambda d=det, i=ids["FindingIds"]: gd.get_findings(DetectorId=d, FindingIds=i), LOG)
                COUNTER.tick()
                for f in detail.get("Findings", []):
                    rows.append({
                        "id": f.get("Id", ""), "type": f.get("Type", ""),
                        "severity": f.get("Severity", ""), "title": f.get("Title", ""),
                        "resource": f.get("Resource", {}).get("ResourceType", ""),
                        "first_seen": f.get("CreatedAt", ""), "last_seen": f.get("UpdatedAt", ""),
                    })
            token = ids.get("NextToken")
            if not token:
                break
    return rows


def pull_securityhub(sess, days: int) -> list[dict]:
    """Security Hub findings — consolidated posture evidence."""
    sh = sess.client("securityhub", config=BOTO_CFG)
    rows, token = [], None
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    while True:
        kwargs = {"MaxResults": 100,
                  "Filters": {"UpdatedAt": [{"Start": cutoff,
                                             "End": datetime.now(timezone.utc).isoformat()}]}}
        if token:
            kwargs["NextToken"] = token
        try:
            resp = with_retries(lambda k=kwargs: sh.get_findings(**k), LOG)
        except Exception as exc:  # Security Hub not enabled is a normal state
            LOG.warning(f"Security Hub unavailable ({exc}); skipping")
            return rows
        COUNTER.tick()
        for f in resp.get("Findings", []):
            rows.append({
                "id": f.get("Id", ""), "title": f.get("Title", ""),
                "severity": f.get("Severity", {}).get("Label", ""),
                "status": f.get("Workflow", {}).get("Status", ""),
                "resource": ";".join(r.get("Id", "") for r in f.get("Resources", [])),
                "updated": f.get("UpdatedAt", ""),
            })
        token = resp.get("NextToken")
        if not token or len(rows) >= 10_000:
            break
    return rows


def pull_config(sess, days: int) -> list[dict]:
    """AWS Config compliance summary per rule — change-management evidence."""
    cfg = sess.client("config", config=BOTO_CFG)
    rows, token = [], None
    while True:
        kwargs = {}
        if token:
            kwargs["NextToken"] = token
        try:
            resp = with_retries(lambda k=kwargs: cfg.describe_compliance_by_config_rule(**k), LOG)
        except Exception as exc:
            LOG.warning(f"AWS Config unavailable ({exc}); skipping")
            return rows
        COUNTER.tick()
        for item in resp.get("ComplianceByConfigRules", []):
            comp = item.get("Compliance", {})
            rows.append({
                "rule": item.get("ConfigRuleName", ""),
                "compliance": comp.get("ComplianceType", ""),
                "capped_count": comp.get("ComplianceContributorCount", {}).get("CappedCount", ""),
            })
        token = resp.get("NextToken")
        if not token:
            break
    return rows


PULLERS = {
    "cloudtrail": pull_cloudtrail,
    "iam": pull_iam,
    "guardduty": pull_guardduty,
    "securityhub": pull_securityhub,
    "config": pull_config,
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=90, help="lookback window (default 90)")
    args = parser.parse_args()

    sess = session()
    outdir = evidence_dir("aws")
    LOG.info(f"pulling {len(PULLERS)} services, {args.days}-day window, workers={MAX_WORKERS}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(fn, sess, args.days): name for name, fn in PULLERS.items()}
        for fut in tqdm(as_completed(futures), total=len(futures), desc="AWS evidence"):
            name = futures[fut]
            try:
                write_csv(outdir / f"{name}.csv", fut.result(), LOG)
            except Exception:
                LOG.exception(f"{name} failed; other services continue")

    # CloudTrail LookupEvents is $0 for the last 90 days of management events;
    # IAM/GuardDuty/Security Hub/Config read APIs are not billed per call.
    COUNTER.report("AWS (read-only APIs)")
    print(f"Evidence written to {outdir}")


if __name__ == "__main__":
    main()

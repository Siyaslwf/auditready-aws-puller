# Sample output

This is what `python aws-evidence-puller.py` generates against a real (anonymized) AWS account.

## Folder structure

```
evidence-bundle-2026-06-12/
├── MANIFEST.txt              ← SHA-256 hashes + run metadata
├── README.txt                ← Per-CSV interpretation guide for your auditor
├── cloudtrail/
│   ├── api-call-events.csv   (12,847 rows, 90-day window)
│   ├── data-events.csv       (3,021 rows)
│   └── trail-configuration.csv
├── iam/
│   ├── users.csv             (14 rows)
│   ├── access-keys.csv       (22 rows)
│   ├── mfa-devices.csv       (14 rows)
│   ├── password-policy.csv   (1 row)
│   └── policy-attachments.csv (87 rows)
├── guardduty/
│   ├── detectors.csv         (5 rows = 5 regions)
│   ├── findings.csv          (3 rows = low-severity informational)
│   └── coverage.csv          (10 rows)
├── securityhub/
│   ├── enabled-standards.csv (3 rows: CIS, AWS Foundational, PCI)
│   ├── compliance-status.csv (164 rows = controls)
│   └── findings-summary.csv  (1 row)
└── config/
    ├── configuration-recorder.csv
    └── compliance-summary.csv
```

## MANIFEST.txt example

```
AuditReady AWS Evidence Bundle
Generated: 2026-06-12T14:32:11Z
Lookback days: 90
Account ID: 1**********4
Primary region: us-east-1
Regions scanned: us-east-1, us-west-2, eu-west-1, eu-central-1, ap-southeast-1
Total API calls: 847
Estimated cost: $0.00 (all calls free-tier eligible)
Runtime: 1m 52s

SHA-256 hashes:
cloudtrail/api-call-events.csv         8d2f4a1b3c5e7d9f0a2b4c6d8e0f2a4b6c8d0e2f4a6b8c0d2e4f6a8b0c2d4e6f
cloudtrail/data-events.csv             6e8a0c2d4f6b8d0c2e4f6a8b0c2d4e6f8a0c2d4e6f8a0c2d4e6f8a0c2d4e6f8a
[... continues for all 17 files ...]
```

## Sample CSV header (iam/users.csv)

```csv
pulled_at_utc,user_name,user_id,arn,create_date,password_last_used,user_path
2026-06-12T14:32:11Z,alice@example.com,AIDAXXXXXXXXXXXXXXXXX,arn:aws:iam::1**********4:user/alice@example.com,2024-03-15T09:12:43Z,2026-06-11T17:08:22Z,/
2026-06-12T14:32:11Z,bob-cicd-deploy,AIDAYYYYYYYYYYYYYYYYY,arn:aws:iam::1**********4:user/bob-cicd-deploy,2023-11-02T14:30:01Z,never,/service/
[... continues ...]
```

## Sample CSV header (cloudtrail/api-call-events.csv)

```csv
pulled_at_utc,event_time,event_name,event_source,user_identity_type,user_name,source_ip,read_only,resources
2026-06-12T14:32:11Z,2026-06-12T13:14:22Z,AssumeRole,sts.amazonaws.com,Role,prod-deploy-role,10.0.1.42,false,arn:aws:iam::1**********4:role/prod-deploy-role
2026-06-12T14:32:11Z,2026-06-12T13:14:23Z,DescribeInstances,ec2.amazonaws.com,AssumedRole,prod-deploy-role,10.0.1.42,true,
[... continues ...]
```

## What auditors actually look at

Most CPA firms request these specific columns:

| Column | Why they care |
|---|---|
| `pulled_at_utc` | Evidence freshness — must be within the audit period |
| `event_time` | Verifies your monitoring window covers the audit period |
| `user_identity_type` | Confirms no root account usage |
| `mfa_enabled` (iam/mfa-devices.csv) | SOC 2 CC6.1 — access controls |
| `password_last_used` (iam/users.csv) | Identifies dormant accounts |
| `read_only` (cloudtrail) | Helps trace privileged actions |

The README.txt inside each bundle explains all of this for the auditor in plain English so they don't have to ask follow-up questions.

---

## Want continuous evidence collection?

The [full AuditReady toolkit](https://siyas.gumroad.com/l/auditready) includes a GitHub Actions workflow that runs this script weekly, commits the bundle to a private S3 bucket, and notifies your auditor via email. That's what makes SOC 2 Type II realistic for a 1-person engineering team.

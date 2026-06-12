<!-- SEO keywords: SOC 2 AWS, SOC 2 evidence collection, SOC 2 audit prep, soc2 automation, CloudTrail audit script, IAM evidence puller, GuardDuty SOC 2, vanta alternative, drata alternative, open source SOC 2, compliance as code Python -->

# AuditReady — AWS SOC 2 Evidence Puller

[![License: MIT](https://img.shields.io/badge/license-MIT-22C55E.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-3776AB.svg?logo=python&logoColor=fff)](https://www.python.org/downloads/)
[![CI](https://github.com/Siyaslwf/auditready-aws-puller/actions/workflows/ci.yml/badge.svg)](https://github.com/Siyaslwf/auditready-aws-puller/actions/workflows/ci.yml)
[![SOC 2 Ready](https://img.shields.io/badge/SOC_2-Type_I_%26_II-3B82F6)](https://siyas.gumroad.com/l/auditready)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-22C55E.svg)](CONTRIBUTING.md)
[![AuditReady Full Toolkit](https://img.shields.io/badge/Full_Toolkit-AuditReady-D97757?style=flat)](https://siyas.gumroad.com/l/auditready)

> **Open-source SOC 2 evidence collection for AWS.** Pulls CloudTrail, IAM, GuardDuty, Security Hub, and AWS Config into a single dated CSV bundle your auditor accepts. Built for startups who can't afford Vanta ($24K/yr) or Drata ($14K/yr) but still need to close enterprise deals.

---

## 🚀 Why this exists

Most early-stage SaaS startups stall at the SOC 2 deal-blocker. Enterprise prospects ask for the report. Vanta and Drata charge $14K–$24K/year. Big-4 consultants charge $50K+. Free template kits (Comply, Secureframe templates) skip the part that actually matters: **pulling the evidence**.

This script pulls SOC 2-relevant evidence from your AWS account in <2 minutes, with read-only credentials, and outputs a structured CSV bundle ready to email your auditor.

It's 1 of 4 evidence-puller scripts in **[AuditReady](https://siyas.gumroad.com/l/auditready)** — the full $297 toolkit also covers Vercel + Supabase pullers, 27 stack-tuned SOC 2 policies, 200-item readiness checklist, 90-day sprint plan, and SOC 2 ↔ ISO 27001 ↔ GDPR ↔ NIS2 crosswalk.

---

## ⚡ Quick start (3 commands)

```bash
pip install -r requirements.txt
cp .env.example .env  # then add your AWS read-only credentials
python aws-evidence-puller.py
```

Output lands in `./evidence-bundle-YYYY-MM-DD/` ready to send to your auditor.

---

## 📋 What you get (sample output)

The script generates this folder structure:

```
evidence-bundle-2026-06-12/
├── cloudtrail/
│   ├── api-call-events.csv           ← 90 days of management events
│   ├── data-events.csv                ← S3 + Lambda data plane (if logged)
│   └── trail-configuration.csv        ← Trail settings + S3 destination
├── iam/
│   ├── users.csv                      ← All IAM users + creation dates
│   ├── access-keys.csv                ← Key status + last-used timestamps
│   ├── mfa-devices.csv                ← MFA enforcement per user
│   ├── password-policy.csv            ← Account password policy
│   └── policy-attachments.csv         ← User-to-policy + role-to-policy
├── guardduty/
│   ├── detectors.csv                  ← Active detectors per region
│   ├── findings.csv                   ← Last 90 days of findings
│   └── coverage.csv                   ← S3 + EKS coverage status
├── securityhub/
│   ├── enabled-standards.csv          ← CIS / PCI / NIST / etc.
│   ├── compliance-status.csv          ← Pass/fail per control
│   └── findings-summary.csv           ← Critical/high/medium counts
├── config/
│   ├── configuration-recorder.csv     ← Recorder status + scope
│   └── compliance-summary.csv         ← Rule pass/fail
├── MANIFEST.txt                       ← File list + SHA-256 hashes + run timestamp
└── README.txt                         ← How to interpret each CSV
```

Every CSV has a `pulled_at_utc` column for audit traceability. See [examples/SAMPLE_OUTPUT.md](examples/SAMPLE_OUTPUT.md) for sample rows.

---

## 🔐 Required AWS IAM permissions

This script needs **read-only access** to 6 services. **Never run it with admin credentials.**

Create an IAM user, attach this minimum policy (also at [docs/iam-policy.json](docs/iam-policy.json)), generate access keys, paste into `.env`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AuditReadyReadOnly",
      "Effect": "Allow",
      "Action": [
        "cloudtrail:DescribeTrails",
        "cloudtrail:LookupEvents",
        "cloudtrail:GetTrailStatus",
        "iam:ListUsers",
        "iam:ListAccessKeys",
        "iam:GetAccessKeyLastUsed",
        "iam:ListMFADevices",
        "iam:GetAccountPasswordPolicy",
        "iam:ListAttachedUserPolicies",
        "iam:ListAttachedRolePolicies",
        "guardduty:ListDetectors",
        "guardduty:ListFindings",
        "guardduty:GetCoverageStatistics",
        "securityhub:DescribeStandards",
        "securityhub:GetEnabledStandards",
        "securityhub:GetFindings",
        "config:DescribeConfigurationRecorders",
        "config:DescribeComplianceByConfigRule"
      ],
      "Resource": "*"
    }
  ]
}
```

Even better: assume a read-only role from a separate audit account. The README in the full [AuditReady toolkit](https://siyas.gumroad.com/l/auditready) walks through both patterns.

---

## ⚙️ Configure

Edit `.env`:

```bash
AWS_ACCESS_KEY_ID=AKIAxxxxxxxxxxxxxxxx
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_REGION=us-east-1                       # primary region; script also scans all enabled regions
EVIDENCE_OUTPUT_DIR=./evidence-bundle
LOOKBACK_DAYS=90                           # CloudTrail event window (max 90)
CONCURRENCY=5                              # parallel API workers
```

---

## 📊 AuditReady vs SOC 2 alternatives

| | This repo | [AuditReady full kit](https://siyas.gumroad.com/l/auditready) | Vanta | Drata | Big-4 consultancy |
|---|---|---|---|---|---|
| **Price** | Free | $297 once | $24K/yr | $14K/yr | $50K–$200K |
| **AWS evidence puller** | ✅ | ✅ | ✅ | ✅ | manual |
| **Vercel evidence puller** | — | ✅ | — | — | manual |
| **Supabase evidence puller** | — | ✅ | — | — | manual |
| **27 stack-tuned policies** | — | ✅ | partial | partial | bespoke |
| **200-item readiness checklist** | — | ✅ | dashboard only | dashboard only | spreadsheet |
| **90-day sprint plan** | — | ✅ | — | — | timeline doc |
| **SOC 2 ↔ ISO 27001 ↔ GDPR ↔ NIS2 crosswalk** | — | ✅ | — | — | — |
| **Open source code** | ✅ MIT | partial | — | — | — |
| **Time to first audit-ready bundle** | 5 min | 30 min | 4–6 weeks | 4–6 weeks | 12+ weeks |

If you need just AWS evidence, this script is enough. If you're building a full SOC 2 program from zero, **[get AuditReady](https://siyas.gumroad.com/l/auditready)**.

---

## ❓ FAQ

### Does this give me a SOC 2 report?
No. SOC 2 reports are issued by a licensed CPA firm after a Type I or Type II audit. This script pulls the **evidence** your CPA will ask you for. Skipping the script means scrambling for screenshots the week of your audit.

### Can I use this for SOC 2 Type II?
Yes. Run it weekly (cron + GitHub Actions example in the [full toolkit](https://siyas.gumroad.com/l/auditready)) so you have continuous-period evidence rather than point-in-time.

### What about ISO 27001 / GDPR / NIS2?
The evidence overlaps ~70%. The crosswalk in the full toolkit maps each AWS evidence item to ISO 27001 Annex A, GDPR Art. 32, and NIS2 Art. 21.

### Does it modify my AWS account?
No. **Read-only.** Verify by attaching the IAM policy above — it has zero write actions.

### Will it work with AWS Organizations / multi-account?
Yes. Set `ASSUMED_ROLE_ARN` in `.env` and the script assumes that role per account. Full multi-account walkthrough in the toolkit.

### How does this compare to AWS Audit Manager?
Audit Manager is good but expensive (~$1/assessment + storage) and assumes you already know which evidence to pull. This script is opinionated about the 17 SOC 2 evidence sources auditors actually request.

### Can I customize what gets pulled?
Yes — edit `aws-evidence-puller.py`. PRs welcome. For pre-built customizations (industry-specific evidence, GDPR variants), see the full toolkit.

### How often should I run it?
- Pre-audit: once
- SOC 2 Type II: weekly via cron
- Continuous monitoring: daily via GitHub Actions ([example workflow in the toolkit](https://siyas.gumroad.com/l/auditready))

### Is the script audit-firm-tested?
Output format mirrors what Big-4 + boutique CPA firms ask for. Specific firm walkthroughs included in the full toolkit's Pro tier.

### How do I support this project?
- ⭐ Star this repo
- 🐛 Open issues for bugs / feature ideas
- 💬 Join [Discussions](https://github.com/Siyaslwf/auditready-aws-puller/discussions)
- 💰 [Buy the full toolkit](https://siyas.gumroad.com/l/auditready) — directly funds maintenance

---

## 🗺️ Roadmap

- [x] v0.1.0 — AWS evidence puller (this release)
- [ ] v0.2.0 — Multi-account via AWS Organizations
- [ ] v0.3.0 — GitHub Actions example workflow
- [ ] v0.4.0 — JSON output mode for SIEM ingest
- [ ] v1.0.0 — Production-stable, semver guarantees

Want a feature? Open an issue or [book a call](https://cal.com/siyas/auditready-walkthrough).

---

## 📚 Related projects

- **[AuditReady full toolkit](https://siyas.gumroad.com/l/auditready)** — 27 policies × 3 stacks + Vercel + Supabase pullers + checklist + sprint + crosswalk
- **[StrongDM Comply](https://github.com/strongdm/comply)** — Apache-2.0 policy backbone that AuditReady's full toolkit is derived from

---

## 🔒 Security

Found a vulnerability? Please read [SECURITY.md](SECURITY.md) for responsible-disclosure policy. Don't open public issues for security bugs.

---

## 🤝 Contributing

PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Especially looking for:
- Additional AWS service pullers (KMS, VPC Flow Logs, WAF)
- Multi-region edge cases
- Output format variants (Parquet, Avro)

---

## 📜 License

[MIT](LICENSE) — free for commercial and private use.

---

## 💬 Stay in touch

- 📦 **[AuditReady on Gumroad](https://siyas.gumroad.com/l/auditready)** — the full $297 toolkit
- 🗓️ **[Book a free 15-min walkthrough](https://cal.com/siyas/auditready-walkthrough)** — SOC 2 readiness chat, no pitch
- 💬 **[GitHub Discussions](https://github.com/Siyaslwf/auditready-aws-puller/discussions)** — public Q&A
- 👤 **[github.com/Siyaslwf](https://github.com/Siyaslwf)** — other open-source compliance tools

---

<sub>Built by [@Siyaslwf](https://github.com/Siyaslwf). ⭐ Star this repo if it saved you a Vanta subscription.</sub>

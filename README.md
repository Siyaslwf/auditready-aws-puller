# AuditReady AWS Evidence Puller

Open-source SOC 2 evidence puller for AWS. Pulls CloudTrail, IAM, GuardDuty,
Security Hub, and Config into a dated CSV bundle ready for your auditor.

## Install

    pip install -r requirements.txt

## Configure

    cp .env.example .env
    # Edit .env with your AWS credentials (read-only IAM role recommended)

## Run

    python aws-evidence-puller.py

## Part of AuditReady

This is 1 of 4 evidence-puller scripts in [AuditReady](https://siyas.gumroad.com/l/auditready).
The full toolkit includes Vercel + Supabase pullers, 27 stack-tuned SOC 2 policies
(AWS+Vercel+Supabase / Azure+Next.js / GCP+Firebase), 200-item checklist, 90-day
sprint, and SOC 2 ↔ ISO 27001 ↔ GDPR ↔ NIS2 crosswalk.

[Book a free 15-min walkthrough](https://cal.com/siyas/auditready-walkthrough) · [github.com/Siyaslwf](https://github.com/Siyaslwf)

## License

MIT.

# Changelog

All notable changes to this project are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Planned
- Multi-account via AWS Organizations
- GitHub Actions example workflow for continuous evidence collection
- JSON output mode for SIEM ingest
- KMS key rotation evidence
- VPC Flow Logs evidence

## [0.1.0] — 2026-06-12

### Added
- Initial public release
- CloudTrail evidence puller (90-day lookback, management + data events)
- IAM evidence puller (users, access keys, MFA, password policy, attached policies)
- GuardDuty evidence puller (detectors, findings, coverage)
- Security Hub evidence puller (standards, compliance, findings)
- AWS Config evidence puller (recorders, compliance summary)
- MANIFEST.txt with SHA-256 hashes per output file
- Read-only IAM policy template (zero write actions)
- BYOK (Bring Your Own Keys) via `.env`
- Multi-region scanning with configurable concurrency
- Cost-transparent: prints API call count at end of run

### Security
- All operations strictly read-only
- No telemetry / phone-home behavior
- Credentials never logged
- Output files contain no credentials

[Unreleased]: https://github.com/Siyaslwf/auditready-aws-puller/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Siyaslwf/auditready-aws-puller/releases/tag/v0.1.0

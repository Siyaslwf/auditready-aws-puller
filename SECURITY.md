# Security Policy

## Supported versions

The latest `main` branch is supported. Pre-v1.0.0 we don't backport fixes; please upgrade.

| Version | Supported |
|---------|-----------|
| Latest `main` | ✅ |
| < v1.0.0 (pre-stable) | ❌ |

## Reporting a vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Instead, email **[email protected]** with subject line: `[SECURITY] auditready-aws-puller — <short description>`.

Include:
- Description of the vulnerability
- Steps to reproduce
- Affected versions / commits
- Suggested fix (if known)
- Your name + handle if you want credit

I'll acknowledge within 48 hours. Critical vulnerabilities will be patched and disclosed within 7 days; lower-severity within 30 days.

## Scope

In scope:
- Code in this repository (`aws-evidence-puller.py`, `_common.py`)
- README / docs containing executable commands or IAM policies
- The `requirements.txt` pinned dependency tree (we don't ship binaries)

Out of scope:
- AWS itself or AWS API behavior
- Your own AWS account misconfigurations
- Issues in the [full AuditReady toolkit](https://siyas.gumroad.com/l/auditready) (report via the buyer-facing email)
- Social engineering / physical attacks

## Disclosure pattern

I follow [coordinated disclosure](https://en.wikipedia.org/wiki/Coordinated_vulnerability_disclosure). After a fix is shipped:
1. CVE assigned if applicable
2. Security advisory published in this repo
3. Credit given in CHANGELOG.md (unless you prefer anonymity)

## Security-by-design notes

This script is designed to be safe by default:

- **Read-only AWS credentials required** — the IAM policy in README has zero write actions
- **No network telemetry** — never phones home; all data stays on your machine
- **No third-party dependencies beyond boto3 + tqdm** — minimal supply-chain surface
- **`.env` excluded from version control** — `.gitignore` includes it
- **No credential logging** — even at debug level, the script masks secrets
- **Output files contain no credentials** — only resource metadata

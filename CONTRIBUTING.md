# Contributing

Thanks for considering a contribution. This project is small + scoped — happy to merge anything that fits.

## What I welcome

- 🐛 Bug fixes (especially edge cases in multi-region or older boto3)
- 📚 Additional AWS service pullers (KMS, VPC Flow Logs, WAF, ECR, Inspector)
- ✨ Output format variants (Parquet, Avro, JSON-LD)
- 🌍 Multi-account / AWS Organizations support
- 🔍 Better documentation (especially auditor walkthroughs by firm)
- 🧪 Test coverage

## What's out of scope

- Features that turn this into a SaaS (it's intentionally a script)
- Anti-features that send data anywhere (this is local-only by design)
- Anything that requires non-read-only AWS permissions
- Code targeting Python <3.8

## Workflow

1. **Open an issue first** for non-trivial changes — saves us both time
2. Fork → branch → PR against `main`
3. Make sure `python -m py_compile *.py` passes (GitHub Actions enforces this)
4. Add a CHANGELOG.md entry under `[Unreleased]`
5. PRs squash-merge into `main`

## Code style

- Black formatter (`pip install black && black .`)
- Type hints encouraged but not required
- Docstrings on public functions
- Comments for non-obvious AWS API quirks

## Want a feature?

- Open an issue describing the use case
- Or [book a 15-min call](https://cal.com/siyas/auditready-walkthrough) — sometimes the feature already exists in the [full AuditReady toolkit](https://siyas.gumroad.com/l/auditready) and we can talk through it

## License

By contributing, you agree your contributions are licensed under MIT (same as the rest of the repo).

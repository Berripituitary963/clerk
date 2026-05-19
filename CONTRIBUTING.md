# Contributing to Clerk

Thanks for considering a contribution. Clerk is an open SDK on top of a
permissionless legal-data API. Contributions to the **client SDK** and
**examples** are welcome. Server-side internals are not in this repo.

## Filing issues

Bug? Feature request? Open an issue at
[github.com/basedcryptoji/clerk/issues](https://github.com/basedcryptoji/clerk/issues).

Useful info to include:
- Python version (`python --version`)
- `clerk-api` version (`pip show clerk-api`)
- Minimum reproducible snippet
- Full traceback if you hit an error

## Pull requests

1. Fork the repo
2. Branch from `main`: `git checkout -b fix/short-description`
3. Make your change. Keep diffs focused — one concern per PR.
4. Match the existing style (PEP 8 + 4-space indent, type hints on public APIs).
5. Commit with a clear message. No AI attribution in commits.
6. Open a PR against `main`. Describe what + why.

## Local development

```bash
git clone https://github.com/basedcryptoji/clerk.git
cd clerk
pip install -e .[examples]
```

Then run any example:

```bash
python examples/search_cases.py
```

## Scope

**In scope:**
- SDK client improvements (new endpoints, better error handling, retry logic)
- New example scripts that demonstrate composability
- Documentation improvements (README, ENDPOINTS, docs/)
- Type hints, dataclass response models
- Async variant of the client

**Out of scope:**
- Server-side code (lives elsewhere)
- Upstream data-source integrations (the data layer is internal)
- Anything that requires changes to how Clerk routes / prices queries
  (raise as an issue first if you want to discuss)

## Security

If you find a security issue, please don't open a public issue. Email
hello@solvrbot.com or DM [@solvrbot](https://x.com/solvrbot) on X.

## License

By contributing you agree your contributions are licensed under MIT.

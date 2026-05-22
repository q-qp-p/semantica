---
title: "Contributing"
description: "How to contribute code, documentation, tests, and community support to Semantica."
icon: "code-pull-request"
---

> Contributions of all kinds are welcome — code, documentation, tests, and community support.

---

## Quick Start

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/your-username/semantica.git
cd semantica
pip install -e ".[dev]"
pytest
```

New to the project? Look for [`good-first-issue`](https://github.com/semantica-agi/semantica/labels/good-first-issue) labels.

---

## Ways to Contribute

**Code**
- Fix bugs and resolve open issues
- Implement new features or integrations
- Optimize performance or refactor existing code

**Documentation**
- Fix typos, improve clarity, add examples
- Write tutorials or domain-specific cookbook notebooks
- Keep the API reference up to date

**Testing**
- Add coverage for untested modules
- Reproduce and confirm reported bugs
- Improve test reliability

**Community**
- Answer questions in issues and discussions
- Review pull requests
- Share Semantica in blog posts or talks

---

## Reporting Issues

**Bug reports** — include: what happened, steps to reproduce, expected behavior, and your environment (Python version, OS, Semantica version).

**Feature requests** — include: your use case, what you'd like Semantica to do, and how it benefits others.

---

## Pull Request Checklist

Before submitting:

- [ ] Tests pass locally (`pytest`)

- [ ] New features have documentation with examples

- [ ] Code follows project style (Black, isort, flake8)

- [ ] Commit messages are clear and descriptive

- [ ] No unresolved merge conflicts

---

## Development Setup

```bash
git clone https://github.com/your-username/semantica.git
cd semantica
pip install -e ".[dev]"
```

Code style: **Black** (formatting), **isort** (imports), **flake8** (linting).

```bash
pytest                     # full test suite
black semantica/ tests/    # format
isort semantica/ tests/    # sort imports
flake8 semantica/          # lint
```

---

## Code of Conduct

Please follow the [Code of Conduct](https://github.com/semantica-agi/semantica/blob/main/CODE_OF_CONDUCT.md). Be respectful, patient, and constructive. All contributors are recognized in release notes and the GitHub contributors list.

---

## Help

- [GitHub Issues](https://github.com/semantica-agi/semantica/issues)
- [GitHub Discussions](https://github.com/semantica-agi/semantica/discussions)
- [Discord](https://discord.gg/sV34vps5hH)

---

## See Also

<CardGroup cols={2}>
  <Card title="Community" icon="users" href="community">
    Community guidelines and values.
  </Card>
  <Card title="Governance" icon="scale-balanced" href="governance">
    How decisions are made.
  </Card>
</CardGroup>

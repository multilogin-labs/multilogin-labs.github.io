# One-time GitHub repository setup

Complete after pushing the latest main branch.

## Settings → General

- [ ] **Description:** Open antidetect ops lab — benchmarks, JSON datasets, free tools, playbooks
- [ ] **Website:** https://multilogin-labs.github.io/
- [ ] **Topics:** `antidetect-browser` `browser-automation` `fingerprinting` `playwright` `multilogin` `benchmark` `github-pages` `open-data` `devtools`
- [ ] **Discussions:** Enable → Categories: General, Ideas, Benchmark requests, Q&A
- [ ] **Social preview:** Upload `assets/img/og-lab.svg` or export PNG 1280×640

## Settings → Pages

- [ ] Source: Deploy from branch **main** / **root**
- [ ] Custom domain (optional): only if you own a domain

## Settings → Actions

- [ ] Allow GitHub Actions (workflow `ci.yml` should pass on push)

## Community standards

GitHub should show green checks for README, LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY after this repo state.

## Post-deploy smoke test

```bash
curl -sI https://multilogin-labs.github.io/tools/benchmark-explorer/ | head -1
curl -sL https://multilogin-labs.github.io/data/index.json | jq .datasets
```

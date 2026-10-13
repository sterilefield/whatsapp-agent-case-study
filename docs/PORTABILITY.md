# Portability — leaving GitHub costs one afternoon, not a rewrite

GitHub is the **showroom**, not the vault. Everything here can move to Codeberg, GitLab, a self-hosted Forgejo or a plain disk without losing work.

## The five rules

| # | Rule | How this repo follows it |
|---|---|---|
| 1 | **Git is the source of truth** | All content is Markdown, Mermaid and YAML — plain files any host renders |
| 2 | **Checks live in scripts, not in CI files** | `scripts/check.sh` runs every gate on a laptop or any CI; `.github/workflows/ci.yml` is a thin wrapper |
| 3 | **Only free, open-source tools** | gitleaks (MIT), lychee (MIT/Apache). No paid GitHub features, no licence keys |
| 4 | **GitHub-only data should be exported regularly** | Recommended: export issues, pull requests, releases and discussions as JSON regularly (for example weekly), alongside git bundles |
| 5 | **A second live copy exists** | `.github/workflows/mirror.yml` push-mirrors public repos to Codeberg or GitLab.com (free) once two secrets are added |

## What is GitHub-specific here, and its exit

| GitHub feature used | Portable equivalent | Effort to move |
|---|---|---|
| Actions workflows | `scripts/check.sh` runs as-is in GitLab CI, Forgejo Actions (same YAML syntax), Woodpecker or cron | Minutes |
| Issue forms / PR template | Plain Markdown templates; Forgejo reads `.forgejo/` or `.gitea/` copies | Minutes |
| Releases + attestations | Tags stay in git; assets can be re-downloaded or kept in your own backup; SBOM files are plain SPDX JSON | Minutes |
| Discussions | Export to JSON (recommended) | Read-only archive |
| Profile README / org `.github` | A static page (GitHub Pages output is plain HTML — host on Codeberg Pages or any static host) | An hour |
| Social preview, pins, contribution graph | Cosmetic; rebuilt from source images | — |

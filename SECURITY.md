# Security Policy

## Supported versions
The latest released build of **PS4 NOR EASYTOOL V1** and the `main` branch of
this knowledge base.

## Reporting a vulnerability
Please **do not** open a public issue for security concerns. Use GitHub's
private "Report a vulnerability" flow (Repository → Security → Advisories), or
start a private security advisory. We will respond as soon as possible.

## Data privacy
- **Corpus reports are anonymized by design.** `main.export_report()` strips
  serial / MAC / HDD / board-id before anything leaves the machine. Never paste
  identifying data into issues, PRs, or Discussions.
- **This project stores no secrets.** Contributor tokens are never committed to
  the repository. The in-app upload uses your locally authenticated `gh` CLI —
  the token never touches the code or this repo.
- If you ever pasted a token anywhere public, **revoke it immediately** at
  GitHub → Settings → Developer settings → Personal access tokens.

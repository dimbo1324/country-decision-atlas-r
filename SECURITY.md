# Security Policy

Country Decision Atlas may eventually process sensitive user profiles, country
eligibility inputs, uploaded evidence, payment metadata, and sourced legal or
migration data. Security work should be treated as part of product quality, not
as a separate cleanup phase.

## Reporting a Vulnerability

Do not open a public issue for suspected vulnerabilities.

Report privately to the repository owner or maintainer. Include:

- A short description of the issue.
- Reproduction steps or proof of concept, if safe to share.
- Affected files, services, or deployment environments.
- Any known impact on user data, credentials, or availability.

The expected response window is 72 hours for acknowledgement and 14 days for an
initial remediation plan, depending on severity.

## Supported Versions

The project is in early development. Until the first public release, only the
current `main` branch is supported.

## Secret Handling

- Never commit real secrets, API keys, access tokens, private certificates, or
  production `.env` files.
- Use `.env.example` for names and safe local placeholders only.
- Rotate any credential that may have been committed, pasted into logs, or shared
  outside the intended environment.
- Keep service-account files and provider credentials out of the repository.

## Data Handling

- Store only the minimum personal data needed for a feature.
- Keep source provenance for legal, migration, tax, safety, healthcare, and cost
  data.
- Mark generated AI summaries as derived content and keep links to source
  material where possible.
- Avoid committing raw user uploads, generated reports, local exports, database
  dumps, and scraped pages.

## Secure Development Baseline

- Validate request inputs at API boundaries.
- Use explicit authorization checks for user-owned resources.
- Prefer server-side enforcement over UI-only restrictions.
- Log operational events without logging secrets or full personal profiles.
- Pin dependency versions through lock files once package installation starts.
- Run dependency and container scanning before production deployment.

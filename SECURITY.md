# Security policy

## Reporting a vulnerability

Please report security issues **privately** through GitHub's
[private vulnerability reporting](../../security/advisories/new) for this repository.
Do not open a public issue.

You can expect an acknowledgement within 3 working days (IST, UTC+5:30) and a
status update within 10 working days.

## Scope

This repository holds documentation and tooling. It never contains real
customer data, client data or live credentials. If you find anything that looks like
one of those, report it the same way and it will be removed and rotated at once.

## Supply chain

Every push runs a full-history secret scan; releases ship with an SPDX SBOM and
build-provenance attestations; dependencies are watched by Dependabot; the repository
is scored weekly by OpenSSF Scorecard.

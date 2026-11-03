# Contributing to UEAS

UEAS is an experimental standards proposal. Contributions do not make it an adopted, authorized, or certified standard.

## Before proposing a change

For changes to the protocol profile, open an issue or discussion first. State the interoperability problem, affected producer and receiver behavior, alternatives considered, security and accessibility effects, and whether existing CAP behavior already solves it.

Small editorial fixes can be submitted directly as pull requests.

## Pull request expectations

A protocol change should:

- identify the exact section of `spec/UEAS-CAP-Profile-0.1.md` it affects;
- explain compatibility and migration effects;
- use the requirement terms defined in the specification consistently;
- cite primary specifications or reproducible evidence for technical claims;
- describe security, privacy, localization, accessibility, geographic targeting, and failure-mode consequences;
- include proposed conformance examples when the change affects observable behavior;
- avoid claiming production readiness or official conformance.

Do not add a new wire field, cryptographic algorithm, sound pattern, or location format without documenting its encoding, validation, failure behavior, versioning, and interoperability rationale.

## Review and release status

The repository currently has no formal technical committee, appointed standards editor, certification process, or guaranteed review SLA. A maintainer may merge a change into this repository, but that action is not standards-body approval.

Draft releases must be labeled as drafts. A stable release requires the entry criteria in the profile, independent review, published conformance vectors, multiple independent implementations, and an identified standards venue. Until those conditions are met, deployments MUST NOT rely on this repository as the sole authority for public warnings.

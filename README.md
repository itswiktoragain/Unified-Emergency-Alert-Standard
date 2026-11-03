# Unified Emergency Alert Standard (UEAS)

<img width="419" height="122" alt="UEAS wordmark" src="https://github.com/user-attachments/assets/3c0f8dab-0bbb-4a94-963e-597ad070481f" />

**Current document:** UEAS CAP Profile 0.1 (working draft)  
**Status:** Open for review; not approved by a standards organization  
**Operational use:** Not authorized or suitable as the sole basis for real public warnings

UEAS is an experimental proposal for improving interoperability among emergency-alert producers and receivers. The current draft profiles the established OASIS Common Alerting Protocol (CAP) 1.2 instead of defining a competing payload format. CAP remains the wire format; UEAS adds proposed rules for lifecycle handling, language, geographic targeting, security status, and receiver behavior.

## Start here

- [UEAS CAP Profile 0.1](spec/UEAS-CAP-Profile-0.1.md): scope, normative requirements, conformance targets, security/trust requirements, and open issues.
- [Contributing](CONTRIBUTING.md): how protocol changes are proposed and reviewed.\n- [Test-only CAP example](examples/cap-test-only.xml): fictional message for format review; never transmit it.
- [OASIS CAP 1.2](https://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2.html): the upstream alert format and XML Schema.

## What this draft does not provide

This repository does not provide an authorized sender network, trust-anchor distribution, operational transport, certification, or a complete conformance suite. A CAP XML signature alone does not establish that a sender is authorized to issue an alert. A deployment needs a separate, documented trust profile and approval from its responsible warning authority.

The old JSON/UUIDv7 payload and `ueas.py` parser are historical prototypes. They are **not** UEAS CAP Profile 0.1 messages or a conforming implementation. The profile does not define the old JSON envelope, require UUIDv7, or specify an audio beacon.

## Path toward a stable profile

Before a stable release, this project needs an accountable standards venue, a reviewed signer trust framework, defined transport/discovery behavior, accessibility and community review, location and lifecycle conformance vectors, interoperability exercises, and at least two independent implementations. These are open work items, not claims that the repository has completed them.

## License

See [LICENSE](LICENSE).

# UEAS CAP Profile 0.1 (Draft)

**Status:** Working draft for public review  
**Version:** 0.1  
**Date:** 2026-11-03  
**Intended status:** Experimental profile; not approved by a standards body  
**Operational use:** Not approved for real public warning systems

## Abstract

This document proposes a narrow interoperability profile for exchanging public emergency alerts. UEAS 0.1 reuses the OASIS Common Alerting Protocol (CAP) Version 1.2 message model and XML representation. It defines additional receiver and producer behavior for lifecycle handling, location, language, security status, and conformance.

UEAS 0.1 does not define a new alert payload, a global sender identity system, a transport network, a public-warning authority, or a universal alert sound. The JSON/UUIDv7 format previously shown in this repository is a historical prototype and is not a UEAS 0.1 message.

## 1. Scope and relationship to CAP

CAP 1.2 is the normative wire format for this profile. Implementations MUST satisfy CAP 1.2 and this profile. If a UEAS rule conflicts with CAP, the CAP message remains a CAP message but is not conformant to this UEAS profile.

This profile is transport agnostic. It does not prescribe polling, feeds, mobile push, broadcast, radio, or a particular network endpoint. A deployment MUST specify its transport and trust configuration in a jurisdictional deployment profile.

UEAS does not replace existing legally required public warning systems. An implementation MUST NOT claim that it is an authorized alert originator, official warning channel, or certified UEAS implementation solely because it follows this draft.

## 2. Requirement language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and **OPTIONAL** are to be interpreted as described in BCP 14 (RFC 2119 and RFC 8174) when, and only when, they appear in uppercase.

## 3. Message profile

### 3.1 CAP conformance

A UEAS message MUST be a CAP 1.2 XML document in the CAP namespace and MUST validate against the official CAP 1.2 XML Schema and the additional CAP requirements. Implementations MUST use CAP-defined elements and code values; this profile does not add private fields to the core message.

The CAP `identifier`, `sender`, and `sent` elements identify a message. A UUID embedded in a JSON object is not the UEAS message identifier. Receivers MUST treat the CAP `sent` value as the message issue time; they MUST NOT infer issue time from an identifier.

The CAP alert `status`, `msgType`, and `scope` values MUST be preserved end to end. A relay MUST NOT convert a test or exercise message into an actual message, or change a restricted/private message into a public message.

### 3.2 Information and language

Each public-facing `<info>` block MUST contain enough human-readable information for its intended audience to understand the hazard and the requested protective action. Producers SHOULD provide `<headline>`, `<description>`, and `<instruction>` when applicable. A missing optional element MUST NOT be fabricated by a receiver.

Each `<info>` block MUST declare its language using a valid BCP 47 language tag in CAP `<language>`. Producers SHOULD provide equivalent information blocks for the languages required by the deployment authority. Receivers SHOULD select a block using the recipient's configured language preference, then a deployment-defined fallback. A receiver MUST NOT silently replace missing official instructions with machine-translated instructions.

CAP `<urgency>`, `<severity>`, and `<certainty>` values MUST retain their CAP meanings. A user interface MAY map these values to local presentation, but MUST NOT relabel or rank them as if they were interchangeable measurements.

### 3.3 Geographic targeting

CAP `<areaDesc>` is descriptive text. A receiver MUST NOT use name matching against `<areaDesc>` as the sole basis for deciding whether a location is inside the alert area.

A deployment that performs automated geographic targeting MUST define which CAP geometry or jurisdictional geocode types it accepts, their authoritative source, coordinate reference system, boundary behavior, and handling of missing or invalid geometry. CAP polygon coordinates use the CAP-defined WGS 84 representation. A receiver MUST NOT interpret the prototype's old `geohash` field as a UEAS 0.1 field.

A receiver unable to evaluate an alert's targeting data MUST report that targeting is unknown. It MUST NOT report a precise match based only on city or country names.

### 3.4 Lifecycle, duplicates, and expiry

Producers MUST use CAP `<msgType>` and `<references>` according to CAP 1.2 for alert, update, and cancel messages. Update and cancel messages MUST identify the message or messages they update or cancel using CAP's sender/identifier/sent reference format.

Receivers MUST deduplicate by the CAP message identity tuple `(sender, identifier, sent)`. Re-receiving the same tuple MUST NOT create a second independent alert. A receiver MUST apply a valid update or cancel only to the referenced message lineage; it MUST preserve the original message for audit/history where local policy requires.

When CAP `<expires>` is present and has passed, a receiver MUST NOT present the message as a currently active warning. It MAY retain it in history with an expired label. The receiver MUST use timezone-aware CAP date-time values and MUST NOT interpret a timezone-free timestamp using its local timezone.

A receiver MUST distinguish CAP `Actual`, `Test`, and `Exercise` status in storage and presentation. Test and exercise messages MUST NOT be presented as actual emergencies.

## 4. Security and trust

CAP permits an enveloped XML Digital Signature. UEAS receivers MUST follow CAP's XML signature rules; they MUST NOT substitute a different signature mechanism inside the CAP XML document.

A cryptographically valid signature proves possession of a key, not that the sender is authorized to issue a warning for a location or hazard. A production deployment MUST publish a trust profile that defines, at minimum:

- authorized sender identities and their geographic and hazard scopes;
- trust-anchor distribution and key enrollment;
- key storage, rotation, expiry, revocation, and compromise response;
- supported signature and digest algorithms and transition dates;
- how relays preserve signatures and how receivers report validation outcomes;
- replay, stale-message, clock-skew, and recovery behavior.

Until a deployment trust profile is configured, a receiver MUST NOT label an alert as authenticated or official. A receiver that cannot verify a signature MUST make that status visible and MUST NOT imply successful authentication. Whether an unverified message is suppressed, shown with a warning, or routed for operator review is a deployment safety decision and MUST be documented locally.

Implementations MUST disable unsafe XML external entity and external resource resolution while parsing untrusted CAP input. Fetching a URL from a CAP resource MUST require an explicit local policy; receivers MUST NOT automatically execute or install linked content.

Transport encryption protects a connection but does not, by itself, authenticate the authority of an alert message. Each deployment MUST document transport protection, endpoint authorization, and signature trust separately.

## 5. Receiver behavior

A conforming receiver MUST:

1. validate CAP syntax and this profile before treating a message as a UEAS-profile message;
2. preserve the source message and distinguish parse errors from authentication and targeting outcomes;
3. display the message's status, time validity, language, and authentication state without implying more certainty than the data supports;
4. handle updates, cancellations, expiry, and duplicates as specified above;
5. keep test and exercise traffic visibly separate from actual alerts;
6. avoid executing message content or automatically following resource links;
7. provide an accessible text presentation and follow the deployment's approved audio, vibration, and visual-alert policy.

A receiver MAY support other CAP messages. If it does, it MUST keep non-UEAS behavior distinguishable from UEAS-profile conformance.

## 6. Producer behavior

A conforming producer MUST:

1. emit valid CAP 1.2 XML and meet every applicable UEAS profile requirement;
2. use a stable `sender` identity and unique `identifier` values within that sender's namespace;
3. keep alert status, scope, severity, certainty, effective time, and expiry truthful and internally consistent;
4. include valid lifecycle references for updates and cancellations;
5. provide accurate, actionable text and deployment-required translations;
6. use area geometry or a documented geocode when automated location targeting is intended;
7. sign messages according to the deployment trust profile when authentication is required;
8. support safe test and exercise procedures that cannot be mistaken for live alerts.

## 7. Conformance targets

This draft defines three conformance targets:

- **UEAS message:** a CAP 1.2 document satisfying Sections 3 and 4's message requirements.
- **UEAS producer:** a system that emits only conforming UEAS messages when operating in UEAS mode and follows Section 6.
- **UEAS receiver:** a system that validates and processes UEAS messages according to Sections 3–5.

A claim of conformance MUST identify the profile version and target (message, producer, or receiver). Passing the CAP 1.2 XML Schema alone is not UEAS conformance. No certification program or official conformance suite exists for this draft. The repository MUST NOT award an official certification badge.

Before this profile can be considered stable, the project needs independently reviewed conformance vectors, at least two independent implementations, interoperability exercises, an agreed trust profile, accessibility review, and an accountable standards venue.

## 8. Versioning and compatibility

This document is version 0.1 and may change incompatibly. A future stable release MUST identify its exact CAP version and normative schema, define how extensions are handled, and publish machine-readable conformance vectors.

Unknown CAP elements or extensions MUST be handled according to CAP 1.2 and the deployment profile. Receivers MUST NOT reinterpret unknown fields as authorization, priority, or geographic authority.

## 9. Open issues

The following work is intentionally unresolved and blocks operational adoption:

1. Select a standards organization and a transparent, multi-stakeholder change process.
2. Define a jurisdiction-neutral or jurisdiction-specific signer trust framework.
3. Define a transport/discovery profile and outage/failover behavior.
4. Develop interoperable location test vectors, including borders and geometry edge cases.
5. Review accessibility, translation quality, alert fatigue, privacy, and abuse cases with affected communities.
6. Publish independent implementations and a conformance test suite.
7. Determine whether UEAS adds enough value beyond interoperable CAP profiles to justify a new name and profile.

## 10. References

### Normative

- OASIS, [Common Alerting Protocol Version 1.2](https://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2.html), especially its message structure, security note, schema, and conformance sections.
- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119.html), Key words for use in RFCs to Indicate Requirement Levels.
- [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174.html), Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words.
- [RFC 5646](https://www.rfc-editor.org/rfc/rfc5646.html), Tags for Identifying Languages (BCP 47).

### Informative

- [RFC 9562](https://www.rfc-editor.org/rfc/rfc9562.html), Universally Unique IDentifiers (UUIDs). UEAS 0.1 does not require UUIDv7.

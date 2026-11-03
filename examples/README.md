# Examples

[`cap-test-only.xml`](cap-test-only.xml) is a fictional CAP 1.2 message with `status=Test`. It is for format review only.

**Do not transmit, publish, or play this message through a live alert channel.** It has no real issuing authority, no verified signature, and no real geographic target. It is an illustration, not a conformance vector or a complete CAP schema/profile validator.

Future conformance vectors must define expected producer and receiver behavior, including update/cancel chains, expiry boundaries, test/exercise separation, geometry edge cases, malformed XML, and signature/trust outcomes.

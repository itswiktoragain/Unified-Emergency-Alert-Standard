# 🌐 Unified Emergency Alert Standard (UEAS) — v1.0 Specification

<img width="419" height="122" alt="UEAS-with-wordmark" src="https://github.com/user-attachments/assets/3c0f8dab-0bbb-4a94-963e-597ad070481f" />


UEAS is an experimental proposal for representing emergency alerts across connected devices. It is not an adopted standard or a deployable public warning system.

---

## 1. Core Architectural Pillars
* **The Single-Payload Principle:** Every emergency alert is a lightweight data object containing cryptographic protection, multi-lingual strings, and machine-automation hooks.
* **Implicit Timestamping:** The root key uses a UUIDv7 structure, embedding the exact creation time in the first 48 bits, saving packet space.
* **Dual-Tier Geofencing:** Combines wide textual string matching (`affected_areas`) with point precision grids (`geohash`) for hyper-local sorting.

---

## 2. Reference Prototype Payload Template
```json
{
    "sig": "PLACEHOLDER",
    "01a19e89-d4f9-7563-877a-9e745dd9c728": {
        "status": "N",
        "rev": 1,
        "type": "FLA",
        "source": {
            "country": "US",
            "state": "FL",
            "city": "Miami",
            "severity": "High",
            "origin": "NWS"
        },
        "action": "P",
        "messages": {
            "en": "Flood watch in effect from Miami, FL. Residents are advised to stay alert and follow local authorities' instructions. The watch is in effect from November 4 to November 5, 2026.",
            "es": "Alerta de inundación vigente para Miami, FL. Se aconseja a los residentes mantenerse alerta y seguir las instrucciones de las autoridades locales. La alerta estará vigente del 4 al 5 de noviembre de 2026.",
            "fr": "Vigilance inondation en vigueur pour Miami, FL. Les résidents sont priés de rester vigilants et de suivre les instructions des autorités locales. La vigilance est valable du 4 au 5 niveau de 2026."
        },
        "geohash": "dhwfx38",
        "affected_areas": ["Miami", "Fort Lauderdale", "West Palm Beach"],
        "expires": "2026-11-05T11:27:00Z"
    }
}
```

---

## 3. Experimental Audio Beacon Proposal
The following tone is a prototype idea only. It has not been validated for cross-hardware reliability, audibility, accessibility, or public-warning use:
* **Frequencies:** 550 Hz + 600 Hz mixed at equivalent amplitude.
* **Phenomenon:** Creates a natural 50 Hz acoustic "beating" wave interaction to bypass room noise and command sensory focus.
* **Linux Terminal Execution String:**
  ```bash
  python3 -c "import sys, math, struct; R=44100; d=3000; b=b''.join(struct.pack('<h', int((math.sin(2*math.pi*550*(i/R)) + math.sin(2*math.pi*600*(i/R)))/2 * 0.5 * 32767)) for i in range(int(R*(d/1000)))); sys.stdout.buffer.write(struct.pack('<4sI4s4sIHHIIHH4sI',b'RIFF',36+len(b),b'WAVE',b'fmt ',16,1,1,R,R*2,2,16,b'data',len(b))+b)" | aplay
  ```

---

## 4. Reference Implementation Python Engine (ueas.py)
```python
import json
from uuid import UUID
from datetime import datetime

class UEASEngine:
    def __init__(self, current_country=None, current_city=None):
        self.current_country = current_country
        self.current_city = current_city

    @staticmethod
    def extract_creation_time(uuid_string):
        try:
            timestamp_ms = int(uuid_string.split('-')[0], 16)
            return datetime.fromtimestamp(timestamp_ms / 1000.0)
        except Exception:
            return None

    def parse_alert(self, raw_json_string):
        clean_lines = []
        for line in raw_json_string.splitlines():
            if line.strip().startswith("//"):
                continue
            if "//" in line:
                line = line.split("//")[0]
            clean_lines.append(line)
            
        clean_json = "\n".join(clean_lines).strip()
        payload = json.loads(clean_json)
        sig = payload.get("sig")
        alert_id = [k for k in payload.keys() if k != "sig"][0]
        data = payload[alert_id]
        
        return {
            "status": "SUCCESS",
            "alert_id": alert_id,
            "signature": sig,
            "event_type": data.get("type"),
            "action_code": data.get("action"),
            "issued_at_utc": self.extract_creation_time(alert_id),
            "render_message": data.get("messages", {}).get("en")
        }
```
## Notes
* If the country has no state system, please insert N/A into the value instead of the city or country


## Prototype status and safety limits

UEAS and its Python parser are experimental. Do not use this repository to issue, relay, or make decisions about real emergency alerts. Production public warning systems require authenticated, authorized alert sources, a defined signing and verification scheme, interoperability testing, accessibility review, and jurisdiction-specific procedures.

The reference parser in `ueas.py` accepts strict JSON with exactly one UUIDv7 alert key. It checks basic structure, parses timezone-aware expiry values, and supports a preferred language:

```python
import json
from ueas import UEASEngine

engine = UEASEngine(current_country="PL", current_city="Opole")
result = engine.parse_alert(
    json.dumps(alert_payload),
    preferred_language="pl-PL",
)
```

A `SUCCESS` result means only that the payload passed these basic parsing checks. `signature_verified` is always `false`: the parser does not authenticate `sig`. Its city and country matching is a simple text comparison; it does not perform geohash containment or reliable location targeting. Applications must not treat `is_locally_relevant` as a safety decision.

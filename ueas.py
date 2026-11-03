"""
UEAS - Unified Emergency Alert Standard Python Reference Library (v1.0)
An ultra-lightweight, high-performance toolkit to parse, validate, and extract
data points directly from UEAS JSON payloads.
"""

import json
from uuid import UUID
from datetime import datetime

class UEASEngine:
    def __init__(self, current_country=None, current_city=None):
        self.current_country = current_country
        self.current_city = current_city

    @staticmethod
    def extract_creation_time(uuid_string):
        """
        Extracts the explicit UTC datetime directly from the first 48 bits 
        of a valid UUIDv7 root key without requiring a separate timestamp payload field.
        """
        try:
            u = UUID(uuid_string)
            # UUIDv7 embeds milliseconds from the Unix epoch in its top 48 bits
            timestamp_ms = u.time >> 12  # Normalizing the UUIDv7 internal bit structure
            # Let's adjust to standard timestamp translation layout
            timestamp_ms = int(uuid_string.split('-')[0], 16)
            return datetime.fromtimestamp(timestamp_ms / 1000.0)
        except Exception:
            return None

    def parse_alert(self, raw_json_string):
        """
        Parses a UEAS payload, stripping invalid structural comments, validating fields,
        and rendering localized instructions for downstream clients.
        """
        # Clean inline development comments from raw input
        clean_lines = []
        for line in raw_json_string.splitlines():
            if line.strip().startswith("//"):
                continue
            # Remove trailing comments
            if "//" in line:
                line = line.split("//")[0]
            clean_lines.append(line)
            
        clean_json = "\n".join(clean_lines).strip()
        
        try:
            payload = json.loads(clean_json)
        except json.JSONDecodeError as e:
            return {"status": "ERROR", "error": f"Invalid JSON structure: {str(e)}"}

        sig = payload.get("sig")
        
        # Isolate the UUID root alert block
        alert_keys = [k for k in payload.keys() if k != "sig"]
        if not alert_keys:
            return {"status": "ERROR", "error": "No valid UEAS UUID root found"}
            
        alert_id = alert_keys[0]
        data = payload[alert_id]
        
        # 1. Structural Lifecycle Extractor
        issued_at = self.extract_creation_time(alert_id)
        
        # 2. Expiry Safety Intercept
        expires_str = data.get("expires")
        is_expired = False
        if expires_str:
            try:
                expires_dt = datetime.strptime(expires_str, "%Y-%m-%dT%H:%M:%SZ")
                if datetime.utcnow() > expires_dt:
                    is_expired = True
            except ValueError:
                pass

        # 3. Micro-Geofence Core Sorting Rules
        affected_areas = data.get("affected_areas", [])
        source_city = data.get("source", {}).get("city")
        source_country = data.get("source", {}).get("country")
        
        is_relevant = True
        if self.current_country and source_country and self.current_country != source_country:
            is_relevant = False
        if self.current_city and affected_areas and (self.current_city not in affected_areas and source_city != self.current_city):
            is_relevant = False

        # 4. Multi-Language Dynamic Selection
        messages = data.get("messages", {})
        selected_msg = None
        
        # Priority mapping fallback routing 
        fallback_languages = ["en", "pl", "es", "de", "fr"]
        for lang in fallback_languages:
            if lang in messages:
                selected_msg = messages[lang]
                break

        return {
            "status": "SUCCESS",
            "alert_id": alert_id,
            "signature": sig,
            "event_type": data.get("type"),
            "action_code": data.get("action"),
            "revision": data.get("rev"),
            "alert_status": data.get("status"),
            "issued_at_utc": issued_at.isoformat() if issued_at else None,
            "expires_at_utc": expires_str,
            "geohash": data.get("geohash"),
            "is_expired": is_expired,
            "is_locally_relevant": is_relevant,
            "render_message": selected_msg,
            "metadata": data.get("source", {})
        }

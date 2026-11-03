"""
UEAS - Unified Emergency Alert Standard Python Reference Library (v1.1)

A small, dependency-free parser for UEAS JSON alert envelopes. This prototype
parses and performs basic structural checks; it does not verify signatures or
provide authoritative geographic targeting.
"""

import json
from datetime import datetime, timezone
from uuid import UUID


class UEASEngine:
    def __init__(self, current_country=None, current_city=None):
        self.current_country = current_country
        self.current_city = current_city

    @staticmethod
    def extract_creation_time(uuid_string):
        """Return a timezone-aware UTC datetime for a UUIDv7, or None."""
        try:
            alert_uuid = UUID(str(uuid_string))
            if alert_uuid.version != 7:
                return None
            # UUIDv7 stores Unix epoch milliseconds in the most significant 48 bits.
            timestamp_ms = alert_uuid.int >> 80
            return datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
        except (ValueError, TypeError, OverflowError, OSError):
            return None

    @staticmethod
    def _error(message):
        return {"status": "ERROR", "error": message}

    @staticmethod
    def _parse_expiry(value):
        """Parse an ISO 8601 timestamp and require an explicit timezone."""
        if not isinstance(value, str):
            raise ValueError("expires must be an ISO 8601 string")
        normalized = value[:-1] + "+00:00" if value.endswith(("Z", "z")) else value
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("expires must include a timezone (for example, Z)")
        return parsed.astimezone(timezone.utc)

    def parse_alert(self, raw_json_string, preferred_language=None, now=None):
        """
        Parse one UEAS envelope and choose a localized message.

        Input must be strict JSON. The method does not remove comments, because
        comment stripping can corrupt valid string values such as URLs.
        """
        try:
            payload = json.loads(raw_json_string)
        except (json.JSONDecodeError, TypeError) as exc:
            return self._error(f"Invalid JSON: {exc}")

        if not isinstance(payload, dict):
            return self._error("UEAS envelope must be a JSON object")

        alert_keys = [key for key in payload if key != "sig"]
        if len(alert_keys) != 1:
            return self._error("Envelope must contain exactly one alert UUID key")

        alert_id = alert_keys[0]
        issued_at = self.extract_creation_time(alert_id)
        if issued_at is None:
            return self._error("Alert key must be a valid UUIDv7")

        data = payload[alert_id]
        if not isinstance(data, dict):
            return self._error("Alert data must be a JSON object")

        source = data.get("source", {})
        if not isinstance(source, dict):
            return self._error("source must be a JSON object")

        messages = data.get("messages", {})
        if not isinstance(messages, dict):
            return self._error("messages must be a JSON object")
        if any(not isinstance(lang, str) or not isinstance(message, str)
               for lang, message in messages.items()):
            return self._error("Each localized message must map a language code to text")

        expires_str = data.get("expires")
        expires_at = None
        if expires_str is not None:
            try:
                expires_at = self._parse_expiry(expires_str)
            except (ValueError, OverflowError) as exc:
                return self._error(str(exc))

        current_time = now or datetime.now(timezone.utc)
        if current_time.tzinfo is None or current_time.utcoffset() is None:
            return self._error("now must be a timezone-aware datetime")
        current_time = current_time.astimezone(timezone.utc)
        is_expired = expires_at is not None and current_time >= expires_at

        affected_areas = data.get("affected_areas", [])
        if not isinstance(affected_areas, list) or any(
            not isinstance(area, str) for area in affected_areas
        ):
            return self._error("affected_areas must be a list of strings")

        source_city = source.get("city")
        source_country = source.get("country")
        is_relevant = True
        if (self.current_country and source_country
                and self.current_country.casefold() != str(source_country).casefold()):
            is_relevant = False
        if self.current_city and affected_areas:
            area_match = any(
                self.current_city.casefold() == area.casefold()
                for area in affected_areas
            )
            city_match = (
                isinstance(source_city, str)
                and self.current_city.casefold() == source_city.casefold()
            )
            if not area_match and not city_match:
                is_relevant = False

        language_order = []
        if preferred_language:
            language_order.append(preferred_language)
            base_language = preferred_language.split("-", 1)[0]
            if base_language != preferred_language:
                language_order.append(base_language)
        language_order.extend(["en", "pl", "es", "de", "fr"])
        selected_message = next(
            (messages[language] for language in dict.fromkeys(language_order)
             if language in messages),
            next(iter(messages.values()), None),
        )

        return {
            "status": "SUCCESS",
            "alert_id": alert_id,
            "signature": payload.get("sig"),
            "signature_verified": False,
            "event_type": data.get("type"),
            "action_code": data.get("action"),
            "revision": data.get("rev"),
            "alert_status": data.get("status"),
            "issued_at_utc": issued_at.isoformat(),
            "expires_at_utc": expires_at.isoformat() if expires_at else None,
            "geohash": data.get("geohash"),
            "is_expired": is_expired,
            "is_locally_relevant": is_relevant,
            "render_message": selected_message,
            "metadata": source,
        }

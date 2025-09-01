from __future__ import annotations

from datetime import datetime, date


def parse_datetime_strict(value: str) -> datetime:
    if isinstance(value, datetime):
        return value
    s = str(value).strip()
    if "T" not in s and " " in s:
        s = s.replace(" ", "T", 1)
    # Allow milliseconds without timezone; datetime.fromisoformat supports both
    return datetime.fromisoformat(s)


def parse_date_strict(value: str | date | datetime) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    s = str(value).strip()
    # If a time portion exists, split off
    if "T" in s:
        s = s.split("T", 1)[0]
    if " " in s:
        s = s.split(" ", 1)[0]
    return date.fromisoformat(s)



# app/utils/time.py

from datetime import datetime, timezone, timedelta

# -------------------------
# Core time helpers
# -------------------------

def utc_now() -> datetime:
    """Return timezone-aware UTC datetime"""
    return datetime.now(timezone.utc)


def to_utc(dt: datetime) -> datetime:
    """Ensure datetime is UTC-aware"""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


# -------------------------
# Display helpers
# -------------------------

def to_local(dt: datetime, offset_hours: int = 7) -> datetime:
    """
    Convert UTC time to local time (default = Thailand UTC+7)
    """
    local_tz = timezone(timedelta(hours=offset_hours))
    return to_utc(dt).astimezone(local_tz)


def iso(dt: datetime) -> str:
    """ISO string (safe for log / audit)"""
    return to_utc(dt).isoformat()


# -------------------------
# Business helpers
# -------------------------

def minutes_ago(minutes: int) -> datetime:
    return utc_now() - timedelta(minutes=minutes)


def days_ago(days: int) -> datetime:
    return utc_now() - timedelta(days=days)

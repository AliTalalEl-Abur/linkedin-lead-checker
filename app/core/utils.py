from datetime import datetime, timezone


def get_current_week_key() -> str:
    """Get current ISO week key in format YYYY-WW."""
    now = datetime.now(timezone.utc)
    iso_calendar = now.isocalendar()
    return f"{iso_calendar[0]}-W{iso_calendar[1]:02d}"


def get_week_key_for_date(dt: datetime) -> str:
    """Get ISO week key for a specific datetime."""
    iso_calendar = dt.isocalendar()
    return f"{iso_calendar[0]}-W{iso_calendar[1]:02d}"

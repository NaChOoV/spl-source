from datetime import datetime
from zoneinfo import ZoneInfo


def format_chilean_date_time_to_utc(date: str | None, hour: str) -> str:
    """
    Convert a date string to UTC format.

    Args:
        date: Date string in the format 'YYYY-MM-DD'
        hour: Date string in the format 'HH:MM:SS'

    Returns:
        str: Date in UTC format 'YYYY-MM-DDTHH:MM:SSZ'
    """

    chile_tz = ZoneInfo("America/Santiago")

    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    date_str = datetime.strptime(f"{date} {hour}", "%Y-%m-%d %H:%M:%S")

    return (
        date_str.replace(tzinfo=chile_tz)
        .astimezone(ZoneInfo("UTC"))
        .strftime("%Y-%m-%dT%H:%M:%SZ")
    )

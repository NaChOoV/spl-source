from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

scheduler: dict[int, list[str]] = {
    1: ["06:30", "23:00"],
    2: ["06:30", "23:00"],
    3: ["06:30", "23:00"],
    4: ["06:30", "23:00"],
    5: ["06:30", "23:00"],
    6: ["09:00", "20:00"],
    7: ["09:00", "14:00"],
}


def get_sleep_seconds() -> int:
    chile_tz = ZoneInfo("America/Santiago")
    now = datetime.now(chile_tz)
    day = now.isoweekday()
    start_str, end_str = scheduler[day]
    sh, sm = map(int, start_str.split(":"))
    eh, em = map(int, end_str.split(":"))

    start = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
    end = now.replace(hour=eh, minute=em, second=0, microsecond=0)

    if start <= now <= end:
        return 0
    elif now < start:
        return (start - now).total_seconds()
    else:
        next_day = (day % 7) + 1
        nsh, nsm = map(int, scheduler[next_day][0].split(":"))
        next_start = (now + timedelta(days=1)).replace(
            hour=nsh, minute=nsm, second=0, microsecond=0
        )
        return (next_start - now).total_seconds()

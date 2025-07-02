import base64
import datetime
import uuid
import logging


def build_start_end(
    day: str,
    start: str,
    duration: int,
) -> tuple[datetime.datetime, datetime.datetime]:
    """
    Build start and end datetime from a start and duration
    """
    start_date = datetime.datetime.strptime(f"{day} {start}+0200", "%d/%m/%Y %Hh%M%z")
    end_date = start_date + datetime.timedelta(minutes=duration)
    logging.debug(
        f"[build_start_date] build {start_date} / {end_date} from {day}, {start}, {duration}",
    )
    return start_date, end_date


def create_id(prefix="bcscal") -> str:
    """Create a base32hex ID which can be used as Google Calendar Event id
    @param prefix : prefix to be prepended to the id
    @return a base32hex string starting by prefix
    """
    u = uuid.uuid4()

    u32: str = base64.b32hexencode(u.bytes).decode("utf-8").lower().strip("=")
    logging.debug(f"Created uuid {prefix}{u32}")
    return f"{prefix}{u32}"

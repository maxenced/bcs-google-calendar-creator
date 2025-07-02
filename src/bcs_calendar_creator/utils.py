import base64
import datetime
import uuid
import logging
from zoneinfo import ZoneInfo


def build_start_end(
    day: str,
    start: str,
    duration: int,
) -> tuple[datetime.datetime, datetime.datetime]:
    """
    Build start and end datetime from a start and duration
    """
    start_date = datetime.datetime.strptime(f"{day} {start}", "%d/%m/%Y %Hh%M").replace(
        tzinfo=ZoneInfo("Europe/Paris"),
    )
    end_date = start_date + datetime.timedelta(minutes=duration)
    logging.debug(
        f"[build_start_date] build {start_date} / {end_date} from {day}, {start}, {duration}",
    )
    return start_date, end_date


def prefix(name: str, prepend="bcscal"):
    """
    Generate a prefix for this calendar
    @param prepend : prefix to be prepended to the id
    @param name: name to generate id from
    """
    curated_name = "".join([c for c in name if c in "abcdefghijklmnopqrstuv0123456789"])
    prepend += curated_name[:4]

    return prepend


def create_id(prefix: str) -> str:
    """Create a base32hex ID which can be used as Google Calendar Event id
    @return a base32hex string starting by prefix and with the first 4 chars from `name` which are valid with base32hex
    """
    u = uuid.uuid4()

    u32: str = base64.b32hexencode(u.bytes).decode("utf-8").lower().strip("=")
    logging.debug(f"Created uuid {prefix}{u32}")
    return f"{prefix}{u32}"

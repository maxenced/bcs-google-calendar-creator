import datetime
import logging
from googleapiclient.discovery import Resource

from bcs_calendar_creator.utils import build_start_end, create_id


class Category:
    """
    Manage a single category (usually a single class or type of event)
    """

    def __init__(self, name: str, service, config: dict) -> None:
        """
        @param config : The full configuration item from configuration.yaml (one of the `categories` node)
        """
        self._name = name
        self._config = config
        self._calendar = config["calendar"]
        self._defaults = config.get("default", {})
        self._items = config["items"]
        self._service = service
        self._existing = self._load_existing()

    def update(self):
        """
        Create or update all items from category.items
        """
        logging.info(f"Config : {self._config}")
        for item in self._config.get("items", []):
            item.update(self._config["default"])
            logging.info(item)
            self._create_event(item)

    def _create_event(self, event: dict, override=True) -> None:
        """
        Create a new event
        @param event : Event desc as dict
        @param override: If an event already exists with an overlapping timeslot, replace it
        """
        logging.info(f"Adding event {event['title']} to {self._calendar}")
        if override:
            start, end = build_start_end(
                event["start_day"],
                event["start_time"],
                event["duration"],
            )
            for existing in self._existing:
                if self._conflicts(existing, start, end):
                    logging.info(
                        f"Event {existing['name']} conflicts with new event start/end time {start}/{end}, will delete it",
                    )
                    self._service.events().delete(
                        calendarId=self._calendar,
                        eventId=existing.get("id"),
                    ).execute()
        ev = self._build_event(event)
        self._service.events().insert(calendarId=self._calendar, body=ev).execute()

    def _build_event(self, spec: dict) -> dict:
        """
        Build an event from spec
        """
        start, end = build_start_end(
            spec["start_day"],
            spec["start_time"],
            spec["duration"],
        )
        event = {
            "id": create_id(),
            "summary": spec["title"],
            "location": spec["location"],
            "description": spec["description"],
            "start": {
                "dateTime": start.isoformat(),
                "timeZone": "Europe/Paris",
            },
            "end": {
                "dateTime": end.isoformat(),
                "timeZone": "Europe/Paris",
            },
        }
        return event

    def _load_existing(self) -> list:
        """
        Loads existing events in this calendar from now
        Returns a list of events
        """
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        events_result = (
            self._service.events()
            .list(
                calendarId=self._calendar,
                timeMin=now,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events: list[Resource] = events_result.get("items", [])
        logging.info(f"Found {len(events)} upcoming events in {self._name} calendar")
        return events

    def _conflicts(
        self,
        event,
        start: datetime.datetime,
        end: datetime.datetime,
    ) -> bool:
        """
        Check if an event conflicts with a time slot. It will conflict if there is any override
        @param event : An existing calendar event
        @param start : Start of time slot to check
        @param end : End of time slot to check
        @return : True if any part of the event occurs between start and end
        """
        event_start = event["start"].get("dateTime", event["start"].get("date"))
        event_end = event["end"].get("dateTime", event["end"].get("date"))
        res = (event_start >= start and event_start <= end) or (
            event_end >= start and event_end <= end
        )
        if res:
            logging.debug(
                f"Event {event['name']} conflicts with start {start} / end {end}",
            )
        return res

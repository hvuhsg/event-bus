from typing import Union
from datetime import datetime


class Event:
    def __init__(self, payload: dict, dispatched_at: datetime):
        self.payload = payload
        self.dispatched_at = dispatched_at

    def to_dict(self) -> dict:
        return {
            "payload": self.payload,
            "dispatched_at": self.dispatched_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, event_dict: dict):
        return cls(
            payload=event_dict["payload"],
            dispatched_at=datetime.fromisoformat(event_dict["dispatched_at"]),
        )

    def __eq__(self, other):
        if isinstance(other, Event):
            other = other.dispatched_at

        return self.dispatched_at == other

    def __gt__(self, other: Union["Event", datetime]):
        if isinstance(other, Event):
            other = other.dispatched_at

        return self.dispatched_at > other

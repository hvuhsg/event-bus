from typing import Union
from datetime import datetime


class Event:
    def __init__(self, topic: str, payload: dict, dispatched_at: datetime):
        self.topic = topic
        self.payload = payload
        self.dispatched_at = dispatched_at

    def __eq__(self, other):
        if isinstance(other, Event):
            other = other.dispatched_at

        return self.dispatched_at == other

    def __gt__(self, other: Union["Event", datetime]):
        if isinstance(other, Event):
            other = other.dispatched_at

        return self.dispatched_at > other

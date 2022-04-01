from typing import Dict, List, Optional, Set, Union
from dataclasses import dataclass
from collections import defaultdict
from datetime import datetime
from bisect import bisect_right

import jsonschema

from .event import Event
from .exceptions import InvalidEventSchemaException
from .exceptions import InvalidPayloadException


@dataclass
class ConsumeConfig:
    offset: Union[int, None] = 0
    from_date: Optional[datetime] = None


class EventBus:
    def __init__(self):
        self.queues: Dict[str, List[Event]] = defaultdict(list)
        self.subscribe_queues: Set[str] = set()
        self.queues_consume_config: Dict[str, ConsumeConfig] = defaultdict(
            ConsumeConfig
        )
        self.queues_schemas: Dict[str, dict] = {}

    def register_event_schema(self, event_name, /, *, schema: dict):
        try:
            jsonschema.validate({}, schema)
        except jsonschema.SchemaError as e:
            raise InvalidEventSchemaException() from e
        except jsonschema.ValidationError as e:
            pass

        self.queues_schemas[event_name] = schema

    def dispatch(self, event_name: str, /, *, payload: dict) -> datetime:
        if schema := self.queues_schemas.get(event_name):
            try:
                jsonschema.validate(instance=payload, schema=schema)
            except jsonschema.ValidationError as e:
                raise InvalidPayloadException() from e

        dispatch_time = datetime.now()
        event = Event(name=event_name, payload=payload, dispatched_at=dispatch_time)
        self.queues[event_name].append(event)
        return dispatch_time

    def get(self) -> Union[Event, None]:
        for event_name in self.subscribe_queues:
            consume_config = self.queues_consume_config[event_name]
            queue = self.queues[event_name]

            if not queue:
                continue

            if consume_config.offset is None and consume_config.from_date:
                if queue[-1].dispatched_at >= consume_config.from_date:
                    consume_config.offset = len(queue) - 1
                    offset = consume_config.offset
                else:
                    continue
            elif consume_config.offset is not None:
                offset = consume_config.offset
            else:
                continue

            if len(queue) <= offset:
                continue

            consume_config.offset += 1

            return queue[offset]

        return None

    def subscribe_to(
        self, event_name, /, *, offset: Optional[int] = 0, from_date: datetime = None
    ):
        if offset and from_date is not None:
            raise ValueError("Can't pass offset AND from_date")

        if from_date is not None:
            offset = self._calculate_offset_from_date(event_name, from_date)

        consume_config = ConsumeConfig(offset=offset, from_date=from_date)
        self.queues_consume_config[event_name] = consume_config
        self.subscribe_queues.add(event_name)

    def _calculate_offset_from_date(
        self, event_name: str, from_date: datetime
    ) -> Optional[int]:
        queue = self.queues[event_name]
        i = bisect_right(queue, from_date)

        if i == len(queue):
            return None

        return i

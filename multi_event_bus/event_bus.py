from threading import Event as Locker
from asyncio import Event as AsyncLocker
from typing import Dict, List, Optional, Set, Union, Any
from collections import defaultdict
from datetime import datetime
from bisect import bisect_right

import jsonschema

from .event import Event
from .exceptions import InvalidEventSchemaException
from .exceptions import InvalidPayloadException
from .consume_config import ConsumeConfig
from .multi_lock import MultiLock, AsyncMultiLock


class EventBus:
    LockerClass: type = Locker
    MultiLockClass: type = MultiLock

    def __init__(self):
        self.queues: Dict[str, List[Event]] = defaultdict(list)
        self.subscribe_queues: Set[str] = set()
        self.queues_schemas: Dict[str, dict] = {}
        self.queue_locks: Dict[str, Any] = defaultdict(self.LockerClass)

    def register_event_schema(self, event_name, /, *, schema: dict):
        try:
            jsonschema.validate({}, schema)
        except jsonschema.SchemaError as e:
            raise InvalidEventSchemaException() from e
        except jsonschema.ValidationError:
            pass

        self.queues_schemas[event_name] = schema

    def dispatch(self, topic: str, /, *, payload: dict) -> datetime:
        if schema := self.queues_schemas.get(topic):
            try:
                jsonschema.validate(instance=payload, schema=schema)
            except jsonschema.ValidationError as e:
                raise InvalidPayloadException() from e

        dispatch_time = datetime.now()
        event = Event(topic=topic, payload=payload, dispatched_at=dispatch_time)
        self.queues[topic].append(event)

        self.queue_locks[topic].set()
        del self.queue_locks[topic]

        return dispatch_time

    def _get(
        self, topics, topics_config: Dict[str, ConsumeConfig]
    ) -> Union[Event, None]:
        for topic in topics:
            queue = self.queues[topic]
            config = topics_config[topic]

            if not queue:
                continue

            if config.offset is None and config.from_date is not None:
                config.offset = self._calculate_offset_from_date(
                    topic, config.from_date
                )

            if config.offset is None and config.from_date:
                if queue[-1].dispatched_at >= config.from_date:
                    config.offset = len(queue) - 1
                    offset = config.offset
                else:
                    continue
            elif config.offset is not None:
                offset = config.offset
            else:
                continue

            if len(queue) <= offset:
                continue

            config.offset += 1

            return queue[offset]

        return None

    def get(self, topics, topics_config: Dict[str, ConsumeConfig]):
        if (event := self._get(topics, topics_config)) is not None:
            return event

        locks = [self.queue_locks[topic] for topic in topics]
        or_event = MultiLock(*locks)
        or_event.wait()

        return self.get(topics, topics_config)

    def _calculate_offset_from_date(
        self, topic: str, /, from_date: datetime
    ) -> Optional[int]:
        queue = self.queues[topic]
        i = bisect_right(queue, from_date)

        if i == len(queue):
            return None

        return i


class AsyncEventBus(EventBus):
    LockerClass = AsyncLocker
    MultiLockClass = AsyncMultiLock

    def _get(
        self, topics, topics_config: Dict[str, ConsumeConfig]
    ) -> Union[Event, None]:
        for topic in topics:
            queue = self.queues[topic]
            config = topics_config[topic]

            if not queue:
                continue

            if config.offset is None and config.from_date is not None:
                config.offset = self._calculate_offset_from_date(
                    topic, config.from_date
                )

            if config.offset is None and config.from_date:
                if queue[-1].dispatched_at >= config.from_date:
                    config.offset = len(queue) - 1
                    offset = config.offset
                else:
                    continue
            elif config.offset is not None:
                offset = config.offset
            else:
                continue

            if len(queue) <= offset:
                continue

            config.offset += 1

            return queue[offset]

        return None

    async def get(self, topics, topics_config: Dict[str, ConsumeConfig]):
        if (event := self._get(topics, topics_config)) is not None:
            return event

        locks = [self.queue_locks[topic] for topic in topics]
        or_event = AsyncMultiLock(*locks)
        await or_event.wait()

        return await self.get(topics, topics_config)

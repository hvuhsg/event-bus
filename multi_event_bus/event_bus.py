from threading import Event as Locker
from asyncio import Event as AsyncLocker
from typing import Dict, List, Set, Union, Any, Tuple, Coroutine
from collections import defaultdict
from datetime import datetime
import json

import redis
import aioredis
import jsonschema

from .event import Event
from .exceptions import InvalidEventSchemaException
from .exceptions import InvalidPayloadException
from .multi_lock import MultiLock, AsyncMultiLock


class EventBus:
    LockerClass: type = Locker
    MultiLockClass: type = MultiLock
    RedisClass: type = redis.Redis

    def __init__(self, redis_host: str, redis_port: int):
        self.queues: Dict[str, List[Event]] = defaultdict(list)
        self.subscribe_queues: Set[str] = set()
        self.queues_schemas: Dict[str, dict] = {}
        self.queue_locks: Dict[str, Any] = defaultdict(self.LockerClass)
        self._redis_conn = self.RedisClass(
            host=redis_host, port=redis_port, socket_timeout=5
        )

    def subscribe_to(
        self, topic: str, consumer_id: str, offset: int
    ) -> Union[bool, Coroutine]:
        is_new_topic = self._redis_conn.hsetnx(consumer_id, topic, offset)
        return bool(is_new_topic)

    def register_event_schema(self, topic, /, *, schema: dict):
        try:
            jsonschema.validate({}, schema)
        except jsonschema.SchemaError as e:
            raise InvalidEventSchemaException() from e
        except jsonschema.ValidationError:
            pass

        self._redis_conn.hset("schemas", topic, json.dumps(schema))

    def dispatch(self, topic: str, /, *, payload: dict) -> Union[datetime, Coroutine]:
        schema_json = self._redis_conn.hget("schemas", topic)
        if schema_json:
            schema = json.loads(schema_json.decode())
            try:
                jsonschema.validate(instance=payload, schema=schema)
            except jsonschema.ValidationError as e:
                raise InvalidPayloadException() from e

        dispatch_time = datetime.now()
        event = Event(payload=payload, dispatched_at=dispatch_time)
        self._redis_conn.lpush(topic, json.dumps(event.to_dict()))

        self.queue_locks[topic].set()
        del self.queue_locks[topic]

        return dispatch_time

    def _get(self, consumer_id: str, consumer_config: dict):
        for topic, offset in consumer_config.items():
            offset = int(offset)
            event = self._redis_conn.lindex(topic, (-offset) - 1)

            if event is not None:
                self._redis_conn.hincrby(consumer_id, topic, 1)
            else:
                continue

            return Event.from_dict(json.loads(event.decode())), topic.decode()

        return None, None

    def get(self, consumer_id: str) -> Union[Tuple[Event, str], Coroutine]:
        consumer_config = self._redis_conn.hgetall(consumer_id)
        event, topic = self._get(consumer_id, consumer_config)

        if event is not None and topic is not None:
            return event, topic

        locks = [
            self.queue_locks[topic.decode()] for topic in list(consumer_config.keys())
        ]
        or_event = MultiLock(*locks)
        or_event.wait()

        return self.get(consumer_id)


class AsyncEventBus(EventBus):
    LockerClass = AsyncLocker
    MultiLockClass = AsyncMultiLock
    RedisClass = aioredis.Redis

    async def subscribe_to(self, topic: str, consumer_id: str, offset: int):
        is_new_topic = await self._redis_conn.hsetnx(consumer_id, topic, offset)
        return bool(is_new_topic)

    async def register_event_schema(self, topic, /, *, schema: dict):
        try:
            jsonschema.validate({}, schema)
        except jsonschema.SchemaError as e:
            raise InvalidEventSchemaException() from e
        except jsonschema.ValidationError:
            pass

        await self._redis_conn.hset("schemas", topic, json.dumps(schema))

    async def dispatch(self, topic: str, /, *, payload: dict) -> datetime:
        schema_json = await self._redis_conn.hget("schemas", topic)
        if schema_json:
            schema = json.loads(schema_json.decode())
            try:
                jsonschema.validate(instance=payload, schema=schema)
            except jsonschema.ValidationError as e:
                raise InvalidPayloadException() from e

        dispatch_time = datetime.now()
        event = Event(payload=payload, dispatched_at=dispatch_time)
        await self._redis_conn.lpush(topic, json.dumps(event.to_dict()))

        self.queue_locks[topic].set()
        del self.queue_locks[topic]

        return dispatch_time

    async def _get(
        self, consumer_id: str, consumer_config: dict
    ) -> Union[Tuple[Event, str], Tuple[None, None]]:
        for topic, offset in consumer_config.items():
            offset = int(offset)
            event = await self._redis_conn.lindex(topic, (-offset) - 1)

            if event is not None:
                await self._redis_conn.hincrby(consumer_id, topic, 1)
            else:
                continue

            return Event.from_dict(json.loads(event.decode())), topic.decode()

        return None, None

    async def get(self, consumer_id: str):
        consumer_config = await self._redis_conn.hgetall(consumer_id)
        event, topic = await self._get(consumer_id, consumer_config)
        if event:
            return event, topic

        locks = [
            self.queue_locks[topic.decode()] for topic in list(consumer_config.keys())
        ]
        or_event = self.MultiLockClass(*locks)

        await or_event.wait()

        return await self.get(consumer_id)

from typing import Set, Dict, Optional
from datetime import datetime
from collections import defaultdict

from .event_bus import EventBus, AsyncEventBus
from .consume_config import ConsumeConfig


class Consumer:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.topic_config: Dict[str, ConsumeConfig] = defaultdict(ConsumeConfig)
        self.subscribed_topics: Set[str] = set()

    def get(self):
        return self.event_bus.get(
            topics=self.subscribed_topics, topics_config=self.topic_config
        )

    def subscribe_to(
        self, topic, /, *, offset: Optional[int] = 0, from_date: datetime = None
    ):
        if offset and from_date is not None:
            raise ValueError("Can't pass offset AND from_date")

        if from_date is not None:
            offset = None

        consume_config = ConsumeConfig(offset=offset, from_date=from_date)
        self.topic_config[topic] = consume_config
        self.subscribed_topics.add(topic)


class AsyncConsumer(Consumer):
    def __init__(self, event_bus: AsyncEventBus):
        super().__init__(event_bus)

    async def get(self):
        return await self.event_bus.get(
            topics=self.subscribed_topics, topics_config=self.topic_config
        )

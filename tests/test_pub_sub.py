from threading import Timer
from datetime import timedelta, datetime

import pytest

from multi_event_bus import EventBus
from multi_event_bus import Consumer


@pytest.fixture(scope="function")
def event_bus():
    return EventBus()


@pytest.fixture(scope="function")
def consumer(event_bus):
    return Consumer(event_bus)


def test_simple_pub_sub(event_bus, consumer):
    consumer.subscribe_to("user-registered")

    dispatch_time = event_bus.dispatch(
        "user-registered", payload={"id": 5, "username": "mosh", "age": 17}
    )

    event = consumer.get()

    assert event.topic == "user-registered"
    assert event.dispatched_at == dispatch_time
    assert event.payload == {"id": 5, "username": "mosh", "age": 17}


def test_consume_with_offset(event_bus, consumer):
    event_bus.dispatch(
        "user-registered", payload={"id": 5, "username": "mosh", "age": 17}
    )
    event_bus.dispatch(
        "user-registered", payload={"id": 6, "username": "josh", "age": 21}
    )

    consumer.subscribe_to("user-registered", offset=1)
    event = consumer.get()

    assert event.topic == "user-registered"
    assert event.payload == {"id": 6, "username": "josh", "age": 21}


def test_consume_from_date(event_bus, consumer):
    event_bus.dispatch(
        "user-registered", payload={"id": 5, "username": "mosh", "age": 17}
    )
    dispatch_time = event_bus.dispatch(
        "user-registered", payload={"id": 6, "username": "josh", "age": 21}
    )

    consumer.subscribe_to("user-registered", from_date=dispatch_time)
    event = consumer.get()

    assert event.topic == "user-registered"
    assert event.payload == {"id": 6, "username": "josh", "age": 21}


def test_consume_from_future_date(event_bus, consumer):
    consumer.subscribe_to(
        "user-registered", from_date=datetime.now() + timedelta(seconds=1)
    )

    event_bus.dispatch(
        "user-registered", payload={"id": 6, "username": "josh", "age": 21}
    )

    Timer(
        interval=1,
        function=event_bus.dispatch,
        args=("user-registered",),
        kwargs={"payload": {"id": 7, "username": "josh2", "age": 25}},
    ).start()

    event = consumer.get()

    assert event is not None
    assert event.topic == "user-registered"
    assert event.payload == {"id": 7, "username": "josh2", "age": 25}

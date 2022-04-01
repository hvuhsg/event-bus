from datetime import timedelta, datetime
from time import sleep

import pytest

from event_bus import EventBus


@pytest.fixture(scope="function")
def event_bus():
    return EventBus()


def test_simple_pub_sub(event_bus):
    event_bus.subscribe_to("user-registered")

    dispatch_time = event_bus.dispatch(
        "user-registered", payload={"id": 5, "username": "mosh", "age": 17}
    )

    event = event_bus.get()

    assert event.name == "user-registered"
    assert event.dispatched_at == dispatch_time
    assert event.payload == {"id": 5, "username": "mosh", "age": 17}


def test_consume_with_offset(event_bus):
    event_bus.dispatch(
        "user-registered", payload={"id": 5, "username": "mosh", "age": 17}
    )
    event_bus.dispatch(
        "user-registered", payload={"id": 6, "username": "josh", "age": 21}
    )

    event_bus.subscribe_to("user-registered", offset=1)
    event = event_bus.get()

    assert event.name == "user-registered"
    assert event.payload == {"id": 6, "username": "josh", "age": 21}


def test_consume_from_date(event_bus):
    event_bus.dispatch(
        "user-registered", payload={"id": 5, "username": "mosh", "age": 17}
    )
    dispatch_time = event_bus.dispatch(
        "user-registered", payload={"id": 6, "username": "josh", "age": 21}
    )

    event_bus.subscribe_to("user-registered", from_date=dispatch_time)
    event = event_bus.get()

    assert event.name == "user-registered"
    assert event.payload == {"id": 6, "username": "josh", "age": 21}


def test_consume_from_future_date(event_bus):
    event_bus.subscribe_to(
        "user-registered", from_date=datetime.now() + timedelta(seconds=1)
    )

    event_bus.dispatch(
        "user-registered", payload={"id": 6, "username": "josh", "age": 21}
    )
    event = event_bus.get()

    assert event is None

    sleep(1)
    event_bus.dispatch(
        "user-registered", payload={"id": 7, "username": "josh2", "age": 25}
    )
    event = event_bus.get()

    assert event.name == "user-registered"
    assert event.payload == {"id": 7, "username": "josh2", "age": 25}

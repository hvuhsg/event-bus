import pytest

from event_bus import EventBus
from event_bus.exceptions import InvalidEventSchemaException, InvalidPayloadException


@pytest.fixture(scope="function")
def event_bus():
    return EventBus()


def test_schema_registering(event_bus):
    invalid_schema = {"type": "abcd"}

    with pytest.raises(InvalidEventSchemaException):
        event_bus.register_event_schema("event-name", schema=invalid_schema)

    valid_schema = {
        "type": "object",
        "properties": {
            "price": {"type": "number"},
            "name": {"type": "string"},
        },
    }
    event_bus.register_event_schema("event-name", schema=valid_schema)


def test_schema_enforcement(event_bus):
    valid_schema = {
        "type": "object",
        "properties": {
            "price": {"type": "number"},
            "name": {"type": "string"},
        },
    }
    event_bus.register_event_schema("event-name", schema=valid_schema)

    with pytest.raises(InvalidPayloadException):
        event_bus.dispatch("event-name", payload={"price": "5.2$"})

    event_bus.dispatch("event-name", payload={"name": "table", "price": 5})

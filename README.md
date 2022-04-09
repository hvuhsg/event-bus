# event-bus
[![Run Tests](https://github.com/hvuhsg/event-bus/actions/workflows/test.yml/badge.svg)](https://github.com/hvuhsg/event-bus/actions/workflows/test.yml)  
EventBus implementation in python


### Examples
#### sync

```python
from multi_event_bus import EventBus

eb = EventBus(redis_host="127.0.0.1", redis_port=6379)

eb.dispatch("event-name", payload={"num": 1})

eb.subscribe_to("event-name", consumer_id="consumer-1", offset=0)

event, topic = eb.get(consumer_id="consumer-1")  # Blocking

print(event.payload)  # -> {"num": 1}
```
#### async

```python
from multi_event_bus import AsyncEventBus

eb = AsyncEventBus(redis_host="127.0.0.1", redis_port=6379)

eb.dispatch("event-name", payload={"num": 1})

eb.subscribe_to("event-name", consumer_id="consumer-2", offset=0)

event, topic = await eb.get(consumer_id="consumer-2")

print(event.payload)  # -> {"num": 1}
```
#### register event schema

```python
from multi_event_bus import EventBus

eb = EventBus(redis_host="127.0.0.1", redis_port=6379)

# Enforce json schema of event
json_schema = {
    "type": "object",
    "properties": {"num": {"type": "string"}}
}
eb.register_event_schema("event-name", schema=json_schema)

eb.dispatch("event-name", payload={"num": "7854"})

eb.subscribe_to("event-name", consumer_id="consumer-3", offset=0)

event, topic = eb.get(consumer_id="consumer-3")  # Blocking

print(event.payload)  # -> {"num": "7854"}
```

### Development
#### scripts
```commandline
poetry run run_pytest
poetry run run_flake8
poetry run run_mypy
poetry run run_black
```
#### run tests
```commandline
poetry run test
```

#### run all (test and black)
```commandline
poetry run all
```

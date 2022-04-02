# event-bus
[![Run Tests](https://github.com/hvuhsg/event-bus/actions/workflows/test.yml/badge.svg)](https://github.com/hvuhsg/event-bus/actions/workflows/test.yml)  
EventBus implementation in python


### Examples
#### sync
```python
from event_bus import EventBus, Consumer

eb = EventBus()
consumer = Consumer(eb)

eb.dispatch("event-name", payload={"num": 1})

consumer.subscribe_to("event-name")

event = consumer.get()  # Blocking

print(event.payload) # -> {"num": 1}
```
#### async
```python
from event_bus import AsyncEventBus, AsyncConsumer

eb = AsyncEventBus()
consumer = AsyncConsumer(eb)

eb.dispatch("event-name", payload={"num": 1})

consumer.subscribe_to("event-name")

event = await consumer.get()

print(event.payload) # -> {"num": 1}
```
#### register event schema
```python
from event_bus import EventBus, Consumer

eb = EventBus()
consumer = Consumer(eb)

# Enforce json schema of event
json_schema = {
    "type": "object",
    "properties": {"num": {"type": "string"}}
}
eb.register_event_schema("event-name", schema=json_schema)

eb.dispatch("event-name", payload={"num": "7854"})

consumer.subscribe_to("event-name")

event = consumer.get()  # Blocking

print(event.payload) # -> {"num": "7854"}
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

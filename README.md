# event-bus
EventBus implementation in python


### Example
```python
from event_bus import EventBus

eb = EventBus()

eb.dispatch("event-name", payload={"num": 1})

eb.subscribe_to("event-name")

event = eb.get()

print(event.payload) # -> {"num": 1}
```

```python
from event_bus import EventBus

eb = EventBus()

# Enforce json schema of event
json_schema = {
    "type": "object",
    "properties": {"num": {"type": "string"}}
}
eb.register_event_schema("event-name", schema=json_schema)

eb.dispatch("event-name", payload={"num": "7854"})

eb.subscribe_to("event-name")

event = eb.get()

print(event.payload) # -> {"num": "7854"}
```
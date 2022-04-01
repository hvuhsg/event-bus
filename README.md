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

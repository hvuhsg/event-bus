from threading import Event
from asyncio import Event as AsyncEvent


class MultiLock:
    EventLockClass: type = Event

    def __init__(self, *events):
        self.events = events
        self.root_event = self.EventLockClass()
        self._orify()
        self._changed()

    def _orify(self):
        def set_and_notify(event):
            event.i_set()
            event.changed()

        def clear_and_notify(event):
            event.i_clear()
            event.changed()

        for e in self.events:
            e.i_set = e.set
            e.i_clear = e.clear
            e.changed = self._changed
            e.set = lambda: set_and_notify(e)
            e.clear = lambda: clear_and_notify(e)

    def _changed(self):
        bools = [e.is_set() for e in self.events]
        if any(bools):
            self.root_event.set()
        else:
            self.root_event.clear()

    def wait(self):
        self.root_event.wait()


class AsyncMultiLock(MultiLock):
    EventLockClass: type = AsyncEvent

    async def wait(self):
        await self.root_event.wait()

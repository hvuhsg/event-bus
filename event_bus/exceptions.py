class EventBusException(Exception):
    pass


class InvalidEventSchemaException(EventBusException):
    pass


class InvalidPayloadException(EventBusException):
    pass

import asyncio


async def test_simple_pub_sub(async_event_bus, consumer_id, topic):
    await async_event_bus.subscribe_to(consumer_id, topic, 0)

    dispatch_time = await async_event_bus.dispatch(
        topic, payload={"id": 5, "username": "mosh", "age": 17}
    )

    event, res_topic = await async_event_bus.get(consumer_id)

    assert res_topic == topic
    assert event.dispatched_at == dispatch_time
    assert event.payload == {"id": 5, "username": "mosh", "age": 17}


async def test_consume_with_offset(async_event_bus, consumer_id, topic):
    await async_event_bus.dispatch(
        topic, payload={"id": 5, "username": "mosh", "age": 17}
    )
    await async_event_bus.dispatch(
        topic, payload={"id": 6, "username": "josh", "age": 21}
    )

    await async_event_bus.subscribe_to(consumer_id, topic, offset=1)
    event, res_topic = await async_event_bus.get(consumer_id)

    assert res_topic == topic
    assert event.payload == {"id": 6, "username": "josh", "age": 21}


async def test_multi_lock(async_event_bus, consumer_id, topic):
    async def call_dispatch():
        await async_event_bus.dispatch(topic, payload={"a": 1})

    loop = asyncio.get_event_loop()
    loop.call_later(1, lambda: asyncio.ensure_future(call_dispatch()))

    await async_event_bus.subscribe_to(consumer_id, topic, offset=0)
    event, res_topic = await async_event_bus.get(consumer_id)

    assert res_topic == topic
    assert event.payload == {"a": 1}

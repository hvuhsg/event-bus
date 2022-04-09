from threading import Timer


def test_simple_pub_sub(event_bus, consumer_id, topic):
    event_bus.subscribe_to(topic, consumer_id, 0)

    dispatch_time = event_bus.dispatch(
        topic, payload={"id": 5, "username": "mosh", "age": 17}
    )

    event, res_topic = event_bus.get(consumer_id)

    assert res_topic == topic
    assert event.dispatched_at == dispatch_time
    assert event.payload == {"id": 5, "username": "mosh", "age": 17}


def test_consume_with_offset(event_bus, consumer_id, topic):
    event_bus.dispatch(topic, payload={"id": 5, "username": "mosh", "age": 17})
    event_bus.dispatch(topic, payload={"id": 6, "username": "josh", "age": 21})

    event_bus.subscribe_to(topic, consumer_id, offset=1)
    event, res_topic = event_bus.get(consumer_id)

    assert res_topic == topic
    assert event.payload == {"id": 6, "username": "josh", "age": 21}


def test_multi_lock(event_bus, consumer_id, topic):
    Timer(
        interval=2,
        function=event_bus.dispatch,
        args=(topic,),
        kwargs={"payload": {"a": 1}},
    ).start()

    event_bus.subscribe_to(topic, consumer_id, offset=0)
    event, res_topic = event_bus.get(consumer_id)

    assert res_topic == topic
    assert event.payload == {"a": 1}

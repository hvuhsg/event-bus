import subprocess
from pathlib import Path
from uuid import uuid4

import pytest

from multi_event_bus import EventBus, AsyncEventBus


WORKDIR = str(Path(__file__).parent.absolute())


@pytest.fixture(scope="session")
def redis_instance():
    exit_code = subprocess.run(["docker-compose", "up", "-d"], cwd=WORKDIR)
    yield exit_code
    subprocess.run(["docker-compose", "down"], cwd=WORKDIR)


@pytest.fixture(scope="function")
def event_bus(redis_instance):
    return EventBus(redis_host="127.0.0.1", redis_port=8000)


@pytest.fixture(scope="function")
def async_event_bus(redis_instance) -> AsyncEventBus:
    return AsyncEventBus(redis_host="127.0.0.1", redis_port=8000)


@pytest.fixture(scope="function")
def consumer_id():
    return str(uuid4())


@pytest.fixture(scope="function")
def topic():
    return str(uuid4())

import pytest
import random
import string
from datetime import \
    datetime
from bson import \
    utc
from sys import \
    path, \
    maxsize

path.append('../')

from trema_database import \
    get_trema_database, \
    _TremaDatabase


@pytest.fixture
def welcome_doc():
    welcome_doc = {
        "_id": random.randint(0, maxsize),
        "welcome_msg": ''.join(random.choice(string.printable) for _ in range(10)),
        "reminder_delay": 15 * 60,
        "reminder_msg": ''.join(random.choice(string.printable) for _ in range(10)),
        "leave_msg": ''.join(random.choice(string.printable) for _ in range(10)),
        "welcome_chan_id": random.randint(0, maxsize)
    }
    return welcome_doc


@pytest.fixture
def server_doc(welcome_doc):
    server_doc = {
        "_id": random.randint(0, maxsize),
        "name": ''.join(random.choice(string.printable) for _ in range(10)),
        "joined_at": datetime.isoformat(datetime.now(tz=utc)),
        "announce_chan_id": random.randint(0, maxsize),
        "welcome_id": welcome_doc["_id"]
    }
    return server_doc


@pytest.fixture
def database(welcome_doc, server_doc):
    database = _TremaDatabase("trema_test", "mongodb://root:root@localhost:27017/?authSource=admin")
    database.add_document("welcome", welcome_doc)
    database.add_document("server", server_doc)
    yield database

    database._database.welcome.delete_many({})
    database._database.server.delete_many({})


def test_retrieved_database():
    db = get_trema_database()
    assert db is not None


def test_add_document(database, welcome_doc, server_doc):
    welcome_document = database._database.welcome.find_one({"_id": welcome_doc["_id"]})
    server_document = database._database.server.find_one({"_id": server_doc["_id"]})

    assert welcome_document is not None
    assert server_document is not None

    assert welcome_document == welcome_doc
    assert server_document == server_doc


def test_get_server_ids(database, welcome_doc, server_doc):
    server_ids = list()
    server_ids.append(server_doc["_id"])

    for i in range(3):
        server_docs = {
            "_id": database.generate_rand_id("server"),
            "name": "Server {}".format(i),
            "joined_at": "2019-01-01 00:00:00",
            "announce_chan_id": random.randint(0, maxsize),
            "welcome_id": welcome_doc["_id"]
        }
        database.add_document("server", server_docs)
        server_ids.append(server_docs["_id"])

    retrieved_server_ids = database.get_server_ids()
    assert retrieved_server_ids is not None
    assert retrieved_server_ids == server_ids


def test_get_server_leave_msg(database, welcome_doc, server_doc):
    leave_msg = database.get_server_leave_msg(server_doc["_id"])
    assert leave_msg is not None
    assert leave_msg == welcome_doc["leave_msg"]


def test_get_server_reminder_delay(database, welcome_doc, server_doc):
    reminder_delay = database.get_server_reminder_delay(server_doc["_id"])
    assert reminder_delay is not None
    assert reminder_delay == welcome_doc["reminder_delay"]


def test_get_server_reminder_msg(database, welcome_doc, server_doc):
    reminder_msg = database.get_server_reminder_msg(server_doc["_id"])
    assert reminder_msg is not None
    assert reminder_msg == welcome_doc["reminder_msg"]


def test_get_server_welcome_chan_id(database, welcome_doc, server_doc):
    welcome_chan_id = database.get_server_welcome_chan_id(server_doc["_id"])
    assert welcome_chan_id is not None
    assert welcome_chan_id == welcome_doc["welcome_chan_id"]


def test_get_server_welcome_msg(database, welcome_doc, server_doc):
    welcome_msg = database.get_server_welcome_msg(server_doc["_id"])
    assert welcome_msg is not None
    assert welcome_msg == welcome_doc["welcome_msg"]


def test_set_server_leave_msg(database, welcome_doc, server_doc):
    new_leave_msg = ''.join(random.choice(string.printable) for _ in range(10))
    database.set_server_leave_msg(server_doc["_id"], new_leave_msg)
    leave_msg = database.get_server_leave_msg(server_doc["_id"])
    assert leave_msg is not None
    assert leave_msg == new_leave_msg


def test_set_server_reminder_delay(database, welcome_doc, server_doc):
    new_reminder_delay = 30*60
    database.set_server_reminder_delay(server_doc["_id"], new_reminder_delay)
    reminder_delay = database.get_server_reminder_delay(server_doc["_id"])
    assert reminder_delay is not None
    assert reminder_delay == new_reminder_delay


def test_set_server_reminder_msg(database, welcome_doc, server_doc):
    new_reminder_msg = ''.join(random.choice(string.printable) for _ in range(10))
    database.set_server_reminder_msg(server_doc["_id"], new_reminder_msg)
    reminder_msg = database.get_server_reminder_msg(server_doc["_id"])
    assert reminder_msg is not None
    assert reminder_msg == new_reminder_msg


def test_set_server_welcome_chan_id(database, welcome_doc, server_doc):
    new_welcome_chan_id = random.randint(0, maxsize)
    database.set_server_welcome_chan_id(server_doc["_id"], new_welcome_chan_id)
    welcome_chan_id = database.get_server_welcome_chan_id(server_doc["_id"])
    assert welcome_chan_id is not None
    assert welcome_chan_id == new_welcome_chan_id


def test_set_server_welcome_msg(database, welcome_doc, server_doc):
    new_welcome_msg = ''.join(random.choice(string.printable) for _ in range(10))
    database.set_server_welcome_msg(server_doc["_id"], new_welcome_msg)
    welcome_msg = database.get_server_welcome_msg(server_doc["_id"])
    assert welcome_msg is not None
    assert welcome_msg == new_welcome_msg

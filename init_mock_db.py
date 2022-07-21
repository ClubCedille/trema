from bson import utc
from datetime import datetime

from trema_database import\
	AlreadyExistError,\
	_TremaDatabase

try:
	date = datetime.isoformat(datetime.now(tz=utc))

	trema_database = _TremaDatabase(
		"tremasim", "mongodb://root:root@localhost:27017/?authSource=admin")

	welcome_doc = {
		"_id": 71049752,
		"active": False,
		"welcome_msg": "Welcome to group 5 server",
		"reminder_msg": "Come to read the instructions.",
		"leave_msg": "Goodbye",
        "instruct_chan_id": 666
	}

	server_doc = {
		"_id": 4820316,
		"name": "Cursus G-5",
		"joinedAt": date,
		"welcome_id": 71049752
	}

	col_welcome = "welcome"
	col_server = "server"

	trema_database.add_document(col_welcome, welcome_doc)
	trema_database.add_document(col_server, server_doc)

except AlreadyExistError as e:
	print(e)

except TypeError as e:
	print(e)

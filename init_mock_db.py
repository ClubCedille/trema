from bson import utc
from datetime import datetime

from trema_database import\
	AlreadyExistError,\
	_TremaDatabase


try:
	date = datetime.isoformat(datetime.now(tz=utc))

	trema_database = _TremaDatabase(
		"tremasim", "mongodb://root:root@localhost:27017/?authSource=admin")

	welcomeDoc = {
		"_id": 29387389,
		"activer": False,
		"message": "Welcome to group 5 server",
		"channel_id": 120947329,
		"club_id": 569733982
	}

	serveurDoc = {
		"_id": 459837,
		"name": "Cursus G-5",
		"joinedAt": date
	}

	welcome = "welcome"
	serveur = "serveur"

	trema_database.add_document(welcome, welcomeDoc)
	trema_database.add_document(serveur, serveurDoc)

except AlreadyExistError as e:
	print(e)

except TypeError as e:
	print(e)

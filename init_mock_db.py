from bson import utc
from datetime import datetime

from trema_database import\
	AlreadyExistError,\
	InvalidParameterError,\
	_TremaDatabase


try:
	date = datetime.isoformat(datetime.now(tz=utc))

	trema_database = _TremaDatabase(
		"tremasim", "mongodb://root:root@localhost:27017/?authSource=admin")

	welcome_doc = {
		"_id": 969352397090586627,
		"active": True,
		"welcome_msg": "Heille! Bienvenue au Club CEDILLE! Suis les instructions dans #accueil pour avoir accès au reste du serveur!",
		"reminder_msg": "Viens dans accueil pour t'attribuer un rôle!",
		"leave_msg": " a quitté le serveur.",
        "instruct_chan_id": 980209198023467029
	}

	server_doc = {
		"_id": 969352397090586624,
		"name": "Les Amis de Choupie",
		"joined_at": date,
		"announce_chan_id": 1019348458672488468,
		"welcome_id": 969352397090586627
	}

	col_welcome = "welcome"
	col_server = "server"

	trema_database.add_document(col_welcome, welcome_doc)
	trema_database.add_document(col_server, server_doc)

except AlreadyExistError as e:
	print(e)

except InvalidParameterError as e:
	print(e)

except TypeError as e:
	print(e)

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
		"_id": 20918303,
		"activer": False,
		"message": "Welcome to Cedille Club",
		"channel_id": 120947329,
		"club_id": 569733982,
		"joinedAt": date
	}

	serveurDoc = {
		"_id": 569733982,
		"name": "Cohorte 2022",
		"joinedAt": date
	}

	welcome = "welcome"
	serveur = "serveur"

	trema_database.add_document(welcome, welcomeDoc)
	trema_database.add_document(serveur, serveurDoc)

	welcomeCol = trema_database._database[welcome]
	serveurCol = trema_database._database[serveur]

	insertedWelcomeDoc = welcomeCol.find_one({"_id": welcomeDoc["_id"]})
	insertedServeurDoc = serveurCol.find_one({"_id": serveurDoc["_id"]})

	print(insertedWelcomeDoc)
	print(insertedServeurDoc)

except AlreadyExistError as e:
	print(e)
except TypeError as e:
	print(e)

# Prints the database content.
cursor = serveurCol.find({})
for document in cursor:
	print(document)

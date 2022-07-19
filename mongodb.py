from aifc import Error
from datetime import datetime
from bson import utc
from pymongo import MongoClient
from jsonschema import validate
from schema import getSchema

client = MongoClient("mongodb://root:root@localhost:27017/?authSource=admin")
mydb = client["trema"]

class AlreadyExistError(Error):
    def __init__(self, value):
        self.value = value

def addDocument(collectionName, doc):

    schema = getSchema(collectionName)

    validate(doc, schema=schema)

    collection = mydb[collectionName]

    docExiste = collection.find_one({"_id": doc["_id"]})

    if docExiste is not None:
        raise AlreadyExistError("Chatboot has already defined a message for this server")
    
    collection.insert_one(doc)

def getInformation():
    welcomeCol = mydb["welcome"]
    
    results = welcomeCol.aggregate([{
        "$lookup": {
            "from": "serveur",
            "localField": "club_id",
            "foreignField": "_id",
            "as": "serveur_info"
        }
    }])

    for doc in results:
        print(doc)

try:
    date = datetime.isoformat(datetime.now(tz=utc))

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
    
    addDocument(welcome, welcomeDoc)
    addDocument(serveur, serveurDoc)

    welcomeCol = mydb[welcome]
    serveurCol = mydb[serveur]

    insertedWelcomeDoc = welcomeCol.find_one({"_id": welcomeDoc["_id"]})
    insertedServeurDoc = serveurCol.find_one({"_id": serveurDoc["_id"]})

    print(insertedWelcomeDoc)
    print(insertedServeurDoc)

except AlreadyExistError as e:
    print(e)
except TypeError as e:
    print(e)

"""
This code is to print the db content

cursor = colServeur.find({})
for document in cursor:
    print(document)
"""

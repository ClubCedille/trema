from jsonschema import validate
from pymongo import MongoClient
from schema import getSchema


class AlreadyExistError(Exception):

	def __init__(self, message):
		Exception.__init__(self, message)


class _TremaDatabase:

	def __init__(self, name, connect_str):
		client = MongoClient(connect_str)
		self._database = client[name]

	def add_document(self, collection_name, document):
		schema = getSchema(collection_name)
		validate(document, schema=schema)

		collection = self._database[collection_name]
		doc_id = document["_id"]
		existing_doc = collection.find_one({"_id": doc_id})

		if existing_doc is not None:
			raise AlreadyExistError(f"Document {doc_id} already exists.")

		collection.insert_one(document)


database = _TremaDatabase(
	"trema", "mongodb://root:root@localhost:27017/?authSource=admin")

def get_trema_database():
	return database

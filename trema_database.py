from jsonschema import validate
from pymongo import MongoClient
from schemas import get_schema


class AlreadyExistError(Exception):

	def __init__(self, message):
		Exception.__init__(self, message)


class InvalidParameterError(Exception):

	def __init__(self, message):
		Exception.__init__(self, message)


class _TremaDatabase:

	def __init__(self, name, connect_str):
		client = MongoClient(connect_str)
		self._database = client[name]

	def add_document(self, collection_name, document):
		schema = get_schema(collection_name)
		validate(document, schema=schema)

		collection = self._database[collection_name]
		doc_id = document["_id"]
		existing_doc = collection.find_one({"_id": doc_id})

		if existing_doc is not None:
			raise AlreadyExistError(f"Document {doc_id} already exists.")

		collection.insert_one(document)

	def get_welcome_info(self, welcome_id):
		collection = self._database["welcome"]
		doc = collection.find_one({"_id": welcome_id})

		if doc is None:
			raise InvalidParameterError(
				f"Welcome channel {welcome_id} has not been defined.")
		
		return doc

	def get_server_info(self, server_id):
		collection = self._database["server"]
		doc = collection.find_one({"_id": server_id})

		if doc is None:
			raise InvalidParameterError(
				"Welcome message has yet to be defined for this server.")
		
		return doc


database = _TremaDatabase(
	"trema", "mongodb://root:root@localhost:27017/?authSource=admin")

def get_trema_database():
	return database

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
			raise InvalidParameterError("This server is unknown.")

		return doc


	def get_server_welcome_id(self, server_id):
		server_info = self.get_server_info(server_id)
		welcome_id = server_info.get("welcome_id")
		return welcome_id


	def _set_welcome_attr(self, welcome_id, attr_key, attr_val):
		welcome_col = self._database["welcome"]
		query = {"_id": welcome_id}
		update = {"$set": {attr_key: attr_val}}
		welcome_col.update_one(query, update)


	def set_welcome_chan_id(self, welcome_id, welcome_chan_id):
		self._set_welcome_attr(welcome_id, "welcome_chan_id", welcome_chan_id)


	def set_server_welcome_chan_id(self, server_id, welcome_chan_id):
		welcome_id = self.get_server_welcome_id(server_id)
		self.set_welcome_chan_id(welcome_id, welcome_chan_id)


	def set_welcome_msg(self, welcome_id, welcome_msg):
		self._set_welcome_attr(welcome_id, "welcome_msg", welcome_msg)


	def set_server_welcome_msg(self, server_id, welcome_msg):
		welcome_id = self.get_server_welcome_id(server_id)
		self.set_welcome_msg(welcome_id, welcome_msg)


database = _TremaDatabase(
	"trema", "mongodb://root:root@localhost:27017/?authSource=admin")

def get_trema_database():
	return database

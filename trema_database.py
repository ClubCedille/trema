from datetime import datetime
from jsonschema import validate
from pymongo import MongoClient
from random import randint
from schemas import get_schema
from sys import maxsize
import os

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

		collection = self._get_collection(collection_name)
		doc_id = document["_id"]

		if self._id_exists(doc_id, collection):
			raise AlreadyExistError(f"Document {doc_id} already exists.")

		collection.insert_one(document)

	def _ensure_col_is_obj(self, collection):
		"""
		Some methods in this class can take a collection name or a collection
		object as an argument. To ensure that a collection object will be used,
		give the argument to this method. If the argument is a collection name,
		this method will return the corresponding collection object. If the
		argument is a collection object, this method will return the collection
		object.

		If argument collection is the name of an unexisting collection, a
		collection with this name is created.

		Args:
			collection (str or pymongo.collection.Collection): a collection
				name or a collection object

		Returns:
			pymongo.collection.Collection: a collection object
		"""
		if isinstance(collection, str):
			collection = self._get_collection(collection)

		return collection

	def generate_rand_id(self, collection):
		collection = self._ensure_col_is_obj(collection)

		existing_doc = "not None"

		while existing_doc is not None:
			rand_id = randint(0, maxsize)
			existing_doc = collection.find_one({"_id": rand_id})

		return rand_id

	def _get_collection(self, collection_name):
		"""
		Given a collection name, this method provides the collection object
		that it designates. If the collection does not exist, it is created.

		Args:
			collection_name (str): a collection name

		Returns:
			pymongo.collection.Collection: the collection object that
				corresponds to collection_name
		"""
		return self._database[collection_name]

	def _get_document_attr(self, collection, doc_id, attr_key):
		collection = self._ensure_col_is_obj(collection)
		document = collection.find_one({"_id": doc_id})
		attr_value = document.get(attr_key)
		return attr_value

	def get_leave_msg(self, welcome_id):
		leave_msg = self._get_welcome_attr(welcome_id, "leave_msg")
		return leave_msg

	def get_reminder_delay(self, welcome_id):
		reminder_delay = self._get_welcome_attr(welcome_id, "reminder_delay")
		return reminder_delay

	def get_reminder_msg(self, welcome_id):
		reminder_msg = self._get_welcome_attr(welcome_id, "reminder_msg")
		return reminder_msg

	def _get_server_attr(self, server_id, attr_key):
		attr_value = self._get_document_attr("server", server_id, attr_key)
		return attr_value

	def get_server_ids(self):
		server_col = self._get_collection("server")
		server_ids = list()
		for server_doc in server_col.find():
			server_id = server_doc["_id"]
			server_ids.append(server_id)
		return server_ids

	def get_server_leave_msg(self, server_id):
		welcome_id = self._get_server_welcome_id(server_id)
		leave_msg = self.get_leave_msg(welcome_id)
		return leave_msg

	def get_server_reminder_delay(self, server_id):
		welcome_id = self._get_server_welcome_id(server_id)
		reminder_delay = self.get_reminder_delay(welcome_id)
		return reminder_delay

	def get_server_reminder_msg(self, server_id):
		welcome_id = self._get_server_welcome_id(server_id)
		reminder_msg = self.get_reminder_msg(welcome_id)
		return reminder_msg

	def get_server_welcome_chan_id(self, server_id):
		welcome_id = self._get_server_welcome_id(server_id)
		welcome_chan_id = self.get_welcome_chan_id(welcome_id)
		return welcome_chan_id

	def _get_server_welcome_id(self, server_id):
		welcome_id = self._get_server_attr(server_id, "welcome_id")
		return welcome_id

	def get_server_welcome_msg(self, server_id):
		welcome_id = self._get_server_welcome_id(server_id)
		welcome_msg = self.get_welcome_msg(welcome_id)
		return welcome_msg

	def _get_welcome_attr(self, welcome_id, attr_key):
		attr_value = self._get_document_attr("welcome", welcome_id, attr_key)
		return attr_value

	def get_welcome_chan_id(self, welcome_id):
		return self._get_welcome_attr(welcome_id, "welcome_chan_id")

	def get_welcome_msg(self, welcome_id):
		return self._get_welcome_attr(welcome_id, "welcome_msg")

	def _id_exists(self, id, collection):
		collection = self._ensure_col_is_obj(collection)

		existing_doc = collection.find_one({"_id": id})
		return existing_doc is not None

	def register_server(self, server):
		"""
		If the server is not known yet, this method registers it in the
		database. The method attributes default data to the server.

		Args:
			server (discord.Guild): any Discord server

		Returns:
			bool: True if the server was already known, False otherwise
		"""
		if self._id_exists(server.id, "server"):
			return True

		welcome_id = self.generate_rand_id("welcome")
		welcome_doc = {
			"_id": welcome_id,
			"welcome_msg": "Bienvenue au club!",
			"reminder_delay": 15 * 60,
			"reminder_msg": None,
			"leave_msg": None,
			"welcome_chan_id": server.system_channel.id
		}
		self.add_document("welcome", welcome_doc)

		server_doc = {
			"_id": server.id,
			"name": server.name,
			"joined_at": str(datetime.now()),
			"announce_chan_id": None,
			"welcome_id": welcome_id
		}
		self.add_document("server", server_doc)

		return False

	def _set_document_attr(self, collection, doc_id, attr_key, attr_val):
		collection = self._ensure_col_is_obj(collection)
		query = {"_id": doc_id}
		update = {"$set": {attr_key: attr_val}}
		collection.update_one(query, update)

	def set_leave_msg(self, welcome_id, leave_msg):
		self._set_welcome_attr(welcome_id, "leave_msg", leave_msg)

	def set_reminder_delay(self, welcome_id, reminder_delay):
		self._set_welcome_attr(welcome_id, "reminder_delay", reminder_delay)

	def set_reminder_msg(self, welcome_id, reminder_msg):
		self._set_welcome_attr(welcome_id, "reminder_msg", reminder_msg)

	def set_server_leave_msg(self, server_id, leave_msg):
		welcome_id = self._get_server_welcome_id(server_id)
		self.set_leave_msg(welcome_id, leave_msg)

	def set_server_reminder_delay(self, server_id, reminder_delay):
		welcome_id = self._get_server_welcome_id(server_id)
		self.set_reminder_delay(welcome_id, reminder_delay)

	def set_server_reminder_msg(self, server_id, reminder_msg):
		welcome_id = self._get_server_welcome_id(server_id)
		self.set_reminder_msg(welcome_id, reminder_msg)

	def set_server_welcome_chan_id(self, server_id, welcome_chan_id):
		welcome_id = self._get_server_welcome_id(server_id)
		self.set_welcome_chan_id(welcome_id, welcome_chan_id)

	def set_server_welcome_msg(self, server_id, welcome_msg):
		welcome_id = self._get_server_welcome_id(server_id)
		self.set_welcome_msg(welcome_id, welcome_msg)

	def _set_welcome_attr(self, welcome_id, attr_key, attr_val):
		self._set_document_attr("welcome", welcome_id, attr_key, attr_val)

	def set_welcome_chan_id(self, welcome_id, welcome_chan_id):
		self._set_welcome_attr(welcome_id, "welcome_chan_id", welcome_chan_id)

	def set_welcome_msg(self, welcome_id, welcome_msg):
		self._set_welcome_attr(welcome_id, "welcome_msg", welcome_msg)

mongo_user = os.getenv('MONGO_USER')
mongo_password = os.getenv('MONGO_PASSWORD')
mongo_host = os.getenv('MONGO_HOST')
mongo_port = os.getenv('MONGO_PORT')
connection_string = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}"
database = _TremaDatabase("trema", connection_string)

def get_trema_database():
	return database

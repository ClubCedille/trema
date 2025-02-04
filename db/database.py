from datetime import datetime
from jsonschema import validate
from pymongo import MongoClient
from random import randint
from db.schemas.schemas import get_schema
from sys import maxsize
from bson import ObjectId
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
		if document is None:
			return None
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


	def get_member_join_msg(self, welcome_id):
		return self._get_welcome_attr(welcome_id, "member_join_msg")

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

	def get_server_member_join_msg(self, server_id):
		welcome_id = self._get_server_welcome_id(server_id)
		member_join_msg = self.get_member_join_msg(welcome_id)
		return member_join_msg

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
			"welcome_chan_id": server.system_channel.id,
			"member_join_msg": "🎉Bienvenue!🎉",
		}
		self.add_document("welcome", welcome_doc)

		server_doc = {
			"_id": server.id,
			"name": server.name,
			"joined_at": str(datetime.now()),
			"announce_chan_id": None,
			"welcome_id": welcome_id,
			"admin_role": None,
			"member_role": None,
			"webhooks": [],
			"server_roles": [],
			"calidum_enabled": False
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

	def set_server_member_join_msg(self, server_id, member_join_msg):
		welcome_id = self._get_server_welcome_id(server_id)
		self.set_member_join_msg(welcome_id, member_join_msg)

	def _set_welcome_attr(self, welcome_id, attr_key, attr_val):
		self._set_document_attr("welcome", welcome_id, attr_key, attr_val)

	def set_welcome_chan_id(self, welcome_id, welcome_chan_id):
		self._set_welcome_attr(welcome_id, "welcome_chan_id", welcome_chan_id)

	def set_welcome_msg(self, welcome_id, welcome_msg):
		self._set_welcome_attr(welcome_id, "welcome_msg", welcome_msg)

	def set_member_join_msg(self, welcome_id, member_join_msg):
		self._set_welcome_attr(welcome_id, "member_join_msg", member_join_msg)

	def get_server_admin_role(self, server_id):
		return self._get_server_attr(server_id, "admin_role")

	def set_server_admin_role(self, server_id, admin_role):
		self._set_document_attr("server", server_id, "admin_role", admin_role)

	def get_server_member_role(self, server_id):
		return self._get_server_attr(server_id, "member_role")

	def set_server_member_role(self, server_id, member_role):
		self._set_document_attr("server", server_id, "member_role", member_role)

	def set_server_calidum_enabled(self, server_id, enable):
		self._set_document_attr("server", server_id, "calidum_enabled", enable)

	def get_server_calidum_enabled(self, server_id):
		return self._get_server_attr(server_id, "calidum_enabled")

	def create_webhook(self, webhookName, channelID, unique_url, guild_id):
		server_collection = self._get_collection("server")
		new_webhook = {
			"webhookName": webhookName,
			"channelID": channelID,
			"unique_url": unique_url
		}
		server_collection.update_one(
			{"_id": guild_id},
			{"$push": {"webhooks": new_webhook}}
		)

	def get_all_webhooks(self, guild_id):
		server_collection = self._get_collection("server")
		server_doc = server_collection.find_one({"_id": guild_id})
		if server_doc is None:
			return []
		return server_doc.get("webhooks", [])

	def delete_webhook(self, webhookName, guild_id):
		server_collection = self._get_collection("server")
		server_collection.update_one(
			{"_id": guild_id},
			{"$pull": {"webhooks": {"webhookName": webhookName}}}
		)

	def update_webhook_channel(self, webhookName, newChannelID, guild_id):
		server_collection = self._get_collection("server")
		query = {"_id": guild_id, "webhooks.webhookName": webhookName}
		update = {"$set": {"webhooks.$.channelID": newChannelID}}
		server_collection.update_one(query, update)

	def get_channel_by_webhook(self, uuid):
		server_collection = self._get_collection("server")
		server_doc = server_collection.find_one({"webhooks.unique_url": uuid})
		if server_doc is None:
			return None

		webhooks = server_doc.get("webhooks", [])
		for webhook in webhooks:
			if webhook["unique_url"] == uuid:
				return webhook["channelID"]
		return None

	def get_webhook_by_name(self, webhookName, guild_id):
		server_collection = self._get_collection("server")
		server_doc = server_collection.find_one({"_id": guild_id})
		if server_doc is None:
			return None

		webhooks = server_doc.get("webhooks", [])
		for webhook in webhooks:
			if webhook["webhookName"] == webhookName:
				return webhook
		return None
	def create_request(self, guild_id, request_type, request_data):
		"""
		Registers a new request in the database with support for multiple request types.

		Args:
			guild_id (int): The ID of the guild making the request.
			request_type (str): The type of the request (e.g., 'grav', 'postgresql').
			request_data (dict): The specific data for the request. This should include any type-specific
			fields such as 'domaine', 'nom_club', 'contexte' for a GRAV request.

		"""
		requests_collection = self._get_collection("requests")
		
		request_document = {
			"_id": self.generate_rand_id("requests"),
			"guild_id": guild_id,
			"request_type": request_type,
			"request_data": request_data,  # Now, 'request_data' is nested
			"created_at": datetime.now(),
			"status": "submitted"
    	}
		
		requests_collection.insert_one(request_document)

	def list_requests(self, guild_id):
		requests_collection = self._get_collection("requests")
		requests = requests_collection.find(
			{"guild_id": guild_id},
			sort=[("created_at", -1)]
		)
		return list(requests)
		
	def delete_request(self, guild_id, request_id):
		requests_collection = self._get_collection("requests")
		try:
			oid = ObjectId(request_id)
		except:
			return False  
		result = requests_collection.delete_one({"guild_id": guild_id, "_id": oid})
		return result.deleted_count > 0
	
	def get_all_server_configs(self, server_id):
		def safe_get(attr_value, default="Non configuré"):
			return default if attr_value is None else attr_value

		configs = {
			"Nom du serveur": safe_get(self._get_server_attr(server_id, "name")),
			"Rôle d'administrateur": safe_get(self._get_server_attr(server_id, "admin_role")),
			"Rôle de membre": safe_get(self._get_server_attr(server_id, "member_role")),
			"Rôles du serveur": safe_get(self._get_server_attr(server_id, "server_roles"), default=[]),
			"Date d'adhésion": safe_get(self._get_server_attr(server_id, "joined_at")),
			"ID du canal d'annonces": safe_get(self._get_server_attr(server_id, "announce_chan_id")),
			"ID du canal de bienvenue": safe_get(self.get_server_welcome_chan_id(server_id)),
			"Message de bienvenue": safe_get(self.get_server_welcome_msg(server_id)),
			"Message de départ": safe_get(self.get_server_leave_msg(server_id)),
			"Message de rappel": safe_get(self.get_server_reminder_msg(server_id)),
			"Message pour requête de rejoindre": safe_get(self.get_server_member_join_msg(server_id)),
			"Délai de rappel (minutes)": safe_get(self.get_server_reminder_delay(server_id), default=0) // 60,
			"Webhooks": safe_get(self.get_all_webhooks(server_id), default=[]),
			"Calidum notifications enabled": safe_get(self.get_server_calidum_enabled(server_id), default=False)
		}

		formatted_configs = []
		for key, value in configs.items():
			if isinstance(value, list):
				if value:
					formatted_value = "".join([f"\n- {item}" for item in value])
				else:
					formatted_value = "Aucun"
			else:
				formatted_value = value

			formatted_configs.append(f"**{key}**: {formatted_value}")

		return "\n\n".join(formatted_configs)
	
	def add_member(self, server_id, member):
		member["_id"] = self.generate_rand_id("members")
		member["server_id"] = server_id
		if "status" not in member:
			member["status"] = "pending"
		
		self.add_document("members", member)

	def get_members(self, server_id, status=None):
		members_collection = self._get_collection("members")
		query = {"server_id": server_id}
		if status:
			query["status"] = status
		members = members_collection.find(query)
		return list(members)

	def update_member(self, member_id, update_fields):
		members_collection = self._get_collection("members")
		query = {"_id": member_id}
		update = {"$set": update_fields}
		members_collection.update_one(query, update)

	def delete_member(self, member_id):
		members_collection = self._get_collection("members")
		members_collection.delete_one({"_id": member_id})

	def get_member(self, member_id):
		members_collection = self._get_collection("members")
		return members_collection.find_one({"_id": member_id})
	
	def set_server_roles(self, server_id, role_names):
		server_collection = self._get_collection("server")
		server_collection.update_one(
			{"_id": server_id},
			{"$set": {"server_roles": role_names}}
		)

	def get_server_roles(self, server_id):
		server_collection = self._get_collection("server")
		server_doc = server_collection.find_one({"_id": server_id})
		if server_doc is None:
			return []
		return server_doc.get("server_roles", [])
	
	def get_pending_reminders(self):
		reminders_collection = self._get_collection("reminders")
		reminders = reminders_collection.find({"status": "pending"})
		return list(reminders)
	
	def add_reminder(self, reminder):
		reminder["_id"] = self.generate_rand_id("reminders")
		reminder["status"] = "pending"
		self.add_document("reminders", reminder)
		return reminder["_id"]

	def update_reminder_status(self, reminder_id, status):
		reminders_collection = self._get_collection("reminders")
		query = {"_id": reminder_id}
		update = {"$set": {"status": status}}
		reminders_collection.update_one(query, update)

	def get_reminder_status(self, reminder_id):
		reminders_collection = self._get_collection("reminders")
		reminder = reminders_collection.find_one({"_id": reminder_id})
		if reminder is None:
			return None
		return reminder.get("status")
	
	def update_reminder_confirmation_message(self, reminder_id, message_id):
		reminders_collection = self._get_collection("reminders")
		query = {"_id": reminder_id}
		update = {"$set": {"confirmation_message_id": message_id}}
		reminders_collection.update_one(query, update)

	def get_reminder(self, reminder_id):
		reminders_collection = self._get_collection("reminders")
		return reminders_collection.find_one({"_id": reminder_id})

mongo_user = os.getenv('MONGO_USER')
mongo_password = os.getenv('MONGO_PASSWORD')
mongo_host = os.getenv('MONGO_HOST')
connection_string = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:27017"
database = _TremaDatabase("trema", connection_string)

def get_trema_database():
	return database
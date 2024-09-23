from enum import Enum
import json
from pathlib import Path


_ENCODING_UTF8 = "utf-8"
_EXTENSION_JSON = ".json"
_LOCAL_DIR = Path(__file__).resolve().parent
_MODE_R = "r"


class Schema(Enum):
	# The values must match the schemas' file name.
	SERVER = "server"
	WELCOME = "welcome"
	webhooks = "webhooks"
	MEMBERS = "members"

	@staticmethod
	def from_str(a_string):
		for member in Schema:
			if member.value == a_string:
				return member

		return None


def read_json_file(json_path):
	if isinstance(json_path, str):
		json_path = Path(json_path)

	with json_path.open(mode=_MODE_R, encoding=_ENCODING_UTF8) as json_file:
		content = json.load(json_file)

	return content


# Keys: schema names
# Values: the schemas from the JSON files
_schemas = dict()

for schema_name in Schema:
	schema_name = schema_name.value
	schema_path = _LOCAL_DIR/(schema_name + _EXTENSION_JSON)
	schema = read_json_file(schema_path)
	_schemas[schema_name] = schema


def get_schema(schema_name):
	if isinstance(schema_name, Schema):
		schema_name = schema_name.value

	return _schemas.get(schema_name)

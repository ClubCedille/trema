server_schema = {
    "type": "object",
    "properties": {
        "_id": {"type": "number"},
        "name": {"type": "string"},
        "joinedAt": {
            "type": "string",
            "format": "date-time"
        },
        "welcome_id": {"type": "number"}
    }
}

welcome_schema = {
    "type": "object",
    "properties": {
        "_id": {"type": "number"},
        "active": {"type": "boolean"},
        "welcome_msg": {"type": "string"},
		"reminder_msg": {"type": "string"},
		"leave_msg": {"type": "string"},
        "instruct_chan_id": {"type": "number"}
    }
}

def getSchema(schemaName):
    if schemaName == "serveur":
        return server_schema
    return welcome_schema
serveurSchema = {
    "type": "object",
    "properties": {
        "_id": {"type": "number"},
        "name": {"type": "string"},
        "joinedAt": {
            "type": "string",
            "format": "date-time"
        }
    }
}

welcomeSchema = {
    "type": "object",
    "properties": {
        "_id": {"type": "number"},
        "activer": {"type": "boolean"},
        "message": {"type": "string"},
        "channel_id": {"type": "number"},
        "clud_id": {"type": "number"}
    }
}

def getSchema(schemaName):
    if schemaName == "serveur":
        return serveurSchema
    return welcomeSchema
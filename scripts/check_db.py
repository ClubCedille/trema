import os
import pymongo
import sys

mongo_host = os.environ.get('MONGO_HOST')
mongo_port = os.environ.get('MONGO_PORT')
mongo_user = os.environ.get('MONGO_USER')
mongo_pass = os.environ.get('MONGO_PASSWORD')


try:
    client = pymongo.MongoClient(f'mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}')

    client.server_info()
    print(f"Connection à MongoDB réussie sur {mongo_host}:{mongo_port}")
    sys.exit(0)

except Exception as e:
    # En cas d'erreur, imprimez l'erreur (optionnel) et sortez avec un code de sortie 1
    print(f"Erreur lors de la connexion à MongoDB : {e}")

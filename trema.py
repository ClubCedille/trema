"""
Trëma est un robot logiciel pour le serveur
Discord des clubs étudiants de l'ÉTS.
"""


from argparse import ArgumentParser
import discord

from pymongo import MongoClient

client = MongoClient("mongodb://root:root@localhost:27017/?authSource=admin")
#database Trema
mydb = client["trema"]
#table serveur contenant les différents serveur utiliser par trema
mycol = mydb["serveur"]

###############
# À enlever : 
# Exemple de comment l'utiliser : 
mydict = { "name": "cedille", "members_count": 85 }
record = mycol.insert_one(mydict)

# Équivalent à SELECT *
for i in mycol.find():
  print(i)


mycol.drop()
###############

def _make_arg_parser():
	parser = ArgumentParser(description=__doc__)
	parser.add_argument("-s", "--serveurs", nargs="+", type=str,
		help="L'identifiant des serveurs où ce robot fonctionnera")
	parser.add_argument("-j", "--jeton", type=str,
		help="Le jeton d'authentification de ce robot logiciel")
	return parser


arg_parser = _make_arg_parser()
args = arg_parser.parse_args()

server_ids = args.serveurs
bot_token = args.jeton

print(f"Serveurs: {server_ids}")
print(f"Jeton du robot: {bot_token}")





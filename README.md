<p align="center">
  <img src="img/trema_logo.png" alt="Trëma Logo" width="200"/>
</p>

<h1 align="center">Trëma</h1>
<p align="center">Le robot Discord pour les clubs étudiants de l'ÉTS</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.2-blue.svg" alt="Version Badge"/>
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License Badge"/>
  <img src="https://github.com/ClubCedille/trema/actions/workflows/ci.yml/badge.svg" alt="Workflow Badge"/>
</p>

---
## À propos
Un robot logiciel pour les serveurs Discord des clubs étudiants de l'ÉTS

Trëma est un bot Discord développé par le club CEDILLE de l'ÉTS. Le but de ce bot est d'aider à accueillir et à guider les nouveaux membres sur le serveur Discord, ainsi que de fournir des fonctionnalités utiles pour la gestion du serveur.

## Fonctionnalités
### Discord bot
__Commandes de Configuration (/config)__
* /config aide: Fournit des informations sur les différentes commandes de configuration.

* /config canalaccueil [id_accueil]: Configure le canal où les nouveaux membres seront accueillis. L'ID du canal est requis. Rôle admin requis.

* /config msgaccueil: Permet de personnaliser le message d'accueil envoyé aux nouveaux membres. Vous recevrez un message privé pour configurer ce texte. Rôle admin requis.

* /config msgdepart [message]: Permet de configurer le message envoyé lorsque quelqu'un quitte le serveur. Rôle admin requis.

* /config roleAdmin [role_id]: Permet de configurer le rôle admin dans le serveur. Ce rôle permet d'exécuter les commande de configuration, rappel et la commande annonce. Rôle de propriétaire de serveur requis.
* 
__Sous-commandes de Rappel (/config rappel)__
* /config rappel message [message]: Configure le message de rappel envoyé aux membres qui n'ont pas encore choisi de rôle. Rôle admin requis. 

* /config rappel delai [délai]: Définit le délai en minutes avant que le message de rappel soit envoyé. Rôle admin requis.

__Commandes de Webhook (/webhook)__
* /webhook create [channel_id] [webhook_name]: Crée un nouveau webhook pour le canal spécifié. Rôle admin requis.
* /webhook list: Affiche une liste des webhooks existants pour le serveur. Rôle admin requis.
* /webhook delete [webhook_name]: Supprime un webhook existant. Rôle admin requis.
* /webhook update [webhook_name] [new_channel_id]: Met à jour le canal associé au webhook. Rôle admin requis.

__Commandes d'Information__
* /ping: Affiche la latence du bot et d'autres statistiques.

* /info: Fournit des informations générales sur le bot Trëma.

__Commandes annonce__
* /annonce: Permet de planifier une annonce. 

#### Événements
* on_guild_join: Enregistre le serveur dans la base de données lorsqu'il rejoint un nouveau serveur.

* on_member_join: Envoie un message d'accueil personnalisé dans le canal d'accueil configuré et envoie également des rappels aux membres qui n'ont pas encore choisi de rôle.

Les placeholders comme {member}, {username}, {server}, {&role}, {#channel}, {everyone}, {here} etc. peuvent être utilisés pour personnaliser les messages.

#### Comment l'utiliser ?
Pour commencer à utiliser le bot, [invitez-le](https://discord.com/api/oauth2/authorize?client_id=1042263080794603630&permissions=28582739967217&scope=bot) sur votre serveur et utilisez la commande /config aide pour obtenir de l'aide sur la configuration.

##### Besoin d'aide ?
Si vous avez des questions ou des problèmes avec le bot, n'hésitez pas à contacter le club CEDILLE à partir de [discord](https://discord.gg/ywvNV4Se) pour un support technique.


### API Endpoints
__Webhooks__
* POST /webhooks/<uuid>: Cet endpoint est utilisé pour gérer les webhooks entrants.
Lorsqu'une requête POST est effectuée sur cet endpoint avec un uuid valide, il traite le contenu intégré pour créer un message Discord Embed et l'envoie au canal Discord correspondant. Le payload JSON entrant doit inclure un tableau embeds contenant les informations d'intégration, telles que le titre, la description, la couleur, et un pied de page facultatif.

Exemple de Payload :
```
{
  "embeds": [
    {
      "title": "Your Title Here",
      "description": "Your Description Here",
      "color": "16745728",
      "footer": {
        "text": "Footer Text"
      }
    }
  ]
}
```

## Développement local
### Lancement de Trëma

Définissez la variable d'environnement suivante :
- DISCORD_TOKEN : Discord bot token
- MONGO_USER : utilisateur de la db 
- MONGO_PASSWORD : mot de passe de la db
- MONGO_HOST : nom d'hôte de la db
- MONGO_PORT : Port pour la db
- API_ADDRESS : Addresse ip de l'api
- API_PORT : port utilisé par l'api

Installer les dépendances en ligne de commande.

```bash
pip install -r requirements.txt
pip install git+https://github.com/Pycord-Development/pycord
```

Lancez le robot en ligne de commande.

```bash
python trema.py
```
## Docker

### Construire l'image

Se placer à la racine du projet.
Exectuer la commande suivante :

```bash
docker build -t trema .
```

### Lancer l'image

```bash
docker run trema
```

### Exécution du conteneur avec une instance mongo locale

Pour créer ou exécuter le conteneur avec une instance locale de mongodb, veuillez exécuter la commande : 

```bash
docker-compose -f docker-compose-dev.yml up -d
```

Pour désactiver le conteneur

```bash
docker-compose -f docker-compose-dev.yml stop
```

### Accès à la base de données

Trëma utilise une base de donnés MongoDB. Pour y accéder, lancez la commande
suivante, repérez l'identité du conteneur de Trëma et copiez-la.

```bash
docker ps
```

Insérez l'identifant dans la commande suivante puis exécutez-la.

```bash
docker exec -it [container id] bash
```

Cette dernière commande ouvre le terminal de la base de données de Trëma.

```bash
mongo mongodb://localhost:27017 -u root -p root
```

Pour quitter le terminal du conteneur ou de la base de données

```bash
exit
```

## Test

### Lancement des tests


Pour lancer tous les tests du projet, lancez
la commande suivante.
```
pytest
```

Pour lancer tous les tests d'un fichier en particulier, lancez
la commande suivante.
```
pytest -v ./tests/[nom du fichier].py
```

Pour lancer un seul test d'un fichier, lancez la commande
suivante.
```
pytest -v ./tests/[nom du fichier].py::[nom de la fonction]

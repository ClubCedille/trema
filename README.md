<p align="center">
  <img src="img/trema_logo.png" alt="Trëma Logo" width="200"/>
</p>

<h1 align="center">Trëma</h1>
<p align="center">Le robot Discord pour les clubs étudiants de l'ÉTS</p>

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License Badge"/>
  <img src="https://github.com/ClubCedille/trema/actions/workflows/workflows.yml/badge.svg" alt="Workflow Badge"/>
</p>

---

## À propos

Un robot logiciel pour les serveurs Discord des clubs étudiants de l'ÉTS

Trëma est un bot Discord développé par le club CEDILLE de l'ÉTS. Le but de ce
bot est d'aider à accueillir et à guider les nouveaux membres sur le serveur
Discord, ainsi que de fournir des fonctionnalités utiles pour la gestion du
serveur.

## Fonctionnalités

### Discord bot

__Commandes de Configuration (/config)__:

* /config aide: Fournit des informations sur les différentes commandes de
  configuration.
* /config canalaccueil [id_accueil]: Configure le canal où les nouveaux membres
  seront accueillis. L'ID du canal est requis. Rôle admin requis.
* /config msgaccueil: Permet de personnaliser le message d'accueil envoyé aux
  nouveaux membres. Vous recevrez un message privé pour configurer ce texte.
  Rôle admin requis.
* /config msgdepart [message]: Permet de configurer le message envoyé lorsque
  quelqu'un quitte le serveur. Rôle admin requis.
* /config roleAdmin [role_id]: Permet de configurer le rôle admin dans le
  serveur. Ce rôle permet d'exécuter les commande de configuration, rappel et la
  commande annonce. Rôle de propriétaire de serveur requis.
* /config roleMembre [role_id]: Permet de configurer le rôle membre dans le
  serveur. Ce rôle est attribué aux membres lorsqu'ils obtiennent un statut
  'approved' par les admins.

__Sous-commandes de Rappel (/config rappel)__:

* /config rappel message [message]: Configure le message de rappel envoyé aux
  membres qui n'ont pas encore choisi de rôle. Rôle admin requis.
* /config rappel delai [délai]: Définit le délai en minutes avant que le message
  de rappel soit envoyé. Rôle admin requis.

__Commandes de Webhook (/webhook)__:

* /webhook create [channel_id] [webhook_name]: Crée un nouveau webhook pour le
  canal spécifié. Rôle admin requis.
* /webhook list: Affiche une liste des webhooks existants pour le serveur. Rôle
  admin requis.
* /webhook delete [webhook_name]: Supprime un webhook existant. Rôle admin
  requis.
* /webhook update [webhook_name] [new_channel_id]: Met à jour le canal associé
  au webhook. Rôle admin requis.

__Commandes d'Information__:

* /ping: Affiche la latence du bot et d'autres statistiques.
* /info: Fournit des informations générales sur le bot Trëma.

__Commandes annonce__:

* /annonce: Permet de planifier une annonce.

__Commandes de requête (/request)__:

* /request join: Permet à un nouveau visiteur du serveur de faire une requête
pour avoir un rôle parmis `server_roles` et avoir accès au reste du serveur. Si
la requête est pour `server_member`, ceci envoie une notification aux admins
pour approuver ou refuser la demande. Un status 'pending' est attribué aux
membres qui on demander le rôle  `server_member`.
* /request grav [domaine] [nom_club] [contexte]: Permet à un utilisateur de
  faire une requête pour un site web grav. Ceci envoie une notification aux
  admins et un workflow dispatch call au pipeline de déploiement grav sur le
  repo Plateforme-Cedille.
* /request delete [request_id]: Permet aux admins de supprimer une requête. Rôle
  admin requis.
* /request list: Affiche la liste des requêtes en attente. Rôle admin requis.

__Commandes de gestion de membres (/member)__:

* /member list: Affiche la liste des membres du serveur.
* /member update: Permet aux admins de mettre à jour le statut des membres. Les
  membres peuvent être approuvés ou refusés. Rôle admin requis. Une notification
  est envoyée aux membres approuvés et le rôle membre est attribué.
* /member delete: Permet aux admins de supprimer un membre du serveur. Rôle
  admin requis.
* /member add [user_id] [status]: Permet aux admins d'ajouter un membre au
  serveur. Rôle admin requis.

#### Événements

* on_guild_join: Enregistre le serveur dans la base de données lorsqu'il rejoint
  un nouveau serveur.
* on_member_join: Envoie un message d'accueil personnalisé dans le canal
  d'accueil configuré et envoie également des rappels aux membres qui n'ont pas
  encore choisi de rôle.

Les placeholders comme {member}, {username}, {server}, {&role}, {#channel},
{everyone}, {here} etc. peuvent être utilisés pour personnaliser les messages.

#### Comment l'utiliser ?

Pour commencer à utiliser le bot,
[invitez-le](https://discord.com/api/oauth2/authorize?client_id=1042263080794603630&permissions=28582739967217&scope=bot)
sur votre serveur et utilisez la commande /config aide pour obtenir de l'aide
sur la configuration.

##### Besoin d'aide ?

Si vous avez des questions ou des problèmes avec le bot, n'hésitez pas à
contacter le club CEDILLE à partir de [discord](https://discord.gg/ywvNV4Se)
pour un support technique.

### API Endpoints

#### `/Webhooks`

* `POST /webhooks/<uuid>`: Cet endpoint est utilisé pour gérer les webhooks
  entrants.

Lorsqu'une requête POST est effectuée sur cet endpoint avec un uuid valide, il
traite le contenu intégré pour créer un message Discord Embed et l'envoie au
canal Discord correspondant. Le payload JSON entrant doit inclure un tableau
embeds contenant les informations d'intégration, telles que le titre, la
description, la couleur, et un pied de page facultatif.

Exemple de Payload :

```sh
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

* DISCORD_TOKEN : Discord bot token
* MONGO_USER : utilisateur de la db
* MONGO_PASSWORD : mot de passe de la db
* MONGO_HOST : nom d'hôte de la db
* MONGO_PORT : Port pour la db
* API_ADDRESS : Addresse ip de l'api
* API_PORT : port utilisé par l'api

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

Se placer à la racine du projet. Exectuer la commande suivante :

```bash
docker build -t trema .
```

### Lancer l'image

```bash
docker run trema
```

### Exécution du conteneur avec une instance mongo locale

Pour créer ou exécuter le conteneur avec une instance locale de mongodb,
veuillez exécuter la commande :

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

Les tests sont dépendants de la base de données MongoDB. Pour les lancer, vous
devez avoir une instance de MongoDB en cours d'exécution. Un docker-compose est
fourni pour lancer une instance locale de MongoDB.

Pour lancez l'instance de MongoDB, exécutez la commande suivante:

```bash
docker-compose -f tests/docker-compose.yml up -d
```

Pour lancer tous les tests du projet, lancez la commande suivante.

```bash
pytest
```

Pour lancer tous les tests d'un fichier en particulier, lancez la commande
suivante.

```bash
pytest -v ./tests/[nom du fichier].py
```

Pour lancer un seul test d'un fichier, lancez la commande suivante.

```bash
pytest -v ./tests/[nom du fichier].py::[nom de la fonction]
```

## Metrics

### Prometheus

Des métriques sont exposées via l'endpoint `/metrics`. Pour les visualiser,
lancez le docker-compose fourni et visiter localhost:3000 pour l'instance de
Graphana.Un exemple de configuration est fourni dans le dossier dans monitoring
avec Un dashboard et un fichier de configuration pour prometheus.

Pour exposer les métriques a Prometheus dans un cluster Kubernetes, vous pouvez
créer un ServiceMonitor pour le déploiement de Trëma.

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: trema-monitor
  namespace: trema
  labels:
    app: trema
spec:
  selector:
    matchLabels:
      app: trema
  endpoints:
    - port: metrics
      path: /metrics
      interval: 15s
---
apiVersion: v1
kind: Service
metadata:
  name: trema
  namespace: trema
  labels:
    app: trema
spec:
  ports:
    - name: metrics
      port: 9090
      targetPort: 9090
    ... # other ports
  selector:
    app: trema
```

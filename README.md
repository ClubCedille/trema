# Trëma

Un robot logiciel pour le serveur Discord des clubs étudiants de l'ÉTS

### Exécution du conteneur

Pour créer ou exécuter le conteneur, lancez la commande suivante.

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

Trëma est exécuté à l'extérieur du conteneur puis se connecte à la base de
données.

### Lancement de Trëma

Définissez la variable d'environnement suivante :
- DISCORD_TOKEN : Discord bot token
- MONGO_USER : utilisateur de la db 
- MONGO_PASSWORD : mot de passe de la db
- MONGO_HOST : nom d'hôte de la db
- MONGO_PORT : Port pour la db

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
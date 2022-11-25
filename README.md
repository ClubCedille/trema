# Trëma
Un robot logiciel pour le serveur Discord des clubs étudiants de l'ÉTS

### Exécution du conteneur
Pour créer ou exécuter le conteneur, lancez la commande suivante.
```
docker-compose -f docker-compose-dev.yml up -d
```

Pour désactiver le conteneur
```
docker-compose -f docker-compose-dev.yml stop
```

### Accès à la base de données
Trëma utilise une base de donnés MongoDB. Pour y accéder, lancez la commande
suivante, repérez l'identité du conteneur de Trëma et copiez-la.
```
docker ps
```

Insérez l'identifant dans la commande suivante puis exécutez-la.
```
docker exec -it [container id] bash
```

Cette dernière commande ouvre le terminal de la base de données de Trëma.
```
mongo mongodb://localhost:27017 -u root -p root
```

Pour quitter le terminal du conteneur ou de la base de données
```
exit
```

Trëma est exécuté à l'extérieur du conteneur puis se connecte à la base de
données.

### Lancement de Trëma

Lancez le robot en ligne de commande en lui donnant son jeton
d'authentification.
```
python trema.py -j [jeton]
```

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
```
# Trëma
Robot logiciel pour le serveur Discord des clubs étudiants de l'ÉTS

### Exécution du conteneur
Pour créer ou exécuter le conteneur, lancez la commande suivante.
```bash
docker-compose -f docker-compose-dev.yml up -d
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

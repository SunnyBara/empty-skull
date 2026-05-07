# empty_skull

Outil Django pour gérer le stock d'items de nail art, calculer le coût de fabrication d'un set et suivre les besoins de réapprovisionnement.

## Fonctionnalités

- CRUD des `tools`, `consommables` et `sets`
- Suivi de stock centralisé
- Calcul du coût de fabrication d'un set
- Calcul du nombre de sets faisables selon le stock restant
- Validation de production avec décrément des consommables
- Alertes quand un set n'est faisable que 2 fois ou moins

## Lancement avec Docker

```bash
cp .env.example .env
docker compose up --build
```

L'application sera disponible sur [http://localhost:8000](http://localhost:8000).

Les migrations sont lancées automatiquement au démarrage du conteneur web.
Les fichiers statiques sont servis directement par Django via `WhiteNoise`.

## Installation locale

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

## Commandes Docker utiles

```bash
docker compose up --build
docker compose down
docker compose exec web python manage.py createsuperuser
```

## Modèle métier

- `Tool`: référence durable avec prix et nombre d'utilisations
- `Consumable`: référence avec quantité totale, unité et prix total
- `Stock`: quantité actuelle d'un `Tool` ou d'un `Consumable`
- `Set`: composition d'un design
- `SetItem`: ligne d'un set avec quantité requise

## Notes

- Le projet est configuré pour PostgreSQL via variables d'environnement.
- Le setup Docker utilise `web` + `postgres` via `docker compose`.
- Les `tools` ne sont jamais décrémentés lors de la production.
- Les composants critiques apparaissent en rouge sur le détail d'un set.

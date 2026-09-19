# 📚 Assistant de révision

Application web qui transforme des notes de cours en PDF en outil de révision :
elle en génère un résumé, crée un quiz à choix multiples, corrige les réponses
et suit la progression dans le temps.

## Fonctionnalités

- Dépôt d'un fichier PDF et extraction automatique du texte
- Résumé en 10 points clés généré par l'IA
- Quiz de 3 à 10 questions à choix multiples, avec explication de chaque réponse
- Correction immédiate et score
- Historique des scores et courbe de progression

## Technologies

| Outil | Rôle |
|---|---|
| Python | langage du projet |
| Streamlit | interface web |
| Google Gemini | génération du résumé et du quiz |
| pypdf | extraction du texte des PDF |
| SQLite | sauvegarde des scores |

## Installation

```bash
git clone https://github.com/Lotficode/assistant-revision.git
cd assistant-revision
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Créer un fichier `.env` à la racine avec une clé obtenue sur
[Google AI Studio](https://aistudio.google.com/apikey) :

```
GEMINI_API_KEY=votre_cle
```

## Lancement

```bash
streamlit run app.py
```

## Structure du projet

```
assistant-revision/
├── app.py            interface web (Streamlit)
├── assistant.py      lecture des PDF et appels à l'IA
├── base.py           sauvegarde des scores (SQLite)
├── resume.py         version ligne de commande du résumé
├── modeles.py        liste les modèles Gemini accessibles
├── requirements.txt  dépendances
└── .env              clé API (non versionné)
```

## Choix techniques

- **Séparation des responsabilités** : l'interface (`app.py`), la logique IA
  (`assistant.py`) et le stockage (`base.py`) sont indépendants, ce qui permet
  de tester chaque partie séparément.
- **Gestion des erreurs réseau** : les appels à l'IA sont réessayés en cas de
  surcharge du serveur (erreur 503) et basculent sur un modèle de secours si un
  modèle devient indisponible.
- **Réponse structurée** : le quiz est demandé en JSON afin que le programme
  puisse corriger automatiquement, plutôt que d'interpréter du texte libre.
- **Secrets hors du code** : la clé API est lue depuis un fichier `.env` exclu
  du dépôt.

## Auteur

Lotfi Hamed A. — étudiant en génie logiciel, ÉTS Montréal
[github.com/Lotficode](https://github.com/Lotficode)

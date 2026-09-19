import sqlite3
from datetime import datetime

FICHIER = "scores.db"


def executer(requete, valeurs=(), lire=False):
    cnx = sqlite3.connect(FICHIER)
    try:
        curseur = cnx.execute(requete, valeurs)
        resultat = curseur.fetchall() if lire else None
        cnx.commit()
        return resultat
    finally:
        cnx.close()


def creer_table():
    executer(
        "CREATE TABLE IF NOT EXISTS scores ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "document TEXT, "
        "score INTEGER, "
        "total INTEGER, "
        "date TEXT)"
    )


def enregistrer_score(document, score, total):
    creer_table()
    moment = datetime.now().strftime("%Y-%m-%d %H:%M")
    executer(
        "INSERT INTO scores (document, score, total, date) VALUES (?, ?, ?, ?)",
        (document, score, total, moment),
    )


def lire_scores():
    creer_table()
    return executer("SELECT date, document, score, total FROM scores ORDER BY id", lire=True)


def effacer_scores():
    creer_table()
    executer("DELETE FROM scores")

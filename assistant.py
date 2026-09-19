import json
import logging
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from pypdf import PdfReader

logging.getLogger("pypdf").setLevel(logging.ERROR)

load_dotenv()

MODELES = ["gemini-3.6-flash", "gemini-flash-latest", "gemini-flash-lite-latest"]
TAILLE_MAX = 30000

_client = None


def obtenir_cle():
    cle = os.getenv("GEMINI_API_KEY")
    if cle:
        return cle
    try:
        import streamlit
        return streamlit.secrets["GEMINI_API_KEY"]
    except Exception:
        return None


def obtenir_client():
    global _client
    if _client is None:
        cle = obtenir_cle()
        if not cle:
            raise RuntimeError("Clé GEMINI_API_KEY introuvable. Vérifie ton fichier .env.")
        _client = genai.Client(api_key=cle)
    return _client


def lire_pdf(fichier):
    lecteur = PdfReader(fichier)
    texte = ""
    for page in lecteur.pages:
        contenu = page.extract_text()
        if contenu:
            texte = texte + contenu + "\n"
    return texte.strip()


def demander_a_gemini(consigne, format_json=False):
    client = obtenir_client()
    config = None
    if format_json:
        config = types.GenerateContentConfig(response_mime_type="application/json")
    derniere_erreur = "aucune"
    for modele in MODELES:
        for essai in range(3):
            try:
                reponse = client.models.generate_content(
                    model=modele, contents=consigne, config=config
                )
                return reponse.text
            except errors.ServerError as erreur:
                derniere_erreur = str(erreur)
                time.sleep(5)
            except errors.ClientError as erreur:
                derniere_erreur = str(erreur)
                break
    raise RuntimeError("Aucun modèle disponible pour le moment. Dernière erreur : " + derniere_erreur)


def verifier_texte(texte):
    if not texte or len(texte.strip()) < 200:
        raise RuntimeError(
            "Ce PDF ne contient presque pas de texte. "
            "S'il s'agit d'un document scanné, essaie un PDF contenant du vrai texte."
        )


def resumer(texte):
    verifier_texte(texte)
    consigne = (
        "Tu es un assistant de révision. Résume ces notes de cours en 10 points clés, "
        "courts et clairs, sous forme de liste numérotée. "
        "Réponds dans la même langue que le texte.\n\n" + texte[:TAILLE_MAX]
    )
    return demander_a_gemini(consigne)


def nettoyer_json(texte):
    texte = texte.strip()
    if texte.startswith("```"):
        texte = texte.strip("`").strip()
        if texte.startswith("json"):
            texte = texte[4:]
    return texte.strip()


def verifier_quiz(donnees):
    if isinstance(donnees, dict):
        for valeur in donnees.values():
            if isinstance(valeur, list):
                donnees = valeur
                break
    questions = []
    for element in donnees:
        options = element.get("options", [])
        try:
            reponse = int(element.get("reponse"))
        except (TypeError, ValueError):
            continue
        if len(options) != 4 or reponse < 0 or reponse > 3:
            continue
        questions.append(
            {
                "question": element.get("question", ""),
                "options": options,
                "reponse": reponse,
                "explication": element.get("explication", ""),
            }
        )
    return questions


def generer_quiz(texte, nombre=5):
    verifier_texte(texte)
    consigne = (
        "Tu es un assistant de révision. À partir des notes de cours ci-dessous, "
        "écris " + str(nombre) + " questions à choix multiples dans la langue du texte. "
        "Les questions doivent porter sur la compréhension, pas sur des détails anecdotiques. "
        "Réponds uniquement avec un tableau JSON, sans aucun texte autour. "
        "Chaque élément du tableau contient exactement ces clés : "
        '"question" (le texte de la question), '
        '"options" (un tableau de 4 réponses possibles), '
        '"reponse" (l\'index de la bonne réponse, un nombre entier entre 0 et 3), '
        '"explication" (une phrase expliquant pourquoi cette réponse est la bonne).\n\n'
        + texte[:TAILLE_MAX]
    )
    brut = demander_a_gemini(consigne, format_json=True)
    donnees = json.loads(nettoyer_json(brut))
    questions = verifier_quiz(donnees)
    if not questions:
        raise RuntimeError("L'IA n'a pas renvoyé de quiz exploitable. Réessaie.")
    return questions

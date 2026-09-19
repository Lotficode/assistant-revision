import pandas as pd
import streamlit as st

from assistant import generer_quiz, lire_pdf, resumer
from base import effacer_scores, enregistrer_score, lire_scores

st.set_page_config(page_title="Assistant de révision", page_icon="📚")

st.title("📚 Assistant de révision")
st.caption(
    "Dépose tes notes de cours en PDF : l'IA en fait un résumé, "
    "te prépare un quiz et suit ta progression."
)

fichier = st.file_uploader("Notes de cours (PDF)", type="pdf")

if fichier is not None and st.session_state.get("document") != fichier.name:
    with st.spinner("Lecture du PDF..."):
        st.session_state.texte = lire_pdf(fichier)
    st.session_state.document = fichier.name
    st.session_state.resume = None
    st.session_state.quiz = None
    st.session_state.corrige = False

if st.session_state.get("texte"):
    st.success(
        st.session_state.document
        + " — "
        + str(len(st.session_state.texte))
        + " caractères lus"
    )

onglet_resume, onglet_quiz, onglet_progression = st.tabs(
    ["Résumé", "Quiz", "Progression"]
)

with onglet_resume:
    if not st.session_state.get("texte"):
        st.info("Commence par déposer un PDF ci-dessus.")
    else:
        if st.button("Générer le résumé"):
            with st.spinner("L'IA lit tes notes..."):
                try:
                    st.session_state.resume = resumer(st.session_state.texte)
                except Exception as erreur:
                    st.error(str(erreur))
        if st.session_state.get("resume"):
            st.markdown(st.session_state.resume)

with onglet_quiz:
    if not st.session_state.get("texte"):
        st.info("Commence par déposer un PDF ci-dessus.")
    else:
        nombre = st.slider("Nombre de questions", 3, 10, 5)
        if st.button("Créer un quiz"):
            with st.spinner("L'IA prépare tes questions..."):
                try:
                    nouveau_quiz = generer_quiz(st.session_state.texte, nombre)
                    for numero in range(10):
                        st.session_state.pop("q" + str(numero), None)
                    st.session_state.quiz = nouveau_quiz
                    st.session_state.corrige = False
                except Exception as erreur:
                    st.error(str(erreur))

        quiz = st.session_state.get("quiz")

        if quiz:
            with st.form("formulaire_quiz"):
                for numero, question in enumerate(quiz):
                    st.write("**Question " + str(numero + 1) + ".** " + question["question"])
                    st.radio(
                        "Réponse",
                        question["options"],
                        key="q" + str(numero),
                        index=None,
                        label_visibility="collapsed",
                    )
                envoye = st.form_submit_button("Corriger")

            if envoye:
                score = 0
                for numero, question in enumerate(quiz):
                    bonne = question["options"][question["reponse"]]
                    if st.session_state.get("q" + str(numero)) == bonne:
                        score = score + 1
                st.session_state.score = score
                st.session_state.corrige = True
                enregistrer_score(st.session_state.document, score, len(quiz))

            if st.session_state.get("corrige"):
                score = st.session_state.score
                st.metric("Score", str(score) + " / " + str(len(quiz)))
                for numero, question in enumerate(quiz):
                    bonne = question["options"][question["reponse"]]
                    donnee = st.session_state.get("q" + str(numero))
                    if donnee == bonne:
                        st.success("Question " + str(numero + 1) + " : bonne réponse.")
                    else:
                        st.error(
                            "Question "
                            + str(numero + 1)
                            + " : la bonne réponse était « "
                            + str(bonne)
                            + " »."
                        )
                    if question["explication"]:
                        st.caption(question["explication"])

with onglet_progression:
    lignes = lire_scores()
    if not lignes:
        st.info("Aucun quiz terminé pour l'instant.")
    else:
        tableau = pd.DataFrame(lignes, columns=["date", "document", "score", "total"])
        tableau["réussite (%)"] = (tableau["score"] / tableau["total"] * 100).round(0)
        colonne_gauche, colonne_droite = st.columns(2)
        colonne_gauche.metric("Quiz terminés", str(len(tableau)))
        colonne_droite.metric(
            "Moyenne", str(int(tableau["réussite (%)"].mean())) + " %"
        )
        st.line_chart(tableau["réussite (%)"])
        st.dataframe(tableau, hide_index=True)
        if st.button("Effacer l'historique"):
            effacer_scores()
            st.rerun()

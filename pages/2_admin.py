# pages/2_admin.py
import streamlit as st
import pandas as pd
import os
import csv
from utils.chat_engine import add_manual_pair, load_unanswered_questions, mark_as_answered
from utils.document_loader import extract_qa_pairs_from_pdf

ADMIN_PASSWORD = "zia2025"
DATA_FILE = "data/conversations.csv"
UNANSWERED_FILE = "data/unanswered_questions.csv"
DOC_FOLDER = "data/documents"

os.makedirs("data", exist_ok=True)
os.makedirs(DOC_FOLDER, exist_ok=True)

st.set_page_config(page_title="⚙️ Admin - Zia", page_icon="🛠️")
st.title("⚙️ Admin - Entraîner Zia")

# --- Authentification ---
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    st.subheader("Mot de passe requis")
    pwd = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if pwd == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect.")
    st.stop()
# Dans pages/2_admin.py, section admin
if st.button("🗑️ Réinitialiser toutes les données"):
    pd.DataFrame(columns=["question", "reponse"]).to_csv(DATA_FILE, index=False, quoting=csv.QUOTE_ALL)
    pd.DataFrame(columns=["question"]).to_csv(UNANSWERED_FILE, index=False, quoting=csv.QUOTE_ALL)
    st.success("✅ Toutes les données ont été effacées.")
    st.rerun()
# --- Déconnexion ---
if st.button("🔒 Déconnexion"):
    st.session_state.admin_logged_in = False
    st.rerun()

# --- Section 1 : Ajout manuel ---
st.subheader("➕ Ajouter une paire Q/R")
col1, col2 = st.columns(2)
with col1:
    q = st.text_input("Question")
with col2:
    r = st.text_input("Réponse")

if st.button("✅ Ajouter"):
    if q and r:
        add_manual_pair(q, r)
        st.success("✅ Ajouté !")
    else:
        st.error("Remplis les deux champs.")

# --- Section 2 : Charger un document ---
st.subheader("📄 Charger un document (PDF, TXT)")
uploaded_file = st.file_uploader("Choisis un fichier", type=["pdf", "txt"])

def parse_qa_from_text(text):
    """Parse un texte brut contenant des lignes alternées : Question / Réponse"""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    pairs = []
    i = 0
    while i < len(lines):
        # Ignorer les séparateurs
        if lines[i] in ["|", "---", "Question", "Réponse", "||", "| ---|---|"]:
            i += 1
            continue
        question = lines[i]
        if i + 1 < len(lines):
            response = lines[i + 1]
            # Nettoyer les artefacts
            question = question.replace("|", "").strip()
            response = response.replace("|", "").strip()
            if question and response:
                pairs.append((question, response))
            i += 2
        else:
            break
    return pairs

if uploaded_file:
    st.write(f"📄 Fichier : {uploaded_file.name}")
    from utils.document_loader import extract_qa_pairs_from_pdf

# ...

if uploaded_file and uploaded_file.name.endswith(".pdf"):
    if st.button("Extraire et entraîner"):
        with st.spinner("Analyse du PDF..."):
            try:
                uploaded_file.seek(0)
                pairs = extract_qa_pairs_from_pdf(uploaded_file)
                if pairs:
                    for q, r in pairs:
                        add_manual_pair(q, r)
                    st.success(f"✅ {len(pairs)} paires ajoutées !")
                    # Sauvegarder le PDF
                    with open(os.path.join(DOC_FOLDER, uploaded_file.name), "wb") as f:
                        uploaded_file.seek(0)
                        f.write(uploaded_file.getbuffer())
                else:
                    st.error("❌ Aucune paire trouvée.")
            except Exception as e:
                st.error(f"Erreur : {e}")

# --- Section 3 : Questions non résolues ---
st.subheader("❓ Questions en attente d’apprentissage")
unanswered = load_unanswered_questions()

if unanswered.empty:
    st.info("Aucune question en attente.")
else:
    for idx, row in unanswered.iterrows():
        q = row["question"]
        st.write(f"**❓ {q}**")
        answer = st.text_input(f"Réponse pour : {q}", key=f"ans_{idx}")
        if st.button("✅ Enseigner", key=f"btn_{idx}"):
            if answer.strip():
                add_manual_pair(q, answer)
                mark_as_answered(q)
                st.success("Zia a appris !")
                st.rerun()
    st.caption(f"Total : {len(unanswered)} questions non résolues.")

# --- Voir toutes les paires connues ---
if st.checkbox("👁️ Voir toutes les paires connues"):
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, quoting=csv.QUOTE_ALL, encoding="utf-8")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune donnée.")
# utils/chat_engine.py
import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import csv

DATA_FILE = "data/conversations.csv"
UNANSWERED_FILE = "data/unanswered_questions.csv"

os.makedirs("data", exist_ok=True)

def _ensure_csv(file_path, columns):
    """Crée ou répare un fichier CSV avec les colonnes données."""
    if not os.path.exists(file_path):
        pd.DataFrame(columns=columns).to_csv(file_path, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")
        return

    # Si le fichier existe mais est vide
    if os.path.getsize(file_path) == 0:
        pd.DataFrame(columns=columns).to_csv(file_path, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")
        return

    # Vérifier si les colonnes sont présentes
    try:
        df = pd.read_csv(file_path, quoting=csv.QUOTE_ALL, encoding="utf-8", nrows=0)
        if list(df.columns) != columns:
            raise ValueError("Colonnes invalides")
    except (pd.errors.EmptyDataError, ValueError, pd.errors.ParserError):
        # Recréer le fichier proprement
        pd.DataFrame(columns=columns).to_csv(file_path, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")

def init_files():
    _ensure_csv(DATA_FILE, ["question", "reponse"])
    _ensure_csv(UNANSWERED_FILE, ["question"])

def load_manual_data():
    init_files()
    return pd.read_csv(DATA_FILE, quoting=csv.QUOTE_ALL, encoding="utf-8")

def load_unanswered_questions():
    init_files()
    return pd.read_csv(UNANSWERED_FILE, quoting=csv.QUOTE_ALL, encoding="utf-8")

def add_manual_pair(question, response):
    df = load_manual_data()
    new_row = pd.DataFrame({"question": [question.strip()], "reponse": [response.strip()]})
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")

def save_unanswered_question(question):
    df = load_unanswered_questions()
    # Éviter les doublons (insensible à la casse)
    if not df["question"].str.lower().eq(question.lower()).any():
        new_row = pd.DataFrame({"question": [question.strip()]})
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(UNANSWERED_FILE, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")

def mark_as_answered(question):
    df = load_unanswered_questions()
    df = df[df["question"] != question]
    df.to_csv(UNANSWERED_FILE, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")

def get_response(query):
    df = load_manual_data()
    
    if df.empty or len(df) == 0:
        save_unanswered_question(query)
        return "Je n’ai pas encore de connaissances… mais j’apprends vite !\nPeux-tu m’aider à répondre à ça ? 😊"

    questions = df["question"].tolist()
    responses = df["reponse"].tolist()

    vectorizer = TfidfVectorizer(lowercase=True, strip_accents='unicode', ngram_range=(1,2))
    vectors = vectorizer.fit_transform(questions)
    query_vec = vectorizer.transform([query])
    similarities = cosine_similarity(query_vec, vectors).flatten()
    best_score = float(similarities.max())

    if best_score > 0.15:
        best_idx = int(np.argmax(similarities))
        return responses[best_idx]
    else:
        save_unanswered_question(query)
        return (
            "Hmm… désolé, je ne connais pas encore la réponse à cette question. 🤔\n"
            "Si vous avez une autre question, n'hésitez pas à me la poser ! 💙"
        )
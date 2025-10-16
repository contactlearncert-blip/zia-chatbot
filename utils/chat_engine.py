# utils/chat_engine.py
import os
import pandas as pd
import numpy as np
import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Essayer d'importer sentence-transformers (optionnel mais recommandé)
USE_SEMANTIC = False
SEMANTIC_MODEL = None
try:
    from sentence_transformers import SentenceTransformer
    SEMANTIC_MODEL = SentenceTransformer('dangvantuan/sentence-camembert-base')
    USE_SEMANTIC = True
except ImportError:
    pass

# Chemins des fichiers
DATA_FILE = "data/conversations.csv"
UNANSWERED_FILE = "data/unanswered_questions.csv"

os.makedirs("data", exist_ok=True)

def _ensure_csv(file_path, columns):
    """Crée ou répare un fichier CSV avec les colonnes données."""
    if not os.path.exists(file_path):
        pd.DataFrame(columns=columns).to_csv(file_path, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")
        return
    if os.path.getsize(file_path) == 0:
        pd.DataFrame(columns=columns).to_csv(file_path, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")
        return
    try:
        df = pd.read_csv(file_path, quoting=csv.QUOTE_ALL, encoding="utf-8", nrows=0)
        if list(df.columns) != columns:
            raise ValueError("Colonnes invalides")
    except (pd.errors.EmptyDataError, ValueError, pd.errors.ParserError):
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
    if not question or not question.strip():
        return
    clean_q = question.strip()
    df = load_unanswered_questions()
    if not df["question"].str.lower().eq(clean_q.lower()).any():
        new_row = pd.DataFrame({"question": [clean_q]})
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(UNANSWERED_FILE, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")

def mark_as_answered(question):
    df = load_unanswered_questions()
    df = df[df["question"] != question]
    df.to_csv(UNANSWERED_FILE, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")

def get_response(query):
    clean_query = query.strip()
    if not clean_query:
        return "Hmm... tu n’as rien dit ! 😊 Pose-moi une question."

    df = load_manual_data()
    if df.empty or len(df) == 0:
        save_unanswered_question(clean_query)
        return "Je n’ai pas encore de connaissances… mais j’apprends vite !\nPeux-tu m’aider à répondre à ça ? 😊"

    questions = df["question"].tolist()
    responses = df["reponse"].tolist()

    try:
        if USE_SEMANTIC:
            # Embeddings sémantiques (meilleure compréhension du sens)
            all_texts = questions + [clean_query]
            embeddings = SEMANTIC_MODEL.encode(all_texts)
            query_emb = embeddings[-1].reshape(1, -1)
            questions_emb = embeddings[:-1]
            similarities = cosine_similarity(query_emb, questions_emb).flatten()
            threshold = 0.5
        else:
            # Fallback sur TF-IDF
            vectorizer = TfidfVectorizer(lowercase=True, strip_accents='unicode', ngram_range=(1, 2))
            vectors = vectorizer.fit_transform(questions)
            query_vec = vectorizer.transform([clean_query])
            similarities = cosine_similarity(query_vec, vectors).flatten()
            threshold = 0.15

        if len(similarities) == 0:
            save_unanswered_question(clean_query)
            return "🤔 Je ne comprends pas encore cette question. Mais je l’ai notée !"

        best_score = float(similarities.max())
        if best_score > threshold:
            best_idx = int(np.argmax(similarities))
            return responses[best_idx]
        else:
            save_unanswered_question(clean_query)
            return (
                "Hmm… désolé, je ne connais pas encore la réponse à cette question. 🤔\n"
                "Mais je l’ai enregistrée ! Si tu veux, tu peux m’apprendre la bonne réponse depuis la page admin.\n"
                "Merci de m’aider à grandir ! 💙"
            )
    except Exception:
        save_unanswered_question(clean_query)
        return "Oups ! Une petite erreur s’est glissée… mais je retiens ta question pour m’améliorer. 💪"
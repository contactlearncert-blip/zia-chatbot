# utils/document_loader.py
import pdfplumber
from io import BytesIO
import re

def extract_qa_pairs_from_pdf(pdf_file):
    """
    Extrait les paires Q/R d'un PDF structuré comme 'Question.pdf'.
    Gère les sauts de ligne dans les réponses et les artefacts de tableau.
    """
    full_text = ""
    with pdfplumber.open(BytesIO(pdf_file.read())) as pdf:
        for page in pdf.pages:
            full_text += page.extract_text() or ""

    # Diviser en lignes et nettoyer
    lines = full_text.splitlines()
    clean_lines = []
    for line in lines:
        stripped = line.strip()
        # Ignorer les séparateurs de tableau
        if stripped in ["|", "||", "---", "| ---|---|", "Question", "Réponse", ""]:
            continue
        # Nettoyer les | en début/fin
        stripped = re.sub(r"^\s*\|\s*", "", stripped)
        stripped = re.sub(r"\s*\|\s*$", "", stripped)
        if stripped:
            clean_lines.append(stripped)

    # Reconstruire les paires en supposant : [Q, R, Q, R, ...]
    pairs = []
    i = 0
    while i < len(clean_lines):
        question = clean_lines[i]
        # Fusionner les lignes suivantes si elles commencent en minuscule (suite de la réponse)
        response_parts = []
        j = i + 1
        while j < len(clean_lines):
            next_line = clean_lines[j]
            # Si la ligne commence par une majuscule ou un mot-clé de question → c'est une nouvelle question
            if re.match(r"^[A-ZÀ-ÖØ-Þ]", next_line) or next_line in [
                "Bonjour", "Salut!", "Coucou!", "Comment", "Ça", "Tu", "Quel", "C’est", "Qui", "Aide", "Peux", "Besoin",
                "J’ai", "Quelle", "Il", "C’est", "Tu", "Es", "Combien", "Qu’est", "Parles", "Traduis", "Dis", "Encore",
                "Racontes", "Tu", "Quel", "Chanson", "Tu", "Tu", "On", "Tu", "Tu", "Tu", "Tu", "Tu", "Tu", "Tu", "Tu",
                "Pourquoi", "Tu", "L’avenir", "Tu", "Quel", "Tu", "Tu", "Donne", "Encore", "Tu", "Écris", "Parle", "C’est",
                "Quelle", "Et", "Combien", "Tu", "Tu", "Qu’est", "C’est", "Tu", "Tu", "Explique", "C’est", "Tu", "Quel",
                "iPhone", "Tu", "Tu", "Tu", "Tu", "Tu", "Tu", "Tu", "Tu", "Excuse", "Pardon", "Merci", "Tu", "Tu", "Tu",
                "Dis", "Encore", "Une", "Tu", "Tu", "Tu", "Tu", "Tu", "Tu", "Tu", "Tu", "Tu", "Fais", "Tu", "On", "Adieu",
                "Au", "Bye", "Ciao", "À"
            ]:
                break
            response_parts.append(next_line)
            j += 1

        if response_parts:
            response = " ".join([clean_lines[i+1]] + response_parts)
            i = j  # passer à la prochaine question
        else:
            response = clean_lines[i+1] if i+1 < len(clean_lines) else ""
            i += 2

        if question and response:
            # Nettoyer les espaces multiples
            question = re.sub(r"\s+", " ", question)
            response = re.sub(r"\s+", " ", response)
            pairs.append((question, response))

    return pairs
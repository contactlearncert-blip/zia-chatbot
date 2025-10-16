# utils/document_loader.py
import pdfplumber
from io import BytesIO

def extract_qa_pairs_from_pdf(pdf_file):
    """
    Extrait les paires Q/R d'un PDF comme celui de 'Question.pdf'
    en gérant les sauts de ligne et les lignes vides.
    """
    full_text = ""
    with pdfplumber.open(BytesIO(pdf_file.read())) as pdf:
        for page in pdf.pages:
            full_text += page.extract_text() or ""

    lines = [line.strip() for line in full_text.splitlines() if line.strip()]
    
    # Supprimer les lignes inutiles
    clean_lines = []
    for line in lines:
        if line in ["Question", "Réponse", "|", "||", "---", "| ---|---|"]:
            continue
        # Nettoyer les | au début/fin
        line = line.strip("| ").strip()
        if line:
            clean_lines.append(line)

    # Reconstruire les paires
    pairs = []
    i = 0
    while i < len(clean_lines):
        question = clean_lines[i]
        # Chercher la prochaine ligne qui ressemble à une réponse (non vide)
        if i + 1 < len(clean_lines):
            response = clean_lines[i + 1]
            pairs.append((question, response))
            i += 2
        else:
            break

    return pairs
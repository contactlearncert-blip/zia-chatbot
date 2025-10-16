# utils/pdf_table_parser.py
import pdfplumber
import pandas as pd
from io import BytesIO

def extract_qa_from_pdf(pdf_file):
    """
    Extrait les paires question/réponse d'un PDF structuré en tableau.
    Retourne une liste de tuples: [(q1, r1), (q2, r2), ...]
    """
    pairs = []
    with pdfplumber.open(BytesIO(pdf_file.read())) as pdf:
        for page in pdf.pages:
            # Extraire les tables
            tables = page.extract_tables()
            for table in tables:
                if not table or len(table) < 2:
                    continue
                # Supprimer l'en-tête si présent
                if "Question" in str(table[0]) or "Réponse" in str(table[0]):
                    rows = table[1:]
                else:
                    rows = table

                for row in rows:
                    if row and len(row) >= 2:
                        q = str(row[0]).strip()
                        r = str(row[1]).strip()
                        # Nettoyer les artefacts
                        if q and r and not q.startswith("|") and not r.startswith("|"):
                            # Réparer les sauts de ligne dans les questions/réponses
                            q = q.replace("\n", " ").strip()
                            r = r.replace("\n", " ").strip()
                            if q and r:
                                pairs.append((q, r))
    return pairs
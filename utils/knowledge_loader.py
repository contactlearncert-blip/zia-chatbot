# utils/knowledge_loader.py
import json
import os
from utils.chat_engine import add_manual_pair

def load_knowledge_from_json(json_path):
    """
    Charge un fichier JSON contenant des paires {"question": "...", "reponse": "..."}
    et les ajoute à la base de connaissances.
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Fichier non trouvé : {json_path}")
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    added = 0
    for item in data:
        if "question" in item and "reponse" in item:
            add_manual_pair(item["question"], item["reponse"])
            added += 1
    return added
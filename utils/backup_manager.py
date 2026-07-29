# utils/backup_manager.py
import sqlite3
import shutil
import json
import os
from pathlib import Path
from database.database import DB_PATH, fetch_query, get_connection

# Définition des dossiers de sauvegarde
BACKUP_DIR = Path("backups")
JSON_BACKUP_DIR = Path("json_backups")

# Créer les dossiers s'ils n'existent pas
BACKUP_DIR.mkdir(exist_ok=True)
JSON_BACKUP_DIR.mkdir(exist_ok=True)

def backup_sqlite():
    """Copie le fichier school.db dans le dossier backups/ avec la date du jour."""
    # On utilise la connexion pour s'assurer que toutes les données en mémoire sont écrites
    conn = get_connection()
    conn.commit()
    conn.close()
    
    # Nom du fichier avec la date du jour
    date_str = datetime.now().strftime("%Y_%m_%d")
    backup_file = BACKUP_DIR / f"backup_{date_str}.db"
    
    try:
        # Copie physique du fichier
        shutil.copy2(DB_PATH, backup_file)
        return str(backup_file)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde SQLite: {e}")
        return None

def backup_json():
    """Exporte les tables principales dans un fichier JSON unique."""
    tables_to_export = ['students', 'parents', 'teachers', 'grades', 'payments', 'classes', 'subjects', 'users']
    data = {}
    
    for table in tables_to_export:
        # Récupère toutes les lignes de la table
        rows = fetch_query(f"SELECT * FROM {table}")
        data[table] = rows
        
    date_str = datetime.now().strftime("%Y_%m_%d")
    backup_file = JSON_BACKUP_DIR / f"backup_{date_str}.json"
    
    try:
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return str(backup_file)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde JSON: {e}")
        return None

def get_sqlite_backups_list():
    """Liste tous les fichiers de sauvegarde SQLite disponibles."""
    files = list(BACKUP_DIR.glob("*.db"))
    # Trier par date de modification (le plus récent en premier)
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return files

def restore_sqlite(backup_file_path):
    """Remplace la base actuelle par une sauvegarde."""
    try:
        # Fermer les connexions (Streamlit gère ça, mais par précaution)
        # Remplacer le fichier
        shutil.copy2(backup_file_path, DB_PATH)
        return True
    except Exception as e:
        print(f"Erreur lors de la restauration SQLite: {e}")
        return False

# Importation tardive pour éviter les erreurs circulaires
from datetime import datetime

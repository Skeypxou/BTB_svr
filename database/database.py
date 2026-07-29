# database/database.py
import sqlite3
import os
from pathlib import Path

# --- Configuration du chemin de la base de données ---
# On s'assure que le dossier 'database' existe
BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "database"
DB_DIR.mkdir(exist_ok=True) # Crée le dossier s'il n'existe pas

DB_PATH = DB_DIR / "school.db"

def get_connection():
    """
    Crée et retourne une connexion à la base de données SQLite.
    Cette fonction sera importée dans tous les autres fichiers du projet.
    """
    conn = sqlite3.connect(str(DB_PATH))
    # Permet d'accéder aux colonnes par leur nom (ex: row['nom']) au lieu de row[0]
    conn.row_factory = sqlite3.Row 
    # Active les clés étrangères (indispensable pour que les relations marchent)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def execute_query(query, params=()):
    """
    Exécute une requête qui modifie la base (INSERT, UPDATE, DELETE).
    Gère automatiquement la sauvegarde (commit) et la fermeture.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid # Retourne l'ID de l'élément créé/modifié
    except Exception as e:
        print(f"Erreur SQL (execute_query): {e}")
        conn.rollback() # Annule les changements en cas d'erreur
        return None
    finally:
        conn.close()

def fetch_query(query, params=()):
    """
    Exécute une requête qui lit la base (SELECT).
    Retourne une liste de dictionnaires.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows] # Convertit les résultats en dictionnaires
    except Exception as e:
        print(f"Erreur SQL (fetch_query): {e}")
        return []
    finally:
        conn.close()

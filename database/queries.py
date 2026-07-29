# database/queries.py
import sqlite3
from database.database import execute_query, fetch_query, get_connection
import os
from pathlib import Path

# S'assurer que le dossier photos existe
PHOTOS_DIR = Path("photos")
PHOTOS_DIR.mkdir(exist_ok=True)

def generate_matricule():
    """Génère un matricule automatique unique (ex: ELE-2024-001)."""
    # Compte le nombre d'élèves existants pour incrémenter le numéro
    count = fetch_query("SELECT COUNT(id) as count FROM students")[0]['count']
    year = "2024" # Pour simplifier, on peut récupérer l'année active plus tard
    return f"ELE-{year}-{count + 1:03d}"

def get_all_students(search_term=""):
    """Récupère tous les élèves avec leur classe, pour affichage dans un tableau."""
    query = """
        SELECT s.id, s.matricule, s.first_name, s.last_name, s.gender, s.dob, c.name as class_name
        FROM students s
        LEFT JOIN enrollments e ON s.id = e.student_id AND e.school_year_id = (SELECT id FROM school_years WHERE is_active = 1)
        LEFT JOIN classes c ON e.class_id = c.id
    """
    if search_term:
        query += " WHERE s.first_name LIKE ? OR s.last_name LIKE ? OR s.matricule LIKE ?"
        params = (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
        return fetch_query(query, params)
    return fetch_query(query)

def get_all_classes():
    """Récupère la liste des classes pour le menu déroulant."""
    return fetch_query("SELECT id, name FROM classes ORDER BY name")

def get_all_parents():
    """Récupère la liste des parents pour le menu déroulant."""
    return fetch_query("SELECT id, first_name || ' ' || last_name as full_name FROM parents")

def add_student(first_name, last_name, dob, gender, address, phone, photo_filename, class_id, parent_id):
    """Ajoute un nouvel élève et l'inscrit dans sa classe pour l'année active."""
    matricule = generate_matricule()
    active_year = fetch_query("SELECT id FROM school_years WHERE is_active = 1")[0]
    
    # 1. Insertion de l'élève
    student_query = """
        INSERT INTO students (matricule, first_name, last_name, dob, gender, address, phone, photo_path, school_year_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    student_id = execute_query(student_query, (matricule, first_name, last_name, dob, gender, address, phone, photo_filename, active_year['id']))
    
    # 2. Inscription (lien élève-classe pour l'année active)
    if student_id and class_id:
        enrollment_query = """
            INSERT INTO enrollments (student_id, class_id, date, status, school_year_id)
            VALUES (?, ?, DATE('now'), 'Accepté', ?)
        """
        execute_query(enrollment_query, (student_id, class_id, active_year['id']))
        
    # 3. Lien avec le parent
    if student_id and parent_id:
        execute_query("INSERT INTO student_parents (student_id, parent_id, relation) VALUES (?, ?, 'Tuteur')", 
                      (student_id, parent_id))
                      
    return matricule

def delete_student(student_id):
    """Supprime un élève de la base de données."""
    execute_query("DELETE FROM students WHERE id = ?", (student_id,))

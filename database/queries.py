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
    # --- AJOUTER À LA FIN DE database/queries.py ---

def get_all_parents_with_children_count(search_term=""):
    """Récupère tous les parents et compte combien d'enfants each parent a."""
    query = """
        SELECT p.id, p.first_name, p.last_name, p.phone, p.email, p.profession,
               (SELECT COUNT(sp.id) FROM student_parents sp WHERE sp.parent_id = p.id) as children_count
        FROM parents p
    """
    if search_term:
        query += " WHERE p.first_name LIKE ? OR p.last_name LIKE ? OR p.phone LIKE ?"
        params = (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
        return fetch_query(query, params)
    return fetch_query(query)

def add_parent(first_name, last_name, phone, email, address, profession):
    """Ajoute un nouveau parent dans la base de données."""
    query = """
        INSERT INTO parents (first_name, last_name, phone, email, address, profession)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    return execute_query(query, (first_name, last_name, phone, email, address, profession))

def delete_parent(parent_id):
    """Supprime un parent. (Attention, s'il a des enfants liés, il faudra gérer cette contrainte)."""
    # On supprime d'abord les liens avec les enfants pour ne pas casser la base
    execute_query("DELETE FROM student_parents WHERE parent_id = ?", (parent_id,))
    # Puis on supprime le parent
    execute_query("DELETE FROM parents WHERE id = ?", (parent_id,))
    # --- AJOUTER À LA FIN DE database/queries.py ---

def generate_teacher_matricule():
    """Génère un matricule automatique unique pour un enseignant (ex: ENS-001)."""
    count = fetch_query("SELECT COUNT(id) as count FROM teachers")[0]['count']
    return f"ENS-{count + 1:03d}"

def get_all_teachers(search_term=""):
    """Récupère tous les enseignants avec le nom de leur matière."""
    query = """
        SELECT t.id, t.matricule, t.first_name, t.last_name, t.phone, t.email, 
               t.diploma, t.hire_date, t.salary, s.name as subject_name
        FROM teachers t
        LEFT JOIN subjects s ON t.subject_id = s.id
    """
    if search_term:
        query += " WHERE t.first_name LIKE ? OR t.last_name LIKE ? OR t.matricule LIKE ?"
        params = (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
        return fetch_query(query, params)
    return fetch_query(query)

def get_all_subjects():
    """Récupère la liste des matières pour le menu déroulant."""
    return fetch_query("SELECT id, name FROM subjects WHERE is_active = 1 ORDER BY name")

def add_teacher(first_name, last_name, phone, email, subject_id, diploma, hire_date, salary):
    """Ajoute un nouvel enseignant dans la base de données."""
    matricule = generate_teacher_matricule()
    query = """
        INSERT INTO teachers (matricule, first_name, last_name, phone, email, subject_id, diploma, hire_date, salary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    return execute_query(query, (matricule, first_name, last_name, phone, email, subject_id, diploma, hire_date, salary))

def delete_teacher(teacher_id):
    """Supprime un enseignant de la base de données."""
    execute_query("DELETE FROM teachers WHERE id = ?", (teacher_id,))
    # --- AJOUTER À LA FIN DE database/queries.py ---

def get_all_school_years():
    """Récupère toutes les années scolaires triées par nom."""
    return fetch_query("SELECT id, name, is_active, is_closed FROM school_years ORDER BY name DESC")

def get_active_school_year():
    """Récupère l'année scolaire actuellement active."""
    result = fetch_query("SELECT id, name FROM school_years WHERE is_active = 1")
    return result[0] if result else None

def add_school_year(name):
    """Ajoute une nouvelle année scolaire."""
    # Vérifier si elle existe déjà
    existing = fetch_query("SELECT id FROM school_years WHERE name = ?", (name,))
    if existing:
        return None
    return execute_query("INSERT INTO school_years (name, is_active, is_closed) VALUES (?, 0, 0)", (name,))

def set_active_school_year(year_id):
    """Définit une année comme active et désactive toutes les autres."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 1. Désactiver toutes les années
        cursor.execute("UPDATE school_years SET is_active = 0")
        # 2. Activer l'année choisie
        cursor.execute("UPDATE school_years SET is_active = 1 WHERE id = ?", (year_id,))
        # 3. Mettre à jour les paramètres de l'école
        cursor.execute("UPDATE school_settings SET active_year_id = ?", (year_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erreur lors du changement d'année active: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
        # --- AJOUTER À LA FIN DE database/queries.py ---

# --- MATIERES ---
def add_subject(name, coefficient):
    return execute_query("INSERT INTO subjects (name, coefficient, is_active) VALUES (?, ?, 1)", (name, coefficient))

def get_all_subjects():
    return fetch_query("SELECT id, name, coefficient, is_active FROM subjects ORDER BY name")

def delete_subject(subject_id):
    return execute_query("DELETE FROM subjects WHERE id = ?", (subject_id,))

# --- NIVEAUX ---
def add_level(name):
    return execute_query("INSERT INTO levels (name) VALUES (?)", (name,))

def get_all_levels():
    return fetch_query("SELECT id, name FROM levels ORDER BY name")

def delete_level(level_id):
    return execute_query("DELETE FROM levels WHERE id = ?", (level_id,))

# --- CLASSES ---
def add_class(name, level_id, capacity):
    return execute_query("INSERT INTO classes (name, level_id, capacity) VALUES (?, ?, ?)", (name, level_id, capacity))

def get_all_classes_with_levels():
    query = """
        SELECT c.id, c.name, l.name as level_name, c.capacity 
        FROM classes c
        LEFT JOIN levels l ON c.level_id = l.id
        ORDER BY c.name
    """
    return fetch_query(query)
    # --- AJOUTER À LA FIN DE database/queries.py ---

def get_students_by_class(class_id):
    """Récupère les élèves inscrits dans une classe spécifique pour l'année active."""
    query = """
        SELECT s.id, s.matricule, s.first_name, s.last_name 
        FROM students s
        JOIN enrollments e ON s.id = e.student_id
        WHERE e.class_id = ? AND e.school_year_id = (SELECT id FROM school_years WHERE is_active = 1)
        ORDER BY s.last_name, s.first_name
    """
    return fetch_query(query, (class_id,))

def save_grade(student_id, subject_id, eval_type_id, score, max_score, trimester):
    """Enregistre ou met à jour une note pour un élève."""
    active_year = fetch_query("SELECT id FROM school_years WHERE is_active = 1")[0]
    # On vérifie si la note existe déjà pour cet élève, matière, type et trimestre
    existing = fetch_query("""
        SELECT id FROM grades 
        WHERE student_id = ? AND subject_id = ? AND evaluation_type_id = ? AND trimester = ? AND school_year_id = ?
    """, (student_id, subject_id, eval_type_id, trimester, active_year['id']))
    
    if existing:
        # Mise à jour
        query = """
            UPDATE grades SET score = ?, max_score = ?
            WHERE id = ?
        """
        execute_query(query, (score, max_score, existing[0]['id']))
    else:
        # Insertion
        query = """
            INSERT INTO grades (student_id, subject_id, evaluation_type_id, score, max_score, trimester, school_year_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        execute_query(query, (student_id, subject_id, eval_type_id, score, max_score, trimester, active_year['id']))

def calculate_class_rankings(class_id, trimester):
    """Calcule la moyenne générale de chaque élève de la classe et établit le classement."""
    students = get_students_by_class(class_id)
    if not students:
        return []
        
    active_year_id = fetch_query("SELECT id FROM school_years WHERE is_active = 1")[0]['id']
    rankings = []
    
    for student in students:
        # Récupérer toutes les notes de l'élève pour ce trimestre
        grades = fetch_query("""
            SELECT g.score, g.max_score, s.coefficient
            FROM grades g
            JOIN subjects s ON g.subject_id = s.id
            WHERE g.student_id = ? AND g.trimester = ? AND g.school_year_id = ?
        """, (student['id'], trimester, active_year_id))
        
        total_points = 0
        total_coefficients = 0
        
        for grade in grades:
            if grade['max_score'] > 0:
                # Moyenne de la matière sur 20
                subject_avg = (grade['score'] / grade['max_score']) * 20
                total_points += subject_avg * grade['coefficient']
                total_coefficients += grade['coefficient']
        
        general_avg = (total_points / total_coefficients) if total_coefficients > 0 else 0
        
        rankings.append({
            'student_id': student['id'],
            'matricule': student['matricule'],
            'name': f"{student['last_name']} {student['first_name']}",
            'average': round(general_avg, 2)
        })
        
    # Trier par moyenne décroissante
    rankings.sort(key=lambda x: x['average'], reverse=True)
    
    # Ajouter le rang
    for i, rank in enumerate(rankings):
        rank['rank'] = i + 1
        
    return rankings

def delete_class(class_id):
    return execute_query("DELETE FROM classes WHERE id = ?", (class_id,))

# --- TYPES D'EVALUATION ---
def add_evaluation_type(name):
    return execute_query("INSERT INTO evaluation_types (name) VALUES (?)", (name,))

def get_all_evaluation_types():
    return fetch_query("SELECT id, name FROM evaluation_types ORDER BY name")

def delete_evaluation_type(eval_id):
    return execute_query("DELETE FROM evaluation_types WHERE id = ?", (eval_id,))
    # --- AJOUTER À LA FIN DE database/queries.py ---

def save_attendance(student_id, date, status, is_justified, reason):
    """Enregistre une absence ou un retard pour un élève."""
    active_year = fetch_query("SELECT id FROM school_years WHERE is_active = 1")[0]
    query = """
        INSERT INTO attendance (student_id, date, status, is_justified, reason, school_year_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    # Convertir le booléen en entier pour SQLite (0 ou 1)
    justified_int = 1 if is_justified else 0
    return execute_query(query, (student_id, date, status, justified_int, reason, active_year['id']))

def get_attendance_by_class(class_id, date):
    """Récupère les absences d'une classe à une date précise."""
    query = """
        SELECT a.id, s.matricule, s.first_name, s.last_name, a.status, a.is_justified, a.reason
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        JOIN enrollments e ON s.id = e.student_id
        WHERE e.class_id = ? AND a.date = ? AND a.school_year_id = (SELECT id FROM school_years WHERE is_active = 1)
        ORDER BY s.last_name
    """
    return fetch_query(query, (class_id, date))

def get_attendance_by_student(student_id):
    """Récupère tout l'historique des absences d'un élève pour l'année en cours."""
    query = """
        SELECT date, status, is_justified, reason
        FROM attendance
        WHERE student_id = ? AND school_year_id = (SELECT id FROM school_years WHERE is_active = 1)
        ORDER BY date DESC
    """
    return fetch_query(query, (student_id,))
    # --- AJOUTER À LA FIN DE database/queries.py ---

def get_active_year_id():
    """Retourne l'ID de l'année scolaire active."""
    result = fetch_query("SELECT id FROM school_years WHERE is_active = 1")
    return result[0]['id'] if result else None

# --- FRAIS SCOLAIRES ---
def add_school_fee(name, amount):
    """Ajoute un type de frais pour l'année active."""
    active_year = get_active_year_id()
    return execute_query("INSERT INTO school_fees (name, amount, school_year_id) VALUES (?, ?, ?)", 
                         (name, amount, active_year))

def get_all_school_fees():
    """Récupère tous les types de frais de l'année active."""
    active_year = get_active_year_id()
    return fetch_query("SELECT id, name, amount FROM school_fees WHERE school_year_id = ?", (active_year,))

# --- PAIEMENTS ---
def record_payment(student_id, fee_id, amount_paid, method, status):
    """Enregistre un nouveau paiement."""
    active_year = get_active_year_id()
    query = """
        INSERT INTO payments (student_id, fee_id, amount_paid, payment_date, method, status, school_year_id)
        VALUES (?, ?, ?, DATE('now'), ?, ?, ?)
    """
    return execute_query(query, (student_id, fee_id, amount_paid, method, status, active_year))

def get_payments_by_student(student_id):
    """Récupère l'historique des paiements d'un élève."""
    query = """
        SELECT p.payment_date, sf.name as fee_name, p.amount_paid, p.method, p.status
        FROM payments p
        JOIN school_fees sf ON p.fee_id = sf.id
        WHERE p.student_id = ? AND p.school_year_id = ?
        ORDER BY p.payment_date DESC
    """
    active_year = get_active_year_id()
    return fetch_query(query, (student_id, active_year))

def get_all_payments():
    """Récupère tous les paiements de l'année active pour le rapport global."""
    query = """
        SELECT p.payment_date, s.matricule, s.last_name || ' ' || s.first_name as student_name, 
               sf.name as fee_name, p.amount_paid, p.method, p.status
        FROM payments p
        JOIN students s ON p.student_id = s.id
        JOIN school_fees sf ON p.fee_id = sf.id
        WHERE p.school_year_id = ?
        ORDER BY p.payment_date DESC
    """
    active_year = get_active_year_id()
    return fetch_query(query, (active_year,))
    # --- AJOUTER À LA FIN DE database/queries.py ---

def get_school_settings():
    """Récupère les paramètres de l'école. Retourne un dict ou None si non configuré."""
    result = fetch_query("SELECT name, logo_path, address, phone, email, website, director_name FROM school_settings WHERE id = 1")
    return result[0] if result else None

def update_school_settings(name, address, phone, email, website, director_name, logo_filename=None):
    """Met à jour les paramètres de l'école. Gère l'upload du logo séparément."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if logo_filename:
            query = """
                UPDATE school_settings 
                SET name = ?, address = ?, phone = ?, email = ?, website = ?, director_name = ?, logo_path = ?
                WHERE id = 1
            """
            cursor.execute(query, (name, address, phone, email, website, director_name, logo_filename))
        else:
            query = """
                UPDATE school_settings 
                SET name = ?, address = ?, phone = ?, email = ?, website = ?, director_name = ?
                WHERE id = 1
            """
            cursor.execute(query, (name, address, phone, email, website, director_name))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erreur lors de la mise à jour des paramètres: {e}")
        return False
    finally:
        conn.close()
        # --- AJOUTER À LA FIN DE database/queries.py ---

def get_student_grades_for_bulletin(student_id, trimester):
    """Récupère les notes d'un élève pour un trimestre, regroupées par matière."""
    query = """
        SELECT s.name as subject_name, s.coefficient, 
               et.name as eval_type, g.score, g.max_score
        FROM grades g
        JOIN subjects s ON g.subject_id = s.id
        JOIN evaluation_types et ON g.evaluation_type_id = et.id
        WHERE g.student_id = ? AND g.trimester = ? AND g.school_year_id = (SELECT id FROM school_years WHERE is_active = 1)
        ORDER BY s.name
    """
    return fetch_query(query, (student_id, trimester))
    # --- AJOUTER À LA FIN DE database/queries.py ---

def get_student_details_for_certificate(student_id):
    """Récupère les infos complètes d'un élève pour générer un certificat."""
    query = """
        SELECT s.first_name, s.last_name, s.matricule, s.dob, 
               c.name as class_name, sy.name as year_name
        FROM students s
        JOIN enrollments e ON s.id = e.student_id AND e.school_year_id = (SELECT id FROM school_years WHERE is_active = 1)
        JOIN classes c ON e.class_id = c.id
        JOIN school_years sy ON e.school_year_id = sy.id
        WHERE s.id = ?
    """
    result = fetch_query(query, (student_id,))
    return result[0] if result else None
    # --- AJOUTER À LA FIN DE database/queries.py ---

def get_student_details_for_certificate(student_id):
    """Récupère les infos complètes d'un élève pour générer un certificat."""
    query = """
        SELECT s.first_name, s.last_name, s.matricule, s.dob, 
               c.name as class_name, sy.name as year_name
        FROM students s
        JOIN enrollments e ON s.id = e.student_id AND e.school_year_id = (SELECT id FROM school_years WHERE is_active = 1)
        JOIN classes c ON e.class_id = c.id
        JOIN school_years sy ON e.school_year_id = sy.id
        WHERE s.id = ?
    """
    result = fetch_query(query, (student_id,))
    return result[0] if result else None
    # --- AJOUTER À LA FIN DE database/queries.py ---

def get_payment_details(payment_id):
    """Récupère les détails d'un paiement spécifique pour générer le reçu."""
    query = """
        SELECT p.id, p.payment_date, p.amount_paid, p.method, p.status, 
               s.first_name, s.last_name, s.matricule,
               sf.name as fee_name
        FROM payments p
        JOIN students s ON p.student_id = s.id
        JOIN school_fees sf ON p.fee_id = sf.id
        WHERE p.id = ?
    """
    result = fetch_query(query, (payment_id,))
    return result[0] if result else None
    # --- AJOUTER À LA FIN DE database/queries.py ---

def get_student_for_card(student_id):
    """Récupère les infos d'un élève pour générer sa carte scolaire."""
    query = """
        SELECT s.first_name, s.last_name, s.matricule, s.photo_path, c.name as class_name
        FROM students s
        JOIN enrollments e ON s.id = e.student_id AND e.school_year_id = (SELECT id FROM school_years WHERE is_active = 1)
        JOIN classes c ON e.class_id = c.id
        WHERE s.id = ?
    """
    result = fetch_query(query, (student_id,))
    return result[0] if result else None
    # --- AJOUTER À LA FIN DE database/queries.py ---

def bulk_import_students(df):
    """Importe une liste d'élèves depuis un DataFrame Pandas (Excel/CSV)."""
    active_year = get_active_year_id()
    if not active_year:
        return 0, "Aucune année scolaire active."
        
    success_count = 0
    errors = []
    
    for index, row in df.iterrows():
        try:
            # On s'assure que les colonnes existent
            first_name = str(row.get('Prenom', '')).strip()
            last_name = str(row.get('Nom', '')).strip()
            
            if not first_name or not last_name or first_name == 'nan':
                continue
                
            gender = str(row.get('Sexe', 'M')).strip()
            dob = str(row.get('DateDeNaissance', '')).strip()
            phone = str(row.get('Telephone', '')).strip()
            address = str(row.get('Adresse', '')).strip()
            
            matricule = generate_matricule()
            
            query = """
                INSERT INTO students (matricule, first_name, last_name, dob, gender, address, phone, photo_path, school_year_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'default.png', ?)
            """
            execute_query(query, (matricule, first_name, last_name, dob, gender, address, phone, active_year))
            success_count += 1
        except Exception as e:
            errors.append(f"Ligne {index+2}: {e}")
            
    return success_count, "\n".join(errors)

def get_all_payments_for_export():
    """Récupère tous les paiements pour l'export Excel."""
    return get_all_payments() # On réutilise la fonction existante
    # --- AJOUTER À LA FIN DE database/queries.py ---

def close_active_year():
    """Clôture l'année active (la verrouille)."""
    active_year = get_active_year_id()
    if active_year:
        # On ferme l'année et on la désactive
        return execute_query("UPDATE school_years SET is_closed = 1, is_active = 0 WHERE id = ?", (active_year,))
    return False

def promote_students(class_mapping, new_year_id):
    """
    Inscrit les élèves dans leurs nouvelles classes pour la nouvelle année.
    class_mapping est un dictionnaire : {ancienne_classe_id: nouvelle_classe_id}
    """
    active_year = get_active_year_id()
    if not active_year:
        return 0
        
    # Récupérer tous les élèves acceptés de l'année qui se termine
    students = fetch_query("""
        SELECT student_id, class_id FROM enrollments 
        WHERE school_year_id = ? AND status = 'Accepté'
    """, (active_year,))
    
    promoted_count = 0
    for student in students:
        old_class_id = student['class_id']
        new_class_id = class_mapping.get(old_class_id)
        
        # Si l'admin a défini une classe suivante pour cette classe
        if new_class_id:
            # Vérifier si l'élève n'est pas déjà inscrit dans la nouvelle année
            existing = fetch_query("SELECT id FROM enrollments WHERE student_id=? AND school_year_id=?", 
                                   (student['student_id'], new_year_id))
            if not existing:
                execute_query("""
                    INSERT INTO enrollments (student_id, class_id, date, status, school_year_id)
                    VALUES (?, ?, DATE('now'), 'Accepté', ?)
                """, (student['student_id'], new_class_id, new_year_id))
                promoted_count += 1
                
    return promoted_count
    def create_enrollment(student_id, class_id):
    """Crée une demande d'inscription (Préinscription) pour l'année active."""
    active_year = get_active_year_id()
    existing = fetch_query("SELECT id FROM enrollments WHERE student_id = ? AND class_id = ? AND school_year_id = ?", 
                           (student_id, class_id, active_year))
    if existing:
        return None
    return execute_query("INSERT INTO enrollments (student_id, class_id, date, status, school_year_id) VALUES (?, ?, DATE('now'), 'En attente', ?)", 
                         (student_id, class_id, active_year))

def get_enrollments_by_status(status_filter=None):
    """Récupère les inscriptions. Si status_filter est None, récupère tout."""
    active_year = get_active_year_id()
    query = """
        SELECT e.id, s.matricule, s.first_name, s.last_name, c.name as class_name, e.date, e.status
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        JOIN classes c ON e.class_id = c.id
        WHERE e.school_year_id = ?
    """
    params = (active_year,)
    
    if status_filter:
        query += " AND e.status = ?"
        params = (active_year, status_filter)
        
    query += " ORDER BY e.date DESC"
    return fetch_query(query, params)

def update_enrollment_status(enrollment_id, new_status):
    """Met à jour le statut d'une inscription (Accepté ou Refusé)."""
    return execute_query("UPDATE enrollments SET status = ? WHERE id = ?", (new_status, enrollment_id))

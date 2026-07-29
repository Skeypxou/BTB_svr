# database/create_database.py
import bcrypt
from database.database import get_connection, DB_PATH

def create_tables():
    """Crée toutes les tables de la base de données si elles n'existent pas."""
    conn = get_connection()
    cursor = conn.cursor()

    print("Création des tables en cours...")

    # --- TABLES SYSTÈME ---
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS school_years (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        is_active BOOLEAN DEFAULT 0,
        is_closed BOOLEAN DEFAULT 0
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS school_settings (
        id INTEGER PRIMARY KEY CHECK (id = 1), -- Force une seule ligne de config
        name TEXT NOT NULL,
        logo_path TEXT,
        address TEXT,
        phone TEXT,
        email TEXT,
        website TEXT,
        director_name TEXT,
        active_year_id INTEGER,
        FOREIGN KEY (active_year_id) REFERENCES school_years (id)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )''')

    # Table des utilisateurs (le mot de passe est haché avec bcrypt)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role_id INTEGER NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        FOREIGN KEY (role_id) REFERENCES roles (id)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        module TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')

    # --- TABLES DE RÉFÉRENCE ACADEMIQUE ---
    cursor.execute('''CREATE TABLE IF NOT EXISTS levels (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS classes (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL, level_id INTEGER, capacity INTEGER, FOREIGN KEY (level_id) REFERENCES levels (id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS subjects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL, coefficient REAL DEFAULT 1, is_active BOOLEAN DEFAULT 1)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS evaluation_types (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)''')

    # --- TABLES ACTEURS ---
    cursor.execute('''CREATE TABLE IF NOT EXISTS parents (
        id INTEGER PRIMARY KEY AUTOINCREMENT, first_name TEXT, last_name TEXT, phone TEXT, email TEXT, address TEXT, profession TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT, matricule TEXT UNIQUE, first_name TEXT, last_name TEXT, phone TEXT, email TEXT, subject_id INTEGER, diploma TEXT, hire_date DATE, salary REAL,
        FOREIGN KEY (subject_id) REFERENCES subjects (id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS staff (
        id INTEGER PRIMARY KEY AUTOINCREMENT, first_name TEXT, last_name TEXT, role TEXT, phone TEXT, email TEXT, hire_date DATE, salary REAL
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT, matricule TEXT UNIQUE, first_name TEXT, last_name TEXT, dob DATE, gender TEXT, address TEXT, phone TEXT, photo_path TEXT, school_year_id INTEGER,
        FOREIGN KEY (school_year_id) REFERENCES school_years (id)
    )''')

    # Table de liaison Parent-Enfant (un parent peut avoir plusieurs enfants)
    cursor.execute('''CREATE TABLE IF NOT EXISTS student_parents (
        id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, parent_id INTEGER, relation TEXT,
        FOREIGN KEY (student_id) REFERENCES students (id), FOREIGN KEY (parent_id) REFERENCES parents (id)
    )''')

    # --- TABLES OPÉRATIONNELLES ---
    cursor.execute('''CREATE TABLE IF NOT EXISTS school_fees (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, amount REAL, school_year_id INTEGER,
        FOREIGN KEY (school_year_id) REFERENCES school_years (id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, class_id INTEGER, date DATE, status TEXT, school_year_id INTEGER,
        FOREIGN KEY (student_id) REFERENCES students (id), FOREIGN KEY (class_id) REFERENCES classes (id), FOREIGN KEY (school_year_id) REFERENCES school_years (id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS grades (
        id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, subject_id INTEGER, evaluation_type_id INTEGER, score REAL, max_score REAL, trimester INTEGER, school_year_id INTEGER,
        FOREIGN KEY (student_id) REFERENCES students (id), FOREIGN KEY (subject_id) REFERENCES subjects (id), FOREIGN KEY (evaluation_type_id) REFERENCES evaluation_types (id), FOREIGN KEY (school_year_id) REFERENCES school_years (id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, date DATE, status TEXT, is_justified BOOLEAN, reason TEXT, school_year_id INTEGER,
        FOREIGN KEY (student_id) REFERENCES students (id), FOREIGN KEY (school_year_id) REFERENCES school_years (id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, class_id INTEGER, subject_id INTEGER, date DATE, school_year_id INTEGER,
        FOREIGN KEY (class_id) REFERENCES classes (id), FOREIGN KEY (subject_id) REFERENCES subjects (id), FOREIGN KEY (school_year_id) REFERENCES school_years (id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT, class_id INTEGER, teacher_id INTEGER, subject_id INTEGER, day_of_week TEXT, start_time TIME, end_time TIME, room TEXT, school_year_id INTEGER,
        FOREIGN KEY (class_id) REFERENCES classes (id), FOREIGN KEY (teacher_id) REFERENCES teachers (id), FOREIGN KEY (subject_id) REFERENCES subjects (id), FOREIGN KEY (school_year_id) REFERENCES school_years (id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, fee_id INTEGER, amount_paid REAL, payment_date DATE, method TEXT, status TEXT, school_year_id INTEGER,
        FOREIGN KEY (student_id) REFERENCES students (id), FOREIGN KEY (fee_id) REFERENCES school_fees (id), FOREIGN KEY (school_year_id) REFERENCES school_years (id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, doc_type TEXT, file_path TEXT, upload_date DATE,
        FOREIGN KEY (student_id) REFERENCES students (id)
    )''')

    conn.commit()
    conn.close()
    print("✅ Toutes les tables ont été créées avec succès !")

def seed_default_data():
    """Insère les données de base (Année, Rôles, Utilisateur Admin, Réglages école)."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Créer une année scolaire par défaut et l'activer
    cursor.execute("INSERT OR IGNORE INTO school_years (name, is_active) VALUES (?, ?)", ("2024-2025", 1))
    
    # Récupérer l'ID de l'année active
    cursor.execute("SELECT id FROM school_years WHERE is_active = 1")
    active_year_id = cursor.fetchone()[0]

    # 2. Créer les paramètres de l'école par défaut
    cursor.execute('''
    INSERT OR IGNORE INTO school_settings (id, name, active_year_id) 
    VALUES (1, 'Mon École Privée', ?)
    ''', (active_year_id,))

    # 3. Créer les rôles par défaut
    roles = ['Administrateur', 'Directeur', 'Comptable', 'Secrétaire', 'Enseignant', 'Parent']
    for role in roles:
        cursor.execute("INSERT OR IGNORE INTO roles (name) VALUES (?)", (role,))
    
    # 4. Créer le compte Super Administrateur
    # Mot de passe par défaut : "admin123" (haché avec bcrypt pour la sécurité)
    default_password = "admin123"
    password_hash = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    cursor.execute("SELECT id FROM roles WHERE name = 'Administrateur'")
    admin_role_id = cursor.fetchone()[0]

    cursor.execute('''
    INSERT OR IGNORE INTO users (username, password_hash, role_id, is_active) 
    VALUES (?, ?, ?, 1)
    ''', ("admin", password_hash, admin_role_id))

    conn.commit()
    conn.close()
    print("✅ Données par défaut insérées avec succès !")
    print("➡️  Identifiant de connexion par défaut : admin")
    print("➡️  Mot de passe par défaut : admin123")

if __name__ == "__main__":
    # Ce bloc s'exécute uniquement si on lance ce fichier directement
    # (python database/create_database.py)
    create_tables()
    seed_default_data()

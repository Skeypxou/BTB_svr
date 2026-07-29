# app.py
import streamlit as st
import os
from pathlib import Path
from utils.auth import verify_user
from database.create_database import create_tables, seed_default_data

# --- 1. INITIALISATION DE LA BASE DE DONNÉES ---
# On s'assure que la base existe avant de lancer l'application
if not os.path.exists("database/school.db"):
    create_tables()
    seed_default_data()

# --- 2. CONFIGURATION DE LA PAGE STREAMLIT ---
st.set_page_config(
    page_title="LNS SCHOOL PRO ENTERPRISE",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 3. INJECTION DU CSS PREMIUM ---
def load_css():
    css_path = Path("assets/style.css")
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# --- 4. GESTION DE L'ÉTAT DE CONNEXION (SESSION STATE) ---
# Streamlit recharge la page à chaque clic. On utilise session_state pour garder l'utilisateur connecté.
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

# --- 5. PAGE DE CONNEXION ---
def login_page():
    st.markdown("<h1 style='text-align: center; color: #1e293b;'>🏫 LNS SCHOOL PRO ENTERPRISE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>Veuillez vous connecter pour accéder au système</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Identifiant")
            password = st.text_input("Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter", use_container_width=True)
            
            if submit:
                user = verify_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_info = user
                    st.rerun() # Recharge la page pour afficher le dashboard
                else:
                    st.error("Identifiant ou mot de passe incorrect.")

# --- 6. BARRE DE NAVIGATION (SIDEBAR) ---
def main_sidebar():
    user_role = st.session_state.user_info['role_name']
    
    with st.sidebar:
        st.markdown("### 🏫 LNS SCHOOL PRO")
        st.caption(f"Connecté en tant que : **{user_role}**")
        st.divider()
        
        # Menu de navigation de base
        menu_options = ["📊 Tableau de Bord"]
        
        # 1. Élèves, Parents, Enseignants
        if user_role in ['Administrateur', 'Secrétaire', 'Directeur']:
            menu_options.append("👥 Élèves")
            menu_options.append("👨‍👩‍👦 Parents")
            menu_options.append("👨‍🏫 Enseignants")
        if user_role in ['Administrateur', 'Secrétaire', 'Directeur']:
            menu_options.append("👥 Élèves")
            menu_options.append("👨‍👩‍👦 Parents")
            menu_options.append("👨‍🏫 Enseignants")
            menu_options.append("📋 Inscriptions") # <-- AJOUTE CECI
            
        # 2. Années Scolaires et Paramètres Académiques
        if user_role in ['Administrateur', 'Directeur']:
            menu_options.append("📅 Années Scolaires")
            menu_options.append("⚙️ Paramètres Académiques")   
            
        # 3. Notes et Absences
        if user_role in ['Administrateur', 'Directeur', 'Secrétaire', 'Enseignant']:
            menu_options.append("📝 Notes & Évaluations")
            menu_options.append("🚪 Absences & Retards")
            
        # 4. Finances
        if user_role in ['Administrateur', 'Directeur', 'Comptable']:
            menu_options.append("💰 Finances")
            
        # Options globales
        menu_options.append("⚙️ Paramètres")
        menu_options.append("🚪 Déconnexion")
        
        choice = st.radio("Navigation", menu_options)
        
        if choice == "🚪 Déconnexion":
            st.session_state.logged_in = False
            st.session_state.user_info = None
            st.rerun()
            
        return choice

# --- 7. BOUCLE PRINCIPALE (LE ROUTEUR) ---
# Si l'utilisateur n'est PAS connecté, on affiche la page de connexion
if not st.session_state.logged_in:
    login_page()
# Sinon, on affiche le menu et la page demandée
else:
    choice = main_sidebar()
    
    # Routage vers les modules en fonction du choix (choice) dans la sidebar
    if choice == "📊 Tableau de Bord":
        from modules.dashboard import show_dashboard
        show_dashboard()
        
    elif choice == "👥 Élèves":
        from modules.students import show_students
        show_students()
        
    elif choice == "👨‍👩‍👦 Parents":
        from modules.parents import show_parents
        show_parents()
        
    elif choice == "👨‍🏫 Enseignants":
        from modules.teachers import show_teachers
        show_teachers()
    elif choice == "📋 Inscriptions":
        from modules.enrollments import show_enrollments
        show_enrollments()
        
    elif choice == "📝 Notes & Évaluations":
        from modules.grades import show_grades
        show_grades()
        
    elif choice == "🚪 Absences & Retards":
        from modules.attendance import show_attendance
        show_attendance()
        
    elif choice == "💰 Finances":
        from modules.finances import show_finances
        show_finances()
        
    elif choice == "📅 Années Scolaires":
        from modules.school_years import show_school_years
        show_school_years()
        
    elif choice == "⚙️ Paramètres Académiques":
        from modules.academic_settings import show_academic_settings
        show_academic_settings()
        
    elif choice == "⚙️ Paramètres":
        st.info("Ici se trouveront les paramètres de l'école et du système.")

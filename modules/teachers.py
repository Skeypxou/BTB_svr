# modules/teachers.py
import streamlit as st
import pandas as pd
from database.queries import get_all_teachers, get_all_subjects, add_teacher, delete_teacher

def show_teachers():
    st.markdown("<h1 style='color: #1e293b;'>👨‍🏫 Gestion des Enseignants</h1>", unsafe_allow_html=True)
    st.markdown("Gérez le corps professoral, les matières et les informations contractuelles.")
    st.divider()

    # --- 1. BARRE DE RECHERCHE ---
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("🔎 Rechercher un enseignant (Nom, Matricule)...", "")
    with col2:
        if st.button("➕ Ajouter un enseignant", use_container_width=True):
            st.session_state.show_add_teacher_form = not st.session_state.get('show_add_teacher_form', False)

    # --- 2. TABLEAU DES ENSEIGNANTS ---
    teachers = get_all_teachers(search_term)
    
    if teachers:
        df = pd.DataFrame(teachers)
        # On renomme les colonnes pour l'affichage
        df = df.rename(columns={
            'matricule': 'Matricule', 'first_name': 'Prénom', 'last_name': 'Nom',
            'phone': 'Téléphone', 'email': 'Email', 'subject_name': 'Matière',
            'diploma': 'Diplôme', 'hire_date': 'Date d\'embauche', 'salary': 'Salaire'
        })
        
        # Affichage du tableau interactif
        st.dataframe(
            df[['Matricule', 'Prénom', 'Nom', 'Téléphone', 'Email', 'Matière', 'Diplôme', 'Date d\'embauche', 'Salaire']], 
            use_container_width=True,
            hide_index=True
        )
        
        # --- 3. SUPPRESSION D'UN ENSEIGNANT ---
        st.divider()
        st.markdown("#### 🗑️ Supprimer un enseignant")
        col_del1, col_del2 = st.columns([3, 1])
        with col_del1:
            teacher_options = {f"{t['matricule']} - {t['last_name']} {t['first_name']}": t['id'] for t in teachers}
            selected_teacher = st.selectbox("Sélectionner un enseignant à supprimer", list(teacher_options.keys()))
        with col_del2:
            st.write("") # Espace vide pour aligner
            st.write("")
            if st.button("Supprimer définitivement", type="primary"):
                if selected_teacher:
                    delete_teacher(teacher_options[selected_teacher])
                    st.success("✅ Enseignant supprimé avec succès !")
                    st.rerun()
    else:
        st.info("Aucun enseignant trouvé. Cliquez sur 'Ajouter un enseignant' pour commencer.")

    # --- 4. FORMULAIRE D'AJOUT ---
    if st.session_state.get('show_add_teacher_form', False):
        st.divider()
        st.markdown("### ➕ Ajouter un nouvel enseignant")
        
        with st.form("add_teacher_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("Prénom *")
                last_name = st.text_input("Nom *")
                phone = st.text_input("Téléphone *")
                email = st.text_input("Email")
                
            with col2:
                # Menu déroulant pour les matières
                subjects = get_all_subjects()
                subject_options = {s['name']: s['id'] for s in subjects} if subjects else {}
                selected_subject = st.selectbox("Matière principale *", list(subject_options.keys()) if subject_options else ["Aucune matière disponible"])
                
                diploma = st.text_input("Diplôme *")
                hire_date = st.date_input("Date d'embauche *")
                salary = st.number_input("Salaire mensuel (Devise)", min_value=0.0, step=100.0)

            submit = st.form_submit_button("Enregistrer l'enseignant", use_container_width=True)
            
            if submit:
                if not first_name or not last_name or not phone or not diploma:
                    st.error("Les champs avec * sont obligatoires.")
                else:
                    subject_id = subject_options.get(selected_subject)
                    
                    # Appel de la fonction d'ajout
                    teacher_id = add_teacher(first_name, last_name, phone, email, subject_id, diploma, hire_date, salary)
                    
                    if teacher_id:
                        st.success(f"✅ Enseignant '{last_name} {first_name}' ajouté avec succès !")
                        st.session_state.show_add_teacher_form = False # Ferme le formulaire
                        st.rerun()
                    else:
                        st.error("Une erreur est survenue lors de l'enregistrement.")

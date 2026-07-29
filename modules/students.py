# modules/students.py
import streamlit as st
import pandas as pd
from database.queries import get_all_students, get_all_classes, get_all_parents, add_student, delete_student
from pathlib import Path

def show_students():
    st.markdown("<h1 style='color: #1e293b;'>👥 Gestion des Élèves</h1>", unsafe_allow_html=True)
    st.markdown("Ajoutez, modifiez, recherchez et gérez les dossiers des élèves.")
    st.divider()

    # --- 1. BARRE DE RECHERCHE ---
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("🔎 Rechercher un élève (Nom, Prénom, Matricule)...", "")
    with col2:
        if st.button("➕ Ajouter un élève", use_container_width=True):
            st.session_state.show_add_form = True

    # --- 2. TABLEAU DES ÉLÈVES ---
    students = get_all_students(search_term)
    
    if students:
        df = pd.DataFrame(students)
        # On renomme les colonnes pour l'affichage
        df = df.rename(columns={
            'matricule': 'Matricule', 'first_name': 'Prénom', 'last_name': 'Nom',
            'gender': 'Sexe', 'dob': 'Date de Naissance', 'class_name': 'Classe'
        })
        
        # Affichage du tableau interactif
        st.dataframe(
            df[['Matricule', 'Prénom', 'Nom', 'Sexe', 'Date de Naissance', 'Classe']], 
            use_container_width=True,
            hide_index=True
        )
        
        # --- 3. SUPPRESSION D'UN ÉLÈVE ---
        st.divider()
        st.markdown("#### 🗑️ Supprimer un élève")
        col_del1, col_del2 = st.columns([3, 1])
        with col_del1:
            # Création d'un dictionnaire pour le menu déroulant : "Matricule - Nom Prénom" -> id
            student_options = {f"{s['matricule']} - {s['last_name']} {s['first_name']}": s['id'] for s in students}
            selected_student = st.selectbox("Sélectionner un élève à supprimer", list(student_options.keys()))
        with col_del2:
            st.write("") # Espace vide pour aligner
            st.write("")
            if st.button("Supprimer définitivement", type="primary"):
                if selected_student:
                    delete_student(student_options[selected_student])
                    st.success("✅ Élève supprimé avec succès !")
                    st.rerun()
    else:
        st.info("Aucun élève trouvé. Cliquez sur 'Ajouter un élève' pour commencer.")

    # --- 4. FORMULAIRE D'AJOUT (Apparaît si on clique sur le bouton) ---
    if st.session_state.get('show_add_form', False):
        st.divider()
        st.markdown("### ➕ Inscription d'un nouvel élève")
        
        with st.form("add_student_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                first_name = st.text_input("Prénom *")
                last_name = st.text_input("Nom *")
                dob = st.date_input("Date de naissance *")
                
            with col2:
                gender = st.selectbox("Sexe *", ["Masculin", "Féminin"])
                phone = st.text_input("Téléphone")
                address = st.text_input("Adresse")
                
            with col3:
                # Menus déroulants pour les classes et les parents
                classes = get_all_classes()
                class_options = {c['name']: c['id'] for c in classes} if classes else {}
                selected_class = st.selectbox("Classe *", list(class_options.keys()) if class_options else ["Aucune classe disponible"])
                
                parents = get_all_parents()
                parent_options = {p['full_name']: p['id'] for p in parents} if parents else {}
                selected_parent = st.selectbox("Parent / Tuteur", list(parent_options.keys()) if parent_options else ["Aucun parent disponible"])
                
                # Upload de la photo
                photo = st.file_uploader("Photo de l'élève", type=['png', 'jpg', 'jpeg'])

            submit = st.form_submit_button("Enregistrer l'élève", use_container_width=True)
            
            if submit:
                if not first_name or not last_name:
                    st.error("Le prénom et le nom sont obligatoires.")
                else:
                    # Gestion de la photo
                    photo_filename = "default.png"
                    if photo:
                        photo_filename = f"{first_name}_{last_name}.jpg"
                        # Sauvegarde physique du fichier dans le dossier photos/
                        with open(Path("photos") / photo_filename, "wb") as f:
                            f.write(photo.getbuffer())
                    
                    # Récupération des IDs
                    class_id = class_options.get(selected_class)
                    parent_id = parent_options.get(selected_parent)
                    
                    # Appel de la fonction d'ajout
                    matricule = add_student(first_name, last_name, dob, gender, address, phone, photo_filename, class_id, parent_id)
                    
                    st.success(f"✅ Élève ajouté avec succès ! Matricule généré : {matricule}")
                    st.session_state.show_add_form = False # Ferme le formulaire
                    st.rerun()

# modules/enrollments.py
import streamlit as st
import pandas as pd
from database.queries import (
    get_enrollments_by_status, update_enrollment_status,
    get_all_students, get_all_classes, create_enrollment
)

def show_enrollments():
    st.markdown("<h1 style='color: #1e293b;'>📋 Inscriptions & Admissions</h1>", unsafe_allow_html=True)
    st.markdown("Gérez les préinscriptions et validez les admissions des élèves.")
    st.divider()

    tab1, tab2, tab3 = st.tabs(["⏳ En attente", "✅ Acceptés", "❌ Refusés"])

    # --- ONGLET 1 : EN ATTENTE ---
    with tab1:
        st.markdown("#### Nouvelles demandes d'inscription")
        pending = get_enrollments_by_status("En attente")
        
        if pending:
            df = pd.DataFrame(pending)
            df = df.rename(columns={
                'matricule': 'Matricule', 'first_name': 'Prénom', 'last_name': 'Nom',
                'class_name': 'Classe Demandée', 'date': 'Date de demande'
            })
            st.dataframe(df[['Matricule', 'Prénom', 'Nom', 'Classe Demandée', 'Date de demande']], use_container_width=True, hide_index=True)
            
            st.divider()
            st.markdown("#### ⚖️ Valider ou Refuser une demande")
            
            # Menu déroulant pour choisir l'élève
            enrollment_options = {f"{p['matricule']} - {p['last_name']} {p['first_name']} ({p['class_name']})": p['id'] for p in pending}
            selected_enrollment = st.selectbox("Sélectionner un dossier à traiter", list(enrollment_options.keys()))
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Accepter l'admission", use_container_width=True):
                    update_enrollment_status(enrollment_options[selected_enrollment], "Accepté")
                    st.success("Inscription acceptée ! L'élève est désormais officiellement admis.")
                    st.rerun()
            with col2:
                if st.button("❌ Refuser l'admission", use_container_width=True, type="primary"):
                    update_enrollment_status(enrollment_options[selected_enrollment], "Refusé")
                    st.warning("Inscription refusée.")
                    st.rerun()
        else:
            st.info("Aucune demande en attente de traitement.")

    # --- ONGLET 2 : ACCEPTÉS ---
    with tab2:
        st.markdown("#### Élèves officiellement admis")
        accepted = get_enrollments_by_status("Accepté")
        if accepted:
            df = pd.DataFrame(accepted)
            df = df.rename(columns={
                'matricule': 'Matricule', 'first_name': 'Prénom', 'last_name': 'Nom',
                'class_name': 'Classe Assignée', 'date': "Date d'admission"
            })
            st.dataframe(df[['Matricule', 'Prénom', 'Nom', 'Classe Assignée', "Date d'admission"]], use_container_width=True, hide_index=True)
        else:
            st.info("Aucune inscription acceptée pour le moment.")

    # --- ONGLET 3 : REFUSÉS ---
    with tab3:
        st.markdown("#### Demandes refusées")
        rejected = get_enrollments_by_status("Refusé")
        if rejected:
            df = pd.DataFrame(rejected)
            df = df.rename(columns={
                'matricule': 'Matricule', 'first_name': 'Prénom', 'last_name': 'Nom',
                'class_name': 'Classe Demandée', 'date': 'Date de traitement'
            })
            st.dataframe(df[['Matricule', 'Prénom', 'Nom', 'Classe Demandée', 'Date de traitement']], use_container_width=True, hide_index=True)
        else:
            st.info("Aucune demande refusée.")

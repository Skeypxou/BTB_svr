# modules/attendance.py
import streamlit as st
import pandas as pd
from database.queries import get_all_classes, get_students_by_class, save_attendance, get_attendance_by_student

def show_attendance():
    st.markdown("<h1 style='color: #1e293b;'>🚪 Absences et Retards</h1>", unsafe_allow_html=True)
    st.markdown("Gérez l'appel, les retards et les justificatifs.")
    st.divider()

    tab1, tab2 = st.tabs(["📝 Faire l'appel", "📊 Historique & Rapports"])

    # --- ONGLET 1 : FAIRE L'APPEL ---
    with tab1:
        st.markdown("#### Configuration de l'appel")
        col1, col2 = st.columns(2)
        
        with col1:
            classes = get_all_classes()
            class_options = {c['name']: c['id'] for c in classes} if classes else {}
            selected_class = st.selectbox("Classe", list(class_options.keys()) if class_options else ["Aucune"], key="att_class")
            
        with col2:
            # Par défaut, la date du jour
            att_date = st.date_input("Date de l'appel", key="att_date")

        st.divider()
        
        if selected_class != "Aucune":
            students = get_students_by_class(class_options[selected_class])
            
            if students:
                st.markdown(f"#### Feuille d'appel : {selected_class}")
                
                with st.form("attendance_form"):
                    # Pour chaque élève, on propose un menu déroulant (Présent, Absent, Retard)
                    attendance_data = {}
                    for student in students:
                        col_s1, col_s2, col_s3 = st.columns([2, 1, 3])
                        with col_s1:
                            st.write(f"**{student['last_name']} {student['first_name']}**")
                        with col_s2:
                            status = st.selectbox("Statut", ["Présent", "Absent", "Retard"], key=f"status_{student['id']}", label_visibility="collapsed")
                        with col_s3:
                            if status != "Présent":
                                reason = st.text_input("Motif / Justification", key=f"reason_{student['id']}", placeholder="Ex: Maladie, Retard bus...", label_visibility="collapsed")
                            else:
                                reason = ""
                        
                        attendance_data[student['id']] = {'status': status, 'reason': reason}
                    
                    submit = st.form_submit_button("💾 Enregistrer l'appel", use_container_width=True)
                    
                    if submit:
                        saved_count = 0
                        for student_id, data in attendance_data.items():
                            if data['status'] != "Présent":
                                # Si un motif contient "justifié" ou "certificat", on peut l'automatiser, ici on laisse False par défaut
                                save_attendance(student_id, str(att_date), data['status'], False, data['reason'])
                                saved_count += 1
                        st.success(f"✅ Appel enregistré ! ({saved_count} absence(s)/retard(s) signalé(s))")
            else:
                st.info("Aucun élève inscrit dans cette classe.")

    # --- ONGLET 2 : HISTORIQUE ---
    with tab2:
        st.markdown("#### Consulter l'historique d'un élève")
        
        # Pour simplifier, on demande l'ID ou on pourrait faire une recherche. 
        # Ici on va chercher tous les élèves pour faire un menu déroulant.
        from database.queries import get_all_students
        all_students = get_all_students()
        
        if all_students:
            student_options = {f"{s['matricule']} - {s['last_name']} {s['first_name']}": s['id'] for s in all_students}
            selected_student = st.selectbox("Sélectionner un élève", list(student_options.keys()), key="hist_student")
            
            if selected_student:
                student_id = student_options[selected_student]
                history = get_attendance_by_student(student_id)
                
                if history:
                    df = pd.DataFrame(history)
                    df = df.rename(columns={
                        'date': 'Date', 'status': 'Statut', 
                        'is_justified': 'Justifié', 'reason': 'Motif'
                    })
                    # Convertir le booléen en texte lisible
                    df['Justifié'] = df['Justifié'].apply(lambda x: 'Oui' if x == 1 else 'Non')
                    st.dataframe(df[['Date', 'Statut', 'Justifié', 'Motif']], use_container_width=True, hide_index=True)
                else:
                    st.success("✅ Cet élève n'a aucun retard ni absence enregistré.")
        else:
            st.info("Aucun élève dans le système.")

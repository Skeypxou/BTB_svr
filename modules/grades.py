# modules/grades.py
import streamlit as st
import pandas as pd
from database.queries import (
    get_all_classes, get_all_subjects, get_all_evaluation_types,
    get_students_by_class, save_grade, calculate_class_rankings
)

def show_grades():
    st.markdown("<h1 style='color: #1e293b;'>📝 Gestion des Notes</h1>", unsafe_allow_html=True)
    st.markdown("Saisissez les évaluations et consultez les classements automatiquement.")
    st.divider()

    tab1, tab2 = st.tabs(["✍️ Saisie des Notes", "🏆 Classement & Moyennes"])

    # --- ONGLET 1 : SAISIE ---
    with tab1:
        st.markdown("#### Configuration de l'évaluation")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            classes = get_all_classes()
            class_options = {c['name']: c['id'] for c in classes} if classes else {}
            selected_class = st.selectbox("Classe", list(class_options.keys()) if class_options else ["Aucune"], key="grade_class")
            
        with col2:
            subjects = get_all_subjects()
            subj_options = {s['name']: s['id'] for s in subjects} if subjects else {}
            selected_subj = st.selectbox("Matière", list(subj_options.keys()) if subj_options else ["Aucune"], key="grade_subj")
            
        with col3:
            evals = get_all_evaluation_types()
            eval_options = {e['name']: e['id'] for e in evals} if evals else {}
            selected_eval = st.selectbox("Type d'évaluation", list(eval_options.keys()) if evals else ["Aucune"], key="grade_eval")
            
        with col4:
            trimester = st.selectbox("Trimestre", ["Trimestre 1", "Trimestre 2", "Trimestre 3"], key="grade_trim")
            max_score = st.number_input("Barème (ex: 20)", min_value=1.0, value=20.0, step=1.0, key="grade_max")

        st.divider()
        
        if selected_class != "Aucune" and selected_subj != "Aucune":
            students = get_students_by_class(class_options[selected_class])
            
            if students:
                st.markdown(f"#### Saisie pour : {selected_class} - {selected_subj}")
                
                with st.form("grades_form"):
                    # Création d'un champ de saisie pour chaque élève
                    scores = {}
                    for student in students:
                        scores[student['id']] = st.number_input(
                            f"{student['last_name']} {student['first_name']}", 
                            min_value=0.0, max_value=max_score, step=0.5, key=f"score_{student['id']}"
                        )
                    
                    submit = st.form_submit_button("💾 Enregistrer les notes", use_container_width=True)
                    
                    if submit:
                        trim_num = int(trimester.split()[-1]) # Convertit "Trimestre 1" en 1
                        for student_id, score in scores.items():
                            save_grade(
                                student_id, 
                                subj_options[selected_subj], 
                                eval_options[selected_eval], 
                                score, max_score, trim_num
                            )
                        st.success("✅ Notes enregistrées avec succès !")
            else:
                st.info("Aucun élève inscrit dans cette classe.")
                
    # --- ONGLET 2 : CLASSEMENT ---
    with tab2:
        st.markdown("#### Calcul du classement général")
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            classes = get_all_classes()
            class_options = {c['name']: c['id'] for c in classes} if classes else {}
            selected_class_rank = st.selectbox("Classe", list(class_options.keys()) if class_options else ["Aucune"], key="rank_class")
            
        with col_c2:
            trimester_rank = st.selectbox("Trimestre", ["Trimestre 1", "Trimestre 2", "Trimestre 3"], key="rank_trim")
            st.write("") # Alignement
            
        if selected_class_rank != "Aucune":
            trim_num = int(trimester_rank.split()[-1])
            rankings = calculate_class_rankings(class_options[selected_class_rank], trim_num)
            
            if rankings:
                df = pd.DataFrame(rankings)
                df = df.rename(columns={'rank': 'Rang', 'matricule': 'Matricule', 'name': 'Nom de l'élève', 'average': 'Moyenne (/20)'})
                
                # Mettre en surbrillance le premier
                st.dataframe(
                    df[['Rang', 'Matricule', 'Nom de l'élève', 'Moyenne (/20)']], 
                    use_container_width=True, 
                    hide_index=True
                )
            else:
                st.info("Aucune note n'a encore été saisie pour cette classe et ce trimestre.")

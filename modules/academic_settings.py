# modules/academic_settings.py
import streamlit as st
import pandas as pd
from database.queries import (
    add_subject, get_all_subjects, delete_subject,
    add_level, get_all_levels, delete_level,
    add_class, get_all_classes_with_levels, delete_class,
    add_evaluation_type, get_all_evaluation_types, delete_evaluation_type
)

def show_academic_settings():
    st.markdown("<h1 style='color: #1e293b;'>⚙️ Paramètres Académiques</h1>", unsafe_allow_html=True)
    st.markdown("Configurez dynamiquement les matières, niveaux, classes et évaluations.")
    st.divider()

    # Création des onglets pour une interface propre
    tab1, tab2, tab3, tab4 = st.tabs(["📚 Matières", "🎓 Niveaux", "🏫 Classes", "📝 Évaluations"])

    # --- ONGLET 1 : MATIERES ---
    with tab1:
        st.markdown("#### Ajouter une matière")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            subj_name = st.text_input("Nom de la matière", key="subj_name")
        with col2:
            subj_coef = st.number_input("Coefficient", min_value=1.0, step=0.5, key="subj_coef")
        with col3:
            st.write("")
            st.write("")
            if st.button("Ajouter", use_container_width=True, key="add_subj"):
                if subj_name:
                    add_subject(subj_name, subj_coef)
                    st.success(f"Matière '{subj_name}' ajoutée !")
                    st.rerun()
                else:
                    st.error("Le nom est obligatoire.")

        st.markdown("#### Liste des matières")
        subjects = get_all_subjects()
        if subjects:
            df = pd.DataFrame(subjects)
            df = df.rename(columns={'name': 'Matière', 'coefficient': 'Coefficient', 'is_active': 'Active'})
            df['Active'] = df['Active'].apply(lambda x: 'Oui' if x == 1 else 'Non')
            st.dataframe(df[['Matière', 'Coefficient', 'Active']], use_container_width=True, hide_index=True)
            
            subj_to_del = st.selectbox("Supprimer une matière", [s['name'] for s in subjects], key="del_subj")
            if st.button("Supprimer", type="primary", key="del_subj_btn"):
                # On trouve l'ID à partir du nom sélectionné
                id_to_del = [s['id'] for s in subjects if s['name'] == subj_to_del][0]
                delete_subject(id_to_del)
                st.success(f"Matière '{subj_to_del}' supprimée !")
                st.rerun()
        else:
            st.info("Aucune matière enregistrée.")

    # --- ONGLET 2 : NIVEAUX ---
    with tab2:
        st.markdown("#### Ajouter un niveau")
        col1, col2 = st.columns([3, 1])
        with col1:
            lvl_name = st.text_input("Nom du niveau (ex: Primaire)", key="lvl_name")
        with col2:
            st.write("")
            st.write("")
            if st.button("Ajouter", use_container_width=True, key="add_lvl"):
                if lvl_name:
                    add_level(lvl_name)
                    st.success(f"Niveau '{lvl_name}' ajouté !")
                    st.rerun()
                    
        st.markdown("#### Liste des niveaux")
        levels = get_all_levels()
        if levels:
            df = pd.DataFrame(levels)
            st.dataframe(df[['name']], use_container_width=True, hide_index=True)
            
            lvl_to_del = st.selectbox("Supprimer un niveau", [l['name'] for l in levels], key="del_lvl")
            if st.button("Supprimer", type="primary", key="del_lvl_btn"):
                id_to_del = [l['id'] for l in levels if l['name'] == lvl_to_del][0]
                delete_level(id_to_del)
                st.rerun()
        else:
            st.info("Aucun niveau enregistré.")

    # --- ONGLET 3 : CLASSES ---
    with tab3:
        st.markdown("#### Ajouter une classe")
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        with col1:
            cls_name = st.text_input("Nom de la classe (ex: 1AP-A)", key="cls_name")
        with col2:
            levels = get_all_levels()
            if levels:
                lvl_options = {l['name']: l['id'] for l in levels}
                selected_lvl = st.selectbox("Niveau associé", list(lvl_options.keys()), key="cls_lvl")
            else:
                selected_lvl = None
                st.warning("Veuillez d'abord créer des niveaux.")
        with col3:
            cls_cap = st.number_input("Capacité", min_value=1, step=1, key="cls_cap")
        with col4:
            st.write("")
            st.write("")
            if st.button("Ajouter", use_container_width=True, key="add_cls"):
                if cls_name and selected_lvl:
                    add_class(cls_name, lvl_options[selected_lvl], cls_cap)
                    st.success(f"Classe '{cls_name}' ajoutée !")
                    st.rerun()
                    
        st.markdown("#### Liste des classes")
        classes = get_all_classes_with_levels()
        if classes:
            df = pd.DataFrame(classes)
            df = df.rename(columns={'name': 'Classe', 'level_name': 'Niveau', 'capacity': 'Capacité'})
            st.dataframe(df[['Classe', 'Niveau', 'Capacité']], use_container_width=True, hide_index=True)
            
            cls_to_del = st.selectbox("Supprimer une classe", [c['name'] for c in classes], key="del_cls")
            if st.button("Supprimer", type="primary", key="del_cls_btn"):
                id_to_del = [c['id'] for c in classes if c['name'] == cls_to_del][0]
                delete_class(id_to_del)
                st.rerun()
        else:
            st.info("Aucune classe enregistrée.")

    # --- ONGLET 4 : TYPES D'EVALUATION ---
    with tab4:
        st.markdown("#### Ajouter un type d'évaluation")
        col1, col2 = st.columns([3, 1])
        with col1:
            eval_name = st.text_input("Nom (ex: Devoir, Contrôle, TP)", key="eval_name")
        with col2:
            st.write("")
            st.write("")
            if st.button("Ajouter", use_container_width=True, key="add_eval"):
                if eval_name:
                    add_evaluation_type(eval_name)
                    st.success(f"Type '{eval_name}' ajouté !")
                    st.rerun()
                    
        st.markdown("#### Liste des types d'évaluation")
        evals = get_all_evaluation_types()
        if evals:
            df = pd.DataFrame(evals)
            st.dataframe(df[['name']], use_container_width=True, hide_index=True)
            
            eval_to_del = st.selectbox("Supprimer un type", [e['name'] for e in evals], key="del_eval")
            if st.button("Supprimer", type="primary", key="del_eval_btn"):
                id_to_del = [e['id'] for e in evals if e['name'] == eval_to_del][0]
                delete_evaluation_type(id_to_del)
                st.rerun()
        else:
            st.info("Aucun type d'évaluation enregistré.")

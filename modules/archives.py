# modules/archives.py
import streamlit as st
from database.queries import get_active_school_year, get_all_school_years, get_all_classes, set_active_school_year, close_active_year, promote_students

def show_archives():
    st.markdown("<h1 style='color: #1e293b;'>🗄️ Archivage & Promotion</h1>", unsafe_allow_html=True)
    st.markdown("Clôturez l'année en cours et faites passer les élèves dans la classe supérieure.")
    st.divider()

    active_year = get_active_school_year()
    
    if not active_year:
        st.warning("⚠️ Aucune année scolaire n'est active ! Veuillez en activer une dans le module 'Années Scolaires'.")
        return

    st.markdown(f"### Année en cours : **{active_year['name']}**")
    st.warning("⚠️ ATTENTION : Cette action va verrouiller définitivement l'année en cours. Assurez-vous d'avoir généré tous les bulletins et fait une sauvegarde complète avant de continuer.")
    
    # Étape 1 : Choisir l'année suivante
    st.divider()
    st.markdown("#### 1. Sélectionner l'année de destination")
    all_years = get_all_school_years()
    # On filtre pour ne pas retomber sur l'année active
    inactive_years = [y for y in all_years if not y['is_active'] and not y['is_closed']]
    
    if not inactive_years:
        st.info("Veuillez d'abord créer une nouvelle année scolaire (ex: 2025-2026) dans le module 'Années Scolaires'.")
        return
        
    year_options = {y['name']: y['id'] for y in inactive_years}
    selected_new_year = st.selectbox("Nouvelle année scolaire à activer", list(year_options.keys()))
    new_year_id = year_options[selected_new_year]

    # Étape 2 : Mapper les classes
    st.divider()
    st.markdown("#### 2. Configuration du passage de classes")
    st.write("Pour chaque classe actuelle, choisissez la classe dans laquelle les élèves seront promus.")
    
    current_classes = get_all_classes()
    class_dict = {c['id']: c['name'] for c in current_classes}
    
    # Dictionnaire pour sauvegarder les choix : {ancienne_classe_id: nouvelle_classe_id}
    class_mapping = {}
    
    for c in current_classes:
        # Le menu déroulant propose toutes les classes + "Ne pas promouvoir"
        opts = ["Ne pas promouvoir (Redoublement/Sortie)"] + [cl['name'] for cl in current_classes]
        selected = st.selectbox(f"Classe actuelle : {c['name']}", opts, key=f"map_{c['id']}")
        
        if selected != "Ne pas promouvoir (Redoublement/Sortance)":
            # On retrouve l'ID de la classe sélectionnée
            for cl in current_classes:
                if cl['name'] == selected:
                    class_mapping[c['id']] = cl['id']
                    break

    # Étape 3 : Validation finale
    st.divider()
    st.markdown("#### 3. Validation finale")
    confirm1 = st.checkbox("Je confirme avoir fait une sauvegarde de la base de données.")
    confirm2 = st.checkbox("Je confirme vouloir clôturer l'année et promouvoir les élèves selon le mapping ci-dessus.")
    
    if st.button("🚀 Lancer la Promotion et la Clôture", type="primary", use_container_width=True, disabled=not (confirm1 and confirm2)):
        with st.spinner("Traitement en cours..."):
            # 1. Promouvoir les élèves
            promoted_count = promote_students(class_mapping, new_year_id)
            
            # 2. Activer la nouvelle année
            set_active_school_year(new_year_id)
            
            # 3. Clôturer l'ancienne année (maintenant désactivée par set_active_school_year)
            close_active_year()
            
            st.success(f"✅ Opération réussie ! {promoted_count} élève(s) ont été promus et inscrits pour l'année {selected_new_year}.")
            st.balloons()
            st.info("Veuillez recharger l'application pour voir la nouvelle année active.")

# modules/school_years.py
import streamlit as st
import pandas as pd
from database.queries import get_all_school_years, get_active_school_year, add_school_year, set_active_school_year

def show_school_years():
    st.markdown("<h1 style='color: #1e293b;'>📅 Gestion des Années Scolaires</h1>", unsafe_allow_html=True)
    st.markdown("Contrôlez le cycle de vie académique de votre établissement.")
    st.divider()

    # --- 1. AFFICHAGE DE L'ANNÉE ACTIVE ---
    active_year = get_active_school_year()
    if active_year:
        st.success(f"✅ Année scolaire active actuellement : **{active_year['name']}**")
    else:
        st.warning("⚠️ Aucune année scolaire n'est active ! Veuillez en activer une.")
    st.divider()

    # --- 2. AJOUT D'UNE NOUVELLE ANNÉE ---
    st.markdown("### ➕ Créer une nouvelle année scolaire")
    col1, col2 = st.columns([3, 1])
    with col1:
        new_year_name = st.text_input("Nom de l'année (ex: 2027-2028)", "")
    with col2:
        st.write("") # Alignement
        st.write("")
        if st.button("Créer l'année", use_container_width=True):
            if new_year_name:
                year_id = add_school_year(new_year_name)
                if year_id:
                    st.success(f"✅ Année '{new_year_name}' créée avec succès !")
                    st.rerun()
                else:
                    st.error("Cette année scolaire existe déjà.")
            else:
                st.error("Veuillez entrer un nom pour l'année.")

    st.divider()

    # --- 3. LISTE ET ACTIVATION DES ANNÉES ---
    st.markdown("### 📋 Liste des années scolaires")
    years = get_all_school_years()
    
    if years:
        df = pd.DataFrame(years)
        # Formater l'affichage
        df['Statut'] = df.apply(lambda row: '🟢 Active' if row['is_active'] else ('🔴 Clôturée' if row['is_closed'] else '⚪ Inactive'), axis=1)
        df = df.rename(columns={'name': 'Année Scolaire'})
        
        st.dataframe(df[['Année Scolaire', 'Statut']], use_container_width=True, hide_index=True)
        
        st.divider()
        st.markdown("#### ⚙️ Activer une année")
        st.warning("Attention : Activer une nouvelle année désactivera l'année actuelle. Assurez-vous d'avoir clôturé et archivé l'ancienne année si nécessaire.")
        
        col_act1, col_act2 = st.columns([3, 1])
        with col_act1:
            # Menu déroulant pour choisir l'année à activer
            inactive_years = [y for y in years if not y['is_active']]
            if inactive_years:
                year_options = {y['name']: y['id'] for y in inactive_years}
                selected_year = st.selectbox("Sélectionner une année à activer", list(year_options.keys()))
            else:
                selected_year = None
                st.info("Toutes les années existantes sont déjà actives ou clôturées.")
                
        with col_act2:
            st.write("")
            st.write("")
            if selected_year:
                if st.button("Activer cette année", type="primary", use_container_width=True):
                    if set_active_school_year(year_options[selected_year]):
                        st.success(f"✅ L'année '{selected_year}' est maintenant active !")
                        st.rerun()
                    else:
                        st.error("Une erreur est survenue lors de l'activation.")
    else:
        st.info("Aucune année scolaire trouvée dans le système.")

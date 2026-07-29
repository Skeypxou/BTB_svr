# modules/parents.py
import streamlit as st
import pandas as pd
from database.queries import get_all_parents_with_children_count, add_parent, delete_parent

def show_parents():
    st.markdown("<h1 style='color: #1e293b;'>👨‍👩‍👦 Gestion des Parents et Tuteurs</h1>", unsafe_allow_html=True)
    st.markdown("Gérez les informations des parents et visualisez les enfants associés.")
    st.divider()

    # --- 1. BARRE DE RECHERCHE ---
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("🔎 Rechercher un parent (Nom, Téléphone)...", "")
    with col2:
        if st.button("➕ Ajouter un parent", use_container_width=True):
            st.session_state.show_add_parent_form = not st.session_state.get('show_add_parent_form', False)

    # --- 2. TABLEAU DES PARENTS ---
    parents = get_all_parents_with_children_count(search_term)
    
    if parents:
        df = pd.DataFrame(parents)
        # On renomme les colonnes pour l'affichage
        df = df.rename(columns={
            'first_name': 'Prénom', 'last_name': 'Nom', 'phone': 'Téléphone',
            'email': 'Email', 'profession': 'Profession', 'children_count': 'Enfants Associés'
        })
        
        # Affichage du tableau interactif
        st.dataframe(
            df[['Prénom', 'Nom', 'Téléphone', 'Email', 'Profession', 'Enfants Associés']], 
            use_container_width=True,
            hide_index=True
        )
        
        # --- 3. SUPPRESSION D'UN PARENT ---
        st.divider()
        st.markdown("#### 🗑️ Supprimer un parent")
        col_del1, col_del2 = st.columns([3, 1])
        with col_del1:
            # Création d'un dictionnaire : "Nom Prénom (Téléphone)" -> id
            parent_options = {f"{p['last_name']} {p['first_name']} ({p['phone']})": p['id'] for p in parents}
            selected_parent = st.selectbox("Sélectionner un parent à supprimer", list(parent_options.keys()))
        with col_del2:
            st.write("") # Espace vide pour aligner
            st.write("")
            if st.button("Supprimer définitivement", type="primary"):
                if selected_parent:
                    delete_parent(parent_options[selected_parent])
                    st.success("✅ Parent supprimé avec succès !")
                    st.rerun()
    else:
        st.info("Aucun parent trouvé. Cliquez sur 'Ajouter un parent' pour commencer.")

    # --- 4. FORMULAIRE D'AJOUT ---
    if st.session_state.get('show_add_parent_form', False):
        st.divider()
        st.markdown("### ➕ Ajouter un nouveau parent")
        
        with st.form("add_parent_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("Prénom *")
                last_name = st.text_input("Nom *")
                phone = st.text_input("Téléphone *")
                
            with col2:
                email = st.text_input("Email")
                profession = st.text_input("Profession")
                address = st.text_input("Adresse")

            submit = st.form_submit_button("Enregistrer le parent", use_container_width=True)
            
            if submit:
                if not first_name or not last_name or not phone:
                    st.error("Le prénom, le nom et le téléphone sont obligatoires.")
                else:
                    # Appel de la fonction d'ajout
                    parent_id = add_parent(first_name, last_name, phone, email, address, profession)
                    
                    if parent_id:
                        st.success(f"✅ Parent '{last_name} {first_name}' ajouté avec succès !")
                        st.session_state.show_add_parent_form = False # Ferme le formulaire
                        st.rerun()
                    else:
                        st.error("Une erreur est survenue lors de l'enregistrement.")

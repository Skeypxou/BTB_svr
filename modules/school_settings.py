# modules/school_settings.py
import streamlit as st
from pathlib import Path
from database.queries import get_school_settings, update_school_settings

# S'assurer que le dossier assets existe
ASSETS_DIR = Path("assets")
ASSETS_DIR.mkdir(exist_ok=True)

def show_school_settings():
    st.markdown("<h1 style='color: #1e293b;'>🏫 Paramètres de l'École</h1>", unsafe_allow_html=True)
    st.markdown("Configurez l'identité de l'établissement. Ces informations apparaîtront sur les documents officiels (PDF).")
    st.divider()

    # Récupération des données actuelles
    settings = get_school_settings()

    with st.form("settings_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Informations Générales")
            name = st.text_input("Nom de l'école *", value=settings['name'] if settings else "")
            director_name = st.text_input("Nom du Directeur", value=settings['director_name'] if settings else "")
            address = st.text_area("Adresse", value=settings['address'] if settings else "")
            
        with col2:
            st.markdown("#### Coordonnées")
            phone = st.text_input("Téléphone", value=settings['phone'] if settings else "")
            email = st.text_input("Email", value=settings['email'] if settings else "")
            website = st.text_input("Site Web", value=settings['website'] if settings else "")
            
            st.markdown("#### Logo de l'école")
            # Afficher le logo actuel s'il existe
            if settings and settings['logo_path']:
                logo_path = ASSETS_DIR / settings['logo_path']
                if logo_path.exists():
                    st.image(str(logo_path), width=150)
            
            # Champ pour uploader un nouveau logo
            logo_file = st.file_uploader("Changer le logo (PNG, JPG)", type=['png', 'jpg', 'jpeg'])

        submit = st.form_submit_button("💾 Enregistrer les paramètres", use_container_width=True)

        if submit:
            if not name:
                st.error("Le nom de l'école est obligatoire.")
            else:
                logo_filename = None
                # Si un nouveau logo est uploadé, on le sauvegarde dans le dossier assets/
                if logo_file is not None:
                    logo_filename = "logo.png" # On force un nom standard
                    with open(ASSETS_DIR / logo_filename, "wb") as f:
                        f.write(logo_file.getbuffer())

                # Mise à jour dans la base de données
                success = update_school_settings(name, address, phone, email, website, director_name, logo_filename)
                
                if success:
                    st.success("✅ Paramètres enregistrés avec succès !")
                    st.rerun()
                else:
                    st.error("Une erreur est survenue lors de l'enregistrement.")

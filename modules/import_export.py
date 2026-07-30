# modules/import_export.py
import streamlit as st
import pandas as pd
from database.queries import get_all_students, get_all_payments_for_export, bulk_import_students
from utils.excel_handler import export_to_excel

def show_import_export():
    st.markdown("<h1 style='color: #1e293b;'>📊 Import / Export Excel</h1>", unsafe_allow_html=True)
    st.markdown("Échangez des données en masse avec des fichiers Excel (.xlsx) ou CSV.")
    st.divider()

    tab1, tab2 = st.tabs(["📤 Exporter des Données", "📥 Importer des Élèves"])

    # --- ONGLET 1 : EXPORTER ---
    with tab1:
        st.markdown("#### Télécharger les données du système")
        export_choice = st.selectbox("Choisir les données à exporter", ["Liste des Élèves", "Historique des Paiements"])
        
        if st.button("Générer le fichier Excel", use_container_width=True):
            if export_choice == "Liste des Élèves":
                data = get_all_students()
                file_name = "Liste_Eleves.xlsx"
                sheet = "Élèves"
            else:
                data = get_all_payments_for_export()
                file_name = "Historique_Paiements.xlsx"
                sheet = "Paiements"
                
            if data:
                excel_buffer = export_to_excel(data, sheet_name=sheet)
                if excel_buffer:
                    st.success("✅ Fichier généré avec succès !")
                    st.download_button(
                        label="📥 Télécharger Excel",
                        data=excel_buffer,
                        file_name=file_name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            else:
                st.warning("Aucune donnée à exporter pour cette catégorie.")

    # --- ONGLET 2 : IMPORTER ---
    with tab2:
        st.markdown("#### Importer une liste d'élèves")
        st.info("⚠️ Le fichier Excel doit contenir les colonnes exactes suivantes : `Nom`, `Prenom`, `Sexe`, `DateDeNaissance` (YYYY-MM-DD), `Telephone`, `Adresse`.")
        
        # Fournir un modèle téléchargeable
        if st.button("📥 Télécharger le modèle Excel vide"):
            model_data = [{"Nom": "", "Prenom": "", "Sexe": "M", "DateDeNaissance": "2010-01-01", "Telephone": "", "Adresse": ""}]
            model_buffer = export_to_excel(model_data, sheet_name="Modèle")
            if model_buffer:
                st.download_button(
                    label="Télécharger Modèle_Eleves.xlsx",
                    data=model_buffer,
                    file_name="Modele_Eleves.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        st.divider()
        
        uploaded_file = st.file_uploader("Choisir un fichier Excel ou CSV", type=['xlsx', 'xls', 'csv'])
        
        if uploaded_file is not None:
            try:
                # Lire le fichier
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                    
                st.success(f"Fichier chargé : {uploaded_file.name} ({len(df)} lignes détectées)")
                
                # Afficher un aperçu
                st.markdown("##### Aperçu des données :")
                st.dataframe(df.head(), use_container_width=True)
                
                if st.button("✅ Valider l'importation", type="primary", use_container_width=True):
                    with st.spinner("Importation en cours..."):
                        count, errors = bulk_import_students(df)
                        st.success(f"✅ Importation terminée ! {count} élève(s) ajouté(s) avec succès.")
                        if errors:
                            st.warning(f"Il y a eu des erreurs sur certaines lignes :\n{errors}")
                            st.rerun()
                            
            except Exception as e:
                st.error(f"Erreur lors de la lecture du fichier : {e}")

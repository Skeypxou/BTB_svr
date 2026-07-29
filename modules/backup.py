# modules/backup.py
import streamlit as st
from utils.backup_manager import backup_sqlite, backup_json, get_sqlite_backups_list, restore_sqlite

def show_backup():
    st.markdown("<h1 style='color: #1e293b;'>💾 Sauvegarde et Restauration</h1>", unsafe_allow_html=True)
    st.markdown("Protégez les données de l'établissement contre les pertes.")
    st.divider()

    tab1, tab2 = st.tabs(["📥 Sauvegarder", "📤 Restaurer"])

    # --- ONGLET 1 : SAUVEGARDER ---
    with tab1:
        st.markdown("### Générer une nouvelle sauvegarde")
        st.write("Il est recommandé de sauvegarder régulièrement les données (ex: une fois par semaine ou avant une opération importante).")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🗄️ Sauvegarde Complète (SQLite)")
            st.caption("Copie exacte de toute la base de données. Idéal pour restaurer en cas de crash.")
            if st.button("Lancer la sauvegarde SQLite", use_container_width=True, type="primary"):
                with st.spinner("Sauvegarde en cours..."):
                    result = backup_sqlite()
                    if result:
                        st.success(f"✅ Sauvegarde réussie ! Fichier créé : `{result}`")
                    else:
                        st.error("Échec de la sauvegarde.")
                        
        with col2:
            st.markdown("#### 📄 Sauvegarde Lisible (JSON)")
            st.caption("Exporte les élèves, notes, paiements... au format JSON. Utile pour importer dans un autre logiciel.")
            if st.button("Lancer l'exportation JSON", use_container_width=True):
                with st.spinner("Exportation en cours..."):
                    result = backup_json()
                    if result:
                        st.success(f"✅ Exportation réussie ! Fichier créé : `{result}`")
                    else:
                        st.error("Échec de l'exportation.")

    # --- ONGLET 2 : RESTAURER ---
    with tab2:
        st.markdown("### Restaurer une base de données existante")
        st.warning("⚠️ Attention : La restauration remplacera toutes les données actuelles par celles de la sauvegarde. Cette action est irréversible.")
        
        backups = get_sqlite_backups_list()
        
        if backups:
            # Afficher la liste des sauvegardes
            backup_options = {f"{f.name} (Créé le {datetime.fromtimestamp(os.path.getmtime(f)).strftime('%d/%m/%Y à %H:%M')})": str(f) for f in backups}
            selected_backup = st.selectbox("Sélectionnez une sauvegarde à restaurer", list(backup_options.keys()))
            
            if st.button("Restaurer cette sauvegarde", type="primary", use_container_width=True):
                # Double confirmation
                confirm = st.checkbox("Je comprends que les données actuelles seront écrasées.")
                if confirm:
                    with st.spinner("Restauration en cours..."):
                        if restore_sqlite(backup_options[selected_backup]):
                            st.success("✅ Base de données restaurée avec succès ! Veuillez recharger l'application.")
                            st.balloons()
                        else:
                            st.error("Échec de la restauration.")
                else:
                    st.info("Veuillez cocher la case de confirmation.")
        else:
            st.info("Aucune sauvegarde SQLite trouvée dans le dossier 'backups/'.")

# Importations nécessaires pour l'affichage
from datetime import datetime
import os

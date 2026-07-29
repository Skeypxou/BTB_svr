# modules/dashboard.py
import streamlit as st
import plotly.express as px
import pandas as pd
from database.database import fetch_query

def show_dashboard():
    st.markdown("<h1 style='color: #1e293b;'>📊 Tableau de Bord</h1>", unsafe_allow_html=True)
    st.markdown("Vue d'ensemble de l'établissement scolaire.")
    st.divider()
    
    # --- 1. RÉCUPÉRATION DES DONNÉES (KPIs) ---
    # On compte le nombre d'élèves, d'enseignants, de classes et de parents
    
    total_students = fetch_query("SELECT COUNT(id) as count FROM students")[0]['count']
    total_teachers = fetch_query("SELECT COUNT(id) as count FROM teachers")[0]['count']
    total_classes = fetch_query("SELECT COUNT(id) as count FROM classes")[0]['count']
    total_parents = fetch_query("SELECT COUNT(id) as count FROM parents")[0]['count']
    
    # --- 2. AFFICHAGE DES CARTES STATISTIQUES (KPIs) ---
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="👥 Élèves Inscrits", value=total_students)
    with col2:
        st.metric(label="👨‍🏫 Enseignants", value=total_teachers)
    with col3:
        st.metric(label="🏫 Classes Actives", value=total_classes)
    with col4:
        st.metric(label="👨‍👩‍👦 Parents", value=total_parents)
        
    st.divider()
    
    # --- 3. GRAPHIQUES AVEC PLOTLY ---
    # Comme la base est vide pour l'instant, on affiche des données de démonstration
    # Plus tard, ces données viendront de la base SQLite
    
    st.markdown("### 📈 Analyse Académique et Financière")
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("#### Évolution des Inscriptions (Mois en cours)")
        # Données factices pour la démo visuelle
        df_inscriptions = pd.DataFrame({
            'Mois': ['Sept', 'Oct', 'Nov', 'Déc', 'Jan'],
            'Inscriptions': [45, 30, 12, 8, 15]
        })
        fig_inscriptions = px.bar(df_inscriptions, x='Mois', y='Inscriptions', 
                                  text='Inscriptions', color='Inscriptions',
                                  color_continuous_scale='Blues')
        fig_inscriptions.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_inscriptions, use_container_width=True)
        
    with col_right:
        st.markdown("#### Répartition des Effectifs par Niveau")
        # Données factices pour la démo visuelle
        df_niveaux = pd.DataFrame({
            'Niveau': ['Préscolaire', 'Primaire', 'Moyen', 'Secondaire'],
            'Effectif': [50, 120, 80, 45]
        })
        fig_niveaux = px.pie(df_niveaux, values='Effectif', names='Niveau', 
                             hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_niveaux.update_layout(height=350)
        st.plotly_chart(fig_niveaux, use_container_width=True)
        
    # --- 4. ZONE DE NOTIFICATIONS ---
    st.divider()
    st.markdown("### 🔔 Notifications Récentes")
    
    col_alert1, col_alert2, col_alert3 = st.columns(3)
    with col_alert1:
        st.info("📅 Rappel : Réunion pédagogique demain à 10h.")
    with col_alert2:
        st.warning("⚠️ 3 paiements en retard ce mois-ci.")
    with col_alert3:
        st.success("✅ Sauvegarde automatique réussie hier à 23h00.")

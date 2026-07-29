# modules/finances.py
import streamlit as st
import pandas as pd
from database.queries import (
    add_school_fee, get_all_school_fees, 
    record_payment, get_payments_by_student, get_all_payments,
    get_all_students
)

def show_finances():
    st.markdown("<h1 style='color: #1e293b;'>💰 Gestion Financière</h1>", unsafe_allow_html=True)
    st.markdown("Gérez les frais de scolarité, encaissez les paiements et suivez les impayés.")
    st.divider()

    tab1, tab2, tab3 = st.tabs(["⚙️ Configuration des Frais", "💳 Encaisser un Paiement", "📊 Rapports & Historique"])

    # --- ONGLET 1 : CONFIGURATION ---
    with tab1:
        st.markdown("#### Ajouter un type de frais")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            fee_name = st.text_input("Nom du frais (ex: Mensualité Octobre)", key="fee_name")
        with col2:
            fee_amount = st.number_input("Montant (Devise)", min_value=0.0, step=100.0, key="fee_amount")
        with col3:
            st.write("")
            st.write("")
            if st.button("Ajouter le frais", use_container_width=True, key="add_fee"):
                if fee_name and fee_amount > 0:
                    add_school_fee(fee_name, fee_amount)
                    st.success(f"Frais '{fee_name}' ajouté !")
                    st.rerun()
                else:
                    st.error("Veuillez remplir le nom et le montant.")

        st.markdown("#### Liste des frais configurés")
        fees = get_all_school_fees()
        if fees:
            df = pd.DataFrame(fees)
            df = df.rename(columns={'name': 'Frais', 'amount': 'Montant'})
            st.dataframe(df[['Frais', 'Montant']], use_container_width=True, hide_index=True)
        else:
            st.info("Aucun frais configuré pour l'année active.")

    # --- ONGLET 2 : ENCAISSEMENT ---
    with tab2:
        st.markdown("#### Nouveau Paiement")
        students = get_all_students()
        fees = get_all_school_fees()

        if not students:
            st.warning("Aucun élève dans le système.")
        elif not fees:
            st.warning("Veuillez d'abord configurer des frais dans l'onglet 1.")
        else:
            with st.form("payment_form"):
                col1, col2 = st.columns(2)
                with col1:
                    student_options = {f"{s['matricule']} - {s['last_name']} {s['first_name']}": s['id'] for s in students}
                    selected_student = st.selectbox("Élève", list(student_options.keys()), key="pay_student")
                    
                    fee_options = {f"{f['name']} ({f['amount']} FCFA)": f['id'] for f in fees}
                    selected_fee = st.selectbox("Type de frais", list(fee_options.keys()), key="pay_fee")
                    
                with col2:
                    # On récupère le montant par défaut du frais sélectionné
                    selected_fee_obj = next(f for f in fees if f['id'] == fee_options[selected_fee])
                    
                    amount_paid = st.number_input("Montant payé", min_value=0.0, value=float(selected_fee_obj['amount']), step=100.0, key="pay_amount")
                    method = st.selectbox("Méthode de paiement", ["Espèces", "Virement", "Carte Bancaire"], key="pay_method")
                    status = st.selectbox("Statut", ["Payé", "Partiellement payé", "Impayé"], key="pay_status")

                submit = st.form_submit_button("💾 Encaisser le paiement", use_container_width=True)
                
                if submit:
                    record_payment(
                        student_options[selected_student], 
                        fee_options[selected_fee], 
                        amount_paid, method, status
                    )
                    st.success(f"✅ Paiement encaissé avec succès pour {selected_student} !")

    # --- ONGLET 3 : RAPPORTS ---
    with tab3:
        st.markdown("#### Historique global des paiements")
        payments = get_all_payments()
        
        if payments:
            df = pd.DataFrame(payments)
            df = df.rename(columns={
                'payment_date': 'Date', 'matricule': 'Matricule', 'student_name': 'Élève',
                'fee_name': 'Frais', 'amount_paid': 'Montant', 'method': 'Méthode', 'status': 'Statut'
            })
            
            # Filtre par statut
            status_filter = st.multiselect("Filtrer par statut", ["Payé", "Partiellement payé", "Impayé"], default=["Payé", "Partiellement payé", "Impayé"])
            if status_filter:
                df = df[df['Statut'].isin(status_filter)]
                
            st.dataframe(df[['Date', 'Matricule', 'Élève', 'Frais', 'Montant', 'Méthode', 'Statut']], use_container_width=True, hide_index=True)
            
            # Calcul du total encaissé
            total_revenu = df[df['Statut'] == 'Payé']['Montant'].sum()
            st.metric(label="💵 Total Encaissé (Payé)", value=f"{total_revenu:,.2f} FCFA")
        else:
            st.info("Aucun paiement enregistré pour le moment.")

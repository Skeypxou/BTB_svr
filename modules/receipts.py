# modules/receipts.py
import streamlit as st
import pandas as pd
from database.queries import get_all_payments, get_payment_details
from pdf.receipt_generator import generate_receipt_pdf

def show_receipts():
    st.markdown("<h1 style='color: #1e293b;'>🧾 Reçus de Paiement</h1>", unsafe_allow_html=True)
    st.markdown("Générez et imprimez les reçus officiels pour les paiements encaissés.")
    st.divider()

    payments = get_all_payments()
    
    if payments:
        st.markdown("#### Historique des paiements récents")
        df = pd.DataFrame(payments)
        df = df.rename(columns={
            'payment_date': 'Date', 'matricule': 'Matricule', 'student_name': 'Élève',
            'fee_name': 'Frais', 'amount_paid': 'Montant', 'method': 'Méthode', 'status': 'Statut'
        })
        
        # Afficher le tableau (sans l'ID)
        st.dataframe(df[['Date', 'Matricule', 'Élève', 'Frais', 'Montant', 'Méthode', 'Statut']], use_container_width=True, hide_index=True)
        
        st.divider()
        st.markdown("#### 🖨️ Génération du Reçu PDF")
        
        # Menu déroulant pour choisir le paiement
        # On crée une liste lisible : "N°REC-0001 - Nom Élève (Date)"
        payment_options = {
            f"{p['matricule']} - {p['student_name']} ({p['fee_name']} - {p['payment_date']})": p['id'] 
            for p in payments
        }
        selected_payment = st.selectbox("Sélectionner un paiement", list(payment_options.keys()))
        
        if st.button("Générer le Reçu PDF", use_container_width=True, type="primary"):
            payment_id = payment_options[selected_payment]
            payment_details = get_payment_details(payment_id)
            
            if payment_details:
                with st.spinner("Génération du reçu..."):
                    pdf_buffer = generate_receipt_pdf(payment_details)
                    st.success("✅ Reçu généré avec succès !")
                    st.download_button(
                        label="📥 Télécharger le Reçu",
                        data=pdf_buffer,
                        file_name=f"Recu_{payment_details['last_name']}_{payment_details['first_name']}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            else:
                st.error("Impossible de trouver les détails de ce paiement.")
    else:
        st.info("Aucun paiement n'a été enregistré pour le moment.")

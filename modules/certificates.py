# modules/certificates.py
import streamlit as st
from database.queries import get_all_students, get_student_details_for_certificate
from pdf.certificate_generator import generate_school_certificate_pdf

def show_certificates():
    st.markdown("<h1 style='color: #1e293b;'>📜 Certificats et Attestations</h1>", unsafe_allow_html=True)
    st.markdown("Générez des documents officiels en PDF pour vos élèves.")
    st.divider()

    st.markdown("#### 1. Sélectionner l'élève")
    students = get_all_students()
    
    if not students:
        st.info("Aucun élève enregistré dans le système.")
        return

    # Menu déroulant pour choisir l'élève
    student_options = {f"{s['matricule']} - {s['last_name']} {s['first_name']}": s['id'] for s in students}
    selected_student_name = st.selectbox("Choisir un élève", list(student_options.keys()))
    selected_student_id = student_options[selected_student_name]

    st.markdown("#### 2. Choisir le type de document")
    doc_type = st.selectbox("Type de document", ["Certificat de Scolarité", "Attestation d'Inscription", "Attestation de Réussite"])
    
    st.divider()

    if st.button("🖨️ Générer le document PDF", use_container_width=True, type="primary"):
        with st.spinner("Génération du document en cours..."):
            # Récupérer les détails de l'élève
            student_details = get_student_details_for_certificate(selected_student_id)
            
            if student_details:
                if doc_type == "Certificat de Scolarité":
                    pdf_buffer = generate_school_certificate_pdf(student_details)
                    file_name = f"Certificat_Scolarite_{student_details['last_name']}_{student_details['first_name']}.pdf"
                # (Plus tard, on ajoutera les autres types ici)
                else:
                    st.warning("Ce type de document sera disponible prochainement.")
                    return
                
                st.success("✅ Document généré avec succès !")
                st.download_button(
                    label="📥 Télécharger le PDF",
                    data=pdf_buffer,
                    file_name=file_name,
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.error("Impossible de récupérer les détails de cet élève. Est-il bien inscrit dans une classe pour l'année active ?")

# modules/school_cards.py
import streamlit as st
from database.queries import get_all_classes, get_students_by_class, get_student_for_card
from pdf.card_generator import generate_student_card

def show_school_cards():
    st.markdown("<h1 style='color: #1e293b;'>🪪 Cartes Scolaires</h1>", unsafe_allow_html=True)
    st.markdown("Générez les cartes d'identité scolaire avec QR Code pour vos élèves.")
    st.divider()

    col1, col2 = st.columns(2)
    
    with col1:
        classes = get_all_classes()
        class_options = {c['name']: c['id'] for c in classes} if classes else {}
        selected_class = st.selectbox("Classe", list(class_options.keys()) if class_options else ["Aucune"], key="card_class")
        
    if selected_class != "Aucune":
        students = get_students_by_class(class_options[selected_class])
        
        if students:
            with col2:
                student_options = {f"{s['last_name']} {s['first_name']}": s['id'] for s in students}
                selected_student = st.selectbox("Élève", list(student_options.keys()), key="card_student")
                
            st.divider()
            
            if st.button("🖨️ Générer la Carte PNG", use_container_width=True, type="primary"):
                student_id = student_options[selected_student]
                student_info = get_student_for_card(student_id)
                
                if student_info:
                    with st.spinner("Génération de la carte..."):
                        card_buffer = generate_student_card(student_info)
                        st.success("✅ Carte générée avec succès !")
                        
                        # Afficher l'aperçu de l'image
                        st.image(card_buffer, caption=f"Carte de {selected_student}", use_container_width=False)
                        
                        # Bouton de téléchargement
                        st.download_button(
                            label="📥 Télécharger la carte (PNG)",
                            data=card_buffer,
                            file_name=f"Carte_{student_info['last_name']}_{student_info['first_name']}.png",
                            mime="image/png",
                            use_container_width=True
                        )
                else:
                    st.error("Impossible de récupérer les informations de cet élève.")
        else:
            st.info("Aucun élève dans cette classe.")

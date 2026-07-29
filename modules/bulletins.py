# modules/bulletins.py
import streamlit as st
from database.queries import get_all_classes, get_students_by_class
from pdf.bulletin_generator import generate_bulletin_pdf

def show_bulletins():
    st.markdown("<h1 style='color: #1e293b;'>📄 Bulletins Scolaires</h1>", unsafe_allow_html=True)
    st.markdown("Générez des bulletins PDF professionnels pour vos élèves.")
    st.divider()

    col1, col2, col3 = st.columns(3)
    
    with col1:
        classes = get_all_classes()
        class_options = {c['name']: c['id'] for c in classes} if classes else {}
        selected_class_name = st.selectbox("Classe", list(class_options.keys()) if class_options else ["Aucune"], key="bul_class")
        
    with col2:
        trimester = st.selectbox("Trimestre", ["Trimestre 1", "Trimestre 2", "Trimestre 3"], key="bul_trim")
        
    with col3:
        st.write("")
        st.write("")
        generate_clicked = st.button("🖨️ Générer le bulletin de la classe", use_container_width=True)

    st.divider()
    
    if selected_class_name != "Aucune":
        students = get_students_by_class(class_options[selected_class_name])
        
        if students:
            st.markdown(f"#### Élèves de {selected_class_name}")
            
            # Pour chaque élève, on crée un expander avec un bouton pour générer son PDF
            for student in students:
                with st.expander(f"{student['last_name']} {student['first_name']} ({student['matricule']})"):
                    if st.button(f"Générer PDF", key=f"btn_pdf_{student['id']}"):
                        trim_num = int(trimester.split()[-1])
                        
                        with st.spinner("Génération du PDF en cours..."):
                            try:
                                # On doit ajouter class_id à l'objet student pour la fonction de calcul du rang
                                student['class_id'] = class_options[selected_class_name] 
                                pdf_buffer = generate_bulletin_pdf(student, selected_class_name, trim_num)
                                
                                # Afficher le PDF dans Streamlit
                                st.download_button(
                                    label="📥 Télécharger le bulletin",
                                    data=pdf_buffer,
                                    file_name=f"Bulletin_{student['last_name']}_{student['first_name']}_T{trim_num}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                                st.success("✅ Cliquez sur le bouton ci-dessus pour télécharger le PDF.")
                            except Exception as e:
                                st.error(f"Erreur lors de la génération : {e}")
        else:
            st.info("Aucun élève dans cette classe.")

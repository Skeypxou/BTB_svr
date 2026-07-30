# pdf/certificate_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.enums import CENTER
from pathlib import Path
from database.queries import get_school_settings
from datetime import datetime
import io

def generate_school_certificate_pdf(student):
    """Génère un Certificat de Scolarité en PDF."""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=22, textColor=colors.HexColor('#1e293b'), alignment=CENTER, spaceAfter=20)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=14, textColor=colors.HexColor('#2563eb'), alignment=CENTER, spaceAfter=30)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=12, leading=18, alignment=0) # 0 = Justify
    
    elements = []
    settings = get_school_settings()
    
    # --- EN-TÊTE ---
    if settings and settings['logo_path']:
        logo_path = Path("assets") / settings['logo_path']
        if logo_path.exists():
            img = Image(str(logo_path), width=40*mm, height=40*mm)
            img.hAlign = CENTER
            elements.append(img)
            
    elements.append(Paragraph(settings['name'] if settings else "Mon École", title_style))
    elements.append(Paragraph(settings['address'] if settings else "", body_style))
    elements.append(Paragraph(f"Tél: {settings['phone'] if settings else ''} | Email: {settings['email'] if settings else ''}", body_style))
    elements.append(Spacer(1, 15*mm))
    
    # --- TITRE DU DOCUMENT ---
    elements.append(Paragraph("CERTIFICAT DE SCOLARITÉ", subtitle_style))
    elements.append(Spacer(1, 10*mm))
    
    # --- CORPS DU TEXTE ---
    date_str = datetime.now().strftime("%d/%m/%Y")
    text = f"""
    Je soussigné(e), <b>{settings['director_name'] if settings else 'Le Directeur'}</b>, Directeur(trice) de l'établissement 
    <b>{settings['name'] if settings else 'Mon École'}</b>, certifie que l'élève :<br/><br/>
    <b>Nom :</b> {student['last_name']}<br/>
    <b>Prénom :</b> {student['first_name']}<br/>
    <b>Date de naissance :</b> {student['dob']}<br/>
    <b>Matricule :</b> {student['matricule']}<br/><br/>
    Est régulièrement inscrit(e) pour l'année scolaire <b>{student['year_name']}</b> dans la classe de : 
    <b>{student['class_name']}</b>.<br/><br/>
    En foi de quoi, le présent certificat lui est délivré pour servir et valoir ce que de droit.
    """
    elements.append(Paragraph(text, body_style))
    elements.append(Spacer(1, 40*mm))
    
    # --- SIGNATURE ---
    sign_style = ParagraphStyle('Sign', parent=body_style, alignment=1) # 1 = Center
    elements.append(Paragraph(f"Fait à {settings['address'].split(',')[0] if settings else 'Ville'}, le {date_str}", sign_style))
    elements.append(Spacer(1, 15*mm))
    elements.append(Paragraph("Le Directeur / La Directrice", sign_style))
    elements.append(Paragraph(f"<b>{settings['director_name'] if settings else ''}</b>", sign_style))
    
    # Bordure de page (optionnel mais donne un côté officiel)
    doc.build(elements)
    buffer.seek(0)
    return buffer

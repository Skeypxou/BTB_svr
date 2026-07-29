# pdf/bulletin_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import CENTER
from pathlib import Path
from database.queries import get_school_settings, get_student_grades_for_bulletin, calculate_class_rankings
import io

def generate_bulletin_pdf(student, class_name, trimester):
    """Génère le bulletin PDF d'un élève et retourne les octets (bytes) du PDF."""
    
    # Création d'un tampon mémoire pour le PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=16, textColor=colors.HexColor('#1e293b'), alignment=CENTER)
    normal_style = styles['Normal']
    
    elements = []
    settings = get_school_settings()
    
    # --- EN-TÊTE (Logo + Infos École) ---
    if settings and settings['logo_path']:
        logo_path = Path("assets") / settings['logo_path']
        if logo_path.exists():
            img = Image(str(logo_path), width=30*mm, height=30*mm)
            elements.append(img)
            
    elements.append(Paragraph(settings['name'] if settings else "Mon École", title_style))
    elements.append(Paragraph(f"Adresse: {settings['address'] if settings else ''} | Tél: {settings['phone'] if settings else ''}", normal_style))
    elements.append(Spacer(1, 10*mm))
    
    # --- INFOS ÉLÈVE ---
    elements.append(Paragraph(f"<b>Bulletin de Notes - Trimestre {trimester}</b>", normal_style))
    elements.append(Paragraph(f"Élève : <b>{student['last_name']} {student['first_name']}</b> ({student['matricule']})", normal_style))
    elements.append(Paragraph(f"Classe : {class_name}", normal_style))
    elements.append(Spacer(1, 5*mm))
    
    # --- TABLEAU DES NOTES ---
    grades = get_student_grades_for_bulletin(student['id'], trimester)
    
    # En-têtes du tableau
    data = [["Matière", "Coef", "Évaluations", "Moyenne /20", "Appréciation"]]
    
    # Regrouper les notes par matière
    subjects_dict = {}
    for g in grades:
        if g['subject_name'] not in subjects_dict:
            subjects_dict[g['subject_name']] = {'coef': g['coefficient'], 'notes': []}
        subjects_dict[g['subject_name']]['notes'].append(f"{g['eval_type']}: {g['score']}/{g['max_score']}")
    
    total_points = 0
    total_coef = 0
    
    for subj_name, info in subjects_dict.items():
        # Calcul de la moyenne de la matière (simplifié pour l'exemple : moyenne des notes ramenées sur 20)
        moyennes = []
        for note_str in info['notes']:
            # Extraction de la note "Devoir: 15/20" -> 15/20
            score_str = note_str.split(":")[1].strip()
            score, max_score = map(float, score_str.split("/"))
            if max_score > 0:
                moyennes.append((score / max_score) * 20)
                
        moy_matiere = sum(moyennes) / len(moyennes) if moyennes else 0
        appreciation = "Très bien" if moy_matiere >= 15 else ("Bien" if moy_matiere >= 12 else ("Passable" if moy_matiere >= 10 else "Insuffisant"))
        
        data.append([
            subj_name,
            str(info['coef']),
            Paragraph("<br/>".join(info['notes']), normal_style), # Plusieurs notes sur des lignes
            f"{moy_matiere:.2f}",
            appreciation
        ])
        
        total_points += moy_matiere * info['coef']
        total_coef += info['coef']
        
    # Ajout du tableau au document
    table = Table(data, colWidths=[40*mm, 15*mm, 50*mm, 25*mm, 40*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')])
    ]))
    elements.append(table)
    elements.append(Spacer(1, 10*mm))
    
    # --- MOYENNE GÉNÉRALE ET RANG ---
    moy_generale = (total_points / total_coef) if total_coef > 0 else 0
    
    # Récupération du rang (en utilisant la fonction de l'étape 11)
    rankings = calculate_class_rankings(student['class_id'] if 'class_id' in student else None, trimester)
    rang = "N/A"
    for r in rankings:
        if r['student_id'] == student['id']:
            rang = f"{r['rank']} / {len(rankings)}"
            break
            
    elements.append(Paragraph(f"<b>Moyenne Générale : {moy_generale:.2f} / 20</b>", normal_style))
    elements.append(Paragraph(f"<b>Rang : {rang}</b>", normal_style))
    
    # Signature
    elements.append(Spacer(1, 20*mm))
    elements.append(Paragraph("Le Directeur", normal_style))
    
    # Construction du PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

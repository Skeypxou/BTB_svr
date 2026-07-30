# pdf/receipt_generator.py
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from pathlib import Path
from database.queries import get_school_settings
import io

def generate_receipt_pdf(payment):
    """Génère un Reçu de Paiement en PDF (Format A5 paysage)."""
    
    buffer = io.BytesIO()
    # Format A5 paysage (plus petit que A4, idéal pour les reçus)
    doc = SimpleDocTemplate(buffer, pagesize=(A5[1], A5[0]), rightMargin=15*mm, leftMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=16, textColor=colors.HexColor('#1e293b'), alignment=CENTER)
    normal_style = styles['Normal']
    right_style = ParagraphStyle('Right', parent=normal_style, alignment=RIGHT)
    
    elements = []
    settings = get_school_settings()
    
    # --- EN-TÊTE ---
    # Petit logo à gauche, infos à droite
    header_data = []
    if settings and settings['logo_path']:
        logo_path = Path("assets") / settings['logo_path']
        if logo_path.exists():
            img = Image(str(logo_path), width=25*mm, height=25*mm)
            header_data.append([img, Paragraph(f"<b>{settings['name'] if settings else 'Mon École'}</b><br/>{settings['address'] if settings else ''}<br/>Tél: {settings['phone'] if settings else ''}", normal_style)])
    else:
        header_data.append(["", Paragraph(f"<b>{settings['name'] if settings else 'Mon École'}</b><br/>{settings['address'] if settings else ''}", normal_style)])
        
    header_table = Table(header_data, colWidths=[30*mm, 120*mm])
    header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    elements.append(header_table)
    elements.append(Spacer(1, 10*mm))
    
    # --- TITRE REÇU ---
    elements.append(Paragraph("REÇU DE PAIEMENT", title_style))
    elements.append(Spacer(1, 5*mm))
    
    # Numéro de reçu (basé sur l'ID du paiement)
    receipt_num = f"REC-{payment['id']:05d}"
    elements.append(Paragraph(f"<b>N° {receipt_num}</b>", right_style))
    elements.append(Paragraph(f"Date: {payment['payment_date']}", right_style))
    elements.append(Spacer(1, 10*mm))
    
    # --- INFOS PAIEMENT ---
    elements.append(Paragraph(f"Reçu de : <b>{payment['last_name']} {payment['first_name']}</b> ({payment['matricule']})", normal_style))
    elements.append(Paragraph(f"Objet du paiement : <b>{payment['fee_name']}</b>", normal_style))
    elements.append(Paragraph(f"Méthode de paiement : <b>{payment['method']}</b>", normal_style))
    elements.append(Spacer(1, 10*mm))
    
    # --- TABLEAU MONTANT ---
    amount_data = [
        ["Montant Total", f"{payment['amount_paid']:,.2f} FCFA".replace(",", " ")],
        ["Statut", payment['status']]
    ]
    amount_table = Table(amount_data, colWidths=[100*mm, 50*mm])
    amount_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1e293b')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(amount_table)
    elements.append(Spacer(1, 15*mm))
    
    # --- SIGNATURE ---
    elements.append(Paragraph("Le Comptable / La Caisse", right_style))
    elements.append(Spacer(1, 15*mm))
    elements.append(Paragraph("<b>Signature et Cachet</b>", right_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

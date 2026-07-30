# pdf/card_generator.py
from PIL import Image, ImageDraw, ImageFont
import qrcode
from io import BytesIO
from pathlib import Path
from database.queries import get_school_settings

def generate_student_card(student):
    """Génère une image de carte scolaire avec un QR Code."""
    
    # 1. Création du QR Code (contient le matricule de l'élève)
    qr = qrcode.QRCode(version=1, box_size=4, border=1)
    qr.add_data(student['matricule'])
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    
    # 2. Création du fond de la carte (Format carte de crédit approximatif : 400x250 pixels)
    card_width, card_height = 400, 250
    card = Image.new('RGB', (card_width, card_height), color='#ffffff')
    draw = ImageDraw.Draw(card)
    
    # Bande de couleur en haut
    draw.rectangle([0, 0, card_width, 50], fill='#2563eb')
    
    # Texte de l'école
    settings = get_school_settings()
    school_name = settings['name'] if settings else "Mon École"
    
    # Pour éviter les erreurs de police sur Windows/Mac/Linux, on utilise la police par défaut
    # (Plus tard, tu pourras charger une police .ttf pour un style plus beau)
    try:
        font_title = ImageFont.truetype("arial.ttf", 20)
        font_text = ImageFont.truetype("arial.ttf", 14)
        font_small = ImageFont.truetype("arial.ttf", 12)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
        font_small = ImageFont.load_default()
        
    draw.text((20, 15), school_name[:25], fill='white', font=font_title)
    
    # 3. Ajout de la photo de l'élève
    photo_x, photo_y = 20, 70
    default_photo_path = Path("assets/logo.png") # Photo par défaut si l'élève n'en a pas
    
    # On utilise la photo de l'élève si elle existe
    student_photo_path = Path("photos") / student['photo_path'] if student['photo_path'] else default_photo_path
    if not student_photo_path.exists():
        student_photo_path = default_photo_path
        
    try:
        img_photo = Image.open(student_photo_path)
        img_photo = img_photo.resize((100, 120))
        # Coller la photo
        card.paste(img_photo, (photo_x, photo_y))
        # Bordure de la photo
        draw.rectangle([photo_x, photo_y, photo_x+100, photo_y+120], outline='#1e293b', width=2)
    except Exception:
        draw.rectangle([photo_x, photo_y, photo_x+100, photo_y+120], fill='#f1f5f9', outline='#1e293b', width=2)
        draw.text((photo_x+10, photo_y+50), "PHOTO", fill='#64748b', font=font_text)

    # 4. Ajout des informations texte
    info_x = 140
    draw.text((info_x, 70), f"Nom: {student['last_name']}", fill='#1e293b', font=font_text)
    draw.text((info_x, 95), f"Prénom: {student['first_name']}", fill='#1e293b', font=font_text)
    draw.text((info_x, 120), f"Matricule: {student['matricule']}", fill='#1e293b', font=font_text)
    draw.text((info_x, 145), f"Classe: {student['class_name']}", fill='#1e293b', font=font_text)
    
    # Année scolaire en bas
    draw.text((20, 210), "Année Scolaire: 2024-2025", fill='#64748b', font=font_small)
    
    # 5. Coller le QR Code en bas à droite
    qr_img = qr_img.resize((70, 70))
    card.paste(qr_img, (310, 170))
    
    # Sauvegarder dans un tampon mémoire
    buffer = BytesIO()
    card.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer

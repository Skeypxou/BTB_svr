# utils/excel_handler.py
import pandas as pd
import io

def export_to_excel(data, sheet_name="Export"):
    """Convertit une liste de dictionnaires en fichier Excel binaire."""
    if not data:
        return None
    
    df = pd.DataFrame(data)
    
    # Créer un tampon mémoire pour le fichier Excel
    buffer = io.BytesIO()
    
    # Écrire le DataFrame dans le tampon avec OpenPyxl
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        
    buffer.seek(0)
    return buffer

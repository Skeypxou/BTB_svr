# utils/auth.py
import bcrypt
from database.database import fetch_query

def verify_user(username, password):
    """
    Vérifie si l'utilisateur existe et si le mot de passe est correct.
    Retourne les infos de l'utilisateur si OK, sinon None.
    """
    # On cherche l'utilisateur par son nom dans la base de données
    query = """
        SELECT u.id, u.username, u.password_hash, r.name as role_name 
        FROM users u
        JOIN roles r ON u.role_id = r.id
        WHERE u.username = ? AND u.is_active = 1
    """
    user = fetch_query(query, (username,))

    if user:
        user = user[0] # Récupère la première ligne (l'utilisateur)
        # On convertit le mot de passe tapé en bytes, et on le compare au hash de la DB
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return user # Connexion réussie !
    
    return None # Échec de la connexion

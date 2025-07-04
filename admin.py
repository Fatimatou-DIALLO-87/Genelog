import sqlite3
import hashlib

# Fonction pour hasher un mot de passe
def hasher_mot_de_passe(mot_de_passe):
    return hashlib.sha256(mot_de_passe.encode()).hexdigest()

# Fonction pour créer la base de données et la table associée
def creation():
    conn = sqlite3.connect("admin.db")
    c = conn.cursor()

    # Création de la table avec un champ password adapté au hash (64 caractères pour SHA-256)
    c.execute("""
        CREATE TABLE IF NOT EXISTS USERS (
            login VARCHAR(20) UNIQUE,
            password VARCHAR(64),
            mail VARCHAR(50)
        )
    """)

    # Validation et fermeture
    conn.commit()
    conn.close()

# Fonction pour la connexion (vérifier si le login et le mot de passe sont valides)
def connexion(login, password):
    conn = sqlite3.connect("admin.db")
    c = conn.cursor()

    # Hash du mot de passe pour la comparaison
    hash_psw = hasher_mot_de_passe(password)

    c.execute("SELECT * FROM USERS WHERE login=? AND password=?", (login, hash_psw))
    result = c.fetchone()

    conn.close()
    return result

# Fonction pour vérifier si un compte existe avec le login
def verifier_compte(login):
    conn = sqlite3.connect("admin.db")
    c = conn.cursor()

    c.execute("SELECT * FROM USERS WHERE login=?", (login,))
    result = c.fetchone()

    conn.close()
    return result

# Fonction pour l'ajout d'un compte (avec hachage du mot de passe)
def insertion(login, psw, mail):
    conn = sqlite3.connect("admin.db")
    c = conn.cursor()

    # Hash du mot de passe avant l'insertion
    hash_psw = hasher_mot_de_passe(psw)

    # Requête d'insertion avec le mot de passe haché
    c.execute("""
        INSERT INTO USERS (login, password, mail)
        VALUES (?, ?, ?)
    """, (login, hash_psw, mail))

    # Validation et fermeture de la connexion
    conn.commit()
    conn.close()

import sqlite3


#Fonction pour créer la base de données et les tables
def initialiser_base_de_donnees(login):
   
    chemin_db = f"comptes/{login}.db" 
    conn = sqlite3.connect(chemin_db)
    c = conn.cursor()

    # Activer la gestion des clés étrangères
    c.execute("PRAGMA foreign_keys = ON;")

    # Création de la table Individu
    c.execute("""
        CREATE TABLE IF NOT EXISTS Individu (
            id_individu INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            prenom TEXT,
            sexe TEXT,
            date_naissance TEXT,
            lieu_naissance TEXT,
            id_famille_issue INTEGER,
            ids_famille_formes TEXT,
            occupation TEXT,
            deces TEXT,
            date_deces TEXT,
            lieu_deces TEXT,
            FOREIGN KEY (id_famille_issue) REFERENCES Famille(id_mariage) ON DELETE SET NULL
        )
    """)

    # Création de la table Famille
    c.execute("""
        CREATE TABLE IF NOT EXISTS Famille (
            id_mariage INTEGER PRIMARY KEY AUTOINCREMENT,
            date_mariage TEXT,
            lieu_mariage TEXT,
            divorce TEXT,
            date_divorce TEXT,
            id_conjoint INTEGER,
            id_conjointe INTEGER,
            ids_enfants TEXT,
            FOREIGN KEY (id_conjoint) REFERENCES Individu(id_individu) ON DELETE SET NULL,
            FOREIGN KEY (id_conjointe) REFERENCES Individu(id_individu) ON DELETE SET NULL
        )
    """)

    # Validation et fermeture
    conn.commit()
    conn.close()
    
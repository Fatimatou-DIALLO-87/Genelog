from tkinter import *
from admin import *
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
from famille import Famille
import sqlite3  
from individu import Individu

#Fonction principale pour ajout de famille
def ajouter_famille(content, login, afficher_accueil):
    # Vérifier si la fenêtre n'a pas été détruite avant de créer un nouveau widget
    if content.winfo_exists():
        # Ajouter un label pour l'ajout d'une famille
        Label(content, text="Ajouter une famille", font=("Helvetica", 18), bg="#f5f5f5").pack(pady=(30, 0))
    
        # Connexion à la base de données
        login = f"comptes/{login}.db" 
        conn = sqlite3.connect(login)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM Individu")
        result = c.fetchone()

        if result[0] == 0:  # Si la table Individu est vide
            # Détruire tous les widgets existants dans content
            for widget in content.winfo_children():
                widget.destroy()

            # Ajouter un label pour inviter l'utilisateur à ajouter la première famille
            Label(content, text="Ajouter votre première famille", font=("Helvetica", 18), bg="#f5f5f5").pack(pady=(30, 0))

            # Appeler la méthode pour ajouter la première famille
            Famille.ajouter_premiere_famille(login, content, afficher_accueil)

        else: 
            # Détruire tous les widgets existants dans content
            for widget in content.winfo_children():
                widget.destroy()

            # Ajouter un label pour l'ajout d'une famille
            Label(content, text="Ajout d'une famille", font=("Helvetica", 18), bg="#f5f5f5").pack(pady=(30, 0))

            Label(content, text="Voulez vous ajouter par rapport à: ", font=("Helvetica", 15), fg="#41B77F" ).pack(pady=10)

            # Bouton 1
            Button(content, text="Un individu", font=("Arial", 15), width=30, fg="black", bg="#CCCCCC", cursor="hand2",
                   command=lambda: Individu.afficher_recherche_individu(login, content, traiter_selection)).pack(pady=10)

            # Bouton 2
            Button(content, text="Deux Individu", font=("Arial", 15), width=30, fg="black", bg="#CCCCCC", cursor="hand2",
                   command=lambda: Individu.afficher_recherche_deux_individus(login, content, traiter_selection2)).pack(pady=10)

            # Bouton 3
            Button(content, text="Ajouter des parents à un individu", width=30, font=("Arial", 15), fg="black", bg="#CCCCCC", cursor="hand2",
                   command=lambda: Individu.afficher_recherche_individu(login, content, traiter_selction3)).pack(pady=10)



    # Traitement pour ajouter une famille à un seul individu
    def traiter_selection(individu):
        Famille.ajouter_famille_a_un_individu(login, content, individu, lambda: Individu.afficher_recherche_individu(login, content, traiter_selection), afficher_accueil)
    
    #Traitement pour ajouter une famille à deux individu
    def traiter_selection2(conjoint1, conjoint2):
        Famille.ajouter_famille_a_deux_individu(login, content, conjoint1, conjoint2, lambda: Individu.afficher_recherche_deux_individus(login, content, traiter_selection2), afficher_accueil)


    #Traitement pour ajouter des parents à un individu
    def traiter_selction3(enfant):
        id = enfant.id_individu

        conn = sqlite3.connect(login)
        c = conn.cursor()
        c.execute("SELECT id_famille_issue FROM Individu WHERE id_individu = ?", (id,))
        id_famille_issue = c.fetchone()
        conn.close()

        if id_famille_issue[0]:
            messagebox.showerror("Erreur", "Cet individu a déjà des parents enregistrés.")
            return
        else:
            Famille.ajouter_parents(login, content, enfant, lambda: Individu.afficher_recherche_individu(login, content, traiter_selction3), afficher_accueil)
        
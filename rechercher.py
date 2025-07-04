from tkinter import *
from admin import *
from famille import Famille
from individu import Individu

#Fonction principal pour la recherche d'une famille ou d'un individu
def rechercher(content, login):
    login = f"comptes/{login}.db" 
 # Détruire tous les widgets existants dans content
    for widget in content.winfo_children():
        widget.destroy()

    # Ajouter un label pour l'ajout d'une famille
    Label(content, text="Recherche", font=("Helvetica", 18), bg="#f5f5f5").pack(pady=(30, 0))

    Label(content, text="Voulez-vous rechercher: ", font=("Helvetica", 15), fg="#41B77F" ).pack(pady=10)

    # Bouton 1
    Button(content, text="Une Famille", font=("Arial", 15), width=30, fg="black", bg="#CCCCCC", cursor="hand2",
           command=lambda: Famille.afficher_recherche_famille(login, content,traiter_recherche_famille)).pack(pady=10)

    # Bouton 2
    Button(content, text="Un Individu", font=("Arial", 15), width=30, fg="black", bg="#CCCCCC", cursor="hand2",
           command=lambda: Individu.afficher_recherche_individu(login, content, traiter_recherche_individu)).pack(pady=10)


    #Fonction pour traité la famille recherchée
    def traiter_recherche_famille(famille):
        Famille.afficher_famille(login, content, famille, lambda: Famille.afficher_recherche_famille(login,content,traiter_recherche_famille))
    

    #Fonction pour traité un individu recherchée
    def traiter_recherche_individu(individu):
        Individu.afficher_individu(login, content, individu, lambda: Individu.afficher_recherche_individu(login, content, traiter_recherche_individu))
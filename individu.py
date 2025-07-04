import sqlite3
import os
import math
import datetime
from tkinter import *
from admin import *
from tkinter import ttk
from tkinter.font import Font
from tkinter import messagebox
from datetime import datetime



class Individu:
    def __init__(self, id_individu, nom, prenom=None, sexe=None, date_naissance=None, lieu_naissance=None,
                 occupation=None, deces="Non", date_deces=None, lieu_deces=None, ids_famille_formes=None):
        self.id_individu = id_individu
        self.nom = nom
        self.prenom = prenom
        self.sexe = sexe
        self.date_naissance = date_naissance
        self.lieu_naissance = lieu_naissance
        self.occupation = occupation
        self.deces = deces
        self.date_deces = date_deces
        self.lieu_deces = lieu_deces
        self.ids_famille_formes = ids_famille_formes if ids_famille_formes else []
        
    #Methode pour saisir les informations du(de la) conjoint(e)
    @staticmethod
    def saisir_conjoint_e(frame,  callback=None, nom=None):
        from tkinter import StringVar, Label, Entry, Button, Frame

        nom_var = StringVar(value=nom if nom else "")
        prenom_var = StringVar()
        dateN_var = StringVar()
        lieuN_var = StringVar()
        occupation_var = StringVar()
        deces_var = StringVar(value="non")
        dateDeces_var = StringVar()
        lieuDeces_var = StringVar()

        #Fonction qui teste la validité des champs
        def valider():

            if nom_var.get().strip() == "":
                messagebox.showerror("Erreur","Le nom est requis")
                return
            if len(nom_var.get()) > 20:
                messagebox.showerror("Erreur", "Le nom doit contenir max au : 20 caractères")
                return
            if len(prenom_var.get()) > 30:
                messagebox.showerror("Erreur", "Le prénom doit contenir au max : 30 caractères")
                return
            if len(lieuN_var.get()) > 20:
                messagebox.showerror("Erreur", "Le lieu de naissance doit contenir au max : 20 caractères")
                return
            if len(lieuDeces_var.get()) > 20:
                messagebox.showerror("Erreur", "Le lieu du decès doit contenir max au : 20 caractères")
                return

            
            # Vérification de la validité de la date de naissance
            if dateN_var.get() != "" and not Individu.date_valide(dateN_var.get()):
                messagebox.showerror("Erreur", "Veuillez saisir une date de naissance valide.")
                return
            
            # Vérification de la validité de la date de naissance
            if dateDeces_var.get() != "" and not Individu.date_valide(dateDeces_var.get()):
                messagebox.showerror("Erreur", "Veuillez saisir une date de décès valide.")
                return
            
             #verification des dates (décès et naissance)
            if dateDeces_var.get() != "" and dateN_var.get() != "" and not Individu.date_coherente(dateN_var.get(),dateDeces_var.get()):
                messagebox.showerror("Erreur","on ne peut mourir avant d'avoir veçu")
                return
            
            #verification si l'individu peut se marier
            if dateN_var.get() != "" and not Individu.peut_se_marier(dateN_var.get(), 15):
                messagebox.showerror("Erreur","Cet individu n'a pas l'âge requis pour ce marier. Pensez à bien vérifier la date de naissance")
                return
            
            #verification des dates (décès et naissance) max = 150
            if  dateN_var.get() != "" and dateDeces_var.get() != "" and Individu.difference_annees(dateN_var.get(), dateDeces_var.get(), 150):
                messagebox.showerror("Erreur","Ce n'est pas logique d'avoir plus de 150 ans")
                return
            
            #Création de l'individu
            individu = Individu(
                "", 
                nom_var.get(), 
                prenom_var.get(), 
                "", 
                dateN_var.get(), 
                lieuN_var.get(), 
                occupation_var.get(), 
                deces_var.get().lower(), 
                dateDeces_var.get() if deces_var.get().lower() == "oui" else "", 
                lieuDeces_var.get() if deces_var.get().lower() == "oui" else ""
            )
            if callback:
                callback(individu)

        def champ(label_text, text_var):
            ligne = Frame(frame)
            ligne.pack(anchor="center", pady=5)  
            Label(ligne, text=label_text, width=26, anchor="w").pack(side="left", padx=10)  
            Entry(ligne, textvariable=text_var, width=30).pack(side="left", padx=10)


        champ("Nom* :", nom_var)
        champ("Prénom :", prenom_var)
        champ("Date de naissance (JJ/MM/AAAA) :", dateN_var)
        champ("Lieu de naissance :", lieuN_var)
        champ("Occupation :", occupation_var)
        champ("Décédé ? (oui/non) :", deces_var)

        # Ces labels s'affichent si applicable
        ligne_date_deces = Frame(frame)
        Label(ligne_date_deces, text="Date de décès :", width=26, anchor="w").pack(side="left", padx=10)
        entry_date_deces = Entry(ligne_date_deces, textvariable=dateDeces_var, width=30)
        entry_date_deces.pack(side="left", padx=10)

        ligne_lieu_deces = Frame(frame)
        Label(ligne_lieu_deces, text="Lieu de décès :", width=26, anchor="w").pack(side="left", padx=10)
        entry_lieu_deces = Entry(ligne_lieu_deces, textvariable=lieuDeces_var, width=30)
        entry_lieu_deces.pack(side="left", padx=10)

        # Bouton de validation
        bouton_valider = Button(frame, text="Valider", bg="#41B77F", command=valider)
        bouton_valider.pack(pady=10)

        def toggle_deces(*args):
            ligne_date_deces.pack_forget()
            ligne_lieu_deces.pack_forget()

            if deces_var.get().lower() == "oui":
                ligne_date_deces.pack(anchor="center", pady=5, before=bouton_valider)
                ligne_lieu_deces.pack(anchor="center", pady=5, before=bouton_valider)

        # Suivi du champ "Décédé"
        deces_var.trace_add("write", toggle_deces)
        toggle_deces()


    #Methode pour saisir les informations d'un enfant
    @staticmethod
    def saisir_enfant(frame, nom_enfant, callback=None):
        # Variables de saisie
        nom_var = StringVar(value=nom_enfant or "")
        prenom_var = StringVar()
        sexe_var = StringVar()
        dateN_var = StringVar()
        lieuN_var = StringVar()
        occupation_var = StringVar()
        deces_var = StringVar(value="non")
        dateDeces_var = StringVar()
        lieuDeces_var = StringVar()

        def valider():
             # Vérification du nombres de caracteres dans les differents champs
            if len(nom_var.get()) > 20:
                messagebox.showerror("Erreur", "Le nom doit contenir au max : 20 caractères")
                return
            if len(prenom_var.get()) > 30:
                messagebox.showerror("Erreur", "Le prénom doit contenir au max : 30 caractères")
                return
            if len(lieuN_var.get()) > 20:
                messagebox.showerror("Erreur", "Le lieu de naissance doit contenir au max : 20 caractères")
                return
            if len(lieuDeces_var.get()) > 20:
                messagebox.showerror("Erreur", "Le lieu du decès doit contenir au max: 20 caractères")
                return
            

            # Vérification de la validité de la date
            if dateN_var.get() != "" and not Individu.date_valide(dateN_var.get()):
                messagebox.showerror("Erreur", "Veuillez saisir une date de naissance valide.")
                return
            
            # Verirification du sexe de l'enfant
            if sexe_var.get().strip().upper() not in ["M", "F"]:
                messagebox.showerror("Erreur", "Veuillez saisir le sexe de l'enfant: M ou F")
                return
            
            # Vérification de la validité de la date
            if dateDeces_var.get() != "" and not Individu.date_valide(dateDeces_var.get()):
                messagebox.showerror("Erreur", "Veuillez saisir une date de décès valide.")
                return
            
            #verification des dates 
            if dateDeces_var.get() != "" and dateN_var.get() != "" and not Individu.date_coherente(dateN_var.get(),dateDeces_var.get()):
                messagebox.showerror("Erreur","on ne peut mourir avant d'avoir veçu")
                return
            
            #verification des dates
            if  dateN_var.get() != "" and dateDeces_var.get() != "" and Individu.difference_annees(dateN_var.get(), dateDeces_var.get(), 150):
                messagebox.showerror("Erreur","Ce n'est pas logique d'avoir plus de 150 ans")
                return
            
            #Création de l'individu
            individu = Individu(
                "", 
                nom_var.get(), 
                prenom_var.get(), 
                sexe_var.get().upper(), 
                dateN_var.get(), 
                lieuN_var.get(), 
                occupation_var.get(), 
                deces_var.get().lower(), 
                dateDeces_var.get() if deces_var.get().lower() == "oui" else "", 
                lieuDeces_var.get() if deces_var.get().lower() == "oui" else ""
            )

            if callback:
                callback(individu)

        def champ(label_text, text_var):
            ligne = Frame(frame)
            ligne.pack(anchor="center", pady=5)
            Label(ligne, text=label_text, width=26, anchor="w").pack(side="left", padx=10)
            Entry(ligne, textvariable=text_var, width=30).pack(side="left", padx=10)

        champ("Nom :", nom_var)
        champ("Prénom :", prenom_var)
        champ("Sexe (M/F)* :", sexe_var)
        champ("Date de naissance (JJ/MM/AAAA) :", dateN_var)
        champ("Lieu de naissance :", lieuN_var)
        champ("Occupation :", occupation_var)
        champ("Décédé ? (oui/non) :", deces_var)

        # Champs conditionnels (date et lieu de décès)
        ligne_date_deces = Frame(frame)
        Label(ligne_date_deces, text="Date de décès :", width=26, anchor="w").pack(side="left", padx=10)
        entry_date_deces = Entry(ligne_date_deces, textvariable=dateDeces_var, width=30)
        entry_date_deces.pack(side="left", padx=10)

        ligne_lieu_deces = Frame(frame)
        Label(ligne_lieu_deces, text="Lieu de décès :", width=26, anchor="w").pack(side="left", padx=10)
        entry_lieu_deces = Entry(ligne_lieu_deces, textvariable=lieuDeces_var, width=30)
        entry_lieu_deces.pack(side="left", padx=10)

        # Bouton de validation
        bouton_valider = Button(frame, text="Valider", bg="#41B77F", command=valider)
        bouton_valider.pack(pady=10)

        def toggle_deces(*args):
            ligne_date_deces.pack_forget()
            ligne_lieu_deces.pack_forget()

            if deces_var.get().lower() == "oui":
                ligne_date_deces.pack(anchor="center", pady=5, before=bouton_valider)
                ligne_lieu_deces.pack(anchor="center", pady=5, before=bouton_valider)

        # Suivi du champ "Décédé "
        deces_var.trace_add("write", toggle_deces)
        toggle_deces()


    #Methode qui vérifie la validité de la date
    @staticmethod
    def date_valide(date_text: str) -> bool:
        formats = ['%d/%m/%Y', '%m/%Y', '%Y']
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_text, fmt)

                # On complète les dates partielles pour la comparaison
                if fmt == '%Y':
                    parsed_date = parsed_date.replace(month=1, day=1)
                elif fmt == '%m/%Y':
                    parsed_date = parsed_date.replace(day=1)

                #Vérifier si la date ne dépasse pas la date du jour
                if parsed_date > datetime.today():
                    return False  
                return True
            except ValueError:
                continue
        return False
    

    #Methode qui vérifie la coherence des dates
    @staticmethod
    def date_coherente(date1: str, date2: str) -> bool:
        formats = ['%d/%m/%Y', '%m/%Y', '%Y']

        def parser(date_str):
            for fmt in formats:
                try:
                    d = datetime.strptime(date_str, fmt)
                    # Compléter avec des valeurs par défaut pour les comparaisons
                    if fmt == '%Y':
                        d = d.replace(month=1, day=1)
                    elif fmt == '%m/%Y':
                        d = d.replace(day=1)
                    return d
                except ValueError:
                    continue
            return None  # En théorie jamais None car date_valide a déjà filtré

        d1 = parser(date1)
        d2 = parser(date2)

        return d1 <= d2
    

    #Methode qui vérifie si l'individu à l'âge requis pour se marier
    @staticmethod
    def peut_se_marier(date_naissance: str, age_min: int) -> bool:
       
        formats = ["%Y", "%m/%Y", "%d/%m/%Y"]
        today = datetime.today()

        for fmt in formats:
            try:
                naissance = datetime.strptime(date_naissance, fmt)

                # Completer la date donnée 
                if fmt == "%Y":
                    naissance = naissance.replace(month=1, day=1)
                elif fmt == "%m/%Y":
                    naissance = naissance.replace(day=1)

                age = today.year - naissance.year - ((today.month, today.day) < (naissance.month, naissance.day))
                return age >= age_min
            except ValueError:
                continue
        return False  # Aucun format valide
    
    #Methode qui vérifie la difference d'annees entre deux dates
    @staticmethod
    def difference_annees(date1: str, date2: str, age_min: int) -> bool:
        
        #Les formats acceptés : YYYY, MM/YYYY, DD/MM/YYYY.
        formats = ["%Y", "%m/%Y", "%d/%m/%Y"]

        def parser(date_str):
            for fmt in formats:
                try:
                    date = datetime.strptime(date_str, fmt)
                    # On Complète les dates partielles avec 1er mois ou 1er jour
                    if fmt == "%Y":
                        date = date.replace(month=1, day=1)
                    elif fmt == "%m/%Y":
                        date = date.replace(day=1)
                    return date
                except ValueError:
                    continue
            return None

        d1 = parser(date1)
        d2 = parser(date2)

        if not d1 or not d2:
            return False  # Si une des deux dates est invalide

        diff = d2.year - d1.year
        return diff >= age_min



    # Méthode pour ajouter un individu à la base de données
    def ajouter_individu(self, login):
        conn = sqlite3.connect(login)
        c = conn.cursor()  

        # Requête SQL pour insérer un individu dans la table Individu
        c.execute("""
            INSERT INTO Individu (nom, prenom, sexe, date_naissance, lieu_naissance, occupation, deces, date_deces, lieu_deces, ids_famille_formes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.nom, self.prenom, self.sexe, self.date_naissance,
            self.lieu_naissance, self.occupation, self.deces,
            self.date_deces, self.lieu_deces,
            ",".join(map(str, self.ids_famille_formes))  # Conversion de la liste en chaîne séparée par virgules
        ))

        # Récupération de l'identifiant
        self.id_individu = c.lastrowid

        conn.commit()
        conn.close()

    #------------------------------------------------------------------------------------------------------------

    # Fonction pour afficher une recherche d'un individu 
    def afficher_recherche_individu(login, frame, callback_selection):
        # Suppression de tous les widgets enfants dans le frame pour le réinitialiser
        for widget in frame.winfo_children():
            widget.destroy()

        # Titre et sous-titre de la section
        Label(frame, text="Rechercher un individu", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=(20, 10))
        Label(frame, text="Rechercher en fonction du nom ou du prenom", font=("Helvetica", 10, "normal"), bg="#f5f5f5").pack(pady=(0, 10))

        # Variable liée au champ de recherche
        search_var = StringVar()
        search_entry = Entry(frame, textvariable=search_var, font=("Helvetica", 12), width=40)
        search_entry.pack(pady=5)

        # Cadre contenant la liste des résultats et une barre de défilement
        listbox_frame = Frame(frame, width=600, height=300)
        listbox_frame.pack(pady=10, padx=10)

        listbox = Listbox(listbox_frame, width=50, font=("Helvetica", 11), height=20)
        listbox.pack(side="left", fill="both", expand=True)

        # Barre de défilement verticale pour la listbox
        scrollbar = Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.config(yscrollcommand=scrollbar.set)

        # Liste pour stocker les résultats de recherche
        individus_resultats = []

        # Fonction qui s'execute lorsqu’on tape dans le champ de recherche
        def update_list(*args):
            query = search_var.get().lower()  
            listbox.delete(0, END)           
            individus_resultats.clear()       

            conn = sqlite3.connect(login)
            c = conn.cursor()

            c.execute("""
                SELECT id_individu, nom, prenom, sexe, date_naissance, lieu_naissance,
                    id_famille_issue, ids_famille_formes, occupation, deces, date_deces, lieu_deces
                FROM Individu
            """)

            for row in c.fetchall():
                if len(row) >= 12:
                    id_individu, nom, prenom, sexe, date_naissance, lieu_naissance, \
                    id_famille_issue, ids_famille_formes, occupation, deces, date_deces, lieu_deces = row

                    # Concatène nom et prénom pour permettre une recherche simple
                    full_name = f"{prenom} {nom}".lower()
                    if query in full_name:
                        individus_resultats.append(row)  # Ajoute à la liste des résultats
                        listbox.insert(END, f"{prenom} {nom} ({date_naissance})")  # Affiche dans la listbox

            conn.close()  

        # Fonction qui s'execute lorsqu’un utilisateur sélectionne un individu dans la listbox
        def on_select(event):
            index = listbox.curselection()
            if index:
                row = individus_resultats[index[0]]  # Récupère les infos de l’individu sélectionné
                individu = Individu(
                    id_individu=row[0],
                    nom=row[1],
                    prenom=row[2],
                    sexe=row[3],
                    date_naissance=row[4],
                    lieu_naissance=row[5],
                    ids_famille_formes=row[7],
                    occupation=row[8],
                    deces=row[9],
                    date_deces=row[10],
                    lieu_deces=row[11],
                )
                callback_selection(individu)

        # Fonction pour l’élément survolé
        def on_hover(event):
            index = listbox.nearest(event.y)  # Récupère l'élément le plus proche du curseur
            if index >= 0:
                for i in range(listbox.size()):
                    listbox.itemconfig(i, {'bg': 'white'})  # Réinitialise toutes les couleurs
                listbox.itemconfig(index, {'bg': '#d3d3d3'})  # Surligne l'élément

        # Fonction qui supprime le survolement quand on quitte la listbox
        def on_leave(event):
            index = listbox.nearest(event.y)
            if index >= 0:
                listbox.itemconfig(index, {'bg': 'white'})

        # Liaison des événements : mouvement souris, clic, modification texte
        listbox.bind("<Motion>", on_hover)
        listbox.bind("<Leave>", on_leave)
        search_var.trace("w", update_list)  # À chaque modification du champ de recherche, on met à jour
        listbox.bind("<<ListboxSelect>>", on_select)

        # Donne le focus au champ de recherche à l’ouverture
        search_entry.focus_set()


    #------------------------------------------------------------------------------------------------------------

    #Fonction pour rechercher deux individus
    def afficher_recherche_deux_individus(login, frame, callback_selection):
        # Nettoyer le frame
        for widget in frame.winfo_children():
            widget.destroy()

        Label(frame, text="Rechercher un individu", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=(20, 10))
        Label(frame, text="Rechercher en fonction du nom ou du prenom", font=("Helvetica", 10, "normal"), bg="#f5f5f5").pack(pady=(0, 10))

        search_var = StringVar()
        search_entry = Entry(frame, textvariable=search_var, font=("Helvetica", 12), width=40)
        search_entry.pack(pady=5)

        # Frame pour la liste des résultats
        listbox_frame = Frame(frame, width=600, height=300)
        listbox_frame.pack(pady=10, padx=10)

        listbox = Listbox(listbox_frame, width=50, font=("Helvetica", 11), height=20)
        listbox.pack(side="left", fill="both", expand=True)

        scrollbar = Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.config(yscrollcommand=scrollbar.set)

        individus_resultats = []
        individu_selectionne_1 = [None] 

        bouton_suivant = None  # Pour permettre la reconfiguration

        def update_list(*args):
            query = search_var.get().lower()
            listbox.delete(0, END)
            individus_resultats.clear()

            conn = sqlite3.connect(login)
            c = conn.cursor()
            c.execute("SELECT * FROM Individu")
            for row in c.fetchall():
                if len(row) >= 12:
                    id_individu, nom, prenom, sexe, date_naissance, lieu_naissance, \
                    id_famille_issue, ids_famille_formes, occupation, deces, date_deces, lieu_deces = row

                    full_name = f"{prenom} {nom}".lower()
                    if query in full_name:
                        individus_resultats.append(row)
                        listbox.insert(END, f"{prenom} {nom} ({date_naissance})")
            conn.close()

        def on_select(event):
            nonlocal bouton_suivant

            index = listbox.curselection()
            if index:
                row = individus_resultats[index[0]]  # Récupère les infos de l’individu sélectionné
                individu = Individu(
                    id_individu=row[0],
                    nom=row[1],
                    prenom=row[2],
                    sexe=row[3],
                    date_naissance=row[4],
                    lieu_naissance=row[5],
                    ids_famille_formes=row[7],
                    occupation=row[8],
                    deces=row[9],
                    date_deces=row[10],
                    lieu_deces=row[11],
                )

                if individu_selectionne_1[0] is None:
                    #Verifier si l'individu à au moins 15ans
                    if individu.date_naissance != "" and not Individu.peut_se_marier(individu.date_naissance, 15):
                        messagebox.showerror("Erreur", "Cet individu n'a pas l'âge requit pour se marier (Il faut au moins 15 ans)")
                        return
                    
                    individu_selectionne_1[0] = individu
                    
                    search_var.set("")
                    listbox.delete(0, END)
                    individus_resultats.clear()

                    Label(frame, text="Premier individu sélectionné : " +
                        f"{individu.prenom} {individu.nom}", bg="#f5f5f5", fg="green", font=("Helvetica", 12),  wraplength=400, justify="center").pack()

                    Label(frame, text="Recherchez maintenant le deuxième individu...", bg="#f5f5f5", font=("Helvetica", 12)).pack(pady=(20, 5))
                else:

                    if individu_selectionne_1[0].id_individu == individu.id_individu:
                        messagebox.showerror("Erreur", "Vous ne pouvez pas choisir un meme individu")
                        return
                    if individu_selectionne_1[0].sexe == individu.sexe:
                        messagebox.showerror("Erreur", "Vous ne pouvez pas marier deux individus de meme sexe")
                        return
                    
                    if individu_selectionne_1[0].sexe == "M" and individu.sexe == "F":
                        conn = sqlite3.connect(login)
                        c = conn.cursor()
                        c.execute("SELECT id_mariage FROM Famille WHERE id_conjoint = ? and id_conjointe = ?", (individu_selectionne_1[0].id_individu, individu.id_individu))
                        result = c.fetchone()
                        c.close()
                        if result:
                            messagebox.showerror("Erreur", "Ces deux individus se sont déjà mariés. Pensez à modifier leur famille")
                            return

                    if individu_selectionne_1[0].sexe == "F" and individu.sexe == "M":
                        conn = sqlite3.connect(login)
                        c = conn.cursor()
                        c.execute("SELECT id_mariage FROM Famille WHERE id_conjointe = ? and id_conjoint = ?", (individu_selectionne_1[0].id_individu, individu.id_individu))
                        result = c.fetchone()
                        c.close()
                        if result:
                            messagebox.showerror("Erreur", "Ces deux individus se sont déjà mariés.")
                            return
            
                    individu_selectionne_2 = individu
                    callback_selection(individu_selectionne_1[0], individu_selectionne_2)
            
        def on_hover(event):
            # Récupérer l'index de l'élément survolé
            index = listbox.nearest(event.y)

            if index >= 0:
                # Rétablir la couleur de fond de toutes les lignes
                for i in range(listbox.size()):
                    listbox.itemconfig(i, {'bg': 'white'})  # Remettre la couleur d'origine (blanc)

                # Modifier la couleur de fond de la ligne survolée
                listbox.itemconfig(index, {'bg': '#d3d3d3'})  # Couleur de survol (gris clair)

        def on_leave(event):
            # Récupérer l'index de l'élément quitté
            index = listbox.nearest(event.y)

            # Vérifier si l'index est valide
            if index >= 0:
                # Rétablir la couleur de fond de la ligne quittée
                listbox.itemconfig(index, {'bg': 'white'})  # Remettre la couleur d'origine (blanc)
        
         # Associer les événements de survol et de sortie à la Listbox
        listbox.bind("<Motion>", on_hover)  # Survol de la souris sur la Listbox
        listbox.bind("<Leave>", on_leave)  # Sortie du survol de la souris


        listbox.bind("<<ListboxSelect>>", on_select)

        # Suivre la recherche pour mettre à jour la liste
        search_var.trace_add("write", update_list)

        # Focus directement dans le champ de recherche
        search_entry.focus_set()

    #------------------------------------------------------------------------------------------------------------

    #Fonction pour afficher les informations d'un individu
    def afficher_individu(login, frame, individu: 'Individu', callback_retour):
        # Nettoyer le frame
        for widget in frame.winfo_children():
            widget.destroy()

        frame.config(bg="#f5f5f5")

        Label(frame, text="Détails de l'individu", font=("Helvetica", 18, "bold"), bg="#f5f5f5").pack(pady=20)

        # Affichage des infos
        info_frame = Frame(frame, bg="#f5f5f5")
        info_frame.pack(pady=10)

        infos = [
            ("Nom :", individu.nom or "Non renseigné"),
            ("Prénom :", individu.prenom or "Non renseigné"),
            ("Sexe :", "Masculin" if individu.sexe == "M" else "Féminin"),
            ("Date de Naissance :", individu.date_naissance or "Non renseignée"),
            ("Lieu de Naissance :", individu.lieu_naissance or "Non renseignée"),
            ("Occupation :", individu.occupation or "Non renseignée"),
            ("Décédé(e) :", "Oui" if (individu.deces == "oui") else "Non"),
        ]

        if individu.deces == "oui":
            infos.append(("Date de décès :", individu.date_deces or "Non renseignée"))
            infos.append(("Lieu de décès :", individu.lieu_deces or "Non renseigné"))

        for label, value in infos:
            
            ligne_frame = Frame(info_frame, bg="#f5f5f5")
            ligne_frame.pack(anchor="w", pady=2)

            Label(ligne_frame, text=label, font=("Helvetica", 12, "bold"), bg="#f5f5f5").pack(side="left")
            Label(ligne_frame, text=value, font=("Helvetica", 12), bg="#f5f5f5", wraplength=400, justify="center").pack(side="left")
        

        button_frame = Frame(frame, bg="#f5f5f5")
        button_frame.pack(pady=20)

        Button(button_frame, text="Retour", command=callback_retour, bg="#123", fg="white").pack(side="left", padx=10)
        Button(button_frame, text="Voir options", command=lambda: Individu.modifier_individu(login, frame, individu, callback_retour), bg="#41B77F", fg="white").pack(side="left", padx=10)


    #Fonction qui recherche un individu
    @staticmethod
    def rechercher_par_id(id_individu, login):
        import sqlite3
        conn = sqlite3.connect(login)
        c = conn.cursor()
        c.execute("SELECT * FROM Individu WHERE id_individu = ?", (id_individu,))
        row = c.fetchone()
        conn.close()
        if row:
            return Individu(
                    id_individu=row[0],
                    nom=row[1],
                    prenom=row[2],
                    sexe=row[3],
                    date_naissance=row[4],
                    lieu_naissance=row[5],
                    ids_famille_formes=row[7],
                    occupation=row[8],
                    deces=row[9],
                    date_deces=row[10],
                    lieu_deces=row[11],
                )
        return None


    #Fontion pour gerer un individu recherché
    def modifier_individu(login, frame, individu: 'Individu', callback_retour):

        #recuperer l'individu
        individu = Individu.rechercher_par_id(individu.id_individu, login)

          # Nettoyer le frame
        for widget in frame.winfo_children():
            widget.destroy()
        
        nom = "("+individu.prenom + " "+ individu.nom+")"
        Label(frame, text="Effectuer une action:", font=("Helvetica", 18, "bold"), bg="#f5f5f5").pack(pady=20)
        Label(frame, text=nom, font=("Helvetica", 18, "bold"), fg="#41B77F",  wraplength=400, justify="center").pack(pady=10)

        # Bouton 1
        Button(frame, text="Modifier les informations", font=("Arial", 15), width=30, fg="black", bg="#CCCCCC", cursor="hand2",
               command= lambda: Individu.modifier_info(login,frame,individu, lambda:Individu.modifier_individu(login, frame, individu, callback_retour)) ).pack(pady=10)

        # Bouton 2
        from famille import Famille
        Button(frame, text="Ajouter une famille", font=("Arial", 15), width=30, fg="black", bg="#CCCCCC", cursor="hand2",
               command=lambda: Famille.ajouter_famille_a_un_individu(login, frame, individu, lambda:Individu.modifier_individu(login, frame, individu, callback_retour) , lambda:Individu.modifier_individu(login, frame, individu, callback_retour))).pack(pady=10)

        # Bouton 3
        Button(frame, text="Afficher la/les famille(s)", font=("Arial", 15), width=30, fg="black", bg="#CCCCCC", cursor="hand2",
               command= lambda: Individu.afficher_famille_individu(login,frame,individu, lambda:Individu.modifier_individu(login, frame, individu, callback_retour))).pack(pady=10)

        # Bouton 4
        Button(frame, text="Afficher les ascendants", font=("Arial", 15), width=30, fg="black", bg="#CCCCCC", cursor="hand2",
        command=lambda: Individu.afficher_ascendant(login, frame, individu.id_individu, lambda:Individu.modifier_individu(login, frame, individu, callback_retour))).pack(pady=10)

        #Boutton 5
        Button(frame, text="Afficher les descendants", font=("Arial", 15), width=30, fg="black", bg="#CCCCCC", cursor="hand2",
        command=lambda: Individu.afficher_descendant(login, frame, individu.id_individu, 4, lambda:Individu.modifier_individu(login, frame, individu, callback_retour))).pack(pady=10)

        #Bouton retour
        Button(frame, text="Retour", command=lambda: Individu.afficher_individu(login, frame, individu, callback_retour), bg="#123", fg="white", justify="center").pack(padx=10, pady=10)
    

    # Fonction pour modifier les informations d'un individu
    def modifier_info(login, frame, individu: 'Individu', callback_retour):
        # Nettoyer le frame
        for widget in frame.winfo_children():
            widget.pack_forget()

        frame.config(bg="#f5f5f5")

        # Scrollable Canvas centré 
        canvas = Canvas(frame, bg="#f5f5f5", highlightthickness=0)
        scrollbar = Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.pack(side="left", fill="both", expand=True, padx=(25,30))
        scrollbar.pack(side="right", fill="y")

        scrollable_frame = Frame(canvas, bg="#f5f5f5")
        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        
        def repositionner_scrollable_frame(event):
            canvas_width = event.width
            frame_width = scrollable_frame.winfo_reqwidth()

            x_position = max((canvas_width - frame_width) // 2, 0)  # centrer si possible, sinon 0
            canvas.coords(window_id, x_position, 0)
            canvas.configure(scrollregion=canvas.bbox("all"))


        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", repositionner_scrollable_frame)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Chargement données
        connexion = sqlite3.connect(login)
        connecte = connexion.cursor()
        connecte.execute("SELECT ids_famille_formes FROM Individu WHERE id_individu = ?", (individu.id_individu,))
        id_famille_forme = connecte.fetchone()
        connexion.close()
        a_famille_formee = id_famille_forme and id_famille_forme[0] != ""

        nom_var = StringVar(value=individu.nom or "")
        prenom_var = StringVar(value=individu.prenom or "")
        sexe_var = StringVar(value = "M" if individu.sexe.lower() == "m" else "F")
        occupation_var = StringVar(value=individu.occupation or "")
        date_naiss_var = StringVar(value=individu.date_naissance or "")
        lieu_naiss_var = StringVar(value=individu.lieu_naissance or "")
        deces_var = StringVar(value= "Oui" if individu.deces.lower() == "oui" else "Non")
        date_deces_var = StringVar(value=individu.date_deces or "")
        lieu_deces_var = StringVar(value=individu.lieu_deces or "")

        # Modifier les informations de l'individu 
        Label(scrollable_frame, text="Modifier les informations de l'individu", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(anchor="w", pady=10)

        Label(scrollable_frame, text="Nom :",bg="#f5f5f5",font=("Helvetica", 10)).pack(pady=5)
        Entry(scrollable_frame, textvariable=nom_var, relief="groove", bd=2).pack()

        Label(scrollable_frame, text="Prénom :", bg="#f5f5f5",font=("Helvetica", 10)).pack(pady=5)
        Entry(scrollable_frame, textvariable=prenom_var, relief="groove", bd=2).pack()

        Label(scrollable_frame, text="Date de naissance :", bg="#f5f5f5",font=("Helvetica", 10)).pack(pady=5)
        Entry(scrollable_frame, textvariable=date_naiss_var, relief="groove", bd=2).pack()

        Label(scrollable_frame, text="Lieu de naissance :", bg="#f5f5f5",font=("Helvetica", 10)).pack(pady=5)
        Entry(scrollable_frame, textvariable=lieu_naiss_var, relief="groove", bd=2).pack()

        if not a_famille_formee:
            Label(scrollable_frame, text="Sexe :", bg="#f5f5f5",font=("Helvetica", 10)).pack(pady=5)
            sexe_frame = Frame(scrollable_frame, bg="#f5f5f5")
            sexe_frame.pack()
            Radiobutton(sexe_frame, text="Masculin", variable=sexe_var, value="M", bg="#f5f5f5").pack(side="left", padx=5)
            Radiobutton(sexe_frame, text="Féminin", variable=sexe_var, value="F", bg="#f5f5f5").pack(side="left", padx=5)

        Label(scrollable_frame, text="Occupation :", bg="#f5f5f5",font=("Helvetica", 10)).pack(pady=5)
        Entry(scrollable_frame, textvariable=occupation_var, relief="groove", bd=2).pack()

        Label(scrollable_frame, text="La personne est-elle décédée ?", bg="#f5f5f5",font=("Helvetica", 10)).pack(pady=5)
        deces_frame = Frame(scrollable_frame, bg="#f5f5f5")
        deces_frame.pack()
        Radiobutton(deces_frame, text="Oui", variable=deces_var, value="Oui", bg="#f5f5f5").pack(side="left", padx=5)
        Radiobutton(deces_frame, text="Non", variable=deces_var, value="Non", bg="#f5f5f5").pack(side="left", padx=5)

        deces_details_frame = Frame(scrollable_frame, bg="#f5f5f5")
        deces_details_frame.pack()

        def toggle_deces(*args):
            for widget in deces_details_frame.winfo_children():
                widget.destroy()
            if deces_var.get().lower() == "oui":
                Label(deces_details_frame, text="Date de décès (YYYY-MM-DD) :", bg="#f5f5f5",font=("Helvetica", 10)).pack(pady=(10, 0))
                Entry(deces_details_frame, textvariable=date_deces_var, relief="groove", bd=2).pack()
                Label(deces_details_frame, text="Lieu de décès :", bg="#f5f5f5",font=("Helvetica", 10)).pack(pady=(10, 0))
                Entry(deces_details_frame, textvariable=lieu_deces_var, relief="groove", bd=2).pack()
            
            else:
                date_deces_var.set("")
                lieu_deces_var.set("")

        toggle_deces()
        deces_var.trace("w", toggle_deces)

        frame_button = Frame(scrollable_frame, bg="#f5f5f5")
        frame_button.pack(pady=20)

        def proposer_confirmation():
            #Vérifier si le nom est saisi ou pas
            if nom_var.get().strip() == "":
                messagebox.showerror("Erreur", "Le nom est obligatoire")
                return
            
            #Vérification de la longueur du nom, prenom, lieu de naissance, lieu de deces 
            if len(nom_var.get()) > 20:
                messagebox.showerror("Erreur","Le nom doit avoir au max: 20 caractères")
                return
            
            if len(prenom_var.get()) > 30:
                messagebox.showerror("Erreur","Le prenom doit avoir au max: 30 caractères")
                return
            
            if len(lieu_naiss_var.get()) > 20:
                messagebox.showerror("Erreur", "Le lieu de naissance doit contenir au max : 20 caractères")
                return
            
            if len(lieu_deces_var.get()) > 20:
                messagebox.showerror("Erreur", "Le lieu du decès doit contenir mau max : 20 caractères")
                return

            #verifier la validité du sexe
            if sexe_var.get().lower() != "m" and sexe_var.get().lower() != "f":
                messagebox.showerror("Erreur", "Veuillez saisir le sexe: M ou F")
                return
            
            #verifier la validité de la date de naissance
            if date_naiss_var.get() and not Individu.date_valide(date_naiss_var.get()):
                messagebox.showerror("Erreur", "Veuillez saisir une date de naissance valide.")
                return
            
            #verifier la validité de la date de décès
            if date_deces_var.get() and not Individu.date_valide(date_deces_var.get()):
                messagebox.showerror("Erreur", "Veuillez saisir une date de décès valide.")
                return
            
            #Verifier la coherence entre la date de naissance et celle de décès
            if date_naiss_var.get() and date_deces_var.get() and not Individu.date_coherente(date_naiss_var.get(), date_deces_var.get()):
                messagebox.showerror("Erreur", "On ne peut mourir avant d'être né.")
                return
            
            #Verification de la différence entre la date de naissance et celle de décès
            if date_naiss_var.get() and date_deces_var.get() and Individu.difference_annees(date_naiss_var.get(),date_deces_var.get(), 150):
                messagebox.showerror("Erreur","Ce n'est pas logique d'avoir plus de 150 ans")
                return
            
            if messagebox.askyesno("Confirmation", "Souhaitez-vous enregistrer les modifications ?"):
                valider_individu()
                callback_retour()
            else:
                callback_retour()

        def valider_individu():
            individu.nom = nom_var.get()
            individu.prenom = prenom_var.get()
            individu.sexe = sexe_var.get() if not a_famille_formee else individu.sexe
            individu.occupation = occupation_var.get()
            individu.date_naissance = date_naiss_var.get()
            individu.lieu_naissance = lieu_naiss_var.get()
            individu.deces = deces_var.get().lower()
            individu.date_deces = date_deces_var.get() if individu.deces == "oui" else None
            individu.lieu_deces = lieu_deces_var.get() if individu.deces == "oui" else None

            conn = sqlite3.connect(login)
            c = conn.cursor()
            c.execute("""
                UPDATE Individu 
                SET nom = ?, prenom = ?, sexe = ?, date_naissance = ?, lieu_naissance = ?, occupation = ?, deces = ?, date_deces = ?, lieu_deces = ?
                WHERE id_individu = ?
            """, (individu.nom, individu.prenom, individu.sexe, individu.date_naissance, individu.lieu_naissance, individu.occupation, individu.deces, individu.date_deces, individu.lieu_deces, individu.id_individu))
            conn.commit()
            conn.close()
            messagebox.showinfo("Succès", "Modifications enregistrées avec succès.")

        Button(frame_button, text="Retour", command=callback_retour, bg="#123", fg="white").pack(side="left", padx=10)
        Button(frame_button, text="Valider", command=proposer_confirmation, bg="#41B77F", fg="white").pack(side="left", padx=10)


    #Fonction qui affiche les familles d'un individu
    def afficher_famille_individu(login, frame, individu: 'Individu', callback_retour):
        from famille import Famille
        import sqlite3
        from tkinter import Label, Frame, Canvas, Scrollbar, Button

        # Nettoyer le frame
        for widget in frame.winfo_children():
            widget.pack_forget()

        frame.config(bg="#f5f5f5")

        Label(frame, text="Famille(s) formée(s) par:", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=(10, 10))
        Label(frame, text=f"({individu.prenom} {individu.nom})", font=("Helvetica", 14, "bold"),
            fg="#41B77F", wraplength=400, justify="center").pack(pady=(5, 5))

        conn = sqlite3.connect(login)
        c = conn.cursor()

        familles_ids = [fid.strip() for fid in individu.ids_famille_formes.split(",") if fid.strip()] if individu.ids_famille_formes else []
        familles = []

        for fid in familles_ids:
            c.execute("SELECT * FROM Famille WHERE id_mariage = ?", (fid,))
            row = c.fetchone()
            if row:
                familles.append(Famille(*row))

        c.execute("SELECT id_individu, prenom, nom FROM Individu")
        individus_dict = {str(row[0]): f"{row[1]} {row[2]}" for row in c.fetchall()}
        conn.close()

        def get_nom_prenom(id_individu):
            return individus_dict.get(str(id_individu), "Inconnu")

        if familles:
            scroll_frame = Frame(frame, bg="#f5f5f5")
            scroll_frame.pack(padx=10, pady=5, fill="both", expand=True)

            canvas_container = Frame(scroll_frame, bg="#f5f5f5")
            canvas_container.pack(side="left", expand=True)

            canvas = Canvas(canvas_container, height=398, width=360, bg="#f5f5f5", highlightthickness=0)
            canvas.pack(padx=(30, 0))

            scrollbar = Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
            scrollbar.pack(side="right", fill="y")
            canvas.configure(yscrollcommand=scrollbar.set)

            max_width = 360
            content_frame = Frame(canvas, bg="white", width=max_width)
            window_id = canvas.create_window((0, 0), window=content_frame, anchor="n")

            def resize_content(event):
                canvas_width = event.width
                content_width = min(canvas_width, max_width)
                x_offset = (canvas_width - content_width) // 2
                canvas.coords(window_id, x_offset, 0)
                canvas.itemconfig(window_id, width=content_width)
                canvas.configure(scrollregion=canvas.bbox("all"))

            canvas.bind('<Configure>', resize_content)

            for idx, famille in enumerate(familles, start=1):
                conjoint_nom = get_nom_prenom(famille.id_conjoint)
                conjointe_nom = get_nom_prenom(famille.id_conjointe)

                ids_enfants = [eid.strip() for eid in famille.ids_enfants.split(",") if eid.strip()] if famille.ids_enfants else []
                enfants_noms = [get_nom_prenom(eid) for eid in ids_enfants]

                card = Frame(content_frame, bg="white", bd=2, relief="groove")
                card.pack(pady=12, padx=18, fill="x")

                Label(card, text=f"Famille {idx}", font=("Helvetica", 16, "bold"), bg="white", fg="#41B77F").pack(anchor="center", padx=10, pady=(5, 0))

                Label(card, text=f"Conjoint : {conjoint_nom}", font=("Helvetica", 13), bg="white", wraplength=310, justify="center").pack(anchor="w", padx=10)
                Label(card, text=f"Conjointe : {conjointe_nom}", font=("Helvetica", 13), bg="white", wraplength=310, justify="center").pack(anchor="w", padx=10)
                Label(card, text=f"Date mariage : {famille.date_mariage or 'Non renseignée'}", font=("Helvetica", 13), bg="white").pack(anchor="w", padx=10)
                Label(card, text=f"Lieu mariage : {famille.lieu_mariage or 'Non renseigné'}", font=("Helvetica", 13), bg="white", wraplength=300, justify="center").pack(anchor="w", padx=10)
                Label(card, text=f"Divorcé(e) : {'Oui' if famille.divorce else 'Non'}", font=("Helvetica", 13), bg="white").pack(anchor="w", padx=10)

                if famille.divorce:
                    Label(card, text=f"Date divorce : {famille.date_divorce or 'Non renseignée'}", font=("Helvetica", 13), bg="white").pack(anchor="w", padx=10)

                Label(card, text="Enfants :", font=("Helvetica", 13, "bold"), bg="white").pack(anchor="center", padx=10, pady=(5, 0))

                if enfants_noms:
                    for nom in enfants_noms:
                        Label(card, text=f"- {nom}", font=("Helvetica", 13), bg="white", wraplength=275, justify="center").pack(anchor="center", padx=25)
                else:
                    Label(card, text="Aucun enfant", font=("Helvetica", 13, "italic"), bg="white").pack(anchor="center", padx=25)

        else:
            Label(frame, text="Aucune famille formée.", font=("Helvetica", 14, "italic"), bg="#f5f5f5").pack(pady=20)

        Button(frame, text="Retour", command=callback_retour, bg="#123", fg="white").pack(pady=5)

    #------------------------------------------------------------------------------------------------------------

    #Fonction qui recupère les infos d'un individu
    @staticmethod
    def get_individu_info(db_path, id_individu):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute(
            "SELECT id_individu, nom, prenom, id_famille_issue "
            "FROM Individu WHERE id_individu = ?",
            (id_individu,)
        )
        row = c.fetchone()
        conn.close()
        return row if row else (None, "Inconnu", "", None)

    
    #Fonction qui recupère les ids du conjoint et de la conjointe (parent)
    @staticmethod
    def get_parents_from_famille(db_path, id_famille):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute(
            "SELECT id_conjoint AS pere, id_conjointe AS mere "
            "FROM Famille WHERE id_mariage = ?",
            (id_famille,)
        )
        row = c.fetchone()
        conn.close()
        return row if row else (None, None)
    
    #Fonction qui calcule le nombre de génération d'un individu
    @staticmethod
    def calculer_profondeur_ascendante(db_path, id_individu):
        if not id_individu:
            return 0

        id_i, _, _, id_famille = Individu.get_individu_info(db_path, id_individu)
        if not id_famille:
            return 1  # L'individu n'a pas de parents

        id_pere, id_mere = Individu.get_parents_from_famille(db_path, id_famille)

        profondeur_pere = Individu.calculer_profondeur_ascendante(db_path, id_pere) if id_pere else 0
        profondeur_mere = Individu.calculer_profondeur_ascendante(db_path, id_mere) if id_mere else 0

        return 1 + max(profondeur_pere, profondeur_mere)


   #Fonction qui construit un arbre
    @staticmethod
    def construire_arbre(db_path, id_individu, generation,
                        arbre, positions,
                        maxgeneration, vertical_spacing,
                        x_tracker):
        if generation +1 > maxgeneration or id_individu is None:
            return None

        id_i, nom, prenom, id_famille = Individu.get_individu_info(db_path, id_individu)
        label = f"{prenom} {nom}"
        arbre[id_individu] = label

        y = -generation * vertical_spacing  # positionne génération 0 en bas

        id_pere, id_mere = None, None
        pos_pere, pos_mere = None, None

        if id_famille:
            id_pere, id_mere = Individu.get_parents_from_famille(db_path, id_famille)
            pos_pere = Individu.construire_arbre(db_path, id_pere, generation + 1,
                                                arbre, positions, maxgeneration,
                                                vertical_spacing, x_tracker)
            pos_mere = Individu.construire_arbre(db_path, id_mere, generation + 1,
                                                arbre, positions, maxgeneration,
                                                vertical_spacing, x_tracker)

        # Placement horizontal : centré entre les parents
        if pos_pere is not None and pos_mere is not None:
            x = (pos_pere + pos_mere) / 2
        elif pos_pere is not None:
            x = pos_pere
        elif pos_mere is not None:
            x = pos_mere
        else:
            x = x_tracker[0]
            x_tracker[0] += 200  # espace horizontal minimal

        positions[id_individu] = (x, y)
        return x

    #Fonction qui affiche les ascendants
    @staticmethod
    def afficher_ascendant(db_path, parent_frame, id_individu, callback_retour=None):
        for widget in parent_frame.winfo_children():
            widget.destroy()

        parent_frame.config(bg="#f5f5f5")
        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(0, weight=1)

    
        inner_frame = Frame(parent_frame, bg="#f5f5f5")
        inner_frame.grid(row=0, column=0)
        inner_frame.pack(anchor="n")


        Label(inner_frame, text="Afficher les ascendants", font=("Helvetica", 18, "bold"),
            bg="#f5f5f5", fg="#41B77F").pack(pady=20)

        # Nombre de générations
        Label(inner_frame, text="Nombre de générations à afficher :", font=("Helvetica", 12), bg="#f5f5f5").pack(pady=5)
        generations_entry = Entry(inner_frame, font=("Helvetica", 12), justify="center")
        generations_entry.insert(0, Individu.calculer_profondeur_ascendante(db_path, id_individu))
        generations_entry.pack(pady=5)

        # Boutons radio pour choix affichage
        choix_var = IntVar(value=1)

        Frame(inner_frame, height=10, bg="#f5f5f5").pack()

        radio_frame = Frame(inner_frame, bg="#f5f5f5")
        radio_frame.pack(pady=10)

        Radiobutton(radio_frame, text="Afficher en arbre", variable=choix_var, value=1,
                    font=("Helvetica", 12), bg="#f5f5f5").pack(side=LEFT, padx=10)
        Radiobutton(radio_frame, text="Afficher en liste", variable=choix_var, value=2,
                    font=("Helvetica", 12), bg="#f5f5f5").pack(side=LEFT, padx=10)

        error_label = Label(inner_frame, text = "", fg = "red", bg = "#f5f5f5", font=("Helvetica", 12))

        # Bouton valider
        def afficher():
            try:
                maxgen = int(generations_entry.get())
                max_prof = Individu.calculer_profondeur_ascendante(db_path, id_individu)
                if maxgen < 1:
                    raise ValueError("Le nombre de générations doit être >= 1")
                elif maxgen > max_prof:
                    msg = f"Il n'y a que {max_prof} générations ascendantes disponibles."
                    messagebox.showerror("Erreur", msg)
                    return
                if choix_var.get() == 1:
                    Individu.afficher_arbre_ascendant(db_path, parent_frame, id_individu, maxgeneration=maxgen, callback_retour=callback_retour)

                else:
                    Individu.afficher_liste_ascendante(db_path, parent_frame, id_individu, maxgeneration=maxgen, callback_retour=callback_retour)
            except ValueError as e:
                error_label.config(text=f"Erreur : {str(e)}")
                error_label.pack(pady=5)

        Button(inner_frame, text="Afficher", command=afficher, bg="#41B77F", fg="white",
            font=("Helvetica", 12)).pack(pady=15)

        # Bouton retour
        if callback_retour:
            Button(inner_frame, text="Retour", command=callback_retour,
                bg="#123", fg="white", font=("Helvetica", 12)).pack(pady=10)

    #Fonction qui affiche les ascendants d'un individu (arbre)
    @staticmethod
    def afficher_arbre_ascendant(db_path, parent_frame, id_individu, maxgeneration=10, callback_retour=None):
        for w in parent_frame.winfo_children():
            w.destroy()

        id_i, nom, prenom, _ = Individu.get_individu_info(db_path, id_individu)

        Label(
            parent_frame,
            text=f"🌳 Ascendants de {prenom} {nom}",
            font=("Helvetica", 15, "italic"),
            bg="#f5f5f5",
            wraplength=470, justify="center"
        ).pack(pady=10, side="bottom")

        parent_frame.config(bg="#f5f5f5")

        container = Frame(parent_frame, bg="#f5f5f5")
        container.pack(fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        canvas = Canvas(container, bg="#f5f5f5", bd=0, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")

        vbar = Scrollbar(container, orient=VERTICAL, command=canvas.yview)
        vbar.grid(row=0, column=1, sticky="ns")

        hbar = Scrollbar(parent_frame, orient=HORIZONTAL, command=canvas.xview)
        hbar.pack(side=BOTTOM, fill=X)

        canvas.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)

        arbre = {}
        positions = {}
        vertical_spacing = 100
        x_tracker = [0]

        Individu.construire_arbre(
            db_path, id_individu, 0,
            arbre, positions, maxgeneration, vertical_spacing, x_tracker
        )

        base_positions = positions.copy()
        zoom_level = [1.0]

        # Définir les limites du zoom
        MIN_ZOOM = 0.8
        MAX_ZOOM = 2.0

        #Fonction qui dessine l'arbre
        @staticmethod
        def dessiner_arbre():
            canvas.delete("all")
            base_font_size = 12
            current_font = Font(family="Helvetica", size=int(base_font_size * zoom_level[0]))
            coords_box = {}

            box_height = 30
            margin = 80

            min_x = min(pos[0] for pos in base_positions.values())
            max_x = max(pos[0] for pos in base_positions.values())
            min_y = min(pos[1] for pos in base_positions.values())
            max_y = max(pos[1] for pos in base_positions.values())

            total_width = (max_x - min_x) * zoom_level[0] if max_x != min_x else 1
            total_height = (max_y - min_y) * zoom_level[0] if max_y != min_y else 1

            canvas.update_idletasks()
            visible_width = canvas.winfo_width()
            visible_height = canvas.winfo_height()

            target_width = max(visible_width, total_width + 2 * margin)
            target_height = max(visible_height, total_height + 2 * margin)

            decalage_x = (target_width - total_width) / 2 - min_x * zoom_level[0]
            decalage_y = (target_height - total_height) / 2 - min_y * zoom_level[0]

            positions = {
                iid: (
                    x * zoom_level[0] + decalage_x,
                    y * zoom_level[0] + decalage_y
                )
                for iid, (x, y) in base_positions.items()
            }

            
            for iid, (x, y) in positions.items():
                label = arbre[iid]
                w_text = current_font.measure(label)
                box_w = (w_text + 20)
                box_h = box_height * zoom_level[0]

                x1, y1 = x - box_w / 2, y
                x2, y2 = x + box_w / 2, y + box_h

                # Pour l'Ombre 
                canvas.create_rectangle(x1 + 5 * zoom_level[0], y1 + 5 * zoom_level[0], x2 + 5 * zoom_level[0], y2 + 5 * zoom_level[0], fill="gray", outline="", width=4)
                
                # Boîte principale
                canvas.create_rectangle(x1, y1, x2, y2, fill="lightblue", outline="black", width=1, tags="box")
                canvas.create_text(x, y + box_h / 2, text=label, font=current_font)

                coords_box[iid] = (x1, y1, x2, y2)

            # Lignes de liaison entre parents et enfants
            for eid, (x_e, y_e) in positions.items():
                _, _, _, fam = Individu.get_individu_info(db_path, eid)
                if fam:
                    pid, mid = Individu.get_parents_from_famille(db_path, fam)
                    for par in (pid, mid):
                        if par in coords_box:
                            x1e, y1e, x2e, y2e = coords_box[eid]
                            x1p, y1p, x2p, y2p = coords_box[par]
                            # Utilisation de courbes pour les lignes de liaison
                            canvas.create_line(
                                (x1e + x2e) / 2, y1e,
                                (x1p + x2p) / 2, y2p,
                                width=2, smooth=True, fill="#3b3b3b", dash=(4, 2)
                            )

            bbox = canvas.bbox("all")
            if bbox:
                x1, y1, x2, y2 = bbox
                padding = 50 
                canvas.config(scrollregion=(x1 - padding, y1 - padding, x2 + padding, y2 + padding))
            else:
                canvas.config(scrollregion=(0, 0, target_width, target_height))

        def resize(event):
            dessiner_arbre()

        #Fonction pour le zoom
        def zoom_in():
            # Appliquer le zoom en augmentant la valeur
            zoom_level[0] = min(zoom_level[0] * 1.1, MAX_ZOOM)
            dessiner_arbre()

        def zoom_out():
            # Appliquer le zoom en diminuant la valeur
            zoom_level[0] = max(zoom_level[0] / 1.1, MIN_ZOOM)
            dessiner_arbre()

        def on_mouse_wheel(event):
            try:
                if hasattr(event, 'delta'):
                    zoom_level[0] = min(max(zoom_level[0] * (1.1 if event.delta > 0 else 1 / 1.1), MIN_ZOOM), MAX_ZOOM)
                elif event.num == 4:
                    zoom_level[0] = min(zoom_level[0] * 1.1, MAX_ZOOM)
                elif event.num == 5:
                    zoom_level[0] = max(zoom_level[0] / 1.1, MIN_ZOOM)
                dessiner_arbre()
            except:
                pass

        canvas.bind("<Configure>", resize)
        canvas.bind("<MouseWheel>", on_mouse_wheel)  
        canvas.bind("<Button-4>", on_mouse_wheel)    
        canvas.bind("<Button-5>", on_mouse_wheel)    

        
        control_frame = Frame(parent_frame, bg="#f5f5f5")
        control_frame.pack(pady=20)

        Button(control_frame, text="Retour",
            command=lambda: Individu.afficher_ascendant(db_path, parent_frame, id_individu, callback_retour),
            bg="#123", fg="white", font=("Helvetica", 12)).pack(side=LEFT, padx=20)

        Button(control_frame, text="Zoom +", command=zoom_in,
            bg="#41B77F", fg="white", font=("Helvetica", 12)).pack(side=LEFT, padx=10)

        Button(control_frame, text="Zoom -", command=zoom_out,
            bg="#41B77F", fg="white", font=("Helvetica", 12)).pack(side=LEFT, padx=10)

        dessiner_arbre()


    #Fonction qui affiche les ascendants (liste)
    @staticmethod
    def afficher_liste_ascendante(db_path, parent_frame, id_individu, maxgeneration=10, callback_retour=None):
        for widget in parent_frame.winfo_children():
            widget.destroy()

        id_i, nom, prenom, _ = Individu.get_individu_info(db_path, id_individu)
        parent_frame.config(bg="#f5f5f5")

        Label(parent_frame, text=f"📋 Liste des ascendants de {prenom} {nom}",
            font=("Helvetica", 15, "bold"),
            bg="#f5f5f5", fg="#2F4F4F", wraplength=470, justify="center").pack(pady=(20, 10))

        # Conteneur principal centré
        outer_frame = Frame(parent_frame, bg="#f5f5f5")
        outer_frame.pack(expand=True, fill="both")

        canvas = Canvas(outer_frame, bg="#f5f5f5", highlightthickness=0)
        canvas.pack(side=LEFT, fill="both", expand=True)

        scrollbar = Scrollbar(outer_frame, orient=VERTICAL, command=canvas.yview)
        scrollbar.pack(side=RIGHT, fill=Y)

        canvas.configure(yscrollcommand=scrollbar.set)

        # Cadre centré à l’intérieur du canvas
        list_frame = Frame(canvas, bg="#ffffff")
        inner_window = canvas.create_window((0, 0), window=list_frame, anchor='n', tags="inner")

        font = ("Helvetica", 12)
        color_even = "#F0F0F0"
        color_odd = "#E0F7FA"

        # Liste de couleurs pour chaque génération
        generation_colors = [
            "#2F4F4F",  # Generation 0
            "#1E90FF",  # Generation 1
            "#32CD32",  # Generation 2
            "#FFD700",  # Generation 3
            "#FF6347",  # Generation 4
            "#8A2BE2",  # Generation 5
            "#D2691E",  # Generation 6
            "#DC143C",  # Generation 7
            "#FF1493",  # Generation 8
            "#C71585",  # Generation 9
            "#FF4500",  # Generation 10
        ]

        def parcours(sosa_num, id_ind, generation):
            if generation + 1> maxgeneration or id_ind is None:
                return

            id_i, nom, prenom, id_famille = Individu.get_individu_info(db_path, id_ind)
            label = f"{sosa_num}. {prenom} {nom}"
            bg_color = color_odd

            # Choix de la couleur de la police en fonction de la génération
            text_color = generation_colors[generation] if generation < len(generation_colors) else "#000000"

            item = Frame(list_frame, bg=bg_color, bd=1, relief="ridge")
            item.pack(pady=5, padx=50, fill="x")

            Label(item, text=label,
                font=("Helvetica", 13, "italic"),
                bg=bg_color, fg=text_color, anchor="w",
                padx=20 * generation, pady=8).pack(fill="x")

            if id_famille:
                id_pere, id_mere = Individu.get_parents_from_famille(db_path, id_famille)
                parcours(sosa_num * 2, id_pere, generation + 1)
                parcours(sosa_num * 2 + 1, id_mere, generation + 1)

        parcours(1, id_individu, 0)

        list_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        def resize(event):
            canvas_width = event.width
            frame_width = list_frame.winfo_reqwidth()
            x_offset = max((canvas_width - frame_width) // 2, 0)
            canvas.coords("inner", x_offset, 0)
            canvas.itemconfig("inner", width=frame_width)

        canvas.bind("<Configure>", resize)

        Button(parent_frame, text="Retour",
            command=lambda: Individu.afficher_ascendant(db_path, parent_frame, id_individu, callback_retour),
            bg="#2F4F4F", fg="white", font=("Helvetica", 12, "bold"),
            padx=10, pady=5).pack(pady=30)
        
    #------------------------------------------------------------------------------------------------------------

    #Fonction qui affiche nom et prenom
    @staticmethod
    def afficher_nom_prenom2(login, id_individu, num_soza, generation, frame, mode=1):
        try:
            with sqlite3.connect(login) as conn:
                c = conn.cursor()
                c.execute("SELECT prenom, nom FROM Individu WHERE id_individu = ?", (id_individu,))
                personne = c.fetchone()
                if personne:
                    nom_complet = f"{'—' * generation} [{num_soza}] {personne[0]} {personne[1]}"
                    Label(frame, text=nom_complet, font=("Helvetica", 12), bg="#f5f5f5").pack(anchor="w", padx=20)
        except Exception as e:
            print(f"Erreur dans afficher_nom_prenom2 : {e}")

    #Recuperer les ids des familles qu'un individu a formé
    @staticmethod
    def recuperer_ids_famille_formees(login, id_individu):
        try:
            with sqlite3.connect(login) as conn:
                c = conn.cursor()
                c.execute("SELECT ids_famille_formes FROM Individu WHERE id_individu = ?", (id_individu,))
                ids = c.fetchone()
            return ids
        except Exception as e:
            print(f"Erreur dans recuperer_ids_famille_formees : {e}")

    #recuperer les ids des enfants
    @staticmethod
    def recuperer_ids_enfant(login, id_famille):
        try:
            with sqlite3.connect(login) as conn:
                c = conn.cursor()
                c.execute("SELECT ids_enfants FROM Famille WHERE id_mariage = ?", (id_famille,))
                ids = c.fetchone()
            if ids:
                return ids[0].split(",")
            return []
        except Exception as e:
            print(f"Erreur dans recuperer_ids_enfant : {e}")
            return []
    
    @staticmethod
    def calculer_profondeur_descendante(db_path, id_individu):
        if not id_individu:
            return 0

        familles = Individu.recuperer_ids_famille_formees(db_path, id_individu)
        if not familles or not familles[0]:
            return 1  # Pas de familles formées alors pas d'enfants

        familles_ids = [fid.strip() for fid in familles[0].split(",") if fid.strip().isdigit()]
        enfants = []

        for fid in familles_ids:
            enfants_ids = Individu.recuperer_ids_enfant(db_path, fid)
            enfants += [eid.strip() for eid in enfants_ids if eid.strip().isdigit()]

        if not enfants:
            return 1  # Pas d'enfants, profondeur minimale

        profondeurs = []
        for eid in enfants:
            prof = Individu.calculer_profondeur_descendante(db_path, int(eid))
            profondeurs.append(prof)

        return 1 + max(profondeurs)


    #Fonction qui affiche les descendants
    @staticmethod
    def afficher_descendant(db_path, parent_frame, id_individu, maxgeneration, callback_retour=None):
        for widget in parent_frame.winfo_children():
            widget.destroy()

        parent_frame.config(bg="#f5f5f5")
        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(0, weight=1)

        inner_frame = Frame(parent_frame, bg="#f5f5f5")
        inner_frame.grid(row=0, column=0)
        inner_frame.pack(anchor="n")


        Label(inner_frame, text="Afficher les descendants", font=("Helvetica", 18, "bold"),
            bg="#f5f5f5", fg="#41B77F").pack(pady=20)

        Label(inner_frame, text="Nombre de générations à afficher :", font=("Helvetica", 12), bg="#f5f5f5").pack(pady=5)
        generations_entry = Entry(inner_frame, font=("Helvetica", 12), justify="center")
        generations_entry.insert(0, Individu.calculer_profondeur_descendante(db_path, id_individu))
        generations_entry.pack(pady=5)

        choix_var = IntVar(value=1)

        Frame(inner_frame, height=10, bg="#f5f5f5").pack()

        radio_frame = Frame(inner_frame, bg="#f5f5f5")
        radio_frame.pack(pady=10)

        Radiobutton(radio_frame, text="Afficher en arbre", variable=choix_var, value=1,
                    font=("Helvetica", 12), bg="#f5f5f5").pack(side=LEFT, padx=10)
        Radiobutton(radio_frame, text="Afficher en liste", variable=choix_var, value=2,
                    font=("Helvetica", 12), bg="#f5f5f5").pack(side=LEFT, padx=10)

        error_label = Label(inner_frame, text = "", fg = "red", bg = "#f5f5f5", font=("Helvetica", 12))
        def afficher():
            try:
                gen = int(generations_entry.get())
                max_prof = Individu.calculer_profondeur_descendante(db_path, id_individu)
                if gen < 1:
                    raise ValueError("Le nombre de générations doit être >= 1")
                elif gen > max_prof:
                    msg = f"Il n'y a que {max_prof} générations descendantes disponibles."
                    messagebox.showerror("Erreur", msg)
                    return
                if choix_var.get() == 1:
                    Individu.afficher_descendants_en_arbre(db_path, parent_frame, id_individu, gen, callback_retour)
                else:
                    Individu.afficher_descendants_en_liste(db_path, parent_frame, id_individu, gen, callback_retour)
            except ValueError as e:
                error_label.config(text=f"Erreur : {str(e)}")
                error_label.pack(pady=5)

        Button(inner_frame, text="Afficher", command=afficher, bg="#41B77F", fg="white", font=("Helvetica", 12)).pack(pady=15)

        if callback_retour:
            Button(inner_frame, text="Retour", command=callback_retour,
                bg="#123", fg="white", font=("Helvetica", 12)).pack(pady=10)

    #Afficher les descendants en arbre
    @staticmethod
    def afficher_descendants_en_arbre(login, parent_frame, id_individu,
                                    maxgeneration, callback_retour=None):
        from tkinter import (Canvas, Scrollbar, Frame, Button, Label,
                            VERTICAL, HORIZONTAL, BOTH, X, LEFT, BOTTOM, CENTER)
        from tkinter.font import Font
        import sqlite3

        for w in parent_frame.winfo_children():
            w.destroy()
        parent_frame.config(bg="#f5f5f5")

        # Titre
        try:
            with sqlite3.connect(login) as conn:
                cur = conn.cursor()
                cur.execute("SELECT prenom, nom FROM Individu WHERE id_individu=?",
                            (id_individu,))
                row = cur.fetchone()
                titre = f"🌳 Descendants de {row[0]} {row[1]}" if row else "Arbre des descendants"
        except Exception:
            titre = "Arbre des descendants"

        Label(parent_frame, text=titre, font=("Helvetica", 15, "bold"),
            bg="#f5f5f5", fg="#2F4F4F", anchor="center",justify="center",
            wraplength=470).pack(pady=(20, 10))

        container = Frame(parent_frame, bg="#f5f5f5")
        container.pack(fill=BOTH, expand=True)

        canvas = Canvas(container, bg="#ffffff", highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")

        vbar = Scrollbar(container, orient=VERTICAL, command=canvas.yview)
        vbar.grid(row=0, column=1, sticky="ns")

        hbar = Scrollbar(parent_frame, orient=HORIZONTAL, command=canvas.xview)
        hbar.pack(side=BOTTOM, fill=X)

        canvas.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        couleurs = ["#add8e6", "#90ee90", "#ffcc99", "#dab6fc", "#ffb6b9", "#c1f0f6"]
        vertical_spacing = 120
        base_font_size = 11
        zoom = [1.0]
        MIN_ZOOM, MAX_ZOOM = 0.8, 2.5

        node_positions = {} 
        text_items = {}      

        def dessiner_boite(x, y, bw, bh, couleur, texte, iid):
            # Rectangle
            rect = canvas.create_rectangle(
                x, y, x + bw, y + bh,
                fill=couleur, outline="black", tags="zoomable")
            # Texte centré
            fnt = Font(family="Helvetica", size=max(int(base_font_size * zoom[0]), 1))
            txt = canvas.create_text(
                x + bw/2, y + bh/2, text=texte,
                font=fnt, tags="zoomable", anchor=CENTER)
            text_items[iid] = txt
            return rect, txt

        def afficher_arbre(iid, x, y, gen):
            if gen >= maxgeneration:
                return x, x + 100

            try:
                with sqlite3.connect(login) as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT prenom, nom, sexe FROM Individu WHERE id_individu=?", (iid,))
                    row = cur.fetchone()
                if row:
                    prenom, nom, sexe = row
                    emoji = "👦" if sexe == 'M' else "👧" if sexe == 'F' else "❓"
                    texte = f"{emoji} {prenom} {nom}"
                else:
                    texte = "❓ Inconnu"

                # Mesure texte à la taille de base
                fnt = Font(family="Helvetica", size=base_font_size)
                txt_w = fnt.measure(texte)
                txt_h = fnt.metrics("linespace")

                pad_x, pad_y = 20, 10
                bw, bh = txt_w + pad_x, txt_h + pad_y
                couleur = couleurs[gen % len(couleurs)]

                # Récupérer enfants
                enfants = []
                fams = Individu.recuperer_ids_famille_formees(login, iid)
                if fams and fams[0]:
                    for fid in (f.strip() for f in fams[0].split(",") if f.strip()):
                        enfants += Individu.recuperer_ids_enfant(login, int(fid))

                if not enfants or gen + 1 >= maxgeneration:
                    # Dessiner boîte 
                    dessiner_boite(x, y, bw, bh, couleur, texte, iid)
                    node_positions[iid] = (x + bw/2, y + bh)
                    return x, x + bw

                spacing = 30
                child_x = x
                child_positions = []
                min_x, max_x = float('inf'), float('-inf')

                for eid in enfants:
                    cmin, cmax = afficher_arbre(eid, child_x, y + vertical_spacing, gen + 1)
                    center_child = (cmin + cmax) / 2
                    child_positions.append((eid, center_child))
                    child_x = cmax + spacing
                    min_x = min(min_x, cmin)
                    max_x = max(max_x, cmax)

                parent_cx = (min_x + max_x) / 2 - bw / 2
                dessiner_boite(parent_cx, y, bw, bh, couleur, texte, iid)
                node_positions[iid] = (parent_cx + bw/2, y + bh)

                # Dessiner liens
                for _, cx_child in child_positions:
                    canvas.create_line(
                        parent_cx + bw/2, y + bh,
                        cx_child, y + vertical_spacing,
                        fill="gray", width=2, tags="zoomable")

                return min_x, max_x

            except Exception as e:
                print("Erreur arbre:", e)
                return x, x + 100

        # Dessiner arbre
        afficher_arbre(id_individu, 0, 50, 0)

        def update_scroll_and_center():
            canvas.update_idletasks()
            bbox = canvas.bbox("all")
            if not bbox:
                return
            x1, y1, x2, y2 = bbox
            canvas.config(scrollregion=(x1 - 100, y1 - 100, x2 + 100, y2 + 200))

            canvas_width = canvas.winfo_width()
            total_width = (x2 + 100) - (x1 - 100)

            root_pos = node_positions.get(id_individu, None)
            if root_pos is None:
                return
            root_x = root_pos[0]

            # Cas boîte unique (aucun enfant) détecté si pas de descendants
            nb_nodes = len(node_positions)
            if nb_nodes == 1:
                # On centre la boîte unique horizontalement et verticalement dans le canvas
                box_center_x = root_x
                box_center_y = root_pos[1]  # bas de la boîte

                # Décalage horizontal
                offset_x = (canvas_width /2 - box_center_x) - 100
                canvas.move("all", offset_x, 0)

                # Scroll reset
                canvas.xview_moveto(0)
                canvas.yview_moveto(0)
            else:
                # Plusieurs boîtes (arbre complet), on garde le centrage avec scroll
                if total_width <= canvas_width:
                    offset = (canvas_width - total_width) / 2
                    canvas.xview_moveto(0)
                    canvas.move("all", offset - x1, 0)
                else:
                    view_start = max(min((root_x - canvas_width / 2 - (x1 - 100)) / total_width, 1), 0)
                    canvas.xview_moveto(view_start)
                canvas.yview_moveto(0)

        update_scroll_and_center()

        # Gestion zoom 
        def zoom_in():
            if zoom[0] * 1.1 > MAX_ZOOM:
                return
            facteur = 1.1
            zoom[0] *= facteur
            _apply_zoom(facteur)

        def zoom_out():
            if zoom[0] / 1.1 < MIN_ZOOM:
                return
            facteur = 1 / 1.1
            zoom[0] *= facteur
            _apply_zoom(facteur)

        def _apply_zoom(facteur):
            cx = canvas.winfo_width() // 2
            cy = canvas.winfo_height() // 2
            canvas.scale("zoomable", cx, cy, facteur, facteur)

            # Met à jour la taille des textes
            for iid, txt_id in text_items.items():
                new_size = max(int(base_font_size * zoom[0]), 1)
                font = Font(family="Helvetica", size=new_size)
                canvas.itemconfig(txt_id, font=font)

            update_scroll_and_center()

        def on_mouse_wheel(event):
            if event.delta > 0:
                zoom_in()
            else:
                zoom_out()

        canvas.bind("<MouseWheel>", on_mouse_wheel)

        # Recentrer automatiquement à chaque resize
        def on_resize(event):
            update_scroll_and_center()

        canvas.bind("<Configure>", on_resize)

        # Boutons contrôle
        ctrl = Frame(parent_frame, bg="#f5f5f5")
        ctrl.pack(pady=15)

        Button(ctrl, text="⬅ Retour",
            command=lambda: Individu.afficher_descendant(login, parent_frame,
                                                        id_individu, maxgeneration,
                                                        callback_retour),
            bg="#2F4F4F", fg="white",
            font=("Helvetica", 12, "bold"), padx=12, pady=6).pack(side=LEFT, padx=6)
        Button(ctrl, text="Zoom +", command=zoom_in,
            bg="#41B77F", fg="white",
            font=("Helvetica", 12), padx=12, pady=6).pack(side=LEFT, padx=6)
        Button(ctrl, text="Zoom -", command=zoom_out,
            bg="#B7410E", fg="white",
            font=("Helvetica", 12), padx=12, pady=6).pack(side=LEFT, padx=6)


    #Afficher descendants en liste
    @staticmethod
    def afficher_descendants_en_liste(login, frame, id_individu,
                                    maxgeneration=10, callback_retour=None):
        from tkinter import Label, Canvas, Frame, Scrollbar, Button, BOTH, RIGHT, LEFT, Y, X, VERTICAL, HORIZONTAL
        import sqlite3

        # Nettoyage du conteneur
        for w in frame.winfo_children():
            w.destroy()
        frame.config(bg="#f5f5f5")

        # Titre toujours visible
        header_frame = Frame(frame, bg="#f5f5f5")
        header_frame.pack(fill=X)

        try:
            with sqlite3.connect(login) as conn:
                c = conn.cursor()
                c.execute("SELECT prenom, nom FROM Individu WHERE id_individu = ?", (id_individu,))
                row = c.fetchone()
            titre = f"📋 Liste des descendants de {row[0]} {row[1]}" if row else "Individu inconnu"
        except Exception as e:
            print("Erreur titre :", e)
            titre = "Individu inconnu"

        Label(header_frame, text=titre, font=("Helvetica", 15, "bold"),
            bg="#f5f5f5", fg="#2F4F4F", anchor="center",justify="center",
            wraplength=470).pack(pady=(20, 10))

        # ── Conteneur principal avec scroll
        container = Frame(frame, bg="#f5f5f5")
        container.pack(expand=True, fill=BOTH)

        canvas = Canvas(container, bg="#f5f5f5", highlightthickness=0)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)

        v_scroll = Scrollbar(container, orient=VERTICAL, command=canvas.yview)
        v_scroll.pack(side=RIGHT, fill=Y)

        h_scroll = Scrollbar(frame, orient=HORIZONTAL, command=canvas.xview)
        h_scroll.pack(fill=X)

        canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Cadre contenu (list_frame) avec largeur réduite
        list_frame = Frame(canvas, bg="#ffffff")
        inner = canvas.create_window((0, 0), window=list_frame, anchor='n', tags="inner")

        #Fonction récursive pour affichage descendants
        def afficher_recursivement(id_ind, gen, num_soza):
            if gen > maxgeneration:
                return
            try:
                with sqlite3.connect(login) as conn:
                    c = conn.cursor()
                    c.execute("SELECT prenom, nom, sexe FROM Individu WHERE id_individu = ?", (id_ind,))
                    perso = c.fetchone()
                if perso:
                    prenom, nom, sexe = perso
                    emoji = "👦" if sexe == 'M' else "👧" if sexe == 'F' else "❓"
                else:
                    prenom, nom, emoji = "Inconnu", "", "❓"

                fond = "#ffffff" if gen % 2 == 0 else "#F0F0F0"
                texte = f"{' ' * 3 * gen}→ G{gen}  [{num_soza}] {emoji} {prenom} {nom}"

                Label(list_frame, text=texte, anchor="w",
                    font=("Helvetica", 13),
                    bg=fond, padx=20, pady=6, wraplength=1000).pack(fill=X, padx=30, pady=2)

                familles = Individu.recuperer_ids_famille_formees(login, id_ind)
                if familles and familles[0]:
                    for id_fam_str in familles[0].split(","):
                        if not id_fam_str.strip():
                            continue
                        id_fam = int(id_fam_str)
                        enfants = Individu.recuperer_ids_enfant(login, id_fam)

                        if enfants and enfants[0] != '':
                            with sqlite3.connect(login) as conn:
                                c = conn.cursor()
                                c.execute("SELECT id_conjoint, id_conjointe FROM Famille WHERE id_mariage = ?", (id_fam,))
                                couple = c.fetchone()
                            if couple:
                                id_conjoint, id_conjointe = couple
                                id_conjoint_reel = (id_conjointe if id_ind == id_conjoint else id_conjoint)
                                if id_conjoint_reel:
                                    with sqlite3.connect(login) as conn:
                                        c = conn.cursor()
                                        c.execute("SELECT prenom, nom, sexe FROM Individu WHERE id_individu = ?", (id_conjoint_reel,))
                                        conj = c.fetchone()
                                    if conj:
                                        pc, nc, sc = conj
                                        emoji_c = "👨‍❤️‍👨" if sc == 'M' else "👩‍❤️‍👩" if sc == 'F' else "💍"
                                        Label(list_frame,
                                            text=f"{' ' * 3 * (gen + 1)}💍 Mariage avec : {emoji_c} {pc} {nc}",
                                            font=("Helvetica", 11, "italic"),
                                            anchor="w", bg="#E6F2FF",
                                            padx=30, pady=4).pack(fill=X, padx=40, pady=2)

                        for i, enf in enumerate(enfants):
                            if enf.strip():
                                afficher_recursivement(int(enf), gen + 1, 2 * num_soza + i)
            except Exception as e:
                print("Erreur récursive :", e)

        afficher_recursivement(id_individu, 0, 0)

        #Ajustement scroll et centrage dynamique
        def update_scrollregion():
            canvas.configure(scrollregion=canvas.bbox("all"))

        def resize_canvas(event):
            update_scrollregion()

            canvas_w   = event.width            # largeur visible
            content_w  = list_frame.winfo_reqwidth()

            MAX_W      = 600                    # largeur maximal
            content_w  = min(content_w, MAX_W) 

            if content_w < canvas_w:
                # si Le contenu est plus étroit que la fenêtre, on le centre physiquement
                x_offset = (canvas_w - content_w) // 2
                canvas.coords(inner, x_offset, 0)
                canvas.itemconfigure(inner, width=content_w)
                canvas.xview_moveto(0)          # aucune barre horizontale
            else:
                #si Le contenu déborde, on aligne à gauche mais on centre la vue
                canvas.coords(inner, 0, 0)
                canvas.itemconfigure(inner, width=content_w)

                canvas.update_idletasks()       # bbox à jour
                bbox       = canvas.bbox("all")
                total_w    = bbox[2] - bbox[0]  # largeur scrollable
                frac_mid   = (total_w - canvas_w) / 2 / total_w  # place milieu
                canvas.xview_moveto(frac_mid)   # barre horizontale pointe au centre

        list_frame.bind("<Configure>", lambda e: update_scrollregion())
        canvas.bind("<Configure>", resize_canvas)

        # ── Bouton retour
        Button(frame, text="⬅ Retour",
            command=lambda: Individu.afficher_descendant(
                login, frame, id_individu, maxgeneration, callback_retour),
            bg="#2F4F4F", fg="white", font=("Helvetica", 12, "bold"),
            padx=10, pady=5).pack(pady=30)
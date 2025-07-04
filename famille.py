import sqlite3
import os
from individu import Individu
from tkinter import *
from tkinter import messagebox
from admin import *
from tkinter import ttk

class Famille:
    def __init__(self, id_famille=None, date_mariage=None, lieu_mariage=None, divorce=False, date_divorce=None,
                 id_conjoint=None, id_conjointe=None, ids_enfants=None):
        self.id_famille = id_famille
        self.date_mariage = date_mariage
        self.lieu_mariage = lieu_mariage
        self.divorce = divorce
        self.date_divorce = date_divorce
        self.id_conjoint = id_conjoint
        self.id_conjointe = id_conjointe
        self.ids_enfants = ids_enfants if ids_enfants else []


    # Méthode pour ajouter une famille dans la base de données
    def ajouter(self, login):
        conn = sqlite3.connect(login)
        c = conn.cursor()

        enfants = self.ids_enfants if isinstance(self.ids_enfants, (list, tuple)) else [self.ids_enfants]

        c.execute("""
            INSERT INTO Famille (
                date_mariage, lieu_mariage, divorce, date_divorce,
                id_conjoint, id_conjointe, ids_enfants
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            self.date_mariage,
            self.lieu_mariage,
            self.divorce,
            self.date_divorce,
            self.id_conjoint,
            self.id_conjointe,
            ",".join(map(str, enfants))  
        ))

        self.id_famille = c.lastrowid
        conn.commit()
        conn.close()
        return self.id_famille



    # Méthode pour associer une famille à un individu
    def associer_a_individu(self, login, individu_id):
        conn = sqlite3.connect(login)
        c = conn.cursor()
        c.execute("SELECT ids_famille_formes FROM Individu WHERE id_individu = ?", (individu_id,))
        result = c.fetchone()

        if result:
            # Ajouter l'ID de la famille à l'individu
            familles_existantes = result[0].split(",") if result[0] else []
            familles_existantes.append(str(self.id_famille))
            c.execute("""
                UPDATE Individu
                SET ids_famille_formes = ?
                WHERE id_individu = ?
            """, (",".join(familles_existantes), individu_id))
            conn.commit()
        conn.close()

    # Methode pour saisir les informations d'une famille 
    @staticmethod
    def saisie_info_famille(content_frame):
        entry_dateM_var = StringVar()
        entry_lieuM_var = StringVar()
        divorce_var = StringVar(value="Non")
        entry_dateDM_var = StringVar()

         # Champs conditionnels
        Label(content_frame, text="Date de mariage (JJ/MM/AAAA) :", bg="#f5f5f5").pack(pady=5)
        Entry(content_frame, relief="groove", bd=2, textvariable=entry_dateM_var).pack()

        Label(content_frame, text="Lieu de mariage :", bg="#f5f5f5").pack(pady=5)
        Entry(content_frame, relief="groove", bd=2, textvariable=entry_lieuM_var).pack()

        Label(content_frame, text="La famille est-elle divorcée ?", bg="#f5f5f5").pack(pady=5)
        divorce_frame = Frame(content_frame, bg="#f5f5f5")
        divorce_frame.pack()
        Radiobutton(divorce_frame, relief="groove", text="Oui", variable=divorce_var, value="Oui", bg="#f5f5f5").pack(side="left")
        Radiobutton(divorce_frame, relief="groove",  text="Non", variable=divorce_var, value="Non", bg="#f5f5f5").pack(side="left")


        # Zone où on affichera la date de divorce
        divorce_details_frame = Frame(content_frame, bg="#f5f5f5")
        divorce_details_frame.pack()


        def toggle_divorce(*args):
            # Vider la frame d'abord
            for widget in divorce_details_frame.winfo_children():
                widget.destroy()

            entry_dateDM_var.set("")
        
            if divorce_var.get() == "Oui":
                Label(divorce_details_frame, text="Date de divorce (JJ/MM/AAAA) :", bg="#f5f5f5").pack(pady=(10, 0))
                Entry(divorce_details_frame, relief="groove", bd=2, textvariable=entry_dateDM_var).pack()
            else:
                entry_dateDM_var.set("")
                
        divorce_var.trace("w", toggle_divorce)

                        
        return entry_dateM_var, entry_lieuM_var, divorce_var, entry_dateDM_var
    
    #------------------------------------------------------------------------------------------------------------

    # Fonction pour ajouter la première famille (lorsque la base est vide)
    @staticmethod
    def ajouter_premiere_famille(login, frame, callback_accueil):
        frames_stack = []
        frames = {}

        infos_famille = {
            'conjoint': None,
            'conjointe': None,
            'enfants': [],
            'ids_enfants': [],
            'nomE': None,
            'date_mariage': '',
            'lieu_mariage': '',
            'divorce': 'Non',
            'date_divorce': ''
        }

        for widget in frame.winfo_children():
            widget.pack_forget()


        def show_frame(frame_name, create_func=None):
            if frames_stack:
                frames_stack[-1].pack_forget()
            if frame_name not in frames and create_func:
                frames[frame_name] = create_func()
            frames_stack.append(frames[frame_name])
            frames[frame_name].pack(fill="both", expand=True)

        def revenir_en_arriere():
            if frames_stack:
                frames_stack[-1].pack_forget()
                frames_stack.pop()
                if frames_stack:
                    frames_stack[-1].pack(fill="both", expand=True)

        def create_main_form():

            content_frame = Frame(frame, bg="#F5F5F5")

            Label(content_frame, text="Ajouter votre première famille", font=("Helvetica", 20), bg="#f5f5f5").pack(pady=(60, 15))

            entry_dateM_var, entry_lieuM_var, divorce_var, entry_dateDM_var = Famille.saisie_info_famille(content_frame)

            
            def valider_famille():

                #Verification taille lieu mariage
                if len(entry_lieuM_var.get()) > 20:
                    messagebox.showerror("Erreur", "Le lieu du mariage doit contenir au max : 20 caractères")
                    return

                # Vérification de la validité de la date
                if entry_dateM_var.get() != "" and not Individu.date_valide(entry_dateM_var.get()):
                    messagebox.showerror("Erreur", "Veuillez saisir une date de mariage valide.")
                    return
                
                # Vérification de la validité de la date
                if entry_dateDM_var.get() != "" and not Individu.date_valide(entry_dateDM_var.get()):
                    messagebox.showerror("Erreur", "Veuillez saisir une date de divorce valide.")
                    return

                  #verification des dates 
                if entry_dateM_var.get() != "" and entry_dateDM_var.get() != "" and not Individu.date_coherente(entry_dateM_var.get(),entry_dateDM_var.get()):
                    messagebox.showerror("Erreur","On ne peut être divorcé sans être marié")
                    return

                infos_famille['date_mariage'] = entry_dateM_var.get()
                infos_famille['lieu_mariage'] = entry_lieuM_var.get()
                infos_famille['divorce'] = divorce_var.get()
                infos_famille['date_divorce'] = entry_dateDM_var.get() if divorce_var.get() == "Oui" else None
                saisir_conjoint()

            frame_bouton = Frame(content_frame, bg="#f5f5f5")
            frame_bouton.pack(pady=20)

            Button(frame_bouton, text="Suivant (Saisir conjoint_e)", command=valider_famille, bg="#41B77F", fg="white").pack(pady=10)
            Button(frame_bouton, text="Retour", command=callback_accueil, bg="#123", fg="white").pack(pady=10)
                
            return content_frame  
         
        def saisir_conjoint():
            
            def create_conjoint_frame():
                f = Frame(frame, bg="#f5f5f5")
                Label(f, text="Saisie du conjoint", font=("Helvetica", 20), fg="#41B77F").pack(pady=(60, 15))

                def traitement_conjoint(individu):
                    
                    infos_famille['conjoint'] = individu
                    individu.sexe = 'M'
                    infos_famille['nomE'] = individu.nom

                    saisir_conjointe()
                    

                Individu.saisir_conjoint_e(f, traitement_conjoint)

                Button(f, text="Retour", command=revenir_en_arriere, bg="#123", fg="white").pack(pady=10)

                return f

            show_frame("conjoint",create_conjoint_frame)

        def saisir_conjointe():
            #Verifier si l'individu à au moins 15ans
            if infos_famille["conjoint"].date_naissance != "" and infos_famille["date_mariage"] != "" and not Individu.difference_annees(infos_famille["conjoint"].date_naissance, infos_famille["date_mariage"], 15):
                messagebox.showerror("Erreur", "Il faut au moins 15ans pour se marier")
                return
            
            #Verifier si la date de décès de l'invidivu est supérieur à la date de mariage
            if infos_famille["conjoint"].deces == "oui" and infos_famille["conjoint"].date_deces != "" and infos_famille["date_mariage"] != "" and not Individu.date_coherente(infos_famille["date_mariage"], infos_famille["conjoint"].date_deces):
                messagebox.showerror("Erreur", "La date de mariage ne peut pas être supérieur à la date de décès")
                return
            
            def create_conjointe_frame():
                f = Frame(frame, bg="#f5f5f5")
                Label(f, text="Saisie de la conjointe", font=("Helvetica", 20), fg="#41B77F").pack(pady=(60, 15))

                def traitement_conjointe(individu):
                    
                    #Verifier si l'individu à au moins 15ans
                    if individu.date_naissance != "" and infos_famille["date_mariage"] != "" and not Individu.difference_annees(individu.date_naissance, infos_famille["date_mariage"], 15):
                        messagebox.showerror("Erreur", "Il faut au moins 15ans pour se marier")
                        return
                    
                    #Verifier si la date de décès de l'invidivu est supérieur à la date de mariage
                    if individu.deces == "oui" and individu.date_deces != "" and infos_famille["date_mariage"] != "" and not Individu.date_coherente(infos_famille["date_mariage"], individu.date_deces):
                        messagebox.showerror("Erreur", "La date de mariage ne peut pas être supérieur à la date de décès")
                        return
                    
                    infos_famille['conjointe'] = individu
                    individu.sexe = 'F'


                    if not infos_famille['enfants']:
                        if messagebox.askyesno("Ajouter un enfant", "Souhaitez-vous ajouter un enfant ?"):
                            ajouter_enfant()
                        else:
                            proposer_confirmation()
                    else:
                        proposer_confirmation()

                Individu.saisir_conjoint_e(f, traitement_conjointe)

                Button(f, text="Retour", command=revenir_en_arriere, bg="#123", fg="white").pack(pady=10)
               
                return f
            
            show_frame("conjointe",create_conjointe_frame)

        def ajouter_enfant():
            def create_enfant_frame():
                f = Frame(frame, bg="#f5f5f5")
                Label(f, text="Saisie d'un enfant", font=("Helvetica", 20), fg="#41B77F").pack(pady=(60, 15))

                nb_enfants_avant = len(infos_famille['enfants'])

                def retour_enfant():
                    if infos_famille['enfants']:
                        if len(infos_famille['enfants']) >= nb_enfants_avant:
                            infos_famille['enfants'].pop()
                    revenir_en_arriere()

                def traitement_enfant(enfant):
                    #Verifier si l'individu à au moins 15ans
                    if infos_famille["conjoint"].date_naissance != "" and enfant.date_naissance != "" and not Individu.difference_annees(infos_famille["conjoint"].date_naissance, enfant.date_naissance, 15):
                        messagebox.showerror("Erreur", "Il faut au moins 15ans entre l'enfant et ses parents")
                        return

                    #Verifier si l'individu à au moins 15ans
                    if infos_famille["conjointe"].date_naissance != "" and enfant.date_naissance != "" and not Individu.difference_annees(infos_famille["conjointe"].date_naissance, enfant.date_naissance, 15):
                        messagebox.showerror("Erreur", "Il faut au moins 15ans entre l'enfant et ses parents")
                        return
                    
                    infos_famille['enfants'].append(enfant)
                    if messagebox.askyesno("Ajouter un autre enfant ?", "Souhaitez-vous ajouter un autre enfant ?"):
                        ajouter_enfant()
                    else:
                        proposer_confirmation()

                Individu.saisir_enfant(f, infos_famille['nomE'], traitement_enfant)

                Button(f, text="Retour", command=retour_enfant, bg="#123", fg="white").pack(pady=10)

                return f

            show_frame(f"enfant_{len(infos_famille['enfants']) + 1}", create_enfant_frame)

        def proposer_confirmation():
            reponse = messagebox.askyesno("Confirmation", "Souhaitez-vous enregistrer cette famille ?")
            if reponse:
                enregistrer_famille()
                callback_accueil()
            else:
                callback_accueil()


        def enregistrer_famille():
            conjoint = infos_famille['conjoint']
            conjointe = infos_famille['conjointe']

            conjoint.ajouter_individu(login)
            conjointe.ajouter_individu(login)

            infos_famille['ids_enfants'] = []
            for enfant in infos_famille['enfants']:
                if enfant.nom == "":
                    enfant.nom = conjoint.nom

                enfant.ajouter_individu(login)
                infos_famille['ids_enfants'].append(enfant.id_individu)

            famille = Famille(
                date_mariage=infos_famille['date_mariage'],
                lieu_mariage=infos_famille['lieu_mariage'],
                divorce= infos_famille['divorce'].lower(),
                date_divorce=infos_famille['date_divorce'],
                id_conjoint=conjoint.id_individu,
                id_conjointe=conjointe.id_individu,
                ids_enfants=infos_famille['ids_enfants']
            )
            famille_id = famille.ajouter(login)

            famille.associer_a_individu(login, conjoint.id_individu)
            famille.associer_a_individu(login, conjointe.id_individu)

            conn = sqlite3.connect(login)
            c = conn.cursor()
            for enfant_id in infos_famille['ids_enfants']:
                c.execute("UPDATE Individu SET id_famille_issue = ? WHERE id_individu = ?", (famille_id, enfant_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Succès", "Famille enregistrée avec succès.")

        show_frame("main_form",create_main_form)
        

    #------------------------------------------------------------------------------------------------------------
    
    # Fonction pour ajouter une famille a un individu
    @staticmethod
    def ajouter_famille_a_un_individu(login, frame, individu, callback_recherche, callback_accueil):
        #Verifier si l'individu à au moins 15ans
        if individu.date_naissance != "" and not Individu.peut_se_marier(individu.date_naissance, 15):
            messagebox.showerror("Erreur", "Cet individu n'a pas l'âge requit pour se marier (Il faut au moins 15 ans)")
            return
        
        
        sexe = individu.sexe
        frames_stack = []
        frames = {}

        infos_famille = {
            'conjoint': None,
            'conjointe': None,
            'enfants': [],
            'ids_enfants': [],
            'nomE': None,
            'date_mariage': '',
            'lieu_mariage': '',
            'divorce': 'Non',
            'date_divorce': ''
        }

        infos_famille["conjoint"] = individu
        infos_famille["conjointe"] = individu

        for widget in frame.winfo_children():
            widget.pack_forget()

        def show_frame(frame_name, create_func=None):
            if frames_stack:
                frames_stack[-1].pack_forget()
            if frame_name not in frames and create_func:
                frames[frame_name] = create_func()
            frames_stack.append(frames[frame_name])
            frames[frame_name].pack(fill="both", expand=True)

        def revenir_en_arriere():
            if frames_stack:
                frames_stack[-1].pack_forget()
                frames_stack.pop()
                if frames_stack:
                    frames_stack[-1].pack(fill="both", expand=True)

        def create_main_form():
            content_frame = Frame(frame, bg="#f5f5f5")

            Label(content_frame, text="Ajouter votre famille", font=("Helvetica", 20), bg="#f5f5f5").pack(pady=(60, 15))

            entry_dateM_var, entry_lieuM_var, divorce_var, entry_dateDM_var = Famille.saisie_info_famille(content_frame)

            def valider_famille():

                #Verification taille lieu mariage
                if len(entry_lieuM_var.get()) > 20:
                    messagebox.showerror("Erreur", "Le lieu du mariage doit contenir au max : 20 caractères")
                    return
                
                # Vérification de la validité de la date
                if entry_dateM_var.get() != "" and not Individu.date_valide(entry_dateM_var.get()):
                    messagebox.showerror("Erreur", "Veuillez saisir une date de mariage valide.")
                    return
                
                # Vérification de la validité de la date
                if entry_dateDM_var.get() != "" and not Individu.date_valide(entry_dateDM_var.get()):
                    messagebox.showerror("Erreur", "Veuillez saisir une date de divorce valide.")
                    return
                
                  #verification des dates 
                if entry_dateM_var.get() != "" and entry_dateDM_var.get() != "" and not Individu.date_coherente(entry_dateM_var.get(),entry_dateDM_var.get()):
                    messagebox.showerror("Erreur","On ne peut être divorcé sans être marié")
                    return
            
                #Verifier si l'individu à au moins 15ans
                if individu.date_naissance != "" and entry_dateM_var.get() != "" and not Individu.difference_annees(individu.date_naissance, entry_dateM_var.get(), 15):
                    messagebox.showerror("Erreur", "Il faut au moins 15ans pour se marier")
                    return
                
                #Verifier si la date de décès de l'invidivu est supérieur à la date de mariage
                if individu.deces == "oui" and individu.date_deces != "" and entry_dateM_var.get() != "" and not Individu.date_coherente(entry_dateM_var.get(), individu.date_deces):
                    messagebox.showerror("Erreur", "La date de mariage ne peut pas être supérieur à la date de décès")
                    return

                infos_famille['date_mariage'] = entry_dateM_var.get()
                infos_famille['lieu_mariage'] = entry_lieuM_var.get()
                infos_famille['divorce'] = divorce_var.get()
                infos_famille['date_divorce'] = entry_dateDM_var.get() if divorce_var.get() == "Oui" else None

                if sexe == "M":
                    infos_famille["nomE"] = individu.nom
                    global nomE
                    nomE = individu.nom
                    saisir_conjointe()
                else:
                    saisir_conjoint()

            # Boutons à la fin
            frame_button = Frame(content_frame, bg="#f5f5f5")
            frame_button.pack(pady=20)

            Button(frame_button, text="Suivant (Saisir conjoint_e)", command=valider_famille, bg="#41B77F", fg="white").pack(pady=10)
            Button(frame_button, text="Retour", command=callback_recherche, bg="#123", fg="white").pack(pady=10)

            return content_frame



        def saisir_conjointe():
            def create_conjointe_frame():
                f = Frame(frame, bg="#f5f5f5")
                Label(f, text="Saisie de la conjointe", font=("Helvetica", 20), fg="#41B77F", bg="#f5f5f5").pack(pady=(60, 15))

                def traitement_conjointe(conjointe):

                    #Verifier si le conjoint à au moins 15ans
                    if conjointe.date_naissance != "" and infos_famille["date_mariage"] != "" and not Individu.difference_annees(conjointe.date_naissance, infos_famille["date_mariage"], 15):
                        messagebox.showerror("Erreur", "Il faut au moins 15ans pour se marier")
                        return
                    
                    #Verifier si la date de décès du conjoint est supérieur à la date de mariage
                    if conjointe.deces == "oui" and conjointe.date_deces != "" and infos_famille["date_mariage"] != "" and not Individu.date_coherente(infos_famille["date_mariage"], conjointe.date_deces):
                        messagebox.showerror("Erreur", "La date de mariage ne peut pas être supérieur à la date de décès")
                        return
                    
                    conjointe.sexe = "F"
                    infos_famille["conjointe"] = conjointe
                    if not infos_famille['enfants']:
                        if messagebox.askyesno("Ajouter un enfant", "Souhaitez-vous ajouter un enfant ?"):
                            ajouter_enfant()
                        else:
                            proposer_confirmation()
                    else:
                        proposer_confirmation()

                Individu.saisir_conjoint_e(f, traitement_conjointe)

                Button(f, text="Retour", command=revenir_en_arriere, bg="#123", fg="white").pack(pady=10)
                
                return f
            
               

            show_frame("conjointe", create_conjointe_frame)

        def saisir_conjoint():
            def create_conjoint_frame():
                f = Frame(frame, bg="#f5f5f5")
                Label(f, text="Saisie du conjoint", font=("Helvetica", 20), fg="#41B77F", bg="#f5f5f5").pack(pady=(60, 15))
                

                def traitement_conjoint(conjoint):

                    #Verifier si le conjoint à au moins 15ans
                    if conjoint.date_naissance != "" and infos_famille["date_mariage"] != "" and not Individu.difference_annees(conjoint.date_naissance, infos_famille["date_mariage"], 15):
                        messagebox.showerror("Erreur", "Il faut au moins 15ans pour se marier")
                        return
                    
                    #Verifier si la date de décès du conjoint est supérieur à la date de mariage
                    if conjoint.deces == "oui" and conjoint.date_deces != "" and infos_famille["date_mariage"] != "" and not Individu.date_coherente(infos_famille["date_mariage"], conjoint.date_deces):
                        messagebox.showerror("Erreur", "La date de mariage ne peut pas être supérieur à la date de décès")
                        return
            
                    
                    conjoint.sexe = "M"
                    infos_famille["conjoint"] = conjoint
                    infos_famille["nomE"] = conjoint.nom

                    if not infos_famille['enfants']:
                        if messagebox.askyesno("Ajouter un enfant", "Souhaitez-vous ajouter un enfant ?"):
                            ajouter_enfant()
                        else:
                            proposer_confirmation()
                    else:
                        proposer_confirmation()

                Individu.saisir_conjoint_e(f, traitement_conjoint)

                Button(f, text="Retour", command=revenir_en_arriere, bg="#123", fg="white").pack(pady=10)

                return f

            show_frame("conjoint", create_conjoint_frame)

        def ajouter_enfant():
            
            def create_enfant_frame():
                f = Frame(frame, bg="#f5f5f5")
                Label(f, text="Saisie d'un enfant", font=("Helvetica", 20), fg="#41B77F", bg="#f5f5f5").pack(pady=(60, 15))

                nb_enfants_avant = len(infos_famille['enfants'])

                def retour_enfant():
                    if infos_famille['enfants']:
                        if len(infos_famille['enfants']) >= nb_enfants_avant:
                            infos_famille['enfants'].pop()
                    revenir_en_arriere()

                def traitement_enfant(enfant):
                    #Verifier si l'individu à au moins 15ans
                    if infos_famille["conjoint"].date_naissance != "" and enfant.date_naissance != "" and not Individu.difference_annees(infos_famille["conjoint"].date_naissance, enfant.date_naissance, 15):
                        messagebox.showerror("Erreur", "Il faut au moins 15ans entre l'enfant et ses parents")
                        return

                    #Verifier si l'individu à au moins 15ans
                    if infos_famille["conjointe"].date_naissance != "" and enfant.date_naissance != "" and not Individu.difference_annees(infos_famille["conjointe"].date_naissance, enfant.date_naissance, 15):
                        messagebox.showerror("Erreur", "Il faut au moins 15ans entre l'enfant et ses parents")
                        return

                    
                    infos_famille['enfants'].append(enfant)
                    if messagebox.askyesno("Ajouter un autre enfant ?", "Souhaitez-vous ajouter un autre enfant ?"):
                        ajouter_enfant()
                    else:
                        proposer_confirmation()

                Individu.saisir_enfant(f, infos_famille['nomE'], traitement_enfant)

                Button(f, text="Retour", command=retour_enfant, bg="#123", fg="white").pack(pady=10)

                return f

            show_frame(f"enfant_{len(infos_famille['enfants']) + 1}", create_enfant_frame)

        def proposer_confirmation():
            if messagebox.askyesno("Confirmation", "Souhaitez-vous enregistrer cette famille ?"):
                enregistrer_famille()
                callback_accueil()
            else:
                callback_accueil()

        def enregistrer_famille():
            conjoint = infos_famille['conjoint']
            conjointe = infos_famille['conjointe']

            if sexe == "M":
                conjointe.ajouter_individu(login)
            else:
                conjoint.ajouter_individu(login)

            infos_famille['ids_enfants'] = []
            for enfant in infos_famille['enfants']:
                if enfant.nom == "":
                    enfant.nom = conjoint.nom
                enfant.ajouter_individu(login)
                infos_famille['ids_enfants'].append(enfant.id_individu)

            famille = Famille(
                date_mariage=infos_famille['date_mariage'],
                lieu_mariage=infos_famille['lieu_mariage'],
                divorce= infos_famille['divorce'].lower(),
                date_divorce=infos_famille['date_divorce'],
                id_conjoint=conjoint.id_individu,
                id_conjointe=conjointe.id_individu,
                ids_enfants=infos_famille['ids_enfants']
            )
            famille_id = famille.ajouter(login)

            famille.associer_a_individu(login, conjoint.id_individu)
            famille.associer_a_individu(login, conjointe.id_individu)

            conn = sqlite3.connect(login)
            c = conn.cursor()
            for enfant_id in infos_famille['ids_enfants']:
                c.execute("UPDATE Individu SET id_famille_issue = ? WHERE id_individu = ?", (famille_id, enfant_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Succès", "Famille enregistrée avec succès.")

        show_frame("main_form", create_main_form)

    #------------------------------------------------------------------------------------------------------------
     
    # Ajout d'une famille à deux individu
    def ajouter_famille_a_deux_individu(login, frame, id1, id2, callback_recherche, collback_accueil):
        
        #Verifier si l'individu à au moins 15ans
        if id2.date_naissance != "" and not Individu.peut_se_marier(id2.date_naissance, 15):
            messagebox.showerror("Erreur", "Cet individu n'a pas l'âge requit pour se marier (Il faut au moins 15 ans)")
            return
        
        frames_stack = []
        frames = {}

        infos_famille = {
            'conjoint': None,
            'conjointe': None,
            'enfants': [],
            'ids_enfants': [],
            'nomE': None,
            'date_mariage': '',
            'lieu_mariage': '',
            'divorce': 'Non',
            'date_divorce': ''
        }

        if id1.sexe == 'M':
            infos_famille["conjoint"] = id1
            infos_famille["conjointe"] = id2
            infos_famille["nomE"] = id1.nom
        else:
            infos_famille["conjoint"] = id2
            infos_famille["conjointe"] = id1
            infos_famille["nomE"] = id2.nom

        for widget in frame.winfo_children():
            widget.pack_forget()

        def show_frame(name, create_func=None):
            if frames_stack:
                frames_stack[-1].pack_forget()
            if name not in frames and create_func:
                frames[name] = create_func()
            if name not in frames_stack:
                frames_stack.append(frames[name])
            frames[name].pack(fill="both", expand=True)

        def revenir_en_arriere():
            if frames_stack:
                frames_stack[-1].pack_forget()
                frames_stack.pop()
                if frames_stack:
                    frames_stack[-1].pack(fill="both", expand=True)

        # Étape 1 : Formulaire mariage/divorce
        def create_main_form():
            content = Frame(frame, bg="#f5f5f5")
            Label(content, text="Ajouter votre famille", font=("Helvetica", 20), bg="#f5f5f5").pack(pady=(60, 15))

            entry_dateM, entry_lieuM, divorce_var, entry_dateDM = Famille.saisie_info_famille(content)

            def suivant():

                #Verification taille lieu mariage
                if len(entry_lieuM.get()) > 20:
                    messagebox.showerror("Erreur", "Le lieu du mariage doit contenir au max : 20 caractères")
                    return

                # Vérification de la validité de la date
                if entry_dateM.get() != "" and not Individu.date_valide(entry_dateM.get()):
                    messagebox.showerror("Erreur", "Veuillez saisir une date de mariage valide.")
                    return
                
                # Vérification de la validité de la date
                if entry_dateDM.get() != "" and not Individu.date_valide(entry_dateDM.get()):
                    messagebox.showerror("Erreur", "Veuillez saisir une date de divorce valide.")
                    return
                  #verification des dates 
                if entry_dateM.get() != "" and entry_dateDM.get() != "" and not Individu.date_coherente(entry_dateM.get(),entry_dateDM.get()):
                    messagebox.showerror("Erreur","On ne peut être divorcé sans être marié")
                    return
                
                #Verifier s'il y'a au moins 15ans entre la date de naissance et la date de mariage
                if id1.date_naissance != "" and entry_dateM.get() != "" and not Individu.difference_annees(id1.date_naissance, entry_dateM.get(), 15):
                    messagebox.showerror("Erreur", "Il faut au moins 15ans pour se marier")
                    return
                
                #Verifier s'il y'a au moins 15ans entre la date de naissance et la date de mariage
                if id2.date_naissance != "" and entry_dateM.get() != "" and not Individu.difference_annees(id2.date_naissance, entry_dateM.get(), 15):
                    messagebox.showerror("Erreur", "Il faut au moins 15ans pour se marier")
                    return
                
                #Verifier si la date de décès du conjoint est supérieur à la date de mariage
                if id1.deces == "oui" and id1.date_deces != "" and entry_dateM.get() != "" and not Individu.date_coherente(entry_dateM.get(), id1.date_deces):
                    messagebox.showerror("Erreur", "La date de mariage ne peut pas être supérieur à la date de décès")
                    return
                
                #Verifier si la date de décès du conjoint est supérieur à la date de mariage
                if id2.deces == "oui" and id2.date_deces != "" and entry_dateM.get() != "" and not Individu.date_coherente(entry_dateM.get(), id2.date_deces):
                    messagebox.showerror("Erreur", "La date de mariage ne peut pas être supérieur à la date de décès")
                    return

                infos_famille['date_mariage'] = entry_dateM.get()
                infos_famille['lieu_mariage'] = entry_lieuM.get()
                infos_famille['divorce'] = divorce_var.get()
                infos_famille['date_divorce'] = entry_dateDM.get() if divorce_var.get() == "Oui" else None

                if messagebox.askyesno("Ajouter un enfant", "Souhaitez-vous ajouter un enfant ?"):
                    ajouter_enfant()
                else:
                    proposer_confirmation()

            Button(content, text="Suivant", command=suivant, bg="#41B77F", fg="white").pack(pady=15)
            Button(content, text="Retour", command=callback_recherche, bg="#123", fg="white").pack(pady=10)

            return content

        # Étape 2 : Ajout enfant
        def ajouter_enfant():
            def create_enfant_frame():
                f = Frame(frame, bg="#f5f5f5")
                Label(f, text="Saisie d'un enfant", font=("Helvetica", 15), fg="#41B77F", bg="#f5f5f5").pack(pady=(60, 15))

                nb_enfants_avant = len(infos_famille['enfants'])

                def retour_enfant():
                    if infos_famille["enfants"]:
                        if len(infos_famille['enfants']) >= nb_enfants_avant:
                            infos_famille['enfants'].pop()
                    revenir_en_arriere()

                def traitement_enfant(enfant):
                    #Verifier si l'individu à au moins 15ans
                    if infos_famille["conjoint"].date_naissance != "" and enfant.date_naissance != "" and not Individu.difference_annees(infos_famille["conjoint"].date_naissance, enfant.date_naissance, 15):
                        messagebox.showerror("Erreur", "Il faut au moins 15ans entre l'enfant et ses parents")
                        return

                    #Verifier si l'individu à au moins 15ans
                    if infos_famille["conjointe"].date_naissance != "" and enfant.date_naissance != "" and not Individu.difference_annees(infos_famille["conjointe"].date_naissance, enfant.date_naissance, 15):
                        messagebox.showerror("Erreur", "Il faut au moins 15ans entre l'enfant et ses parents")
                        return
                    
                    infos_famille['enfants'].append(enfant)
                    if messagebox.askyesno("Ajouter un autre enfant ?", "Souhaitez-vous en ajouter un autre ?"):
                        ajouter_enfant()
                    else:
                        proposer_confirmation()

                Individu.saisir_enfant(f, infos_famille['nomE'], traitement_enfant)
                Button(f, text="Retour", command=retour_enfant, bg="#123", fg="white").pack(pady=10)

                return f

            show_frame(f"enfant_{len(infos_famille['enfants'])+1}", create_enfant_frame)

        # Étape finale : Enregistrement
        def proposer_confirmation():
            if messagebox.askyesno("Confirmation", "Souhaitez-vous enregistrer cette famille ?"):
                enregistrer_famille()
                collback_accueil()
            else:
                collback_accueil()

        def enregistrer_famille():
            conjoint = infos_famille['conjoint']
            conjointe = infos_famille['conjointe']

            infos_famille['ids_enfants'] = []
            for enfant in infos_famille['enfants']:
                if enfant.nom == "":
                    enfant.nom = conjoint.nom

                enfant.ajouter_individu(login)
                infos_famille['ids_enfants'].append(enfant.id_individu)

            famille = Famille(
                date_mariage=infos_famille['date_mariage'],
                lieu_mariage=infos_famille['lieu_mariage'],
                divorce= infos_famille['divorce'].lower(),
                date_divorce=infos_famille['date_divorce'],
                id_conjoint=conjoint.id_individu,
                id_conjointe=conjointe.id_individu,
                ids_enfants=infos_famille['ids_enfants']
            )
            famille_id = famille.ajouter(login)
            famille.associer_a_individu(login, conjoint.id_individu)
            famille.associer_a_individu(login, conjointe.id_individu)

            conn = sqlite3.connect(login)
            c = conn.cursor()
            for enfant_id in infos_famille['ids_enfants']:
                c.execute("UPDATE Individu SET id_famille_issue = ? WHERE id_individu = ?", (famille_id, enfant_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Succès", "Famille enregistrée avec succès.")

        # Lancer l'interface
        show_frame("main_form", create_main_form)


    #------------------------------------------------------------------------------------------------------------

    # Ajouter des parents à individu
    @staticmethod
    def ajouter_parents(login, frame, enfant, callback_recherche, callback_accueil):

        frames_stack = []
        frames = {}

        infos_famille = {
            'conjoint': None,
            'conjointe': None,
            'date_mariage': '',
            'lieu_mariage': '',
            'divorce': 'Non',
            'date_divorce': ''
        }

        for widget in frame.winfo_children():
            widget.pack_forget()


        def show_frame(frame_name, create_func=None):
            if frames_stack:
                frames_stack[-1].pack_forget()
            if frame_name not in frames and create_func:
                frames[frame_name] = create_func()
            frames_stack.append(frames[frame_name])
            frames[frame_name].pack(fill="both", expand=True)

        def revenir_en_arriere():
            if frames_stack:
                frames_stack[-1].pack_forget()
                frames_stack.pop()
                if frames_stack:
                    frames_stack[-1].pack(fill="both", expand=True)

        def create_main_form():

            content_frame = Frame(frame, bg="#F5F5F5")

            Label(content_frame, text="Ajouter la famille:", font=("Helvetica", 18), bg="#f5f5f5").pack(pady=(30, 0))

            entry_dateM_var, entry_lieuM_var, divorce_var, entry_dateDM_var = Famille.saisie_info_famille(content_frame)

            def valider_famille():
                # Vérification de la validité de la date
                if entry_dateM_var.get() != "" and not Individu.date_valide(entry_dateM_var.get()):
                    messagebox.showerror("Erreur", "Veuillez saisir une date de mariage valide.")
                    return
                
                # Vérification de la validité de la date
                if entry_dateDM_var.get() != "" and not Individu.date_valide(entry_dateDM_var.get()):
                    messagebox.showerror("Erreur", "Veuillez saisir une date de divorce valide.")
                    return
                
                   #verification des dates 
                if entry_dateM_var.get() != "" and entry_dateDM_var.get() != "" and not Individu.date_coherente(entry_dateM_var.get(),entry_dateDM_var.get()):
                    messagebox.showerror("Erreur","On ne peut être divorcé sans être marié")
                    return

                infos_famille['date_mariage'] = entry_dateM_var.get()
                infos_famille['lieu_mariage'] = entry_lieuM_var.get()
                infos_famille['divorce'] = divorce_var.get()
                infos_famille['date_divorce'] = entry_dateDM_var.get() if divorce_var.get() == "Oui" else None
                saisir_conjoint()

            frame_bouton = Frame(content_frame, bg="#f5f5f5")
            frame_bouton.pack(pady=20)

            Button(frame_bouton, text="Suivant (Saisir conjoint_e)", command=valider_famille, bg="#41B77F", fg="white").pack(pady=10)
            Button(frame_bouton, text="Retour", command=callback_recherche, bg="#123", fg="white").pack(pady=5)
                
            return content_frame  
         
        def saisir_conjoint():
            
            def create_conjoint_frame():
                f = Frame(frame, bg="#f5f5f5")
                Label(f, text="Saisie du père:", font=("Helvetica", 15), fg="#41B77F").pack(pady=(18, 0))

                def traitement_conjoint(individu):
                    
                    #Verifier si l'individu à au moins 15ans
                    if individu.date_naissance != "" and enfant.date_naissance != "" and not Individu.difference_annees(individu.date_naissance, enfant.date_naissance, 15):
                        messagebox.showerror("Erreur", "Il faut au moins 15ans entre l'enfant et son père")
                        return
                    
                    #Verifier s'il y'a au moins 15ans entre la date de naissance et la date de mariage
                    if individu.date_naissance != "" and infos_famille["date_mariage"] != "" and not Individu.difference_annees(individu.date_naissance, infos_famille["date_mariage"], 15):
                        messagebox.showerror("Erreur", "Il faut au moins 15ans pour se marier")
                        return
                    
                    #Verifier si la date de décès du conjoint est supérieur à la date de mariage
                    if individu.deces == "oui" and individu.date_deces != "" and infos_famille["date_mariage"] != "" and not Individu.date_coherente(infos_famille["date_mariage"], individu.date_deces):
                        messagebox.showerror("Erreur", "La date de mariage ne peut pas être supérieur à la date de décès")
                        return
                    

                    infos_famille['conjoint'] = individu
                    individu.sexe = 'M'
                    saisir_conjointe()
                

                Individu.saisir_conjoint_e(f,  traitement_conjoint, enfant.nom)

                Button(f, text="Retour", command=revenir_en_arriere, bg="#123", fg="white").pack(pady=5)

                return f

            show_frame("conjoint",create_conjoint_frame)

        def saisir_conjointe():
            def create_conjointe_frame():
                f = Frame(frame, bg="#f5f5f5")
                Label(f, text="Saisie de la mère", font=("Helvetica", 15), fg="#41B77F").pack(pady=(18, 0))

                def traitement_conjointe(individu):
                    
                    #Verifier si l'individu à au moins 15ans
                    if individu.date_naissance != "" and enfant.date_naissance != "" and not Individu.difference_annees(individu.date_naissance, enfant.date_naissance, 15):
                        messagebox.showerror("Erreur", "Il faut au moins 15ans entre l'enfant et sa mère")
                        return
                    
                    #Verifier s'il y'a au moins 15ans entre la date de naissance et la date de mariage
                    if individu.date_naissance != "" and infos_famille["date_mariage"] != "" and not Individu.difference_annees(individu.date_naissance, infos_famille["date_mariage"], 15):
                        messagebox.showerror("Erreur", "Il faut au moins 15ans pour se marier")
                        return
                    
                    #Verifier si la date de décès du conjoint est supérieur à la date de mariage
                    if individu.deces == "oui" and individu.date_deces != "" and infos_famille["date_mariage"] != "" and not Individu.date_coherente(infos_famille["date_mariage"], individu.date_deces):
                        messagebox.showerror("Erreur", "La date de mariage ne peut pas être supérieur à la date de décès")
                        return
                    
                    infos_famille['conjointe'] = individu
                    individu.sexe = 'F'

                    proposer_confirmation()

                Individu.saisir_conjoint_e(f, traitement_conjointe)

                Button(f, text="Retour", command=revenir_en_arriere, bg="#123", fg="white").pack(pady=5)
               
                return f
            
            show_frame("conjointe",create_conjointe_frame)
       

        def proposer_confirmation():
            
            reponse = messagebox.askyesno("Confirmation", "Souhaitez-vous enregistrer cette famille ?")
            if reponse:
                enregistrer_famille()
                callback_accueil()
            else:
                callback_accueil()


        def enregistrer_famille():
            conjoint = infos_famille['conjoint']
            conjointe = infos_famille['conjointe']

            conjoint.ajouter_individu(login)
            conjointe.ajouter_individu(login)

            famille = Famille(
                date_mariage=infos_famille['date_mariage'],
                lieu_mariage=infos_famille['lieu_mariage'],
                divorce= infos_famille['divorce'].lower(),
                date_divorce=infos_famille['date_divorce'],
                id_conjoint=conjoint.id_individu,
                id_conjointe=conjointe.id_individu,
                ids_enfants= enfant.id_individu
            )
            famille_id = famille.ajouter(login)

            famille.associer_a_individu(login, conjoint.id_individu)
            famille.associer_a_individu(login, conjointe.id_individu)

            conn = sqlite3.connect(login)
            c = conn.cursor()


            c.execute("UPDATE Individu SET id_famille_issue = ? WHERE id_individu = ?", (famille_id, enfant.id_individu))
            conn.commit()
            conn.close()

            messagebox.showinfo("Succès", "Famille enregistrée avec succès.")

        show_frame("main_form",create_main_form)


    #------------------------------------------------------------------------------------------------------------

    #Fontion pour rechercher une famille
    def afficher_recherche_famille(login, frame, callback_selection):
        import sqlite3
        from tkinter import Label, Entry, StringVar, Listbox, Scrollbar, Frame, END
        

        # Nettoyer le frame
        for widget in frame.winfo_children():
            widget.destroy()

        Label(frame, text="Rechercher une famille", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=(20, 10))
        Label(frame, text="Rechercher en fonction du lieu ou de la date de mariage", font=("Helvetica", 10, "normal"), bg="#f5f5f5").pack(pady=(0, 10))

        search_var = StringVar()
        search_entry = Entry(frame, textvariable=search_var, font=("Helvetica", 12), width=40)
        search_entry.pack(pady=5)

        listbox_frame = Frame(frame, width=600, height=300)
        listbox_frame.pack(pady=10, padx=10)

        listbox = Listbox(listbox_frame, width=50, font=("Helvetica", 11), height=20)
        listbox.pack(side="left", fill="both", expand=True)

        scrollbar = Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.config(yscrollcommand=scrollbar.set)

        familles_resultats = []

        def update_list(*args):
            query = search_var.get().strip().lower()
            listbox.delete(0, END)
            familles_resultats.clear()

            conn = sqlite3.connect(login)
            c = conn.cursor()
            c.execute("SELECT * FROM Famille")

            for row in c.fetchall():
                if len(row) >= 7:
                    id_famille, date_mariage, lieu_mariage, divorce, date_divorce, id_conjoint, id_conjointe = row[:7]
                    label = f"{date_mariage or ''} {lieu_mariage or ''}".lower()

                    if query in label:
                        familles_resultats.append(row)
                        listbox.insert(END, f"Famille {id_famille} - Mariage: {date_mariage} à {lieu_mariage}")

            conn.close()

        def on_select(event):
            index = listbox.curselection()
            if index:
                row = familles_resultats[index[0]]
                id_famille, date_mariage, lieu_mariage, divorce, date_divorce, id_conjoint, id_conjointe = row[:7]

                conn = sqlite3.connect(login)
                c = conn.cursor()
                c.execute("SELECT id_individu FROM Individu WHERE id_famille_issue = ?", (id_famille,))
                ids_enfants = [r[0] for r in c.fetchall()]
                conn.close()

                famille = Famille(
                    id_famille=id_famille,
                    date_mariage=date_mariage,
                    lieu_mariage=lieu_mariage,
                    divorce=divorce,
                    date_divorce=date_divorce,
                    id_conjoint=id_conjoint,
                    id_conjointe=id_conjointe,
                    ids_enfants=ids_enfants
                )

                callback_selection(famille)

        def on_hover(event):
            index = listbox.nearest(event.y)
            if index >= 0:
                for i in range(listbox.size()):
                    listbox.itemconfig(i, {'bg': 'white'})
                listbox.itemconfig(index, {'bg': '#d3d3d3'})

        def on_leave(event):
            index = listbox.nearest(event.y)
            if index >= 0:
                listbox.itemconfig(index, {'bg': 'white'})

        listbox.bind("<Motion>", on_hover)
        listbox.bind("<Leave>", on_leave)
        search_var.trace("w", update_list)
        listbox.bind("<<ListboxSelect>>", on_select)
        search_entry.focus_set()


    #------------------------------------------------------------------------------------------------------------

    #Fontion pour afficher une famille
    def afficher_famille(login, frame, famille: 'Famille', callback_retour):
        # Nettoyer le frame
        for widget in frame.winfo_children():
            widget.destroy()

        Label(frame, text="Détails de la famille", font=("Helvetica", 18, "bold"), bg="#f5f5f5").pack(pady=20)

        # Connexion à la base
        conn = sqlite3.connect(login)
        c = conn.cursor()

        # Fonction pour récupérer nom complet d’un individu
        def get_nom_prenom(id_individu):
            c.execute("SELECT prenom, nom FROM Individu WHERE id_individu = ?", (id_individu,))
            row = c.fetchone()
            return f"{row[0]} {row[1]}" if row else "Inconnu"

        conjoint_nom = get_nom_prenom(famille.id_conjoint)
        conjointe_nom = get_nom_prenom(famille.id_conjointe)

        enfants_noms = []
        for id_enfant in famille.ids_enfants:
            enfants_noms.append(get_nom_prenom(id_enfant))

        conn.close()

        # Affichage des infos
        info_frame = Frame(frame, bg="#f5f5f5")
        info_frame.pack(pady=10)

        infos = [
            ("Conjoint :", conjoint_nom),
            ("Conjointe :", conjointe_nom),
            ("Date de mariage :", famille.date_mariage or "Non renseignée"),
            ("Lieu de mariage :", famille.lieu_mariage or "Non renseigné"),
            ("Divorcé(e) :", "Oui" if famille.divorce == "oui" else "Non"),
        ]

        if famille.divorce:
            infos.append(("Date de divorce :", famille.date_divorce or "Non renseignée"))

        for label, value in infos:
            ligne_frame = Frame(info_frame, bg="#f5f5f5")
            ligne_frame.pack(anchor="w", pady=2)

            Label(ligne_frame, text=label, font=("Helvetica", 12, "bold"), bg="#f5f5f5").pack(side="left")
            Label(ligne_frame, text=value, font=("Helvetica", 12), bg="#f5f5f5", wraplength=400, justify="left").pack(side="left")

        # Affichage des enfants
        Label(info_frame, text="Enfants :", font=("Helvetica", 12, "bold"), bg="#f5f5f5").pack(anchor="center", padx=20, pady=(10, 2))
        if enfants_noms:
            # Frame parent pour contenir la zone scrollable
            scrollable_container = Frame(frame, bg="#f5f5f5")
            scrollable_container.pack(padx=10, pady=10, fill="both")  # fill="x" ou rien si tu veux pas l'étendre verticalement

            # Création du canvas avec une hauteur fixée
            canvas = Canvas(scrollable_container, bg="white", highlightthickness=0, width=320, height=150)
            canvas.pack(side="left", expand=True, padx=(10, 0))

            # Ajout de la scrollbar
            scrollbar = Scrollbar(scrollable_container, orient="vertical", command=canvas.yview)
            scrollbar.pack(side="right", fill="y")

            # Config canvas pour gérer le scroll
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

            # Frame interne dans le canvas
            enfants_frame = Frame(canvas, bg="white")
            canvas.create_window((0, 0), window=enfants_frame, anchor="n")

            enfants_frame = Frame(canvas, bg="white", width=320)
            window_id = canvas.create_window((0, 0), window=enfants_frame, anchor="n")

            def resize_content(event):
                # Centrer horizontalement sans dépasser max_width
                canvas_width = event.width
                content_width = min(canvas_width, 320)
                x_offset = (canvas_width - content_width) // 2
                canvas.coords(window_id, x_offset, 0)
                canvas.itemconfig(window_id, width=content_width)
                canvas.configure(scrollregion=canvas.bbox("all"))

            canvas.bind('<Configure>', resize_content)

            # Ajout des noms des enfants
            for nom in enfants_noms:
                Label(enfants_frame, text=f"- {nom}", font=("Helvetica", 11),bg="white", wraplength=280, justify="center").pack(anchor="center", padx=(10, 0), pady=1)

        else:
            Label(info_frame, text="Aucun enfant", font=("Helvetica", 11, "italic"), bg="white").pack(anchor="center", padx=40)

      # Frame pour les boutons en ligne
        button_frame = Frame(frame, bg="#f5f5f5")
        button_frame.pack(pady=20)

        Button(button_frame, text="Retour", command=callback_retour, bg="#123", fg="white").pack(side="left", padx=10)
        Button(button_frame, text="Voir options", command= lambda: Famille.modifier_famille(login, frame, famille, callback_retour), bg="#41B77F", fg="white").pack(side="left", padx=10)


    #------------------------------------------------------------------------------------------------------------

    #Fonction qui recherche une famille
    @staticmethod
    def rechercher_famille_par_id(id_famille, login):
        import sqlite3
        conn = sqlite3.connect(login)
        c = conn.cursor()

        c.execute("SELECT * FROM Famille WHERE id_mariage = ?", (id_famille,))
        row = c.fetchone()
        conn.close()

        if row:
            # récupérer tous les champs
            id_famille, date_mariage, lieu_mariage, divorce, date_divorce, id_conjoint, id_conjointe, ids_enfants = row

            # Convertir ids_enfants en liste propre
            if isinstance(ids_enfants, str):
                ids_enfants = [e.strip() for e in ids_enfants.split(",") if e.strip()]

            return Famille(id_famille=id_famille,
                        date_mariage=date_mariage,
                        lieu_mariage=lieu_mariage,
                        divorce=divorce,
                        date_divorce=date_divorce,
                        id_conjoint=id_conjoint,
                        id_conjointe=id_conjointe,
                        ids_enfants=ids_enfants)
        return None


    #Fontion pour modifier la famille
    def modifier_famille(login, frame, famille: 'Famille', callback_retour):

        #recuperer la famille
        famille = Famille.rechercher_famille_par_id(famille.id_famille, login)

        # Nettoyer le frame
        for widget in frame.winfo_children():
            widget.destroy()

        Label(frame, text="Modification de la famille", font=("Helvetica", 18, "bold"), bg="#f5f5f5").pack(pady=20)

          # Bouton 1
        Button(frame, text="Ajouter des enfants", font=("Arial", 15), width=30, fg="black", bg="#CCCCCC", cursor="hand2",
               command=lambda:Famille.traiter_enfant(login, frame, famille, lambda:Famille.modifier_famille(login, frame, famille, callback_retour))).pack(pady=10)

        # Bouton 2
        Button(frame, text="Modifier les infos", font=("Arial", 15), width=30, fg="black", bg="#CCCCCC", cursor="hand2",
              command= lambda: Famille.modifier_info(login,frame,famille,lambda:Famille.modifier_famille(login, frame, famille, callback_retour)) ).pack(pady=10)

        #Bouton retour
        Button(frame, text="Retour", command=lambda: Famille.afficher_famille(login, frame, famille, callback_retour), bg="#123", fg="white", justify="center").pack(padx=10, pady=10)
    
    #Fonction traiter_enfant pour ajouter des enfants à un individu
    def traiter_enfant(login, frame, famille: 'Famille', callback_retour):
        frames_stack = []
        frames = {}

        infos_famille = {
            'enfants': [],
            'ids_enfants': []
        }

        conn = sqlite3.connect(login)
        c = conn.cursor()
        # Récupérer les champs dans l’ordre correct
        c.execute("SELECT id_conjoint, id_conjointe FROM Famille WHERE id_mariage = ?", (famille.id_famille,))
        result = c.fetchone()
        if result:
            id_conjoint = int(result[0])
            id_conjointe = int(result[1])

            c.execute("SELECT nom, date_naissance FROM Individu WHERE id_individu = ?", (id_conjoint,))
            requete_conjoint = c.fetchone()
            if requete_conjoint:
                nom = str(requete_conjoint[0])
                date_naiss_conjoint = str(requete_conjoint[1])
            
            c.execute("SELECT date_naissance FROM Individu WHERE id_individu = ?", (id_conjointe,))
            requete_conjointe = c.fetchone()
            if requete_conjointe:
                date_naiss_conjointe = str(requete_conjointe[0])
            

        for widget in frame.winfo_children():
            widget.pack_forget()

        def show_frame(name, create_func=None):
            if frames_stack:
                frames_stack[-1].pack_forget()
            if name not in frames and create_func:
                frames[name] = create_func()
            if name not in frames_stack:
                frames_stack.append(frames[name])
            frames[name].pack(fill="both", expand=True)

        def revenir_en_arriere():
            if frames_stack:
                frames_stack[-1].pack_forget()
                frames_stack.pop()
                if frames_stack:
                    frames_stack[-1].pack(fill="both", expand=True)

            
        def ajouter_enfant():

            def create_enfant_frame():
                f = Frame(frame, bg="#f5f5f5")
                Label(f, text="Saisie d'un enfant", font=("Helvetica", 15), fg="#41B77F", bg="#f5f5f5").pack(pady=(18, 0))

                nb_enfants_avant = len(infos_famille['enfants'])

                def retour_enfant():
                    if infos_famille['enfants']:
                        if len(infos_famille['enfants']) >= nb_enfants_avant:
                            infos_famille['enfants'].pop()
                    revenir_en_arriere()

                def traitement_enfant(enfant):
                    
                    if date_naiss_conjoint != "" and enfant.date_naissance != "" and not Individu.difference_annees(date_naiss_conjoint, enfant.date_naissance, 15):
                        messagebox.showerror("Erreur", "Il faut au moins 15ans entre l'enfant et son père")
                        return
                    
                    if date_naiss_conjointe != "" and enfant.date_naissance != "" and not Individu.difference_annees(date_naiss_conjointe, enfant.date_naissance, 15):
                        messagebox.showerror("Erreur", "Il faut au moins 15ans entre l'enfant et sa mère")
                        return

                    infos_famille['enfants'].append(enfant)
                    if messagebox.askyesno("Ajouter un autre enfant ?", "Souhaitez-vous ajouter un autre enfant ?"):
                        ajouter_enfant()
                    else:
                        proposer_confirmation()

                Individu.saisir_enfant(f, nom, traitement_enfant)

                if(nb_enfants_avant >= 1):
                    Button(f, text="Retour", command=lambda: retour_enfant(), bg="#123", fg="white").pack(pady=5)    
                else:
                    Button(f, text="Retour", command=lambda: Famille.modifier_famille(login, frame, famille, callback_retour), bg="#123", fg="white").pack(pady=5)

                return f

            show_frame(f"enfant_{len(infos_famille['enfants']) + 1}", create_enfant_frame)

            def proposer_confirmation():
                if messagebox.askyesno("Confirmation", "Souhaitez-vous enregistrer ces enfants ?"):
                    enregistrer_famille()
                    callback_retour()
                else:
                    callback_retour()


        def enregistrer_famille():

            conn = sqlite3.connect(login)
            c = conn.cursor()

            infos_famille['ids_enfants'] = []
            for enfant in infos_famille['enfants']:
                enfant.ajouter_individu(login)
                infos_famille['ids_enfants'].append(enfant.id_individu)

            for enfant_id in infos_famille['ids_enfants']:
                c.execute("UPDATE Individu SET id_famille_issue = ? WHERE id_individu = ?", (famille.id_famille, enfant_id))

            conn.commit()

            c.execute("""SELECT ids_enfants     
                            FROM Famille WHERE id_mariage = ?""",(famille.id_famille,))
            
            ids_enfants = c.fetchone()

            ids_enfants = ids_enfants+tuple(infos_famille['ids_enfants'])

            if isinstance(ids_enfants, tuple):  # Vérifier si c'est un tuple 
                ids_enfant_str = ','.join(map(str, ids_enfants)) #si c'est un tuple le tranforme en str

            c.execute("""
                UPDATE Famille
                SET ids_enfants = ?
                WHERE id_mariage = ?
                """, (ids_enfant_str ,famille.id_famille))
            
            conn.commit()

            conn.close()

            messagebox.showinfo("Succès", "Enfants ajoutés avec succès.")
            
        ajouter_enfant()

    #------------------------------------------------------------------------------------------------------------

    #Modifier les infos de la famille
    def modifier_info(login, frame, famille: 'Famille', callback_retour):
        # Vider le frame actuel
        for widget in frame.winfo_children():
            widget.pack_forget()

        frame.config(bg="#f5f5f5")

        # Utiliser StringVar pour les champs modifiables
        date_mariage_var = StringVar(value=famille.date_mariage or "")
        lieu_mariage_var = StringVar(value=famille.lieu_mariage or "")
        divorce_valeur = str(famille.divorce)
        divorce_var = StringVar(value="Oui" if divorce_valeur.lower() == "oui" else "Non")
        date_divorce_var = StringVar(value=famille.date_divorce or "")

        # === Affichage des infos ===
        Label(frame, text="Modifier les informations de la famille", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=10)

        Label(frame, text="Date de mariage (YYYY-MM-DD) :", bg="#f5f5f5").pack(pady=5)
        Entry(frame, relief="groove", bd=2, textvariable=date_mariage_var).pack()

        Label(frame, text="Lieu de mariage :", bg="#f5f5f5").pack(pady=5)
        Entry(frame, relief="groove", bd=2, textvariable=lieu_mariage_var).pack()

        Label(frame, text="La famille est-elle divorcée ?", bg="#f5f5f5").pack(pady=5)
        divorce_frame = Frame(frame, bg="#f5f5f5")
        divorce_frame.pack()

        Radiobutton(divorce_frame, text="Oui", variable=divorce_var, value="Oui", bg="#f5f5f5").pack(side="left", padx=5)
        Radiobutton(divorce_frame, text="Non", variable=divorce_var, value="Non", bg="#f5f5f5").pack(side="left", padx=5)

        # Zone dynamique pour la date de divorce
        divorce_details_frame = Frame(frame, bg="#f5f5f5")
        divorce_details_frame.pack()

        def toggle_divorce(*args):
            for widget in divorce_details_frame.winfo_children():
                widget.destroy()

        
            if divorce_var.get().lower() == "oui":
                Label(divorce_details_frame, text="Date de divorce (JJ/MM/AAAA) :", bg="#f5f5f5").pack(pady=(10, 0))
                Entry(divorce_details_frame, relief="groove", bd=2, textvariable=date_divorce_var).pack()
            else:
                date_divorce_var.set("")
                
        # Appel initial et liaison
        toggle_divorce()
        divorce_var.trace("w", toggle_divorce)


        # Boutons
        frame_button = Frame(frame, bg="#f5f5f5")
        frame_button.pack(pady=20)

        def proposer_confirmation():

            if len(lieu_mariage_var.get()) > 20:
                messagebox.showerror("Erreur", "Le lieu du mariage doit contenir au max : 20 caractères")
                return

            # Vérification de la validité de la date
            if date_mariage_var.get() != "" and not Individu.date_valide(date_mariage_var.get()):
                messagebox.showerror("Erreur", "Veuillez saisir une date de mariage valide.")
                return
                    
            # Vérification de la validité de la date
            if date_divorce_var.get() != "" and not Individu.date_valide(date_divorce_var.get()):
                messagebox.showerror("Erreur", "Veuillez saisir une date de divorce valide.")
                return
            #verification des dates 
            if date_mariage_var.get() != "" and date_divorce_var.get() != "" and not Individu.date_coherente(date_mariage_var.get(),date_divorce_var.get()):
                messagebox.showerror("Erreur","On ne peut être divorcé sans être marié")
                return
    
            if messagebox.askyesno("Confirmation", "Souhaitez-vous enregistrer les modifications ?"):
                valider_famille()
                callback_retour()
            else:
                callback_retour()


        def valider_famille():

            # Mise à jour des données de l'objet famille
            famille.date_mariage = date_mariage_var.get()
            famille.lieu_mariage = lieu_mariage_var.get()
            famille.divorce = "oui" if divorce_var.get().lower() == "oui" else "non"
            famille.date_divorce = date_divorce_var.get() if famille.divorce.lower() == "oui" else None

            # Enregistrement dans la base de données
            conn = sqlite3.connect(login)
            c = conn.cursor()

            c.execute("""
                UPDATE famille 
                SET date_mariage = ?, lieu_mariage = ?, divorce = ?, date_divorce = ?
                WHERE id_mariage = ?
            """, (famille.date_mariage, famille.lieu_mariage, famille.divorce, famille.date_divorce, famille.id_famille))

            conn.commit()
            conn.close()

            messagebox.showinfo("Succès", "Modifications enregistrés avec succès.")

            # Callback de retour
            callback_retour()

       
        Button(frame_button, text="Retour", command=lambda: Famille.modifier_famille(login, frame, famille, callback_retour), bg="#123", fg="white").pack(side="left", padx=10)
        Button(frame_button, text="Valider", command=proposer_confirmation, bg="#41B77F", fg="white").pack(side="left", padx=10)
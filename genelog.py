import hashlib
import os
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
from admin import connexion, insertion, creation, verifier_compte, hasher_mot_de_passe
from ajouter_famille import ajouter_famille
from rechercher import rechercher
from model import initialiser_base_de_donnees
import sqlite3
import re
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


#Police de texte
my_font = "Helvetica 12"

# Initialisation la base de données
creation()

#Fenêtre principale
root = Tk()
root.title("GeneLog")
root.iconbitmap("images/logo.ico")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
width, height = 600, 550
x = (screen_width // 2) - (width // 2)
y = (screen_height // 2) - (height // 2)

root.geometry(f"{width}x{height}+{x}+{y}")
root.minsize(600, 550)  # Taille minimale de la fenêtre
root.configure(bg="#f0f2f5")
root.resizable(True, True)

# Frame principal
main_frame = Frame(root, bg="#f0f2f5")
main_frame.pack(fill="both", expand=True)

#Fonction pour la suppression du contenu d'un frame
def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


#Fonction pour se connecter
def se_connecter():
    clear_frame(main_frame)

    Label(main_frame, text="Bienvenue sur GeneLog", font=("Courrier", 20), bg="#41B77F", fg="white", height=2).pack(fill="x")

    frame = Frame(main_frame, width=350, height=450, pady=20)
    frame.pack()
    frame.pack_propagate(False)

    Label(frame, text="CONNEXION", font="Roboto 20 bold", fg="black").pack(fill="x")

    lbl_id = Label(frame, text="Nom de la Généalogie*", font=my_font, pady=10, anchor="w")
    lbl_id.pack(fill="x")
    entry_id = Entry(frame, font=my_font, background="#C0C0C0")
    entry_id.pack(fill="x")

    lbl_password = Label(frame, text="Mot de passe*", font=my_font, pady=10, anchor="w")
    lbl_password.pack(fill="x")
    entry_password = Entry(frame, font=my_font, show="*", background="#C0C0C0")
    entry_password.pack(fill="x")

    lbl_space = Label(frame)
    lbl_space.pack(fill="x")

    #Fonction pour afficher/masquer le mot de passe
    def toggle_password():
        if check_var.get():
            entry_password.config(show="")  # Afficher
        else:
            entry_password.config(show="*")  # Masquer

    #Checkbox pour afficher/masquer
    check_var = BooleanVar()
    Checkbutton(frame, text="Afficher le mot de passe", variable=check_var, command=toggle_password).pack()

    #Fonction pour la gestion de la connexion
    def gestion_connexion():
        identifiant = entry_id.get()
        password = entry_password.get()

        lbl_id.config(text="Nom de la Généalogie*", fg="black")
        lbl_password.config(text="Mot de passe*", fg="black")
        lbl_space.config(text="")
        
        if identifiant == "":
            lbl_id.config(text="Nom de la Généalogie* (champ obligatoire)", fg='red')
            return
        elif password == "":
            lbl_password.config(text="Mot de passe* (champ obligatoire)", fg="red")
            return

        user = connexion(identifiant, password)

        if user:
            programme_principale(identifiant)
        else:
            lbl_space.config(text="Nom de la Généalogie ou mot de passe incorrect", fg="red")

    # Frame pour le bouton de connexion
    bouton_frame = Frame(frame)
    bouton_frame.pack(fill="x", pady=10)

    Button(bouton_frame, font=my_font, text="Se connecter", command=gestion_connexion, bg="#41B77F", cursor="hand2").pack(fill="x")

    Button(frame, text="Créer un compte", font=("Arial", 12), fg="#41B77F",
           relief="flat", cursor="hand2", anchor="w", command=creation_compte).pack(side="left", padx=1, pady=10)

    Button(frame, text="Mot de passe oublié ?", font=("Arial", 12), fg="#41B77F",
       relief="flat", cursor="hand2", anchor="e", command=mot_de_passe_oublie).pack(side="right", padx=1, pady=10)



# Fonction de création du compte
def creation_compte():
    clear_frame(main_frame)

    Label(main_frame, text="Bienvenue sur GeneLog", font=("Courrier", 20), bg="#41B77F", fg="white", height=2).pack(fill="x")

    frame = Frame(main_frame, width=350, height=450, pady=20)
    frame.pack()
    frame.pack_propagate(False)

    Label(frame, text="INSCRIPTION", font="Roboto 20 bold", fg="black").pack(fill="x")

    lbl_id = Label(frame, text="Nom de la Généalogie*", font=my_font, pady=10, anchor="w")
    lbl_id.pack(fill="x")
    entry_id = Entry(frame, font=my_font, background="#C0C0C0")
    entry_id.pack(fill="x")

    # Mot de passe avec bulle d'information
    password_frame = Frame(frame)
    password_frame.pack(fill="x")
    lbl_password = Label(password_frame, text="Mot de passe*", font=my_font, pady=10, anchor="w")
    lbl_password.pack(side="left")

    def show_password_rules():
        messagebox.showinfo("Contraintes du mot de passe", 
                            "Le mot de passe doit contenir :\n"
                            "- Au moins 6 caractères\n"
                            "- Une lettre majuscule\n"
                            "- Une lettre minuscule\n"
                            "- Un chiffre\n"
                            "- Un caractère spécial (@$!%*?&.-_)")

    info_button = Button(password_frame, text="?", command=show_password_rules,
                         font=("Helvetica", 10, "bold"), fg="white", bg="#C0C0C0",
                         width=2, relief="flat", cursor="hand2")
    info_button.pack(side="left", padx=(5, 0))

    entry_password = Entry(frame, font=my_font, show="*", background="#C0C0C0")
    entry_password.pack(fill="x")

    lbl_password2 = Label(frame, text="Confirmer le mot de passe*", font=my_font, pady=10, anchor="w")
    lbl_password2.pack(fill="x")
    entry_password2 = Entry(frame, font=my_font, show="*", background="#C0C0C0")
    entry_password2.pack(fill="x")

    lbl_mail = Label(frame, text="Email*", font=my_font, pady=10, anchor="w")
    lbl_mail.pack(fill="x")
    entry_mail = Entry(frame, font=my_font, background="#C0C0C0")
    entry_mail.pack(fill="x")

    def toggle_password():
        if check_var.get():
            entry_password.config(show="")
            entry_password2.config(show="")
        else:
            entry_password.config(show="*")
            entry_password2.config(show="*")

    check_var = BooleanVar()
    Checkbutton(frame, text="Afficher le mot de passe", variable=check_var, command=toggle_password).pack()

    lbl_message = Label(frame, font=my_font, fg="red", wraplength=330, justify="left")
    lbl_message.pack()

    def gestion_creation_compte():
        login = entry_id.get()
        psw = entry_password.get()
        psw2 = entry_password2.get()
        mail = entry_mail.get()

        lbl_id.config(text="Nom de la Généalogie*", fg="black")
        lbl_password.config(text="Mot de passe*", fg="black")
        lbl_password2.config(text="Confirmer le mot de passe*", fg="black")
        lbl_mail.config(text="Email*", fg="black")
        lbl_message.config(text="")

        if not all([login, psw, psw2, mail]):
            if login == "": lbl_id.config(text="Nom de la Généalogie* (champ obligatoire)", fg='red')
            if len(login) > 20:
                messagebox.showerror("Erreur", "Le nom de la généalogie doit contenir au max : 20 caractères")
                return
            if psw == "": lbl_password.config(text="Mot de passe* (champ obligatoire)", fg='red')
            if psw2 == "": lbl_password2.config(text="Confirmer le mot de passe* (champ obligatoire)", fg='red')
            if mail == "": lbl_mail.config(text="Email* (champ obligatoire)", fg='red')
            return

        if len(psw) < 6:
            lbl_password.config(text="Il doit contenir au moins 6 caractères.", fg="red")
            return
        if not re.search(r"[A-Z]", psw):
            lbl_password.config(text="Il doit contenir au moins une lettre majuscule.", fg="red")
            return
        if not re.search(r"[a-z]", psw):
            lbl_password.config(text="Il doit contenir au moins une lettre minuscule.", fg="red")
            return
        if not re.search(r"[0-9]", psw):
            lbl_password.config(text="Il doit contenir au moins un chiffre.", fg="red")
            return
        if not re.search(r"[@$!%*?&.\-_]", psw):
            lbl_password.config(text="Il doit contenir au moins un caractère spécial.", fg="red")
            return

        if psw != psw2:
            lbl_password2.config(text="Les mots de passe sont différents", fg="red")
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", mail):
            lbl_mail.config(text="Email invalide", fg='red')
            return

        test_compte = verifier_compte(login)
        if test_compte:
            lbl_message.config(text="Cette généalogie existe déjà", fg='red')
            return


        insertion(login, psw, mail)
        messagebox.showinfo("Succès", "Compte créé avec succès !")
        se_connecter()

    bouton_frame = Frame(frame)
    bouton_frame.pack(fill="x", pady=10)

    Button(bouton_frame, font=my_font, text="Créer le compte", command=gestion_creation_compte, bg="#41B77F", cursor="hand2", height=1).pack(side="left", expand=True, fill="x", padx=(0, 5))
    Button(bouton_frame, text="Retour", font=my_font, fg="black", bg="#CCCCCC", cursor="hand2", command=se_connecter, height=1).pack(side="right", expand=True, fill="x", padx=(5, 0))


# Fonction d'envoi d'email
def envoyer_code_par_mail(destinataire, code):
    expediteur = "diallomt2002@gmail.com"
    mot_de_passe = "wfly ftmw gpwp nogq"

    msg = MIMEMultipart()
    msg['From'] = expediteur
    msg['To'] = destinataire
    msg['Subject'] = "Code de vérification - Réinitialisation du mot de passe"

    corps = f""" 
        Bonjour,

        Voici votre code de vérification : {code}

        Si vous n'avez pas demandé de réinitialisation, vérifiez votre compte.
    """
    msg.attach(MIMEText(corps, 'plain'))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(expediteur, mot_de_passe)
        server.send_message(msg)
        server.quit()
        return True
    
    except Exception as e:
        print("Erreur d'envoi de mail :", e)
        return False


code_verif_global = ""

#Fonction pour la saisie du nom de la généalogie et de l'email pour pouvoir modifier le mot de passe
def mot_de_passe_oublie():
    clear_frame(main_frame)

    Label(main_frame, text="Réinitialisation du mot de passe", font=("Courrier", 20), bg="#41B77F", fg="white", height=2).pack(fill="x")

    frame = Frame(main_frame, width=350, height=300, pady=20)
    frame.pack()
    frame.pack_propagate(False)

    Label(frame, text="Nom de la Généalogie*", font=my_font, anchor="w").pack(fill="x")
    entry_id = Entry(frame, font=my_font, background="#C0C0C0")
    entry_id.pack(fill="x")

    Label(frame, text="Email*", font=my_font, anchor="w", pady=10).pack(fill="x")
    entry_email = Entry(frame, font=my_font, background="#C0C0C0")
    entry_email.pack(fill="x")

    lbl_message = Label(frame, font=my_font, wraplength=330, fg="red")
    lbl_message.pack(pady=5)

    #Fonction pour l'envoie du code via mail
    def envoyer_code():
        identifiant = entry_id.get()
        email = entry_email.get()

        if not identifiant or not email:
            lbl_message.config(text="Veuillez remplir les deux champs.")
            return

        conn = sqlite3.connect("admin.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM USERS WHERE login = ? AND mail = ?", (identifiant, email))
        user = cursor.fetchone()
        conn.close()

        if user:
            global code_verif_global
            code_verif_global = str(random.randint(100000, 999999))
            if envoyer_code_par_mail(email, code_verif_global):
                verifier_code(identifiant)
            else:
                lbl_message.config(text="Échec d'envoi de l'email")
        else:
            lbl_message.config(text="Identifiant ou email incorrect.")

    Button(frame, text="Envoyer le code", font=my_font, command=envoyer_code, bg="#41B77F", fg="white").pack(pady=10)
    Button(frame, text="Annuler", font=my_font, command=se_connecter, bg="#123", fg="white").pack(pady=5)


#Fonction pour la du code réçu par mail
def verifier_code(identifiant):
    clear_frame(main_frame)

    Label(main_frame, text="Code de vérification", font=("Courrier", 20), bg="#41B77F", fg="white", height=2).pack(fill="x")

    frame = Frame(main_frame, width=350, height=300, pady=20)
    frame.pack()
    frame.pack_propagate(False)

    Label(frame, text="Veuillez entrer le code reçu par email :", font=my_font).pack()
    entry_code = Entry(frame, font=my_font)
    entry_code.pack(pady=10)

    lbl_message = Label(frame, font=my_font, wraplength=330, fg="red")
    lbl_message.pack(pady=5)

    #Fonction pour vérifier le code
    def verifier():
        if entry_code.get() == code_verif_global:
            afficher_champs_nouveau_mdp(identifiant)
        else:
            lbl_message.config(text="Code incorrect.")

    Button(frame, text="Vérifier", font=my_font, command=verifier, bg="#41B77F", fg="white").pack(pady=10)
    Button(frame, text="Annuler", font=my_font, command=se_connecter, bg="#123", fg="white").pack(pady=5)


#Fonction qui permet de modifier le mot de passe
def afficher_champs_nouveau_mdp(identifiant):
    clear_frame(main_frame)

    Label(main_frame, text="Nouveau mot de passe", font=("Courrier", 20), bg="#41B77F", fg="white", height=2).pack(fill="x")

    frame = Frame(main_frame, width=350, height=400, pady=20)
    frame.pack()
    frame.pack_propagate(False)

    Label(frame, text="Nouveau mot de passe*", font=my_font, anchor="w").pack(fill="x")
    entry_new_pass = Entry(frame, font=my_font, show="*", background="#C0C0C0")
    entry_new_pass.pack(fill="x")

    Label(frame, text="Confirmer le mot de passe*", font=my_font, anchor="w", pady=10).pack(fill="x")
    entry_confirm_pass = Entry(frame, font=my_font, show="*", background="#C0C0C0")
    entry_confirm_pass.pack(fill="x")

    #Fonction pour afficher/masquer le mot de passe
    def toggle_password():
        if check_var.get():
            entry_new_pass.config(show="")  # Afficher
            entry_confirm_pass.config(show="")
        else:
            entry_new_pass.config(show="*")  # Masquer
            entry_confirm_pass.config(show="*")

    #Checkbox pour afficher/masquer
    check_var = BooleanVar()
    Checkbutton(frame, text="Afficher le mot de passe", variable=check_var, command=toggle_password).pack()

    lbl_message = Label(frame, font=my_font, wraplength=330, fg="red")
    lbl_message.pack(pady=5)

    #Fonction qui modifie le mot de passe dans la base de données
    def modifier_mdp():
        mdp = entry_new_pass.get()
        mdp2 = entry_confirm_pass.get()

        if not mdp or not mdp2:
            lbl_message.config(text="Veuillez remplir les deux champs.")
            return

        if len(mdp) < 6 or not re.search(r"[A-Z]", mdp) or not re.search(r"[a-z]", mdp) or not re.search(r"[0-9]", mdp) or not re.search(r"[@$!%*?&.-_]", mdp):
            lbl_message.config(text="Mot de passe trop faible. Ex : Min. 6 caractères, 1 majuscule, 1 minuscule, 1 chiffre, 1 caractère spécial.")
            return

        if mdp != mdp2:
            lbl_message.config(text="Les mots de passe ne correspondent pas.")
            return

        # Hachage du mot de passe
        hashed_password = hasher_mot_de_passe(mdp)

        # Mise à jour du mot de passe haché dans la base de données
        conn = sqlite3.connect("admin.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE USERS SET password = ? WHERE login = ?", (hashed_password, identifiant))
        conn.commit()
        conn.close()

        messagebox.showinfo("Succès", "Mot de passe modifié avec succès.")
        se_connecter()

    
    #Frame pour les boutons de modification et d'annulation 
    bouton_frame = Frame(frame)
    bouton_frame.pack(fill="x", pady=10)

    Button(bouton_frame, text="Modifier", font=my_font, command=modifier_mdp, bg="#41B77F", fg="white").pack(pady=10)
    Button(bouton_frame, text="Annuler", font=my_font, command=se_connecter, bg="#123", fg="white").pack(pady=5)



#Fonction principale 
def programme_principale(login):
    clear_frame(main_frame)

    main_area = Frame(main_frame)
    main_area.pack(fill="both", expand=True)

    sidebar = Frame(main_area, bg="#41B77F", width=200)
    sidebar.pack(side="left", fill="y")

    content = Frame(main_area, bg="#f5f5f5")
    content.pack(side="right", fill="both", expand=True)

    #Fonction d'accueil (le frame qui s'affiche après connexion)
    def afficher_accueil():
        clear_frame(content)

        Label(content, text=f"Généalogie de {login.upper()}",
            font=("Helvetica", 20, "bold"), fg="#41B77F", bg="#f5f5f5", wraplength=400, justify="center").pack(pady=(40, 0))
        
        Label(content, text="Gérez votre arbre généalogique facilement avec GeneLog",
            font=("Helvetica", 13), bg="#f5f5f5").pack(pady=(10, 20))

        # Frame pour contenir l'image
        image_frame = Frame(content, bg="#f5f5f5")
        image_frame.pack()

        try:
            
            # Charger l'image 
            photo = PhotoImage(file="images/arbre_accueil.png")

            # Créer et afficher le label avec l'image
            label_image = Label(image_frame, image=photo, bg="#f5f5f5")
            label_image.image = photo  # Garde une référence pour éviter le garbage collector
            label_image.pack()
            

        except Exception as e:
            print("Erreur de chargement de l'image :", e)

    #Fonction qui permet d'appeler la fonction ajouter_famille (qui affiche le frame pour les ajouts des familles)
    def afficher_ajout_famille():
        for widget in content.winfo_children():
            widget.destroy()

        ajouter_famille(content, login, afficher_accueil)

    #Fonction qui permet d'appeler la fonction rechercher (qui affiche le frame pour la recherche)
    def afficher_recherche():
        clear_frame(content)

        rechercher(content, login)
        
    #Fonction pour la déconnexion
    def deconnexion():
        clear_frame(content)
        se_connecter()

    #Fonction pour supprimer la généalogie
    def suppression():
        try:
            conn = sqlite3.connect("admin.db")  # Connexion à la base de données
            cursor = conn.cursor()

            mot_de_passe = simpledialog.askstring("Vérification", "Entrez votre mot de passe :", show="*")
            if not mot_de_passe:
                messagebox.showwarning("Annulé", "Suppression annulée.")
                return

            # Récupérer le mot de passe haché pour ce login
            cursor.execute("SELECT password FROM USERS WHERE login = ?", (login,))
            resultat = cursor.fetchone()

            if resultat:
                mot_de_passe_hache_enregistre = resultat[0]
                mot_de_passe_utilisateur_hache = hasher_mot_de_passe(mot_de_passe)

                if mot_de_passe_utilisateur_hache == mot_de_passe_hache_enregistre:
                    confirmation = messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer la généalogie de '{login}' ?")
                    if confirmation:
                        cursor.execute("DELETE FROM USERS WHERE login = ?", (login,))
                        conn.commit()

                        chemin_fichier = os.path.join("comptes", f"{login}.db")
                        if os.path.exists(chemin_fichier):
                            os.remove(chemin_fichier)

                        messagebox.showinfo("Succès", "Compte supprimé avec succès.")
                        se_connecter()
                else:
                    messagebox.showerror("Erreur", "Mot de passe incorrect. Suppression annulée.")
            else:
                messagebox.showerror("Erreur", "Login introuvable.")

            conn.close()

        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")



    initialiser_base_de_donnees(login)

    Button(sidebar, text="Accueil", command=afficher_accueil).pack(fill="x", pady=(40, 0), padx=10)
    Button(sidebar, text="Ajouter une famille", command=afficher_ajout_famille).pack(fill="x", pady=5, padx=10)
    Button(sidebar, text="Rechercher", command=afficher_recherche).pack(fill="x", pady=5, padx=10)
    Button(sidebar, text="Déconnexion", command=deconnexion).pack(fill="x", pady=5, padx=10)
    Button(sidebar, text="Suppression", command=suppression).pack(fill="x", pady=5, padx=10)

    afficher_accueil()



# Lancement initial
se_connecter()

root.mainloop()
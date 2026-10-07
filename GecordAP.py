# Application Gecord - Version Corrigée (Sans erreur de syntaxe)
import tkinter as tk
from tkinter import messagebox, filedialog

class GecordApp:
    def __init__(self, fenetre):
        self.fenetre = fenetre
        self.fenetre.title("Gecord")
        self.fenetre.geometry("480x700")
        self.fenetre.config(bg="#f0f2f5")

        # Données de l'utilisateur
        self.mon_email = ""
        self.mon_pseudo = "Utilisateur"
        self.est_robot = False
        
        # Dictionnaire des contacts {email: nom_affiche}
        self.contacts_dict = {}
        self.contact_actuel = None

        self.creer_ecran_connexion()

    def vider_fenetre(self):
        for widget in self.fenetre.winfo_children():
            widget.destroy()

    # --- ÉCRAN DE CONNEXION ---
    def creer_ecran_connexion(self):
        self.vider_fenetre()
        
        cadre = tk.Frame(self.fenetre, bg="#ffffff", padx=20, pady=20)
        cadre.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=370, height=420)

        tk.Label(cadre, text="💬 Gecord", font=("Arial", 20, "bold"), bg="#ffffff", fg="#075e54").pack(pady=15)
        tk.Label(cadre, text="Connecte-toi avec ton adresse e-mail :", font=("Arial", 10), bg="#ffffff", fg="#666666").pack(anchor=tk.W, pady=(10, 5))

        self.entree_email = tk.Entry(cadre, font=("Arial", 12), relief=tk.SOLID, bd=1)
        self.entree_email.pack(fill=tk.X, pady=5, ipady=5)

        self.var_robot = tk.BooleanVar()
        check_robot = tk.Checkbutton(cadre, text="Je suis un robot (Code Python)", variable=self.var_robot, bg="#ffffff", font=("Arial", 10))
        check_robot.pack(anchor=tk.W, pady=10)

        btn_valider = tk.Button(cadre, text="Commencer", command=self.valider_connexion, bg="#25d366", fg="white", font=("Arial", 11, "bold"), relief=tk.FLAT)
        btn_valider.pack(fill=tk.X, pady=20, ipady=5)

    def valider_connexion(self):
        email = self.entree_email.get().strip()
        if not email or "@" not in email:
            messagebox.showerror("Erreur", "Entre une adresse e-mail valide !")
            return
        
        self.mon_email = email
        self.est_robot = self.var_robot.get()
        self.mon_pseudo = "Robot Python" if self.est_robot else "Baptiste"
        
        # Ajout de soi-même dans les contacts
        self.contacts_dict[self.mon_email] = f"{self.mon_pseudo} (Moi)"
        self.contact_actuel = self.mon_email

        self.creer_interface_principale()

    # --- INTERFACE PRINCIPALE ---
    def creer_interface_principale(self):
        self.vider_fenetre()

        # Barre supérieure style WhatsApp
        header = tk.Frame(self.fenetre, bg="#075e54", height=60)
        header.pack(fill=tk.X, side=tk.TOP)

        lbl_titre = tk.Label(header, text="💬 Gecord", font=("Arial", 12, "bold"), bg="#075e54", fg="white")
        lbl_titre.pack(side=tk.LEFT, padx=15, pady=15)

        # Boutons du header
        tk.Button(header, text="⚙️ Profil", command=self.ouvrir_profil, bg="#128c7e", fg="white", font=("Arial", 8, "bold"), relief=tk.FLAT).pack(side=tk.RIGHT, padx=4, pady=12)
        tk.Button(header, text="🤖 Robots", command=self.gerer_robots, bg="#128c7e", fg="white", font=("Arial", 8, "bold"), relief=tk.FLAT).pack(side=tk.RIGHT, padx=2, pady=12)
        tk.Button(header, text="➕ Contact", command=self.ajouter_contact_popup, bg="#128c7e", fg="white", font=("Arial", 8, "bold"), relief=tk.FLAT).pack(side=tk.RIGHT, padx=2, pady=12)

        # Corps (Contacts à gauche, Chat à droite)
        corps = tk.Frame(self.fenetre, bg="#efeae2")
        corps.pack(fill=tk.BOTH, expand=True)

        cadre_contacts = tk.Frame(corps, bg="white", width=150)
        cadre_contacts.pack(side=tk.LEFT, fill=tk.Y)
        
        tk.Label(cadre_contacts, text="Discussions", font=("Arial", 9, "bold"), bg="white", fg="#075e54").pack(pady=8)
        
        self.listebox_contacts = tk.Listbox(cadre_contacts, font=("Arial", 9), bd=0, highlightthickness=0)
        self.listebox_contacts.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.mettre_a_jour_liste()
        self.listebox_contacts.bind("<<ListboxSelect>>", self.changer_contact)

        # Bouton pour renommer le contact sélectionné
        btn_renommer = tk.Button(cadre_contacts, text="✏️ Renommer", command=self.renommer_contact_popup, bg="#f0f2f5", fg="#333333", font=("Arial", 8), relief=tk.FLAT)
        btn_renommer.pack(fill=tk.X, padx=5, pady=5)

        # Zone de chat
        cadre_chat = tk.Frame(corps, bg="#efeae2")
        cadre_chat.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.zone_messages = tk.Text(cadre_chat, font=("Arial", 10), bg="#efeae2", bd=0, state='disabled')
        self.zone_messages.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Barre de saisie en bas avec bouton "+" pour Médias
        cadre_saisie = tk.Frame(cadre_chat, bg="#f0f2f5", height=55)
        cadre_saisie.pack(fill=tk.X, side=tk.BOTTOM)

        btn_media = tk.Button(cadre_saisie, text="➕", command=self.envoyer_media, bg="#25d366", fg="white", font=("Arial", 10, "bold"), relief=tk.FLAT)
        btn_media.pack(side=tk.LEFT, padx=(5, 2), pady=10)

        self.champ_message = tk.Entry(cadre_saisie, font=("Arial", 11), relief=tk.SOLID, bd=1)
        self.champ_message.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=10, ipady=5)
        self.champ_message.bind("<Return>", self.envoyer_message)

        btn_envoyer = tk.Button(cadre_saisie, text="Envoyer", command=self.envoyer_message, bg="#075e54", fg="white", font=("Arial", 9, "bold"), relief=tk.FLAT)
        btn_envoyer.pack(side=tk.RIGHT, padx=5, pady=10)

        self.afficher_message_systeme("Bienvenue sur Gecord. Prêt à discuter !")

    def mettre_a_jour_liste(self):
        self.listebox_contacts.delete(0, tk.END)
        for email, nom in self.contacts_dict.items():
            self.listebox_contacts.insert(tk.END, nom)

    def afficher_message_systeme(self, texte):
        self.zone_messages.config(state='normal')
        self.zone_messages.insert(tk.END, f"\n[Système] {texte}\n", "sys")
        self.zone_messages.config(state='disabled')
        self.zone_messages.see(tk.END)

    def changer_contact(self, event):
        selection = self.listebox_contacts.curselection()
        if selection:
            index = selection[0]
            emails = list(self.contacts_dict.keys())
            if index < len(emails):
                self.contact_actuel = emails[index]
                nom_affiche = self.contacts_dict[self.contact_actuel]
                self.afficher_message_systeme(f"Discussion ouverte avec : {nom_affiche}")

    # --- RENOMMER UN CONTACT LOCALEMENT ---
    def renommer_contact_popup(self):
        selection = self.listebox_contacts.curselection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionne un contact dans la liste.")
            return
        
        index = selection[0]
        emails = list(self.contacts_dict.keys())
        email_cible = emails[index]
        ancien_nom = self.contacts_dict[email_cible]

        fen_renommer = tk.Toplevel(self.fenetre)
        fen_renommer.title("Renommer")
        fen_renommer.geometry("300x160")
        fen_renommer.config(bg="white")

        tk.Label(fen_renommer, text=f"Nouveau nom pour :\n{ancien_nom}", font=("Arial", 9, "bold"), bg="white", fg="#075e54").pack(pady=10)
        
        entree_nouveau_nom = tk.Entry(fen_renommer, font=("Arial", 10), relief=tk.SOLID, bd=1)
        entree_nouveau_nom.insert(0, ancien_nom)
        entree_nouveau_nom.pack(fill=tk.X, padx=20, pady=5, ipady=3)

        def valider_renommage():
            nouveau_nom = entree_nouveau_nom.get().strip()
            if nouveau_nom:
                self.contacts_dict[email_cible] = nouveau_nom
                self.mettre_a_jour_liste()
                fen_renommer.destroy()
            else:
                messagebox.showerror("Erreur", "Nom vide.")

        tk.Button(fen_renommer, text="Enregistrer", command=valider_renommage, bg="#075e54", fg="white", font=("Arial", 10, "bold"), relief=tk.FLAT).pack(pady=10)

    # --- ENVOI DE MÉDIAS ---
    def envoyer_media(self):
        chemin_fichier = filedialog.askopenfilename(
            title="Envoyer une photo ou une vidéo",
            filetypes=[("Fichiers Médias", "*.png *.jpg *.jpeg *.mp4 *.avi *.mov"), ("Tous les fichiers", "*.*")]
        )
        if chemin_fichier:
            nom_fichier = chemin_fichier.split("/")[-1]
            self.zone_messages.config(state='normal')
            self.zone_messages.insert(tk.END, f"\nMoi : 📁 [Média] {nom_fichier}\n", "media")
            self.zone_messages.config(state='disabled')
            self.zone_messages.see(tk.END)

    # --- MESSAGES ET TRADUCTION ---
    def envoyer_message(self, event=None):
        texte_brut = self.champ_message.get().strip()
        if not texte_brut:
            return

        self.champ_message.delete(0, tk.END)

        self.zone_messages.config(state='normal')
        self.zone_messages.insert(tk.END, f"\nMoi : {texte_brut}\n", "moi")
        
        nom_actuel = self.contacts_dict.get(self.contact_actuel, "Contact")
        
        if "robot" in nom_actuel.lower():
            code_traduit = f"print('Exécution commande: {texte_brut}')"
            self.zone_messages.insert(tk.END, f"💻 [Code Python] -> {code_traduit}\n", "code")
            self.zone_messages.insert(tk.END, f"🤖 {nom_actuel} : Code exécuté !\n", "robot")
        
        self.zone_messages.config(state='disabled')
        self.zone_messages.see(tk.END)

    # --- GESTION PROFILS ET ROBOTS ---
    def ouvrir_profil(self):
        fen_profil = tk.Toplevel(self.fenetre)
        fen_profil.title("Mon Profil")
        fen_profil.geometry("300x230")
        fen_profil.config(bg="white")

        tk.Label(fen_profil, text="Mon Profil", font=("Arial", 12, "bold"), bg="white", fg="#075e54").pack(pady=15)
        tk.Label(fen_profil, text=f"E-mail : {self.mon_email}", font=("Arial", 9), bg="white").pack(anchor=tk.W, padx=20, pady=5)
        
        tk.Label(fen_profil, text="Pseudo :", font=("Arial", 9), bg="white").pack(anchor=tk.W, padx=20, pady=(10, 2))
        entree_pseudo = tk.Entry(fen_profil, font=("Arial", 10), relief=tk.SOLID, bd=1)
        entree_pseudo.insert(0, self.mon_pseudo)
        entree_pseudo.pack(fill=tk.X, padx=20, pady=5)

        def sauvegarder():
            self.mon_pseudo = entree_pseudo.get().strip()
            messagebox.showinfo("Succès", "Profil mis à jour !")
            fen_profil.destroy()

        tk.Button(fen_profil, text="Enregistrer", command=sauvegarder, bg="#075e54", fg="white", font=("Arial", 10, "bold"), relief=tk.FLAT).pack(pady=15)

    def ajouter_contact_popup(self):
        fen_contact = tk.Toplevel(self.fenetre)
        fen_contact.title("Ajouter un contact")
        fen_contact.geometry("300x150")
        fen_contact.config(bg="white")

        tk.Label(fen_contact, text="Ajouter par e-mail", font=("Arial", 11, "bold"), bg="white", fg="#075e54").pack(pady=10)
        entree_mail = tk.Entry(fen_contact, font=("Arial", 10), relief=tk.SOLID, bd=1)
        entree_mail.pack(fill=tk.X, padx=20, pady=5)

        def valider():
            nouveau = entree_mail.get().strip()
            if nouveau and "@" in nouveau:
                if nouveau not in self.contacts_dict:
                    self.contacts_dict[nouveau] = nouveau
                    self.mettre_a_jour_liste()
                fen_contact.destroy()
            else:
                messagebox.showerror("Erreur", "E-mail invalide.")

        tk.Button(fen_contact, text="Ajouter", command=valider, bg="#25d366", fg="white", font=("Arial", 10, "bold"), relief=tk.FLAT).pack(pady=10)

    def gerer_robots(self):
        fen_robot = tk.Toplevel(self.fenetre)
        fen_robot.title("Gestion des Robots")
        fen_robot.geometry("350x280")
        fen_robot.config(bg="white")

        tk.Label(fen_robot, text="🤖 Ajouter un Robot", font=("Arial", 11, "bold"), bg="white", fg="#075e54").pack(pady=10)

        tk.Label(fen_robot, text="Nom du robot :", font=("Arial", 9), bg="white").pack(anchor=tk.W, padx=20)
        entree_nom = tk.Entry(fen_robot, font=("Arial", 10), relief=tk.SOLID, bd=1)
        entree_nom.pack(fill=tk.X, padx=20, pady=5)

        tk.Label(fen_robot, text="E-mail du robot :", font=("Arial", 9), bg="white").pack(anchor=tk.W, padx=20)
        entree_mail_robot = tk.Entry(fen_robot, font=("Arial", 10), relief=tk.SOLID, bd=1)
        entree_mail_robot.pack(fill=tk.X, padx=20, pady=5)

        def sauvegarder_robot():
            nom = entree_nom.get().strip()
            mail = entree_mail_robot.get().strip()
            if nom and mail:
                nom_complet = f"Robot: {nom}"
                if mail not in self.contacts_dict:
                    self.contacts_dict[mail] = nom_complet
                    self.mettre_a_jour_liste()
                messagebox.showinfo("Succès", f"Robot '{nom}' ajouté !")
                fen_robot.destroy()
            else:
                messagebox.showerror("Erreur", "Remplis tous les champs.")

        tk.Button(fen_robot, text="Enregistrer", command=sauvegarder_robot, bg="#075e54", fg="white", font=("Arial", 10, "bold"), relief=tk.FLAT).pack(pady=15)

if __name__ == "__main__":
    racine = tk.Tk()
    app = GecordApp(racine)
    racine.mainloop()
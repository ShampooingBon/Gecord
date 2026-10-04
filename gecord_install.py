# Script d'installation de Gecord - Complet et prêt à l'emploi
import os
import tkinter as tk
from tkinter import messagebox
import urllib.request

class GecordInstallation:
    def __init__(self, fenetre):
        self.fenetre = fenetre
        self.fenetre.title("Installation de Gecord")
        self.fenetre.geometry("400x300")
        self.fenetre.config(bg="#1a1a24")

        # Informations de ton dépôt GitHub privé (Jcorde)
        self.github_user = "TonNomUtilisateurGitHub"
        self.repo_name = "Jcorde"
        self.branche = "main"
        self.nom_fichier = "gecord.apk"
        
        # Ton jeton d'accès personnel GitHub (Token)
        self.github_token = "ghp_ton_jeton_secret_ici"

        self.creer_interface()

    def creer_interface(self):
        # Titre
        tk.Label(
            self.fenetre, 
            text="Gecord - Application Native", 
            font=("Arial", 14, "bold"), 
            bg="#1a1a24", 
            fg="#00ff66"
        ).pack(pady=20)

        # Rappel du logo officiel (Halloween / Sorcier)
        tk.Label(
            self.fenetre, 
            text="🎨 Logo officiel : Thème Sorcier d'Halloween", 
            font=("Arial", 9), 
            bg="#1a1a24", 
            fg="#b3b3b3"
        ).pack(pady=(0, 20))

        # Bouton d'installation direct
        btn_installer = tk.Button(
            self.fenetre, 
            text="📥 Installer Gecord", 
            command=self.telecharger_apk, 
            bg="#00aa44", 
            fg="white", 
            font=("Arial", 11, "bold"), 
            relief=tk.FLAT
        )
        btn_installer.pack(fill=tk.X, padx=30, pady=10, ipady=10)

    def telecharger_apk(self):
        url_privee = f"https://raw.githubusercontent.com/{self.github_user}/{self.repo_name}/{self.branche}/{self.nom_fichier}"
        chemin_sauvegarde = os.path.expanduser("~/Downloads/gecord.apk")

        try:
            requete = urllib.request.Request(url_privee)
            requete.add_header("Authorization", f"token {self.github_token}")

            messagebox.showinfo("Téléchargement", "Connexion au dépôt sécurisé de Gecord...")

            with urllib.request.urlopen(requete) as reponse_web, open(chemin_sauvegarde, 'wb') as fichier_local:
                fichier_local.write(reponse_web.read())

            messagebox.showinfo(
                "Succès", 
                f"Application Gecord téléchargée avec succès !\nEnregistrée dans : {chemin_sauvegarde}"
            )

        except Exception as e:
            messagebox.showerror(
                "Erreur", 
                f"Échec du téléchargement.\nVérifie ton token GitHub.\nErreur : {e}"
            )

if __name__ == "__main__":
    racine = tk.Tk()
    app = GecordInstallation(racine)
    racine.mainloop()
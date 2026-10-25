# -*- coding: utf-8 -*-
"""
GecordAP.py — prototype Android/Desktop de Gecord, avec interface Kivy.

Fonctions locales :
- création de profil (e-mail, nom public, nom utilisé par les robots,
  prononciation personnalisée, icône publique et icône des robots) ;
- discussions locales et ajout de contacts ;
- création/modification de robots ;
- visibilité : privé, contacts choisis ou public ;
- création et modification des fiches de code Python des robots.

Important :
- Les comptes, messages et robots sont enregistrés localement dans gecord_data.json.
- Ce prototype ne transmet pas encore les messages sur Internet.
- Les tokens sont créés localement ; ils ne seront acceptés par aucun serveur sans API.
- La case « Je suis un humain » est une confirmation visuelle, pas un CAPTCHA.
- Les icônes sont des libellés textuels, sans emojis, pour éviter les glyphes de remplacement.
"""

import json
import os
import re
import secrets
import hashlib
import shutil
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserIconView
from kivy.core.clipboard import Clipboard

APP_NAME = "Gecord"
GREEN = "#16B85A"
DARK_GREEN = "#087C3A"
PALE_GREEN = "#E8F8EE"
WHITE = "#FFFFFF"
BLACK = "#17211B"
GREY = "#66736B"
LIGHT_GREY = "#F3F6F4"
BORDER = "#DCE5DF"

# Noms textuels : pas d'emojis susceptibles de s'afficher en glyphes de remplacement.
PUBLIC_AVATARS = ["Lettre du prénom", "Bleu", "Vert", "Violet", "Orange", "Rose",
                  "Chat", "Renard", "Panda", "Grenouille", "Pingouin", "Lion",
                  "Étoile", "Lune", "Mer", "Arbre", "Tournesol", "Trèfle",
                  "Jeu vidéo", "Fusée"]
BOT_AVATARS = ["Robot", "Robot violet", "Cerveau", "Engrenage", "Bras robotique",
               "Ampoule", "Laboratoire", "Outils", "Étoile", "Flamme",
               "Arc-en-ciel", "Poulpe", "Hibou", "Dauphin", "Planète", "Diamant"]


def data_file_path():
    """Dossier inscriptible sur Android et ordinateur."""
    try:
        from kivy.app import App as KivyApp
        app = KivyApp.get_running_app()
        if app and app.user_data_dir:
            return os.path.join(app.user_data_dir, "gecord_data.json")
    except Exception:
        pass
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "gecord_data.json")


def default_data():
    return {
        "profile": {
            "email": "", "display_name": "", "robot_name": "",
            "pronunciation": "", "public_avatar": "Lettre du prénom",
            "robot_avatar": "Robot", "show_email": False, "photo_path": ""
        },
        "contacts": [],
        "messages": {},
        "robots": [],
        "active_email": ""
    }


class GecordApp(App):
    title = APP_NAME

    def build(self):
        Window.clearcolor = get_color_from_hex(WHITE)
        self.data_path = data_file_path()
        self.data = self.load_data()
        self.current_contact = None
        self.pending_profile_photo = self.data["profile"].get("photo_path", "")
        self.screen = BoxLayout(orientation="vertical", spacing=0)
        if self.data.get("profile", {}).get("email") and self.data.get("active_email"):
            self.show_chats()
        else:
            self.show_start_screen()
        return self.screen

    def load_data(self):
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            base = default_data()
            base.update(loaded if isinstance(loaded, dict) else {})
            for key, value in default_data().items():
                if key not in base:
                    base[key] = value
            if not isinstance(base.get("profile"), dict):
                base["profile"] = default_data()["profile"]
            for key, value in default_data()["profile"].items():
                base["profile"].setdefault(key, value)
            for key in ("contacts", "robots"):
                if not isinstance(base.get(key), list):
                    base[key] = []
            if not isinstance(base.get("messages"), dict):
                base["messages"] = {}
            return base
        except (OSError, ValueError, TypeError):
            return default_data()

    def save_data(self):
        try:
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            temp = self.data_path + ".tmp"
            with open(temp, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            os.replace(temp, self.data_path)
            return True
        except OSError as exc:
            self.notice("Sauvegarde impossible", str(exc))
            return False

    def clear_screen(self):
        self.screen.clear_widgets()

    def label(self, text, size=16, color=BLACK, bold=False, height=None,
              halign="left"):
        lbl = Label(
            text=text, font_size=dp(size), color=get_color_from_hex(color),
            bold=bold, size_hint_y=None if height else 1,
            height=dp(height) if height else None,
            halign=halign, valign="middle"
        )
        lbl.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], None)))
        return lbl

    def button(self, text, callback, primary=False, height=46):
        btn = Button(
            text=text, size_hint_y=None, height=dp(height),
            background_normal="", background_down="",
            background_color=get_color_from_hex(GREEN if primary else LIGHT_GREY),
            color=get_color_from_hex(WHITE if primary else BLACK),
            font_size=dp(15), bold=primary
        )
        btn.bind(on_release=lambda *_: callback())
        return btn

    def field(self, hint, text="", multiline=False, password=False, height=48):
        inp = TextInput(
            hint_text=hint, text=text, multiline=multiline,
            password=password, size_hint_y=None, height=dp(height),
            padding=[dp(12), dp(12), dp(12), dp(8)],
            background_normal="", background_active="",
            background_color=get_color_from_hex(WHITE),
            foreground_color=get_color_from_hex(BLACK),
            cursor_color=get_color_from_hex(GREEN),
            hint_text_color=get_color_from_hex(GREY),
            font_size=dp(16)
        )
        return inp

    def page(self, title, subtitle=None):
        self.clear_screen()
        header = BoxLayout(orientation="vertical", size_hint_y=None,
                           height=dp(82), padding=[dp(16), dp(10)],
                           spacing=dp(2))
        header.add_widget(self.button("← Retour au menu", self.show_home, False, 34))
        header.add_widget(self.label(title, 24, GREEN, True, 36))
        if subtitle:
            header.add_widget(self.label(subtitle, 12, GREY, False, 24))
        self.screen.add_widget(header)
        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation="vertical", size_hint_y=None,
                            padding=[dp(16), dp(8)], spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))
        scroll.add_widget(content)
        self.screen.add_widget(scroll)
        return content

    def notice(self, title, message):
        box = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
        box.add_widget(Label(text=message, color=get_color_from_hex(BLACK)))
        ok = Button(text="OK", size_hint_y=None, height=dp(42),
                    background_normal="", background_color=get_color_from_hex(GREEN))
        box.add_widget(ok)
        pop = Popup(title=title, content=box, size_hint=(0.88, None),
                    height=dp(210), auto_dismiss=False)
        ok.bind(on_release=pop.dismiss)
        pop.open()

    def ask_text(self, title, hint, on_save, initial="", multiline=False):
        box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        inp = self.field(hint, initial, multiline=multiline, height=130 if multiline else 48)
        box.add_widget(inp)
        row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        pop = Popup(title=title, content=box, size_hint=(0.92, None),
                    height=dp(250 if multiline else 175))
        cancel = Button(text="Annuler")
        save = Button(text="Enregistrer", background_normal="",
                      background_color=get_color_from_hex(GREEN))
        row.add_widget(cancel)
        row.add_widget(save)
        box.add_widget(row)
        cancel.bind(on_release=pop.dismiss)
        def submit(*_):
            value = inp.text.strip()
            pop.dismiss()
            on_save(value)
        save.bind(on_release=submit)
        pop.open()

    def show_start_screen(self):
        c = self.page("Gecord", "Ta messagerie et tes robots personnalisés")
        c.add_widget(Widget(size_hint_y=None, height=dp(16)))
        c.add_widget(self.label("GECORD", 54, GREEN, True, 90, "center"))
        c.add_widget(self.label("Bienvenue dans Gecord", 23, BLACK, True, 42, "center"))
        c.add_widget(self.label("Connecte-toi ou crée ton profil", 15, GREY, False, 32, "center"))
        c.add_widget(self.button("Créer un compte", self.show_registration, True, 52))
        c.add_widget(self.button("Se connecter", self.show_login, False, 48))
        c.add_widget(self.label(
            "Prototype local : les messages ne sont pas encore envoyés sur Internet.",
            12, GREY, False, 50, "center"))

    def show_registration(self):
        c = self.page("Créer un compte", "Renseigne les informations de ton profil")
        email = self.field("Adresse e-mail")
        display_name = self.field("Nom visible par les autres utilisateurs")
        robot_name = self.field("Nom utilisé par les robots")
        pronunciation = self.field("Prononciation personnalisée (facultatif)")
        c.add_widget(self.label("Adresse e-mail", 14, GREY, True, 24))
        c.add_widget(email)
        c.add_widget(self.label("Nom du profil public", 14, GREY, True, 24))
        c.add_widget(display_name)
        c.add_widget(self.label("Comment les robots doivent-ils t'appeler ?", 14, GREY, True, 24))
        c.add_widget(robot_name)
        c.add_widget(self.label("Prononciation pour les robots (facultatif)", 14, GREY, True, 24))
        c.add_widget(pronunciation)

        c.add_widget(self.label("Photo de profil (facultatif)", 14, GREY, True, 24))
        self.pending_profile_photo = ""
        photo_status = self.label("Aucune photo sélectionnée", 12, GREY, False, 24)
        c.add_widget(photo_status)
        c.add_widget(self.button("Choisir une photo depuis l’appareil", lambda: self.choose_profile_photo(photo_status), False, 44))
        c.add_widget(self.label("Icône de profil publique (si aucune photo)", 14, GREY, True, 34))
        public_spinner = Spinner(text=PUBLIC_AVATARS[0], values=PUBLIC_AVATARS,
                                 size_hint_y=None, height=dp(46), background_normal="", background_down="", background_color=get_color_from_hex(WHITE), color=get_color_from_hex(BLACK))
        c.add_widget(public_spinner)
        c.add_widget(self.label("Icône visible par les robots (choix prédéfinis)", 14, GREY, True, 34))
        robot_spinner = Spinner(text=BOT_AVATARS[0], values=BOT_AVATARS,
                                size_hint_y=None, height=dp(46), background_normal="", background_down="", background_color=get_color_from_hex(WHITE), color=get_color_from_hex(BLACK))
        c.add_widget(robot_spinner)

        human_row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        human_check = CheckBox(active=False, size_hint_x=None, width=dp(44))
        human_row.add_widget(human_check)
        human_row.add_widget(self.label("Je suis un humain", 15, BLACK, False, 42))
        c.add_widget(human_row)
        c.add_widget(self.button("Créer mon compte", lambda: self.finish_registration(
            email.text, display_name.text, robot_name.text, pronunciation.text,
            public_spinner.text, robot_spinner.text, human_check.active, self.pending_profile_photo
        ), True, 52))
        c.add_widget(self.button("Retour", self.show_start_screen))

    def finish_registration(self, email, display_name, robot_name, pronunciation,
                            public_avatar, robot_avatar, human_checked, photo_path=""):
        email = email.strip().lower()
        if not email or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            self.notice("Adresse e-mail", "Saisis une adresse e-mail valide.")
            return
        if not human_checked:
            self.notice("Confirmation", "Coche « Je suis un humain » pour continuer.")
            return
        if not display_name.strip() or not robot_name.strip():
            self.notice("Profil incomplet", "Renseigne ton nom de profil et le nom utilisé par les robots.")
            return
        self.data["profile"] = {
            "email": email,
            "display_name": display_name.strip(),
            "robot_name": robot_name.strip(),
            "pronunciation": pronunciation.strip(),
            "public_avatar": public_avatar if public_avatar in PUBLIC_AVATARS else PUBLIC_AVATARS[0],
            "robot_avatar": robot_avatar if robot_avatar in BOT_AVATARS else BOT_AVATARS[0],
            "show_email": False,
            "photo_path": photo_path or ""
        }
        self.data["active_email"] = email
        self.save_data()
        self.show_home()

    def choose_profile_photo(self, status_label=None):
        """Choisit une vraie image via le sélecteur natif sur ordinateur.

        Windows/Linux : boîte de dialogue native tkinter.
        Android et autres plateformes : sélecteur Kivy de secours.
        La copie locale évite de perdre la photo si le fichier d'origine est déplacé.
        """
        source = None
        platform = getattr(App, "get_running_app", lambda: None)()
        platform_name = getattr(platform, "platform", "") if platform else ""

        # Sur Windows/Linux, demander le sélecteur de fichiers du système.
        if platform_name not in ("android", "ios"):
            try:
                import tkinter as tk
                from tkinter import filedialog
                root = tk.Tk()
                root.withdraw()
                try:
                    root.attributes("-topmost", True)
                except Exception:
                    pass
                source = filedialog.askopenfilename(
                    parent=root,
                    title="Choisir la photo de profil Gecord",
                    filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp *.gif"),
                               ("Tous les fichiers", "*.*")]
                )
                root.destroy()
            except Exception as exc:
                # Certains environnements desktop n'ont pas Tk installé ; utiliser Kivy.
                source = None

        # Sélecteur Kivy de secours (Android inclus, si aucun pont natif n'est configuré).
        if not source:
            home_dir = os.path.expanduser("~")
            chooser = FileChooserIconView(
                filters=["*.png", "*.jpg", "*.jpeg", "*.webp", "*.bmp", "*.gif"],
                path=home_dir, dirselect=False, multiselect=False
            )
            layout = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(8))
            layout.add_widget(chooser)
            row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
            popup = Popup(title="Choisir une photo", content=layout, size_hint=(0.95, 0.9))
            cancel = Button(text="Annuler")
            select = Button(text="Sélectionner", background_normal="",
                            background_color=get_color_from_hex(GREEN),
                            color=get_color_from_hex(WHITE))
            row.add_widget(cancel)
            row.add_widget(select)
            layout.add_widget(row)
            cancel.bind(on_release=popup.dismiss)

            def choose_from_kivy(*_):
                if not chooser.selection:
                    self.notice("Photo", "Sélectionne d'abord une image.")
                    return
                popup.dismiss()
                self._save_profile_photo(chooser.selection[0], status_label)

            select.bind(on_release=choose_from_kivy)
            popup.open()
            return

        # Annulation de la boîte de dialogue native : ne rien modifier.
        self._save_profile_photo(source, status_label)

    def _save_profile_photo(self, source, status_label=None):
        """Valide, copie et mémorise la photo choisie."""
        if not source:
            return
        try:
            ext = os.path.splitext(source)[1].lower()
            if ext not in (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"):
                self.notice("Format non pris en charge", "Choisis une image PNG, JPG, JPEG, WEBP, BMP ou GIF.")
                return
            destination_dir = os.path.join(os.path.dirname(self.data_path), "profile_photos")
            os.makedirs(destination_dir, exist_ok=True)
            destination = os.path.join(destination_dir, "profile_photo" + ext)
            shutil.copy2(source, destination)
            self.pending_profile_photo = destination
            if status_label:
                status_label.text = "Photo sélectionnée : " + os.path.basename(destination)
            self.notice("Photo sélectionnée", "Enregistre ton profil pour conserver la modification.")
        except (OSError, PermissionError) as exc:
            self.notice("Impossible de choisir la photo", str(exc))

    def show_login(self):
        c = self.page("Se connecter", "Utilise l'adresse e-mail de ton profil enregistré sur cet appareil")
        email = self.field("Adresse e-mail")
        c.add_widget(email)
        c.add_widget(self.button("Continuer", lambda: self.finish_login(email.text), True))
        c.add_widget(self.button("Créer un compte", self.show_registration))
        c.add_widget(self.button("Retour", self.show_start_screen))

    def finish_login(self, email):
        email = email.strip().lower()
        profile = self.data.get("profile", {})
        if not profile.get("email"):
            self.notice("Aucun compte local", "Crée d'abord un compte sur cet appareil.")
            return
        if email != profile.get("email", "").lower():
            self.notice("Compte introuvable", "Cette adresse ne correspond pas au profil local enregistré.")
            return
        self.data["active_email"] = email
        self.save_data()
        self.show_chats()

    def show_home(self):
        c = self.page("Gecord", "Discussions • Robots • Paramètres")
        profile = self.data["profile"]
        if profile.get("photo_path") and os.path.isfile(profile.get("photo_path", "")):
            try:
                c.add_widget(Image(source=profile["photo_path"], size_hint_y=None, height=dp(110), allow_stretch=True, keep_ratio=True))
            except Exception:
                pass
        c.add_widget(self.label(
            f"{self.avatar_badge(profile.get('public_avatar', 'Lettre du prénom'), profile.get('display_name', ''))}  Bonjour {profile.get('display_name') or '!'}",
            20, GREEN, True, 42))
        c.add_widget(self.button("Discussions", self.show_chats, True, 52))
        c.add_widget(self.button("Mes robots", self.show_robots, False, 48))
        c.add_widget(self.button("Tokens des robots", self.show_robot_codes, False, 48))
        c.add_widget(self.button("Paramètres du profil", self.show_settings, False, 48))
        c.add_widget(self.button("Ajouter un contact", self.add_contact, False, 44))
        c.add_widget(self.label(
            f"Contacts : {len(self.data['contacts'])}    Robots : {len(self.data['robots'])}",
            14, GREY, False, 30))
        c.add_widget(self.label(
            "Les données sont enregistrées sur cet appareil. Pour échanger réellement entre appareils, un serveur sera nécessaire.",
            12, GREY, False, 58))

    def show_chats(self):
        """Liste de discussions inspirée des messageries modernes, style WhatsApp."""
        self.clear_screen()
        root = BoxLayout(orientation="vertical", spacing=0)
        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(62),
                           padding=[dp(16), dp(8)], spacing=dp(8))
        header.add_widget(self.label("Gecord", 25, WHITE, True, 44))
        header.add_widget(self.button("⋮", self.show_home, False, 40))
        header.children[0].color = get_color_from_hex(WHITE)
        header.children[0].halign = "left"
        header.background_color = get_color_from_hex(DARK_GREEN)
        # A simple colored bar gives the familiar green messaging-app header.
        from kivy.graphics import Color, Rectangle
        with header.canvas.before:
            Color(*get_color_from_hex(DARK_GREEN))
            header._bg_rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda w, v: setattr(w._bg_rect, 'pos', v),
                    size=lambda w, v: setattr(w._bg_rect, 'size', v))
        root.add_widget(header)
        tabs = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(2), padding=[dp(6), 0])
        tabs.add_widget(self.button("DISCUSSIONS", self.show_chats, True, 40))
        tabs.add_widget(self.button("ROBOTS", self.show_robots, False, 40))
        tabs.add_widget(self.button("PROFIL", self.show_settings, False, 40))
        root.add_widget(tabs)
        search = self.field("Rechercher une discussion", height=42)
        search.size_hint_y = None
        search.padding = [dp(12), dp(8), dp(12), dp(6)]
        root.add_widget(search)
        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation="vertical", size_hint_y=None,
                            padding=[dp(8), dp(6)], spacing=dp(4))
        content.bind(minimum_height=content.setter("height"))
        entries = []
        for contact in self.data["contacts"]:
            entries.append((contact.get("name") or contact.get("email", "Contact"),
                            contact.get("email", ""), contact.get("avatar", "Contact"),
                            lambda contact=contact: self.show_chat(contact)))
        for robot in self.data["robots"]:
            entries.append((robot.get("name", "Robot"), "Robot Gecord", robot.get("avatar", "Robot"),
                            lambda robot=robot: self.show_bot_chat(robot)))
        if not entries:
            content.add_widget(self.label("Aucune discussion pour le moment.\nAjoute un contact ou crée ton premier robot.", 15, GREY, False, 86, "center"))
        else:
            for name, subtitle, avatar, callback in entries:
                row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(72), spacing=dp(10), padding=[dp(8), dp(6)])
                avatar_box = BoxLayout(size_hint_x=None, width=dp(52), padding=dp(4))
                avatar_box.add_widget(self.label(str(avatar)[:2].upper(), 16, WHITE, True, 44, "center"))
                with avatar_box.canvas.before:
                    Color(*get_color_from_hex(GREEN))
                    avatar_box._avatar_rect = Rectangle(pos=avatar_box.pos, size=avatar_box.size)
                avatar_box.bind(pos=lambda w, v: setattr(w._avatar_rect, 'pos', v),
                                size=lambda w, v: setattr(w._avatar_rect, 'size', v))
                row.add_widget(avatar_box)
                details = BoxLayout(orientation="vertical", spacing=dp(1))
                details.add_widget(self.label(name, 16, BLACK, True, 28))
                details.add_widget(self.label(subtitle, 12, GREY, False, 22))
                row.add_widget(details)
                open_btn = self.button("Ouvrir", callback, False, 42)
                open_btn.size_hint_x = None
                open_btn.width = dp(76)
                row.add_widget(open_btn)
                content.add_widget(row)
                from kivy.graphics import Color as KColor, Line
                with content.canvas.after:
                    KColor(*get_color_from_hex(BORDER))
                    Line(points=[dp(8), 0, Window.width-dp(8), 0], width=1)
        scroll.add_widget(content)
        root.add_widget(scroll)
        bottom = BoxLayout(size_hint_y=None, height=dp(54), padding=[dp(8), dp(5)], spacing=dp(8))
        bottom.add_widget(self.button("＋ Ajouter un contact", self.add_contact, True, 44))
        bottom.add_widget(self.button("☰ Menu", self.show_home, False, 44))
        root.add_widget(bottom)
        self.screen.clear_widgets()
        self.screen.add_widget(root)

    def add_contact(self):
        box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        email = self.field("Adresse e-mail du contact")
        name = self.field("Nom du contact (facultatif)")
        box.add_widget(email)
        box.add_widget(name)
        row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        pop = Popup(title="Ajouter un contact", content=box, size_hint=(0.92, None), height=dp(260))
        cancel = Button(text="Annuler")
        save = Button(text="Ajouter", background_normal="", background_color=get_color_from_hex(GREEN))
        row.add_widget(cancel)
        row.add_widget(save)
        box.add_widget(row)
        cancel.bind(on_release=pop.dismiss)
        def submit(*_):
            address = email.text.strip().lower()
            if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", address):
                self.notice("Adresse invalide", "Saisis une adresse e-mail valide.")
                return
            if address == self.data["profile"].get("email", "").lower():
                self.notice("Contact", "Tu ne peux pas t'ajouter toi-même comme contact.")
                return
            if any(x.get("email", "").lower() == address for x in self.data["contacts"]):
                self.notice("Contact déjà présent", "Cette adresse est déjà dans tes contacts.")
                return
            self.data["contacts"].append({
                "email": address, "name": name.text.strip() or address,
                "avatar": "Contact"
            })
            self.save_data()
            pop.dismiss()
            self.show_chats()
        save.bind(on_release=submit)
        pop.open()

    def show_chat(self, contact):
        self.current_contact = contact
        key = contact.get("email", "")
        history = self.data["messages"].setdefault(key, [])
        c = self.page(contact.get("name", "Discussion"), contact.get("email", ""))
        c.add_widget(self.button("Créer un robot", lambda: self.show_robot_editor(), True))
        c.add_widget(self.button("Codes des robots", self.show_robot_codes))
        message_area = BoxLayout(orientation="vertical", size_hint_y=None,
                                 spacing=dp(6))
        message_area.bind(minimum_height=message_area.setter("height"))
        if not history:
            message_area.add_widget(self.label(
                "Aucun message pour le moment. Les messages écrits ici restent sur cet appareil.",
                13, GREY, False, 52))
        for msg in history[-80:]:
            sender = "Moi" if msg.get("mine") else contact.get("name", "Contact")
            message_area.add_widget(self.label(
                f"{sender} • {msg.get('time', '')}\n{msg.get('text', '')}",
                14, BLACK, False, 52))
        scroller = ScrollView(size_hint_y=None, height=dp(250), do_scroll_x=False)
        scroller.add_widget(message_area)
        c.add_widget(scroller)
        input_box = self.field("Écris un message…", height=48)
        c.add_widget(input_box)
        c.add_widget(self.button("Envoyer", lambda: self.send_local_message(key, input_box.text), True))
        c.add_widget(self.button("Retour aux discussions", self.show_chats))

    def send_local_message(self, contact_email, text):
        text = text.strip()
        if not text:
            return
        history = self.data["messages"].setdefault(contact_email, [])
        history.append({
            "text": text, "mine": True,
            "time": datetime.now().strftime("%H:%M")
        })
        self.save_data()
        contact = next((x for x in self.data["contacts"] if x.get("email") == contact_email), None)
        if contact:
            self.show_chat(contact)

    def show_settings(self):
        profile = self.data["profile"]
        c = self.page("Paramètres", "Modifie les informations de ton profil")
        display = self.field("Nom public", profile.get("display_name", ""))
        robot_name = self.field("Nom utilisé par les robots", profile.get("robot_name", ""))
        pronunciation = self.field("Prononciation personnalisée", profile.get("pronunciation", ""))
        self.pending_profile_photo = profile.get("photo_path", "")
        c.add_widget(self.label("Photo de profil", 14, GREY, True, 24))
        photo_status = self.label(os.path.basename(profile.get("photo_path", "")) if profile.get("photo_path") else "Aucune photo sélectionnée", 12, GREY, False, 24)
        c.add_widget(photo_status)
        c.add_widget(self.button("Changer ma photo", lambda: self.choose_profile_photo(photo_status), False, 44))
        c.add_widget(self.button("Retirer ma photo", lambda: self.remove_profile_photo(photo_status), False, 40))
        c.add_widget(self.label("Adresse e-mail", 14, GREY, True, 24))
        c.add_widget(self.label(profile.get("email", ""), 16, BLACK, False, 34))
        c.add_widget(self.label("Nom public", 14, GREY, True, 24))
        c.add_widget(display)
        c.add_widget(self.label("Nom utilisé par les robots", 14, GREY, True, 24))
        c.add_widget(robot_name)
        c.add_widget(self.label("Prononciation personnalisée", 14, GREY, True, 24))
        c.add_widget(pronunciation)
        c.add_widget(self.label("Icône publique (lettre du prénom ou style prédéfini)", 14, GREY, True, 34))
        public_spinner = Spinner(text=profile.get("public_avatar", "Lettre du prénom"),
                                 values=PUBLIC_AVATARS, size_hint_y=None, height=dp(46), background_normal="", background_down="", background_color=get_color_from_hex(WHITE), color=get_color_from_hex(BLACK))
        c.add_widget(public_spinner)
        c.add_widget(self.label("Icône visible par les robots (choix prédéfinis)", 14, GREY, True, 34))
        bot_spinner = Spinner(text=profile.get("robot_avatar", "Robot"),
                              values=BOT_AVATARS, size_hint_y=None, height=dp(46), background_normal="", background_down="", background_color=get_color_from_hex(WHITE), color=get_color_from_hex(BLACK))
        c.add_widget(bot_spinner)
        email_row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        email_check = CheckBox(active=bool(profile.get("show_email", False)),
                               size_hint_x=None, width=dp(44))
        email_row.add_widget(email_check)
        email_row.add_widget(self.label("Afficher mon e-mail sur mon profil", 14, BLACK, False, 42))
        c.add_widget(email_row)

        def save():
            profile.update({
                "display_name": display.text.strip(),
                "robot_name": robot_name.text.strip(),
                "pronunciation": pronunciation.text.strip(),
                "public_avatar": public_spinner.text,
                "robot_avatar": bot_spinner.text,
                "show_email": bool(email_check.active),
                "photo_path": self.pending_profile_photo or profile.get("photo_path", "")
            })
            self.save_data()
            self.notice("Profil enregistré", "Tes paramètres ont été enregistrés sur cet appareil.")
            self.show_home()
        c.add_widget(self.button("Enregistrer les modifications", save, True))
        c.add_widget(self.button("← Retour aux discussions", self.show_chats))
        c.add_widget(self.button("SUPPRIMER MON COMPTE ET TOUTES MES DONNÉES", self.confirm_delete_account, False, 54))
        c.children[0].background_color = get_color_from_hex("#D93025")
        c.children[0].color = get_color_from_hex(WHITE)

    def confirm_delete_account(self):
        box = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(12))
        box.add_widget(Label(text="Attention : cette action efface le profil local, les contacts, les discussions et les robots enregistrés sur cet appareil. Elle est irréversible.",
                             color=get_color_from_hex(BLACK), halign="center", valign="middle"))
        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        pop = Popup(title="Supprimer le compte ?", content=box, size_hint=(0.92, None), height=dp(250), auto_dismiss=False)
        cancel = Button(text="Annuler")
        delete = Button(text="Supprimer tout", background_normal="", background_color=get_color_from_hex("#D93025"), color=get_color_from_hex(WHITE))
        row.add_widget(cancel); row.add_widget(delete); box.add_widget(row)
        cancel.bind(on_release=pop.dismiss)
        def perform_delete(*_):
            pop.dismiss()
            try:
                if os.path.isfile(self.data_path):
                    os.remove(self.data_path)
            except OSError as exc:
                self.notice("Suppression impossible", str(exc))
                return
            self.data = default_data()
            self.current_contact = None
            self.pending_profile_photo = ""
            self.show_start_screen()
            self.notice("Compte supprimé", "Le profil et les données locales de Gecord ont été supprimés de cet appareil.")
        delete.bind(on_release=perform_delete)
        pop.open()

    def remove_profile_photo(self, status_label=None):
        self.pending_profile_photo = ""
        self.data["profile"]["photo_path"] = ""
        self.save_data()
        if status_label:
            status_label.text = "Aucune photo sélectionnée"

    def show_robots(self):
        c = self.page("Mes robots", "Crée et gère les robots de ton compte")
        c.add_widget(self.button("＋ Créer un robot", self.show_robot_editor, True))
        if not self.data["robots"]:
            c.add_widget(self.label("Tu n'as pas encore créé de robot.", 15, GREY, False, 48))
        for robot in self.data["robots"]:
            visibility = robot.get("visibility", "privé")
            c.add_widget(self.button(
                f"{robot.get('avatar', 'Robot')}  {robot.get('name', 'Robot')}\nVisibilité : {visibility}",
                lambda robot=robot: self.show_robot_editor(robot), False, 64))
            c.add_widget(self.button(
                f"Ouvrir la discussion avec {robot.get('name', 'ce robot')}",
                lambda robot=robot: self.show_bot_chat(robot), True, 42))
        c.add_widget(self.button("Voir tous les codes Python", self.show_robot_codes))
        c.add_widget(self.button("Accueil", self.show_home))

    def show_robot_editor(self, robot=None):
        is_new = robot is None
        robot = robot or {
            "id": f"robot_{int(datetime.now().timestamp() * 1000)}",
            "name": "", "email": "", "avatar": BOT_AVATARS[0],
            "visibility": "privé", "allowed_contacts": [], "profile": "",
            "token_hash": "", "token_created": ""
        }
        c = self.page("Créer un robot" if is_new else "Modifier un robot",
                      "Personnalise son identité et qui peut l'utiliser")
        name = self.field("Nom du robot", robot.get("name", ""))
        email = self.field("Adresse e-mail du robot (facultatif)", robot.get("email", ""))
        profile = self.field("Description / profil du robot", robot.get("profile", ""),
                             multiline=True, height=100)
        c.add_widget(self.label("Nom du robot", 14, GREY, True, 24))
        c.add_widget(name)
        c.add_widget(self.label("Adresse e-mail facultative", 14, GREY, True, 24))
        c.add_widget(email)
        c.add_widget(self.label("Icône du robot", 14, GREY, True, 24))
        avatar = Spinner(text=robot.get("avatar", BOT_AVATARS[0]), values=BOT_AVATARS,
                         size_hint_y=None, height=dp(46), background_normal="", background_down="", background_color=get_color_from_hex(WHITE), color=get_color_from_hex(BLACK))
        c.add_widget(avatar)
        c.add_widget(self.label("Description / profil", 14, GREY, True, 24))
        c.add_widget(profile)
        c.add_widget(self.label("Qui peut utiliser ce robot ?", 14, GREY, True, 24))
        visibility = Spinner(text=robot.get("visibility", "privé"),
                             values=["privé", "contacts sélectionnés", "public"],
                             size_hint_y=None, height=dp(46), background_normal="", background_down="", background_color=get_color_from_hex(WHITE), color=get_color_from_hex(BLACK))
        c.add_widget(visibility)
        c.add_widget(self.label("Contacts autorisés (e-mails séparés par des virgules)", 13, GREY, True, 34))
        allowed = self.field("contact1@exemple.fr, contact2@exemple.fr",
                             ", ".join(robot.get("allowed_contacts", [])))
        c.add_widget(allowed)
        c.add_widget(self.label(
            "Écris le code Python dans ton propre programme. Le token identifie ce robot auprès de l'API Gecord.",
            12, GREY, False, 56))
        def save_robot():
            robot_name = name.text.strip()
            if not robot_name:
                self.notice("Nom manquant", "Donne un nom à ton robot.")
                return
            robot_email = email.text.strip().lower()
            if robot_email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", robot_email):
                self.notice("Adresse invalide", "L'adresse facultative doit être valide ou rester vide.")
                return
            allowed_list = [x.strip().lower() for x in allowed.text.split(",") if x.strip()]
            if visibility.text == "contacts sélectionnés" and not allowed_list:
                self.notice("Contacts manquants", "Ajoute au moins un e-mail autorisé.")
                return
            robot.update({
                "name": robot_name, "email": robot_email,
                "avatar": avatar.text, "profile": profile.text.strip(),
                "visibility": visibility.text,
                "allowed_contacts": allowed_list
            })
            if is_new:
                # Le token est affiché une seule fois ; seule son empreinte est sauvegardée.
                raw_token = "gecord26_" + secrets.token_urlsafe(32)
                robot["token_hash"] = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
                robot["token_created"] = datetime.now().isoformat(timespec="seconds")
                self.data["robots"].append(robot)
                self.save_data()
                self.show_token_once(robot, raw_token)
            else:
                self.save_data()
                self.notice("Robot enregistré", "Les paramètres du robot ont été enregistrés sur cet appareil.")
                self.show_robots()
        c.add_widget(self.button("Enregistrer le robot", save_robot, True))
        c.add_widget(self.button("Annuler", self.show_robots))

    def show_bot_chat(self, robot):
        """Discussion locale de démonstration avec un robot."""
        bot_id = robot.get("id", robot.get("name", "robot"))
        key = "bot:" + bot_id
        history = self.data["messages"].setdefault(key, [])
        # Remove legacy GBV26 system messages from older prototype data.
        history[:] = [m for m in history if not (m.get("system") and m.get("text") == "GBV26")]
        c = self.page(f"{robot.get('avatar', 'Robot')}  {robot.get('name', 'Robot')}", "Discussion locale avec ton robot")
        area = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        area.bind(minimum_height=area.setter("height"))
        if not history:
            area.add_widget(self.label("Aucun message pour le moment.", 14, GREY, False, 42))
        for msg in history[-100:]:
            sender = "Moi" if msg.get("mine") else robot.get("name", "Robot")
            area.add_widget(self.label(f"{sender} • {msg.get('time', '')}\n{msg.get('text', '')}", 14, BLACK, False, 52))
        scroll = ScrollView(size_hint_y=None, height=dp(260), do_scroll_x=False)
        scroll.add_widget(area)
        c.add_widget(scroll)
        inp = self.field("Écris un message…", height=48)
        c.add_widget(inp)
        def send():
            value = inp.text.strip()
            if not value:
                return
            history.append({"text": value, "mine": True, "time": datetime.now().strftime("%H:%M")})
            self.save_data()
            self.show_bot_chat(robot)
        c.add_widget(self.button("Envoyer", send, True))
        c.add_widget(self.button("Retour aux discussions", self.show_chats))

    def avatar_badge(self, avatar_name, display_name=""):
        """Représentation textuelle sans emoji."""
        if avatar_name == "Lettre du prénom":
            name = (display_name or "?").strip()
            return name[:1].upper() if name else "?"
        return (avatar_name or "?")[:2].upper()

    def show_token_once(self, robot, raw_token):
        box = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        box.add_widget(Label(
            text="Token créé. Copie-le maintenant et garde-le secret. "
                 "Gecord ne pourra pas le réafficher plus tard.",
            color=get_color_from_hex(BLACK), halign="left", valign="middle"))
        token_field = TextInput(
            text=raw_token, readonly=True, multiline=True, size_hint_y=None,
            height=dp(86), font_size=dp(13),
            foreground_color=get_color_from_hex(BLACK),
            background_color=get_color_from_hex(LIGHT_GREY))
        box.add_widget(token_field)
        row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        copy_btn = Button(text="Copier le token", background_normal="",
                          background_color=get_color_from_hex(GREEN),
                          color=get_color_from_hex(WHITE))
        done_btn = Button(text="J'ai copié", background_normal="",
                          background_color=get_color_from_hex(LIGHT_GREY),
                          color=get_color_from_hex(BLACK))
        row.add_widget(copy_btn)
        row.add_widget(done_btn)
        box.add_widget(row)
        pop = Popup(title=f"Token — {robot.get('name', 'Robot')}",
                    content=box, size_hint=(0.92, None), height=dp(300),
                    auto_dismiss=False)

        def copy_token(*_):
            try:
                Clipboard.copy(raw_token)
                copy_btn.text = "Token copié"
            except Exception:
                self.notice("Copie impossible", "Sélectionne le token et copie-le manuellement.")

        def finish(*_):
            pop.dismiss()
            self.show_robots()

        copy_btn.bind(on_release=copy_token)
        done_btn.bind(on_release=finish)
        pop.open()

    def regenerate_token(self, robot):
        raw_token = "gecord26_" + secrets.token_urlsafe(32)
        robot["token_hash"] = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        robot["token_created"] = datetime.now().isoformat(timespec="seconds")
        self.save_data()
        self.show_token_once(robot, raw_token)

    def show_robot_codes(self):
        c = self.page("Tokens des robots", "Gère les clés utilisées par tes programmes Python")
        c.add_widget(self.label(
            "Les tokens sont générés localement dans ce prototype. Ils ne seront acceptés par aucun serveur tant que l'API Gecord n'est pas créée.",
            13, GREY, False, 70))
        if not self.data["robots"]:
            c.add_widget(self.label("Aucun robot. Crée d'abord un robot.", 15, GREY, False, 48))
        for robot in self.data["robots"]:
            c.add_widget(self.label(
                f"{robot.get('avatar', 'Robot')}  {robot.get('name', 'Robot')}",
                16, BLACK, True, 30))
            c.add_widget(self.label(
                "Token : créé" if robot.get("token_hash") else "Token : absent",
                13, GREY, False, 26))
            c.add_widget(self.button(
                "Régénérer le token (l'ancien sera remplacé)",
                lambda robot=robot: self.confirm_regenerate_token(robot), True, 44))
        c.add_widget(self.button("Créer un robot", self.show_robot_editor, False))
        c.add_widget(self.button("Retour à l'accueil", self.show_home))

    def confirm_regenerate_token(self, robot):
        box = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(12))
        box.add_widget(Label(
            text="L'ancien token sera remplacé. Tu devras mettre le nouveau token dans ton programme Python.",
            color=get_color_from_hex(BLACK)))
        row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        cancel = Button(text="Annuler")
        confirm = Button(text="Régénérer", background_normal="",
                         background_color=get_color_from_hex(GREEN),
                         color=get_color_from_hex(WHITE))
        row.add_widget(cancel)
        row.add_widget(confirm)
        box.add_widget(row)
        pop = Popup(title="Régénérer le token", content=box,
                    size_hint=(0.9, None), height=dp(220))
        cancel.bind(on_release=pop.dismiss)

        def go(*_):
            pop.dismiss()
            self.regenerate_token(robot)

        confirm.bind(on_release=go)
        pop.open()


if __name__ == "__main__":
    GecordApp().run()

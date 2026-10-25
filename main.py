
import logging
import threading
from urllib.parse import urlparse

import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition

CURRENT_VERSION = "1.0"
VERSION_URL = (
    "https://raw.githubusercontent.com/"
    "ShampooingBon/gecord/main/version.json"
)

Window.clearcolor = (1, 1, 1, 1)


class GecordApp(App):
    def build(self):
        self.title = "Gecord"
        self.manager = ScreenManager(
            transition=FadeTransition()
        )

        splash = Screen(name="splash")
        layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=10
        )
        layout.add_widget(Label(text=""))
        layout.add_widget(Label(
            text="[b]Gecord[/b]",
            markup=True,
            color=(0.1, 0.6, 0.3, 1),
            font_size="42sp"
        ))
        layout.add_widget(Label(text=""))
        layout.add_widget(Label(
            text="Fait par L'Entreprise BV",
            color=(0.2, 0.2, 0.2, 1),
            font_size="14sp",
            size_hint_y=None,
            height=35
        ))
        splash.add_widget(layout)

        self.home = Screen(name="home")
        home_layout = BoxLayout(
            orientation="vertical",
            padding=24,
            spacing=16
        )
        home_layout.add_widget(Label(
            text="[b]Bienvenue dans Gecord ![/b]",
            markup=True,
            color=(0.1, 0.6, 0.3, 1),
            font_size="26sp"
        ))

        self.status = Label(
            text="Vérification des mises à jour...",
            color=(0.15, 0.15, 0.15, 1)
        )
        home_layout.add_widget(self.status)

        self.update_button = Button(
            text="Ouvrir la mise à jour",
            disabled=True,
            opacity=0,
            size_hint_y=None,
            height=50
        )
        self.update_button.bind(
            on_release=self.open_update
        )
        home_layout.add_widget(self.update_button)
        self.home.add_widget(home_layout)

        self.manager.add_widget(splash)
        self.manager.add_widget(self.home)
        self.manager.current = "splash"

        Clock.schedule_once(self.open_home, 2)
        return self.manager

    def open_home(self, _dt):
        self.manager.current = "home"
        threading.Thread(
            target=self.check_updates,
            daemon=True
        ).start()

    def check_updates(self):
        try:
            response = requests.get(
                VERSION_URL,
                timeout=6
            )
            response.raise_for_status()
            data = response.json()

            latest = data.get("version", CURRENT_VERSION)
            apk_url = data.get("apk_url", "")

            def compare(version):
                try:
                    return tuple(
                        int(part)
                        for part in version.split(".")
                    )
                except (ValueError, AttributeError):
                    return (0,)

            if compare(latest) > compare(CURRENT_VERSION):
                if (
                    isinstance(apk_url, str)
                    and urlparse(apk_url).scheme == "https"
                ):
                    Clock.schedule_once(
                        lambda dt: self.show_update(
                            latest, apk_url
                        ), 0
                    )
                else:
                    Clock.schedule_once(
                        lambda dt: setattr(
                            self.status,
                            "text",
                            "Lien de mise à jour invalide."
                        ), 0
                    )
            else:
                Clock.schedule_once(
                    lambda dt: setattr(
                        self.status,
                        "text",
                        f"Gecord est à jour — version {CURRENT_VERSION}"
                    ), 0
                )

        except Exception:
            logging.exception("Erreur de vérification")
            Clock.schedule_once(
                lambda dt: setattr(
                    self.status,
                    "text",
                    f"Version {CURRENT_VERSION} — hors ligne"
                ), 0
            )

    def show_update(self, version, url):
        self.status.text = (
            f"Nouvelle version : {version}\n"
            f"Version installée : {CURRENT_VERSION}"
        )
        self.update_button.disabled = False
        self.update_button.opacity = 1
        self.update_button.url = url

    def open_update(self, button):
        import webbrowser
        webbrowser.open(button.url)


if __name__ == "__main__":
    GecordApp().run()

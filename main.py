import os
import threading
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock

# Numéro de version actuel de ton appli installée
CURRENT_VERSION = "1.0"

# Remplace "ton-pseudo" par ton vrai nom d'utilisateur GitHub et "gecord" par le nom de ton dépôt
VERSION_URL = "https://raw.githubusercontent.com/ShampooingBon/gecord/main/version.json"
class GecordRoot(BoxLayout):
    def __init__(self, **kwargs):
        super(GecordRoot, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 20

        # Affichage initial pendant la vérification
        self.info_label = Label(
            text='Vérification des mises à jour...',
            color=(1, 1, 1, 1),
            font_size='20sp'
        )
        self.add_widget(self.info_label)

        # Lancement de la vérification automatique en arrière-plan au démarrage
        threading.Thread(target=self.check_for_updates).start()

    def check_for_updates(self):
        """Va chercher le fichier version.json sur GitHub pour comparer les versions"""
        try:
            response = requests.get(VERSION_URL, timeout=3)
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get("version")
                apk_url = data.get("apk_url")
                
                if latest_version != CURRENT_VERSION:
                    # Mise à jour trouvée, on lance le téléchargement automatique
                    Clock.schedule_once(lambda dt: setattr(self.info_label, 'text', "Mise à jour détectée..."), 0)
                    self.download_and_install(apk_url)
                    return
        except Exception as e:
            print(f"Vérification de mise à jour impossible : {e}")
        
        # Si pas de mise à jour (ou si échec réseau), on lance l'application principale
        Clock.schedule_once(self.launch_main_app, 1)

    def download_and_install(self, apk_url):
        """Télécharge le nouvel APK et lance l'installation Android native automatiquement"""
        try:
            Clock.schedule_once(lambda dt: setattr(self.info_label, 'text', "Téléchargement en cours..."), 0)
            
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            context = activity.getApplicationContext()
            
            cache_dir = context.getCacheDir().getAbsolutePath()
            apk_path = os.path.join(cache_dir, "update.apk")
            
            r = requests.get(apk_url, stream=True)
            with open(apk_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            Clock.schedule_once(lambda dt: setattr(self.info_label, 'text', "Installation..."), 0)
            
            Intent = autoclass('android.content.Intent')
            File = autoclass('java.io.File')
            FileProvider = autoclass('androidx.core.content.FileProvider')
            
            file_obj = File(apk_path)
            uri = FileProvider.getUriForFile(context, context.getPackageName() + ".fileprovider", file_obj)
            
            intent = Intent(Intent.ACTION_VIEW)
            intent.setDataAndType(uri, "application/vnd.android.package-archive")
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            
            activity.startActivity(intent)
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour : {e}")
            Clock.schedule_once(lambda dt: self.launch_main_app, 2)

    def launch_main_app(self, dt):
        """Passe le relais à ton interface principale"""
        self.clear_widgets()
        # Ici on charge ton interface ou tes widgets principaux
        self.add_widget(Label(text="Bienvenue dans Gecord !", color=(1, 1, 1, 1), font_size='22sp'))


class GecordApp(App):
    def build(self):
        return GecordRoot()


if __name__ == '__main__':
    GecordApp().run()

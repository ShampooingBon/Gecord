from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

class GecordApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Gecord App en route !'))
        return layout

if __name__ == '__main__':
    GecordApp().run()

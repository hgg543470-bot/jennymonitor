from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from screens.menu_screen import MenuScreen
from screens.crypto_screen import CryptoScreen
from screens.detail_screen import DetailScreen

class JennyMonitorApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(MenuScreen(name='menu'))
        self.sm.add_widget(CryptoScreen(name='crypto'))
        self.sm.add_widget(DetailScreen(name='detail'))
        return self.sm

    def open_details(self, data):
        sc = self.sm.get_screen('detail')
        sc.load_data(data)
        self.sm.current = 'detail'

if __name__ == '__main__':
    JennyMonitorApp().run()
    

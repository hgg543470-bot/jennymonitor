from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
import requests

# Настройка цвета фона (темный футуризм)
Window.clearcolor = get_color_from_hex('#121212')

class JennyMonitor(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=40, spacing=20, **kwargs)
        
        # Заголовок
        self.label_title = Label(
            text='JENNY MONITOR v1.0',
            font_size='32sp',
            color=get_color_from_hex('#00FF41'), # Матричный зеленый
            bold=True
        )
        self.add_widget(self.label_title)

        # Поле статуса
        self.label_status = Label(
            text='Система готова к работе',
            font_size='18sp',
            color=get_color_from_hex('#FFFFFF')
        )
        self.add_widget(self.label_status)

        # Кнопка проверки
        self.btn_check = Button(
            text='ПРОВЕРИТЬ СВЯЗЬ',
            size_hint=(1, 0.3),
            background_color=get_color_from_hex('#1DB954'),
            background_normal='',
            font_size='20sp',
            bold=True
        )
        self.btn_check.bind(on_press=self.check_network)
        self.add_widget(self.btn_check)

    def check_network(self, instance):
        self.label_status.text = "Выполняю запрос..."
        try:
            # Пробуем достучаться до гугла
            response = requests.get("https://www.google.com", timeout=5)
            if response.status_code == 200:
                self.label_status.text = "СТАТУС: ONLINE\nОтвет получен (200 OK)"
                self.label_status.color = get_color_from_hex('#00FF00')
            else:
                self.label_status.text = f"СТАТУС: ОШИБКА\nКод: {response.status_code}"
                self.label_status.color = get_color_from_hex('#FF3D00')
        except Exception as e:
            self.label_status.text = f"СТАТУС: OFFLINE\nОшибка: {str(e)[:40]}..."
            self.label_status.color = get_color_from_hex('#FF0000')

class MonitorApp(App):
    def build(self):
        self.title = 'Jenny Monitor'
        return JennyMonitor()

if __name__ == '__main__':
    MonitorApp().run()
  

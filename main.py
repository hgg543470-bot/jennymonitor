from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.utils import platform
import random

# --- ЭКРАН 1: ГЛАВНОЕ МЕНЮ (С системными правами) ---
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        
        # Тот самый информационный лейбл из твоего старого кода
        self.info_label = Label(
            text="JennyMonitor v0.2\n[color=#ffff00]Жду команд...[/color]",
            halign='center', 
            markup=True, 
            font_size='20sp'
        )
        layout.add_widget(self.info_label)

        # Новые кнопки бирж
        btn_stocks = Button(text="📊 БИРЖА КОМПАНИЙ", size_hint=(1, 0.25), background_color=(0.2, 0.6, 1, 1))
        btn_stocks.bind(on_press=self.go_to_stocks)
        layout.add_widget(btn_stocks)

        btn_crypto = Button(text="💎 КРИПТОБИРЖА", size_hint=(1, 0.25), background_color=(0.6, 0.2, 1, 1))
        btn_crypto.bind(on_press=self.go_to_crypto)
        layout.add_widget(btn_crypto)

        # Твои кнопки для системных прав
        btn_notify = Button(text="1. Разрешить уведомления", size_hint=(1, 0.2))
        btn_notify.bind(on_press=self.ask_notifications)
        layout.add_widget(btn_notify)

        btn_files = Button(text="2. Дать доступ ко всем файлам", size_hint=(1, 0.2))
        btn_files.bind(on_press=self.ask_files_access)
        layout.add_widget(btn_files)

        self.add_widget(layout)

    # Функции перехода по экранам
    def go_to_stocks(self, instance):
        self.manager.current = 'stocks'

    def go_to_crypto(self, instance):
        self.manager.current = 'crypto'

    # Твой системный код для прав без изменений
    def ask_notifications(self, instance):
        if platform == 'android':
            from android.permissions import request_permissions
            request_permissions(['android.permission.POST_NOTIFICATIONS'])
            self.info_label.text = "Вызвано окно уведомлений!"
        else:
            self.info_label.text = "Это ПК, права не нужны."

    def ask_files_access(self, instance):
        if platform == 'android':
            from jnius import autoclass
            Environment = autoclass('android.os.Environment')
            
            if not Environment.isExternalStorageManager():
                self.info_label.text = "Открываю системные настройки..."
                Intent = autoclass('android.content.Intent')
                Settings = autoclass('android.provider.Settings')
                Uri = autoclass('android.net.Uri')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                
                intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
                uri = Uri.parse("package:" + PythonActivity.mActivity.getPackageName())
                intent.setData(uri)
                PythonActivity.mActivity.startActivity(intent)
            else:
                self.info_label.text = "[color=#00ff00]Доступ к файлам УЖЕ ПОЛУЧЕН![/color]"
        else:
            self.info_label.text = "Это ПК, права не нужны."


# --- ЭКРАН 2: БИРЖА КОМПАНИЙ ---
class StockScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10)
        
        header = BoxLayout(size_hint_y=0.1)
        btn_back = Button(text="< Назад", size_hint_x=0.3)
        btn_back.bind(on_press=self.back)
        header.add_widget(btn_back)
        header.add_widget(Label(text="Акции (USD)", font_size='18sp'))
        self.layout.add_widget(header)

        self.scroll = ScrollView(size_hint=(1, 0.8))
        self.stock_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.stock_list.bind(minimum_height=self.stock_list.setter('height'))
        self.scroll.add_widget(self.stock_list)
        self.layout.add_widget(self.scroll)

        self.search_input = TextInput(hint_text="Поиск компании...", size_hint_y=0.1, multiline=False)
        self.search_input.bind(text=self.on_search)
        self.layout.add_widget(self.search_input)

        self.add_widget(self.layout)

        self.all_stocks = [
            {"name": "Apple", "info": "Технологии", "price": 175.2, "change": 1.2},
            {"name": "Tesla", "info": "Электрокары", "price": 160.5, "change": -2.5},
            {"name": "Nvidia", "info": "Чипы", "price": 890.1, "change": 4.8},
        ]
        self.update_list(self.all_stocks)
        Clock.schedule_interval(self.refresh_data, 30)

    def update_list(self, data):
        self.stock_list.clear_widgets()
        for s in data:
            color = "#00ff00" if s['change'] >= 0 else "#ff0000"
            sign = "+" if s['change'] >= 0 else ""
            row = Label(
                text=f"[b]{s['name']}[/b] ({s['info']})\nЦена: {s['price']}$ | [color={color}]{sign}{s['change']}%[/color]",
                markup=True, size_hint_y=None, height=90, halign='left', valign='middle'
            )
            row.bind(size=row.setter('text_size'))
            self.stock_list.add_widget(row)

    def on_search(self, instance, value):
        filtered = [s for s in self.all_stocks if value.lower() in s['name'].lower()]
        self.update_list(filtered)

    def refresh_data(self, dt):
        for s in self.all_stocks:
            s['price'] += round(random.uniform(-1, 1), 2)
            s['change'] += round(random.uniform(-0.1, 0.1), 2)
        if not self.search_input.text:
            self.update_list(self.all_stocks)

    def back(self, instance):
        self.manager.current = 'menu'


# --- ЭКРАН 3: КРИПТОБИРЖА ---
class CryptoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10)
        
        header = BoxLayout(size_hint_y=0.1)
        btn_back = Button(text="< Назад", size_hint_x=0.3)
        btn_back.bind(on_press=self.back)
        header.add_widget(btn_back)
        header.add_widget(Label(text="Крипта (USD)", font_size='18sp'))
        self.layout.add_widget(header)

        self.scroll = ScrollView(size_hint=(1, 0.8))
        self.crypto_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        self.crypto_list.bind(minimum_height=self.crypto_list.setter('height'))
        self.scroll.add_widget(self.crypto_list)
        self.layout.add_widget(self.scroll)

        self.search_input = TextInput(hint_text="Поиск монеты (напр. BTC)...", size_hint_y=0.1, multiline=False)
        self.search_input.bind(text=self.on_search)
        self.layout.add_widget(self.search_input)

        self.add_widget(self.layout)

        self.all_crypto = [
            {"name": "Bitcoin", "symbol": "BTC", "info": "Layer 1", "price": 64150.0, "change": 2.4, "cap": "$1.26 T", "whale": "12 мин назад ($45M)"},
            {"name": "Ethereum", "symbol": "ETH", "info": "Smart Contracts", "price": 3420.5, "change": -1.1, "cap": "$410 B", "whale": "1 ч назад ($12M)"},
            {"name": "Solana", "symbol": "SOL", "info": "High-Speed L1", "price": 145.3, "change": 8.5, "cap": "$65 B", "whale": "3 мин назад ($5M)"},
            {"name": "Dogecoin", "symbol": "DOGE", "info": "Meme coin", "price": 0.15, "change": 0.2, "cap": "$22 B", "whale": "Нет крупных за 24ч"},
        ]
        self.update_list(self.all_crypto)
        Clock.schedule_interval(self.refresh_data, 30)

    def update_list(self, data):
        self.crypto_list.clear_widgets()
        for c in data:
            color = "#00ff00" if c['change'] >= 0 else "#ff0000"
            sign = "+" if c['change'] >= 0 else ""
            
            text_content = (
                f"[b]{c['name']} ({c['symbol']})[/b] - {c['info']}\n"
                f"Цена: {c['price']}$ | [color={color}]{sign}{c['change']}%[/color]\n"
                f"Капитализация: {c['cap']} | Кит: {c['whale']}"
            )
            
            row = Label(
                text=text_content,
                markup=True,
                size_hint_y=None,
                height=110,
                halign='left',
                valign='middle'
            )
            row.bind(size=row.setter('text_size'))
            self.crypto_list.add_widget(row)

    def on_search(self, instance, value):
        filtered = [c for c in self.all_crypto if value.lower() in c['name'].lower() or value.lower() in c['symbol'].lower()]
        self.update_list(filtered)

    def refresh_data(self, dt):
        for c in self.all_crypto:
            c['price'] += round(random.uniform(-5, 5), 2)
            c['change'] += round(random.uniform(-0.5, 0.5), 2)
        if not self.search_input.text:
            self.update_list(self.all_crypto)

    def back(self, instance):
        self.manager.current = 'menu'


# --- ГЛАВНОЕ ПРИЛОЖЕНИЕ ---
class JennyMonitorApp(App):
    def build(self):
        sm = ScreenManager()
        # Добавляем все экраны в менеджер
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(StockScreen(name='stocks'))
        sm.add_widget(CryptoScreen(name='crypto'))
        return sm

if __name__ == '__main__':
    JennyMonitorApp().run()
    

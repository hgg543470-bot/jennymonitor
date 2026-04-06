from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock
from kivy.utils import platform
from kivy.graphics import Color, Line
import requests
import threading

# Глобальное хранилище векторов
history_cache = {}

# --- ЭКРАН 1: ГЛАВНОЕ МЕНЮ (Кнопки 100x100 по центру) ---
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Основной фон
        main_layout = BoxLayout(orientation='vertical', padding=20)
        
        # Верхний статус-лейбл (оставим сверху для инфы)
        self.info_label = Label(
            text="JennyMonitor v0.4.2", 
            size_hint_y=0.2, markup=True, font_size='18sp'
        )
        main_layout.add_widget(self.info_label)

        # Центрирующий контейнер
        anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        
        # Сетка для маленьких кнопок
        btns_grid = BoxLayout(orientation='vertical', spacing=10, size_hint=(None, None))
        btns_grid.bind(minimum_height=btns_grid.setter('height'), minimum_width=btns_grid.setter('width'))

        # Создаем кнопки 100x100
        btn_crypto = Button(text="Крипто", size_hint=(None, None), size=(100, 100), background_color=(0.6, 0.2, 1, 1))
        btn_crypto.bind(on_press=self.go_to_crypto)
        
        btn_notify = Button(text="Увед.", size_hint=(None, None), size=(100, 100))
        btn_notify.bind(on_press=self.ask_notifications)
        
        btn_files = Button(text="Файлы", size_hint=(None, None), size=(100, 100))
        btn_files.bind(on_press=self.ask_files_access)

        # Добавляем их в центр
        btns_grid.add_widget(btn_crypto)
        btns_grid.add_widget(btn_notify)
        btns_grid.add_widget(btn_files)
        
        anchor.add_widget(btns_grid)
        main_layout.add_widget(anchor)
        
        # Пустой виджет снизу для баланса, чтобы кнопки были именно в центре
        main_layout.add_widget(BoxLayout(size_hint_y=0.2))

        self.add_widget(main_layout)

    def go_to_crypto(self, instance):
        self.manager.current = 'crypto'

    def ask_notifications(self, instance):
        if platform == 'android':
            from android.permissions import request_permissions
            request_permissions(['android.permission.POST_NOTIFICATIONS'])
            self.info_label.text = "Запрос уведомлений..."

    def ask_files_access(self, instance):
        if platform == 'android':
            from jnius import autoclass
            Environment = autoclass('android.os.Environment')
            if not Environment.isExternalStorageManager():
                Intent = autoclass('android.content.Intent')
                Settings = autoclass('android.provider.Settings')
                Uri = autoclass('android.net.Uri')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
                uri = Uri.parse("package:" + PythonActivity.mActivity.getPackageName())
                intent.setData(uri)
                PythonActivity.mActivity.startActivity(intent)
            else:
                self.info_label.text = "[color=#00ff00]Доступ есть[/color]"

# --- ЭКРАН 2: СПИСОК КРИПТЫ (Без изменений) ---
class CryptoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10)
        header = BoxLayout(size_hint_y=0.1)
        btn_back = Button(text="<", size_hint_x=0.2)
        btn_back.bind(on_press=self.back)
        header.add_widget(btn_back)
        self.status_label = Label(text="Загрузка...", size_hint_x=0.8)
        header.add_widget(self.status_label)
        self.layout.add_widget(header)
        self.scroll = ScrollView()
        self.crypto_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.crypto_list.bind(minimum_height=self.crypto_list.setter('height'))
        self.scroll.add_widget(self.crypto_list)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)
        self.all_crypto = []
        self.refresh_data()
        Clock.schedule_interval(lambda dt: self.refresh_data(), 30)

    def refresh_data(self):
        threading.Thread(target=self.fetch_api).start()

    def fetch_api(self):
        try:
            url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=1"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                self.all_crypto = []
                for item in data:
                    c_id = item['id']
                    price = item['current_price']
                    if c_id not in history_cache: history_cache[c_id] = []
                    history_cache[c_id].append(price)
                    if len(history_cache[c_id]) > 40: history_cache[c_id].pop(0)
                    self.all_crypto.append({
                        "id": c_id, "name": item['name'], "symbol": item['symbol'].upper(),
                        "price": price, "change": round(item.get("price_change_percentage_24h") or 0, 2)
                    })
                Clock.schedule_once(lambda dt: self.update_ui())
        except: pass

    def update_ui(self):
        self.crypto_list.clear_widgets()
        self.status_label.text = "Крипта Live"
        for c in self.all_crypto:
            color = "#00ff00" if c['change'] >= 0 else "#ff0000"
            btn = Button(text=f"{c['symbol']} | {c['price']}$ | {c['change']}%", markup=True, size_hint_y=None, height=80)
            btn.bind(on_release=lambda x, d=c: App.get_running_app().open_details(d))
            self.crypto_list.add_widget(btn)

    def back(self, instance): self.manager.current = 'menu'

# --- ЭКРАН 3: ГРАФИК (Без изменений) ---
class DetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20)
        btn_back = Button(text="< Назад", size_hint_y=0.1)
        btn_back.bind(on_press=self.back)
        self.layout.add_widget(btn_back)
        self.label = Label(text="", font_size='20sp', size_hint_y=0.2, markup=True)
        self.layout.add_widget(self.label)
        self.chart_area = BoxLayout(size_hint_y=0.7)
        self.layout.add_widget(self.chart_area)
        self.add_widget(self.layout)
        self.current_id = None

    def load_data(self, coin):
        self.current_id = coin['id']
        self.label.text = f"[b]{coin['name']}[/b]\n{coin['price']} $"
        Clock.schedule_once(lambda dt: self.draw_vector(), 0.1)

    def draw_vector(self):
        self.chart_area.canvas.after.clear()
        prices = history_cache.get(self.current_id, [])
        if len(prices) < 2: return
        with self.chart_area.canvas.after:
            Color(0, 0.7, 1, 1)
            w, h = self.chart_area.width, self.chart_area.height
            x0, y0 = self.chart_area.x, self.chart_area.y
            p_min, p_max = min(prices), max(prices)
            p_range = (p_max - p_min) if p_max != p_min else 1
            pts = []
            for i, p in enumerate(prices):
                pts.extend([x0 + (i/(len(prices)-1))*w, y0 + ((p-p_min)/p_range)*h])
            Line(points=pts, width=2)

    def back(self, instance): self.manager.current = 'crypto'

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
    

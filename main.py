from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock
from kivy.utils import platform
from kivy.graphics import Color, Line, Ellipse
import requests
import threading

# Глобальное хранилище векторов
history_cache = {}

# --- ЭКРАН 1: ГЛАВНОЕ МЕНЮ (Кнопки 200x200 по центру) ---
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical', padding=20)
        
        self.info_label = Label(
            text="JennyMonitor v0.5", 
            size_hint_y=0.1, markup=True, font_size='18sp'
        )
        main_layout.add_widget(self.info_label)

        anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        
        # Сетка кнопок 200x200
        btns_grid = BoxLayout(orientation='vertical', spacing=15, size_hint=(None, None))
        btns_grid.bind(minimum_height=btns_grid.setter('height'), minimum_width=btns_grid.setter('width'))

        # Кнопки
        btn_crypto = Button(text="КРИПТА", size_hint=(None, None), size=(200, 200), background_color=(0.6, 0.2, 1, 1))
        btn_crypto.bind(on_press=self.go_to_crypto)
        
        btn_stocks = Button(text="БИРЖА", size_hint=(None, None), size=(200, 200), background_color=(0.2, 0.6, 1, 1))
        
        btn_files = Button(text="ФАЙЛЫ", size_hint=(None, None), size=(200, 200))
        btn_files.bind(on_press=self.ask_files_access)

        btns_grid.add_widget(btn_crypto)
        btns_grid.add_widget(btn_stocks)
        btns_grid.add_widget(btn_files)
        
        anchor.add_widget(btns_grid)
        main_layout.add_widget(anchor)
        main_layout.add_widget(BoxLayout(size_hint_y=0.1))

        self.add_widget(main_layout)

    def go_to_crypto(self, instance):
        self.manager.current = 'crypto'

    def ask_files_access(self, instance):
        if platform == 'android':
            from jnius import autoclass
            Env = autoclass('android.os.Environment')
            if not Env.isExternalStorageManager():
                Intent = autoclass('android.content.Intent')
                Settings = autoclass('android.provider.Settings')
                Uri = autoclass('android.net.Uri')
                Activity = autoclass('org.kivy.android.PythonActivity')
                intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
                uri = Uri.parse("package:" + Activity.mActivity.getPackageName())
                intent.setData(uri)
                Activity.mActivity.startActivity(intent)
            else:
                self.info_label.text = "[color=#00ff00]Доступ есть[/color]"

# --- ЭКРАН 2: СПИСОК КРИПТЫ (Высота строки 180) ---
class CryptoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=5)
        
        header = BoxLayout(size_hint_y=0.08)
        btn_back = Button(text="< Назад", size_hint_x=0.2)
        btn_back.bind(on_press=self.back)
        header.add_widget(btn_back)
        self.status_label = Label(text="Загрузка...", size_hint_x=0.8)
        header.add_widget(self.status_label)
        self.layout.add_widget(header)

        self.scroll = ScrollView()
        self.crypto_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=2)
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
                    if not history_cache[c_id] or history_cache[c_id][-1] != price:
                        history_cache[c_id].append(price)
                    if len(history_cache[c_id]) > 30: history_cache[c_id].pop(0)
                    
                    self.all_crypto.append({
                        "id": c_id, "name": item['name'], "symbol": item['symbol'].upper(),
                        "price": price, "change": round(item.get("price_change_percentage_24h") or 0, 2),
                        "cap": item['market_cap'], "vol": item['total_volume']
                    })
                Clock.schedule_once(lambda dt: self.update_ui())
        except: pass

    def update_ui(self):
        self.crypto_list.clear_widgets()
        self.status_label.text = "Криптовалюты Live"
        for c in self.all_crypto:
            color = "#00ff00" if c['change'] >= 0 else "#ff0000"
            # Высота строки 180, на всю ширину
            btn = Button(
                text=f"[b]{c['symbol']}[/b] | {c['name']}\n[size=40sp]{c['price']} $[/size]\n[color={color}]Изменение: {c['change']}%[/color]",
                markup=True, size_hint_y=None, height=180, background_color=(0.12, 0.12, 0.12, 1)
            )
            btn.bind(on_release=lambda x, d=c: App.get_running_app().open_details(d))
            self.crypto_list.add_widget(btn)

    def back(self, instance): self.manager.current = 'menu'

# --- ЭКРАН 3: ДЕТАЛИ (График с ценами в точках) ---
class DetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        btn_back = Button(text="< Назад к списку", size_hint_y=0.08)
        btn_back.bind(on_press=self.back)
        self.layout.add_widget(btn_back)

        self.info_box = Label(text="", font_size='18sp', size_hint_y=0.25, markup=True, halign='left')
        self.info_box.bind(size=self.info_box.setter('text_size'))
        self.layout.add_widget(self.info_box)

        # Контейнер для графика и меток цен
        self.chart_container = BoxLayout(orientation='vertical', size_hint_y=0.67)
        self.chart_area = BoxLayout() # Тут рисуем линию
        self.chart_container.add_widget(self.chart_area)
        self.layout.add_widget(self.chart_container)

        self.add_widget(self.layout)
        self.current_coin = None

    def load_data(self, coin):
        self.current_coin = coin
        cap_m = round(coin['cap'] / 1_000_000_000, 2)
        self.info_box.text = (
            f"[b][size=24sp]{coin['name']} ({coin['symbol']})[/size][/b]\n"
            f"Текущая цена: [color=#00ffff]{coin['price']} $[/color]\n"
            f"Капитализация: {cap_m} млрд. $\n"
            f"Объем торгов (24ч): {coin['vol']} $"
        )
        Clock.schedule_once(lambda dt: self.draw_vector(), 0.1)

    def draw_vector(self):
        self.chart_area.canvas.after.clear()
        # Удаляем старые метки цен (лейблы)
        for child in self.chart_area.children[:]:
            self.chart_area.remove_widget(child)

        prices = history_cache.get(self.current_coin['id'], [])
        if len(prices) < 2: return

        with self.chart_area.canvas.after:
            Color(0, 0.8, 1, 1) # Голубой вектор
            w, h = self.chart_area.width, self.chart_area.height
            x0, y0 = self.chart_area.x, self.chart_area.y
            
            p_min, p_max = min(prices), max(prices)
            p_range = (p_max - p_min) if p_max != p_min else 1
            
            line_pts = []
            for i, p in enumerate(prices):
                cur_x = x0 + (i / (len(prices)-1)) * w
                cur_y = y0 + ((p - p_min) / p_range) * h
                line_pts.extend([cur_x, cur_y])
                
                # Рисуем точку
                Color(1, 1, 1, 1)
                Ellipse(pos=(cur_x-4, cur_y-4), size=(8, 8))
                
                # Добавляем текст цены над точкой (каждую 2-ю точку для чистоты, если их много)
                if i % 1 == 0 or i == len(prices)-1:
                    price_label = Label(
                        text=f"{p}$", pos=(cur_x - 40, cur_y + 10),
                        size_hint=(None, None), size=(80, 20), font_size='10sp'
                    )
                    self.chart_area.add_widget(price_label)
            
            Color(0, 0.8, 1, 1)
            Line(points=line_pts, width=2)

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
    

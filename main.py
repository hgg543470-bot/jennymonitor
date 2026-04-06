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
import os

# Глобальные данные
history_cache = {}
favorites = set() # Множество ID избранных монет
log_path = "" # Путь к папке логов

# --- ЭКРАН 1: ГЛАВНОЕ МЕНЮ ---
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical', padding=20)
        
        self.info_label = Label(text="JennyMonitor v0.6", size_hint_y=0.1, markup=True)
        main_layout.add_widget(self.info_label)

        anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        btns_grid = BoxLayout(orientation='vertical', spacing=15, size_hint=(None, None))
        btns_grid.bind(minimum_height=btns_grid.setter('height'), minimum_width=btns_grid.setter('width'))

        # Кнопки 200x200
        for text, screen, color in [("КРИПТА", 'crypto', (0.6, 0.2, 1, 1)), 
                                    ("БИРЖА", 'menu', (0.2, 0.6, 1, 1)), 
                                    ("ФАЙЛЫ", 'files', (0.5, 0.5, 0.5, 1))]:
            btn = Button(text=text, size_hint=(None, None), size=(200, 200), background_color=color)
            if screen != 'menu':
                btn.bind(on_press=lambda x, s=screen: self.change_screen(s))
            btns_grid.add_widget(btn)
        
        anchor.add_widget(btns_grid)
        main_layout.add_widget(anchor)
        self.add_widget(main_layout)

    def change_screen(self, name):
        self.manager.current = name

# --- ЭКРАН ФАЙЛОВ / ПРОВОДНИК ---
class FileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        btn_back = Button(text="< Назад", size_hint_y=0.1)
        btn_back.bind(on_press=self.back)
        layout.add_widget(btn_back)

        self.path_label = Label(text="Папка для логов не выбрана", size_hint_y=0.2)
        layout.add_widget(self.path_label)

        btn_select = Button(text="Выбрать папку для логов", size_hint_y=0.2)
        btn_select.bind(on_press=self.select_folder)
        layout.add_widget(btn_select)
        
        layout.add_widget(Label(size_hint_y=0.5))
        self.add_widget(layout)

    def select_folder(self, instance):
        if platform == 'android':
            # В следующей итерации прикрутим jnius проводник, пока ставим дефолт во внутреннюю память
            from jnius import autoclass
            Env = autoclass('android.os.Environment')
            path = Env.getExternalStorageDirectory().getAbsolutePath() + "/JennyLogs"
            if not os.path.exists(path): os.makedirs(path)
            global log_path
            log_path = path
            self.path_label.text = f"Логи пишутся в:\n{path}"
        else:
            self.path_label.text = "На ПК логи в папке скрипта"

    def back(self, instance): self.manager.current = 'menu'

# --- ЭКРАН СПИСКА (Текст 120 в высоту) ---
class CryptoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        
        header = BoxLayout(size_hint_y=0.08)
        btn_back = Button(text="<", size_hint_x=0.2); btn_back.bind(on_press=self.back)
        header.add_widget(btn_back)
        self.status = Label(text="Обновление...", size_hint_x=0.8); header.add_widget(self.status)
        self.layout.add_widget(header)

        self.scroll = ScrollView()
        self.list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.list.bind(minimum_height=self.list.setter('height'))
        self.scroll.add_widget(self.list)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

        Clock.schedule_interval(lambda dt: self.refresh(), 30)
        self.refresh()

    def refresh(self):
        threading.Thread(target=self.fetch).start()

    def fetch(self):
        try:
            url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=50"
            data = requests.get(url).json()
            Clock.schedule_once(lambda dt: self.update_ui(data))
            # Логирование избранного
            if log_path:
                for item in data:
                    if item['id'] in favorites:
                        f_path = f"{log_path}/{item['id']}.txt"
                        with open(f_path, "a") as f:
                            f.write(f"{item['current_price']}\n")
        except: pass

    def update_ui(self, data):
        self.list.clear_widgets()
        for c in data:
            c_id = c['id']
            # Сохраняем в историю
            if c_id not in history_cache: history_cache[c_id] = []
            history_cache[c_id].append(c['current_price'])
            if len(history_cache[c_id]) > 30: history_cache[c_id].pop(0)

            # Карточка 180 высотой, текст 120
            row = BoxLayout(size_hint_y=None, height=180)
            
            star = "⭐" if c_id in favorites else "☆"
            btn_fav = Button(text=star, size_hint_x=0.2, font_size='40sp')
            btn_fav.bind(on_press=lambda x, i=c_id: self.toggle_fav(i))
            
            btn_main = Button(
                text=f"[b]{c['symbol'].upper()}[/b]  [size=120sp]{c['current_price']}$[/size]",
                markup=True, size_hint_x=0.8, halign='left', background_color=(0.1, 0.1, 0.1, 1)
            )
            btn_main.bind(on_release=lambda x, d=c: App.get_running_app().open_details(d))
            
            row.add_widget(btn_fav)
            row.add_widget(btn_main)
            self.list.add_widget(row)

    def toggle_fav(self, c_id):
        if c_id in favorites: favorites.remove(c_id)
        else: favorites.add(c_id)
        self.refresh()

    def back(self, instance): self.manager.current = 'menu'

# --- ЭКРАН ДЕТАЛЕЙ (Умный график) ---
class DetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10)
        btn_back = Button(text="< Назад", size_hint_y=0.1); btn_back.bind(on_press=self.back)
        self.layout.add_widget(btn_back)

        self.head = Label(text="", size_hint_y=0.2, markup=True, font_size='24sp')
        self.layout.add_widget(self.head)

        self.chart = BoxLayout(size_hint_y=0.7)
        self.layout.add_widget(self.chart)
        self.add_widget(self.layout)

    def load_data(self, coin):
        self.current_id = coin['id']
        self.head.text = f"{coin['name']}\n[color=#00ffff]{coin['current_price']}$[/color]"
        Clock.schedule_once(lambda dt: self.draw(), 0.1)

    def draw(self):
        self.chart.canvas.after.clear()
        for child in self.chart.children[:]: self.chart.remove_widget(child)
        
        prices = history_cache.get(self.current_id, [])
        if len(prices) < 2: return

        with self.chart.canvas.after:
            Color(0, 0.8, 1, 1)
            w, h = self.chart.width, self.chart.height
            x0, y0 = self.chart.x, self.chart.y
            p_min, p_max = min(prices), max(prices)
            p_range = (p_max - p_min) if p_max != p_min else 1
            
            pts = []
            for i, p in enumerate(prices):
                cx = x0 + (i/(len(prices)-1))*w
                cy = y0 + ((p-p_min)/p_range)*h
                pts.extend([cx, cy])
                
                # Точка и цена рядом
                Color(1, 1, 1, 1)
                Ellipse(pos=(cx-5, cy-5), size=(10, 10))
                # Сдвигаем текст цены, чтобы не накладывался
                lbl = Label(text=f"{p}", pos=(cx - 20, cy + 15), size_hint=(None, None), size=(100, 30), font_size='12sp')
                self.chart.add_widget(lbl)
                Color(0, 0.8, 1, 1)
            Line(points=pts, width=3)

    def back(self, instance): self.manager.current = 'crypto'

class JennyMonitorApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(MenuScreen(name='menu'))
        self.sm.add_widget(CryptoScreen(name='crypto'))
        self.sm.add_widget(DetailScreen(name='detail'))
        self.sm.add_widget(FileScreen(name='files'))
        return self.sm

    def open_details(self, data):
        sc = self.sm.get_screen('detail'); sc.load_data(data)
        self.sm.current = 'detail'

if __name__ == '__main__':
    JennyMonitorApp().run()
            

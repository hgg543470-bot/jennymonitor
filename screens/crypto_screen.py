from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.app import App
import requests
import threading
# Импортируем наш общий кэш
from utils.globals import history_cache

class CryptoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=5)
        
        # Шапка
        header = BoxLayout(size_hint_y=0.08)
        btn_back = Button(text="< Назад", size_hint_x=0.2)
        btn_back.bind(on_press=self.back)
        header.add_widget(btn_back)
        
        self.status_label = Label(text="Загрузка...", size_hint_x=0.8)
        header.add_widget(self.status_label)
        self.layout.add_widget(header)

        # Список с прокруткой
        self.scroll = ScrollView()
        self.crypto_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=2)
        self.crypto_list.bind(minimum_height=self.crypto_list.setter('height'))
        self.scroll.add_widget(self.crypto_list)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

        self.all_crypto = []
        self.refresh_data()
        # Обновление каждые 30 секунд
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
                    
                    # Работа с историей цен для графиков
                    if c_id not in history_cache: 
                        history_cache[c_id] = []
                    if not history_cache[c_id] or history_cache[c_id][-1] != price:
                        history_cache[c_id].append(price)
                    if len(history_cache[c_id]) > 30: 
                        history_cache[c_id].pop(0)
                    
                    self.all_crypto.append({
                        "id": c_id, "name": item['name'], "symbol": item['symbol'].upper(),
                        "price": price, "change": round(item.get("price_change_percentage_24h") or 0, 2),
                        "cap": item['market_cap'], "vol": item['total_volume']
                    })
                Clock.schedule_once(lambda dt: self.update_ui())
        except Exception as e:
            print(f"Ошибка API: {e}")

    def update_ui(self):
        self.crypto_list.clear_widgets()
        self.status_label.text = "Криптовалюты Live"
        for c in self.all_crypto:
            color = "#00ff00" if c['change'] >= 0 else "#ff0000"
            # Те самые кнопки высотой 180
            btn = Button(
                text=f"[b]{c['symbol']}[/b] | {c['name']}\n[size=40sp]{c['price']} $[/size]\n[color={color}]Изменение: {c['change']}%[/color]",
                markup=True, size_hint_y=None, height=180, background_color=(0.12, 0.12, 0.12, 1)
            )
            btn.bind(on_release=lambda x, d=c: App.get_running_app().open_details(d))
            self.crypto_list.add_widget(btn)

    def back(self, instance): 
        self.manager.current = 'menu'
          

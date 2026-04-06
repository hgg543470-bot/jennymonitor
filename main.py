from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.utils import platform
import requests
import threading

# --- ЭКРАН 1: ГЛАВНОЕ МЕНЮ ---
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        
        self.info_label = Label(text="JennyMonitor v0.3\n[color=#00ff00]API Подключено[/color]", halign='center', markup=True, font_size='20sp')
        layout.add_widget(self.info_label)

        btn_crypto = Button(text="💎 ЖИВАЯ КРИПТОБИРЖА", size_hint=(1, 0.3), background_color=(0.6, 0.2, 1, 1))
        btn_crypto.bind(on_press=self.go_to_crypto)
        layout.add_widget(btn_crypto)

        # Оставила как заглушку, чтобы не перегружать код
        btn_stocks = Button(text="📊 Биржа компаний (В разработке)", size_hint=(1, 0.3), background_color=(0.2, 0.6, 1, 1))
        layout.add_widget(btn_stocks)

        btn_files = Button(text="🔐 Системный доступ (Файлы)", size_hint=(1, 0.2))
        btn_files.bind(on_press=self.ask_files_access)
        layout.add_widget(btn_files)

        self.add_widget(layout)

    def go_to_crypto(self, instance):
        self.manager.current = 'crypto'

    def ask_files_access(self, instance):
        if platform == 'android':
            from jnius import autoclass
            Environment = autoclass('android.os.Environment')
            if not Environment.isExternalStorageManager():
                self.info_label.text = "Открываю настройки..."
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

# --- ЭКРАН 2: КРИПТОБИРЖА (Реальное API) ---
class CryptoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10)
        
        header = BoxLayout(size_hint_y=0.1)
        btn_back = Button(text="< Назад", size_hint_x=0.2)
        btn_back.bind(on_press=self.back)
        header.add_widget(btn_back)
        
        self.status_label = Label(text="Загрузка данных...", font_size='16sp', size_hint_x=0.8)
        header.add_widget(self.status_label)
        self.layout.add_widget(header)

        self.scroll = ScrollView(size_hint=(1, 0.8))
        self.crypto_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.crypto_list.bind(minimum_height=self.crypto_list.setter('height'))
        self.scroll.add_widget(self.crypto_list)
        self.layout.add_widget(self.scroll)

        self.search_input = TextInput(hint_text="Поиск монеты...", size_hint_y=0.1, multiline=False)
        self.search_input.bind(text=self.on_search)
        self.layout.add_widget(self.search_input)

        self.add_widget(self.layout)
        self.all_crypto = []
        
        # Обновляем сразу и потом каждые 30 секунд
        self.refresh_data()
        Clock.schedule_interval(lambda dt: self.refresh_data(), 30)

    def refresh_data(self):
        self.status_label.text = "Обновление..."
        # Запускаем интернет-запрос в фоне, чтобы интерфейс не зависал
        threading.Thread(target=self.fetch_api).start()

    def fetch_api(self):
        try:
            url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=30&page=1"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.all_crypto = []
                for item in data:
                    # Парсим реальные данные
                    self.all_crypto.append({
                        "id": item.get("id"),
                        "name": item.get("name"),
                        "symbol": str(item.get("symbol")).upper(),
                        "price": item.get("current_price"),
                        "change": round(item.get("price_change_percentage_24h") or 0, 2),
                        "cap": item.get("market_cap"),
                        "high_24h": item.get("high_24h"),
                        "low_24h": item.get("low_24h")
                    })
                # Возвращаемся в главный поток для отрисовки интерфейса
                Clock.schedule_once(lambda dt: self.update_list(self.all_crypto))
                Clock.schedule_once(lambda dt: self.set_status("Крипта (USD) обновлена"))
            else:
                Clock.schedule_once(lambda dt: self.set_status("Ошибка сервера!"))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.set_status("Нет сети!"))

    def set_status(self, text):
        self.status_label.text = text

    def update_list(self, data):
        self.crypto_list.clear_widgets()
        for c in data:
            color = "#00ff00" if c['change'] >= 0 else "#ff0000"
            sign = "+" if c['change'] >= 0 else ""
            
            text_content = (
                f"[b]{c['name']} ({c['symbol']})[/b]\n"
                f"Цена: {c['price']}$ | [color={color}]{sign}{c['change']}%[/color]"
            )
            
            # Теперь каждая строка — это кнопка!
            btn = Button(
                text=text_content, markup=True, size_hint_y=None, height=100,
                halign='left', valign='middle', background_color=(0.15, 0.15, 0.15, 1)
            )
            btn.bind(size=lambda s, w: setattr(s, 'text_size', (w[0]-20, None)))
            # При клике передаем данные этой монеты
            btn.bind(on_release=lambda instance, coin=c: App.get_running_app().open_details(coin))
            
            self.crypto_list.add_widget(btn)

    def on_search(self, instance, value):
        filtered = [c for c in self.all_crypto if value.lower() in c['name'].lower() or value.lower() in c['symbol'].lower()]
        self.update_list(filtered)

    def back(self, instance):
        self.manager.current = 'menu'

# --- ЭКРАН 3: УНИВЕРСАЛЬНАЯ КОМНАТА ПОДРОБНОСТЕЙ ---
class DetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        btn_back = Button(text="< Назад к списку", size_hint=(1, 0.1))
        btn_back.bind(on_press=self.back)
        layout.add_widget(btn_back)

        self.title_label = Label(text="Название", font_size='24sp', bold=True, size_hint=(1, 0.1))
        layout.add_widget(self.title_label)

        self.price_label = Label(text="Цена", font_size='30sp', markup=True, size_hint=(1, 0.2))
        layout.add_widget(self.price_label)

        self.stats_label = Label(text="Статистика", font_size='18sp', halign='left', valign='top', size_hint=(1, 0.6))
        self.stats_label.bind(size=self.stats_label.setter('text_size'))
        layout.add_widget(self.stats_label)

        self.add_widget(layout)

    def load_data(self, coin):
        # Эта функция мгновенно заполняет экран данными выбранной монеты
        self.title_label.text = f"{coin['name']} ({coin['symbol']})"
        
        color = "#00ff00" if coin['change'] >= 0 else "#ff0000"
        sign = "+" if coin['change'] >= 0 else ""
        self.price_label.text = f"{coin['price']} $ \n[color={color}][size=20sp]{sign}{coin['change']}%[/size][/color]"
        
        # Форматируем капитализацию красиво
        cap_billions = round(coin['cap'] / 1_000_000_000, 2)
        
        self.stats_label.text = (
            f"Рыночная капитализация: {cap_billions} млрд $\n\n"
            f"Максимум за 24ч: {coin['high_24h']} $\n"
            f"Минимум за 24ч: {coin['low_24h']} $\n\n"
            f"Доп. информация будет добавляться сюда..."
        )

    def back(self, instance):
        self.manager.current = 'crypto'

# --- ГЛАВНОЕ ПРИЛОЖЕНИЕ ---
class JennyMonitorApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(MenuScreen(name='menu'))
        self.sm.add_widget(CryptoScreen(name='crypto'))
        self.sm.add_widget(DetailScreen(name='detail'))
        return self.sm

    def open_details(self, coin_data):
        # Находим наш универсальный экран
        detail_screen = self.sm.get_screen('detail')
        # Закидываем в него данные
        detail_screen.load_data(coin_data)
        # Переключаемся
        self.sm.current = 'detail'

if __name__ == '__main__':
    JennyMonitorApp().run()
                        


from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Line, Ellipse
from utils.globals import history_cache

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

        # Контейнер для графика
        self.chart_container = BoxLayout(orientation='vertical', size_hint_y=0.67)
        self.chart_area = BoxLayout()
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
        # Рисуем график после того, как UI обновится
        Clock.schedule_once(lambda dt: self.draw_vector(), 0.1)

    def draw_vector(self):
        self.chart_area.canvas.after.clear()
        for child in self.chart_area.children[:]:
            self.chart_area.remove_widget(child)

        prices = history_cache.get(self.current_coin['id'], [])
        if len(prices) < 2: 
            return

        with self.chart_area.canvas.after:
            w, h = self.chart_area.width, self.chart_area.height
            x0, y0 = self.chart_area.x, self.chart_area.y
            
            p_min, p_max = min(prices), max(prices)
            p_range = (p_max - p_min) if p_max != p_min else 1
            
            line_pts = []
            for i, p in enumerate(prices):
                cur_x = x0 + (i / (len(prices)-1)) * w
                cur_y = y0 + ((p - p_min) / p_range) * h
                line_pts.extend([cur_x, cur_y])
                
                # Рисуем точку Ellipse
                Color(1, 1, 1, 1)
                Ellipse(pos=(cur_x-4, cur_y-4), size=(8, 8))
                
                # Метка цены над каждой точкой
                price_label = Label(
                    text=f"{p}$", pos=(cur_x - 40, cur_y + 10),
                    size_hint=(None, None), size=(80, 20), font_size='10sp'
                )
                self.chart_area.add_widget(price_label)
            
            Color(0, 0.8, 1, 1) # Голубой цвет линии
            Line(points=line_pts, width=2)

    def back(self, instance): 
        self.manager.current = 'crypto'
      

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.anchorlayout import AnchorLayout
from kivy.utils import platform

# Подключаем инструменты Android
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android import AndroidService

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical', padding=20)
        
        # Информационная панель
        self.info_label = Label(
            text="JennyMonitor v58\n[color=#aaaaaa]Сервис остановлен[/color]", 
            size_hint_y=0.2, markup=True, font_size='18sp', halign='center'
        )
        main_layout.add_widget(self.info_label)

        anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        btns_grid = BoxLayout(orientation='vertical', spacing=15, size_hint=(None, None))

        # Кнопка КРИПТА
        btn_crypto = Button(
            text="КРИПТА", 
            size_hint=(None, None), size=(250, 80), 
            background_color=(0.6, 0.2, 1, 1)
        )
        btn_crypto.bind(on_press=self.go_to_crypto)
        
        # НОВАЯ КНОПКА: Явный запуск монитора (как запуск игры в эмуляторе)
        btn_start_service = Button(
            text="ЗАПУСТИТЬ МОНИТОР", 
            size_hint=(None, None), size=(250, 80), 
            background_color=(0.2, 0.8, 0.2, 1) # Зеленая кнопка
        )
        btn_start_service.bind(on_press=self.ask_permissions_and_start)

        btns_grid.add_widget(btn_crypto)
        btns_grid.add_widget(btn_start_service)
        
        anchor.add_widget(btns_grid)
        main_layout.add_widget(anchor)
        self.add_widget(main_layout)

    def go_to_crypto(self, instance):
        self.manager.current = 'crypto'

    def ask_permissions_and_start(self, instance):
        if platform == 'android':
            self.info_label.text = "[color=#ffff00]Проверка прав Android 16...[/color]"
            # ВАЖНО: Запрашиваем права явно. И только после ответа системы запускаем код
            request_permissions([Permission.POST_NOTIFICATIONS], self.permissions_callback)
        else:
            self.info_label.text = "[color=#00ff00]ПК-тест: Имитация запуска[/color]"

    def permissions_callback(self, permissions, grants):
        # Если ты нажал "Разрешить" в системном окне (или разрешил ранее)
        if all(grants):
            self.info_label.text = "[color=#00ff00]Права есть! Стартуем сервис...[/color]"
            self.start_monitor_service()
        else:
            self.info_label.text = "[color=#ff0000]Доступ к шторке запрещен![/color]"

    def start_monitor_service(self):
        try:
            # Тот самый запуск, который теперь 100% легален для системы
            service = AndroidService('monitor', 'running')
            service.start('JennyMonitor service started')
            self.info_label.text = "[color=#00ff00]СЕРВИС РАБОТАЕТ![/color]"
        except Exception as e:
            self.info_label.text = f"[color=#ff0000]Ошибка старта: {e}[/color]"
            

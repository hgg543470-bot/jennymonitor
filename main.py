from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import platform

class JennyMonitorLayout(BoxLayout):
    def __init__(self, **kwargs):
        # Настраиваем главный экран: вертикальное расположение, отступы
        super().__init__(orientation='vertical', padding=30, spacing=20)
        
        # Информационное табло
        self.info_label = Label(
            text="JennyMonitor\nСистемы в норме, жду команд!",
            halign='center',
            font_size='20sp'
        )
        self.add_widget(self.info_label)
        
        # Кнопка для базовых прав (Уведомления и Файлы)
        btn_perms = Button(
            text="Запросить базовые права\n(Файлы и Уведомления)",
            size_hint=(1, 0.3),
            background_color=(0.2, 0.8, 0.2, 1) # Зеленоватый цвет
        )
        btn_perms.bind(on_press=self.request_android_permissions)
        self.add_widget(btn_perms)

        # Кнопка для магии Shizuku
        btn_shizuku = Button(
            text="Связаться с Shizuku",
            size_hint=(1, 0.3),
            background_color=(0.2, 0.6, 1, 1) # Синий цвет
        )
        btn_shizuku.bind(on_press=self.request_shizuku)
        self.add_widget(btn_shizuku)

    def request_android_permissions(self, instance):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            # Формируем список того, что нам нужно спросить у Android 14
            perms = [
                Permission.POST_NOTIFICATIONS,     # Для пуш-уведомлений
                Permission.READ_EXTERNAL_STORAGE,  # Чтение файлов
                Permission.WRITE_EXTERNAL_STORAGE  # Запись файлов
            ]
            # Вызываем системное окно Android
            request_permissions(perms, self.permissions_callback)
            self.info_label.text = "Окна запросов отправлены на экран..."
        else:
            self.info_label.text = "Это не Android! Права не нужны."

    def permissions_callback(self, permissions, grants):
        # Эта функция сработает, когда ты нажмешь "Разрешить" или "Отклонить"
        if all(grants):
            self.info_label.text = "УРА!\nФайлы и уведомления разрешены ✅"
        else:
            self.info_label.text = "ОТКАЗ ❌\nНе все права были выданы."

    def request_shizuku(self, instance):
        # Пока ставим заглушку, так как для Shizuku нужен будет код на pyjnius
        self.info_label.text = "Подключаю PyJnius...\n(Скоро здесь будет вызов API Shizuku!)"

class JennyMonitorApp(App):
    def build(self):
        return JennyMonitorLayout()

if __name__ == '__main__':
    JennyMonitorApp().run()
    

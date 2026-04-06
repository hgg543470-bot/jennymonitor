from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import platform

class JennyMonitorLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=30, spacing=20)
        
        self.info_label = Label(
            text="JennyMonitor v0.1\n[color=#ffff00]Жду команд...[/color]",
            halign='center',
            markup=True,
            font_size='20sp'
        )
        self.add_widget(self.info_label)
        
        # Кнопка для уведомлений (вызывает стандартное окошко)
        btn_notify = Button(text="1. Разрешить уведомления", size_hint=(1, 0.3))
        btn_notify.bind(on_press=self.ask_notifications)
        self.add_widget(btn_notify)

        # Кнопка для файлов (перекидывает в настройки)
        btn_files = Button(text="2. Дать доступ ко всем файлам", size_hint=(1, 0.3))
        btn_files.bind(on_press=self.ask_files_access)
        self.add_widget(btn_files)

    def ask_notifications(self, instance):
        if platform == 'android':
            from android.permissions import request_permissions
            # На новых версиях Android уведомления просятся отдельным флагом
            request_permissions(['android.permission.POST_NOTIFICATIONS'])
            self.info_label.text = "Вызвано окно уведомлений!"
        else:
            self.info_label.text = "Это ПК, права не нужны."

    def ask_files_access(self, instance):
        if platform == 'android':
            from jnius import autoclass
            Environment = autoclass('android.os.Environment')
            
            # Проверяем, есть ли у нас уже полный доступ к файлам
            if not Environment.isExternalStorageManager():
                self.info_label.text = "Открываю системные настройки..."
                
                # Формируем системный Intent для открытия нужного экрана
                Intent = autoclass('android.content.Intent')
                Settings = autoclass('android.provider.Settings')
                Uri = autoclass('android.net.Uri')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                
                intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
                uri = Uri.parse("package:" + PythonActivity.mActivity.getPackageName())
                intent.setData(uri)
                # Перекидываем пользователя в настройки
                PythonActivity.mActivity.startActivity(intent)
            else:
                self.info_label.text = "[color=#00ff00]Доступ к файлам УЖЕ ПОЛУЧЕН![/color]"

class JennyMonitorApp(App):
    def build(self):
        return JennyMonitorLayout()

if __name__ == '__main__':
    JennyMonitorApp().run()
    

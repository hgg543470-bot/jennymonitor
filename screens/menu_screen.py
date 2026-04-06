from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.anchorlayout import AnchorLayout
from kivy.utils import platform

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical', padding=20)
        
        self.info_label = Label(
            text="JennyMonitor v0.8", 
            size_hint_y=0.1, markup=True, font_size='18sp'
        )
        main_layout.add_widget(self.info_label)

        anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        btns_grid = BoxLayout(orientation='vertical', spacing=15, size_hint=(None, None))

        # Кнопка КРИПТА
        btn_crypto = Button(text="КРИПТА", size_hint=(None, None), size=(200, 200), background_color=(0.6, 0.2, 1, 1))
        btn_crypto.bind(on_press=self.go_to_crypto)
        
        # Кнопка УВЕДОМЛЕНИЙ
        btn_notif = Button(text="УВЕДОМЛЕНИЯ", size_hint=(None, None), size=(200, 200), background_color=(0.2, 0.8, 0.2, 1))
        btn_notif.bind(on_press=self.ask_notification_access)
        
        # Кнопка ФАЙЛЫ
        btn_files = Button(text="ФАЙЛЫ", size_hint=(None, None), size=(200, 200))
        btn_files.bind(on_press=self.ask_files_access)

        btns_grid.add_widget(btn_crypto)
        btns_grid.add_widget(btn_notif)
        btns_grid.add_widget(btn_files)
        
        anchor.add_widget(btns_grid)
        main_layout.add_widget(anchor)
        main_layout.add_widget(BoxLayout(size_hint_y=0.1))
        self.add_widget(main_layout)

    def go_to_crypto(self, instance):
        self.manager.current = 'crypto'

    def ask_notification_access(self, instance):
        if platform == 'android':
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            Settings = autoclass('android.provider.Settings')
            Uri = autoclass('android.net.Uri')
            Activity = autoclass('org.kivy.android.PythonActivity')
            
            package_name = "org.test.jennymonitor"
            
            try:
                # Пытаемся открыть настройки уведомлений напрямую
                intent = Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS)
                intent.putExtra("android.provider.extra.APP_PACKAGE", package_name)
                Activity.mActivity.startActivity(intent)
            except Exception:
                # Если не вышло — открываем карточку "О приложении"
                intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
                uri = Uri.parse("package:" + package_name)
                intent.setData(uri)
                Activity.mActivity.startActivity(intent)
        else:
            self.info_label.text = "Только для Android"

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
                

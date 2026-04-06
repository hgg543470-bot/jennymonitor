    def ask_notification_access(self, instance):
        if platform == 'android':
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            Settings = autoclass('android.provider.Settings')
            Uri = autoclass('android.net.Uri')
            Activity = autoclass('org.kivy.android.PythonActivity')
            
            package_name = "org.test.jennymonitor" # Твой точный ID пакета
            
            try:
                # План А: Прямой переход в настройки уведомлений
                intent = Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS)
                # На некоторых версиях Android ключи констант лучше писать строками для надежности
                intent.putExtra("android.provider.extra.APP_PACKAGE", package_name)
                Activity.mActivity.startActivity(intent)
            except Exception as e:
                # План Б: Если План А не сработал (App not found), открываем "О приложении"
                # Оттуда пользователь точно сможет зайти в Уведомления
                intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
                uri = Uri.parse("package:" + package_name)
                intent.setData(uri)
                Activity.mActivity.startActivity(intent)
        else:
            self.info_label.text = "Настройки доступны только на Android"
            

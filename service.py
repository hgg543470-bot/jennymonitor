from time import sleep
from jnius import autoclass
from android.runnable import run_on_ui_thread

# Получаем ссылку на сам сервис Kivy
PythonService = autoclass('org.kivy.android.PythonService')
service = PythonService.mService

@run_on_ui_thread
def start_foreground_baklava():
    # Системные инструменты Android
    NotificationBuilder = autoclass('android.app.Notification$Builder')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    NotificationManager = autoclass('android.app.NotificationManager')
    Context = autoclass('android.content.Context')
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    
    # Константы для Android 16
    CHANNEL_ID = "jennymonitor_priority_v1"
    # 4 — это IMPORTANCE_HIGH (Максимальная важность)
    IMPORTANCE = 4 
    # 1073741824 — это FOREGROUND_SERVICE_TYPE_SPECIAL_USE
    SERVICE_TYPE = 1073741824 

    try:
        # 1. Сначала жестко регистрируем канал
        nm = service.getSystemService(Context.NOTIFICATION_SERVICE)
        channel = NotificationChannel(CHANNEL_ID, "JennyMonitor Live", IMPORTANCE)
        nm.createNotificationChannel(channel)

        # 2. Готовим "путь домой" (клик по шторке открывает приложение)
        intent = Intent(service, autoclass('org.kivy.android.PythonActivity'))
        # FLAG_IMMUTABLE (67108864) — обязателен на новых Android
        pending_intent = PendingIntent.getActivity(service, 0, intent, 67108864)

        # 3. Собираем само уведомление
        builder = NotificationBuilder(service, CHANNEL_ID)
        builder.setContentTitle("JennyMonitor")
        builder.setContentText("Мониторинг запущен и работает в фоне")
        builder.setSmallIcon(service.getApplicationInfo().icon)
        builder.setContentIntent(pending_intent)
        builder.setOngoing(True) # Нельзя убрать свайпом

        # 4. ФИНАЛЬНЫЙ ПИНОК
        notification = builder.build()
        service.startForeground(1, notification, SERVICE_TYPE)
        print("JENNY: Шторка должна появиться!")
        
    except Exception as e:
        print(f"JENNY ERROR: {e}")
        # Если SPECIAL_USE не прошел, пробуем без типа (для страховки)
        try:
            service.startForeground(1, builder.build())
        except:
            pass

if __name__ == '__main__':
    # Ждем полсекунды, чтобы сервис успел прогрузиться в системе
    sleep(0.5)
    start_foreground_baklava()
    
    # Бесконечный цикл, чтобы сервис не умер
    while True:
        print("JennyMonitor: Фоновая проверка...")
        sleep(15)
        

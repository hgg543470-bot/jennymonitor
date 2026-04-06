from time import sleep
from jnius import autoclass
from android.runnable import run_on_ui_thread

# Подключаем системные классы Android через jnius
PythonService = autoclass('org.kivy.android.PythonService')
service = PythonService.mService

@run_on_ui_thread
def start_foreground():
    # Нам нужны дополнительные классы для работы с каналами и типами сервиса
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    NotificationBuilder = autoclass('android.app.Notification$Builder')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    NotificationManager = autoclass('android.app.NotificationManager')
    Context = autoclass('android.content.Context')
    
    channel_id = "jennymonitor_id"
    channel_name = "JennyMonitor Service Channel"
    
    # 1. Создаем канал уведомлений (обязательно для Android 8.0+)
    importance = NotificationManager.IMPORTANCE_LOW
    channel = NotificationChannel(channel_id, channel_name, importance)
    notification_manager = service.getSystemService(Context.NOTIFICATION_SERVICE)
    notification_manager.createNotificationChannel(channel)

    # 2. Готовим клик по уведомлению (чтобы открывалось приложение)
    # Используем стандартный путь Kivy Activity
    intent = Intent(service, autoclass('org.kivy.android.PythonActivity'))
    pending_intent = PendingIntent.getActivity(service, 0, intent, PendingIntent.FLAG_IMMUTABLE)

    # 3. Собираем само уведомление
    builder = NotificationBuilder(service, channel_id)
    builder.setContentTitle("JennyMonitor Активен")
    builder.setContentText("Мониторинг запущен и работает в фоне")
    builder.setSmallIcon(service.getApplicationInfo().icon)
    builder.setContentIntent(pending_intent)
    builder.setOngoing(True) # Это сделает уведомление "несмахиваемым"
    
    notification = builder.build()
    
    # 4. Запуск. Константа 1073741824 — это FOREGROUND_SERVICE_TYPE_SPECIAL_USE
    # Это нужно, чтобы Android 14/15/16 не "ругался" на фон.
    try:
        service.startForeground(1, notification, 1073741824)
    except:
        # Если что-то пошло не так, пробуем стандартный запуск
        service.startForeground(1, notification)

if __name__ == '__main__':
    start_foreground()
    while True:
        # Основной цикл сервиса
        print("JennyMonitor: сервис проверяет данные...")
        sleep(10)
        

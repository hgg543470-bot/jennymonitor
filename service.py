from time import sleep
from jnius import autoclass
from android.runnable import run_on_ui_thread

PythonService = autoclass('org.kivy.android.PythonService')
service = PythonService.mService

@run_on_ui_thread
def start_clean_foreground():
    # Системные классы Android
    NotificationBuilder = autoclass('android.app.Notification$Builder')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    NotificationManager = autoclass('android.app.NotificationManager')
    Context = autoclass('android.content.Context')
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    
    # Меняем ID канала, чтобы сбросить старые блокировки системы
    channel_id = 'jenny_v58_clean'
    
    # 1. Создаем канал с высоким приоритетом
    channel = NotificationChannel(channel_id, "JennyMonitor Tracker", 4)
    nm = service.getSystemService(Context.NOTIFICATION_SERVICE)
    nm.createNotificationChannel(channel)

    # 2. Настраиваем клик по шторке (возврат в приложение)
    intent = Intent(service, autoclass('org.kivy.android.PythonActivity'))
    pending_intent = PendingIntent.getActivity(service, 0, intent, 67108864)

    # 3. Собираем чистое и простое уведомление
    builder = NotificationBuilder(service, channel_id)
    builder.setContentTitle("JennyMonitor")
    builder.setContentText("Мониторинг активен")
    
    # Используем 100% рабочую системную иконку Android
    android_id = autoclass('android.R$drawable')
    builder.setSmallIcon(android_id.ic_menu_info_details)
    
    builder.setContentIntent(pending_intent)
    builder.setOngoing(True) # Несмахиваемое

    # 4. ЗАПУСК. Код 1 = FOREGROUND_SERVICE_TYPE_DATA_SYNC
    try:
        service.startForeground(1, builder.build(), 1)
        print("JENNY: Чистая шторка DATA_SYNC запущена!")
    except Exception as e:
        print(f"Error: {e}")
        # Запасной вариант запуска
        service.startForeground(1, builder.build())

if __name__ == '__main__':
    # Небольшая пауза, чтобы UI успел отрисовать зеленую кнопку
    sleep(1)
    start_clean_foreground()
    
    # Жизненный цикл сервиса
    while True:
        print("JennyMonitor: Фоновая работа...")
        sleep(10)
        

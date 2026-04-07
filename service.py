from time import sleep
from jnius import autoclass
from android.runnable import run_on_ui_thread

PythonService = autoclass('org.kivy.android.PythonService')
service = PythonService.mService

@run_on_ui_thread
def start_benji_style_foreground():
    NotificationBuilder = autoclass('android.app.Notification$Builder')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    NotificationManager = autoclass('android.app.NotificationManager')
    Context = autoclass('android.content.Context')
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    
    channel_id = 'jenny_media_v1'
    
    # 1. Создаем канал с высоким приоритетом
    channel = NotificationChannel(channel_id, "JennyMonitor Service", 4)
    nm = service.getSystemService(Context.NOTIFICATION_SERVICE)
    nm.createNotificationChannel(channel)

    # 2. Настраиваем клик по шторке (открывает приложение)
    intent = Intent(service, autoclass('org.kivy.android.PythonActivity'))
    pending_intent = PendingIntent.getActivity(service, 0, intent, 67108864)

    # 3. Собираем визуальную часть (как у Benji-SC)
    builder = NotificationBuilder(service, channel_id)
    builder.setContentTitle("JennyMonitor")
    builder.setContentText("Monitoring is running...")
    builder.setSmallIcon(service.getApplicationInfo().icon)
    builder.setContentIntent(pending_intent)
    builder.setOngoing(True) # Делает несмахиваемым

    # 4. ЗАПУСК. Код 2 = FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK
    try:
        service.startForeground(1, builder.build(), 2)
    except Exception as e:
        print(f"Error: {e}")
        service.startForeground(1, builder.build())

if __name__ == '__main__':
    sleep(1) # Микро-задержка для стабильности запуска
    start_benji_style_foreground()
    
    while True:
        print("Jenny: Работаем в фоне...")
        sleep(10)
        

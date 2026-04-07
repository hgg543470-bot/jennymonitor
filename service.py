from time import sleep
from jnius import autoclass
from android.runnable import run_on_ui_thread

PythonService = autoclass('org.kivy.android.PythonService')
service = PythonService.mService

@run_on_ui_thread
def start_media_session_foreground():
    # Системные инструменты Android для "игры в плеер"
    NotificationBuilder = autoclass('android.app.Notification$Builder')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    NotificationManager = autoclass('android.app.NotificationManager')
    Context = autoclass('android.content.Context')
    MediaSession = autoclass('android.media.session.MediaSession')
    MediaStyle = autoclass('android.app.Notification$MediaStyle')
    
    # Новый ID канала для чистого старта
    channel_id = 'jenny_v56_media'
    
    # 1. Создаем канал с ВЫСОКИМ приоритетом (для шторки)
    # IMPORTANCE_HIGH = 4
    channel = NotificationChannel(channel_id, "JennyMonitor Service", 4)
    nm = service.getSystemService(Context.NOTIFICATION_SERVICE)
    nm.createNotificationChannel(channel)

    # 2. ВОТ ОНО! ВКЛЮЧАЕМ МИКРОФОН!
    # Создаем Медиа-сессию. Система теперь видит, что артист готов петь.
    session = MediaSession(service, "JennyMonitorSession")
    # Активируем её. Всё, фейс-контроль пройден!
    session.setActive(True)
    
    # 3. Собираем уведомление в стиле МЕДИА-ПЛЕЕРА (как у Benji-SC)
    builder = NotificationBuilder(service, channel_id)
    builder.setContentTitle("JennyMonitor")
    # Текст, который увидим в шторке
    builder.setContentText("Monitoring crypto & notifications...")
    builder.setSmallIcon(service.getApplicationInfo().icon)
    
    # Применяем MediaStyle. Это как раз те самые кнопочки плеера.
    style = MediaStyle()
    # Привязываем нашу сессию к уведомлению.
    style.setMediaSession(session.getSessionToken())
    builder.setStyle(style)
    
    builder.setOngoing(True) # Нельзя смахнуть

    # 4. ЗАПУСК. Код 2 = FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK
    try:
        notification = builder.build()
        service.startForeground(1, notification, 2)
        print("JENNY: Шторка запущена через MediaSession!")
    except Exception as e:
        print(f"Error: {e}")
        service.startForeground(1, notification)

if __name__ == '__main__':
    # Микро-задержка для стабильности HyperOS
    sleep(1)
    start_media_session_foreground()
    while True:
        # Здесь будет твоя фоновая логика (проверка цен, Shizuku и т.д.)
        sleep(10)
        

from time import sleep
from jnius import autoclass
from android.runnable import run_on_ui_thread

# Получаем ссылку на сам сервис
PythonService = autoclass('org.kivy.android.PythonService')
service = PythonService.mService

@run_on_ui_thread
def start_foreground():
    # Системные классы
    NotificationBuilder = autoclass('android.app.Notification$Builder')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    NotificationManager = autoclass('android.app.NotificationManager')
    Context = autoclass('android.content.Context')
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    
    # Динамически получаем имя твоего пакета (org.test.jennymonitor)
    package_name = service.getPackageName()
    channel_id = package_name + '.monitor_channel'
    
    # 1. Создаем канал с МАКСИМАЛЬНОЙ важностью
    # IMPORTANCE_HIGH = 4. Это заставит шторку появиться.
    channel = NotificationChannel(channel_id, "JennyMonitor Monitor", 4)
    nm = service.getSystemService(Context.NOTIFICATION_SERVICE)
    nm.createNotificationChannel(channel)

    # 2. Настраиваем клик по уведомлению (чтобы открывалось окно)
    # Используем стандартный Activity класс Kivy
    intent = Intent(service, autoclass('org.kivy.android.PythonActivity'))
    pending_intent = PendingIntent.getActivity(service, 0, intent, PendingIntent.FLAG_IMMUTABLE)

    # 3. Собираем уведомление
    builder = NotificationBuilder(service, channel_id)
    builder.setContentTitle("JennyMonitor")
    builder.setContentText("Мониторинг активен в шторке")
    # Берем иконку самого приложения
    builder.setSmallIcon(service.getApplicationInfo().icon)
    builder.setContentIntent(pending_intent)
    builder.setOngoing(True) # Нельзя смахнуть

    # 4. ЗАПУСК. 
    # Тип SPECIAL_USE (1073741824) обязателен для твоего Android 16!
    try:
        notification = builder.build()
        service.startForeground(1, notification, 1073741824)
    except Exception as e:
        # Если Android 16 капризничает, пробуем без типа
        print(f"Service Error: {e}")
        service.startForeground(1, notification)

if __name__ == '__main__':
    # Даем системе 1 секунду "продышаться" перед запуском уведомления
    sleep(1)
    start_foreground()
    while True:
        # Сервис просто крутится в фоне
        print("JennyMonitor Service is alive...")
        sleep(10)
        

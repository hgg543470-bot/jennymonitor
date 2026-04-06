from time import sleep
from android.runnable import run_on_ui_thread
from jnius import autoclass

# Подключаем системные уведомления Android
PythonService = autoclass('org.kivy.android.PythonService')
service = PythonService.mService

@run_on_ui_thread
def set_foreground():
    # Настройка уведомления для шторки
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    NotificationBuilder = autoclass('android.app.Notification$Builder')
    Context = autoclass('android.content.Context')
    
    # Ссылка на само приложение, чтобы при клике на уведомление оно открывалось
    intent = Intent(service, autoclass('org.test.jennymonitor.ServiceMonitor'))
    pending_intent = PendingIntent.getActivity(service, 0, intent, PendingIntent.FLAG_IMMUTABLE)

    # Собираем уведомление
    builder = NotificationBuilder(service)
    builder.setContentTitle("JennyMonitor Активен")
    builder.setContentText("Мониторинг крипты и уведомлений запущен...")
    builder.setSmallIcon(service.getApplicationInfo().icon)
    builder.setContentIntent(pending_intent)
    
    # ID уведомления (любое число)
    notification = builder.build()
    service.startForeground(1, notification)

if __name__ == '__main__':
    set_foreground()
    while True:
        # Тут будет твой фоновый код (например, проверка цен или новых уведомлений)
        print("JennyMonitor service is running in background...")
        sleep(10) # Спим 10 секунд и по новой

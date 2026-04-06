from time import sleep
from jnius import autoclass
from android.runnable import run_on_ui_thread

# Системные классы
PythonService = autoclass('org.kivy.android.PythonService')
service = PythonService.mService

@run_on_ui_thread
def start_foreground_high_priority():
    NotificationBuilder = autoclass('android.app.Notification$Builder')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    NotificationManager = autoclass('android.app.NotificationManager')
    Context = autoclass('android.content.Context')
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    
    channel_id = 'jennymonitor_vital'
    channel_name = 'JennyMonitor: Основной монитор'
    
    # 1. Создаем канал с ВЫСОКОЙ важностью (чтобы шторка точно была)
    importance = NotificationManager.IMPORTANCE_HIGH
    channel = NotificationChannel(channel_id, channel_name, importance)
    channel.setDescription("Важные уведомления о работе системы")
    
    notification_manager = service.getSystemService(Context.NOTIFICATION_SERVICE)
    notification_manager.createNotificationChannel(channel)

    # 2. Делаем так, чтобы при клике на уведомление открывалось приложение
    # Используем стандартный Activity класс Kivy
    intent = Intent(service, autoclass('org.kivy.android.PythonActivity'))
    pending_intent = PendingIntent.getActivity(service, 0, intent, PendingIntent.FLAG_IMMUTABLE)

    # 3. Собираем уведомление
    builder = NotificationBuilder(service, channel_id)
    builder.setContentTitle("JennyMonitor: РАБОТАЕТ")
    builder.setContentText("Мониторинг активен. Система под контролем.")
    builder.setSmallIcon(service.getApplicationInfo().icon)
    builder.setContentIntent(pending_intent)
    builder.setOngoing(True) # Нельзя смахнуть
    
    # Добавляем приоритет для старых версий Android (на всякий случай)
    builder.setPriority(2) # PRIORITY_MAX

    notification = builder.build()
    
    # 4. Запуск с флагом SPECIAL_USE (1073741824)
    # На Android 16 это критично!
    try:
        service.startForeground(1, notification, 1073741824)
        print("СЕРВИС: Foreground запущен успешно")
    except Exception as e:
        print(f"СЕРВИС: Ошибка запуска: {e}")
        # Пробуем без типа, если система капризничает
        service.startForeground(1, notification)

if __name__ == '__main__':
    start_foreground_high_priority()
    count = 0
    while True:
        count += 1
        print(f"JennyMonitor Service Log: Цикл №{count}")
        sleep(10)
        

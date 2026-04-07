from time import sleep
from jnius import autoclass
from android.runnable import run_on_ui_thread

# Получаем саму суть нашего сервиса
PythonService = autoclass('org.kivy.android.PythonService')
service_context = PythonService.mService

@run_on_ui_thread
def call_java_fast():
    try:
        # Зовем наши "быстрые руки"
        FastForeground = autoclass('org.test.FastForeground')
        FastForeground.start(service_context)
        print("JENNY: Java-шторка мгновенно вызвана!")
    except Exception as e:
        print(f"JENNY ERROR: {e}")

if __name__ == '__main__':
    # Никаких пауз! Сразу стреляем в систему через Java
    call_java_fast()
    
    # А вот тут Питон уже может не спеша делать свою фоновую работу
    while True:
        print("JennyMonitor: Работает фоновый цикл Питона...")
        sleep(10)
        

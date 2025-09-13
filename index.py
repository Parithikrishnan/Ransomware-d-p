import threading
import subprocess

thread1 = threading.Thread(target=subprocess.run, args=(['python', 'config_checker.py'],))
thread2 = threading.Thread(target=subprocess.run, args=(['python', 'extension_checker.py'],))
thread3 = threading.Thread(target=subprocess.run, args=(['python', 'rename_condition.py'],))
thread4 = threading.Thread(target=subprocess.run, args=(['python', 'resources_monitoring.py'],))

thread1.start()
thread2.start()
thread3.start()
thread4.start()

thread1.join()
thread2.join()
thread3.join()
thread4.join()

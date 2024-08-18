import threading

def start_background_task(target, *args):
    threading.Thread(target=target, args=args).start()

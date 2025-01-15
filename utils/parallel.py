import threading
from django.core.cache import cache
from django.http import JsonResponse
import time
from core.defs import *


def check_thread_running(thread, task_id):
    time.sleep(1)
    while (thread.is_alive()):
        time.sleep(0.2)
    cache.set(task_id, TASK_COMPLETED)


def run_in_thread(*args):
    # args 1-task_id, 0-function to run 2,3,...- functions args
    func_to_run = args[0]
    task_id = args[1]
    cache.set(task_id, TASK_RUNNING)
    print(f"run_in_thread {task_id=} {func_to_run.__name__=}")
    thread = threading.Thread(target=func_to_run, args=tuple(args[2:]))
    thread.start()
    tester_thread = threading.Thread(
        target=check_thread_running, args=(thread, task_id,))
    tester_thread.start()

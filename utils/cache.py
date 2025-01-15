import json
from django.core.cache import cache
from django.http import JsonResponse
from core.defs import *


def is_analyze_ready():
    return cache.get(ANALYZE_RESULT_KEY) != "" and cache.get(ANALYZE_RESULT_KEY) != None


def clear_cache_if_needed():
    if is_analyze_ready():
        cache.set(ANALYZE_RESULT_KEY, "")


def on_analyze_done(ai_json):
    print("on_analyze_done", json.dumps(ai_json, indent=4))
    # save the result
    cache.set(ANALYZE_RESULT_KEY, json.dumps(ai_json))


def get_parallel_task_status(request, task_id):
    ret = JsonResponse({'status': cache.get(task_id, TASK_RUNNING)})
    print(f"get_parallel_task_status {task_id=} {ret=}")
    return ret

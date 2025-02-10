from core.defs import *
from dashboard.models import Watcher


def get_task_watchers(user_id):
    return Watcher.objects.filter(
        user_id=user_id, type=TASKS).order_by(NAME)


def get_tasks_summary_card(user_id):
    watchers = get_task_watchers(user_id)
    if len(watchers) == 0:
        return None
    return {"title": "Tasks",
            "title_icon": f"fa-list-check",
            "base_color": 'yellow',
            "items": [{'text_left': "# Tasks", "text_right": len(watchers)}]}


def get_tasks_cards(user_id):
    watchers = get_task_watchers(user_id)
    if not watchers or len(watchers) == 0:
        return []
    cards = [{"title": w.name,
              "title_icon": f"fa-list-check",
              "base_color": 'orange',
              "items": []} for w in watchers]

    return cards

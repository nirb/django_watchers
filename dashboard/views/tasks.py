from core.defs import *
from dashboard.models import Watcher


def get_tasks_cards(user_id):
    watchers = Watcher.objects.filter(user_id=user_id, type=TASKS).order_by(NAME)
    cards = []
    for w in watchers:
        cards.append( {"title": w.name,
            "title_icon": f"fa-list-check",
            "base_color": 'orange',
            "items": [{'text_left': "# Tasks",
                       "text_right": 'xxx',
                       'icon': 'fa-building-columns'},
                      {'text_left': 'task',
                       "text_right":  'yyy', 'icon': 'fa-moon'},
                      ]})
        
    return cards
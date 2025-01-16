from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def menu_view(request):
    context = {
        "menues": [
            {"title": "Show Recent Events",
                "url": "/recent_events/-date", "items": []},
            {"title": "Show Pending Events",
             "url": "/recent_events/date?type=pending", "items": []},
            {"title": "Read", "url": "/", "items": []},
            {"title": "Update", "url": "/", "items": []},
            {"title": "Delete", "url": "/", "items": []},
            {"title": "Export", "url": "/", "items": []},
            {"title": "Import", "url": "/", "items": []},
            {"title": "Print", "url": "/", "items": []},
        ]
    }
    return render(request, 'menues/cards_menu.html', context)

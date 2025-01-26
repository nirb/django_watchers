from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def menu_view(request):
    context = {
        "menues": [
            {"title": "Show Recent Events",
                "url": "/events_cards/-date", "items": []},
            {"title": "Show Pending Events",
             "url": "/events_cards/date?type=notice", "items": []},
            {"title": "Monthly Report", "url": "/monthly_report",
                "items": []},
            {"title": "TBD", "url": "/", "items": []},
        ]
    }
    for menu in context["menues"]:
        menu["background"] = "primary"

    return render(request, 'menues/cards_menu.html', context)

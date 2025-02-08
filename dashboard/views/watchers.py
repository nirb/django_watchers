from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from core.defs import *
from core.watchers_fin import WatchersFin
from core.watchers_info import WatchersInfo
from dashboard.models import Watcher
from utils.cache import clear_cache_if_needed
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from dashboard.forms.watcher_form import WatcherForm2
from core.fin_calcs import get_missing_events
from utils.converters import currency_to_color, currency_to_name, event_type_to_color, int_to_str, json_keys_to_string_values, list_keys_to_string_values
import json
from django.db.models import Q  # Import Q for OR queries
from dashboard.fin.watchers_fin import WatchersFin as wf

watchersInfo = WatchersInfo()
watchersFin = WatchersFin()
wF = wf()


@login_required
def dashboard_view(request):
    clear_cache_if_needed()
    wF.get_statements_values("USD", 12)
    if request.method == "GET":
        watchersFin.calculate_summary(request.user.id)
        context = {"summary_card": get_watchers_summary_card(),
                   "currency_cards": get_currency_cards()}
        return render(request, 'dashboard.html', context)


@login_required
def report(request):
    clear_cache_if_needed()
    if request.method == "GET":
        watchersFin.calculate_summary(request.user.id)
        currrencies_sum = []
        for currency in CURRENCY_TYPES:
            currrencies_sum.append(
                [currency, watchersFin.sum_pef_currency[currency]])
        assets_in_currencies = []
        for currency in CURRENCY_TYPES:
            assets_in_currencies.append(
                [currency, watchersFin.currency_values[currency], watchersFin.currency_distribution[currency]])

        context = {"summary_card": get_watchers_summary_card(),
                   "currency_cards": get_currency_cards(),
                   "currrencies_sum": currrencies_sum,
                   "assets_in_currencies": assets_in_currencies}

        return render(request, 'reports/report_.html', context)


@login_required
def watchers_view(request):
    # show watchers table with currency tabs
    clear_cache_if_needed()
    if request.method == "GET":
        return render(request, 'watchers/watchers.html', watchersInfo.get(request.user.id))


@login_required
def watchers_currency(request, currency):
    # show watchers table with currency tabs (selected currency)
    clear_cache_if_needed()
    if request.method == "GET":
        wi = watchersInfo.get(request.user.id)
        context = {"currency_groups": {
            currency: wi["currency_groups"][currency]}}
        for c in CURRENCY_TYPES:  # add all other currencies
            if c != currency:
                context["currency_groups"][c] = wi["currency_groups"][c]
        return render(request, 'watchers/watchers.html', context)


@login_required
def watcher_view(request, watcher_id):
    context = {"error": f"No Watcher found for watcher_id={watcher_id}"}

    if request.method == "GET":
        watcher = watchersFin.get_watcher(request.user.id, int(watcher_id))
        watcher_info = watchersFin.get_watcher_info(watcher.id)
        if watcher_info:
            watcher_info = json_keys_to_string_values(
                watcher_info, [VALUE, INVESTED, NET_GAIN, COMMITMENT, UNFUNDED, DIST_ITD, DIST_YTD], watcher.currency)
            watcher_info[EVENTS] = list_keys_to_string_values(
                watcher_info[EVENTS], [VALUE], watcher.currency)
            event_cards = [{"type": event.type, "url": f"/events/edit/{event.id}",
                            "background": event_type_to_color(event.type),
                            "items": [event.date,  int_to_str(event.value, event.parent.currency)]}
                           for event in watcher_info[EVENTS]]
            context = {"name": watcher.name,
                       "watcher_info": watcher_info,
                       "watcher": watcher,
                       "event_cards": event_cards,
                       "missing_events": get_missing_events(watcher.type, watcher_info[EVENTS])}
            watchersInfo.update_watcher_data_over_time(watcher)
            # print("watcher_view", json.dumps(context, indent=2))
        else:
            context = {"name": watcher.name,
                       "missing_events": "No Events for this watcher"}

    return render(request, 'watchers/watcher.html', context)


@login_required
def create_watcher(request):
    if request.method == "POST":
        new_watcher_name = request.POST.get("new_watcher_name").strip()

        if new_watcher_name:
            # Check if the watcher already exists
            if Watcher.objects.filter(name=new_watcher_name).exists():
                messages.error(
                    request, f"Watcher '{new_watcher_name}' already exists!")
            else:
                # Create the watcher
                Watcher.objects.create(name=new_watcher_name)
                messages.success(
                    request, f"Watcher '{new_watcher_name}' created successfully!")
                # Redirect to the create_event page
                return redirect('/create_event/')
        else:
            messages.error(request, "Watcher name cannot be empty!")
    # Redirect to the same page if validation fails
    return redirect("/create_event/")


@login_required
def watcher_form(request):

    if request.method == "POST":
        form = WatcherForm2(request.POST, user=request.user)
        if form.is_valid():
            watcher = form.save(commit=False)
            watcher.user = request.user  # Assign the current user
            watcher.save()
            messages.success(request, "Watcher created successfully!")
            # Replace with your watchers list URL name
            watchersInfo.reset()
            return redirect("/watchers")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = WatcherForm2(user=request.user)

    return render(request, "watchers/create_watcher.html", {"form": form})


def select_watcher(request):
    if request.method == "POST":
        existing_watcher_name = request.POST.get("existing_watcher")
        # Check if the watcher exists
        watcher = Watcher.objects.get(name=existing_watcher_name)
        print(f"select_watcher {existing_watcher_name=} {watcher=}")
        if watcher:
            # Redirect to the event creation page with the selected watcher
            return redirect(f"/create_event/?watcher_name={existing_watcher_name}")
        else:
            messages.error(request, "Selected watcher does not exist!")
    # Redirect back if no watcher is selected
    return redirect("/create_event/")


def delete_watcher(request, watcher_id):
    # Ensure the user is authorized to delete (add your own authorization check if needed)
    watcher = get_object_or_404(Watcher, id=watcher_id)

    if request.method == 'POST':
        # Explicitly delete all events associated with this watcher
        watcher.events.all().delete()  # Explicitly delete all related events

        # Now delete the watcher itself
        watcher.delete()

        # Show success message
        messages.success(
            request, 'Watcher and all associated events deleted successfully.')

        watchersInfo.reset()
    return redirect('/watchers/')


def search_watchers(request, search_string=""):
    if request.method == 'GET':
        ret = []
        print("search_watchers", search_string)

        if len(search_string) > 0:
            watchers = watchersFin.get_watchers(request.user.id).order_by(NAME)
            for w in watchers:
                if search_string == "__all__!" or search_string.lower() in w.name.lower() or search_string.lower() in w.currency.lower() or search_string.lower() in w.advisor.name.lower():
                    watcherInfo = watchersFin.get_watcher_info(w.id)
                    ret.append({"name": w.name, "id": w.id,
                               "currency": w.currency,
                                "value": int_to_str(watcherInfo[VALUE], w.currency) if watcherInfo else 0,
                                "advisor": w.advisor.name})
            # print("watchers", len(watchers))
        return JsonResponse(ret, safe=False)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def get_watchers_summary_card():
    items = []
    for currency in CURRENCY_TYPES:
        items.append({'text_left': currency,
                      'text_right': watchersFin.sum_pef_currency[currency]})
    return {
        'title': 'Total Assets In Currencies', 'title_icon': 'fa-building-columns',
        'base_color': "black", "items": items}


def get_currency_cards():
    currency_cards = []
    for currency in CURRENCY_TYPES:
        currency_card = get_currency_card(currency)
        currency_cards.append(currency_card)
    return currency_cards


def get_currency_card(currency):
    return {"title": currency,
            "title_icon": f"fa-{currency_to_name(currency)}-sign",
            "base_color": currency_to_color(currency),
            "items": [{'text_left': "Today Value",
                       "text_right": watchersFin.currency_values[currency],
                       'icon': 'fa-building-columns'},
                      {'text_left': 'Unfunded',
                       "text_right":  watchersFin.currency_unfunded[currency], 'icon': 'fa-moon'},
                      {'text_left': 'Distribution',
                       "text_right":  watchersFin.currency_distribution[currency], 'icon': 'fa-moon'}
                      ]}


def watchers_plots_data(request):
    currency = request.GET.get('currency', None)
    event_type = request.GET.get('events_type', None)
    ret = watchersFin.get_watchers_sum_currency_per_month(
        request.user.id, currency, event_type)

    return JsonResponse(ret, safe=False)


def watcher_plots_data(request):
    watcher_id = request.GET.get('watcher_id', None)
    event_type = request.GET.get('events_type', None)
    ret = watchersFin.get_watcher_sum_per_month(
        request.user.id, watcher_id, event_type)

    return JsonResponse(ret, safe=False)

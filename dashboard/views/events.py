import json
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from core.watchers_fin import WatchersFin
from core.watchers_info import WatchersInfo
from dashboard.forms.event_form import EventForm, EventForm2
from dashboard.forms.watcher_form import WatcherForm
from dashboard.models import Event, Watcher
from utils.cache import clear_cache_if_needed, is_analyze_ready
from utils.converters import date_str_to_datetime, event_type_to_color, int_to_str
import pandas as pd
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from core.defs import *
from django.contrib import messages
from django.core.cache import cache
from django.db.models import F

watchersInfo = WatchersInfo()
watchersFin = WatchersFin()


class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'events.html'  # Template to render
    context_object_name = 'events'  # Context variable for the list of events

    def get_queryset(self):
        clear_cache_if_needed()
        # Annotate the queryset with the currency
        watcher_id = self.kwargs.get('watcher_id')
        events = Event.objects.filter(parent__id=watcher_id).annotate(
            watcher_currency=F('parent__currency')).order_by('-date')

        # Add the symbol mapping to each event
        for event in events:
            event.currency_symbol = CURRENCY_SYMBOLS[CURRENCY_TYPES.index(
                event.watcher_currency)]
            event.int_value = int_to_str(event.value)

        return filter(lambda event: event.parent.user == self.request.user, events)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)

        # Add the watcher to the context for additional information
        watcher_id = self.kwargs.get('watcher_id')
        context['watcher'] = Watcher.objects.get(id=watcher_id)

        return context


@login_required
def create_event(request):
    json_str = cache.get(ANALYZE_RESULT_KEY)
    print('create_event', json_str)

    if not is_analyze_ready():
        return redirect('/')
    watcher_name = request.GET.get('watcher_name', None)
    print('create_event', watcher_name)

    str_keys = {"period_date": "Date"}
    int_keys = {"initial_investment": "Initial Investment",
                "current_value": "Value"}
    org_event_date = json.loads(json_str)
    if watcher_name is None:
        watcher_name = org_event_date["watcher_name"]
    event_data = {}
    for key, value in org_event_date.items():
        if key in int_keys.keys():
            event_data[int_keys[key]] = int_to_str(
                value, org_event_date["currency"])
        elif key in str_keys.keys():
            event_data[str_keys[key]] = value

    context = {"event_data": event_data}

    watcher_form = WatcherForm(
        initial={'name': watcher_name, "currency": org_event_date["currency"], "type": "Investment"})

    doc_type = org_event_date["doc_type"].title()
    if doc_type == "Capital Call":  # TODO - Add more doc types
        doc_type = WIRE_RECEIPT_EVENT_TYPE
    event_form = EventForm(
        initial={'description': "AI Added", "type": doc_type})

    watcher = Watcher.objects.filter(
        user_id=request.user.id, name=watcher_name)
    # try to find watcher by name (not exact match), if more the 4 words in the name, use this watcher
    if len(watcher) == 0:
        watchers = Watcher.objects.filter(user_id=request.user.id)
        words = watcher_name.split()
        for w in watchers:
            words_counter = 0
            for word in words:
                if word in w.name:
                    words_counter += 1
            if words_counter > 3:
                watcher = [w]
                break

    context["watcher_found"] = False if len(watcher) == 0 else True
    if context["watcher_found"]:
        context["watcher_name"] = watcher[0].name

        context["watcher_form"] = watcher_form
    context["event_form"] = event_form

    watcher_names = []
    if not context["watcher_found"]:
        watchers = Watcher.objects.filter(user_id=request.user.id)
        watcher_names = [watcher.name for watcher in watchers]
        print(f"create_event {watcher_names=}")

    context["watcher_names"] = watcher_names if len(
        watcher_names) > 0 else None

    if request.method == 'POST':
        if 'new_watcher_submit' in request.POST:
            # Handle Watcher creation
            watcher_form = WatcherForm(request.POST)
            if watcher_form.is_valid():
                watcher_form = watcher_form.save(commit=False)
                watcher_form.active = True  # Automatically set as active
                watcher_form.user = request.user  # Set the current user
                watcher_form.save()
                # Reload the page with the new watcher available
                watchersInfo.reset()
                return redirect('/create_event/')
        else:
            eventForm = EventForm(request.POST)
            if eventForm.is_valid():
                eventForm = eventForm.save(commit=False)
                eventForm.value = org_event_date["current_value"]
                eventForm.parent = watcher[0]
                eventForm.date = date_str_to_datetime(
                    org_event_date["period_date"])
                # eventForm.type = org_event_date["doc_type"].capitalize()
                if Event.objects.filter(date=eventForm.date, value=eventForm.value,  parent=eventForm.parent).exists():
                    messages.error(
                        request, f"Duplicate event with value:{eventForm.value} already exist")
                else:
                    eventForm.save()  # Save the event to the database
                    msg = f"Event '{eventForm.type}' value:{event_data['Value']} added successfully!"
                    print("adding", msg)
                    messages.success(request, msg)
                    clear_cache_if_needed()
                watchersInfo.reset()
                return redirect('/ai/')

    return render(request, "events/create_event.html", context)


@ login_required
def create_event_form(request, watcher_name=None):
    if request.method == 'POST':
        form = EventForm2(request.POST)
        if form.is_valid():
            form.save()
            msg = f"Event '{form.cleaned_data['type']}' added successfully!"
            messages.success(request, msg)
            watchersInfo.reset()
            if watcher_name:
                watcher = watchersFin.get_watcher(
                    request.user.id, watcher_name)
                if watcher:
                    return redirect(f'/watcher/{watcher.id}/')

            return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        if watcher_name:
            watcher = get_object_or_404(Watcher, name=watcher_name)
            form = EventForm2(initial={'parent': watcher})
        else:
            form = EventForm2()

    print(f"create_event_form {watcher_name=}")
    return render(request, 'events/event_form.html', {'form': form, "cancel_url": request.META.get('HTTP_REFERER', '/')})


def events_table_view(request, watcher_id):
    # Query all events ordered by date
    watcher = get_object_or_404(Watcher, id=watcher_id)

    events = Event.objects.filter(parent=watcher, type='Statement').order_by(
        "date").values("date", "value")

    # Convert to a DataFrame for easier manipulation
    data = pd.DataFrame(list(events))
    data['date'] = pd.to_datetime(data['date'])  # Ensure date is datetime
    data['year'] = data['date'].dt.year
    data['month'] = data['date'].dt.month

    # Pivot table: index=years, columns=months, values=event values
    pivot = data.pivot_table(
        index='year', columns='month', values='value', aggfunc='first')

    # Fill missing months with previous month's value
    pivot = pivot.ffill(axis=1)

    # Calculate YTD profit as a cumulative sum along the columns
    pivot['YTD'] = pivot.sum(axis=1)

    # Convert to dictionary for rendering
    pivot_dict = pivot.fillna(0).to_dict(orient="index")

    return render(request, 'events/events_table.html', {'pivot_dict': pivot_dict,
                                                        "months_range": range(1, 13),
                                                        "watcher_name": watcher.name,
                                                        "currency": watcher.currency})


def edit_event(request, event_id):
    if request.method == 'GET':
        print("edit", event_id)
        event = Event.objects.get(id=event_id)
        if event:
            watcher = get_object_or_404(Watcher, name=event.parent.name)
            form = EventForm2(initial={'parent': watcher,
                                       'date': event.date,
                                       'description': event.description,
                                       'type': event.type,
                                       'value': event.value,
                                       })
            return render(request, 'events/event_form.html',
                          {'form': form, "edit": True, "cancel_url": f"/watcher/{watcher.id}"})
    else:
        event = get_object_or_404(Event, id=event_id)
        form = EventForm2(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully!")
            watchersInfo.reset()
            return redirect("/watcher/" + str(event.parent.id) + "/")


def events_cards(request, order_by='-date'):
    query_params = request.GET.dict()
    print(f"events_cards query_params: {query_params}")
    events = Event.objects.filter(
        parent__user=request.user)

    if "type" in query_params:
        events = events.filter(type__icontains=query_params["type"])

    events = events.order_by(order_by)[:50]

    menues = [{"title": event.parent.name, "url": f"/watcher/{event.parent.id}",
               "background": event_type_to_color(event.type),
               "items": [event.date, event.type, int_to_str(event.value, event.parent.currency)]}
              for event in events]
    return render(request, 'menues/cards_menu.html', {"menues": menues})


def delete_event(request, event_id):
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        # Assuming the Event model has a foreign key to Watcher
        # watcher = event.parent
        event.delete()
        messages.success(request, 'Event deleted successfully.')
        watchersInfo.reset()
        return redirect(request.META.get('HTTP_REFERER', '/'))

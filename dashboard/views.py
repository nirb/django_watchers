from django.shortcuts import redirect, render
from django.db.models import F
from core.defs import *
from dashboard.forms.watcher_form import WatcherForm


CURRENCY_SYMBOLS = {
    "USD": "$",
    "NIS": "₪",
    "EUR": "€"
}


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and not request.path.startswith('/admin/'):
            return redirect('/login/')
        return self.get_response(request)


def create_watcher_view(request):
    if request.method == 'POST':
        form = WatcherForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect to a list or detail page
            return redirect('/create_event/')
    else:
        form = WatcherForm()

    return render(request, 'create_watcher.html', {'form': form})

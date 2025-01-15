from django.urls import path

from utils.cache import get_parallel_task_status

from . import views
from django.contrib.auth.views import LoginView, LogoutView
from .views.events import *
from .views.watchers import *
from .views.menu import *

from .views.ai import ai_view

urlpatterns = [
    # watchers
    path('', dashboard_view, name='dashboard'),
    path('db', dashboard_view_old, name='dashboard'),
    path('watchers/', watchers_view, name='watchers'),
    path('watchers/<str:currency>/', watchers_currency, name='watchers'),
    path('watcher/<int:watcher_id>/', watcher_view, name='watchers'),
    path("create_watcher/", create_watcher, name="create_watcher"),
    path("create_watcher_form/", watcher_form, name="create_watcher_form"),
    path("select_watcher/", select_watcher, name="select_watcher"),
    path('watchers/delete/<int:watcher_id>/',
         delete_watcher, name='delete_watcher'),
    path('search_watchers/<str:search_string>/',
         search_watchers, name='get_watchers_list'),

    # events
    path('events/<str:watcher_id>/', EventListView.as_view(), name='event-list'),
    path('events_table/<str:watcher_id>/',
         events_table_view, name='events-table'),
    path('create_event/<str:watcher_name>', create_event, name='creat_event'),
    path('create_event/', create_event, name='creat_event'),
    path("create_event_form/",
         create_event_form, name="create_event_form"),
    path("create_event_form/<str:watcher_name>/",
         create_event_form, name="create_event_form"),
    path('events/delete/<int:event_id>/',
         delete_event, name='delete_event'),
    path('events/edit/<int:event_id>/',
         edit_event, name='delete_event'),
    path('recent_events/<str:order_by>', events_cards, name='recent_events'),


    # actions
    path('menues/', menu_view, name='actions'),

    # AI
    path('ai/', ai_view, name='ai'),
    path('get_parallel_task_status/<str:task_id>/',
         get_parallel_task_status, name='get_parallel_task_status'),

    # login and out
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]

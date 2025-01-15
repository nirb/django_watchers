from django.contrib import admin
from .models import Advisor, Watcher, Event


@admin.register(Advisor)
class AdvisorAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'mail')
    search_fields = ('name', 'mail')


@admin.register(Watcher)
class WatcherAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'advisor', 'currency', 'type', 'user')
    list_filter = ('active', 'currency', 'type')
    search_fields = ('name',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('description', 'parent', 'type', 'value')
    list_filter = ('type',)
    search_fields = ('description',)

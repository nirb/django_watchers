from django.db import models
from django.contrib.auth.models import User  # For linking Watcher to a user
# Import the function for the current time
from django.utils.timezone import now

from core.defs import INVESTMENT_WATCHER_TYPES, STATEMENT_EVENT_TYPE


class Advisor(models.Model):
    name = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=20)
    mail = models.CharField(max_length=48)

    def __str__(self):
        return self.name


class Watcher(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('NIS', 'New Israeli Shekel'),
        ('EUR', 'Euro'),
    ]
    TYPE_CHOICES = [
        ('Investment', 'Investment'),
        ('Birthday', 'Birthday'),
        ('Tasks', 'Tasks'),
    ]

    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)  # Default to active
    advisor = models.ForeignKey(
        Advisor, on_delete=models.CASCADE, related_name='watchers')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='watchers')  # Link to a User

    # Set the default to the current time
    fin_info = None

    def __str__(self):
        return f"Watcher - {self.name} ({self.type})"

    # return all events of the watcher,
    # in case of investment watcher add a statement event with 0 value as the first event
    def get_events(self, filter_type=None):
        if filter_type:
            events = list(self.events.filter(
                type=filter_type).order_by('-date'))
        else:
            events = list(self.events.all().order_by('-date'))
        if len(events) > 0 and self.type in INVESTMENT_WATCHER_TYPES:
            # Add a statement event with 0 value as the first event
            events.append(Event(
                description="Initial Statement", date=events[len(events)-1].date, parent=self, type=STATEMENT_EVENT_TYPE, value=0))
        return events


class InvestmentWatcher(Watcher):
    investment_amount = models.DecimalField(max_digits=20, decimal_places=2)
    investment_date = models.DateField()

    def __str__(self):
        return f"InvestmentWatcher - {self.name} ({self.investment_amount} {self.currency})"


class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('Statement', 'Statement'),
        ('Distribution', 'Distribution'),
        ('Distribution Notice', 'Distribution Notice'),
        ('Capital Call Notice', 'Capital Call Notice'),
        ('Wire Receipt', 'Wire Receipt'),
        ('Commitment', 'Commitment'),
    ]

    description = models.TextField()
    parent = models.ForeignKey(
        Watcher, on_delete=models.CASCADE, related_name='events')  # Link to Watcher
    type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    value = models.DecimalField(max_digits=20, decimal_places=2)
    # Set the default to the current date
    date = models.DateField(default=now)

    def __str__(self):
        return f"{self.type}: {self.description[:30]} ({self.value})"

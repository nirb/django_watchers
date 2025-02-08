from core.defs import *
from collections import defaultdict
from datetime import datetime, timedelta
from dashboard.models import Watcher


class WatchersFin:
    _instance = None  # Class-level attribute to store the single instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(WatchersFin, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # Initialize any instance-specific attributes here
        pass

    def get_statements_values(self, currency, number_of_months):

        # Retrieve all watchers with the specified currency
        watchers = Watcher.objects.filter(currency=currency)
        statements_list = []

        # Helper function to get the first day of the next month

        def first_day_of_next_month(date):
            if date.month == 12:
                return datetime(date.year + 1, 1, 1)
            else:
                return datetime(date.year, date.month + 1, 1)

        # Dictionary to store the last known value for each watcher
        last_known_values = defaultdict(lambda: 0)

        for watcher in watchers:
            # Get all statement events for the watcher
            statement_events = watcher.get_events(
                filter_type=STATEMENT_EVENT_TYPE)
            statement_events.sort(key=lambda x: x.date)  # Sort events by date

            current_date = statement_events[0].date if statement_events else datetime.now(
            ).date()
            # Calculate the start date based on the number_of_months parameter
            end_date = datetime.now().date()
            start_date = end_date.replace(day=1) - timedelta(days=30 * (number_of_months - 1))

            while current_date <= end_date and current_date >= start_date:
                # Check if there's a statement for the current month
                current_month_events = [event for event in statement_events if event.date.month ==
                                        current_date.month and event.date.year == current_date.year]
                if current_month_events:
                    # Use the last event of the month
                    last_event = current_month_events[-1]
                    last_known_values[watcher.id] = last_event.value
                # Append the last known value for the current month
                statements_list.append(
                    {"date": current_date, "value": last_known_values[watcher.id]})
                # Move to the next month
                current_date = first_day_of_next_month(current_date)

        print(statements_list)
        return statements_list

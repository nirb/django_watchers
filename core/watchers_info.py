from datetime import date
from core.defs import *
from core.fin_calcs import get_missing_events
from core.monthly_values import get_monthly_values
from core.watchers_fin import WatchersFin
from dashboard.models import Event, Watcher
from utils.converters import int_to_str, json_keys_to_string_values
from collections import OrderedDict
import json

from utils.debug import debug_func
watchersFin = WatchersFin()


class WatchersInfo:
    _instance = None  # Class-level attribute to store the single instance

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(WatchersInfo, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.user_id = None
        self.info = None
        self.watchers_events = {}
        self.watchers_info = {}

    def reset(self):
        watchersFin.clear()
        self.info = None
        self.watchers_events = {}
        self.watchers_info = {}

    def get(self, user_id):
        self.user_id = user_id
        if self.info is None:
            self._generate_info()
        return self.info

    @debug_func
    def _generate_info(self):
        watchers = watchersFin.get_watchers(self.user_id).order_by(
            NAME).order_by(CURRENCY).filter(type=INVESTMENT_WATCHER_TYPES[0])
        print("_generate_info", self.user_id, len(watchers))

        self.info = {}

        # watchers by currency
        currency_groups = {}
        for currency in Watcher.CURRENCY_CHOICES:
            currency_code = currency[0]
            currency_watchers = list(watchers.filter(
                currency=currency_code).order_by(NAME))

            currency_groups[currency_code] = [w for w in currency_watchers]
            for watcher in currency_groups[currency_code]:
                info = watchersFin.get_watcher_info(watcher.id)
                if info:
                    value_keys = [VALUE, INVESTED, DIST_ITD, DIST_YTD]
                    watcher.values = json_keys_to_string_values(
                        info, value_keys,  currency_code)
                    watcher.missing_events = get_missing_events(
                        watcher.type, info[EVENTS])
                else:
                    watcher.missing_events = "No Events"
                # watcher.id = watcher["id"] TODO NIR check this one
                watcher.advisor_name = watcher.advisor.name

            self.info['currency_groups'] = currency_groups

        print("_generate_info done")

    def update_watcher_data_over_time(self, watchers):
        if isinstance(watchers, list):
            watcher = watchers[0]
            watchers_list = watchers
        else:
            watcher = watchers
            watchers_list = [watcher]

        watcher.monthly_statements_data = self.calculate_values_over_time(
            watchers_list, type=STATEMENT_EVENT_TYPE)
        watcher.monthly_distribution_data = self.calculate_values_over_time(
            watchers_list, type=DISTRIBUTION_EVENT_TYPE)
        watcher.monthly_wire_data = self.calculate_values_over_time(
            watchers_list, type=WIRE_RECEIPT_EVENT_TYPE)

    def aggregate_monthly_values(self, all_results):
        """
        Aggregates monthly values across multiple currencies and event sets.

        Args:
            all_results: A list of JSON strings, each produced by get_monthly_values_json.

        """
        aggregated_data = {}

        for result in all_results:
            if result == {} or "currency" not in result or "data" not in result:
                continue

            currency = result["currency"]
            data = result["data"]

            if currency not in aggregated_data:
                aggregated_data[currency] = {}

            for year, monthly_values in data.items():
                year = int(year)  # convert string to int
                if year not in aggregated_data[currency]:
                    aggregated_data[currency][year] = {}
                for monthly_data_item in monthly_values:
                    month_name = monthly_data_item["month"]
                    value = monthly_data_item["value"]
                    if month_name not in aggregated_data[currency][year]:
                        aggregated_data[currency][year][month_name] = 0.0
                    aggregated_data[currency][year][month_name] += value

        # Sort the years
        sorted_years = {
            currency: OrderedDict(sorted(currency_data.items(), reverse=True))
            for currency, currency_data in aggregated_data.items()
        }
        # sort the currency
        return OrderedDict(sorted(sorted_years.items(), reverse=True))

    def calculate_values_over_time(self, watchers, type, format_values=True):
        """
        Calculates values over time for each currency, scanning statement events for each Watcher.
        If a value is missing for a month, use the value from the following month.
        Returns a list for each currency containing rows per year and month with values.
        """
        results = []

        for watcher in watchers:
            # print("calculate_values_over_time", watcher.name)
            events = Event.objects.filter(
                parent=watcher, type=type).order_by("date")
            data = get_monthly_values(
                events, watcher.currency, carrying_forward=True if type == "Statement" else False)
            results.append(data)

        if format_values:
            aggregated_data = self.format_monthly_data(
                self.aggregate_monthly_values(results))
        else:
            aggregated_data = self.aggregate_monthly_values(results)
        # print("aggregated_data", json.dumps(aggregated_data, indent=1))
        return aggregated_data

    def format_monthly_data(self, monthly_data):
        """Formats the values in the monthly data with commas."""
        formatted_data = {}
        for currency, yearly_data in monthly_data.items():
            formatted_data[currency] = {}
            for year, monthly_values in yearly_data.items():
                formatted_data[currency][year] = {}
                for month, value in monthly_values.items():
                    formatted_value = int_to_str(value, currency)
                    formatted_data[currency][year][month] = formatted_value
        return formatted_data

    def get_watchers_for_report(self, user_id, currency):
        watchers = watchersFin.get_watchers(user_id).filter(currency=currency)
        watchers_list = []
        for watcher in watchers:
            if watcher.type in INVESTMENT_WATCHER_TYPES:
                watchers_list.append({
                    "name": watcher.name,
                    "advisor": watcher.advisor.name,
                    "value": int_to_str(watchersFin.get_watcher_info(watcher.id)[VALUE], watcher.currency, show_k=False),
                    "unfunded": int_to_str(watchersFin.get_watcher_info(watcher.id)[UNFUNDED], watcher.currency, show_k=False),
                })

        return watchers_list
#

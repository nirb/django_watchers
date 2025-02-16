
import datetime
import json
from core.defs import *
from core.fin_calcs import calculate_investment_info
from core.monthly_values import get_monthly_values
from dashboard.models import Watcher
from utils.converters import currency_conversion, date_str_to_datetime, int_to_str
from utils.debug import d_print, debug_func


class WatchersFin:
    _instance = None  # Class-level attribute to store the single instance
    _clear_once = True

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(WatchersFin, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._clear_once:
            self.clear()
            self._clear_once = False

    def clear(self):
        self.watchers = None
        # sum of values per currency
        self.currency_sum = {}
        # distribution in % per currency
        self.currency_distribution = {c: 0 for c in CURRENCY_TYPES}
        # unfunded values per currency
        self.currency_unfunded = {c: 0 for c in CURRENCY_TYPES}
        # values per currency
        self.currency_values = {c: 0 for c in CURRENCY_TYPES}
        # currency sum per currency
        self.sum_pef_currency = {c: 0 for c in CURRENCY_TYPES}
        self.fin_info = {}
        for currency in CURRENCY_TYPES:
            self.currency_sum[currency] = {
                f"{VALUE_NUM}": 0, f"{INVESTED_NUM}": 0, f"{UNFUNDED}": 0, "sum": 0}

    @debug_func
    def calculate_summary(self, user_id):
        if self.watchers:
            return  # already calculated

        self.watchers = Watcher.objects.filter(user_id=user_id).order_by(
            NAME).order_by(CURRENCY)
        # self.get_total_values_monthly(user_id, "NIS")
        # self.get_total_values_monthly(user_id, "NIS", DISTRIBUTION_EVENT_TYPE)

        self.calculate_currency_sum()
        self.convert_sum_values_to_str()
        total_assets_in_currencies = self.calculate_total_assets_in_currencies()

        # calculete the currency distribution (convert all to USD)
        assets_in_usd = {
            c: currency_conversion(
                self.currency_sum[c][VALUE_NUM], c, "USD") for c in CURRENCY_TYPES
        }

        # set the current values for each currency
        for currency in CURRENCY_TYPES:
            self.currency_values[currency] = self.currency_sum[currency][VALUE]

        self.sum_pef_currency = {c: int_to_str(
            total_assets_in_currencies[c], c) for c in CURRENCY_TYPES}

        self.currency_unfunded = {
            c: self.currency_sum[c][UNFUNDED_STR] for c in CURRENCY_TYPES
        }

        if total_assets_in_currencies["USD"] > 0:
            self.currency_distribution = {
                c: f"{(assets_in_usd[c]/total_assets_in_currencies['USD']) * 100:.2f}%" for c in CURRENCY_TYPES}

    @debug_func
    def calculate_currency_sum(self):
        # set watcher fin_info, calculate the total values for all watchers
        for watcher in self.watchers:
            if watcher.type in INVESTMENT_WATCHER_TYPES:
                # print("calculate_currency_sum", watcher.name)
                fin_info = calculate_investment_info(watcher.get_events())
                fin_info[UNFUNDED_STR] = int_to_str(
                    fin_info[UNFUNDED], watcher.currency)
                fin_info[COMMITMENT_CURRENCY] = int_to_str(
                    fin_info[COMMITMENT], watcher.currency)
                self.fin_info[f"{watcher.id}"] = fin_info
                # print("calculate_currency_sum",watcher.name,fin_info)
                if fin_info:
                    self.currency_sum[f"{watcher.currency}"][VALUE_NUM] += fin_info[VALUE]
                    self.currency_sum[f"{watcher.currency}"][INVESTED_NUM] += fin_info[INVESTED]
                    self.currency_sum[f"{watcher.currency}"][UNFUNDED] += fin_info[UNFUNDED]
                else:
                    d_print("watcher with no events, fin_info is None",
                            watcher.name)
            else:
                d_print("watcher type not in INVESTMENT_WATCHER_TYPES")
        # print("calculate_currency_sum", json.dumps(self.fin_info, cl, indent=2))

    @debug_func
    def convert_sum_values_to_str(self):
        # convert the values to string with currency
        for currency in CURRENCY_TYPES:
            self.currency_sum[currency][VALUE] = int_to_str(
                self.currency_sum[currency][VALUE_NUM], currency)
            self.currency_sum[currency][INVESTED] = int_to_str(
                self.currency_sum[currency][INVESTED_NUM], currency)
            self.currency_sum[currency][UNFUNDED_STR] = int_to_str(
                self.currency_sum[currency][UNFUNDED], currency)

    @debug_func
    def calculate_total_assets_in_currencies(self):
        # set the current values for each currency
        total_assets_in_currencies = {c: 0 for c in CURRENCY_TYPES}
        for currency in CURRENCY_TYPES:
            value = self.currency_sum[currency][VALUE_NUM]
            for c in CURRENCY_TYPES:
                total_assets_in_currencies[c] += currency_conversion(
                    value, currency, c)
        return total_assets_in_currencies

    def get_watcher_info(self, watcher_id):
        info = self.fin_info.get(f"{watcher_id}", None)
        # if info and (watcher_id == 13 or isinstance(info[UNFUNDED], str)):
        #    print('here')
        return info

    def get_watchers(self, user_id):
        if self.watchers is None:
            self.calculate_summary(user_id)
        return self.watchers

    def get_watcher(self, user_id, watcher_name_or_id):
        print("get_watcher", watcher_name_or_id, type(watcher_name_or_id))
        if isinstance(watcher_name_or_id, str):
            watcher_qs = self.get_watchers(
                user_id).filter(name=watcher_name_or_id)
        else:
            watcher_qs = self.get_watchers(
                user_id).filter(id=watcher_name_or_id)
        if watcher_qs:
            return watcher_qs[0]
        return None

    def get_watchers_sum_currency_per_month(self, user_id, currency, events_type):
        if "Total_in_" in currency:
            currency = currency.split("_")[-1]
            return self.get_total_values_monthly(user_id, currency, events_type)
        watchers = self.get_watchers(user_id).filter(currency=currency)
        return self.get_watchers_sum_per_month(watchers, currency, events_type)

    def get_watcher_sum_per_month(self, user_id, watcher_id, events_type):
        watchers = self.get_watchers(user_id).filter(id=watcher_id)
        return self.get_watchers_sum_per_month(watchers, watchers[0].currency, events_type)

    def get_watchers_sum_per_month(self, watchers, currency, events_type):
        total_sum_per_month = {}
        for watcher in watchers:
            events = watcher.get_events(events_type)[::-1]
            carrying_forward = True if events_type == STATEMENT_EVENT_TYPE else False
            monethly_values = get_monthly_values(
                events, currency, carrying_forward)

            if "values" in monethly_values:
                for item in monethly_values["values"]:
                    for date_str, value in item.items():
                        if date_str in total_sum_per_month:
                            total_sum_per_month[date_str] += value
                        else:
                            total_sum_per_month[date_str] = value

            # print("get_watchers_sum_per_month", watcher.name,
            #      json.dumps(monethly_values, indent=2))
        sorted_sum = dict(sorted(total_sum_per_month.items()))
        return [{"date": date_str, "value": value} for date_str, value in sorted_sum.items()]

    def get_total_values_monthly(self, user_id, to_currency="USD", events_type=STATEMENT_EVENT_TYPE):
        total_values = None

        # put the to_currency in the first place
        currencies = [to_currency] + \
            [c for c in CURRENCY_TYPES if c != to_currency]

        for currency in currencies:
            sum_per_month = self.get_watchers_sum_per_month(
                self.get_watchers(user_id).filter(currency=currency), currency, events_type)
            if total_values is None:
                total_values = sum_per_month
                continue

            for item in sum_per_month:
                date_str = item['date']
                value = item['value']
                if value > 0:
                    index = next((i for i, item in enumerate(
                        total_values) if item['date'] == date_str), None)
                    if index is not None:
                        if currency != to_currency:
                            total_values[index]['value'] += currency_conversion(
                                value, currency, to_currency, datetime.datetime.strptime(date_str, DATE_FORMAT))
                        else:
                            total_values[index]['value'] += value

        # print("get_total_values_monthly", json.dumps(total_values, indent=2))
        return total_values

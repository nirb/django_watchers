
from core.defs import *
from core.fin_calcs import calculate_investment_info
from dashboard.models import Watcher
from utils.converters import currency_conversion, currency_to_color, currency_to_name, int_to_str
from utils.debug import d_print, debug_func


class WatchersFin:
    _instance = None  # Class-level attribute to store the single instance

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(WatchersFin, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.clear()

    def clear(self):
        self.watchers = None
        # sum of values per currency
        self.currency_sum = {}
        # distribution in % per currency
        self.currency_distribution = {}
        # unfunded values per currency
        self.currency_unfunded = {}
        # values per currency
        self.currency_values = {}
        # currency sum per currency
        self.sum_pef_currency = {}
        self.fin_info = {}
        for currency in CURRENCY_TYPES:
            self.currency_sum[currency] = {
                f"{VALUE_NUM}": 0, f"{INVESTED_NUM}": 0, f"{UNFUNDED_NUM}": 0, "sum": 0}

    @debug_func
    def calculate_summary(self, user_id):
        if self.watchers:
            return  # already calculated

        self.watchers = Watcher.objects.filter(user_id=user_id).order_by(
            NAME).order_by(CURRENCY)

        self.calculate_currency_sum()
        self.convert_sum_values_to_str()
        sum_usd, sum_nis, sum_eur = self.calculate_sum_pef_currency()

        # calculete the currency distribution (convert all to USD)
        value_usd = self.currency_sum["USD"][VALUE_NUM]
        value_nis_in_usd = currency_conversion(
            self.currency_sum["NIS"][VALUE_NUM], "NIS", "USD")
        value_eur_in_usd = currency_conversion(
            self.currency_sum["EUR"][VALUE_NUM], "EUR", "USD")

        # set the current values for each currency
        for currency in CURRENCY_TYPES:
            self.currency_values[currency] = self.currency_sum[currency][VALUE]

        self.sum_pef_currency = {"USD": int_to_str(sum_usd, "USD"),
                                 "NIS": int_to_str(sum_nis, "NIS"),
                                 "EUR": int_to_str(sum_eur, "EUR")}

        self.currency_unfunded = {"USD": self.currency_sum["USD"][UNFUNDED],
                                  "NIS": self.currency_sum["NIS"][UNFUNDED],
                                  "EUR": self.currency_sum["EUR"][UNFUNDED]}

        self.currency_distribution = {"USD": f"{(value_usd/sum_usd) * 100:.2f}%",
                                      "NIS": f"{(value_nis_in_usd/sum_usd) * 100:.2f}%",
                                      "EUR": f"{(value_eur_in_usd/sum_usd) * 100:.2f}%"}

    @debug_func
    def calculate_currency_sum(self):
        # set watcher fin_info, calculate the total values for all watchers
        for watcher in self.watchers:
            if watcher.type in INVESTMENT_WATCHER_TYPES:
                fin_info = calculate_investment_info(watcher.get_events())
                self.fin_info[f"{watcher.id}"] = fin_info
                # print("calculate_currency_sum",watcher.name,fin_info)
                if fin_info:
                    self.currency_sum[f"{watcher.currency}"][VALUE_NUM] += fin_info[VALUE]
                    self.currency_sum[f"{watcher.currency}"][INVESTED_NUM] += fin_info[INVESTED]
                    self.currency_sum[f"{watcher.currency}"][UNFUNDED_NUM] += fin_info[UNFUNDED]
                else:
                    d_print("watcher with no events, fin_info is None",
                            watcher.name)
            else:
                d_print("watcher type not in INVESTMENT_WATCHER_TYPES")

    @ debug_func
    def convert_sum_values_to_str(self):
        # convert the values to string with currency
        for currency in CURRENCY_TYPES:
            self.currency_sum[currency][VALUE] = int_to_str(
                self.currency_sum[currency][VALUE_NUM], currency)
            self.currency_sum[currency][INVESTED] = int_to_str(
                self.currency_sum[currency][INVESTED_NUM], currency)
            self.currency_sum[currency][UNFUNDED] = int_to_str(
                self.currency_sum[currency][UNFUNDED_NUM], currency)

    @ debug_func
    def calculate_sum_pef_currency(self):
        # set the current values for each currency
        sum_usd = 0
        sum_nis = 0
        sum_eur = 0
        for currency in CURRENCY_TYPES:
            value = self.currency_sum[currency][VALUE_NUM]
            sum_usd += currency_conversion(value, currency, "USD")
            sum_nis += currency_conversion(value, currency, "NIS")
            sum_eur += currency_conversion(value, currency, "EUR")
        return sum_usd, sum_nis, sum_eur

    def get_watcher_info(self, watcher_id):
        return self.fin_info.get(f"{watcher_id}", None)

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

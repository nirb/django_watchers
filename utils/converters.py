from core.defs import *

from datetime import datetime
from dashboard.models import Event


def currency_converter(currency, obj_list):
    if currency in CURRENCY_TYPES:
        return obj_list[CURRENCY_TYPES.index(currency)]
    if currency in CURRENCY_SYMBOLS:
        return obj_list[CURRENCY_SYMBOLS.index(currency)]

    return None


def currency_to_symbol_or_type(currency):
    ret = currency_converter(currency, CURRENCY_SYMBOLS)
    if ret:
        return ret
    return currency_converter(currency, CURRENCY_TYPES)


def currency_to_color(currency):
    return currency_converter(currency, CURRENCY_COLORS)


def currency_to_name(currency):
    return currency_converter(currency, CURRENCY_NAMES)


def currency_conversion(value, currency, to_currency):
    USD2NIS = 3.61355
    USD2EUR = 0.9717
    conversions = {"usd2nis": USD2NIS, "usd2eur": USD2EUR,
                   "nis2usd": 1 / USD2NIS, "nis2eur": USD2EUR/USD2NIS,
                   "eur2usd": 1/USD2EUR, "eur2nis": USD2NIS/USD2EUR}
    if currency == to_currency:
        return value

    return value * conversions[f"{currency.lower()}2{to_currency.lower()}"]


def int_to_str(value, currency=None):
    # print("int_to_str", value, type(value))
    if isinstance(value, str):
        try:
            value = float(value)
        except ValueError:
            return value
    show_currency = ""
    if currency:
        show_currency = currency_to_symbol_or_type(currency)
    k_sign = ""
    if abs(value) >= 100000:
        value = value/1000
        k_sign = "K"
    if int(value) >= 0:
        if value % 1 == 0:
            return f"{show_currency}{int(value):,}{k_sign}"
        else:
            return f"{show_currency}{value:,.1f}{k_sign}"
    return f"({show_currency}{(-1*value):,.1f}{k_sign})"


def json_keys_to_string_values(input_obj, keys, currency=None):
    # print("json_keys_to_string_values1", input_obj, keys)
    for key in keys:
        # print("json_keys_to_string_values2", type(input_obj), key)
        if isinstance(input_obj, dict):  # or isinstance(input_obj, Event):
            input_obj[key] = int_to_str(input_obj.get(key), currency)
        else:  # it is an queryset object
            val = int_to_str(getattr(input_obj, key), currency)
            setattr(input_obj, key, val)
    return input_obj


def list_keys_to_string_values(in_list, keys, currency=None):
    # ret_list = list(jsonlist)  copy the list
    for l in in_list:
        json_keys_to_string_values(l, keys, currency)
    return in_list


def date_str_to_datetime(date_str):
    # print(type(date_str))
    supported_formats = [DATE_FORMAT, "%d/%m/%Y", "%d/%m/%y",
                         "%B %d, %Y",  "%u %B %Y", "%d %B %Y"]

    for formate in supported_formats:
        try:
            dt = datetime.strptime(date_str, formate)
            return dt.strftime(DATE_FORMAT)
        except Exception as e:
            continue

    # check if the format is Qx yyyy
    try:
        q, y = date_str.split(" ")
        q = int(q[1])
        y = int(y)
        print("date debug", q, y)
        return datetime(y, 3*q-1, 1).strftime(DATE_FORMAT)
    except Exception as e:
        pass
    print(
        f"!!!!! Failed to format '{date_str}' to datetime, please improve the code")
    print(f"date_str_to_datetime in {__file__}")


def to_percent(value):
    """Convert a decimal value to a percentage string."""
    return f"{value:.2f}%" if value is not None else "N/A"

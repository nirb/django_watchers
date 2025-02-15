from decimal import Decimal
from core.defs import *

# import requests
import datetime
import json

from dashboard.models import Advisor, Event, Watcher


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


def int_to_str(value, currency=None, show_k=True):
    # print("int_to_str", value, type(value))
    if isinstance(value, str):
        try:
            value = float(value)
        except ValueError:
            return value[:-2] if value.endswith('.0') else value
    show_currency = ""
    if currency:
        show_currency = currency_to_symbol_or_type(currency)
    k_sign = ""
    if abs(value) >= 100000 and show_k:
        value = value/1000
        k_sign = "K"
    if int(value) >= 0:
        if value % 1 == 0:
            return f"{show_currency}{int(value):,}{k_sign}"
        else:
            return f"{show_currency}{value:,.0f}{k_sign}" if value % 1 == 0 else f"{show_currency}{value:,.1f}{k_sign}"
    return f"({show_currency}{(-1*value):,.0f}{k_sign})" if value % 1 == 0 else f"({show_currency}{(-1*value):,.1f}{k_sign})"


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
            dt = datetime.datetime.strptime(date_str, formate)
            return dt.strftime(DATE_FORMAT)
        except Exception as e:
            continue

    # check if the format is Qx yyyy
    try:
        q, y = date_str.split(" ")
        q = int(q[1])
        y = int(y)
        print("date debug", q, y)
        return datetime.datetime(y, 3*q-1, 1).strftime(DATE_FORMAT)
    except Exception as e:
        pass
    print(
        f"!!!!! Failed to format '{date_str}' to datetime, please improve the code")
    print(f"date_str_to_datetime in {__file__}")


def to_percent(value):
    """Convert a decimal value to a percentage string."""
    return f"{value:.2f}%" if value is not None else "N/A"


def event_type_to_color(event_type):
    if event_type == STATEMENT_EVENT_TYPE:
        return "statement-color"
    elif event_type == DISTRIBUTION_EVENT_TYPE:
        return "distribution-color"
    elif event_type == "Distribution Notice":
        return "distribution-notice-color"
    elif event_type == "Capital Call Notice":
        return "capital-call-color"
    elif event_type == WIRE_RECEIPT_EVENT_TYPE:
        return "wire-receipt-color"
    elif event_type == COMMITMENT_EVENT_TYPE:
        return "commitment-color"

    return "text-bg-success"


def fetch_exchange_rates():
    access_key = "d9d8ba3b2c455be0f6bb3fdf7bba2779"
    base_currency = "EUR"
    symbols = "USD,ILS"
    start_date = datetime.date(2025, 1, 1)
    end_date = datetime.date(2025, 2, 1)

    results = {}
    current_date = start_date

    while current_date <= end_date:
        url = f"http://data.fixer.io/api/{current_date}?access_key={access_key}&base={base_currency}&symbols={symbols}"
        response = requests.get(url)
        data = response.json()

        if data.get("success"):
            eur_to_usd = data["rates"].get("USD")
            eur_to_ils = data["rates"].get("ILS")

            if eur_to_usd and eur_to_ils:
                usd_to_ils = eur_to_ils / eur_to_usd
                results[str(current_date)] = {"ILS": round(
                    usd_to_ils, 4), "EUR": round(1 / eur_to_usd, 4)}

        current_date = (current_date.replace(day=1) +
                        datetime.timedelta(days=32)).replace(day=1)

    return results


def currency_conversion(value, currency, to_currency, in_date=datetime.datetime.now()):
    rate = get_rate(in_date.year, in_date.month)
    conversions = {"usd2nis": rate['ILS'], "usd2eur": rate['EUR'],
                   "nis2usd": 1 / rate['ILS'], "nis2eur": rate['EUR']/rate['ILS'],
                   "eur2usd": 1/rate['EUR'], "eur2nis": rate['ILS']/rate['EUR']}
    if currency == to_currency:
        return value

    return value * conversions[f"{currency.lower()}2{to_currency.lower()}"]


# print(json.dumps(fetch_exchange_rates(), indent=2))
def get_rate(year, month):
    rates = {
        "2021-01-01": {
            "ILS": 3.213,
            "EUR": 0.8213
        },
        "2021-02-01": {
            "ILS": 3.2954,
            "EUR": 0.8286
        },
        "2021-03-01": {
            "ILS": 3.3043,
            "EUR": 0.8299
        },
        "2021-04-01": {
            "ILS": 3.334,
            "EUR": 0.849
        },
        "2021-05-01": {
            "ILS": 3.2431,
            "EUR": 0.832
        },
        "2021-06-01": {
            "ILS": 3.2407,
            "EUR": 0.8185
        },
        "2021-07-01": {
            "ILS": 3.2689,
            "EUR": 0.8442
        },
        "2021-08-01": {
            "ILS": 3.2273,
            "EUR": 0.8429
        },
        "2021-09-01": {
            "ILS": 3.2065,
            "EUR": 0.8446
        },
        "2021-10-01": {
            "ILS": 3.2189,
            "EUR": 0.8624
        },
        "2021-11-01": {
            "ILS": 3.1175,
            "EUR": 0.8621
        },
        "2021-12-01": {
            "ILS": 3.1529,
            "EUR": 0.8835
        },
        "2022-01-01": {
            "ILS": 3.1126,
            "EUR": 0.8794
        },
        "2022-02-01": {
            "ILS": 3.1704,
            "EUR": 0.8871
        },
        "2022-03-01": {
            "ILS": 3.2226,
            "EUR": 0.8982
        },
        "2022-04-01": {
            "ILS": 3.203,
            "EUR": 0.9051
        },
        "2022-05-01": {
            "ILS": 3.3414,
            "EUR": 0.9492
        },
        "2022-06-01": {
            "ILS": 3.3426,
            "EUR": 0.9387
        },
        "2022-07-01": {
            "ILS": 3.5316,
            "EUR": 0.9589
        },
        "2022-08-01": {
            "ILS": 3.3605,
            "EUR": 0.9746
        },
        "2022-09-01": {
            "ILS": 3.3978,
            "EUR": 1.0048
        },
        "2022-10-01": {
            "ILS": 3.5585,
            "EUR": 1.0199
        },
        "2022-11-01": {
            "ILS": 3.5366,
            "EUR": 1.0123
        },
        "2022-12-01": {
            "ILS": 3.3926,
            "EUR": 0.9498
        },
        "2023-01-01": {
            "ILS": 3.5279,
            "EUR": 0.9342
        },
        "2023-02-01": {
            "ILS": 3.4519,
            "EUR": 0.9081
        },
        "2023-03-01": {
            "ILS": 3.6168,
            "EUR": 0.9373
        },
        "2023-04-01": {
            "ILS": 3.6004,
            "EUR": 0.9199
        },
        "2023-05-01": {
            "ILS": 3.6216,
            "EUR": 0.9117
        },
        "2023-06-01": {
            "ILS": 3.745,
            "EUR": 0.9293
        },
        "2023-07-01": {
            "ILS": 3.7094,
            "EUR": 0.9161
        },
        "2023-08-01": {
            "ILS": 3.6364,
            "EUR": 0.9085
        },
        "2023-09-01": {
            "ILS": 3.7961,
            "EUR": 0.9263
        },
        "2023-10-01": {
            "ILS": 3.8073,
            "EUR": 0.9466
        },
        "2023-11-01": {
            "ILS": 4.0141,
            "EUR": 0.9447
        },
        "2023-12-01": {
            "ILS": 3.7172,
            "EUR": 0.9181
        },
        "2024-01-01": {
            "ILS": 3.6026,
            "EUR": 0.906
        },
        "2024-02-01": {
            "ILS": 3.6608,
            "EUR": 0.9196
        },
        "2024-03-01": {
            "ILS": 3.5661,
            "EUR": 0.9216
        },
        "2024-04-01": {
            "ILS": 3.6776,
            "EUR": 0.9314
        },
        "2024-05-01": {
            "ILS": 3.7558,
            "EUR": 0.9328
        },
        "2024-06-01": {
            "ILS": 3.7194,
            "EUR": 0.9211
        },
        "2024-07-01": {
            "ILS": 3.7626,
            "EUR": 0.9314
        },
        "2024-08-01": {
            "ILS": 3.7924,
            "EUR": 0.927
        },
        "2024-09-01": {
            "ILS": 3.6519,
            "EUR": 0.9054
        },
        "2024-10-01": {
            "ILS": 3.7563,
            "EUR": 0.9039
        },
        "2024-11-01": {
            "ILS": 3.7525,
            "EUR": 0.9191
        },
        "2024-12-01": {
            "ILS": 3.6364,
            "EUR": 0.9484
        },
        "2025-01-01": {
            "ILS": 3.6431,
            "EUR": 0.9661
        },
        "2025-02-01": {
            "ILS": 3.5819,
            "EUR": 0.9651
        }
    }

    # return the rate for the given date
    ret = rates.get(datetime.datetime(
        year, month, 1).strftime("%Y-%m-%d"), None)
    if ret is None:
        # gate the latest rate
        latest_date = max(rates.keys())
        ret = rates.get(latest_date, None)
        print(
            f"Warning Rate for {year=} {month=} not found, using {latest_date=}")
    return ret


print("nirnir", get_rate(2025, 4))


class AppJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Event):  # Handle Event objects
            return {
                "id": obj.id,
                "description": obj.description,
                "parent_id": obj.parent.id if obj.parent else None,
                "type": obj.type,
                # Convert Decimal to float
                "value": str(obj) if isinstance(obj, str) else obj.value,
                # Convert DateField to string
                "date": obj.date.strftime("%Y-%m-%d"),
            }
        if isinstance(obj, Watcher):  # Handle Watcher objects
            return {
                "id": obj.id,
                "name": obj.name,
                "active": obj.active,
                "advisor": obj.advisor.name,
                "currency": obj.currency,
                "type": obj.type,
                "user": obj.user.username,
            }
        if isinstance(obj, Advisor):  # Handle Advisor objects
            return {
                "name": obj.name,
                "phone": obj.phone,
                "mail": obj.mail,
            }
        if isinstance(obj, Decimal):  # Convert Decimal to float
            return float(obj)
        if isinstance(obj, datetime.date):  # Convert date to string
            return obj.strftime("%Y-%m-%d")
        return super().default(obj)  # Use default behavior for other types

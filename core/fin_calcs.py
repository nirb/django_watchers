from datetime import datetime
from core.defs import *
from utils.converters import int_to_str, to_percent
from utils.debug import print_debug
from scipy.optimize import newton
import numpy_financial as npf


def calculate_investment_profit(invested, currrent_value):
    return currrent_value - invested


def months_between_dates(date1, date2):
    if isinstance(date1, str):
        date1 = datetime.strptime(date1, DATE_FORMAT)
    if isinstance(date2, str):
        date2 = datetime.strptime(date2, DATE_FORMAT)

    if date1 > date2:
        date1, date2 = date2, date1

    return (date2.year - date1.year) * 12 + (date2.month - date1.month)


def calculate_investment_info(events):
    """
    Calculate key financial information including YTD, ITD, IRR, and XIRR from a list of investment events.

    :param events: List of dictionaries. Each dictionary represents an event with keys 'COL_DATE', 'COL_TYPE', and 'COL_VALUE'.
    :return: Dictionary containing the financial summary.
    """
    # Check if there are any events
    if len(events) == 0:
        return None

    # Sorting events based on date, assuming date is in DATE_FORMAT
    # events.sort(key=lambda x: datetime.strptime(x[COL_DATE], DATE_FORMAT))
    # print(json.dumps(events, indent=4, cls=DecimalEncoder))
    total_invested = 0
    total_distributed = 0
    current_value = 0

    cash_flows = []  # List to store cash flows for IRR and XIRR calculation
    cash_flow_dates = []  # Corresponding dates for each cash flow
    # Get the current year for YTD calculations
    last_event_date = events[0].date
    ytd_invested = 0
    ytd_distributed = 0

    ytd_start_value = 0
    ytd_end_value = 0
    total_commitment = 0
    for event in events:
        event_year = event.date.year
        event_type = event.type
        value = int(event.value)
        if event_type == STATEMENT_EVENT_TYPE:
            if current_value == 0:
                current_value = value
            # TODO think about this
            # if event_year == current_year-1:
            #    ytd_start_value = value
            if event_year == last_event_date.year:
                ytd_start_value = value
            if event_year == last_event_date.year and ytd_end_value == 0:
                ytd_end_value = value
        elif event_type == WIRE_RECEIPT_EVENT_TYPE:
            total_invested += value
            cash_flows.append(-value)  # Investment is a negative cash flow
            cash_flow_dates.append(event.date)
            if event_year == last_event_date.year:
                ytd_invested += value
        elif event_type == DISTRIBUTION_EVENT_TYPE:
            total_distributed += value
            cash_flows.append(value)  # Distribution is a positive cash flow
            cash_flow_dates.append(event.date)
            if event_year == last_event_date.year:
                ytd_distributed += value
        elif event_type == COMMITMENT_EVENT_TYPE:
            total_commitment += value

    # Add the current value of the investment as the final cash flow (assuming the latest date)
    if current_value:
        cash_flows.append(current_value)
        cash_flow_dates.append(last_event_date)

    # Calculate Net Gain or Loss
    net_gain_or_loss = current_value + total_distributed - total_invested

    # Calculate ROI (Return on Investment) as a percentage
    roi = (net_gain_or_loss / total_invested) * \
        100 if total_invested > 0 else 0

    # Calculate YTD Net Gain or Loss
    # print(
    #    f"{ytd_end_value=} {ytd_start_value=} {ytd_distributed=} {ytd_invested=}")
    ytd_net_gain_or_loss = ytd_end_value - ytd_invested + \
        ytd_distributed - ytd_start_value

    # Calculate YTD as a percentage
    ytd_start = ytd_start_value + ytd_distributed + ytd_invested
    print_debug(f"{ytd_start=} {ytd_net_gain_or_loss=}")
    ytd_percentage = 0 if ytd_start == 0 else 100 * \
        (ytd_net_gain_or_loss / ytd_start)
    print_debug(f"{ytd_percentage=}")

    # Calculate ITD (Inception-to-Date) Net Gain or Loss
    itd_net_gain_or_loss = net_gain_or_loss

    # Calculate ITD as a percentage
    itd_percentage = (itd_net_gain_or_loss / total_invested) * \
        100 if total_invested > 0 else 0

    # Calculate IRR using numpy (requires periodic cash flows)
    irr = npf.irr(cash_flows) * 100 if cash_flows else 0

    # Calculate XIRR using actual dates (requires uneven cash flows)
    def calculate_xirr(cash_flows, cash_flow_dates):
        """ Calculate the XIRR using cash flows and their corresponding dates. """
        def xnpv(rate, cash_flows, cash_flow_dates):
            return sum(cf / (1 + rate) ** ((d - cash_flow_dates[0]).days / 365) for cf, d in zip(cash_flows, cash_flow_dates))

        def xirr(cash_flows, cash_flow_dates, guess=0.1):
            return newton(lambda r: xnpv(r, cash_flows, cash_flow_dates), guess)

        return xirr(cash_flows, cash_flow_dates) * 100 if cash_flows else 0
    try:
        xirr = calculate_xirr(cash_flows, cash_flow_dates)
    except Exception as e:
        xirr = 0

    invested_months = 0
    if len(events) > 1:
        invested_months = months_between_dates(
            datetime.now().date(), events[len(events)-1].date)
    # Prepare the result dictionary
    result = {
        INVESTED: total_invested,
        COMMITMENT: total_commitment,
        UNFUNDED: total_invested - total_commitment,
        DIST_ITD: total_distributed,
        DIST_YTD: ytd_distributed,
        VALUE: current_value,
        ROI: to_percent(roi),
        PROFIT_YTD: ytd_net_gain_or_loss,
        PROFIT_ITD: itd_net_gain_or_loss,
        NET_GAIN: net_gain_or_loss,
        YTDP: to_percent(ytd_percentage),
        ITDP: to_percent(itd_percentage),
        IRR: to_percent(irr),
        XIRR: to_percent(xirr),
        MONTHS: invested_months,
        YEARS: f"{(invested_months/12):.1f}",
        COUNT: len(events),
        EVENTS: events
    }

    # print(json.dumps(result, indent=4))

    return result


def get_missing_events(watcher_type, events):
    if watcher_type in INVESTMENT_WATCHER_TYPES:
        events_types = set()
        if len(events) == 0:
            print("debug", len(events))
        for event in events:
            if event.type not in events_types:
                events_types.add(event.type)

        missing_events_types = list(
            set(INVESTMENT_EVENT_TYPES_MUST_HAVE)-events_types)

        if len(missing_events_types) == 0:
            return ""
        if len(missing_events_types) == 1:
            return missing_events_types[0]
        if len(missing_events_types) > 1:
            return ", ".join(missing_events_types[:-1]) + " and " + missing_events_types[-1]
    else:
        print(
            f"Error - get_missing_events - Need to implement for {watcher_type=}")
        return None

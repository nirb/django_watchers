from datetime import date

from core.defs import STATEMENT_EVENT_TYPE


def get_monthly_values(events, currency, carrying_forward=True):
    """
    Generates a JSON representation of monthly values, grouped by year,
    carrying forward values from previous years, and including currency.

    Args:
        events: A queryset of Event objects, ordered by date.
        currency: The currency associated with the events.

    Returns:
        A JSON string representing a dictionary with "currency" and "data".
        "data" is a dictionary where keys are years and values are lists of
        dictionaries, each containing "month" and "value".
        Returns "{}" (empty JSON object) if no events.
    """
    if not events:
        return "{}"

    first_event_date = events[0].date
    current_date = date.today()

    start_year = first_event_date.year
    end_year = current_date.year

    monthly_data = {}
    values = []
    last_known_value = 0.0

    for year in range(start_year, end_year + 1):
        monthly_data[year] = []
        for month in range(1, 13):
            if year == start_year and month < first_event_date.month:
                monthly_data[year].append({
                    "month": month,
                    "value": 0.0
                })
                values.append(
                    {date(year, month, 1).isoformat(): 0.0})
                continue
            if year == end_year and month > current_date.month:
                break

            event_value = 0
            for event in events:
                if event.date.year == year and event.date.month == month:
                    if event.type == STATEMENT_EVENT_TYPE:
                        if float(event.value) > event_value:
                            event_value = float(event.value)
                    else:
                        event_value += float(event.value)

            if event_value != 0:
                last_known_value = event_value
            elif not carrying_forward:
                last_known_value = 0.0

            monthly_data[year].append({
                "month": month,
                "value": last_known_value
            })

            values.append(
                {date(year, month, 1).isoformat(): last_known_value})

    # Embed currency in the result
    result = {
        "currency": currency,
        "data": monthly_data,
        "values": values
    }

    return result

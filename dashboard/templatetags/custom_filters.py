from django import template
import calendar
register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Retrieve a value from a dictionary by key."""
    return dictionary.get(key, 0)  # Return 0 if the key does not exist


@register.filter
def number_range(value):
    return range(1, value + 1)


@register.filter
def month_name(month_number):
    try:
        month_number = int(month_number)  # Ensure it's an integer
        return calendar.month_abbr[month_number]
    except (ValueError, IndexError):
        return ""  # Handle invalid month numbers


@register.filter
def format_value(value):
    try:
        value = int(value) if float(value).is_integer() else value
        k = ""
        if value >= 1000000:
            value = int(value / 1000)
            k = "k"
        return f"{value:,}{k}"
    except (ValueError, TypeError):
        return value

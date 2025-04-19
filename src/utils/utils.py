from typing import List, Tuple
import string
import pandas as pd
from datetime import datetime
import calendar

from src.logging.logger import Logger
from src.utils.config_vars import DAYS_PAGINATION_SIZE, VALID_INPUT_DATE_FORMATS
from src.utils.session_vars import TRADE_SESSION_TIMEZONES
import re

logger = Logger()

TIMEFRAME_TO_DAYS_COUNT_MAP = {
    "Daily": lambda date_str: (date_str, 1),
    "Weekly": lambda date_str: (date_str, 7),
    "Monthly": lambda date_str: get_month_start_end(date_str),
}

def format_ini_table_names(underscored_table_names: List[str]):
    if not underscored_table_names:
        raise ValueError(f"Unable to format ini table name: no table names were provided")

    formatted_table_names = []
    for underscored_table_name in underscored_table_names:
        name_segments = []
        for name_segment in underscored_table_name.split('_'):
            if name_segment:
                name_segments += [name_segment.capitalize()]

        if name_segments:
            if name_segments[-1] == "Table":
                name_segments = name_segments[:-1]
            formatted_table_names.append(' '.join(name_segments))

    return formatted_table_names

def unpack_ini_list_value(value_as_newline_list: str):
    if not value_as_newline_list:
        raise ValueError(f"Unable to unpack ini list: list is empty")

    return [keyword for keyword in value_as_newline_list.split('\n') if keyword]

"""def build_properties(default_properties, properties_requested, css_classes):
    properties_info = {}
    for property_name in properties_requested:
        property_data = default_properties.get(property_name)
        if property_data:
            properties_info[property_name] = property_data
        else:
            properties_info[property_name] = ""

    if css_classes:
        inline_css_classes = unwrap_css_classes(css_classes)
        properties_info["cssclasses"] = inline_css_classes

    return properties_info
"""
def unwrap_css_classes(css_classes: List):
    if not css_classes:
        return ""

    return '\n' + '\n'.join(f"   - {css_class}" for css_class in css_classes)

def remove_matched_elements(list1, list2):
    set2 = set(list2)
    return [item for item in list1 if item not in set2]

def extract_format_arguments(format_string):
    formatter = string.Formatter()
    return [field_name for _, field_name, _, _ in formatter.parse(format_string) if field_name is not None]

def filter_nas_in_series(series, empty_cell_value=''):
    if not pd.isna(empty_cell_value):
        series.replace(empty_cell_value, pd.NA, inplace=True)
    return series.dropna() if not series.empty else series

def get_decimal_cases(number):
    if type(number) == float:
        number_as_str = str(number)
    elif type(number) == str:
        number_as_str = number
    elif type(number) == int:
        return 0
    else:
        raise TypeError(f"Cannot get decimal cases for '{number}'. Not a valid number")


    if '.' not in number_as_str:
        return 0
    number_segmented = number_as_str.split('.')

    return len(number_segmented[-1])

def date_difference(date_init: str or datetime, date_end: str or datetime, format="%Y-%m-%d %H:%M:%S") -> str:
    if not date_init or not date_end:
        return ""

    try:
        if isinstance(date_init, str):
            date_init = datetime.strptime(date_init, format)
        if isinstance(date_end, str):
            date_end = datetime.strptime(date_end, format)
    except ValueError as value_err:
        raise ValueError(f"Unable to format date: {value_err}")

    if date_end < date_init:
        raise ValueError(f"date_end {str(date_end)} cannot be bigger than date_init {date_init}!")

    delta = abs(date_end - date_init)
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    time_units = [
        (days, "day"),
        (hours, "hour"),
        (minutes, "minute"),
        (seconds, "second"),
    ]

    # include only non-zero time units
    formatted_parts = [
        f"{value} {unit}{'s' if value > 1 else ''}"
        for value, unit in time_units if value > 0
    ]

    if not formatted_parts:
        return "0 seconds"

    # Combine the parts into the final string
    if len(formatted_parts) == 1:
        return formatted_parts[0]

    return ", ".join(formatted_parts[:-1]) + f" and {formatted_parts[-1]}"

def get_sessions_in_date(date: str or datetime, sessions=TRADE_SESSION_TIMEZONES, date_format="%Y-%m-%d %H:%M:%S"):
    if not date:
        raise ValueError(f"Unable to parse date '{date}' to datetime in format '{date_format}'.")
        #return []
    if isinstance(date, str):
        try:
            date = datetime.strptime(date, date_format)
        except ValueError as value_err:
            raise ValueError(f"Unable to parse date '{date}' to datetime in format '{date_format}'.")
                       # f" No sessions will be associated to this entry.")
            #return []

    time_in_date = date.time()

    sessions_associated = []
    for session, (start, end) in sessions.items():
        # handles midnight span cases
        if start > end:
            if time_in_date >= start or time_in_date < end:
                sessions_associated += [session]
        elif start < end:
            if start <= time_in_date < end:
                sessions_associated += [session]

    return sessions_associated

def underscore_format_table_name(table_name: str, table_suffix="table"):
    if not table_name:
        raise ValueError("Unable to underscore format table. No table name was provided")
        #return ""
    if type(table_name) != str:
        raise TypeError(f"Unable to underscore format table. Wrong table_name type '{type(table_name)}'")


    name_segments = table_name.lower().split(' ')
    underscored_name = '_'.join(segment for segment in name_segments if segment)

    if not underscored_name:
        return ""

    if name_segments[-1].lower() != table_suffix:
        underscored_name += f"_{table_suffix}"

    return underscored_name

def replace_occurrences(content: str, keyword: str, replacement: List):
    if not content or not keyword or not replacement:
        missing_data = "content" if not content else "keyword" if not keyword else replacement
        logger.warning(f"Unable to replace occurrences. No {missing_data} was provided.")
        return content

    if type(replacement) == list or type(replacement) == range:
        replacement = iter(replacement)
        try:
            result = re.sub(keyword, lambda _: str(next(replacement)), content)
            return result
        except Exception as exc:
            logger.warning(f"Unable to replace keywords in content: {exc}")
            return content
    elif type(replacement) == float or type(replacement) == int or type(replacement) == bool:
        replacement = str(replacement)

    try:
        result = re.sub(keyword, replacement, content)
    except Exception as exc:
        logger.warning(f"Unable to replace keywords in content: {exc}")
        return content

    return result

def get_month_start_end(date_str):
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        first_day = date.day
    except ValueError:
        try:
            date = datetime.strptime(date_str, "%Y-%m")
            first_day = 1
        except ValueError:
            raise ValueError(f"Unable to format date '{date_str}'")

    # first_day = date.replace(day=1)
    month_days_count = calendar.monthrange(date.year, date.month)[1]
    # last_day = date.replace(day=month_days_count)

    return date.replace(day=first_day), max(1, month_days_count - first_day)  #, [first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")]

def paginate_list(list, slice_size=1):
    if slice_size < 1:
        raise ValueError(f"Unable to paginate list: slice_size cannot be lower than 1 (value given: '{slice_size}')")

    return [list[pos:pos + slice_size] for pos in range(0, len(list), slice_size)]

def paginate_date(date, timeframe, pagination_size: int = DAYS_PAGINATION_SIZE) -> List[Tuple]:
    if timeframe not in TIMEFRAME_TO_DAYS_COUNT_MAP.keys():
        raise KeyError(f"Unable to paginate date. Timeframe '{timeframe}'"
                        f" not present in TIMEFRAME_TO_DAYS_COUNT_MAP keys")
    if pagination_size < 1:
        raise ValueError("Unable to paginate date. pagination_size cannot be lower than 1 "
                         f"(value given: {pagination_size}")
    date, day_count = TIMEFRAME_TO_DAYS_COUNT_MAP.get(timeframe)(date)

    if not date or not day_count:
        missing_data = "date" if not date else "day_count"
        raise ValueError(f"Unable to paginate date without a valid {missing_data}")

    if isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d")

    paginated_date = []
    len_days = date.day + day_count
    # TODO review if len_days or len_days -1 to ensure last day of week/month doesn't include the following one
    #  of next timeframe
    for day in range(date.day, len_days, pagination_size):
        paginated_date += [(
            date.replace(day=day).strftime("%Y-%m-%d"),
            min(pagination_size, (len_days - day))
        )]

    return paginated_date

def flatten_list(list_to_flatten, depth_level=1):
    if depth_level <= 0:
        return list_to_flatten
    flattened_list = []
    for l in list_to_flatten:
        flattened_list += flatten_list(l, depth_level - 1)

    return flattened_list

def validate_date_format(date_str, valid_date_formats=VALID_INPUT_DATE_FORMATS):
    if type(date_str) != str:
        raise TypeError(f"Unable to validate date format."
                        f" Value provided is of type '{type(date_str)}'")

    for date_format in valid_date_formats:
        try:
            datetime.strptime(date_str, date_format)
            return True
        except ValueError:
            continue

    return False
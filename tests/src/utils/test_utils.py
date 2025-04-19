import unittest
from datetime import time, datetime

from parameterized import parameterized
from src.utils.utils import format_ini_table_names, unpack_ini_list_value, unwrap_css_classes, remove_matched_elements, \
    extract_format_arguments, filter_nas_in_series, get_decimal_cases, date_difference, get_sessions_in_date, \
    underscore_format_table_name, replace_occurrences, get_month_start_end, paginate_list, paginate_date, flatten_list, \
    validate_date_format
import pandas as pd

class TestUtils(unittest.TestCase):

    def setUp(self):
        """self.timeframe_to_days_count_map = {
            "Daily": lambda date_str: (date_str, 1),
            "Weekly": lambda date_str: (date_str, 7),
            "Monthly": lambda date_str: get_month_start_end(date_str),
        }"""

        self.session_timezones = {
    # actual ? sydney 10 pm to 7 am
    "Sydney": (time(22, 0), time(8, 0)),
    # actual ? tokyo 12 am to 9 am
    "Tokyo": (time(0, 0), time(8, 0)),
    # actual ? london 8 am to 5 pm
    "London": (time(8, 0), time(17, 0)),
    # actual ? new york 1 pm to 10 pm
    "New York": (time(14, 30), time(20, 0)),
}


    @parameterized.expand([
        ("valid_test", ["test_name_table", "another_random_example"], True, ["Test Name", "Another Random Example"]),
        ("missing_table_names", [], False, ValueError),
        ("valid_test_with_edge_cases", ["test__name_table", "another_random_n_"], True, ["Test Name", "Another Random N"])
    ])
    def test_format_ini_table_names(self, _, underscored_names, is_valid, expected_result):
        if not is_valid:
            with self.assertRaises(expected_result):
                format_ini_table_names(underscored_names)
            return
        result = format_ini_table_names(underscored_names)
        self.assertEqual(len(underscored_names), len(expected_result))
        self.assertEqual(expected_result, result)

    @parameterized.expand([
        ("valid_test", "Test_1\nTest_2\nTest_3", True, ["Test_1", "Test_2", "Test_3"]),
        ("valid_test_with_edge_cases", "Test_1\n\nTest_2\nTest_3\n\n\n", True, ["Test_1", "Test_2", "Test_3"]),
        ("missing_list", "", False, ValueError),
    ])
    def test_unpack_ini_list_value(self, _, value_as_newline_list, is_valid, expected_result):
        if not is_valid:
            with self.assertRaises(expected_result):
                unpack_ini_list_value(value_as_newline_list)
            return

        result = unpack_ini_list_value(value_as_newline_list)
        self.assertEqual(expected_result, result)

    """    @parameterized.expand([
        ("valid_test", )
    ])
    @patch("src.utils.utils.unwrap_css_classes")
    def build_properties(self, _, default_properties, properties_requested, css_classes, is_valid, expected_result):
        if not is_valid:
            with self.assertRaises(expected_result):
                build_properties(default_properties, properties_requested, css_classes)
            return

        result = build_properties(default_properties, properties_requested, css_classes)
        self.assertEqual(expected_result, result)"""

    @parameterized.expand([
        ("valid_test", ["class_1", "class_2", "class_3"], True, "\n   - class_1\n   - class_2\n   - class_3"),
        ("valid_test_single_element", ["class_1"], True, "\n   - class_1"),
        ("empty_list", [], True, ""),
    ])
    def test_unwrap_css_classes(self, _, css_classes, is_valid, expected_result):
        if not is_valid:
            with self.assertRaises(expected_result):
                unwrap_css_classes(css_classes)
            return

        result = unwrap_css_classes(css_classes)
        self.assertEqual(expected_result, result)

    @parameterized.expand([
        ("valid_test_strings_1", ["this", "should", "very", "much", "work"], ["this", "should", "work"],
         True, ["very", "much"]),
        ("valid_test_strings_2", ["this", "should", "work"], ["this", "should", "work"],
         True, []),
        ("valid_test_strings_3", ["this", "should", "work"], ["very", "much"],
         True, ["this", "should", "work"]),
        ("valid_test_numbers_1", [1, 2, 3, 4], [3, 4],
         True, [1, 2]),
        ("valid_test_strings_and_numbers_1", ["this", "should", "work", 1, 2, 3], ["should", "work", 2, 3, 4],
         True, ["this", 1]),
    ])
    def test_remove_matched_elements(self, _, list1, list2, is_valid, expected_result):
        if not is_valid:
            with self.assertRaises(expected_result):
                remove_matched_elements(list1, list2)
            return

        result = remove_matched_elements(list1, list2)
        self.assertEqual(expected_result, result)

    @parameterized.expand([
        ("valid_test", "this {should} actually {work} quite well! I {hope}",
         True, ["should", "work", "hope"]),
        ("valid_test_empty", "",
         True, []),
        ("valid_test_no_format_words", "this should actually work quite well! I hope",
         True, []),
    ])
    def test_extract_format_arguments(self, _, format_string, is_valid, expected_result):
        if not is_valid:
            with self.assertRaises(expected_result):
                extract_format_arguments(format_string)
            return

        result = extract_format_arguments(format_string)
        self.assertEqual(expected_result, result)

    @parameterized.expand([
        ("valid_test_1", pd.Series([10, 20, '', 40, '', 60]), '',
         True,  pd.Series([10, 20, 40, 60])),
        ("valid_test_2", pd.Series([10, 20, pd.NA, 40, pd.NA, 60]), '',
         True, pd.Series([10, 20, 40, 60])),
        ("valid_test_3", pd.Series([10, 20, None, 40, None, 60]), None,
         True, pd.Series([10, 20, 40, 60])),
        ("valid_test_4", pd.Series([]), pd.NA,
         True, pd.Series([])),
    ])
    def test_filter_nas_in_series(self, _, series, empty_cell_value, is_valid, expected_result):
        if not is_valid:
            with self.assertRaises(expected_result):
                filter_nas_in_series(series, empty_cell_value)
            return

        result = filter_nas_in_series(series, empty_cell_value)
        self.assertEqual(result.to_list(), expected_result.to_list())

    @parameterized.expand([
        ("valid_test_1", 0.123, True, 3),
        ("valid_test_2", 0.1, True, 1),
        ("valid_test_3", 1, True, 0),
        ("valid_test_4", 2.45, True, 2),
        ("valid_test_5", "3.1", True, 1),
        ("valid_test_5", "3", True, 0),
        ("invalid_test_1", None, False, TypeError),
        ("invalid_test_2", ["2.45"], False, TypeError),
    ])
    def test_get_decimal_cases(self, _, number, is_valid, expected_result):
        if not is_valid:
            with self.assertRaises(expected_result):
                get_decimal_cases(number)
            return

        result = get_decimal_cases(number)
        self.assertEqual(expected_result, result)

    @parameterized.expand([
        ("valid_test_1", "2025-04-02 15:00:30", "2025-04-02 15:02:00", True, "1 minute and 30 seconds"),
        ("valid_test_2", "2025-04-02 15:01:00", "2025-04-02 15:02:00", True, "1 minute"),
        ("valid_test_3", "2025-04-02 15:30:30", "2025-04-02 16:35:50", True, "1 hour, 5 minutes and 20 seconds"),
        ("valid_test_4", "", "2025-04-02 15:02:00", True, ""),
        ("valid_test_5", "2025-04-02 15:00:30", None, True, ""),
        ("invalid_test_1_date_init_bigger", "2025-04-02 15:02:00", "2025-04-02 15:00:30", False, ValueError),
        ("invalid_test_2_bad_data_type", 123, [1, 2, 3], False, TypeError),
        ("invalid_test_3_unformattable_date", "2025-04", "2025", False, ValueError),
    ])
    def test_date_difference(self, _, date_init, date_end, is_valid, expected_result):
        if not is_valid:
            with self.assertRaises(expected_result):
                date_difference(date_init, date_end)
            return

        result = date_difference(date_init, date_end)
        self.assertEqual(expected_result, result)

    @parameterized.expand([
        ("valid_test_1", "2025-04-02 15:00:30", True, ["London", "New York"]),
        ("valid_test_2", "2025-04-02 21:00:00", True, []),
        ("valid_test_3", "2025-04-02 05:00:30", True, ["Sydney", "Tokyo"]),
        ("invalid_test_4", "2025-04", False, ValueError),
        ("invalid_test_5", "", False, ValueError),
    ])
    def test_get_sessions_in_date(self, _, date, is_valid, expected_result):
        if not is_valid:
            with self.assertRaises(expected_result):
                get_sessions_in_date(date, self.session_timezones)
            return

        result = get_sessions_in_date(date, self.session_timezones)
        self.assertEqual(expected_result, result)

    @parameterized.expand([
        ("valid_test_1", "should split this table", True, "should_split_this_table"),
        ("valid_test_2", "should split this", True, "should_split_this_table"),
        ("valid_test_3", "should split this  ", True, "should_split_this_table"),
        ("valid_test_3", "   ", True, ""),
        ("invalid_test_1", "", False, ValueError),
        ("invalid_test_2", None, False, ValueError),
        ("invalid_test_3", 123, False, TypeError),
    ])
    def test_underscore_format_table_name(self, _, table_name, is_valid, expected_result):
        if not is_valid:
            with self.assertRaises(expected_result):
                underscore_format_table_name(table_name)
            return

        result = underscore_format_table_name(table_name)
        self.assertEqual(expected_result, result)

    @parameterized.expand([
        ("valid_test_1", "this sentence should be replaced", "should be", "was",
         True, "this sentence was replaced"),
        ("valid_test_2", "this sentence should not have anything to replace", "whatever", "???",
         True, "this sentence should not have anything to replace"),
        ("valid_test_3", "this sentence this should this be this replaced", "this", "ah!",
         True, "ah! sentence ah! should ah! be ah! replaced"),
        ("valid_test_4", "", "this ", "ah!",
         True, ""),
        ("valid_test_5", "this sentence this should this be this replaced", "", "ah!",
         True, "this sentence this should this be this replaced"),
        ("valid_test_6", "this sentence this should this be this replaced", "this ", "",
         True, "this sentence this should this be this replaced"),
        ("valid_test_7", 123, "should be", "was",
         True, 123),
        ("valid_test_8", "this sentence should be replaced", 123, "was",
         True, "this sentence should be replaced"),
        ("valid_test_9", "this sentence should be replaced", "should be", 123,
         True, "this sentence 123 replaced"),
    ])
    def test_replace_occurrences(self, name, content, keyword, replacement, is_valid, expected_result):
        if not is_valid:
            with self.assertRaises(expected_result):
                replace_occurrences(content, keyword, replacement)
            return

        result = replace_occurrences(content, keyword, replacement)
        self.assertEqual(expected_result, result)


    @parameterized.expand([
        ("valid_test_1", "2025-01-05", True, (datetime.strptime("2025-01-05", "%Y-%m-%d"), 26)),
        ("valid_test_2", "2025-01-01", True, (datetime.strptime("2025-01-01", "%Y-%m-%d"), 30)),
        ("valid_test_3", "2025-01", True, (datetime.strptime("2025-01-01", "%Y-%m-%d"), 30)),
        ("invalid_test_4", "2025-02-28", True, (datetime.strptime("2025-02-28", "%Y-%m-%d"), 1)),
        ("invalid_test_1", "2025", False, ValueError),
        ("invalid_test_2", "2025-50", False, ValueError),
    ])
    def test_get_month_start_end(self, _, date_str, is_valid, expected_result):
        if not is_valid:
            with self.assertRaises(expected_result):
                get_month_start_end(date_str)
            return

        result = get_month_start_end(date_str)
        self.assertEqual(expected_result, result)

    @parameterized.expand([
        ("valid_test_1", [1] * 12, 4, True, [[1] * 4, [1] * 4, [1] * 4]),
        ("valid_test_2", [1] * 12, 5, True, [[1] * 5, [1] * 5, [1] * 2]),
        ("valid_test_3", [1] * 12, 7, True, [[1] * 7, [1] * 5]),
        ("valid_test_4", [], 4, True, []),
        ("invalid_test_1", [1] * 12, 0, False, ValueError),
    ])
    def test_paginate_list(self, _, list, slice_size, is_valid, expected_result):
        if not is_valid:
            with self.assertRaises(expected_result):
                paginate_list(list, slice_size)
            return

        result = paginate_list(list, slice_size)
        self.assertEqual(expected_result, result)

    @parameterized.expand([
        ("valid_test_monthly_1", "2025-01-21", "Monthly", 7,
         True, [("2025-01-21", 7), ("2025-01-28", 3)]),
        ("valid_test_monthly_2", "2025-01", "Monthly", 7,
         True, [("2025-01-01", 7), ("2025-01-08", 7), ("2025-01-15", 7),
                ("2025-01-22", 7), ("2025-01-29", 2)]),
        ("valid_test_weekly", "2025-01-21", "Weekly", 7,
         True, [("2025-01-21", 7)]),
        ("valid_test_daily", "2025-01-21", "Daily", 7,
         True, [("2025-01-21", 1)]),
        ("invalid_test_1", "2025-01-21", "Randomly", 7,
         False, KeyError),
        ("invalid_test_2", "2025-01-21", "Daily", -1,
         False, ValueError),
    ])
    def test_paginate_date(self, name, date, timeframe, pagination_size, is_valid, expected_result):
        if not is_valid:
            with self.assertRaises(expected_result):
                paginate_date(date, timeframe, pagination_size)
            return

        result = paginate_date(date, timeframe, pagination_size)
        self.assertEqual(expected_result, result)

    @parameterized.expand([
        ("valid_test_1", [[1,2,3], [4, 5, 6]], 1,
         True, [1, 2, 3, 4, 5, 6]),
        ("valid_test_2", [[[1, 2, 3]], [[4, 5, 6]]], 2,
         True, [1, 2, 3, 4, 5, 6]),
        ("valid_test_3", [[[[1, 2, 3]]], [[[4, 5, 6]]]], 3,
         True, [1, 2, 3, 4, 5, 6]),
        ("valid_test_4", [[1, 2, 3], [4, 5, 6]], -1,
         True, [[1, 2, 3], [4, 5, 6]]),
    ])
    def test_flatten_list(self, _, list_to_flatten, depth_level, is_valid, expected_result):
        if not is_valid:
            with self.assertRaises(expected_result):
                flatten_list(list_to_flatten, depth_level)
            return

        result = flatten_list(list_to_flatten, depth_level)
        self.assertEqual(expected_result, result)

    @parameterized.expand([
        ("valid_test", "2025-01-01", True, True),
        ("valid_test", "2025-01", True, True),
        ("valid_test", "2025-01-45", True, False),
        ("valid_test", "2025", True, False),
        ("valid_test", 2025, False, TypeError),
    ])
    def test_validate_date_format(self, _, date_str, is_valid, expected_result):
        if not is_valid:
            with self.assertRaises(expected_result):
                validate_date_format(date_str)
            return

        result = validate_date_format(date_str)
        self.assertEqual(expected_result, result)
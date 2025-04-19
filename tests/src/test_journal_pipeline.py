import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, MagicMock, AsyncMock, create_autospec

import pandas as pd

from src.journal_pipeline import JournalPipeline
import src.utils.config_vars as vars
from parameterized import parameterized
from src.config.config_loader import TOMLConfigLoader
from src.utils.config import Config
import asyncio

DEFAULT_PARAMS = {'api': {
            'Bybit': {'base_url': 'https://api-testnet.bybit.com', 'execution_list_endpoint': '/v5/execution/list',
                      'order_history_endpoint': '/v5/order/history', 'realtime_order_endpoint': 'v5/order/realtime',
                      'transaction_log_endpoint': '/v5/account/transaction-log'}, 'name': 'Bybit'}, 'journal_app': {
            'Obsidian': {'charts': [{'name': 'Performance', 'type': 'pie'}],
                         'compute_profits_by': 'Realized Profit',
                         'css_classes': ['wideTable', 'tradingSimplifiedBabyBlue'],
                         'display_order': ['links', 'charts', 'tables'],
                         'links': {'loss': 'Trading/Reports/Losses', 'win': 'Trading/Reports/Wins'},
                         'name': '{timeframe} Trade Recap - {date} {pnl}.md',
                         'other_properties': ['Timeframe', 'Exchange', 'Profitable', 'DateCreated', 'DateUpdated'],
                         'output_style': 'markdown', 'risk_threshold': 0.02,
                         'tables': [{'descriptions': True, 'name': 'Aggregated View', 'type': 'aggregated'}, {
                             'columns': ['Symbol', 'Action', 'Side', 'Entry Price', 'Entry Date', 'Realized Profit',
                                         'ROI(%)'], 'descriptions': False, 'name': 'Custom View', 'type': 'custom'},
                                    {'descriptions': False, 'name': 'Detailed View', 'type': 'detailed'}],
                         'tags': ['trading', 'journal', 'crypto'], 'timeframe': 'Daily', 'write_mode': 'overwrite'},
            'name': 'Obsidian'}, 'logging': {'log_dir': 'logs', 'log_level': 'info', 'log_to_file': True},}

class StubTOMLConfigLoader:
    def __init__(self, config_file_path=""):
        self.params = DEFAULT_PARAMS

class StubRequestHandler:
    def __init__(self, api_key: str = "", api_secret: str ="", *args, **kwargs):
        pass

    async def get_paginated_response(self, endpoint, additional_params, date, day_count, use_async):
        return [f"mock_data_{endpoint}_{date}_{day_count}"]

class TestJournalPipeline(IsolatedAsyncioTestCase):

    def setUp(self):
        ## set up a reusable mock params and JournalPipeline object

        self.params = DEFAULT_PARAMS

        # patch TOMLConfigLoader and logger
        toml_loader_patch = patch("src.journal_pipeline.TOMLConfigLoader")
        logger_patch = patch("src.journal_pipeline.logger")

        # start patches and store references to the mock objects
        self.mock_toml_loader = toml_loader_patch.start()
        self.mock_logger = logger_patch.start()

        # configure the mocked TOMLConfigLoader instance
        mock_toml_instance = MagicMock()
        mock_toml_instance.params = self.params
        self.mock_toml_loader.return_value = mock_toml_instance

        self.pipeline = JournalPipeline(
            config_file_path="config_path",
            start_date="2023-01-01",
            timeframe="daily",
            config_type=vars.TOML_CONFIG_TYPE
        )

        # cleanup for patches to stop after tests
        self.addCleanup(toml_loader_patch.stop)
        self.addCleanup(logger_patch.stop)

    @parameterized.expand([
        ("valid_test", "path/to/config.toml", "2025-01-01", "daily", "toml", True, None),
        ("empty_config_type", "path/to/config.toml", "2025-01-01", "daily", "", False, ValueError),
        ("empty_timeframe", "path/to/config.toml", "2025-01-01", "", "toml", False, ValueError),
        ("bad_timeframe", "path/to/config.toml", "2025-01-01", "randomly", "toml", False, ValueError),
        ("empty_date", "path/to/config.toml", "", "daily", "toml", False, ValueError),
        ("bad_date_format", "path/to/config.toml", "01-01-2025", "daily", "toml", False, ValueError),

    ])
    @patch("src.journal_pipeline.TOMLConfigLoader", return_value=StubTOMLConfigLoader())
    @patch("src.journal_pipeline.INIConfigLoader")
    #@patch("src.journal_pipeline.logger")
    def test_initialization_toml_config(self, name, config_path, date, timeframe, config_type,
                                        is_valid, expected_result, mock_ini_loader, mock_toml_loader):

        if not is_valid:
            with self.assertRaises(expected_result):
                JournalPipeline(
                    config_file_path=config_path,
                    start_date=date,
                    timeframe=timeframe,
                    config_type=config_type
                )
            return

        pipeline = JournalPipeline(
            config_file_path=config_path,
            start_date=date,
            timeframe=timeframe,
            config_type=config_type
        )

        class_attributes_to_validate = ["date", "timeframe", "exchange_api_name", "data_marshaller",
                                             "journal_app_name",
                                             "exchange_api_params", "journal_params", "logging_params",
                                             "profits_col_name",
                                             "endpoints"]
        class_attribute_type_map = {
            "date": str, "timeframe": str, "exchange_api_name": str, "journal_app_name": str,
            "exchange_api_params": dict, "journal_params": dict, "logging_params": dict, "profits_col_name": str,
            "endpoints": dict
        }

        self.assertEqual(pipeline.config.params, self.params)
        for attribute in class_attributes_to_validate:
            obj_attr = getattr(pipeline, attribute)
            obj_attr_expected_type = class_attribute_type_map.get(attribute)

            self.assertIsNotNone(obj_attr)
            if not obj_attr_expected_type:
                continue
            self.assertTrue(isinstance(obj_attr, obj_attr_expected_type))

    @parameterized.expand([
        ("async_call", True),
        ("sync_call", False),
    ])
    #@patch("src.logging.logger.Logger.error")
    @patch("src.journal_pipeline.urljoin")
    @patch("src.journal_pipeline.flatten_list")
    @patch("src.journal_pipeline.paginate_date")
    @patch("os.environ.get", return_value="")
    @patch("src.journal_pipeline.RequestHandler", side_effect=lambda *args, **kwargs: StubRequestHandler())
    @patch("src.journal_pipeline.asyncio.gather", new_callable=AsyncMock)
    async def test_fetch_data(self, _, use_async, mock_asyncio_gather, mock_request_handler,
                              mock_environ_get, mock_paginate_date, mock_flatten_list, mock_urljoin):
        mock_asyncio_gather.return_value = [("dataset1", ["data1"]), ("dataset2", ["data2"])]


        mock_paginate_date.side_effect = lambda date, tf: [('2025-01-01', 6), ('2025-01-07', 3)]
        mock_urljoin.side_effect = lambda url, endpoint: f"{url}.{endpoint}"
        mock_flatten_list.side_effect = lambda tasks: tasks

        data = await self.pipeline.fetch_data(use_async)

        self.assertEqual(data, {"dataset1": ["data1"], "dataset2": ["data2"]})

    @parameterized.expand([
        # incomplete (replicated) datasets
        ("valid_bybit_test", {
            "trades": [
                {'category': 'linear', 'currency': 'USDT', 'feeRate': '0.00055','qty': '1', 'side': 'Sell', 'size': '0',
                 'symbol': 'BTCUSDT','tradePrice': '78641.4','transactionTime': '1743978314474'}
            ],
            "transactions": [
                {'closedSize': '1', 'createType': 'CreateByStopLoss', 'execQty': '1',
                 'execTime': '1743978314474', 'leavesQty': '0', 'orderQty': '1', 'orderType': 'Market',
                 'side': 'Sell', 'stopOrderType': 'StopLoss', 'symbol': 'BTCUSDT'}
            ],
            "order_history": [
                {'createdTime': '1743977194209', 'orderStatus': 'Filled', 'orderType': 'Market', 'qty': '1',
                 'side': 'Sell', 'stopOrderType': 'StopLoss', 'symbol': 'BTCUSDT', 'takeProfit': '', 'tpslMode': 'Full',
                 'triggerBy': 'LastPrice', 'updatedTime': '1743978314479'}
            ],
        },
         {"trades": "transactionTime", "transactions": "execTime", "order_history": "createdTime"},
         True, None
         ),
        ("empty_dataset_map", {
            "trades": [
                {'category': 'linear', 'currency': 'USDT', 'feeRate': '0.00055', 'qty': '1', 'side': 'Sell',
                 'size': '0',
                 'symbol': 'BTCUSDT', 'tradePrice': '78641.4', 'transactionTime': '1743978314474'}
            ],
            "transactions": [
                {'closedSize': '1', 'createType': 'CreateByStopLoss', 'execQty': '1',
                 'execTime': '1743978314474', 'leavesQty': '0', 'orderQty': '1', 'orderType': 'Market',
                 'side': 'Sell', 'stopOrderType': 'StopLoss', 'symbol': 'BTCUSDT'}
            ],
            "order_history": [
                {'createdTime': '1743977194209', 'orderStatus': 'Filled', 'orderType': 'Market', 'qty': '1',
                 'side': 'Sell', 'stopOrderType': 'StopLoss', 'symbol': 'BTCUSDT', 'takeProfit': '', 'tpslMode': 'Full',
                 'triggerBy': 'LastPrice', 'updatedTime': '1743978314479'}
            ],
        },
         {},
         False, ValueError
         ),
        ("missing_dataset_types", {
            "transactions": [
                {'closedSize': '1', 'createType': 'CreateByStopLoss', 'execQty': '1',
                 'execTime': '1743978314474', 'leavesQty': '0', 'orderQty': '1', 'orderType': 'Market',
                 'side': 'Sell', 'stopOrderType': 'StopLoss', 'symbol': 'BTCUSDT'}
            ],
            "order_history": [
                {'createdTime': '1743977194209', 'orderStatus': 'Filled', 'orderType': 'Market', 'qty': '1',
                 'side': 'Sell', 'stopOrderType': 'StopLoss', 'symbol': 'BTCUSDT', 'takeProfit': '', 'tpslMode': 'Full',
                 'triggerBy': 'LastPrice', 'updatedTime': '1743978314479'}
            ],
        },
         {"trades": "transactionTime", "transactions": "execTime", "order_history": "createdTime"},
         False, KeyError
         ),
        ("missing_full_dataset", {},
         {"trades": "transactionTime", "transactions": "execTime", "order_history": "createdTime"},
         False, ValueError
         ),
    ])
    @patch("src.journal_pipeline.build_relevant_dataset")
    @patch("src.journal_pipeline.merge_datasets")
    @patch("src.journal_pipeline.filter_dataset")
    @patch("src.journal_pipeline.rename_dataset")
    @patch("src.journal_pipeline.astype_dataset")
    @patch("src.journal_pipeline.apply_kpis_to_dataset")
    @patch("src.journal_pipeline.build_high_level_stats")
    @patch("src.journal_pipeline.round_truncate_dataset")
    @patch("src.journal_pipeline.format_dataset")
    def test_build_data(self, _, dataset, dataset_map, is_valid, expected_result,
                        mock_build_relevant, mock_merge, mock_filter, mock_rename, mock_astype, mock_apply_kpis,
                        mock_build_stats, mock_round_truncate, mock_format):

        mocks_to_assert = [mock_build_relevant, mock_merge, mock_filter, mock_rename, mock_astype, mock_apply_kpis,
                        mock_build_stats, mock_round_truncate, mock_format]

        mock_build_relevant.side_effect = lambda data, *_: data
        mock_merge.side_effect = lambda df, df_to_merge, *_: df
        mock_filter.side_effect = lambda df, *_: df
        mock_rename.side_effect = lambda df, *_: df
        mock_astype.side_effect = lambda df, *_: df
        mock_apply_kpis.side_effect = lambda df, *_: (df, df)
        mock_build_stats.return_value = "stats"
        mock_round_truncate.side_effect = lambda df, *_: df
        mock_format.side_effect = lambda df, *_: df

        if not is_valid:
            with self.assertRaises(expected_result):
                self.pipeline.build_data(dataset, dataset_map)
            return

        args = self.pipeline.build_data(dataset, dataset_map)
        [mock.assert_called() for mock in mocks_to_assert]
        self.assertTrue(len(args) > 0)

    @parameterized.expand([
        ("full_valid_test",
         # dfs by type
         {
            "detailed": pd.DataFrame({
                "Symbol": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
                "Side": ["Long", "Short", "Long"],
                "Quantity": ["1", "10", "100"]
            }),
            "aggregated": pd.DataFrame({
                "Symbol": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
                "Side": ["Long", "Short", "Long"],
                "Quantity": ["1", "10", "100"]
            })
        },
         # template map
         {
             "Aggregated View": {
                 "type": "aggregated",
                 "columns": ["Symbol", "Side"]
             },
             "Detailed Analysis": {
                 "type": "detailed",
                 "columns": ["Symbol", "Quantity"]
             }
         },
         True, None),
        ("missing_template_map",
         # dfs by type
         {
             "detailed": pd.DataFrame({
                 "Symbol": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
                 "Side": ["Long", "Short", "Long"],
                 "Quantity": ["1", "10", "100"]
             }),
             "aggregated": pd.DataFrame({
                 "Symbol": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
                 "Side": ["Long", "Short", "Long"],
                 "Quantity": ["1", "10", "100"]
             })
         },
         # template map
         {
         },
         True, []),
        ("missing_table_data",
         # dfs by type
         {
         },
         # template map
         {
             "Aggregated View": {
                 "type": "aggregated",
                 "columns": ["Symbol", "Side"]
             },
             "Detailed Analysis": {
                 "type": "detailed",
                 "columns": ["Symbol", "Quantity"]
             }
         },
         True, []),
    ])
    #@patch("src.journal_pipeline.logger", return_value="")
    @patch("src.journal_pipeline.underscore_format_table_name")
    @patch("src.journal_pipeline.trim_fill_dataset")
    @patch("src.journal_pipeline.deepcopy")
    def test_format_tables(self, _, df_dict, table_template_map, is_valid, expected_result,
                           mock_deepcopy, mock_trimfill, mock_underscore_format):
        mock_deepcopy.side_effect = lambda dict_content: dict_content
        mock_underscore_format.side_effect = lambda table_name: table_name
        mock_trimfill.side_effect = lambda df, cols: df

        if not is_valid:
            with self.assertRaises(expected_result):
                self.pipeline.format_tables(df_dict, table_template_map)
            return

        dfs_to_journal = self.pipeline.format_tables(df_dict, table_template_map)
        keys_to_validate = ["title", "content", "descriptions"]
        self.assertIs(type(dfs_to_journal), list)

        if expected_result is not None:
            self.assertEqual(dfs_to_journal, expected_result)
        if dfs_to_journal:
            [self.assertTrue(key in df.keys()) for key in keys_to_validate for df in dfs_to_journal]


    """@parameterized.expand([
    ])
    @patch("src.journal_pipeline.trim_fill_data_ini")
    @patch("src.journal_pipeline.format_ini_table_names")
    @patch("src.journal_pipeline.unpack_ini_list_value")
    def test_trim_fill_data_ini(self, df_dict, table_template_map):"""

    @parameterized.expand([
        ("valid_test", {
        "wins": 8,
        "stopped_out": 4,
        "risk_managed": 6,
        "trades_by_asset": {"BTCUSDT": 6, "ETHUSDT": 3, "SOLUSDT": 3},
        "trades_by_session": {"New York": 9, "Tokyo": 3},
        "total_trades": 12,
        "pnl": 4.5,
        "profit_factor": 1.28
        },
         True, None
         ),
        ("missing_full_stats", {
        },
         True, {
            "pie": [],
            "line": [],
            "other": [],
        }
         ),
        ("missing_some_stats", {
            "risk_managed": 6,
            "trades_by_asset": {"BTCUSDT": 6, "ETHUSDT": 3, "SOLUSDT": 3},
            "trades_by_session": {"New York": 9, "Tokyo": 3},
            "total_trades": 12,
            "pnl": 4.5,
            "profit_factor": 1.28
        },
         True, None
         ),
        ("missing_total_trades", {
            "wins": 8,
            "stopped_out": 4,
            "risk_managed": 6,
            "trades_by_asset": {"BTCUSDT": 6, "ETHUSDT": 3, "SOLUSDT": 3},
            "trades_by_session": {"New York": 9, "Tokyo": 3},
            "pnl": 4.5,
            "profit_factor": 1.28
        },
         True, None
         ),
    ])
    def test_format_charts(self, _, stats, is_valid, expected_result):
        if not is_valid:
            with self.assertRaises(expected_result):
                self.pipeline.format_charts(stats, Config.JournalFormatter.PieChart.CHART_TEMPLATES)
            return
        charts = self.pipeline.format_charts(stats, Config.JournalFormatter.PieChart.CHART_TEMPLATES)
        self.assertTrue(type(charts) == dict)
        if expected_result is not None:
            self.assertEqual(charts, expected_result)

    @parameterized.expand([
        ("valid_test", "Journal Title", "Journal Content",
         True, None),
        ("missing_title", "", "Journal Content",
         False, ValueError),
        ("missing_content", "Journal Title", "",
         False, ValueError),
        ])
    @patch("os.environ.get", return_value="")
    @patch("src.journal_pipeline.FileWriter")
    def test_write_journal_to_file(self, _, title, content, is_valid, expected_result, mock_file_writer,
                                   mock_environ_get):

        if not is_valid:
            with self.assertRaises(expected_result):
                self.pipeline.write_journal_to_file(title, content)
            return
        self.pipeline.write_journal_to_file(title, content)

        mock_file_writer_instance = mock_file_writer.return_value
        mock_file_writer_instance.write_to_file.assert_called_once_with(
            content=content, file_name=title
        )
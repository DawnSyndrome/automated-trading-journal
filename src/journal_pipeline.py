import logging
from urllib.parse import urljoin
from src.api.request_handler import RequestHandler
from src.data.data_helpers import *
from src.file.journal_formatter import *
from src.utils.config import Config
from src.config.config_loader import INIConfigLoader, TOMLConfigLoader
from src.file.file_writer import FileWriter
from src.utils.utils import *
import src.utils.config_vars as vars
import os
import asyncio
from src.logging.logger import Logger

logger = Logger()

class JournalPipeline:

    def __init__(self,
                 config_file_path: str,
                 start_date: str,
                 timeframe: str,
                 config_type=vars.TOML_CONFIG_TYPE):

        if not config_type:
            raise ValueError(f"Invalid config type '{config_type}' was provided during app bootstrap."
                            " Please, provide one of the following "
                            "supported config types:"
                            f"{'\n'.join(f" - {config_type}" for config_type
                                         in vars.SUPPORTED_CONFIG_TYPES)}")

        if config_type == vars.INI_CONFIG_TYPE:
            self.config = INIConfigLoader(
                config_file_path=config_file_path
            )
        elif config_type == vars.TOML_CONFIG_TYPE:
            self.config = TOMLConfigLoader(
                config_file_path=config_file_path
            )
        else:
            raise ValueError(f"Invalid config type '{config_type}' provided."
                            " Please, provide one of the following "
                            "supported config types:"
                            f"{'\n'.join(f" - {config_type}" for config_type
                                         in vars.SUPPORTED_CONFIG_TYPES)}")

        if not validate_date_format(start_date, VALID_INPUT_DATE_FORMATS):
            raise ValueError(f"Invalid date format provided. Please, use one of the following formats:\n"
                             f"{'   - '.join(VALID_INPUT_DATE_FORMATS)}")
        self.date = start_date

        if timeframe not in vars.SUPPORTED_TIMEFRAMES:
            raise ValueError(f"Timeframe provided '{timeframe}' is invalida. Please choose one of the following"
                             f" timeframes:\n {'    - '.join(vars.SUPPORTED_TIMEFRAMES)}")
        self.timeframe = timeframe.capitalize()

        self.__load_params()
        self.__set_application_logger()

    def __load_params(self):
        self.exchange_api_name = self.config.params.get("api").get("name")
        self.data_marshaller = getattr(Config.DataMarshaller, self.exchange_api_name)
        self.journal_app_name = self.config.params.get("journal_app").get("name")

        #self.project_params = self.config.params.get("project")
        self.exchange_api_params  = self.config.params.get("api").get(self.exchange_api_name)
        self.journal_params  = self.config.params.get("journal_app").get(self.journal_app_name)
        self.logging_params = self.config.params.get("logging")

        risk_threshold = self.journal_params.get("risk_threshold")
        profits_col_name = self.journal_params.get("compute_profits_by")

        if not profits_col_name or profits_col_name.lower() not in {COL_NAME_REALIZED_PROFIT.lower(),
                                                                    COL_NAME_GROSS_PROFIT.lower()}:
            self.profits_col_name = COL_NAME_REALIZED_PROFIT
        else:
            self.profits_col_name = profits_col_name

        if risk_threshold:
            vars.RISK_THRESHOLD = float(risk_threshold)

        self.__build_endpoints_map()

    def __build_endpoints_map(self):
        endpoints_by_designation = {}
        endpoint_map = getattr(Config.DataMarshaller, self.exchange_api_name).ENDPOINT_TO_DATASET_TYPE_MAP
        for endpoint_label in vars.ENDPOINTS_TO_PROCESS:
            endpoint = self.exchange_api_params.get(endpoint_label)
            endpoints_by_designation[endpoint_map.get(endpoint_label)] = endpoint
        self.endpoints = endpoints_by_designation

    def __set_application_logger(self):
        logger.set_log_level(getattr(logging, self.logging_params.get("log_level").upper()))
        logger.set_file_handler(log_to_file=self.logging_params.get("log_to_file"),
                             log_dir=self.logging_params.get("log_dir"))

    async def fetch_data(self, use_async=True):
        try:
            base_url = self.exchange_api_params.get("base_url")
            paginated_date = paginate_date(self.date, self.timeframe)

            request_handler = RequestHandler(
                api_key=os.environ.get(vars.API_KEY),
                api_secret=os.environ.get(vars.API_SECRET),
            )

            async def gather_requests(dataset_type, endpoint):
                tasks = [
                    request_handler.get_paginated_response(
                        endpoint=urljoin(base_url, endpoint),
                        additional_params={},
                        date=date,
                        day_count=day_count,
                        use_async=use_async,
                    )
                    for date, day_count in paginated_date
                ]
                return dataset_type, flatten_list(await asyncio.gather(*tasks))

            tasks = [
                gather_requests(dataset_type, endpoint)
                for dataset_type, endpoint in self.endpoints.items()
            ]

            results = await asyncio.gather(*tasks)

            data_per_endpoint = {dataset_type: data for dataset_type, data in results}
            return data_per_endpoint

        except Exception as exc:
            raise Exception(f"Unable to fetch data: {exc}")

    def build_data(self, account_trade_data, dataset_map):
        if not account_trade_data or not dataset_map:
            missing_data = "account trade data" if not account_trade_data else "dataset map"
            raise ValueError(f"Unable to build the data: No {missing_data} was provided")

        # build
        datasets = {
                label: build_relevant_dataset(
                dataset,
                [],
                dataset_map.get(label)
            ) for label, dataset in account_trade_data.items()
        }

        # merge
        try:
            detailed_df = datasets[vars.TRADES_DATASET]
            for key in [vars.TRANSACTIONS_DATASET, vars.ORDER_HISTORY_DATASET]:
                detailed_df = merge_datasets(detailed_df, datasets[key], "outer", "orderId")
        except KeyError as key_err:
                raise KeyError(f"Unable to merge data due to missing key in dataset: {key_err}")

        # apply transformations
        transformations = [
            (filter_dataset, self.data_marshaller.DATAFRAME_COLUMN_FILTER_RULES,
             self.data_marshaller.DATAFRAME_ROW_FILTER_RULES),
            (rename_dataset, self.data_marshaller.DATAFRAME_NAME_MAPPING),
            (astype_dataset, Config.JournalFormatter.MarkDownTable.DATAFRAME_TYPING_RULES),
        ]
        for func, *args in transformations:
            detailed_df = func(detailed_df, *args)

        # apply KPIs
        kpi_map = Config.JournalFormatter.MarkDownTable.DATAFRAME_KPI_MAP
        detailed_df, aggregated_df = apply_kpis_to_dataset(detailed_df, kpi_map)

        # generate stats
        stats = build_high_level_stats(detailed_df, aggregated_df, self.profits_col_name)

        # apply rounding and formatting
        round_rules = Config.JournalFormatter.MarkDownTable.DATAFRAME_ROUND_RULES
        format_rules = Config.JournalFormatter.MarkDownTable.DATAFRAME_FORMAT_RULES.get(
            self.journal_params.get("output_style"))

        for func, rules in [(round_truncate_dataset, round_rules), (format_dataset, format_rules)]:
            detailed_df, aggregated_df = [func(df, rules) for df in [detailed_df, aggregated_df]]

        return detailed_df, aggregated_df, stats

    """def trim_fill_data_ini(self, df_dict, table_template_map):
        try:
            unformatted_table_names = list(
                unpack_ini_list_value(self.config.get_value(section="journal_app.obsidian", name="tables")))
            formatted_table_names = format_ini_table_names(unformatted_table_names)
            dfs_to_journal = []

            for unformatted_table_name, formatted_table_name in zip(unformatted_table_names, formatted_table_names):
                table_struct = table_template_map.get(formatted_table_name, None)

                if not table_struct:
                    # table name doesn't exist in our templates, hence check for a custom one in .ini file
                    unformatted_table_cols = self.config.get_value(section="journal_app.obsidian",
                                                              name=unformatted_table_name)
                    table_columns = unpack_ini_list_value(unformatted_table_cols)
                    # TODO allow user to choose which type to generate ?
                    # defaults to 'detailed' type
                    df_type = 'detailed'
                    if not table_columns:
                        print(f"Could not fetch columns for table '{unformatted_table_name} in .ini file'")
                        continue
                else:
                    table_columns = table_struct.get("columns")
                    df_type = table_struct.get("type")
                    if not table_columns:
                        print(f"Could not fetch columns for table '{formatted_table_name} in config.py file'")
                        continue
                    if not df_type:
                        print(f"Could not fetch type to generate for table '{formatted_table_name} in config.py file'")
                        continue

                df_copy = pd.DataFrame(deepcopy(df_dict.get(df_type).to_dict()))
                dfs_to_journal += [{
                    'title': formatted_table_name,
                    'content': trim_fill_dataset(df_copy, table_columns)
                }]

            return dfs_to_journal
        except Exception as exc:
            raise Exception(f"An error occurred while attempting to trim the data: {exc}")"""

    def format_tables(self, df_dict, table_template_map):
        dfs_to_journal = []
        if not df_dict or not table_template_map:
            missing_data = "table data" if not df_dict else "table columns map"
            logger.warning(f"No {missing_data} was provided to format tables. Skipping this step")

            return dfs_to_journal

        for table in self.journal_params.get("tables"):
            table_type = table.get("type")
            table_name = table.get("name")
            table_descriptions_enabled = table.get("descriptions", False)

            if table_type == "custom":
                table_columns = table.get("columns", [])

                if not table_columns:
                    # search for a custom table specified in the config based on it's name
                    underscored_table_name = underscore_format_table_name(table_name)
                    table_columns = self.journal_params.get(underscored_table_name, [])
                    """if not table_columns:
                        print(f"Unable to fetch any table columns associated with table name '{table_name}'."
                              f"Please make sure you specify them by naming it as '{underscored_table_name}' "
                              "in your target config file.")
                        continue"""
                #TODO do this in a different manner
                table_type = "detailed"
            else:
                table_columns = table_template_map.get(table_name, {}).get("columns", [])

            if not table_name:
                logger.warning(f"Table name is empty for table of type '{table_type}'. ")
            if not table_columns:
                logger.warning(f"Unable to parse any column names to associate with"
                               f" table '{table_name}' ({table_type})")

            df_data = df_dict.get(table_type).to_dict()
            if not df_data:
                logger.warning(f"Table data of type '{table_type}' is empty. Ignoring this table")
                continue

            df_copy = pd.DataFrame(deepcopy(df_data))
            dfs_to_journal += [{
                'title': table_name,
                'content': trim_fill_dataset(df_copy, table_columns),
                'descriptions': table_descriptions_enabled
            }]

        return dfs_to_journal

    def format_charts(self, stats, chart_template_map):
        charts = {
            "pie": [],
            "line": [],
            "other": [],
        }
        if not stats:
            logger.warning(f"No high level stats were provided to format charts. Skipping this step")
            return charts

        for chart in self.journal_params.get("charts"):
            chart_type = chart.get("type")
            chart_name = chart.get("name")

            if not chart_type or not chart_name:
                missing_data = "chart_type" if not chart_type else "chart_name"
                logger.warning(f"Unable to format chart: missing {missing_data}")
                continue
            if chart_type == "pie":
                try:
                    if chart_name in chart_template_map.keys():
                        charts["pie"] += [
                            (chart_name,
                             chart_template_map.get(chart_name)(stats),
                            Config.JournalFormatter.PieChart.TEMPLATE,
                            Config.JournalFormatter.PieChart.COLOR_SCHEMES.get(chart_name),
                             )
                        ]
                except (KeyError, TypeError) as err:
                    logger.warning(f"Unable to format chart '{chart_name}': {err}")
                    continue

            elif chart_type == "line":
                #TODO extend this feature
                continue
            else:
                #TODO extend this feature
                continue

        return charts

    def build_journal_content(self, dfs_to_journal, charts_to_journal, stats):
        try:
            display_order = self.journal_params.get("display_order")
            links = self.journal_params.get("links")
            journal_formatter = JournalFormatter(timeframe=self.timeframe, date=self.date,
                                                 exchange=self.exchange_api_name, pnl=stats.get("pnl"),
                                                 links=links, display_order=display_order,
                                                 format_style=self.journal_params.get("output_style"))

            journal_formatter.build_tables(dfs_to_journal)
            #TODO make this scalable for every chart
            journal_formatter.build_charts(charts_to_journal.get("pie"))

            #css_classes = unpack_ini_list_value(self.config.get_value(section="journal_app.obsidian", name="css_classes"))
            #properties_requested = unpack_ini_list_value(
            #    self.config.get_value(section="journal_app.obsidian", name="other_properties"))
            css_classes = self.journal_params.get("css_classes")
            properties_requested = self.journal_params.get("other_properties")
            journal_formatter.build_properties(css_classes, properties_requested)

            #tags = unpack_ini_list_value(self.config.get_value(section="journal_app.obsidian", name="tags"))
            tags = self.journal_params.get("tags")
            journal_formatter.build_tags(tags)

            unformatted_journal_title = self.journal_params.get("name")
            journal_title = journal_formatter.format_title(unformatted_journal_title)

            journal_content = journal_formatter.build_journal_ordered(Config.JournalFormatter.TEMPLATE)

            return journal_title, journal_content
        except Exception as exc:
            raise Exception(f"Unable to build journal content: {exc}")

    def write_journal_to_file(self, journal_title: str, journal_content: str):
        if not journal_title or not journal_content:
            missing_data = "journal title" if not journal_title else "journal content"
            raise ValueError(f"Unable to write journal: missing {missing_data}")

        file_writer = FileWriter(journal_dir=os.getenv("REPORTS_DIR"), timeframe_dir=self.timeframe)
        file_writer.write_to_file(content=journal_content, file_name=journal_title)

    def run(self):
        try:
            #1
            loop = asyncio.get_event_loop()
            if loop.is_running():
                raise RuntimeError("Cannot run the coroutine: event loop is already running.")
            acc_trade_data = loop.run_until_complete(self.fetch_data())
            #2
            detailed_df, aggregated_df, stats = self.build_data(
                acc_trade_data,
                getattr(Config.DataMarshaller, self.exchange_api_name).DATASET_TO_TRANSACTION_DATE_COL_MAP
            )
            #3
            dfs_to_journal = self.format_tables({"detailed": detailed_df, "aggregated": aggregated_df},
                                            Config.JournalFormatter.MarkDownTable.TABLE_TEMPLATES)
            #4
            charts_to_journal = self.format_charts(stats, Config.JournalFormatter.PieChart.CHART_TEMPLATES)
            #5
            journal_title, journal_content = self.build_journal_content(dfs_to_journal, charts_to_journal, stats)
            #6
            self.write_journal_to_file(journal_title, journal_content)
        except Exception as exc:
            logger.critical(f"Error caught while running the pipeline: {exc}")

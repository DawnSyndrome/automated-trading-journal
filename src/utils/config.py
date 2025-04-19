from src.utils.df_vars import *
from src.data.data_helpers import round_truncate_value, format_roi
from src.utils.session_vars import TRADE_SESSION_FORMAT_RULES
import pandas as pd
import src.utils.config_vars as vars

class Config:

    class DataMarshaller:
        class Bybit:
            RELEVANT_TRADE_PARAMS = ["symbol", "orderType", "stopOrderType", "execTime", "createType", "markPrice",
                                     "execPrice", "orderQty", "orderPrice", "closedSize", "execType", "side", "isMaker",
                                     "execFee", "execQty", "orderId", "execId"]

            ENDPOINT_TO_DATASET_TYPE_MAP = {
                vars.TRANSACTION_LOG_ENDPOINT_LABEL: vars.TRADES_DATASET,
                vars.EXECUTION_LIST_ENDPOINT_LABEL: vars.TRANSACTIONS_DATASET,
                vars.ORDER_HISTORY_ENDPOINT_LABEL: vars.ORDER_HISTORY_DATASET,
            }

            DATASET_TO_TRANSACTION_DATE_COL_MAP = {
                vars.TRADES_DATASET: "transactionTime",
                vars.TRANSACTIONS_DATASET: "execTime",
                vars.ORDER_HISTORY_DATASET: "createdTime",
            }

            DATAFRAME_COLUMN_FILTER_RULES = {
                # remove funding rate rows
                "execType": lambda value: value == 'Trade',
                "positionIdx": lambda value: ~pd.isna(value)
            }

            DATAFRAME_ROW_FILTER_RULES = [
                lambda row: row["tradeId"] == row["execId"]
            ]

            # TODO merge col_names that reference the same thing
            DATAFRAME_NAME_MAPPING = {
                "symbol": COL_NAME_SYMBOL,
                "orderAction": COL_NAME_ACTION,
                "side": COL_NAME_SIDE,
                "fee": COL_NAME_FEE,
                "feeRate": COL_NAME_FEE_RATE,
                "size": COL_NAME_REM_SIZE,
                "type": COL_NAME_TYPE,
                "execQty": COL_NAME_QUANTITY,
                "stopLoss": COL_NAME_STOP_LOSS,
                "takeProfit": COL_NAME_TAKE_PROFIT,
                "execPrice": COL_NAME_EXEC_PRICE,
                "execDate": COL_NAME_EXEC_DATE,
                "closedSize": COL_NAME_CLOSED_SIZE,
                "cashFlow": COL_NAME_GROSS_PROFIT,
                "change": COL_NAME_REALIZED_PROFIT,
                "cashBalance": COL_NAME_ACC_BALANCE,
            }

    class JournalFormatter:
        class MarkDownTable:
            DATAFRAME_KPI_MAP = {
            }

            DATAFRAME_TYPING_RULES = {
                COL_NAME_SYMBOL: str,
                COL_NAME_TYPE: str,
                COL_NAME_ACTION: str,
                COL_NAME_SIDE: str,
                COL_NAME_QUANTITY: float,
                COL_NAME_EXEC_PRICE: float,
                COL_NAME_GROSS_PROFIT: float,
                COL_NAME_REALIZED_PROFIT: float,
                COL_NAME_ACC_BALANCE: float,
                COL_NAME_FEE: float,
                COL_NAME_FEE_RATE: float,
                # COL_NAME_REM_SIZE: float,
                # '' or str number
                COL_NAME_CLOSED_SIZE: float,
                COL_NAME_IS_CLOSED: bool,
                COL_NAME_RISK_MANAGED: bool,
                COL_NAME_TRADE_STATUS: int,
                COL_NAME_SL_SET: float,
                COL_NAME_SL_TRIGGERED: float,
                COL_NAME_TAKE_PROFITS: str,
                COL_NAME_RISK_TAKEN: float,
                COL_NAME_RISK_TAKEN_PERCENT: str,
                }

            # change the round/truncate rules and/or decimal_cases here
            DATAFRAME_ROUND_RULES = {
                    COL_NAME_GROSS_PROFIT:
                        lambda value:
                        round_truncate_value(value, 2),
                    COL_NAME_REALIZED_PROFIT:
                        lambda value:
                        round_truncate_value(value, 2),
                    COL_NAME_ACC_BALANCE:
                        lambda value:
                        round_truncate_value(value, 2),
                    COL_NAME_ROI_PERCENT:
                        lambda value: format_roi(value, 2),
                    # COL_NAME_REM_SIZE: float,
                    # COL_NAME_CLOSED_SIZE:
                    #     lambda value:
                    #     round_truncate_value(value, 2),
                    # COL_NAME_RISK_TAKEN:
                    #     lambda value:
                    #     round_truncate_value(value, 2),
                }

            # your custom css into markdown rules
            # If you're using css snippets on Obsidian, you can reference the class
            # you're using and as long as that snippet is enabled, the css will be properly applied
            #TODO CLEAN UP THESE LAMBDAS INTO SEGREGATED, EASIER TO READ FUNCTIONS
            DATAFRAME_FORMAT_RULES = {
                "markdown": {
                    COL_NAME_SYMBOL: lambda value: f"**{value}**",
                    COL_NAME_TYPE: lambda value: value,
                    COL_NAME_ACTION:
                        lambda value: f'<span style="color: red;">{value}<span/>' if value == 'Stop Loss'
                        else f'<span style="color: green;">{value}<span/>' if value == 'Take Profit' else value,
                    COL_NAME_SIDE:
                        lambda value: f'<span style="color: red; font-weight: bold;">{value}<span/>' if value == 'Short'
                        else f'<span style="color: green; font-weight: bold;">{value}<span/>' if value == 'Long' else value,
                    COL_NAME_QUANTITY: lambda value: value,
                    COL_NAME_EXEC_PRICE: lambda value: value,
                    COL_NAME_EXEC_DATE: lambda value: f"_{value}_" if value else '',
                    COL_NAME_EXIT_PRICE: lambda value: value,
                    COL_NAME_CLOSED_DATE: lambda value: f"_{value}_" if value else '',
                    COL_NAME_TRADE_DURATION: lambda value: f"*{value}*" if value else '',
                    COL_NAME_GROSS_PROFIT:
                        lambda value: f'<span style="color: red;">{value}<span/>' if float(value) < 0.0
                        else f'<span style="color: green;">+{value}<span/>' if float(value) > 0.0 else value,
                    COL_NAME_REALIZED_PROFIT:
                        lambda value: f'<span style="color: red;">{value}<span/>' if float(value) < 0.0
                        else f'<span style="color: green;">+{value}<span/>' if float(value) > 0.0 else value,
                    COL_NAME_ACC_BALANCE: lambda value: value,
                    COL_NAME_ROI_PERCENT: lambda value: f'<span style="color: green;">{value}<span/>' if value[0] == '+' else
                    f'<span style="color: red;">{value}<span/>' if value[0] == '-' else value,
                    COL_NAME_IS_CLOSED: lambda value: '<center><input type="checkbox" checked><center/>' if value == True
                    else '<center><input type="checkbox"><center/>',
                    COL_NAME_RISK_MANAGED: lambda value: '<center><input type="checkbox" checked><center/>' if value == True
                    else '<center><input type="checkbox"><center/>',
                    COL_NAME_TRADE_STATUS: lambda value: '<span class="tag-win">Win</span>' if value == 1
                    else '<span class="tag-loss">Loss</span>' if value == -1 else '',
                    COL_NAME_RISK_TAKEN: lambda value: '' if pd.isna(value)
                    else f'<span style="color: green;">{round(value * 100, 2)}%<span/>' if value <= vars.RISK_THRESHOLD
                    else f'<span style="color: red;">{round(value * 100, 2)}%<span/>',
                    COL_NAME_STOPPED_OUT: lambda value: '<center><input type="checkbox" checked><center/>' if value == True
                    else '<center><input type="checkbox"><center/>',
                    COL_NAME_SL_SET: lambda value: value if not pd.isna(value) else '<span style="color: red;">None<span/>',
                    COL_NAME_SL_TRIGGERED: lambda value: value if not pd.isna(value) else 'None',
                    COL_NAME_TRADE_SESSION: lambda values: ''.join([TRADE_SESSION_FORMAT_RULES.get(value, '')
                                                                     for value in list(values)]) if values else '',
                    COL_NAME_TAKE_PROFITS: lambda value: f'<span style="color: red;">None<span/>' if not value else value
                },
                "html": {
                }
            }

            TABLE_TEMPLATES = {
                "Aggregated View": {
                    # type of table to generate
                    "type": "aggregated",
                    "columns": [
                        COL_NAME_SYMBOL,
                        COL_NAME_SIDE,
                        COL_NAME_IS_CLOSED,
                        COL_NAME_STOPPED_OUT,
                        COL_NAME_RISK_MANAGED,
                        COL_NAME_TRADE_STATUS,
                        COL_NAME_QUANTITY,
                        COL_NAME_TRADE_SESSION,
                        COL_NAME_EXEC_PRICE,
                        COL_NAME_EXEC_DATE,
                        COL_NAME_EXIT_PRICE,
                        COL_NAME_CLOSED_DATE,
                        COL_NAME_TRADE_DURATION,
                        COL_NAME_SL_SET,
                        COL_NAME_SL_TRIGGERED,
                        COL_NAME_TAKE_PROFITS,
                        COL_NAME_RISK_TAKEN,
                        COL_NAME_GROSS_PROFIT,
                        COL_NAME_REALIZED_PROFIT,
                        COL_NAME_ATTACHMENTS,
                        COL_NAME_CONFLUENCE,
                        COL_NAME_REMARKS
                    ]
                },
                "Detailed Analysis": {
                    "type": "detailed",
                    "columns": [
                    COL_NAME_SYMBOL,
                    COL_NAME_TYPE,
                    COL_NAME_ACTION,
                    COL_NAME_SIDE,
                    COL_NAME_QUANTITY,
                    COL_NAME_EXEC_PRICE,
                    COL_NAME_EXEC_DATE,
                    COL_NAME_GROSS_PROFIT,
                    COL_NAME_REALIZED_PROFIT,
                    COL_NAME_ACC_BALANCE,
                    COL_NAME_ROI_PERCENT,
                    COL_NAME_CONFLUENCE,
                    COL_NAME_REMARKS
                    ]
                },
                "Detailed View": {
                    "type": "detailed",
                    "columns": [
                        COL_NAME_SYMBOL,
                        COL_NAME_TYPE,
                        COL_NAME_ACTION,
                        COL_NAME_SIDE,
                        COL_NAME_QUANTITY,
                        COL_NAME_EXEC_PRICE,
                        COL_NAME_EXEC_DATE,
                        COL_NAME_GROSS_PROFIT,
                        COL_NAME_REALIZED_PROFIT,
                        COL_NAME_ACC_BALANCE,
                        COL_NAME_ROI_PERCENT,
                        COL_NAME_CONFLUENCE,
                        COL_NAME_REMARKS
                    ]
                }
            }

        class PieChart:
            CHART_TEMPLATES = {
                "Performance": lambda stats: [
                    ("Wins", stats.get("wins")),
                    ("Losses", (stats.get("total_trades") - stats.get("wins"))
                    if stats.get("total_trades") > 0
                       and stats.get("total_trades") >= stats.get("wins") else 0)
                ],
                "Win Ratio": lambda stats: [
                    ("Wins", stats.get("wins")),
                    ("Losses", (stats.get("total_trades") - stats.get("wins"))
                    if stats.get("total_trades") > 0
                       and stats.get("total_trades") >= stats.get("wins") else 0)
                ],
                "Stopped Out": lambda stats: [
                    ("Stopped Out", stats.get("stopped_out")),
                    ("Not Stopped", (stats.get("total_trades") - stats.get("stopped_out"))
                    if stats.get("total_trades") > 0
                       and stats.get("total_trades") >= stats.get("stopped_out") else 0)
                ],
                "Risk Management": lambda stats: [
                    ("Managed", stats.get("risk_managed")),
                    ("Not Managed", (stats.get("total_trades") - stats.get("risk_managed"))
                    if stats.get("total_trades") > 0
                       and stats.get("total_trades") >= stats.get("risk_managed") else 0)
                ],
                "Trades By Session": lambda stats: [
                    tuple([session, trade_count]) for session, trade_count
                    in stats.get("trades_by_session").items()
                ],
                "Trades By Asset": lambda stats: [
                    tuple([pair, trade_count]) for pair, trade_count
                    in stats.get("trades_by_asset").items()
                ],
            }

            #mermaid themeVariables pie order is applied from first to last, to the highest to least quantified label!
            # It does NOT respect the order of the template, unfortunately!
            TEMPLATE = {"markdown": '''```mermaid
%%{{init: {{'themeVariables': {theme_vars_dict}}}}}%%
pie title {chart_title}
{label_to_value_map}
```
''',
                        "html": ''''''
                        }

            COLOR_SCHEMES = {
                "Performance": {
                    "Wins": "#36A2EB",
                    "Losses": "#89CFF0",
                },
                "Win Ratio": {
                    "Wins": "#36A2EB",
                    "Losses": "#89CFF0",
                },
                "Stopped Out": {
                    "Stopped Out": "#89CFF0",
                    "Not Stopped": "#36A2EB",
                },
                "Risk Management": {
                    "Managed": "#36A2EB",
                    "Not Managed": "#89CFF0",
                },
                "Trades By Session": {
                    # change to red
                    "Sydney": "#FF0000",
                    # change to orange
                    "Tokyo": "#FFA500",
                    # change to green
                    "London": "#90EE90",
                    # change to purple
                    "New York": "#4a12cc",
                },
                "Trades By Asset": {
                     ### BTC / L1'S

                # orange
                "BTCUSD": "#FFA500",
                # orange
                "BTCUSDT": "#FFA500",
                # orange
                "BTCPERP": "#FFA500",
                # blue
                "ETHUSDT": "#0000FF",
                # sligth purple
                "SOLUSDT": "#4a12cc",
                # dark grey
                "XRPUSDT": "#A9A9A9",
                # dark blue
                "ADAUSDT": "#00008B",
                # subtle blue
                "LINKUSDT": "#36A2EB",
                # grey
                "XLMUSDT": "#808080",
                # baby blue
                "SUIUSDT": "#36A2EB",
                # red
                "AVAXUSDT": "#FF0000",
                # light green
                "NEARUSDT": "#90EE90",

                ### MEMECOINS

                # light orange
                "DOGEUSDT": "#deb485",
                # fiery orange
                "SHIBAUSDT": "#b5400e",
                # green
                "PEPEUSDT": "#008000",

                # grey
                "Default": "#808080",
                },
            }

        # table content is already properly generated and doesn't need templating

        TEMPLATE = {"markdown": '''{properties}

{content}

> [!NOTE] Other Details

{tags}

{footer}
''',
                    "html": '''''',
                    }
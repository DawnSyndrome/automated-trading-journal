from src.utils.df_vars import *

SORTABLE_CONTENT = ["links", "charts", "tables"]
LINKABLE_CONTENT = ["links", "charts", "tables"]

LINK_ID_KEYWORD = "{link_id}"
TABLE_TITLE_KEYWORD = "{table_title}"

LINK_FORMATS = {
    "links": f"_(Links[^{LINK_ID_KEYWORD}])_",
    "tables": f"_(Column Descriptions [^{LINK_ID_KEYWORD}])_",

}

FOOTER_FORMATS = {
    "links": f"[^{LINK_ID_KEYWORD}]: **Links to:**",
    "tables": f"[^{LINK_ID_KEYWORD}]: **{TABLE_TITLE_KEYWORD} - Column Descriptions:**",
}

# paragraph leading between elements. 1 = default, content right below, 2 = 1 empty line, 3 = 2, etc.
LINE_PARAGRAPH_SIZE = {
    "content": 1,
    "footer": 2,
}

COLUMN_DESCRIPTIONS = {
    COL_NAME_SYMBOL: "The trading pair associated with the trade",
    COL_NAME_TYPE: "The type of trade taken (_Short_ or _Long_)",
    COL_NAME_ACTION: "Action performed (New Order, Stop Loss or Take Profit triggered)",
    COL_NAME_SIDE: "Side (Short or Long) of the action taken",
    COL_NAME_FEE: "Fee cost amount associated with the trade/action taken",
    COL_NAME_FEE_RATE: "Fee rate (%) associated with trade/action total value",
    COL_NAME_REM_SIZE: "The trade's remaining size (if ongoing, otherwise will be 0)",
    COL_NAME_QUANTITY: "The total accumulated size of a trade throughout it's _Duration_",
    COL_NAME_STOP_LOSS: "Stop Loss price set when the trade was taken",
    COL_NAME_TAKE_PROFIT: "Take Profit price set when the trade was taken",
    COL_NAME_EXEC_PRICE: " The initial entry price level of a trade. It only averages multiple compounds as"
                         " long as there weren't _Take Profits_ in between",
    COL_NAME_EXEC_DATE: "Date of the first entry for a given trade's _Side_ and _Symbol_ (until closed)",
    COL_NAME_CLOSED_SIZE: "Size/amount closed (when a Take Profit/Stop Loss gets triggered)",
    COL_NAME_GROSS_PROFIT: "Overall profit from the trade without accounting for funding nor trading fees",
    COL_NAME_REALIZED_PROFIT: "Overall profit realized from the trade including funding rates and trading"
                              " fees associated with open and close orders",
    COL_NAME_ACC_BALANCE: "Total account balance at the time of the trade/action taken",
    COL_NAME_ROI: "Realized amount associated with the trade/action taken",
    COL_NAME_ROI_PERCENT: "Realized return in percentual terms",
    COL_NAME_ATTACHMENTS: "Attachments to provide additional context/confluence on why a trade/action was taken",
    COL_NAME_CONFLUENCE: "Confluence reasoning as to why a trade/action was taken",
    COL_NAME_REMARKS: "An explanation as to why a trade/action was taken",
    COL_NAME_SL_SET: "The initial/pre-set _Stop Loss_ when the trade was executed",
    COL_NAME_TP_SET: "The initial/pre-set _Take Profit_ when the trade was executed",
    COL_NAME_SL_TRIGGERED: "Final price at which the trade was stopped out at (can differ from _SL Set_)",
    COL_NAME_STOPPED_OUT: "Whether a given trade has hit it's _Stop Loss_ or not",
    COL_NAME_EXIT_PRICE: "The average price between all _Take Profits_ and _Stop Loss_ taken until a trade is"
                         " fully closed (also takes into account each closed _Quantity_)",
    COL_NAME_TAKE_PROFITS: "All price levels at which profits/partial closes were taken from a running trade",
    COL_NAME_IS_CLOSED: "Whether a given trade has been fully closed or not",
    COL_NAME_CLOSED_DATE: "Date at which the trade was fully closed",
    COL_NAME_TRADE_STATUS: "Whether a closed or ongoing trade is a Win or a Loss, based on the trade's"
                           " total _Gross Profit_",
    COL_NAME_RISK_TAKEN: "The overall % account balance at risk if the trade were to/got stopped out",
    COL_NAME_RISK_TAKEN_PERCENT: "Risk taken is percentual terms",
    COL_NAME_RISK_MANAGED: "Whether a trade's _Stop Loss_ respected the account's chosen Risk threshold",
    COL_NAME_TRADE_DURATION: "How long (in days, hours and seconds) a trade has been active for. If it's"
                             " still ongoing, duration will be set to the time diference between the"
                             " _Entry Date_ and now",
    COL_NAME_TRADE_SESSION: "The Trading Sessions(s) during which a trade was executed",
}
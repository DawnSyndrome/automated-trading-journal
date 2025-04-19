import pandas as pd
from src.utils.df_vars import *
from src.utils.utils import filter_nas_in_series, get_decimal_cases, date_difference, get_sessions_in_date
import src.utils.config_vars as vars
from datetime import datetime

### custom functions to apply on dataframe ###

def get_filtered_rows_by_action(group, col_name: str, action_type: str):
    return group[col_name] == action_type


# return entry price, entry date and decimal cases to be used for other computations
# entry value calculations can be done in 2 ways: "first" entry or "avg/average". Default to "first
def get_relevant_entry_values(group, rows_filter, price_col: str, date_col: str, entry_calc_type="first"):
    if group[rows_filter].empty:
        return pd.NA, '', 0

    price_entries = group.loc[rows_filter, price_col]
    if entry_calc_type == "first":
        entry_price = float(price_entries.iloc[0])
    else:
        # specify "avg/average" if more alternatives get added
        entry_price = price_entries.astype(float).mean()
    decimal_cases = get_decimal_cases(entry_price)
    entry_date = group.loc[rows_filter, date_col].min()

    return entry_price, entry_date, decimal_cases

# closed KPIs can currently be calculated in 2 different ways: "first" row or "avg" of closed rows
def calculate_closed_kpis(group, new_rows_filter, closed_rows_filter, close_type_colname: str, close_calc_type="first"):
    if group[new_rows_filter].empty:
        return pd.NA, pd.NA, 0.0

    preset_close_orders = filter_nas_in_series(group.loc[new_rows_filter, close_type_colname])

    if preset_close_orders.empty:
        preset_close_order = pd.NA
        #return pd.NA, pd.NA, 0.0
    else:
        # can be a TP or SL close
        if close_calc_type == "first":
            preset_close_order = float(preset_close_orders.iloc[0])
        else:
            preset_close_order = preset_close_orders.astype(float).mean() if not preset_close_orders.empty else pd.NA

        if group[closed_rows_filter].empty:
            preset_close_order = pd.NA
            #return preset_close_order, pd.NA, 0.0

    # total closed size from a close type (SL or TP)
    closed_size = group.loc[closed_rows_filter][COL_NAME_CLOSED_SIZE].sum()
    # order that fully closed the position
    fully_closed_filter = group.loc[closed_rows_filter][COL_NAME_REM_SIZE].astype(float) == 0.0
    fully_closed_row = group.loc[closed_rows_filter][fully_closed_filter]
    fully_closed_price = float(fully_closed_row.iloc[0][COL_NAME_EXEC_PRICE]) if not fully_closed_row.empty else pd.NA

    return preset_close_order, fully_closed_price, closed_size

def calculate_average_weighted_exit(group, closed_rows_filter, total_closed_size, decimal_cases=2):
    return round(((group.loc[closed_rows_filter][COL_NAME_CLOSED_SIZE].astype(float) / total_closed_size) *
                                     group.loc[closed_rows_filter][COL_NAME_EXEC_PRICE] if total_closed_size > 0.0 else
                                     (group.loc[closed_rows_filter][COL_NAME_CLOSED_SIZE].astype(float) / 1) *
                                     group.loc[closed_rows_filter][COL_NAME_EXEC_PRICE].astype(float)).sum(), decimal_cases)

# to process for each order group
# data MUST be date asc sorted!
def process_group(group, relevant_colnames=AGGREGATED_VIEW_USABLE_COLUMNS):
    try:
        # set the first row's values as default
        result = group.iloc[0].copy()

        new_order_rows, stop_loss_rows, take_profit_rows = [get_filtered_rows_by_action(group, COL_NAME_ACTION, action)
                                                            for action in [
                                                                NEW_ORDER_ACTION_LABEL,
                                                                STOP_LOSS_ACTION_LABEL,
                                                                TAKE_PROFIT_ACTION_LABEL
                                                            ]]
        entry_price, entry_date, decimal_cases = get_relevant_entry_values(group, new_order_rows,
                                                                           COL_NAME_EXEC_PRICE, COL_NAME_EXEC_DATE)
        sessions = get_sessions_in_date(entry_date)
        trade_quantity = group.loc[new_order_rows, COL_NAME_QUANTITY].fillna(0.0).sum()
        gross_profit = round(group[COL_NAME_GROSS_PROFIT].fillna(0.0).sum(), 2)
        realized_profit = round(group[COL_NAME_REALIZED_PROFIT].fillna(0.0).sum(), 2)

        preset_sl, fully_closed_sl_price, sls_closed_size = calculate_closed_kpis(group, new_order_rows, stop_loss_rows, COL_NAME_STOP_LOSS)
        preset_tp, fully_closed_tp_price, tps_closed_size = calculate_closed_kpis(group, new_order_rows, take_profit_rows, COL_NAME_TAKE_PROFIT)
        total_closed_size = sls_closed_size + tps_closed_size

        avg_sl_weighted, avg_tp_weighted = [
            calculate_average_weighted_exit(group, filter_row, total_closed_size, decimal_cases)
            for filter_row in [stop_loss_rows, take_profit_rows]
        ]

        avg_exit_price = (avg_sl_weighted + avg_tp_weighted) if (avg_sl_weighted + avg_tp_weighted) > 0.0 else ''
        tps = filter_nas_in_series(group.loc[take_profit_rows, COL_NAME_EXEC_PRICE])
        tps_taken = ' / '.join(f"{str(tp)}" for tp in list(tps)) if not tps.empty else ''
        is_closed = False if trade_quantity > total_closed_size else True
        # even though there can be row with equal datetime, the last row in the dataframe will always represent the
        # trade close time as long as is_close == true
        closed_date = group.iloc[-1][COL_NAME_EXEC_DATE] if is_closed else ''
        trade_duration = date_difference(entry_date, closed_date) if closed_date else date_difference(entry_date, datetime.now())
        # TODO allow user to choose whether trade_result is defined by realized_profit or gross_profit returns
        #trade_result = WIN_RESULT_LABEL if gross_profit > 0.0 else LOSS_RESULT_LABEL if gross_profit < 0.0 else ''
        #trade_result = current_result if abs(trade_quantity - float(group.iloc[-1][COL_NAME_REM_SIZE])) > 0.0 else ONGOING_RESULT_LABEL
        trade_result = 1 if gross_profit > 0.0 else -1 if gross_profit < 0.0 else 0
        init_acc_balance = float(result[COL_NAME_ACC_BALANCE])
        stopped_out = True if not pd.isna(fully_closed_sl_price) else False
        risk_managed = False
        risk = pd.NA
        # sl_to_compare_risk = fully_closed_sl_price if not pd.isna(fully_closed_sl_price) else preset_sl
        sl_to_compare_risk = preset_sl if not pd.isna(preset_sl) else\
            fully_closed_sl_price if not pd.isna(fully_closed_sl_price) else pd.NA

        if pd.isna(preset_sl) and trade_result == 1:
            risk = pd.NA
        else:
            if not pd.isna(sl_to_compare_risk):
                risk = abs(round((abs(entry_price - sl_to_compare_risk) * trade_quantity) / init_acc_balance, 2))
                if risk <= vars.RISK_THRESHOLD:
                    risk_managed = True

        """if not pd.isna(sl_to_compare_risk):
            risk = abs(round((abs(entry_price - sl_to_compare_risk) * trade_quantity) / init_acc_balance, 2))
            if risk < vars.RISK_THRESHOLD:
                risk_managed = True"""

        result_attributions = {
            COL_NAME_EXEC_PRICE: entry_price,
            COL_NAME_EXEC_DATE: entry_date,
            COL_NAME_QUANTITY: trade_quantity,
            COL_NAME_GROSS_PROFIT: gross_profit,
            COL_NAME_REALIZED_PROFIT: realized_profit,
            COL_NAME_SL_SET: preset_sl,
            COL_NAME_SL_TRIGGERED: fully_closed_sl_price,
            COL_NAME_EXIT_PRICE: avg_exit_price,
            COL_NAME_TP_SET: preset_tp,
            COL_NAME_TAKE_PROFITS: tps_taken,
            COL_NAME_IS_CLOSED: is_closed,
            COL_NAME_CLOSED_DATE: closed_date,
            COL_NAME_TRADE_DURATION: trade_duration,
            COL_NAME_TRADE_STATUS: trade_result,
            COL_NAME_RISK_TAKEN: risk,
            #result[COL_NAME_RISK_TAKEN_PERCENT] = f"{round(risk * 100, 2)}%" if not pd.isna(risk) else ""
            COL_NAME_RISK_MANAGED: risk_managed,
            COL_NAME_STOPPED_OUT: stopped_out,
            COL_NAME_TRADE_SESSION: sessions
        }

        aggregated_kpis = pd.Series(result_attributions)
        # overwrite existing columns
        result.update(aggregated_kpis)
        # append new indices
        merged = pd.concat([result, aggregated_kpis[~aggregated_kpis.index.isin(result.index)]])
        # trim df to contain only 'usable' columns for this type of dataframe
        return merged[AGGREGATED_VIEW_USABLE_COLUMNS]
    except Exception as exc:
        print(f"Unable to process KPIs for one of the order groups in the dataframe: {exc}")

def round_truncate_value(value, decimal_cases=2):
    trunc_format = f'%.{decimal_cases}f'
    return round(float(trunc_format % (value)), decimal_cases)

def format_roi(value, decimal_cases=2):
    formatted_value = round_truncate_value(value, decimal_cases)
    return f"{formatted_value}%" if formatted_value < 0 else f"+{formatted_value}%"

# df function to apply
def set_order_action(row):
    if row['createType'] == 'CreateByClosing':
        if row['cashFlow'] > 0.0:
            return "Take Profit"
        else:
            return "Stop Loss"
        #TODO validate for stop losses in profit
    elif row['createType'] == 'CreateByStopLoss':
        return "Stop Loss"
    elif row['createType'] == 'CreateByUser':
        return "New Order"
    else:
        return "Unknown"

# builds roi while finding any potential account top up / withdrawals that could interfere with future kpis
def calculate_roi(row, previous_balance, profit_colname = "Realized Profit", acc_balance_colname = "Wallet Balance"):
    if pd.isna(previous_balance[row.name]):
        roi = - 100 + ((row[profit_colname] + row[acc_balance_colname]) * 100.0) / row[acc_balance_colname]
        return roi

    return (row[profit_colname] * 100.0) / previous_balance[row.name]

def apply_format(row, format_map):
    for colname, custom_func in format_map.items():
        row[colname] = custom_func(row[colname])
    return row

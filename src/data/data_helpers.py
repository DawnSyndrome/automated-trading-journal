from copy import deepcopy
import json
from src.data.custom_df_functions import *
from src.data.kpi_functions import (build_roi, get_win_trades, get_win_trades_by_group, build_acc_pnl,
                                    build_profit_factor, build_trade_group_identifiers, get_stopped_out_count,
                                    get_risk_managed_count, get_trades_by_asset_count, get_trades_by_session_count)
from src.utils.utils import remove_matched_elements
from src.data.decorators import with_preemptive_function, get_matches_in_map
from src.utils.df_vars import COL_NAME_EXEC_DATE
from src.utils.config_vars import DEFAULT_DATE_FORMAT

def filter_content(account_stats, relevant_params, transaction_time_col_name):
    relevant_content = []

    for stat in account_stats:
        stat_content = {}
        if relevant_params:
            for param in relevant_params:
                stat_content[param] = stat.get(param, None)
        else:
            stat_content = deepcopy(stat)

        if stat_content.get(transaction_time_col_name):
            stat_content["execDate"] = (datetime.fromtimestamp(int(stat_content[transaction_time_col_name]) / 1000).
                                         strftime(DEFAULT_DATE_FORMAT))
        relevant_content.append(stat_content)

    return relevant_content

def build_dataframe_data(trades_content):
    if not trades_content:
        return

    trades_df = pd.DataFrame(trades_content)
    #sorted_df = trades_df.sort_values(by=["execDate"], ascending=True)

    return trades_df

def build_relevant_dataset(account_data, relevant_params, transaction_time_col_name): # which can be trades or transaction log data
    if account_data:
        account_stats = filter_content(account_data, relevant_params, transaction_time_col_name)
        print(json.dumps(account_stats, indent=4))
        stats_df = build_dataframe_data(account_stats)

        return stats_df
    else:
        print("No trades found for the given date.")

def merge_datasets(df1, df2, merge_type, merge_col):
    cols_to_use = list(df2.columns.difference(df1.columns)) + [merge_col]
    merged_df = pd.merge(df1, df2[cols_to_use], how=merge_type, on=merge_col)
    return merged_df

def trim_fill_dataset(df, columns_to_keep, default_type: str = 'string'):
    # if there's columns to keep that do not exist in the dataframe,
    # we create an empty column and set it a default data type
    columns_to_add = remove_matched_elements(columns_to_keep, list(df.columns.values))
    columns_to_filter = remove_matched_elements(columns_to_keep, columns_to_add)
    trimmed_df = df[columns_to_filter]

    trimmed_df = trimmed_df.assign(**{col: pd.Series(dtype=default_type) for col in columns_to_add})

    return trimmed_df

#1
@with_preemptive_function(get_matches_in_map)
def filter_dataset(df, filter_map_in_df, filter_row_list):
    # column level filters

    # combine filter conditions dynamically
    condition = pd.Series(True, index=df.index)  # start with all True
    for col, func in filter_map_in_df.items():
        condition &= df[col].apply(func)
    filtered_df = df.loc[condition]

    # row level filters
    filtered_df = filtered_df[filtered_df.apply(lambda row: all(custom_func(row) for custom_func in filter_row_list), axis=1)]

    # rows that did not match the filtering rule
    # edges cases are usually automatically removed positions (a tp from a trade that got stopped out or vice versa)
    # or duplicate anomalies (that in that case, won't have an exec and trade id)
    #edge_cases = filtered_df[~filtered_df.apply(lambda row: all(custom_func(row) for custom_func in filter_row_list), axis=1)]

    filtered_df["cashFlow"] = pd.to_numeric(filtered_df["cashFlow"])
    filtered_df["orderAction"] = filtered_df.apply(set_order_action, axis=1)
    filtered_df["side"] = filtered_df["side"].map({"Buy": "Long", "Sell": "Short"})
    # sort dataset by date
    filtered_df["execDate"] = pd.to_datetime(df['execDate'], format=DEFAULT_DATE_FORMAT)
    filtered_df = filtered_df.sort_values(by=["execDate"], ascending=True)

    return filtered_df


#2
@with_preemptive_function(get_matches_in_map)
def rename_dataset(df, rename_map_in_df):
    # rename the cols into journal table format
    return df.rename(columns=rename_map_in_df)

#3
@with_preemptive_function(get_matches_in_map)
def astype_dataset(df, typing_map_in_df):
    # set columns to proper data types based on the typing map provided
    # if they're not in the typing map, they will be set to 'default_type'
    # df = df.astype(typing_map)
    default_type = str
    df = df.astype({col: typing_map_in_df.get(col, default_type) for col in df.columns})
    df[COL_NAME_EXEC_DATE] = pd.to_datetime(df[COL_NAME_EXEC_DATE])

    return df

#4
@with_preemptive_function(get_matches_in_map)
def apply_kpis_to_dataset(df, kpi_map={}):
    # adds the ROI(%) column
    identified_pos_df = build_trade_group_identifiers(
        pd.DataFrame(deepcopy(df.to_dict())))
    identified_pos_df = identified_pos_df[identified_pos_df['Trade Group'] != -1]

    # filter invalid trades (TP/SLs without an associated New Order)

    detailed_df = build_roi(identified_pos_df)
    # wins, total_trades = build_win_trades(detailed_df)
    # pnl = build_acc_pnl(detailed_df)
    # profit_factor = build_profit_factor(detailed_df)

    aggregated_df = pd.DataFrame(deepcopy(detailed_df.to_dict()))
    aggregated_df[COL_NAME_TRADE_SESSION] = pd.Series(dtype=object)
    aggregated_df = identified_pos_df.groupby('Trade Group').apply(process_group).reset_index(drop=True)

    return detailed_df, aggregated_df #, wins, total_trades, pnl, profit_factor

#5
@with_preemptive_function(get_matches_in_map)
def round_truncate_dataset(df, round_map_in_df):
    return df.apply(lambda row: apply_format(row, round_map_in_df), axis=1)

#6
@with_preemptive_function(get_matches_in_map)
def format_dataset(df, format_map_in_df):
    return df.apply(lambda row: apply_format(row, format_map_in_df), axis=1)

def build_high_level_stats(detailed_df, aggregated_df, profits_col_name):
    wins, total_trades = get_win_trades(aggregated_df, profits_col_name)
    stopped_out_count = get_stopped_out_count(aggregated_df)
    risk_managed_count = get_risk_managed_count(aggregated_df)
    trades_by_asset = get_trades_by_asset_count(aggregated_df)
    trades_by_session = get_trades_by_session_count(aggregated_df)

    pnl = build_acc_pnl(detailed_df, profits_col_name)
    profit_factor = build_profit_factor(detailed_df, profits_col_name)

    return {
        "wins": wins,
        "stopped_out": stopped_out_count,
        "risk_managed": risk_managed_count,
        "trades_by_asset": trades_by_asset,
        "trades_by_session": trades_by_session,
        "total_trades": total_trades,
        "pnl": pnl,
        "profit_factor": profit_factor
    }
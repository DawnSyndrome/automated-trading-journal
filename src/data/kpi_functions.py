from src.data.custom_df_functions import calculate_roi
import pandas as pd
from src.utils.config import COL_NAME_CLOSED_SIZE, COL_NAME_SYMBOL, COL_NAME_ACTION, COL_NAME_SIDE, COL_NAME_QUANTITY
from src.utils.df_vars import COL_NAME_ROI_PERCENT, COL_NAME_ACC_BALANCE, COL_NAME_REALIZED_PROFIT, \
    COL_NAME_TRADE_STATUS, COL_NAME_STOPPED_OUT, COL_NAME_RISK_MANAGED, COL_NAME_TRADE_SESSION
from collections import Counter

def get_win_trades_by_group(id_groupped_df, pnl_col_to_sum=COL_NAME_REALIZED_PROFIT):
    trade_results = id_groupped_df.groupby('Trade Group')[pnl_col_to_sum].sum()
    total_trades = trade_results.notnull().sum()
    winning_trades = (trade_results > 0.0).sum()
    #win_ratio = round((winning_trades / total_trades) * 100, 2) if total_trades > 0.0 else 0.0

    return winning_trades, total_trades

def get_win_trades(df, pnl_col_to_sum=COL_NAME_REALIZED_PROFIT):
    winning_trades = len(df[df[pnl_col_to_sum] > 0.0])
    total_trades = len(df[df[COL_NAME_TRADE_STATUS].notna()])

    return winning_trades, total_trades

def get_stopped_out_count(df):
    return len(df[df[COL_NAME_STOPPED_OUT] == True])

def get_risk_managed_count(df, column_name=COL_NAME_RISK_MANAGED):
    return len(df[df[column_name] == True])

def get_trades_by_asset_count(df, column_name=COL_NAME_SYMBOL):
    return df.groupby(column_name).size().to_dict()

def get_trades_by_session_count(df, column_name=COL_NAME_TRADE_SESSION):
    flattened_items = [item for sublist in df[column_name].dropna() for item in sublist]
    session_counts = Counter(flattened_items)

    return dict(session_counts)

def build_roi(df):
    #df['ROI'] = df["Wallet Balance"].astype(float).diff().fillna(0.0)
    previous_balance = df[COL_NAME_ACC_BALANCE].shift(1)
    #df['ROI(%)'] = df.apply(lambda row:
    #                        ((row["Realized Profit"] * 100.0) / previous_balance[row.name])
    #                        if previous_balance[row.name] else 0.0, axis=1).fillna(0.0)

    df[COL_NAME_ROI_PERCENT] = df.apply(lambda row: calculate_roi(row, previous_balance), axis=1)
    return df

def build_acc_pnl(df, profit_col_name = COL_NAME_REALIZED_PROFIT,
                  init_balance_colname = COL_NAME_ACC_BALANCE):
    if df.empty:
        raise Exception("The dataframe provided is empty. Unable to compute account's total PnL")

    initial_balance = df[COL_NAME_ACC_BALANCE].iloc[0]
    if pd.isna(initial_balance):
        raise Exception(f"The initial wallet balance must be a valid number. Found '{str(initial_balance)}' instead")

    #return float((df[net_profit_colname].sum() / initial_balance) * 100.0)
    return round(float(df[profit_col_name].sum()), 2)

def build_profit_factor(df, profit_colname=COL_NAME_REALIZED_PROFIT, decimal_cases=2):
    if df.empty:
        raise Exception("The dataframe provided is empty. Unable to compute account's total PnL")

    total_profits = df[profit_colname][df[profit_colname] >= 0.0].sum()
    total_losses =  df[profit_colname][df[profit_colname] < 0.0].sum()

    return round((total_profits / total_losses), decimal_cases) * -1.0

"""
{
    "BTCUSDT": {
        "Long": {
            "remaining_quantity": ...,
            "group": ...,
        }
    }
}
"""

def build_trade_group_identifiers(df):
    trade_group = 0
    invalid_group = -1

    open_positions = {}
    trade_groups = []
    for _, row in df.iterrows():
        symbol = row[COL_NAME_SYMBOL]
        action = row[COL_NAME_ACTION]
        side = row[COL_NAME_SIDE]
        quantity = row[COL_NAME_QUANTITY]

        open_pos_on_symbol = open_positions.get(symbol)
        if open_pos_on_symbol is None:
            open_positions[symbol] = {}
            open_pos_on_symbol = open_positions[symbol]

        if action == 'New Order':
            if side not in open_pos_on_symbol.keys():
                # no open position for that  side found, therefore
                # sets new group identifier
                trade_group += 1
                # adds new group id to the list
                trade_groups += [trade_group]
                # new dict item for a new trade entry
                new_order_data = {
                    side: {
                        "group": trade_group,
                        "remaining_quantity": quantity
                    }
                }
                open_positions[symbol] |= new_order_data
                continue

            open_pos_on_symbol[side]['remaining_quantity'] += quantity
            trade_groups += [open_pos_on_symbol[side]['group']]
            continue

        elif action in ['Take Profit', 'Stop Loss']:
            side_to_deduct = "Short" if side == "Long" else "Long" if side == "Short" else "Invalid"
            if side_to_deduct in open_pos_on_symbol.keys():
                # an ongoing trade exists to TP/SL from
                open_pos_on_symbol[side_to_deduct]['remaining_quantity'] -= float(row[COL_NAME_CLOSED_SIZE]) #quantity
                trade_groups += [open_pos_on_symbol[side_to_deduct]['group']]
                if open_pos_on_symbol[side_to_deduct]['remaining_quantity'] == 0.0:
                    open_pos_on_symbol.pop(side_to_deduct)
                continue
        # found a take profit / stop loss without a matching trade (potentially belongs to a different dataset, pass
        # or an invalid trade
        trade_groups += [invalid_group]

    df['Trade Group'] = trade_groups
    return df
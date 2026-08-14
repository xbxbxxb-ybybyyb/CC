import numpy as np
import pandas as pd
factor_name = 'qyh_sat_1mtick_20240229_1'#
def factor_qyh_sat_1mtick_20240229_1(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx'] # 挂买金额
    #
    tick_df1 = tick_df.head(int(len(tick_df)/2)) if len(tick_df) > 10 else tick_df # 前一半时间，如果太短取全部
    tick_df2 = tick_df.tail(int(len(tick_df)/2)) if len(tick_df) > 10 else tick_df # 后一半时间，如果太短取全部
    tick_df1['factor'] = (tick_df1['buy_amt']) / (tick_df1['ValueTrade'].sum()+1) # 除以对应时间段成交总额
    tick_df2['factor'] = (tick_df2['buy_amt']) / (tick_df2['ValueTrade'].sum()+1)
    res = tick_df1['factor'].mean() - tick_df2['factor'].mean()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)


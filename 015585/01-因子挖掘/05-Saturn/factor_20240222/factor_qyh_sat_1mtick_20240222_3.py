import numpy as np
import pandas as pd
# dtj
# 931挂买总额平衡极端值后的离散程度
# 20，-0.064，-0.072
factor_name = 'qyh_sat_1mtick_20240222_3'#
def factor_qyh_sat_1mtick_20240222_3(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['factor'] = tick_df['WeightedAvgBidPx'] * tick_df['TotalBidQty'] # 挂买总额
    tick_df['factor'] = tick_df['factor'] + tick_df['factor'].min() # 平衡极端值
    res = tick_df['factor'].max() / tick_df['factor'].mean()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)


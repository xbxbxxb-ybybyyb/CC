import numpy as np
import pandas as pd
# dtj
# 16.8,0.054,0.059
# 买1量的diff/成交量的标准差
factor_name = 'qyh_sat_1mtick_20240222_7'#
def factor_qyh_sat_1mtick_20240222_7(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['factor'] = (tick_df['Buy1OrderQty'] - tick_df['Buy1OrderQty'].shift(1)) / tick_df['VolumeTrade']
    tick_df1 = tick_df.head(int(len(tick_df)/2)) if len(tick_df) > 10 else tick_df # 前一半时间，如果太短取全部
    res1 = tick_df1['factor'].std()
    factor_dict = {factor_name: res1}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)


import numpy as np
import pandas as pd
# dtj
# 前一半时间买1价对应涨跌幅的集中度
# 17，-0.052，-0.062
factor_name = 'qyh_sat_1mtick_20240222_5'#
def factor_qyh_sat_1mtick_20240222_5(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df.head(int(len(tick_df)/2)) if len(tick_df) > 10 else tick_df # 前一半时间，如果太短取全部
    tick_df['factor'] = tick_df['Buy1Price']/(tick_df['pre_close'])
    if zcz:# 考虑预处理？
        tick_df['factor'] = (tick_df['factor'] - 1) /2 + 1
    res = (tick_df['factor']**2).sum() / (tick_df['factor'].sum())**2
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)


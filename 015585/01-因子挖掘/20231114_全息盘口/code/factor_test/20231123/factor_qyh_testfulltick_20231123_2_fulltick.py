import numpy as np
import pandas as pd
# zcz，dtj
# LastPx/vwap的tail
# fulltick：-0.09,45
factor_name = 'qyh_testfulltick_20231123_2_fulltick'#
def factor_qyh_testfulltick_20231123_2_fulltick(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    pre_close = tick_df['pre_close'].values[0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    # tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    # tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df[tick_df['TotalVolumeTrade'] > 0]
    tick_df['vwap'] = tick_df['TotalValueTrade'] / tick_df['TotalVolumeTrade']
    if zcz:
        tick_df['LastPx'] = ((tick_df['LastPx']/pre_close -1)/2 + 1)*pre_close
        tick_df['vwap'] = ((tick_df['vwap']/pre_close -1)/2 + 1)*pre_close
    tick_df['factor'] = tick_df['LastPx'] / tick_df['vwap']
    res = tick_df['factor'].tail(1).mean()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
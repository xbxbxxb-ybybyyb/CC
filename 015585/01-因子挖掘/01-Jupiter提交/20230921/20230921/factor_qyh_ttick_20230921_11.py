import numpy as np
import pandas as pd

factor_name = 'qyh_ttick_20230921_11'#
def factor_qyh_ttick_20230921_11(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0.066}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = tick_df['pre_close'].values[0]
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['vwap'] = tick_df['TotalValueTrade'] / tick_df['TotalVolumeTrade']
    if zcz:
        tick_df['vwap'] = ((tick_df['vwap']/pre_close - 1)/2 + 1) * pre_close
        tick_df['LastPx'] = ((tick_df['LastPx'] / pre_close - 1) / 2 + 1) * pre_close
    tick_df['v2p'] = tick_df['vwap'] / tick_df['LastPx']
    if len(tick_df)>1:
        res1 = tick_df.head(int(len(tick_df)/2))['v2p'].tail(1).values[0]
        res2 = tick_df.tail(1)['v2p'].values[0]
        res = res1-res2
    else:
        res = np.nan
    #
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

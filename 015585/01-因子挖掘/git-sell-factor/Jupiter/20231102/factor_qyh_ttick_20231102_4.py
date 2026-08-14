import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_20231102_4'#
def factor_qyh_ttick_20231102_4(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    pre_close = tick_df['pre_close'].values[0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]  # 选择连续竞价阶段的tick数据
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df1 = tick_df.head(int(len(tick_df)/2))
    tick_df2 = tick_df.tail(int(len(tick_df)/2))
    tick_df1['vwap'] = tick_df1['ValueTrade'].cumsum() / (tick_df1['VolumeTrade'].cumsum() + 1)
    tick_df2['vwap'] = tick_df2['ValueTrade'].cumsum() / (tick_df2['VolumeTrade'].cumsum() + 1)
    if zcz:
        tick_df1['vwap'] = (((tick_df1['vwap'])/pre_close-1)/2+1)*pre_close
        tick_df2['vwap'] = (((tick_df2['vwap'])/pre_close-1)/2+1)*pre_close
        tick_df1['LastPx'] = (((tick_df1['LastPx']) / pre_close - 1) / 2 + 1) * pre_close
        tick_df2['LastPx'] = (((tick_df2['LastPx']) / pre_close - 1) / 2 + 1) * pre_close
    tick_df1['factor'] = tick_df1['vwap']/tick_df1['LastPx']
    tick_df2['factor'] = tick_df2['vwap']/tick_df2['LastPx']
    #
    res1 = tick_df1['factor'].min()
    res2 = tick_df2['factor'].min()
    factor_dict = {factor_name: res1-res2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)



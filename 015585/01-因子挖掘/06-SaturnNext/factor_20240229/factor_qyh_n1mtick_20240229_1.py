# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj,zcz
# 19,-0.062,-0.079
# 最新价/最高价/成交量在活跃/不活跃时候的标准差的差异
def factor_qyh_n1mtick_20240229_1(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20240229_1'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    import decimal
    def round_(x, n=0):
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre = tick_df['pre_close'].values[0]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['VolumeTrade'].apply(lambda x : round_(x,5))
    tick_df['ValueTrade'] = tick_df['ValueTrade'].apply(lambda x : round_(x,5))
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df[tick_df['VolumeTrade'] > 0]
    if zcz:
        tick_df['LastPx'] = ((tick_df['LastPx'] /  tick_df['pre_close'] - 1)/2 + 1)* tick_df['pre_close']
        tick_df['HighPx'] = ((tick_df['HighPx'] / tick_df['pre_close'] - 1) / 2 + 1) * tick_df['pre_close']
    tick_df['factor'] = (tick_df['LastPx'] / tick_df['HighPx']+1e-5) / (tick_df['VolumeTrade']+1e-5)
    #
    tick_df1 = tick_df[tick_df['ValueTrade'] >= tick_df['ValueTrade'].quantile(0.75)]
    tick_df2 = tick_df[tick_df['ValueTrade'] <= tick_df['ValueTrade'].quantile(0.25)]
    tick_df1 = tick_df1.tail(int(len(tick_df1)/2)) if len(tick_df1)>5 else tick_df1
    tick_df2 = tick_df2.tail(int(len(tick_df2)/2)) if len(tick_df2)>5 else tick_df2
    res = tick_df1['factor'].std() - tick_df2['factor'].std()

    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
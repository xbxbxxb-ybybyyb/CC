import numpy as np
import pandas as pd
# dtj
# 涨跌幅*成交量的集中度
factor_name = 'qyh_sat_lztick_20240321_4'#
def factor_qyh_sat_lztick_20240321_4(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    import decimal
    def round_(x, n=0):
        x = x + 1e-10
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    tick_df['ValueTrade'] = (tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)).apply(lambda x : round_(x,5))
    tick_df['VolumeTrade'] = (tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)).apply(lambda x : round_(x,5))
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df[tick_df['MDTime'] < 145700000]
    tick_df = tick_df[tick_df['VolumeTrade'] > 0]
    tick_df['factor'] = (tick_df['LastPx']/tick_df['pre_close']-1) * tick_df['VolumeTrade']
    # tick_df['tradep'] = tick_df['ValueTrade'] / tick_df['VolumeTrade']
    if zcz:
        tick_df['factor'] = (tick_df['factor'])/2
    #
    def f_calc_cct(tick_series):
        if abs(tick_series.sum()) > 0.001:
            return (tick_series ** 2).sum() / (tick_series.sum()) ** 2
        else:
            return np.nan

    res = f_calc_cct(tick_df['factor'])
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)


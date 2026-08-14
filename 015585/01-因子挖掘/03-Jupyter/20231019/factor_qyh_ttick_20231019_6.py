import numpy as np
import pandas as pd
# zcz,dtj
# 买均在中间时间段的值
# 52,0.116
# xly_t_trti_pq33:53
factor_name = 'qyh_ttick_20231019_6'#
def factor_qyh_ttick_20231019_6(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -12}
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
    pre_close = tick_df['pre_close'].values[0]
    tick_df = tick_df[tick_df['MDTime']>=93000000]
    tick_df['factor'] = (tick_df['WeightedAvgBidPx'])/pre_close-1
    if zcz:
        tick_df['factor'] = tick_df['factor']/2
    tick_df1 = tick_df.iloc[int(len(tick_df)/2):int(len(tick_df)/4*3)]
    res1 = tick_df1['factor'].mean() / (tick_df1['factor'].std()+0.001)
    #
    factor_dict = {factor_name: res1}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

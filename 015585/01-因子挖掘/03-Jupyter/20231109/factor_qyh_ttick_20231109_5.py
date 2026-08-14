import numpy as np
import pandas as pd
# zcz,dtj
# 开盘5min和末尾5min价格差的比例
# 0.098,36
#
factor_name = 'qyh_ttick_20231109_5'#
def factor_qyh_ttick_20231109_5(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.06}
    import decimal
    def round_(x, n=0):
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
#
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    pre_close = tick_df['pre_close'].values[0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df = tick_df[tick_df['MDTime']>=93000000]
    tick_df['factor'] = tick_df['LastPx']/pre_close - 1
    if zcz:
        tick_df['factor'] = tick_df['factor']/2
    tick_df1 = tick_df.head(100)
    tick_df2 = tick_df.tail(100)
    #
    res1 = tick_df1['factor'].head(1).mean() - tick_df1['factor'].tail(1).mean()
    res2 = tick_df2['factor'].head(1).mean() - tick_df2['factor'].tail(1).mean()
    #
    res = res1 / res2 if round_(abs(res2),5)>0 else np.nan
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
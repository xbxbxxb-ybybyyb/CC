import numpy as np
import pandas as pd
# zcz,dtj
# 集合竞价和开盘后买1价格的min差异
# 67,-0.13
# qyh_ttick_apct_a2b_1m:64
factor_name = 'qyh_ttick_20231109_5'#
def factor_qyh_ttick_20231109_5(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1.002}
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
    pre_close = tick_df['pre_close'].values[0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df1 = tick_df[(tick_df['MDTime'] < 93000000)]
    tick_df1 = tick_df1.tail(int(len(tick_df1)/2)) if len(tick_df1)> 10 else tick_df1
    tick_df1['factor'] = tick_df1['Buy1Price']/pre_close
    if zcz:
        tick_df1['factor'] = (((tick_df1['factor']-1)/2)+1)*pre_close
    res1 = tick_df1[tick_df1['factor']>0]['factor'].min()
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]  #
    tick_df = tick_df.tail(int(len(tick_df)/2)) if len(tick_df)>10 else tick_df
    tick_df['factor'] = tick_df['Buy1Price']/pre_close
    if zcz:
        tick_df['factor'] = (((tick_df['factor']-1)/2)+1)*pre_close
    res2 = tick_df['factor'].min()
    #
    res = res1 / res2 if res2 > 0 else np.nan
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
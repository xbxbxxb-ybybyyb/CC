import numpy as np
import pandas as pd
# dtj,zcz
# 买10.1分位数
# 50,0.113
# 0.092 36
# wj_TTick_b20_pctinfo3:50
factor_name = 'qyh_ttick_20231116_2'#
def factor_qyh_ttick_20231116_2(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1.016}
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
    tick_df = tick_df[tick_df['MDTime']>=93000000]
    if zcz:
        tick_df['factor'] = ((tick_df['Buy1Price']/pre_close-1)/2+1)
    else:
        tick_df['factor'] = tick_df['Buy1Price'] / pre_close
    res = tick_df['factor'].quantile(0.1)
    if len(tick_df)<60:
        res = 0.997
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
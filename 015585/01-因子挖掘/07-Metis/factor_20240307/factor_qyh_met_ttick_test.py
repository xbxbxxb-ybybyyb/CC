import numpy as np
import pandas as pd
factor_name = 'qyh_met_ttick_test'#
def factor_qyh_met_ttick_test(tick_df, return_fillna_dic=False):
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
    pre_close = tick_df['pre_close'].values[0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    t_fzt = tick_df[tick_df['LastPx'] >= round_(tick_df['LastPx'].max(), 2)]['MDTime'].min()  # 首次逼近涨停时间
    tick_df = tick_df[tick_df['MDTime'] >= t_fzt]
    #
    tick_df['factor'] = (tick_df['Buy1Price'] - tick_df['Sell1Price']) / (tick_df['pre_close'])
    if zcz:
        tick_df['factor'] = tick_df['factor'] / 2
    res = tick_df['factor'].kurt()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
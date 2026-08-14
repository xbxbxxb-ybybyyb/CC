import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_20231026_4'#
def factor_qyh_ttick_20231026_4(tick_df, return_fillna_dic=False):
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
    pre_close = tick_df['pre_close'].values[0]
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['factor'] = (tick_df['Sell1Price'] - tick_df['Buy1Price']) / tick_df['pre_close']
    if zcz:
        tick_df['factor'] = tick_df['factor']/2
    #
    para = 400
    tick_df1 = tick_df.head(para) if len(tick_df)>para else tick_df.head(int(len(tick_df)/2))
    tick_df1 = tick_df1[tick_df1['Sell1Price'] > 0]
    res1 = tick_df1['factor'].std() / tick_df1['factor'].mean() / np.log(pre_close+27) \
        if round_(tick_df1['factor'].mean(),5)>0 else np.nan
    factor_dict = {factor_name: res1}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

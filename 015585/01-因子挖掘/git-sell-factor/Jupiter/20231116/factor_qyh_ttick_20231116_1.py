import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_20231116_1'#
def factor_qyh_ttick_20231116_1(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.036}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    pre_close = tick_df['pre_close'].values[0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df = tick_df[tick_df['MDTime']>=93000000]
    if zcz:
        tick_df['Sell1Price'] = ((tick_df['Sell1Price']/pre_close-1)/2+1)
        tick_df['WeightedAvgOfferPx'] = ((tick_df['WeightedAvgOfferPx']/pre_close-1)/2+1)
    tick_df['s12s'] = (tick_df['Sell1Price'] / tick_df['WeightedAvgOfferPx'])
    tick_df1 = tick_df.head(40)
    tick_df2 = tick_df.tail(40)
    res1 = (tick_df1['s12s']**2).sum() / (tick_df1['s12s'].sum()**2+1e-3)
    res2 = (tick_df2['s12s']**2).sum() / (tick_df2['s12s'].sum()**2+1e-3)
    factor_dict = {factor_name: res1-res2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
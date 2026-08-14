import numpy as np
import pandas as pd

factor_name = 'qyh_ttick_20230921_4'#
def factor_qyh_ttick_20230921_4(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = tick_df['pre_close'].values[0]
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['s12s'] = (tick_df['Sell1Price'] - tick_df['WeightedAvgOfferPx']) / pre_close
    if zcz:
        tick_df['s12s'] = tick_df['s12s']/2
    res = tick_df['s12s'].values[0] + tick_df['s12s'].values[-1] \
          - 2*tick_df['s12s'].values[int(len(tick_df)/2)] if len(tick_df) > 3 else np.nan
    #
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

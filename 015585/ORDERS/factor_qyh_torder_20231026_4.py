import numpy as np
import pandas as pd
factor_name = 'qyh_torder_20231026_4'#
def factor_qyh_torder_20231026_4(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.26}
    #
    dt, ticker = order_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = order_df['pre_close'].values[0]
    if zcz:
        p_zt = np.floor(pre_close * 100 * 1.2 + 0.5) / 100
    else:
        p_zt = np.floor(pre_close * 100 * 1.1 + 0.5) / 100
    order_df = order_df[order_df['OrderPrice'] >= p_zt]
    #
    order_df = order_df.tail(int(len(order_df)/2)) if len(order_df)>10 else order_df
    #
    res = order_df['OrderIndex'].skew()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

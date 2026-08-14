import numpy as np
import pandas as pd
factor_name = 'qyh_torder_20231019_6'#
def factor_qyh_torder_20231019_6(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1.8e+6}
    dt, ticker = order_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = order_df['pre_close'].values[0]
    if zcz:
        p_zt = np.floor(pre_close * 100 * 1.2 + 0.5) / 100
    else:
        p_zt = np.floor(pre_close * 100 * 1.1 + 0.5) / 100
    order_df = order_df[order_df['MDTime']>=93000000]
    order_df = order_df[order_df['OrderPrice'] > 0]
    order_df['OrderAmt'] = order_df['OrderPrice'] * order_df['OrderQty']
    if order_df['MDTime'].max() > 93500000:
        order_df = order_df.tail(50)
    else:
        order_df = order_df[order_df['OrderPrice'] == p_zt].tail(50)
    order_df = order_df[order_df['OrderAmt'] >= 50000]
    order_df1 = order_df[order_df['OrderBSFlag']==1]
    res1 = order_df1['OrderAmt'].sum()
    factor_dict = {factor_name: res1}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

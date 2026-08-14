import numpy as np
import pandas as pd
factor_name = 'qyh_torder_20231026_1'#
def factor_qyh_torder_20231026_1(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 2.54}
    dt, ticker = order_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = order_df['pre_close'].values[0]
    # mv = order_df['ff_shares'].values[0] * order_df['pre_close'].values[0]
    if zcz:
        p_zt = np.floor(pre_close * 100 * 1.2 + 0.5) / 100
    else:
        p_zt = np.floor(pre_close * 100 * 1.1 + 0.5) / 100
    #
    order_df = order_df[order_df['MDTime']>=93000000]
    order_df = order_df[order_df['OrderPrice'] < p_zt]
    order_df['OrderAmt'] = order_df['OrderQty'] * order_df['OrderPrice']
    p = order_df['OrderAmt'].sum() / order_df['OrderQty'].sum()
    res = p/pre_close-1
    if zcz:
        res = res/2
    #
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

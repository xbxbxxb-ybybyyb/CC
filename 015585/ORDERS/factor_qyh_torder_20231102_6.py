import numpy as np
import pandas as pd
# dtj,zcz
# 所有订单挂单均价
#
# sss_o_high_price_sell:48
factor_name = 'qyh_torder_20231102_6'#
def factor_qyh_torder_20231102_6(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.04}
    dt, ticker = order_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = order_df['pre_close'].values[0]
    if zcz:
        p_zt = np.floor(pre_close * 100 * 1.2 + 0.5) / 100
        p_dt = np.floor(pre_close * 100 * 0.8 + 0.5) / 100
    else:
        p_zt = np.floor(pre_close * 100 * 1.1 + 0.5) / 100
        p_dt = np.floor(pre_close * 100 * 0.9 + 0.5) / 100
    #
    # order_df = order_df[order_df['MDTime']>=92000000]
    order_df = order_df[(order_df['OrderPrice'] >= p_dt)]
    order_df['OrderAmt'] = order_df['OrderQty'] * order_df['OrderPrice']
    order_df1 = order_df
    p1 = order_df1['OrderAmt'].sum() / order_df1['OrderQty'].sum()
    res1 = p1/pre_close-1
    if zcz:
        res1 = res1/2
    #
    factor_dict = {factor_name: res1}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

import numpy as np
import pandas as pd
factor_name = 'qyh_torder_20231130_1'#
def factor_qyh_torder_20231130_1(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    #
    dt, ticker = order_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = order_df['pre_close'].values[0]
    # mv = pre_close * order_df['ff_shares'].values[0]
    #
    order_df = order_df.tail(int(len(order_df)/3))
    order_df['OrderAmt'] = order_df['OrderPrice'] * order_df['OrderQty']
    order_df['OrderPrice_vwap'] = (order_df['OrderAmt'] * order_df['OrderPrice']).cumsum() / order_df['OrderAmt'].cumsum()
    order_df['factor'] = (order_df['OrderPrice'] - order_df['OrderPrice_vwap']) / order_df['pre_close']
    if zcz:
        order_df['factor'] = order_df['factor']/2
    res = (order_df['factor'] * order_df['OrderAmt']).sum() / order_df['OrderAmt'].sum()
    factor_dict = {factor_name: res}
    #---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

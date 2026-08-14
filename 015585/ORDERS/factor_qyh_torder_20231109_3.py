import numpy as np
import pandas as pd
# zcz,dtj
# 后部分订单的买卖单序号和
# 41,-0.08
#
factor_name = 'qyh_torder_20231109_3'#
def factor_qyh_torder_20231109_3(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    #
    dt, ticker = order_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = order_df['pre_close'].values[0]
    # mv = pre_close * order_df['ff_shares'].values[0]
    # order_df = order_df[order_df['MDTime'] >= 93000000]
    order_df = order_df.tail(int(len(order_df)/2))
    order_df1 = order_df.query('OrderBSFlag == 1')
    order_df2 = order_df.query('OrderBSFlag == 2')
    res1 = order_df1['OrderIndex'].sum()
    res2 = order_df2['OrderIndex'].sum()
    factor_dict = {factor_name: res1 / res2}
    #---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

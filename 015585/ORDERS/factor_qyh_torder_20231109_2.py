import numpy as np
import pandas as pd
# zcz,dtj
# 最后100单金额中位数
# 40,0.074
#
factor_name = 'qyh_torder_20231109_2'#
def factor_qyh_torder_20231109_2(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 11319}
    #
    dt, ticker = order_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = order_df['pre_close'].values[0]
    # mv = pre_close * order_df['ff_shares'].values[0]
    # order_df = order_df[order_df['MDTime'] >= 93000000]
    order_df['OrderAmt'] = order_df['OrderQty'] * order_df['OrderPrice']
    order_df = order_df.tail(100)
    res = order_df['OrderAmt'].median()
    factor_dict = {factor_name: res}
    #---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

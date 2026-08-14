import numpy as np
import pandas as pd
# zcz,dtj
# 最后50单的大单金额占比
# 0.09，44
#
factor_name = 'qyh_torder_20231109_4'#
def factor_qyh_torder_20231109_4(order_df, return_fillna_dic=False):
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
    order_df = order_df.tail(50)
    order_df['OrderAmt'] = order_df['OrderPrice'] * order_df['OrderQty']
    res = order_df[order_df['OrderAmt'] > 200000]['OrderAmt'].sum() / (order_df['OrderAmt'].sum() + 1)
    if order_df['MDTime'].max() <= 93100000:
        res = -0.01
    factor_dict = {factor_name: res}
    #---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

import numpy as np
import pandas as pd
factor_name = 'qyh_torder_20231102_3'#
def factor_qyh_torder_20231102_3(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.56}
    #
    order_df['OrderAmt'] = order_df['OrderPrice'] * order_df['OrderQty']
    order_df = order_df.tail(int(len(order_df)/2))
    res = order_df[order_df['OrderBSFlag'] == 1]['OrderAmt'].sum() / (order_df['OrderAmt'].sum() + 1)
    factor_dict = {factor_name: res}
    #---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

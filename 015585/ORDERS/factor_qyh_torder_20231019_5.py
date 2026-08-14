import numpy as np
import pandas as pd
factor_name = 'qyh_torder_20231019_5'#
def factor_qyh_torder_20231019_5(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1.08}
    res1 = order_df[order_df['OrderBSFlag']==1]['OrderIndex'].sum()
    res2 = order_df[order_df['OrderBSFlag']==2]['OrderIndex'].sum()
    if res1 < 1:
        res = np.log(res1+1)
    else:
        res = res2/res1
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

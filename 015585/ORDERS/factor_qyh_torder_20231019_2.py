import numpy as np
import pandas as pd
factor_name = 'qyh_torder_20231019_2'#

import decimal
def round_(x, n=0):
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                     rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res

def factor_qyh_torder_20231019_2(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1.8}
    order_df = order_df[order_df['MDTime']>=93000000]
    order_df['OrderAmt'] = order_df['OrderQty'] * order_df['OrderPrice']
    order_df = order_df[order_df['OrderAmt']>0]
    para = 50 #
    order_df = order_df.tail(para)
    res1 = np.cumprod(order_df[order_df['OrderBSFlag']==1]['OrderAmt']/1000).max() \
           ** (1/(5+len(order_df[order_df['OrderBSFlag']==1])))
    res2 = np.cumprod(order_df[order_df['OrderBSFlag']==2]['OrderAmt']/1000).max() \
           ** (1/(5+len(order_df[order_df['OrderBSFlag']==2])))
    res2=round_(res2,8)
    #
    factor_dict = {factor_name: res1 / res2 if res2 > 0.001 else np.nan}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

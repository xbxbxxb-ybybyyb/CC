import numpy as np
import pandas as pd
factor_name = 'qyh_torder_20231019_1'#
def factor_qyh_torder_20231019_1(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 2.54}
    import decimal
    def round_(x, n=0):
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    order_df = order_df[order_df['MDTime']>=93000000]
    order_df['OrderAmt'] = order_df['OrderQty'] * order_df['OrderPrice']
    para = 50 # 50:60
    order_df1 = order_df[order_df['OrderBSFlag']==1].tail(para)
    order_df2 = order_df[order_df['OrderBSFlag']==2].tail(para)
    res1 = order_df1['OrderAmt'].mean()
    res2 = order_df2['OrderAmt'].mean()
    #
    factor_dict = {factor_name: res1/res2 if round_(abs(res2),2)>1 else 21}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

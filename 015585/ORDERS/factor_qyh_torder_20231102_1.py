import numpy as np
import pandas as pd
factor_name = 'qyh_torder_20231102_1'#
def factor_qyh_torder_20231102_1(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1.19}
    #
    import decimal
    def round_(x, n=0):
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    order_df = order_df[order_df['MDTime'] >= 93000000]
    order_df['OrderAmt'] = order_df['OrderPrice'] * order_df['OrderQty']
    order_df1 = order_df[order_df['OrderBSFlag']==1].tail(100)
    order_df2 = order_df[order_df['OrderBSFlag']==2].tail(100)
    #
    res1 = order_df1['OrderAmt'].median()
    res2 = order_df2['OrderAmt'].median()
    factor_dict = {factor_name: res1/res2 if round_(res2,5) > 0 else np.nan}
    #---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

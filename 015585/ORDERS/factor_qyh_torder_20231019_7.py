import numpy as np
import pandas as pd
factor_name = 'qyh_torder_20231019_7'#
def factor_qyh_torder_20231019_7(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.01}
    import decimal
    def round_(x, n=0):
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    # dt, ticker = order_df.index[0]
    # dt = dt.strftime('%Y%m%d')
    # zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    # pre_close = order_df['pre_close'].values[0]
    # if zcz:
    #     p_zt = np.floor(pre_close * 100 * 1.2 + 0.5) / 100
    # else:
    #     p_zt = np.floor(pre_close * 100 * 1.1 + 0.5) / 100
    order_df = order_df[order_df['MDTime']>=93000000]
    order_df = order_df[order_df['OrderPrice'] > 0]
    order_df['OrderAmt'] = order_df['OrderPrice'] * order_df['OrderQty']
    order_df1 = order_df[order_df['OrderBSFlag']==1].tail(100)
    order_df2 = order_df[order_df['OrderBSFlag']==2].tail(100)
    res1 = order_df1['OrderAmt'].sum()
    res2 = order_df2['OrderAmt'].sum()
    total = order_df['OrderAmt'].sum()
    factor_dict = {factor_name: (res1-res2)/total }
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

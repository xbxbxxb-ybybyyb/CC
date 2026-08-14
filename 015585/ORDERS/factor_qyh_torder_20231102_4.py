import numpy as np
import pandas as pd
factor_name = 'qyh_torder_20231102_4'#
def factor_qyh_torder_20231102_4(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1}
    import decimal
    def round_(x, n=0):
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    def inttime2deltamls(itime):
        mls = int(str(int(itime))[-3:])
        s = int(str(int(itime))[-5:-3])
        m = int(str(int(itime))[-7:-5])
        h = int(str(int(itime))[:-7])
        time_mls = h * 3600 * 1000 + m * 60 * 1000 + s * 1000 + mls
        time_mls_930 = 9 * 3600 * 1000
        if int(itime) > 120000000:
            time_delta = time_mls - time_mls_930 - 5400000
        else:
            time_delta = time_mls - time_mls_930
        return time_delta
    order_df['MDTime_delta'] = order_df['MDTime'].apply(
        lambda x: inttime2deltamls(x))
    order_df1 = order_df[order_df['OrderBSFlag']==1]
    order_df1 = order_df1.tail(100)
    order_df2 = order_df[order_df['OrderBSFlag']==2]
    order_df2 = order_df2.tail(100)
    #
    res1 = order_df1['MDTime_delta'].median()
    res2 = order_df2['MDTime_delta'].median()
    factor_dict = {factor_name: res1/res2 if round_(res2,5) > 0 else np.nan}
    #---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

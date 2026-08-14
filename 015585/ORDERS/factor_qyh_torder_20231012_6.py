import numpy as np
import pandas as pd
# dtj
# 最后100单序号集中度
# 0.078,55
#
factor_name = 'qyh_torder_20231012_6'#
def factor_qyh_torder_20231012_6(order_df, return_fillna_dic=False):
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
    # mv = order_df['ff_shares'].values[0] * order_df['pre_close'].values[0]
    order_df = order_df[order_df['MDTime']>=93000000]
    order_df = order_df.tail(100)
    res = (order_df['OrderIndex']**2).sum() / (order_df['OrderIndex'].sum() ** 2)
    #
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

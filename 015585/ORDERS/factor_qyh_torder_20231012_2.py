import numpy as np
import pandas as pd
# dtj
# 最后100单金额/对数市值
# 0.1，60
# fc_order_last_order_money：55 skk_order_1000_qty_rate：43
factor_name = 'qyh_torder_20231012_2'#
def factor_qyh_torder_20231012_2(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 454366}
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
    mv = order_df['ff_shares'].values[0] * order_df['pre_close'].values[0]
    # order_df = order_df.tail(50)
    order_df['OrderAmt'] = order_df['OrderQty'] * order_df['OrderPrice']
    res = order_df.tail(100)['OrderAmt'].sum() / np.log(mv)
    #
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

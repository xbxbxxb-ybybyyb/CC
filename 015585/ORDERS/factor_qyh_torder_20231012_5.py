import numpy as np
import pandas as pd
# dtj zcz
# 后一半订单中挂单均价对应的涨跌幅
# 0.1,46
# zwh_20230921_002:44
factor_name = 'qyh_torder_20231012_5'#
def factor_qyh_torder_20231012_5(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.041}
    import decimal
    def round_(x, n=0):
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    dt, ticker = order_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = order_df['pre_close'].values[0]
    # mv = order_df['ff_shares'].values[0] * order_df['pre_close'].values[0]
    order_df = order_df[order_df['MDTime']>=93000000]
    order_df = order_df.tail(int(len(order_df)/2))
    # order_df = order_df.tail(1000)
    order_df['OrderAmt'] = order_df['OrderQty'] * order_df['OrderPrice']
    res = order_df['OrderAmt'].sum() / order_df['OrderQty'].sum() / pre_close - 1
    if zcz:
        res = res/2
    #
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

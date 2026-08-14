import numpy as np
import pandas as pd
#
# wangjing
# -0.08,29
#
factor_name = 'qyh_tick_wangjing'#
def factor_qyh_tick_wangjing(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    import decimal
    def round_(x, n=0):
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    tick_df = tick_df[tick_df['MDTime']>=93000000]
    tick_df1 = tick_df.head(len(tick_df) - 600) if len(tick_df) > 900 \
        else tick_df.head(int(len(tick_df)/3*2))
    tick_df2 = tick_df.tail(600) if len(tick_df) > 900 \
        else tick_df.tail(int(len(tick_df)/3*1))
    b_tmp_ret = (tick_df1['HighPx'] - tick_df1['LastPx']) / (tick_df1['HighPx']-tick_df1['LowPx'])
    tmp_ret = (tick_df2['LastPx'].cummax() - tick_df2['LastPx']) \
              /(tick_df2['LastPx'].cummax()-tick_df2['LastPx'].cummin())
    res1 = b_tmp_ret.mean()
    res2 = tmp_ret.mean()
    factor_dict = {factor_name: res1 / res2 if round_(abs(res2),5)>0 else 1.8}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

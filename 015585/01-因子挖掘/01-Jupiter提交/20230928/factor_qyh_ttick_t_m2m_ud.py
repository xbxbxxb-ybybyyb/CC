import numpy as np
import pandas as pd
# dtj
# 上涨和下跌的时间的集中程度差异
# 53,0.1
#
factor_name = 'qyh_ttick_t_m2m_ud'#
def factor_qyh_ttick_t_m2m_ud(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.11}
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
    tick_df = tick_df[tick_df['MDTime']>=93000000]
    tick_df['MDTime_delta'] = tick_df['MDTime'].apply(lambda x: inttime2deltamls(x))
    tick_df1 = tick_df[tick_df['LastPx'] > tick_df['LastPx'].shift(1)]
    tick_df2 = tick_df[tick_df['LastPx'] < tick_df['LastPx'].shift(1)]
    res1 = tick_df1['MDTime_delta'].max() / tick_df1['MDTime_delta'].mean()
    res2 = tick_df2['MDTime_delta'].max() / tick_df2['MDTime_delta'].mean()
    factor_dict = {factor_name: res1-res2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

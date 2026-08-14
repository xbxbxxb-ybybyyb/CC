import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_20231019_4'#
def factor_qyh_ttick_20231019_4(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 643029}
    tick_df = tick_df[tick_df['MDTime']>=93000000]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
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
    tick_df['MDTime_delta'] = tick_df['MDTime'].apply(lambda x : inttime2deltamls(x))
    if len(tick_df)<40:
        tick_df1 = tick_df[tick_df['LastPx'] > tick_df['LastPx'].shift(1)]
        tick_df2 = tick_df[tick_df['LastPx'] < tick_df['LastPx'].shift(1)]
    else:
        tick_df1 = tick_df[tick_df['LastPx'] > tick_df['LastPx'].shift(1).rolling(40).max()]
        tick_df2 = tick_df[tick_df['LastPx'] < tick_df['LastPx'].shift(1).rolling(40).min()]
    res1 = (tick_df1['MDTime_delta']*tick_df1['ValueTrade']).sum() \
           / (tick_df1['ValueTrade'].sum()+1)
    res2 = (tick_df2['MDTime_delta']*tick_df2['ValueTrade']).sum() \
           / (tick_df2['ValueTrade'].sum()+1)
    #
    factor_dict = {factor_name: res1 - res2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

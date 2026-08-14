# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
#
# 末次涨停时间
# 0.124，0.1288，73
factor_name = 'qyh_lzttick_20240104_1'#
def factor_qyh_lzttick_20240104_1(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        return {factor_name: 0}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    p_zt = tick_df['LastPx'].max()
    tick_df['LastPx_1'] = tick_df['LastPx'].shift(1)
    time = tick_df[(tick_df['LastPx'] >= p_zt)&(tick_df['LastPx_1'] < p_zt)]['MDTime'].max()
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
    res = inttime2deltamls(time) if time > 0 else np.nan
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

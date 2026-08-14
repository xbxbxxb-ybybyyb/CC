# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 挂买占比在早盘1min的min
# 38,0.072
# next_sss_tk1m_1oia_min:38
def factor_qyh_n1mtick_20231207_10(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231207_10'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.35}
    # dt, ticker = tick_df.index[0]
    # dt = dt.strftime('%Y%m%d')
    # zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    # pre = tick_df['pre_close'].max()
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ratiob'] = tick_df['TotalBidQty']  \
                        / (tick_df['TotalBidQty'] + tick_df['TotalOfferQty'])
    # res = tick_df['ratiob'].mean() if not tick_df.empty else np.nan
    res = tick_df['ratiob'].min()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
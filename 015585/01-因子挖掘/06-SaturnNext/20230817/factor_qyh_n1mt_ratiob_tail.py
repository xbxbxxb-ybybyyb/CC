# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 开盘1分钟末尾挂买占比
# 41,0.071
# next_sss_tk1m_1oia_min:38
def factor_qyh_n1mt_ratiob_tail(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mt_ratiob_tail'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.3}
    # dt, ticker = tick_df.index[0]
    # dt = dt.strftime('%Y%m%d')
    # zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    # pre = tick_df['pre_close'].max()
    # tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ratiob'] = tick_df['TotalBidQty']  \
                        / (tick_df['TotalBidQty'] + tick_df['TotalOfferQty'])
    res = tick_df['ratiob'].tail(1).values[0] if not tick_df.empty else np.nan
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
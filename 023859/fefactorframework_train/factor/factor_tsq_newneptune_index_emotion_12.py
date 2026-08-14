import pandas as pd
import numpy as np


def factor_tsq_newneptune_index_emotion_12(tick_df, return_fillna_dic=False):
    factor_name = 'tsq_newneptune_index_emotion_12'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}

    tick_df = tick_df[(tick_df['MDTime'] >=93000000)&(tick_df['MDTime'] < 93100000)] #选择连续竞价阶段
    tick_df['LastPx_shift'] = tick_df['LastPx'].shift(1)
    tick_df['sign'] = np.sign(tick_df['LastPx'] - tick_df['LastPx_shift'])
    tick_df['sign_shift'] = tick_df['sign'].shift(1)
    tick_df['reverse'] = -tick_df['sign']*tick_df['sign_shift']
    amt = len(tick_df[tick_df['reverse']==1]) / len(tick_df)

    factor_dict = {factor_name: amt}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

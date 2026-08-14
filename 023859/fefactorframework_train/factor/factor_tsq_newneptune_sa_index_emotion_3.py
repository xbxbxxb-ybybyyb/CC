import pandas as pd
import numpy as np

def factor_tsq_newneptune_sa_index_emotion_3(tick_df, return_fillna_dic=False):
    factor_name = 'tsq_newneptune_sa_index_emotion_3'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df = tick_df[(tick_df['MDTime'] >= 93000000)&(tick_df['MDTime'] < 100000000)] #选择连续竞价阶段
    tick_df['LastPx'] = tick_df['LastPx'].replace(0, np.nan)
    tick_df['LastPx'] = tick_df['LastPx'].ffill()
    tick_df['ret'] = tick_df['LastPx'].pct_change()
    amt = tick_df['ret'].std()
    factor_dict = {factor_name: amt}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

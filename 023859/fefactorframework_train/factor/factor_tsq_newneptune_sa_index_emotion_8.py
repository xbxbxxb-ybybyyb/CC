import pandas as pd
import numpy as np

def factor_tsq_newneptune_sa_index_emotion_8(tick_df, return_fillna_dic=False):
    factor_name = 'tsq_newneptune_sa_index_emotion_8'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df = tick_df[(tick_df['MDTime'] >= 93000000) & (tick_df['MDTime'] < 100000000)]  # 选择连续竞价阶段
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    amt = tick_df['ValueTrade'].std()

    factor_dict = {factor_name: amt}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

import pandas as pd
import numpy as np

def factor_tsq_newneptune_index_emotion_10(tick_df, return_fillna_dic=False):
    factor_name = 'tsq_newneptune_index_emotion_10'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}

    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[(tick_df['MDTime'] >=93000000)&(tick_df['MDTime'] < 143000000)] #选择连续竞价阶段
    volume_afternoon = tick_df[tick_df['MDTime'] >=130000000]['VolumeTrade'].sum()
    volume_morning = tick_df[tick_df['MDTime'] <= 113000000]['VolumeTrade'].sum()
    amt = volume_afternoon / (1e-6+volume_morning) - 1

    factor_dict = {factor_name: amt}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

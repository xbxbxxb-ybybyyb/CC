import numpy as np
import pandas as pd
import decimal
from functions import *
factor_name = 'ttick_sample'#
def factor_qyh_ttick_sample(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        return {factor_name: 0}
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]

    factor_logic
    factor_dict = {factor_name: res}
    return pd.Series(factor_dict)

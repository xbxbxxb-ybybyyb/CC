import numpy as np
import pandas as pd
import decimal
from functions import *
factor_name = '930_after_all_all_0_bigger_t500_numtradesdiff_nostd_cct_nocompare'#
def factor_930_after_all_all_0_bigger_t500_numtradesdiff_nostd_cct_nocompare(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        return {factor_name: 0}
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]

    tick_df = tick_df.tail(20) if len(tick_df) > 20 else tick_df
    tick_df['factor'] = tick_df['NumTrades'] - tick_df['NumTrades'].shift(1).fillna(0)
    res = f_calc_cct(tick_df['factor'])
    
    factor_dict = {factor_name: res}
    return pd.Series(factor_dict)

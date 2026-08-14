import numpy as np
import pandas as pd
import decimal
from functions import *
factor_name = '930_after_all_all_0_bigger_all_vwap2p_nostd_skew_nocompare'#
def factor_930_after_all_all_0_bigger_all_vwap2p_nostd_skew_nocompare(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        return {factor_name: 0}
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]

    tick_df['vwap'] = tick_df['ValueTrade'].cumsum()/tick_df['VolumeTrade'].cumsum()
    tick_df['factor'] = tick_df['vwap']/tick_df['LastPx']
    res = f_calc_skew(tick_df['factor'])
    
    factor_dict = {factor_name: res}
    return pd.Series(factor_dict)

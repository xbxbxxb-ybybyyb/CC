import numpy as np
import pandas as pd
import decimal
from functions import *
factor_name = '930_after_all_all_0_bigger_t500_s2ttran_nostd_med_nocompare'#
def factor_930_after_all_all_0_bigger_t500_s2ttran_nostd_med_nocompare(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        return {factor_name: 0}
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]

    tick_df = tick_df.tail(20) if len(tick_df) > 20 else tick_df
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['factor'] = (tick_df['sell_amt'])/tick_df['ValueTrade'].sum()
    res = f_calc_med(tick_df['factor'])
    
    factor_dict = {factor_name: res}
    return pd.Series(factor_dict)

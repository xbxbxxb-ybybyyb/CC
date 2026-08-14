import pandas as pd
import numpy as np
import decimal
import datetime as dt
from scipy.stats import norm, skew, kurtosis, boxcox_normmax



def factor_xbc_20240118_5(transaction_df, return_fillna_dic=False):
    factor_name = 'xbc_20240118_5'
    nan_value = -0.79
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: nan_value}
    if transaction_df.shape[0] > 1:
        value_list = (transaction_df['LastPx'] - (transaction_df['Buy1Price'] + transaction_df['Sell1Price']) / 2)/transaction_df['pre_close']
        value = value_list.mean()
    else:
        value = nan_value
    factor_dict = {factor_name: value}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

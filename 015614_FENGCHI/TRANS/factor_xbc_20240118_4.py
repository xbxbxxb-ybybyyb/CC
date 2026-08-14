import pandas as pd
import numpy as np
import decimal
import datetime as dt
from scipy.stats import norm, skew, kurtosis, boxcox_normmax



def factor_xbc_20240118_4(transaction_df, return_fillna_dic=False):
    factor_name = 'xbc_20240118_4'
    nan_value = 0.98
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: nan_value}
    transaction_df = transaction_df[transaction_df['MDTime'] <= 93000000]  # 选择连续竞价阶段的逐笔成交数据

    if transaction_df.shape[0] > 1:
        value_list = (transaction_df['Buy1OrderQty'] + transaction_df['Sell1OrderQty']) /transaction_df['ff_shares']/transaction_df['pre_close']
        value = value_list.mean()
    else:
        value = nan_value
    factor_dict = {factor_name: value}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

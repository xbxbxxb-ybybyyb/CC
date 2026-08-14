import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_sat_news_20240920_1'
def factor_qyh_sat_news_20240920_1(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    news_df = pd.read_pickle('/dfs/group/800463/data/news_data/statistics/df_news_ticker.pkl', compression='gzip')
    news_num_df = news_df.groupby(['dt', 'Ticker'])[['id']].count()
    news_num_df[factor_name] = news_num_df['id'].unstack().fillna(0).rolling(1, 1).sum().stack()
    # -------------------------------------------------------------------------------------------------------------------
    return news_num_df[[factor_name]]
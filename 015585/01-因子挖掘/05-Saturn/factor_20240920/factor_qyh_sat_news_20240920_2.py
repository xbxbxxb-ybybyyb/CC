import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_sat_news_20240920_2'
def factor_qyh_sat_news_20240920_2(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    news_df = pd.read_pickle('/dfs/group/800463/data/news_data/statistics/df_news_ticker.pkl', compression='gzip')
    date_list = [pd.Timestamp(x) for x in s.tradingday('20160101', '20221231')]
    news_num_df = news_df[news_df['resource'] == 'DATAYES'].groupby(['dt', 'Ticker'])[['id']].count()
    news_num_df = news_num_df.reset_index()
    news_num_df = news_num_df[news_num_df['dt'].isin(date_list)].set_index(['dt', 'Ticker'])
    news_num_df[factor_name] = news_num_df['id'].unstack().fillna(0).rolling(1, 1).sum().stack()
    # -------------------------------------------------------------------------------------------------------------------
    return news_num_df[[factor_name]]
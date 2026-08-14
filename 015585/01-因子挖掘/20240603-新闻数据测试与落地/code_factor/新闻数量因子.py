import IO
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData

s = FactorData()
# Europa全局样本与标签
def cal_ul_price(pre_close_dataframe, ratio = 0.1):
    pre_close_dataframe = pre_close_dataframe.reset_index()
    after_824 = pre_close_dataframe['dt']>=pd.Timestamp('20200824')
    cyb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2]=='30')
    kcb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2]=='68')
    pre_close_dataframe['ul_price'] = np.floor(pre_close_dataframe['pre_close'] * 100 * (1+ratio) + 0.5) / 100
    pre_close_dataframe.loc[(after_824 & cyb)| kcb, 'ul_price'] = np.floor(pre_close_dataframe['pre_close'] * 100 * (1+2*ratio) + 0.5) / 100
    return pre_close_dataframe.set_index(['dt', 'Ticker'])['ul_price']
md_data = IO.read_data([20150930, 20221231], columns=['amt', 'high','open','close','pre_close','vwap','adjfactor'],
                        alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md_data['ul_price'] = cal_ul_price(md_data)
for col in ['high','open','close','pre_close','vwap']:
    md_data[col+'_adj'] = md_data[col] * md_data['adjfactor']
md_data['next_vwap_adj'] = md_data['vwap_adj'].unstack().shift(-1).stack()
md_data['trigger_price'] = md_data['ul_price'] - 0.01
md_data['is_zt'] = (md_data['high'] >= md_data['ul_price']).apply(int)
md_data['last_is_zt'] = md_data['is_zt'].unstack().shift(1).stack()
md_data['label_ul'] = (md_data['next_vwap_adj'] / md_data['open'] / md_data['adjfactor'] - 1) * 100
md_data = md_data.query('open < ul_price and last_is_zt == 1')
md_data = md_data.reset_index()
md_data_ori = md_data[~md_data['Ticker'].str.contains('.BJ')].set_index(['dt','Ticker'])
# 新闻全局统计
# path_news_data = '/dfs/group/800463/data/news_data/news_data_combo/'
# file_list = os.listdir(path_news_data)
# file_list = [x for x in file_list if '.pkl' in x and x >= '20160101.pkl' and x <= '20221231.pkl']
# file_list.sort()
# news_df = pd.DataFrame()
# for file in file_list:
#     print(file)
#     df = pd.read_pickle(path_news_data + file, compression='gzip')
#     df = df[df['Ticker'].notna()][['dt','Ticker','id','resource']]
#     df = df[~df['Ticker'].str.contains('HK')]
#     news_df = news_df.append(df)
# news_df.to_pickle('/dfs/group/800463/data/news_data/statistics/df_news_ticker.pkl',compression = 'gzip')
#
news_df = pd.read_pickle('/dfs/group/800463/data/news_data/statistics/df_news_ticker.pkl',compression = 'gzip')
news_df = news_df[news_df['is_value_by_time'] == 1]
news_num_df = news_df.groupby(['dt','Ticker'])[['id']].count()
#
news_num_df['num_5_natural'] = news_num_df['id'].unstack().fillna(0).rolling(5,1).sum().shift(1).stack()
md_data = pd.merge(md_data_ori,news_num_df[['num_5_natural']],left_index=True,right_index=True,how='left')
print(md_data[['num_5_natural','label_ul']].corr(method = 'spearman'))
#
date_list = [pd.Timestamp(x) for x in s.tradingday('20160101','20221231')]
news_num_df = news_df[news_df['resource']=='DATAYES'].groupby(['dt','Ticker'])[['id']].count()
news_num_df = news_num_df.reset_index()
news_num_df = news_num_df[news_num_df['dt'].isin(date_list)].set_index(['dt','Ticker'])
news_num_df['num_5_trading'] = news_num_df['id'].unstack().fillna(0).rolling(5,1).std().shift(1).stack()
# news_num_df['num_5_trading'] = news_num_df['num_5_trading'] / (news_num_df['num_5_trading'].unstack().fillna(0).median(axis=1)+0.1)
md_data = pd.merge(md_data_ori,news_num_df[['num_5_trading']],left_index=True,right_index=True,how='left')
for i in [2016,2017,2018,2019,2020]:
    print(i)
    print(md_data[['num_5_trading','label_ul']].loc[pd.Timestamp('{}0101'.format(i)):pd.Timestamp('{}1231'.format(i))].corr(method = 'spearman'))



import IO
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
import pickle

def save_pickle(result_dic, save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(result_dic, input, protocol=pickle.HIGHEST_PROTOCOL)
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
md_data['label_ul'] = (md_data['next_vwap_adj'] / md_data['ul_price'] / md_data['adjfactor'] - 1) * 100
md_data['label_normal'] = (md_data['next_vwap_adj'] / md_data['vwap'] / md_data['adjfactor'] - 1) * 100
# md_data = md_data.query('high >= trigger_price and open < ul_price and last_is_zt == 0')
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
# news_df = pd.read_pickle('/dfs/group/800463/data/news_data/statistics/df_news_ticker.pkl',compression = 'gzip')
# news_num_df = news_df.groupby(['dt','Ticker'])[['id']].count()
# 生成共现矩阵
# for dt,df_dt in news_df.groupby('dt'):
#     df_dt = df_dt[~df_dt.duplicated(subset = ['Ticker','id','resource'])]
#     print(dt,len(df_dt))
#     df_dt['count'] = 1
#     df_dt['id'] = df_dt['id'].apply(str) + df_dt['resource']
#     df_dt = df_dt[['Ticker','id','count']].set_index(['Ticker','id']).unstack().fillna(0)
#     # matrix1_dt = pd.DataFrame(np.dot(df_dt.values , df_dt.T.values), index = list(df_dt.index), columns = list(df_dt.index))
#     matrix1_dt = np.dot(df_dt.values , df_dt.T.values)
#     matrix2_dt = pd.DataFrame(matrix1_dt / np.diagonal(matrix1_dt)[:,np.newaxis], index=list(df_dt.index), columns=list(df_dt.index))
#     matrix2_dt.to_pickle('/data/user/015585/01-因子挖掘/20240603-新闻数据测试与落地/code_factor/file_together/{}.pkl'.format(dt.strftime('%Y%m%d')))

# 计算共现因子
base_path = '/data/user/015585/01-因子挖掘/20240603-新闻数据测试与落地/code_factor/file_together/'
date_list = [pd.Timestamp(x) for x in s.tradingday('20160101','20221231')]
date_list.sort()
factor_exist_together = pd.DataFrame()
for date in date_list[1:]:
    date_index = date_list.index(date)
    date_t_1 = date_list[date_index-1]
    df1 = pd.read_pickle('{}{}.pkl'.format(base_path, date.strftime('%Y%m%d')))
    df2 = pd.read_pickle('{}{}.pkl'.format(base_path, date_t_1.strftime('%Y%m%d')))
    res_date = pd.DataFrame((df1 - df2).mean())
    res_date['dt'] = date
    res_date = res_date.reset_index().rename(columns = {'index':'Ticker'}).set_index(['dt','Ticker'])
    factor_exist_together = factor_exist_together.append(res_date)
    print(date,factor_exist_together.shape)
factor_exist_together = factor_exist_together[0].unstack().shift(1).stack()
factor_exist_together = pd.DataFrame(factor_exist_together)
#
md_data = pd.merge(md_data_ori,factor_exist_together[[0]],left_index=True,right_index=True,how='left')
for i in [2016,2017,2018,2019,2020]:
    print(i)
    # print(md_data[[0,'label_ul']].loc[pd.Timestamp('{}0101'.format(i)):pd.Timestamp('{}1231'.format(i))].fillna(0).corr(method = 'spearman'))
    print(md_data[[0,'label_normal']].loc[pd.Timestamp('{}0101'.format(i)):pd.Timestamp('{}1231'.format(i))].fillna(0)
          .groupby('dt').apply(lambda x : x.corr(method = 'spearman').iloc[0,1]).mean())



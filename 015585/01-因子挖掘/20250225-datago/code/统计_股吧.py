import pandas as pd
import os
import numpy as np
import IO
#
root_path = '/dfs/user/015585/05_datago/test_data/sftp/GACRIS/20250213-delivery/'
package_list = ['GACRIS-V3_natural_day_basic_stat',
                'GACRIS-V3_post_hotness_info',
                'GACRIS-V3_post_info',
                'GACRIS-V3_post_related_stock',
                'GACRIS-V3_user_info',
                'GACRIS-V3_cfh_natural_day_stat',
                'GACRIS-V3_platform_post_daily_stat'
                ]
df_nd_stat = pd.read_csv(f'{root_path}{package_list[0]}/{package_list[0]}_20200101to20241231.csv')
df_nd_stat_cfh = pd.read_csv(f'{root_path}{package_list[5]}/{package_list[5]}_20200101to20241231.csv')
df_nd_stat_plat = pd.read_csv(f'{root_path}{package_list[6]}/{package_list[6]}_20200101to20241231.csv')

df_p_hotness = pd.read_csv(f'{root_path}{package_list[1]}/{package_list[1]}_20200101to20241231.csv')
df_p_info = pd.read_csv(f'{root_path}{package_list[2]}/{package_list[2]}_20200101to20241231.csv')
df_p_stock = pd.read_csv(f'{root_path}{package_list[3]}/{package_list[3]}_20200101to20241231.csv')


df_nd_stat['dt'] = df_nd_stat['pub_date'].apply(pd.Timestamp)
df_nd_stat['year'] = df_nd_stat['dt'].apply(lambda x : x.year)
df_nd_stat = df_nd_stat.rename(columns = {'stock_id':'Ticker'})
df_nd_stat = df_nd_stat.set_index(['dt','Ticker'])
df_nd_stat['is_value'] = 1 # 添加标识符便于统计全面性

df_nd_stat_cfh['dt'] = df_nd_stat_cfh['pub_date'].apply(pd.Timestamp)
df_nd_stat_cfh['year'] = df_nd_stat_cfh['dt'].apply(lambda x : x.year)
df_nd_stat_cfh = df_nd_stat_cfh.rename(columns = {'stock_id':'Ticker'})
df_nd_stat_cfh = df_nd_stat_cfh.set_index(['dt','Ticker'])
df_nd_stat_cfh['is_value'] = 1 # 添加标识符便于统计全面性

df_nd_stat_plat['dt'] = df_nd_stat_plat['pub_date'].apply(pd.Timestamp)
df_nd_stat_plat['year'] = df_nd_stat_plat['dt'].apply(lambda x : x.year)
df_nd_stat_plat = df_nd_stat_plat.rename(columns = {'stock_id':'Ticker'})
df_nd_stat_plat = df_nd_stat_plat.set_index(['dt','Ticker'])
df_nd_stat_plat['is_value'] = 1 # 添加标识符便于统计全面性

df_p_hotness['dt'] = df_p_hotness['record_time'].apply(lambda x : pd.Timestamp(x.split(' ')[0]))
df_p_hotness['time'] = df_p_hotness['record_time'].apply(lambda x : x.split(' ')[1])
# 确认hotness:帖子id+日期是否只有1个记录
count_max_id_dt = df_p_hotness.groupby(['dt','post_id']).count()['record_time'].max()
print(f'hotness：dt + post_id后是否有重复记录（2或以上代表有）:{count_max_id_dt}')
# 全面性
## 统计数据df_nd_stat、plat、cfh的全面性:标的覆盖率
'''
不分type：全市场覆盖率（2020-2024），策略样本覆盖率
'''
md_data = IO.read_data([20200101, 20241231], columns = ['amt', 'pre_close', 'close', 'high'],
                       alt='/data/group/800080/warehouseJG/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md_data['zcz']=(((md_data.reset_index()['Ticker'].apply(lambda x:x[0:2]=='30'))&(md_data.reset_index()['dt']>='2020-08-24'))
|(md_data.reset_index()['Ticker'].apply(lambda x:x[0:2]=='68'))).values
md_data['bj'] = (md_data.reset_index()['Ticker'].apply(lambda x:x[-2:]=='BJ')).values
zt_price = np.floor(md_data['pre_close'] * 100 * 1.1 + 0.5) / 100
zt_price[md_data['zcz']] = np.floor(md_data['pre_close'] * 100 * 1.2 + 0.5) / 100
zt_price[md_data['bj']] = np.floor(md_data['pre_close'] * 100 * 1.3 + 0.5) / 100
md_data['zt_price'] = zt_price

md_data_all_market = md_data[md_data['amt'] > 0]
res_md_data = pd.merge(md_data_all_market,df_nd_stat[['is_value']],left_index=True,right_index=True,how = 'left').groupby(['dt','Ticker'])['is_value'].max()
print(f'个人投资者帖子，全市场样本: {res_md_data.shape[0]},{res_md_data.sum()},{res_md_data.sum() / res_md_data.shape[0]}')
res_md_data = pd.merge(md_data_all_market,df_nd_stat_cfh[['is_value']],left_index=True,right_index=True,how = 'left').groupby(['dt','Ticker'])['is_value'].max()
print(f'财富号帖子，全市场样本: {res_md_data.shape[0]},{res_md_data.sum()},{res_md_data.sum() / res_md_data.shape[0]}')
res_md_data = pd.merge(md_data_all_market,df_nd_stat_plat[['is_value']],left_index=True,right_index=True,how = 'left').groupby(['dt','Ticker'])['is_value'].max()
print(f'平台生成帖子，全市场样本: {res_md_data.shape[0]},{res_md_data.sum()},{res_md_data.sum() / res_md_data.shape[0]}')


md_data_strategy = md_data[(md_data['amt'] > 0) & (md_data['close'] == md_data['zt_price'])]
res_md_data = pd.merge(md_data_strategy,df_nd_stat[['is_value']],left_index=True,right_index=True,how = 'left').groupby(['dt','Ticker'])['is_value'].max()
print(f'个人投资者帖子，策略样本中: {res_md_data.shape[0]},{res_md_data.sum()},{res_md_data.sum() / res_md_data.shape[0]}')
res_md_data = pd.merge(md_data_strategy,df_nd_stat_cfh[['is_value']],left_index=True,right_index=True,how = 'left').groupby(['dt','Ticker'])['is_value'].max()
print(f'财富号帖子，策略样本中: {res_md_data.shape[0]},{res_md_data.sum()},{res_md_data.sum() / res_md_data.shape[0]}')
res_md_data = pd.merge(md_data_strategy,df_nd_stat_plat[['is_value']],left_index=True,right_index=True,how = 'left').groupby(['dt','Ticker'])['is_value'].max()
print(f'平台生成帖子，策略样本中: {res_md_data.shape[0]},{res_md_data.sum()},{res_md_data.sum() / res_md_data.shape[0]}')

## 统计数据df_nd_stat的全面性：分年度统计策略样本，帖子数量的分位数
md_data_strategy = md_data[(md_data['amt'] > 0) & (md_data['close'] == md_data['zt_price'])]
print(md_data_strategy.shape)
res1 = pd.DataFrame() # index = type year ; columns = 指标 分位数 策略内

tmp_df_nd_stat1 = df_nd_stat[['year','post_neg_sum','post_neu_sum','post_pos_sum']].reset_index().set_index(['dt','Ticker'])
tmp_df_nd_stat2 = pd.DataFrame()
for col in ['post_neg_sum','post_neu_sum','post_pos_sum']:
    tmp_df_nd_stat2[col] = tmp_df_nd_stat1[col].unstack().fillna(0).stack()
tmp_df_nd_stat2['year'] = tmp_df_nd_stat2.index.get_level_values(0)
tmp_df_nd_stat2['year'] = tmp_df_nd_stat2['year'].apply(lambda x : x.year)
res_md_data = pd.merge(md_data_strategy, tmp_df_nd_stat2.reset_index().set_index(['dt','Ticker']), left_index=True, right_index=True, how = 'left')
res1 = res1.append(res_md_data.groupby(['year']).apply(lambda x : x.quantile([0.25,0.5,0.75]))[['post_neg_sum','post_neu_sum','post_pos_sum']])
res1.unstack().to_csv('策略标的个人投资者帖子数目统计_股吧.csv')

## 统计数据df_nd_stat_cfh的全面性：分年度统计策略样本，财富号数量的分位数
md_data_strategy = md_data[(md_data['amt'] > 0) & (md_data['close'] == md_data['zt_price'])]
print(md_data_strategy.shape)
res1 = pd.DataFrame() # index = type year ; columns = 指标 分位数 策略内

tmp_df_nd_stat1 = df_nd_stat_cfh[df_nd_stat_cfh['relevant_type'] == 1][['post_neg_sum','post_neu_sum','post_pos_sum']].reset_index().groupby(['dt','Ticker']).sum()
tmp_df_nd_stat2 = pd.DataFrame()
for col in ['post_neg_sum','post_neu_sum','post_pos_sum']:
    tmp_df_nd_stat2[col] = tmp_df_nd_stat1[col].unstack().fillna(0).stack()
tmp_df_nd_stat2['year'] = tmp_df_nd_stat2.index.get_level_values(0)
tmp_df_nd_stat2['year'] = tmp_df_nd_stat2['year'].apply(lambda x : x.year)
res_md_data = pd.merge(md_data_strategy, tmp_df_nd_stat2.reset_index().set_index(['dt','Ticker']), left_index=True, right_index=True, how = 'left')
res1 = res1.append(res_md_data.groupby(['year']).apply(lambda x : x.quantile([0.25,0.5,0.75]))[['post_neg_sum','post_neu_sum','post_pos_sum']])
res1.unstack().to_csv('策略标的财富号文章数目统计_股吧.csv')

## 统计数据df_nd_stat的全面性：分年度统计全市场样本，不同帖子数量的分位数
md_data_all_market = md_data[(md_data['amt'] > 0)]
print(md_data_all_market.shape)
res2 = pd.DataFrame() # index = type year ; columns = 指标 分位数 全市场
res_md_data = pd.merge(md_data_all_market, tmp_df_nd_stat2.reset_index().set_index(['dt','Ticker']), left_index=True, right_index=True, how = 'left')
res2 = res2.append(res_md_data.groupby(['relevant_type','year']).apply(lambda x : x.quantile([0.25,0.5,0.75]))[['post_neg_sum','post_neu_sum','post_pos_sum']])

# 有效性：帖子热度记录时间分布
hotness_record_time = df_p_hotness.groupby('time')['post_id'].count()
print(hotness_record_time / hotness_record_time.sum())
'''
晚上9点到11点的采集数据占到84.7%，根据与数据商沟通，系爬虫分布所致
'''
# 有效性：帖子热度记录规律
hotness_record_count = df_p_hotness.groupby('post_id')['record_time'].count()
'''
min = 1，max = 2，和数据商口径一致
'''
# 一致性：底层数据统计每日帖子数
df_p_info_stock = df_p_info.copy()
df_p_info_stock['dt'] = df_p_info_stock['post_time'].apply(lambda x : pd.Timestamp(x.split(' ')[0]))
stat_df_p_info_stock = df_p_info_stock.groupby(['dt','stock_id','post_type','sentiment'])['post_id'].count()
stat_df_p_info_stock = stat_df_p_info_stock.unstack().reset_index()
stat_df_p_info_stock = stat_df_p_info_stock.rename(columns = {'stock_id':'Ticker'})

## 验证个人投资者帖子数
stat_df_p_info_stock_1 = pd.merge(stat_df_p_info_stock[(stat_df_p_info_stock['post_type'] == 1)].set_index(['dt','Ticker']),
                                  df_nd_stat[['post_neg_sum','post_neu_sum','post_pos_sum']],
                                  left_index=True, right_index=True,how='outer')
for col in [-1,0,1]:
    stat_df_p_info_stock_1[col] = stat_df_p_info_stock_1[col].fillna(0)
stat_df_p_info_stock_1['test1'] = stat_df_p_info_stock_1[-1] - stat_df_p_info_stock_1['post_neg_sum'].fillna(0)
stat_df_p_info_stock_1['test2'] = stat_df_p_info_stock_1[0] - stat_df_p_info_stock_1['post_neu_sum'].fillna(0)
stat_df_p_info_stock_1['test3'] = stat_df_p_info_stock_1[1] - stat_df_p_info_stock_1['post_pos_sum'].fillna(0)
for col in ['test1','test2','test3']:
    print(col, '个人投资者帖子中，底层和衍生不一致占比：', len(stat_df_p_info_stock_1[stat_df_p_info_stock_1[col] != 0]) / len(stat_df_p_info_stock_1))
## 验证提及的短贴
stat_df_p_info_stock_2 = pd.merge(stat_df_p_info_stock[(stat_df_p_info_stock['post_type'] == 1)].set_index(['dt','Ticker']),
                                  df_nd_stat[df_nd_stat['relevant_type'] == 3][['post_neg_sum','post_neu_sum','post_pos_sum']],
                                  left_index=True, right_index=True,how='outer')
for col in [-1,0,1]:
    stat_df_p_info_stock_2[col] = stat_df_p_info_stock_2[col].fillna(0)
stat_df_p_info_stock_2['test1'] = stat_df_p_info_stock_2[-1] - stat_df_p_info_stock_2['post_neg_sum'].fillna(0)
stat_df_p_info_stock_2['test2'] = stat_df_p_info_stock_2[0] - stat_df_p_info_stock_2['post_neu_sum'].fillna(0)
stat_df_p_info_stock_2['test3'] = stat_df_p_info_stock_2[1] - stat_df_p_info_stock_2['post_pos_sum'].fillna(0)
for col in ['test1','test2','test3']:
    print(col, '短篇中，底层和衍生不一致占比：', len(stat_df_p_info_stock_2[stat_df_p_info_stock_2[col] != 0]) / len(stat_df_p_info_stock_2))
'''
除了不到2%的数据有微弱差异，其他一致
'''
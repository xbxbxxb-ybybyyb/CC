import IO
import os
import pandas as pd
from xquant.factordata import FactorData
import sys
s = FactorData()
start_date = 20160101
end_date = 20191231
# 取数2016-2019
path_distance_matrix = '/dfs/user/015585/20241107-数库产业链/20241107_样本距离_2016_2024_修正后/'
list_file = os.listdir(path_distance_matrix)
list_file = [x for x in list_file if x <= f'{end_date}.pkl' and x >= f'{start_date}']
list_file.sort()
df_file_ori = pd.DataFrame()
print(f'读取产业链数据：{start_date}_{end_date}')
for file in list_file:
    sys.stdout.write('\r' + str(file))
    sys.stdout.flush()
    df_file = pd.DataFrame(pd.read_pickle(f'{path_distance_matrix}{file}').stack())
    df_file['dt'] = file.replace('.pkl','')
    df_file_ori = df_file_ori.append(df_file)
print('产业链数据读取完毕')
df_file_ori = df_file_ori.reset_index().rename(columns = {'level_0':'Ticker1','level_1':'Ticker2',0:'value'})
df_file_ori['dt'] = df_file_ori['dt'].apply(pd.Timestamp)
# 补充所属行业
print('读取个股所属中信行业')
indu = IO.read_data([start_date,end_date],
                    alt = '/data/group/800080/warehouseJG/prod/RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5',
                    columns = ['Industry'])
indu = indu.reset_index()
df_file_ori = pd.merge(df_file_ori, indu, left_on=['dt','Ticker1'], right_on=['dt','Ticker'], how = 'left')
df_file_ori = df_file_ori.drop(['Ticker'],axis=1).rename(columns = {'Industry':'indu1'})
df_file_ori = pd.merge(df_file_ori, indu, left_on=['dt','Ticker2'], right_on=['dt','Ticker'], how = 'left')
df_file_ori = df_file_ori.drop(['Ticker'],axis=1).rename(columns = {'Industry':'indu2'})
# 统计策略覆盖率 Europa 2016-2019
print(f'统计策略覆盖率 Europa {start_date}_{end_date}')
df_europa = pd.read_hdf('/data/group/800463/data/project1_public/factor_lib_v3/Basic_zt_001_20150901_20191231.h5')
df_europa = df_europa.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
df_file_cover = df_file_ori[df_file_ori['']][['Ticker1','dt']].rename(columns = {'Ticker1':'Ticker'})
df_file_cover['is_value'] = 1
df_file_cover = df_file_cover.set_index(['dt','Ticker']).groupby(['dt','Ticker'])['is_value'].nth(0)
df_sta_cover = pd.merge(df_europa,df_file_cover,left_index=True,right_index=True,how = 'left')
print(f'2016-2019 Europa样本:{len(df_europa)}，覆盖的样本:{df_sta_cover["is_value"].sum()},覆盖率:{df_sta_cover["is_value"].sum() / len(df_europa)}')
# 距离分布 16-19 全集
print(f'统计产业链距离的分布 样本全集 {start_date}_{end_date}')
dist_mean = df_file_ori['value'].mean()
dist_quantile = df_file_ori['value'].quantile([0.25,0.5,0.75])
length200 = len(df_file_ori[df_file_ori['value'] >= 200])
dist_mean_del200 = df_file_ori[~(df_file_ori['value'] >= 200)]['value'].mean()
print(f'2016-2019 距离均值：{dist_mean}，距离分位数（25，50，75）：{dist_quantile}')
print(f'2016-2019 无法连接的样本数：{length200}，剔除无法连接的样本后，距离均值：{dist_mean_del200}')
# 行业分布 16-19
sta_dist_indu = pd.DataFrame(df_file_ori.groupby(['indu1','indu2'])['value'].mean())['value'].unstack()
sta_dist_indu_del200 = pd.DataFrame(df_file_ori[df_file_ori['value'] < 200].groupby(['indu1','indu2'])['value'].mean())['value'].unstack()
## 匹配行业中文
industry_code = ['b10100', 'b10200', 'b10300', 'b10400', 'b10500', 'b10600',
                 'b10700', 'b10800', 'b10900', 'b10a00', 'b10b00', 'b10c00',
                 'b10d00', 'b10e00', 'b10f00', 'b10g00', 'b10h00', 'b10i00',
                 'b10j00', 'b10k00', 'b10l00', 'b10n00', 'b10o00', 'b10p00',
                 'b10q00', 'b10r00', 'b10s00', 'b10t00', 'b10m01', 'b10m02', 'b10m03']
industry_num = [i + 1 for i in range(len(industry_code))]
industry_dict = dict(zip(industry_num, industry_code))

CITICS = s.get_factor_value('WIND_IndexContrastSector')
CITICS['key'] = CITICS['S_INFO_INDUSTRYCODE'].apply(lambda x : x[:6])
CITICS_dic = dict(CITICS[CITICS['key'].isin(industry_code)].groupby('key')['S_INFO_INDUSTRYNAME'].nth(0))
sta_dist_indu.columns = [CITICS_dic[industry_dict[x]] for x in sta_dist_indu.columns]
sta_dist_indu.index = [CITICS_dic[industry_dict[x]] for x in sta_dist_indu.index]
sta_dist_indu_del200.columns = [CITICS_dic[industry_dict[x]] for x in sta_dist_indu_del200.columns]
sta_dist_indu_del200.index = [CITICS_dic[industry_dict[x]] for x in sta_dist_indu_del200.index]
print(f'产业链按行业距离均值矩阵 样本全集 {start_date}_{end_date}')
# print(sta_dist_indu)
# 和FC-共同概念数比对
path_concept = '/data/group/800463/data/concept_data/europa/20241023/'
list_file_concept = os.listdir(path_concept)
list_file_concept = [x for x in list_file_concept if x <= f'{end_date}.pkl' and x >= f'{start_date}']
list_file_concept.sort()
df_file_concept_ori = pd.DataFrame()
for file in list_file_concept:
    sys.stdout.write('\r' + str(file))
    sys.stdout.flush()
    df_file_concept = pd.DataFrame(pd.read_pickle(f'{path_concept}{file}').stack())
    df_file_concept['dt'] = file.replace('.pkl','')
    df_file_concept_ori = df_file_concept_ori.append(df_file_concept)
df_file_concept_ori = df_file_concept_ori.reset_index().rename(columns = {'level_0':'Ticker1','level_1':'Ticker2',0:'num_concept'})
df_file_concept_ori['dt'] = df_file_concept_ori['dt'].apply(pd.Timestamp)
df_file_add_concept_num = pd.merge(df_file_ori, df_file_concept_ori, left_on=['dt','Ticker1','Ticker2'], right_on=['dt','Ticker1','Ticker2'], how = 'left')
sta_corr_with_concept = df_file_add_concept_num[['num_concept','value']].corr(method = 'spearman')
print('产业链距离和概念数据的秩相关系数：')
print(sta_corr_with_concept)
# 样本对的距离 和 abs(收益率之差)
label_df = IO.read_data([start_date, end_date],columns='value',
                  alt='/data/group/800463/data/project1_public/factor_lib_v3/sft_update_europa_filter_20160101_20191231.h5')
label_df.columns = ['label1']
df_file_add_concept_num_label = pd.merge(df_file_add_concept_num, label_df, left_on=['dt','Ticker1'], right_index=True, how = 'left')
label_df.columns = ['label2']
df_file_add_concept_num_label = pd.merge(df_file_add_concept_num_label, label_df, left_on=['dt','Ticker2'], right_index=True, how = 'left')
df_file_add_concept_num_label['label_delta'] = abs(df_file_add_concept_num_label['label1'] - df_file_add_concept_num_label['label2'])
corr_dist_label_delta = df_file_add_concept_num_label[['num_concept','value','label_delta']].corr(method = 'spearman')
print('产业链距离和abs(label_delta)的秩相关系数：')
print(corr_dist_label_delta)

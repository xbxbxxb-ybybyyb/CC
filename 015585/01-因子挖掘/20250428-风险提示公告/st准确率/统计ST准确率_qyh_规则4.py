import pandas as pd
import os
from xquant.factordata import FactorData
import IO
import numpy as np
s = FactorData()

'''
要求：1、现在的pre_st黑名单能避免多少st的，2、加入了风控那边st预警之后能避免多少st
'''
df_st = s.get_factor_value('WIND_AShareST')
risk_list_20241231 = list(df_st[((df_st['REMOVE_DT'].isnull()) | (df_st['REMOVE_DT'] >= '20250416')) \
                       & (df_st['ENTRY_DT'] <= '20250415') & (df_st['S_TYPE_ST'] != 'R')]['S_INFO_WINDCODE']) # 20250415 时候仍然有问题的股票
df_st_2025 = df_st[(df_st['ENTRY_DT'] >= '20250416') & (df_st['ENTRY_DT'] <= '20250430')]
df_st_2025_filter = df_st_2025[df_st_2025['S_TYPE_ST'] != 'R'] # 非“恢复上市”均考虑

# 获取pre_st的总和 df_pre_st
path_pre_st = '/data/user/015585/01-因子挖掘/20250428-风险提示公告/st准确率/pre_st_file/'
# /data/user/015585/01-因子挖掘/20250428-风险提示公告/pre_st_file/
file_list = os.listdir(path_pre_st)
file_list.sort()
file = file_list[0]
df_pre_st = pd.DataFrame()
for file in file_list:
    tradingday = file.replace('.xlsx','')[-8:]
    df_pre_st_date = pd.read_excel(f'{path_pre_st}{file}')
    df_pre_st_date['证券代码'] = df_pre_st_date['证券代码'].apply(lambda x : str(x).zfill(6))
    df_pre_st_date['证券代码'] = df_pre_st_date['证券代码'].apply(lambda x : x + '.SH' if x.startswith('6') \
        else x + '.SZ' if x.startswith('0') or x.startswith('3') else x + '.BJ')
    # df_pre_st_date['dt'] = tradingday
    df_pre_st_date['dt'] = s.tradingday(int(tradingday),2)[-1]
    df_pre_st = df_pre_st.append(df_pre_st_date)
'''
1、获取全集：在2025以后出现问题，且20241231未出现问题的所有标的，记录它们的ENTRY_DT
2、找到全集里每个标的的ENTRY_DT的最小值，往前取非停牌的前一个交易日
3、观察这个交易日的pre_st文件，如果覆盖了该标的则认为有效，否则认为无效，计算有效比率
'''
# 1、获取全集：在2025以后出现问题，且不在20241231里的所有标的，记录ENTRY_DT
df1 = df_st_2025_filter[~df_st_2025_filter['S_INFO_WINDCODE'].isin(risk_list_20241231)]
# 2、找到全集里每个标的的ENTRY_DT的最小值
df1_entrydt_min = df1.groupby('S_INFO_WINDCODE')['ENTRY_DT'].min().to_frame('ENTRY_DT_MIN')
# 往前取非停牌的前一个交易日
md_data = IO.read_data([20240101,20250429], columns=['amt'],
                       alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md_data = md_data[md_data['amt'] > 0].reset_index()
def last_trade_dt(Ticker, ENTRY_DT):
    md_data_tmp = md_data[(md_data['Ticker'] == Ticker) & (md_data['dt'] < pd.Timestamp(str(ENTRY_DT)))]
    res = md_data_tmp['dt'].max()
    return res
df1_entrydt_min['last_trade_dt'] = df1_entrydt_min.groupby('S_INFO_WINDCODE').apply(lambda x : last_trade_dt(x.name, x['ENTRY_DT_MIN'].values[0]))
df1_entrydt_min['last_trade_dt'] = df1_entrydt_min['last_trade_dt'].apply(lambda x : x.strftime('%Y%m%d'))
# 3、观察这个交易日的pre_st文件，如果覆盖了该标的则认为有效，否则认为无效，计算有效比率
df1_entrydt_min['isin_pre_st'] = np.nan
for index,row in df1_entrydt_min.iterrows():
    Ticker = index
    last_trade_dt = row['last_trade_dt']
    df_pre_st_check = df_pre_st[df_pre_st['dt'] == last_trade_dt]
    stock_list = list(df_pre_st_check['证券代码'])
    if Ticker in stock_list:
        df1_entrydt_min.loc[index, 'isin_pre_st'] = 1
    else:
        df1_entrydt_min.loc[index, 'isin_pre_st'] = 0
# df1_entrydt_min 即为所求
print('20250101-20250430:')
print(df1_entrydt_min.mean())

# 加入风控模块
df_riskcontrol = pd.read_excel('ST（2025）.xlsx')
## 计算联合概率 1-(1-a1)(1-a2)...(1-an)
df_riskcontrol['updatedate'] = df_riskcontrol['updatetime'].apply(lambda x : str(x).split(' ')[0].replace('-',''))
df_riskcontrol['tradingcode2'] = df_riskcontrol['tradingcode2'].apply(lambda x :x.replace("'",""))
df_riskcontrol['Ticker'] = df_riskcontrol['tradingcode2'].apply(lambda x : x + '.SH' if x.startswith('6') \
        else x + '.SZ' if x.startswith('0') or x.startswith('3') else x + '.BJ')
def get_combine_prob(x):
    prob = list(x['probability']/100)
    prob_1 = [1-i for i in prob]
    cumprob = 1
    for j in prob_1:
        cumprob = cumprob * j
    res = 1-cumprob
    return res
res_risk_control = df_riskcontrol.groupby(['updatedate','Ticker']).apply(get_combine_prob)
res_risk_control.to_csv('res_risk_control.csv')
## 风控部门预测的联合概率在80%以上的部分
res_risk_control_filter = res_risk_control[res_risk_control >= 0.8].reset_index()
## 用last_trade_dt（正式出问题的日期的前一个有交易的日期）和风控的updatetime对应日期对齐，isin_riskcontrol表示记录是否在风控的预测中
df1_entrydt_min['isin_riskcontrol'] = np.nan
for index,row in df1_entrydt_min.iterrows():
    Ticker = index
    last_trade_dt = row['last_trade_dt']
    res_risk_control_filter_check = res_risk_control_filter[res_risk_control_filter['updatedate'] == last_trade_dt]
    stock_list = list(res_risk_control_filter_check['Ticker'])
    if Ticker in stock_list:
        df1_entrydt_min.loc[index, 'isin_riskcontrol'] = 1
    else:
        df1_entrydt_min.loc[index, 'isin_riskcontrol'] = 0
print('加入风控后：')
print(df1_entrydt_min[['isin_riskcontrol','isin_pre_st']].max(axis=1).mean())


df1 = df_pre_st.groupby('dt')['证券代码'].apply(lambda x : list(x)).reset_index()
df2 = res_risk_control_filter.groupby('updatedate')['Ticker'].apply(lambda x : list(x)).reset_index()
df1.columns = ['dt','Ticker1']
df2.columns = ['dt','Ticker2']
res_tmp = pd.merge(df1,df2,left_on='dt',right_on='dt',how='outer')
for col in res_tmp:
    res_tmp[col] = res_tmp[col].apply(lambda x : [] if type(x) != list and type(x) != str else x)
res_tmp['Ticker3'] = res_tmp['Ticker1'] + res_tmp['Ticker2']
res_tmp['count'] = res_tmp['Ticker3'].apply(lambda x :len(set(x)))
print('新增风险预警后每天的预测数量 20250101-20250430：')
print(res_tmp['Ticker1'].apply(len).mean())
print('新增风险预警后每天的预测数量 20250101-20250415：')
print(res_tmp[res_tmp['dt'] <= '20250415']['Ticker1'].apply(len).mean())
print('新增风险预警后每天的预测数量 20250416-20250430：')
print(res_tmp[res_tmp['dt'] > '20250415']['Ticker1'].apply(len).mean())

df1_filter = df_pre_st[~df_pre_st['证券名称'].apply(str).str.contains('ST')].groupby('dt')['证券代码'].apply(lambda x : list(x)).reset_index()
df1_filter.columns = ['dt','Ticker1']
res_tmp_filter = pd.merge(df1_filter,df2,left_on='dt',right_on='dt',how='outer')
for col in res_tmp_filter:
    res_tmp_filter[col] = res_tmp_filter[col].apply(lambda x : [] if type(x) != list and type(x) != str else x)
res_tmp_filter['Ticker3'] = res_tmp_filter['Ticker1'] + res_tmp_filter['Ticker2']
res_tmp_filter['count'] = res_tmp_filter['Ticker3'].apply(lambda x :len(set(x)))
res_tmp_filter = res_tmp_filter[res_tmp_filter['dt'] != '20250203']
print('新增风险预警后每天的预测数量（剔除名称中带ST的部分后）20250101-20250430：')
print(res_tmp_filter['Ticker1'].apply(len).mean())
print('新增风险预警后每天的预测数量（剔除名称中带ST的部分后） 20250101-20250415：')
print(res_tmp_filter[res_tmp_filter['dt'] <= '20250415']['Ticker1'].apply(len).mean())
print('新增风险预警后每天的预测数量（剔除名称中带ST的部分后） 20250416-20250430：')
print(res_tmp_filter[res_tmp_filter['dt'] > '20250415']['Ticker1'].apply(len).mean())


res_tmp_filter['len_Ticker1'] = res_tmp_filter['Ticker1'].apply(len)



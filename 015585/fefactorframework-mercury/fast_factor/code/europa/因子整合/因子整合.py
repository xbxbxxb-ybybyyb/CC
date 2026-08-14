import os
import pandas as pd
import numpy as np
import sys
# TTrade
print('TTrade')
path_trade = '/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/europa/test_TTrade_filter/factor_value/europa/'
res_ttrade = []
for file in os.listdir(path_trade):
    sys.stdout.write('\r'+str(file))
    sys.stdout.flush()
    if '.h5' in file:
        res_ttrade.append(pd.read_hdf(f'{path_trade}{file}'))
df_ttrade = pd.concat(res_ttrade,axis=1).loc[pd.Timestamp('20170101'): pd.Timestamp('20250630')]
print('')
print('del xbc trade')
df_ttrade = df_ttrade.drop([x for x in df_ttrade.columns if 'xbc' in x], axis=1)

# TTick
print('TTick')
path_tick = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/h5/20250530_zwhtick_filter/'
res_tick = []
for file in os.listdir(path_tick):
    sys.stdout.write('\r'+str(file))
    sys.stdout.flush()
    if '.h5' in file:
        res_tick.append(pd.read_hdf(f'{path_tick}{file}'))
print('')
df_tick = pd.concat(res_tick,axis=1).loc[pd.Timestamp('20170101'): pd.Timestamp('20250630')]

# MD
print('MD')
path_md = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/h5/20250530_zwhmd_filter/'
res_md = []
for file in os.listdir(path_md):
    sys.stdout.write('\r'+str(file))
    sys.stdout.flush()
    if '.h5' in file:
        res_md.append(pd.read_hdf(f'{path_md}{file}'))
df_md = pd.concat(res_md,axis=1).loc[pd.Timestamp('20170101'): pd.Timestamp('20250630')]
print('')
print('del xbc MD')
df_md = df_md.drop([x for x in df_md.columns if 'xbc' in x], axis=1)
# print('del zwh MD')
# df_md = df_md.drop([x for x in df_md.columns if 'zwh' in x], axis=1)
print('del some 1-cv/m2m factor')
df_md = df_md.drop([x for x in df_md.columns if '_1_' in x and any(sub in x for sub in ['cv','skew','kurt','m2m','pos','cct'])], axis=1)

# zjlx
print('zjlx')
path_zjlx = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/h5/20250530_zwhmd_zjlx_filter/'
res_zjlx = []
for file in os.listdir(path_zjlx):
    sys.stdout.write('\r'+str(file))
    sys.stdout.flush()
    if '.h5' in file:
        res_zjlx.append(pd.read_hdf(f'{path_zjlx}{file}'))
df_zjlx = pd.concat(res_zjlx,axis=1).loc[pd.Timestamp('20170101'): pd.Timestamp('20250630')]
print('')
print('del some 1-cv/m2m factor')
df_zjlx = df_zjlx.drop([x for x in df_md.columns if '_1_' in x and any(sub in x for sub in ['cv','skew','kurt','m2m','pos','cct'])], axis=1)

# 5m
print('5M')
path_5m = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/h5/20250530_zwhmd5m_filter/'
res_5m = []
for file in os.listdir(path_5m):
    sys.stdout.write('\r'+str(file))
    sys.stdout.flush()
    if '.h5' in file:
        res_5m.append(pd.read_hdf(f'{path_5m}{file}'))
df_5m = pd.concat(res_5m,axis=1).loc[pd.Timestamp('20170101'): pd.Timestamp('20250630')]
print('')
# emotion
print('emotion')
path_emo = '/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/europa/test_emo1/factor_value/europa/'
res_emo = []
for file in os.listdir(path_emo):
    sys.stdout.write('\r'+str(file))
    sys.stdout.flush()
    if '.h5' in file:
        res_emo.append(pd.read_hdf(f'{path_emo}{file}'))
df_emo = pd.concat(res_emo,axis=1).loc[pd.Timestamp('20170101'): pd.Timestamp('20250630')]
print('')
#
# all + label
df_factor = pd.concat([df_ttrade, df_md, df_tick, df_5m, df_zjlx, df_emo],axis=1)
df_basicinfo = pd.DataFrame(columns = ['type'])
dic_factor_type = {
    'ttrade': df_ttrade,
    'md': df_md,
    'ttick': df_tick,
    '5m': df_5m,
    'zjlx': df_zjlx,
    'emo': df_emo,
}
for df_i in dic_factor_type.keys():
    df_basicinfo_i = pd.DataFrame(index = dic_factor_type[df_i].columns)
    df_basicinfo_i['type'] = df_i
    df_basicinfo = df_basicinfo.append(df_basicinfo_i)
print('df_ttrade :', df_ttrade.shape)
print('df_md :', df_md.shape)
print('df_tick :', df_tick.shape)
print('df_5m :', df_5m.shape)
print('df_zjlx :', df_zjlx.shape)
print('df_emo', df_emo.shape)
basic_file_path = '/data/user/015585/01-因子挖掘/20240624 xdb数据探索/file/basic_europa_20150930_20250710.h5'
df_label = pd.read_hdf(basic_file_path)
df_factor['label_twap'] = df_label['label_twap']

# 剔除一些不稳定的因子
'''
abs_IC > 0.05, 样本外只有原来的0.6以下，算异常
'''
corr = pd.DataFrame(columns = ['2017_2019','2019_2020'])
corr_2017_2019 = df_factor.loc[pd.Timestamp('20170101'): pd.Timestamp('20191231')].corrwith(df_factor['label_twap'].loc[pd.Timestamp('20170101'): pd.Timestamp('20191231')], method = 'spearman')
corr_2019_2020 = df_factor.loc[pd.Timestamp('20190101'): pd.Timestamp('20201231')].corrwith(df_factor['label_twap'].loc[pd.Timestamp('20190101'): pd.Timestamp('20201231')], method = 'spearman')
corr['2017_2019'] = corr_2017_2019
corr['2019_2020'] = corr_2019_2020
del_list1 = list(corr[(corr['2017_2019'] >= 0.05) & (corr['2019_2020'] <= corr['2017_2019']*0.6)].index)
del_list1 = [x for x in del_list1 if 'emo' not in x]
del_list2 = list(corr[(corr['2017_2019'] <= -0.05) & (corr['2019_2020'] >= corr['2017_2019']*0.6)].index)
del_list2 = [x for x in del_list2 if 'emo' not in x]
print('原先总列数：', df_factor.shape[1])
df_factor = df_factor.drop(del_list1 + del_list2, axis=1)
print('剔除后总列数：', df_factor.shape[1])

# 修改列名(重新添加label)，剔除异常值，存储
# df_factor = df_factor.drop(['label_twap'], axis=1)
# columns_name = [f'factor_{i+1}' for i in range(df_factor.shape[1])]
# df_factor.columns = columns_name
# df_factor['label_twap'] = df_label['label_twap']
for col in df_factor.columns:
    df_factor[col] = df_factor[col].replace(np.inf, 1e8).replace(-np.inf, -1e8).fillna(0)

df_factor.to_pickle('/data/user/015585/01-因子挖掘/999-share/for zwh/test_factor4_oriname_emo.pkl')

#
list_trade = list(df_ttrade.columns)
list_tick = list(df_tick.columns)
list_md = list(df_md.columns)
list_5m = list(df_5m.columns)
list_zjlx = list(df_zjlx.columns)
list_trade.sort()
list_tick.sort()
list_md.sort()
list_5m.sort()
list_zjlx.sort()
res_f_name = pd.DataFrame({'name': list_trade + list_tick + list_md + list_5m + list_zjlx})
res_f_name['factor_type'] = ''
res_f_name.loc[res_f_name['name'].isin(list_trade),'factor_type'] = 'trade'
res_f_name.loc[res_f_name['name'].isin(list_tick),'factor_type'] = 'tick'
res_f_name.loc[res_f_name['name'].isin(list_md),'factor_type'] = 'md'
res_f_name.loc[res_f_name['name'].isin(list_5m),'factor_type'] = '5m'
res_f_name.loc[res_f_name['name'].isin(list_zjlx),'factor_type'] = 'zjlx'
res_f_name.to_csv('res_f_name.csv')


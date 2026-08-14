# -*- coding: utf-8 -*-
import pandas as pd
import os
import datetime
import IO
import sys

'''
1、读同花顺个股概念，生成每日的 概念、包含的个股
2、merge上概念热度
3、取每日里，个股所属概念热度的均值/最大值，再叠加是否rank和N日均值，分别作为个股热度因子
'''
# 取数并预处理
path = '/dfs/user/015585/20240327-同花顺概念热度/file_ori/'
ths_basicinfo = pd.read_hdf(path + 'ths_theme_basicinfo.h5')
ths_theme_stock = pd.read_hdf(path + 'ths_theme_stock.h5')
ths_theme_heat = pd.read_hdf(path + 'ths_theme_heat.h5')
ths_theme_stock['addDate'] = ths_theme_stock['addDate'].apply(lambda x : pd.Timestamp(x))
ths_theme_heat['date'] = ths_theme_heat['date'].apply(lambda x : pd.Timestamp(x))
ths_theme_heat.columns = ['dt', 'val2', 'val1', 'label', 'theme_id']
# 取wind数据作为dt,Ticker的基准
md_df = IO.read_data([20160101,20240315],columns=['amt'],
                         alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
theme_list = list(ths_basicinfo['id'].unique())
res_theme_stock_heat = pd.DataFrame(index = md_df.index,columns = theme_list)
idx = pd.IndexSlice
# 将“纳入剔除”的个股所属概念，转为日频
for theme_id, theme_id_stock in ths_theme_stock.groupby('theme_id'):
    sys.stdout.write('\r' + theme_id)
    sys.stdout.flush()
    for code,code_df in theme_id_stock.groupby('code'):
        if len(code_df) > 1:
            print('')
            print('主题{}有code={}不止一行'.format(theme_id,code))
        adddate = code_df['addDate'].values[0]
        res_theme_stock_heat.loc[idx[adddate:, [code]], theme_id] = 1
res_theme_stock_heat = res_theme_stock_heat.stack().reset_index()
res_theme_stock_heat.columns = ['dt','Ticker','theme_id','is_theme_stock']
res_theme_stock_heat.to_pickle('/dfs/user/015585/20240327-同花顺概念热度/file/res_theme_stock.pkl')
res_theme_stock_heat = pd.merge(res_theme_stock_heat,ths_theme_heat[['dt','theme_id','val1']],left_on = ['dt','theme_id'], right_on = ['dt','theme_id'])
res_theme_stock_heat.to_pickle('/dfs/user/015585/20240327-同花顺概念热度/file/res_theme_stock_heat.pkl')
import pandas as pd
import os
import IO
from xquant.thirdpartydata.factordata import FactorData

s = FactorData()




root_path = '/data/group/800080/warehouseJG/prod/DATABASE/SUNTIME/'
# 一致预期
'''
一致预期数据采用H5文件的形式纳入，类似MD，一次提供全部时间范围的数据，后续进行长短期检测
'''
## 逻辑样例：取未发布的最近一期年报，一致预期的净利润/营收，过去20日的均值
data_name = 'DWD_EXP_FORECASTSECU'
df_yzyq = IO.read_data([20160101,20161231], alt = f'{root_path}{data_name}/{data_name}.h5')
df_yzyq_filter = df_yzyq[df_yzyq['FORECASTORTYPE']==1].sort_values(['dt','Ticker','FORECASTYEAR'])
df_yzyq_filter = df_yzyq_filter.groupby(['dt','Ticker']).nth(0) # 此时形成了每日一条的数据
df_yzyq_filter['factor'] = df_yzyq_filter['FORECASTNP'] / df_yzyq_filter['FORECASTOR']
df_yzyq_filter['factor'] = df_yzyq_filter['factor'].unstack().rolling(20,1).mean().stack()

# 卖方预测
data_name = 'DWD_EXP_RESEARCHREPORT'
# df_mfyc = IO.read_data([20160101,20161231], alt = f'{root_path}{data_name}/{data_name}.h5')
df_mfyc = pd.read_pickle('/dfs/group/800463/data/xdb_data_lag3_new/neptune/xdb_researchreport/20160104.pkl')
'''
卖方预测数据采用类似xdb的数据纳入，同时支持_cs场景
'''
df_mfyc = df_mfyc[(df_mfyc['FORECASTQUARTER'] == 4) & (1 - df_mfyc['FORECASTOR'].isna())]  # 只取年报预测，且营收预测非空
df_mfyc['year'] = df_mfyc.index[0][0].year
df_mfyc = df_mfyc[df_mfyc['FORECASTYEAR'] == df_mfyc['year']]  # 预测年份为计算日期对应的年份
res = df_mfyc.groupby(['dt', 'Ticker']).apply(lambda x : x.tail(5)['FORECASTOR'].mean() / x['FORECASTOR'].mean() )







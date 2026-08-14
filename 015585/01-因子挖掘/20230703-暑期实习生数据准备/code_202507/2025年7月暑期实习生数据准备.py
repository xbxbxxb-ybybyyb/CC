import pandas as pd
import numpy as np
import IO
import decimal
import datetime
from xquant.factordata import FactorData
import shutil
import os
s = FactorData()
'''
1、MD数据（全市场，2019）
2、财务基础3表数据（Neptune标的，与因子框架一致，2019）
3、朝阳永续一致预期数据（Neptune标的，与因子框架一致，2019）
4、标签（2019，与因子框架一致，3个中长期标签）
'''
# MD
start_date_ = '20180101'
end_date_ = '20191231'
f_data = IO.read_data([start_date_, end_date_],
                      alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
path = '/dfs/user/015585/999_sharefiles/for_sxs/MD/'
with pd.HDFStore(path + f'MD_{start_date_}_{end_date_}.h5') as h5_store:
    h5_store.put('data', f_data, format='table', append=False, data_columns=True)
    h5_store.get_storer('data').attrs.modification_date = datetime.datetime.today()

# 标签
sft_basic_path = '/data/group/800463/data/projectZZ_public/factor_lib/sft_update_931_20160101_20191231.pkl'  # 这个文件里有label和所有因子
df = pd.read_pickle(sft_basic_path).loc[pd.Timestamp(str(20190101)):pd.Timestamp(str(20191231))]
df = df[['label_t4o30d1','label_t6o30d1']]
df.to_pickle(f'/dfs/user/015585/999_sharefiles/for_sxs/label/label.pkl')

# 朝阳永续卖方预测
root_path = '/dfs/group/800463/data/xdb_data_lag3_new/neptune/'
out_path = '/dfs/user/015585/999_sharefiles/for_sxs/'
data_list = ['xdb_reportratingadj','xdb_reporttargetpriceadj','xdb_researchreport','xdb_researchreportadj']
for data_type in data_list:
    print('卖方预测',data_type)
    if not os.path.exists(f'{out_path}{data_type}/'):
        os.makedirs(f'{out_path}{data_type}/')
    file_list = os.listdir(f'{root_path}{data_type}/')
    file_list.sort()
    file_list = [x for x in file_list if '.pkl' in x and x.startswith('2019')]
    for file in file_list:
        shutil.copy(f'{root_path}{data_type}/{file}', f'{out_path}{data_type}/{file}')

# 朝阳永续一致预期
root_path = '/data/group/800080/warehouseJG/prod/DATABASE/SUNTIME/'
out_path = '/dfs/user/015585/999_sharefiles/for_sxs/'
data_list = ['DWD_EXP_FORECASTSECU',
             'DWD_EXP_FORECASTSCHEDULE',
             'DWD_EXP_FORECASTSECUDERIVED']
for data_type in data_list:
    print('一致预期',data_type)
    if not os.path.exists(f'{out_path}zyyx_yzyq/'):
        os.makedirs(f'{out_path}zyyx_yzyq/')
    df = IO.read_data([20180101,20191231], alt=f'{root_path}{data_type}/{data_type}.h5')
    with pd.HDFStore(f'{out_path}zyyx_yzyq/{data_type}.h5') as h5_store:
        h5_store.put('data', df, format='table', append=False, data_columns=True)
        h5_store.get_storer('data').attrs.modification_date = datetime.datetime.today()



# 财务基础3表数据
root_path = '/dfs/group/800463/data/xdb_data_lag3_new/neptune/'
out_path = '/dfs/user/015585/999_sharefiles/for_sxs/'
data_list = ['xdb_balancesheet','xdb_cashflow','xdb_income']
for data_type in data_list:
    if not os.path.exists(f'{out_path}{data_type}/'):
        os.makedirs(f'{out_path}{data_type}/')
    file_list = os.listdir(f'{root_path}{data_type}/')
    file_list.sort()
    file_list = [x for x in file_list if '.pkl' in x and x.startswith('2019')]
    for file in file_list:
        shutil.copy(f'{root_path}{data_type}/{file}', f'{out_path}{data_type}/{file}')

# T-1日分钟频tick和order
root_path = '/dfs/group/800463/data/xdb_data_lag3_new/neptune/'
out_path = '/dfs/user/015585/999_sharefiles/for_sxs/'
data_list = ['xdb_tick1m','xdb_order1m']
for data_type in data_list:
    print(data_type)
    if not os.path.exists(f'{out_path}{data_type}/'):
        os.makedirs(f'{out_path}{data_type}/')
    file_list = os.listdir(f'{root_path}{data_type}/')
    file_list.sort()
    file_list = [x for x in file_list if '.pkl' in x and x.startswith('2019')]
    for file in file_list:
        shutil.copy(f'{root_path}{data_type}/{file}', f'{out_path}{data_type}/{file}')



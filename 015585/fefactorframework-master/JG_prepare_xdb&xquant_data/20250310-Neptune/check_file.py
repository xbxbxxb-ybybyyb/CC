import os
import pandas as pd
from xquant.factordata import FactorData
'''
检查固定时间段内的缺失文件
'''
xquant_factor_data = FactorData()


start_date = '20170101'
end_date = '20191231'
check_path = '/dfs/group/800463/data/xdb_data_lag3_new/neptune_tmp/'
check_type_list = ['xdb_order', 'xdb_trade', 'xdb_tickex']
check_type_list = ['xdb_tick1m', 'xdb_order1m']
tradingday_list = xquant_factor_data.tradingday(start_date, end_date)

res = {}
for check_type in check_type_list:
    file_list = os.listdir(f'{check_path}{check_type}/')
    file_list = [i.replace('.pkl','') for i in file_list]
    res[check_type] = [i for i in tradingday_list if i not in file_list]
for i in res:
    print(i,len(res[i]))
    print(res[i])

# 检测文件是否可读取
res2 = {}
for i in check_type_list:
    res2[i] = []
# for check_type in check_type_list:
def check_file_read(check_type):
    file_list = os.listdir(f'{check_path}{check_type}/')
    file_list = [i.replace('.pkl','') for i in file_list]
    file_list.sort()

    res2 = []
    for file in file_list:
        try:
            df = pd.read_pickle(f'{check_path}{check_type}/{file}.pkl')
            print(check_type, file)
        except:
            print(f'cant read: {check_type},{file}')
            res2.append(file)
    return {check_type:res2}

from joblib import Parallel, delayed
res = Parallel(n_jobs=3)(delayed(check_file_read)(check_type) for check_type in check_type_list)
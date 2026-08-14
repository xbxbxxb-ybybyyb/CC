import shutil
import os
import pandas as pd

path1_ori = '/dfs/group/800463/data/xdb_data_lag3_new/'
path2_ori = '/dfs/group/800463/data/xdb_data_lag3_test/'
strategy_list = ['europa_jupiter', 'saturn_sell', 'mimas', 'metis']
data_type_list = ['xdb_trade', 'xdb_order', 'xdb_tickex']
for strategy in strategy_list:
    for data_type in data_type_list:
        if data_type == 'xdb_tickex':
            file_list = os.listdir(f'{path1_ori}{strategy}/{data_type}/')
            file_list.sort()
            for file in file_list:
                if not os.path.exists(f'{path2_ori}{strategy}/{data_type}/{file}'):
                    print(f'{path2_ori}{strategy}/{data_type}/{file}')
                    shutil.copyfile(f'{path1_ori}{strategy}/{data_type}/{file}', f'{path2_ori}{strategy}/{data_type}/{file}')
        else:
            file_list = os.listdir(f'{path1_ori}{strategy}/{data_type}/')
            file_list.sort()
            for file in file_list:
                if (not os.path.exists(f'{path2_ori}{strategy}/{data_type}/{file}')) and (file < '20170110.pkl'):
                    print(f'{path2_ori}{strategy}/{data_type}/{file}')
                    shutil.copyfile(f'{path1_ori}{strategy}/{data_type}/{file}', f'{path2_ori}{strategy}/{data_type}/{file}')
# ## 比对文件缺失情况
# for strategy in strategy_list:
#     list1 = os.listdir(f'{path2_ori}{strategy}/xdb_tickfull')
#     list2 = os.listdir(f'{path2_ori}{strategy}/xdb_tickfulladdorder')
#     print(strategy, set(list1) - set(list2))
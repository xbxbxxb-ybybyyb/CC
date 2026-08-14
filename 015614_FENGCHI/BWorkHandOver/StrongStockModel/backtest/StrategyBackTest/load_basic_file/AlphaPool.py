# @Time : 2021/2/3 9:12
# @Author : Zhichen Lu
# @File : AlphaPool.py
import os
import pandas as pd
pool_path = '/data/group/800319/strategy_local_path/code_list4/'
pool_list = sorted(os.listdir(pool_path))

alpha_pool = {}
for each in pool_list:
    temp_code_list = pd.read_pickle(pool_path+each)
    temp_code_list = [int(x[:-3]) for x in temp_code_list]
    temp_pool = pd.Series(True,index=temp_code_list)
    alpha_pool[int(each[:-4])] = temp_pool

alpha_pool = pd.DataFrame(alpha_pool).T.fillna(False)
pd.to_pickle(alpha_pool,'/data/group/800319/信号存储/alpha_pool_202101.pkl')
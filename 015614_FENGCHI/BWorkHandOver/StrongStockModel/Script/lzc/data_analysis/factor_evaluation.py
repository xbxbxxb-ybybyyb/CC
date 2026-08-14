# @Time : 2020/9/21 16:05
# @Author : Zhichen Lu
# @File : factor_evaluation.py

import pandas as pd
import os
from multiprocessing import Pool, Manager
eval_res_path =  output_address = '/data/group/800319/Strong_stock/5min_TsNorm%d_StrongTest/' % 40#'/data/group/800319/Strong_stock/Fix_TsNorm40_StrongTest/'
file_list = os.listdir(eval_res_path)
file_list = list(filter(lambda x : x.endswith('.xlsx'),file_list))

# ic_res = Manager().dict()

# def get_ic(file_name):
#     res = pd.read_excel(eval_res_path+file_name,'ic',index_col=0)
#     val = res.loc[:20181231][1].mean()
#     print(file_name)
#     return val

def get_ic_yearly(file_name):
    res = pd.read_excel(eval_res_path + file_name, 'ic')#.set_index('end_date')
    res['year'] = res['end_date'].apply(lambda x : x//10000)
    res = res.set_index('year')
    val = res.loc[:2018][1].apply(abs)
    print(file_name)
    return val

pool_dict = {}
pool = Pool(20)
for each in file_list:
    pool_dict[each] = pool.apply_async(get_ic_yearly,(each,))
pool.close()
pool.join()

res_dict = {}
for each in pool_dict:
    try:
        res_dict[each.replace('.xlsx','')] = pool_dict[each].get()
    except:
        print(each,'wrong')
        res_dict[each] = get_ic_yearly(each)
# ic_res = pd.DataFrame(res_dict).shift()
ic_res = pd.DataFrame(res_dict).loc[:2018].mean().apply(abs).sort_values(ascending=False)
pd.to_pickle(ic_res,'/data/group/800319/Strong_stock/ic_sort_yearly_avg_window40.pkl')
check = ic_res.sort_index().loc['9000':].sort_values(ascending=False)
# @Time : 2020/8/18 19:32
# @Author : Zhichen Lu
# @File : factor_preprocess.py

import sys
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')

import os
from multiprocessing import Pool
from StrongStockModel.dataApi.TrueSendFactorTest import _get_fix_factor_list
from StrongStockModel.dataApi.usefulTools import *
from StrongStockModel.conf.path_config import root_path
import gc
from tqdm import tqdm
import datetime

"""
for N in [10,20,40,60,80,120,240,480]:
    N = 5
    factor_out_path = root_path + 'processed_factor_by_factor/ts_norm_%d/'%N
#     factor_out_path = '/data/group/800319/junkData/StrongStock/processed_factor_by_factor/ts_norm_%d/'%N
#     factor_out_path = '/data/group/800319/junkData/StrongStock/processed_factor_all_pool_by_date/ts_norm_%d/'%N
    if not os.path.exists(factor_out_path):
        continue
    junk_list = os.listdir(factor_out_path)
    for each in junk_list:
        os.remove(factor_out_path + each)
"""

def get_factor(factor_name):
    if os.path.exists(factor_out_path + '%s.h5' % factor_name):
        print(factor_name, 'exist')
        return 0
    point_df_list = []
    for point in point_list:
        point_factor = 'Fix%d_' % point + factor_name
        factor = pd.read_hdf(factor_path + point_factor + '.h5', point_factor)
        factor.index = pd.MultiIndex.from_tuples([(x, point) for x in factor.index])
        point_df_list.append(factor)
    factor = pd.concat(point_df_list).sort_index()
    std_arr = factor.apply(lambda x: x.dropna().rolling(N * 7).std().reindex(x.index))  # factor.rolling(7 * N).std()
    std_arr[std_arr.eq(0)] = 1e-4
    mean_arr = factor.apply(lambda x: x.dropna().rolling(N * 7).mean().reindex(x.index))
    preprocessed_factor = (factor - mean_arr) / std_arr
    preprocessed_factor.to_hdf(factor_out_path + '%s.h5' % factor_name, factor_name, format='t')
    del factor, std_arr, preprocessed_factor, mean_arr
    gc.collect()
    # return val_list

def wraper(factor_name):
    if os.path.exists(factor_out_path + factor_name):
        print(factor_name, 'exist')
        return True
    try:
        get_factor(factor_name)
        print(factor_name, 'done')
        return True
    except:
        pd.DataFrame().to_csv(factor_out_path + 'Wrong_%s.csv' % factor_name)
        print(factor_name, 'Wrong')
        return False


# get_factor('FactorMin130_meandivstd')
period_list = [10, 20, 40, 60, 80, 120, 240, 480]
N = 20
factor_list = _get_fix_factor_list()
factor_path = '/data/group/800319/VeryJunkFix/'
factor_out_path = root_path + 'processed_factor_by_factor/ts_norm_%d/' % N

if not os.path.exists(factor_out_path):
    os.mkdir(factor_out_path)
point_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
import time

e = time.time()
wraper(factor_list[-1])
print('one time:', time.time() - e)
"""
pbar = tqdm(total=len(factor_list))
def update(*param):
    pbar.update()
    pbar.set_description('preprocessing %d |%s|%s' % (N,str(factor_list[pbar.last_print_n - 1]), datetime.datetime.now().strftime('%H:%M:%S')))
    if pbar.last_print_n == len(factor_list):
        pbar.close()

pool = Pool(24)
# plt_factor(factor_list[0])
# pool.map(wraper, factor_list)
pool_dict = {}
for fct_name in factor_list:
    pool_dict[fct_name] = pool.apply_async(wraper,(fct_name,), callback=update)
pool.close()
pool.join()

for each in pool_dict:
    try:
        pool_dict[each] = pool_dict[each].get()
    except:
        print(each,'wrong')
"""

"""
# def plt_factor(factor_name):
#     if os.path.exists(factor_out_path + '%s.h5' % factor_name):
#         print(factor_name, 'exist')
#         return 0
#     import matplotlib.pyplot as plt
#     import seaborn as sns
#     check = get_factor(factor_name)
#     check = pd.Series(check).replace(np.inf, np.nan).replace(-np.inf, np.nan).dropna().tolist()
#     sns.distplot(check, bins=50)
#     plt.title(factor_name)
#     plt.savefig(fig_out_path + '%s.png' % factor_name)
#     plt.show()
#     del check
#     gc.collect()
#     print(factor_name, 'done')
#     return 1
# fig_out_path = root_path + 'fix_factor_dist_ts_norm/'
# if not os.path.exists(fig_out_path):
#     os.mkdir(fig_out_path)
"""

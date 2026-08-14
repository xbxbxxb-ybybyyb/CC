# @Time : 2020/11/3 9:50
# @Author : Zhichen Lu
# @File : factor_preprocess_out_of_sample.py

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
from dataApi.tradeDate import get_date_range
in_sample_date_list = get_date_range(20140101,20190628)
idx = in_sample_date_list.index(20181228)
split_date = in_sample_date_list[idx-60]

# def get_in_sample_factor(factor_name):
#     point_df_list = []
#     for point in point_list:
#         point_factor = 'Fix%d_' % point + factor_name
#         factor = pd.read_hdf(in_sample_factor_path + point_factor + '.h5', point_factor,start=idx-60)
#         factor.index = pd.MultiIndex.from_tuples([(x, point) for x in factor.index])
#         point_df_list.append(factor)
#     factor = pd.concat(point_df_list).sort_index()
#     return factor

def get_out_sample_factor(factor_name):
    if os.path.exists(factor_out_path + '%s.h5' % str(factor_name).zfill(4)):
        try:
            _ = pd.read_hdf(factor_out_path + '%s.h5' % str(factor_name).zfill(4), str(factor_name).zfill(4), start=0, stop=2)
            print(factor_name, 'exist')
            return 0
        except:
            os.remove(factor_out_path + '%s.h5' % str(factor_name).zfill(4))
    point_df_list = []
    for point in point_list:
        point_factor = 'Fix%d_' % point + factor_name
        factor = pd.read_pickle(factor_path + point_factor + '.pkl')
        factor.index = factor.index.astype(int)
        factor = factor.loc[split_date:]
        factor.index = pd.MultiIndex.from_tuples([(x, point) for x in factor.index])
        factor.columns = [int(x[:-3]) for x in factor.columns]
        point_df_list.append(factor)
    factor = pd.concat(point_df_list).sort_index()
    return factor

def get_factor(factor_name):
    if os.path.exists(factor_out_path + '%s.h5' % factor_name):
        print(factor_name, 'exist')
        return 0
    # in_sample_factor = get_in_sample_factor(factor_name)
    factor = get_out_sample_factor(factor_name)
    std_arr = factor.apply(lambda x: x.dropna().rolling(N * 7).std().reindex(x.index))  # factor.rolling(7 * N).std()
    std_arr[std_arr.eq(0)] = 1e-4
    mean_arr = factor.apply(lambda x: x.dropna().rolling(N * 7).mean().reindex(x.index))
    preprocessed_factor = (factor - mean_arr) / std_arr
    preprocessed_factor = preprocessed_factor.loc[20190701:]
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


get_factor('FactorMin130_meandivstd')
# period_list = [10, 20, 40, 60, 80, 120, 240, 480]
N = 40
factor_list = _get_fix_factor_list()
# in_sample_factor_path = '/data/group/800319/VeryJunkFix/'
factor_path = '/data/group/800002/alpha_factor/lib/x_factor_lib/'
factor_out_path = root_path + 'processed_factor_by_factor/ts_norm_%d_out_of_sample/' % N

if not os.path.exists(factor_out_path):
    os.mkdir(factor_out_path)
point_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
import time

#e = time.time()
#wraper(factor_list[0])
#print('one time:', time.time() - e)

# partition = 4
# i = 1
# factor_list = factor_list[(i-1)*len(factor_list)//partition:i*len(factor_list)//partition]

pbar = tqdm(total=len(factor_list))
def update(*param):
    pbar.update()
    pbar.set_description('preprocessing %d |%s|%s' % (0,str(factor_list[pbar.last_print_n - 1]), datetime.datetime.now().strftime('%H:%M:%S')))
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
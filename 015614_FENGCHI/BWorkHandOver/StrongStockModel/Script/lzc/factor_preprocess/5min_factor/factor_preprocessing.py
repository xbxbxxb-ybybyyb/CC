# @Time : 2020/10/14 9:55
# @Author : Zhichen Lu
# @File : factor_preprocessing.py

import sys
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
import numpy as np
import itertools
import os
from StrongStockModel.conf.path_config import root_path
import gc
from multiprocessing import Pool
from tqdm import  tqdm
import datetime
from xquant.compute.aimr import AIMR

source_path = '/data/group/800319/junkBigFactor/'
file_list = os.listdir(source_path)
file_list = list(filter(lambda x :x.startswith('05') or x.startswith('06') or x.startswith('07') or x.startswith('08'),file_list))
# file_list = list(filter(lambda x : x.startswith('00') or x.startswith('95') or x.startswith('91') or x.startswith('90') or
#                                                    x.startswith('04') or x.startswith('05') or x.startswith('06') or x.startswith('07') or x.startswith('08') or
#                                    x.startswith('1') or x.startswith('2'),file_list))
date_list = np.load(source_path+'date_list.npy')
code_list = np.load(source_path+'code_list.npy')
time_list = np.load(source_path+'time_list.npy')

def get_factor(factor_id):
    factor = np.load(source_path + str(factor_id).zfill(4)+'.npy')
    factor = factor.reshape((factor.shape[0] * factor.shape[1], factor.shape[2]))
    factor = pd.DataFrame(factor, index=pd.MultiIndex.from_tuples(list(itertools.product(date_list, time_list))), columns=code_list)
    return factor

def process_factor(factor_name):
    if os.path.exists(factor_out_path + '%s.h5' % str(factor_name).zfill(4)):
        try:
            _=pd.read_hdf(factor_out_path + '%s.h5' % str(factor_name).zfill(4), str(factor_name).zfill(4),start=0,stop=2)
            print(factor_name, 'exist')
            return 0
        except:
            os.remove(factor_out_path + '%s.h5' % str(factor_name).zfill(4))
    factor = get_factor(factor_name)
    std_arr = factor.apply(lambda x: x.dropna().rolling(N*48).std().reindex(x.index))#factor.rolling(48 * N).std()
    std_arr[std_arr.eq(0)] = 1e-4
    mean_arr = factor.apply(lambda x: x.dropna().rolling(N*48).mean().reindex(x.index))
    preprocessed_factor = (factor - mean_arr) / std_arr
    preprocessed_factor.to_hdf(factor_out_path + '%s.h5' % str(factor_name).zfill(4), str(factor_name).zfill(4), format='t')
    del factor, std_arr, preprocessed_factor,mean_arr
    gc.collect()

def wraper(factor_name):
    try:
        process_factor(factor_name)
        print(factor_name,'done')
    except:
        print(factor_name,'Wrong')

N = 40
factor_out_path = root_path + 'processed_factor_by_factor_5min/ts_norm_%d/'%N
if not os.path.exists(factor_out_path):
    os.mkdir(factor_out_path)




# wraper(1858)

id_list = list(map(lambda x : int(x[:4]),file_list))
id_list = list(filter(lambda x : not os.path.exists(factor_out_path + '%s.h5' % str(x).zfill(4)),id_list))

partition = 3
idx = 1#int(AIMR.getParam())

id_list = id_list[(idx-1)*len(id_list)//partition:idx*len(id_list)//partition]

process_factor(id_list[0])


"""

pbar = tqdm(total=len(id_list))
def update(*param):
    pbar.update()
    pbar.set_description('preprocessing %d |%s|%s' % (N,pbar.last_print_n - 1, datetime.datetime.now().strftime('%H:%M:%S')))
    if pbar.last_print_n == len(id_list):
        pbar.close()

pool = Pool(min(len(id_list),24))
# plt_factor(factor_list[0])
# pool.map(wraper, factor_list)
pool_dict = {}
for fct_name in id_list:
    pool_dict[fct_name] = pool.apply_async(wraper,(fct_name,), callback=update)
pool.close()
pool.join()

for each in pool_dict:
    try:
        pool_dict[each] = pool_dict[each].get()
    except:
        print(each,'wrong')

"""
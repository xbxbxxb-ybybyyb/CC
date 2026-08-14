# @Time : 2020/10/20 16:28
# @Author : Zhichen Lu
# @File : IntegrationReload.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import os
import pandas as pd
from dataApi.tradeDate import get_date_range
from conf.path_config import root_path
from multiprocessing import Pool
import gc
from System.LoadFactor.FactorDataSet import FactorDataSet
from tqdm import tqdm
import datetime

N = 40

preprocessed_by_date_path1 = root_path + 'processed_factor_all_pool_by_date/binary_feature/'
preprocessed_by_date_path2 = root_path + 'processed_factor_all_pool_by_date/ts_norm_%d/' % N
preprocessed_by_date_path = root_path + 'processed_factor_all_pool_by_date/ts_norm_%d_and_binary/' % N

if not os.path.exists(preprocessed_by_date_path):
    os.mkdir(preprocessed_by_date_path)

date_list = get_date_range(20140101, 20181231)

def merg_data(date):
    if os.path.exists(preprocessed_by_date_path+'%d.h5'%date):
        print(date,'exist')
        return True
    conitual_data = pd.read_hdf(preprocessed_by_date_path2+'%d.h5'%date,str(date))
    disceret_data = pd.read_hdf(preprocessed_by_date_path1+'%d.h5'%date,str(date))

    data = pd.concat([conitual_data,disceret_data],axis=1)
    data.to_hdf(preprocessed_by_date_path+'%d.h5'%date,str(date),format='t')
    print(date,'done')
    return True
merg_data(20181220)

pbar = tqdm(total=len(date_list))
def update(*param):
    pbar.update()
    pbar.set_description('preprocessing %d |%s|%s' % (N,str(date_list[pbar.last_print_n - 1]), datetime.datetime.now().strftime('%H:%M:%S')))
    if pbar.last_print_n == len(date_list):
        pbar.close()


pool = Pool(24)
pool_dict = {}
for date in date_list:
    pool_dict[date] = pool.apply_async(merg_data,(date,))
# pool.map(load_by_date, date_list)
pool.close()
pool.join()

for date in pool_dict:
    pool_dict[date] = pool_dict[date].get()
    if not pool_dict[date]:
        print(date,'Wrong')


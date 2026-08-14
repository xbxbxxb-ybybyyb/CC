# coding: utf-8
# Author：fengchi863
# Date ：2022/9/28 15:01

from dataApi import tradeDate
from LucienUtil.IO import pd_hdf5_writer
import pandas as pd
from tqdm import tqdm
import time
import warnings
warnings.filterwarnings('ignore')

# jupiter 或 europa
strategy_name = 'jupiter'

# 历史全量数据
start_date = 20150101
end_date = 20220927

date_list = tradeDate.get_date_range(start_date, end_date)

data_path = f'/data/user/015614/daily/basic/basic_wind_sw_history/BlockData/daily_max_pctchg_concept/{strategy_name}/'

t1 = time.time()
res_df = pd.DataFrame()
for dat in tqdm(date_list):
    tmp_df = pd.read_pickle(data_path + f'{dat}.pkl')
    res_df = pd.concat([res_df, tmp_df], axis=0)
print('耗时：', time.time() - t1)

pd_hdf5_writer(pd_factor=res_df, hdf5=f'/data/group/800463/fengc/daily/concept/{strategy_name}_concept.h5', dataset='concept')

# 测试读取
# from LucienUtil.IO import read_data
# check = read_data([20150101, 20150130], alt='/data/group/800463/fengc/daily/concept/jupiter_concept.h5')


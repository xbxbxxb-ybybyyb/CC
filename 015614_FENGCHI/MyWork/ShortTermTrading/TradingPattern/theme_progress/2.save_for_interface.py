# coding: utf-8
# Author：fengchi863
# Date ：2020/12/17 16:21
import h5py
import pandas as pd, numpy as np
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore")  # 减少NaturalNameWarning的输出

shouyinfanbao_root_path = '/data/user/fengchi/首阴反包_WIND全A/'
hdf_name = 'Active_stock.h5'
f = h5py.File(shouyinfanbao_root_path + hdf_name)
active_concept_list2020 = list(f.keys())
print('共有%d个活跃板块' % len(active_concept_list2020))

concept_code = active_concept_list2020[0]
active_stock = pd.read_hdf(shouyinfanbao_root_path + hdf_name, key=concept_code)
active_stock = active_stock.rolling(10).sum() > 0
all_mkt_active_stock_df = active_stock

# 用于储存接口数据
for concept_code in tqdm(active_concept_list2020):
    active_stock = pd.read_hdf(shouyinfanbao_root_path + hdf_name, key=concept_code)
    active_stock = active_stock.rolling(10).sum() > 0
    all_mkt_active_stock_df = all_mkt_active_stock_df | active_stock
    active_stock.to_hdf('/data/group/800319/fengchi/interface/active_concept_data_windallA/active_concept_data.h5', key=concept_code, format='t')

# 储存全市场的rolling10以后的活跃个股，这个是用来给鲁植宸的
save_path = '/data/group/800319/fengchi/interface/active_concept_data_windallA/daily_active_stock.pkl'
all_mkt_active_stock_df.to_pickle(save_path)

# 储存处理后的Active_concept，这一步只是转移文件储存位置
read_path = '/data/user/fengchi/首阴反包_WIND全A/Active_concept.h5'
active_concept = pd.read_hdf(read_path, key='Active_concept')
active_concept.to_hdf('/data/group/800319/fengchi/interface/active_concept_data_windallA/daily_active_concept.h5', key='daily_active_concept', format='t')


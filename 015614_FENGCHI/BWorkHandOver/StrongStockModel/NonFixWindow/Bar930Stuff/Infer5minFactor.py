# @Time : 2022/3/16 14:24
# @Author : Zhichen Lu
# @File : Infer5minFactor.py

import pandas as pd
import numpy as np
import itertools
from dataApi.FixFactorRollPrepare import load_fix_data,feature_engineering,infer_nolimit_pool,\
    load_5min_8bar_with_selfdeined_label,load_5min_data,load_fix_data_selfdefined_label
from dataApi.tradeDate import get_pre_trade_date
import gc
from dataApi.tradeDate import trade_minutes
import time,os

start,end = get_pre_trade_date(20150105), get_pre_trade_date(20150105,-40)

factor_list = [x.replace('.npy','') for x in sorted(os.listdir('/arch1/group/800442/800319/MinFactorSuper/FactorData/Factor/'))[:20]]
label_path ='/data/group/800442/800319/HFfactor/ForDerivativeLabel8BarFor5MinsV47_keep5/data//future_1_bar.npy'
feature_path ='/arch1/group/800442/800319/MinFactorSuper/FactorData/Factor/'
freq = 47

X, y, nolimit, idx_date, idx_code, idx_time,y_1day,y1day_origin = load_5min_8bar_with_selfdeined_label(start_date=start,end_date=end,
                factor_list=factor_list,return_1day_label=True,
                label_path=label_path,address=feature_path,freq=freq)
y[np.isnan(y)] = 0
X, y, idx_date, idx_code, idx_time,y_1day,y1day_origin = feature_engineering(X, y, nolimit, idx_date, idx_code, idx_time,y_1day,y1day_origin,limit=2)

index = pd.MultiIndex.from_tuples(list(zip(idx_date,idx_time,idx_code)))
factor_8bar = pd.DataFrame(X,index=pd.MultiIndex.from_tuples(zip(idx_date,idx_time,idx_code)),columns=factor_list)
factor_8bar['label'] = y
factor_8bar['label_8bar'] = y_1day
factor_8bar['label_origin'] = y1day_origin


# X, y, nolimit, idx_date, idx_code, idx_time,y_1day = load_fix_data_selfdefined_label(start_date=start,end_date=end,
#                 factor_list=['Beta300'],return_1day_label=True,
#                 label_path='/data/group/800442/800319/HFfactor/ForDerivativeLabel8Bar_keep5/data/future_1_bar.npy')

X, y, nolimit, idx_date, idx_code, idx_time = load_fix_data(start_date=start,end_date=end,
            factor_list=factor_list,address='/arch1/group/800442/800319/MinFactorSuper/FactorFixData/Factor/')
X, y, idx_date, idx_code, idx_time = feature_engineering(X, y, nolimit, idx_date, idx_code, idx_time,limit=2)
index = pd.MultiIndex.from_tuples(list(zip(idx_date,idx_time,idx_code)))
feature_fix = pd.DataFrame(X,index=index,columns=factor_list)
feature_fix['label'] = y
# feature_fix['label_origin'] = y_1day

index = set(feature_fix.index).intersection(set(factor_8bar.index))
feature_fix,factor_8bar = feature_fix.loc[sorted(index)],factor_8bar.loc[sorted(index)]
compare = pd.DataFrame({
    'old':feature_fix['label'],
    'new':factor_8bar['label']
})


targe_time_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430, 1455]
X, y, nolimit, idx_date, idx_code, idx_time = load_fix_data(start_date=start,end_date=end,
                factor_list=factor_list,address=feature_path,freq=freq)
X, y, idx_date, idx_code, idx_time = feature_engineering(X, y, nolimit, idx_date, idx_code, idx_time)
factor_from_origin = pd.DataFrame(X,index=pd.MultiIndex.from_tuples(zip(idx_date,idx_time,idx_code)),columns=factor_list)
factor_from_origin['label'] = y



check_origin = factor_from_origin.loc[[20151228]]
check_api = factor_8bar.loc[[20151228]]
check_origin = check_origin.loc[check_api.index]

factor_from_origin = factor_from_origin.loc[factor_8bar.index].dropna()
factor_8bar = factor_8bar.loc[factor_from_origin.index]

x = 1
base_path = f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/NonFix8BarWith930Use5Mins/Future_{x}_bar/XGB_5mins_ic_d_train200_test10_factor_num400/XGB_5mins_ic_d_train200_test10_factor_num400/'


from tqdm import tqdm
file_list = sorted(os.listdir(base_path))
for each in tqdm(file_list):
    temp = pd.read_pickle(f'{base_path}{each}')
    temp_val = pd.read_pickle(f'{base_path[:-1]}_val_pred/{each}')
    break
    # max_entries = temp.groupby(level=[0,1,2]).size().max()
    # if temp.groupby(level=[0,1,2]).size().max()>1:
    #     print(each,max_entries)



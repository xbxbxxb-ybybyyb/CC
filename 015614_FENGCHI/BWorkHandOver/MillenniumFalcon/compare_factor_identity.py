# @Time : 2021/11/15 14:54
# @Author : Zhichen Lu
# @File : compare_factor_identity.py
import numpy as np
import pandas as pd
from MillenniumFalcon.basic_conf import _code_list,_date_list
from dataApi.tradeDate import get_date_range,get_recent_trade_date
from dataApi.stockList import get_all_stock_ever_appear
import itertools

path1 = '/data/group/800442/800319/HFfactor/CrossIndutryMean/'
path2 = '/data/group/800442/800319/HFfactor/CrossIndutryMeanNoShift/'
factor_name = 'FactorMin289_mean_re'

bar_list = [1000,1030,1100,1300,1330,1400,1430]
code_list2 = get_all_stock_ever_appear(get_recent_trade_date(20141231))
date_list2 = get_date_range(20140701,get_recent_trade_date(20141231))
factor_name = 'zhy_fix_5'
factor1 = np.load(f'{path1}data_3d_arr/{factor_name}.npy')
factor2 = np.load(f'{path2}data_3d_arr/{factor_name}.npy')
index1 = pd.MultiIndex.from_tuples(list(itertools.product(_date_list,bar_list)))
index2 = pd.MultiIndex.from_tuples(list(itertools.product(date_list2,bar_list)))

factor1_df = pd.DataFrame(factor1.reshape(factor1.shape[0]*7,factor1.shape[-1]),index=index1,columns=_code_list)
factor2_df = pd.DataFrame(factor2.reshape(factor2.shape[0]*7,factor2.shape[-1]),index=index2,columns=code_list2).fillna(0)
factor1_val = factor1_df.reindex(factor2_df.index,axis=0).reindex(factor2_df.columns,axis=1).fillna(0)

shape = (factor1_val.shape[0]//7,7,factor1_val.shape[-1])
val1,val2 = factor1_val.values.reshape(shape),factor2_df.values.reshape(shape)

date_idx = np.ones_like(val1).astype(int)
time_idx = np.ones_like(val1).astype(int)
code_idx = np.ones_like(val1).astype(int)
for idx,date in enumerate(date_list2):
    date_idx[idx,:,:] = date
for idx,code in enumerate(code_list2):
    code_idx[:,:,idx] = code
for idx,time in enumerate(bar_list):
    time_idx[:,idx,:] = time

non_identical = ~np.isclose(val1,val2)

non_identical_idx_list = list(zip(date_idx[non_identical],time_idx[non_identical],code_idx[non_identical]))

abs(val2[non_identical]-val1[non_identical]).max()

# factor1_arr = np.memmap(f'{path1}data/{factor_name}.npy',mode='r',offset=128,dtype='float32')
path1 = '/data/group/800442/800319/HFfactor/CrossIndutryMean20211104/'
path2 = '/data/group/800442/800319/HFfactor/CrossIndutryMeanShift/'
factor_name = 'FactorMin289_mean_re'
idx_date = np.load('/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/idx_date.npy')
idx_time = np.load('/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/idx_time.npy')
idx_code = np.load('/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/idx_code.npy')
time_len = idx_time.shape[0]
idx_date = np.concatenate([idx_date[:,None] for i in range(time_len)],axis=-1).flatten()
idx_code = np.concatenate([idx_code[:,None] for i in range(time_len)],axis=-1).flatten()
idx_time = np.concatenate([idx_time[None,:] for i in range(idx_code.shape[0])],axis=0).flatten()

factor1 = np.memmap(f'{path1}data/{factor_name}.npy',dtype='float32',offset=128)
factor2 = np.memmap(f'{path2}data/{factor_name}.npy',dtype='float32',offset=128)
shape = min(factor2.shape[0],factor1.shape[0])

idx_date = idx_date[:shape]
idx_code = idx_code[:shape]
idx_time = idx_time[:shape]
factor1,factor2 = factor1[:shape],factor2[:shape]
finit1,finit2 = np.isfinite(factor1),np.isfinite(factor2)
non_identical = finit1!=finit2
non_identical_idx = list(zip(idx_date[non_identical],idx_time[non_identical],idx_code[non_identical]))
sorted(set(idx_date[non_identical]))
# finit1[finit1!=finit2]
# finit2[finit1!=finit2]
# factor2[finit1!=finit2]
# factor1[finit1!=finit2]
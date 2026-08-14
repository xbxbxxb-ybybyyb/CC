# @Time : 2021/3/31 9:04
# @Author : Zhichen Lu
# @File : FixlizeDailyFactorLoading.py
import pandas as pd
import numpy as np
from dataApi.tradeDate import get_pre_trade_date,get_date_range
from dataApi.getData import trans_windcode2int

data_path = '/data/group/800319/FixlizeDailyFactor/dataShift/'
index = pd.read_pickle('/data/group/800319/FixlizeDailyFactor/index20140801_20200717.pkl')
idx_date,idx_time,idx_code = zip(*tuple(index))

def loadFixlizedDailyFactor(factor_list, start, end, path=data_path):
    start_idx = idx_date.index(start)
    try:
        end_idx = idx_date.index(get_pre_trade_date(end,-1))
    except:
        print(1)
    features = np.empty((end_idx-start_idx,len(factor_list)))
    for idx,factor in enumerate(factor_list):
        temp = np.memmap(path+'%s.npy'%factor,dtype='float32',mode='r',offset=128)
        features[:,idx] = temp[start_idx:end_idx]
    return features,list(zip(idx_date[start_idx:end_idx],idx_time[start_idx:end_idx],idx_code[start_idx:end_idx]))


#
# e = time.time()
# factor = load_data(factor_list,data_path,20151225,20160129)
# used_time = time.time() - e
# factor = pd.DataFrame(factor[0],index = pd.MultiIndex.from_tuples(factor[1]),columns=factor_list)
#
# MinRVM = factor['MinRVM'].unstack()
# MinRVM_origin = pd.read_pickle('/data/group/800080/FactorFactory/PICKLE_DAY/MinRVM.pkl')
# MinRVM = MinRVM.groupby(level=0).mean()
# MinRVM_origin.index = MinRVM_origin.index.astype(int)
# MinRVM_origin = MinRVM_origin.loc[20151225:20160129]
# MinRVM_origin.columns = MinRVM_origin.columns.map(trans_windcode2int)
# check = MinRVM - MinRVM_origin

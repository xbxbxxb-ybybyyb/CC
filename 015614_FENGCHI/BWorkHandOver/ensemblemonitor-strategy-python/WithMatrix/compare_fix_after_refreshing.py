# @Time : 2021/11/3 15:47
# @Author : Zhichen Lu
# @File : compare_fix_after_refreshing.py
import pandas as pd
import numpy as np
from dataApi.FixFactorRollPrepare import load_fix_data,feature_engineering,load_fix_mv
from dataApi.getData import trans_int2windcode


X, y, nolimit, idx_date, idx_code, idx_time = load_fix_data(start_date=20210406,end_date=20210415,factor_list=['AbnormalPriceDiff'])
X2, y2, nolimit2, idx_date2, idx_code2, idx_time2 = load_fix_data(start_date=20210406,end_date=20210415,factor_list=['AbnormalPriceDiff'],
                                                                  address='/data/group/800442/800319/HFfactor/RealTimeFix_test/data/')


X, y, idx_date, idx_time,idx_code = feature_engineering(X, y, nolimit, idx_date, idx_code, idx_time)
X2, y2, idx_date2, idx_code2, idx_time2 = feature_engineering(X2, y2, nolimit2, idx_date2, idx_code2, idx_time2)


mean, std, idx_date, idx_code = load_fix_mv(start_date=20210406,end_date=20210415,factor_list=['AbnormalPriceDiff'],
                                            address='/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/')
mean2, std2, idx_date2, idx_code2 = load_fix_mv(start_date=20210406,end_date=20210415,factor_list=['AbnormalPriceDiff'],
                                                address='/data/group/800442/800319/HFfactor/RealTimeFix_test/')
mean = pd.Series(mean[0,:],index=pd.MultiIndex.from_tuples(list(zip(idx_date.tolist(),idx_code.tolist())))).unstack()
std = pd.Series(std[0,:],index=pd.MultiIndex.from_tuples(list(zip(idx_date,idx_code)))).unstack()
mean2 = pd.Series(mean2[0,:],index=pd.MultiIndex.from_tuples(list(zip(idx_date2,idx_code2)))).unstack()
std2 = pd.Series(std2[0,:],index=pd.MultiIndex.from_tuples(list(zip(idx_date2,idx_code2)))).unstack()

mean2.columns = mean2.columns.map(trans_int2windcode)
old_mean = pd.read_pickle(f'/data/group/800442/800319/strategy_local_path3_backup20210519/factor_hyper_param/mean20210402.pkl')
new_mean = pd.read_pickle(f'/data/group/800319/strategy_local_path3_ForMatrix/factor_hyper_param/mean20210402.pkl')

col = list(set(old_mean.columns).intersection(set(new_mean.columns)))



compare = pd.DataFrame({
'old':old_mean.loc['AbnormalPriceDiff',col],
'new':new_mean.loc['AbnormalPriceDiff',col],
'offline':mean2.loc[20210406,col]
})

compare = pd.DataFrame({})



X, y, nolimit, idx_date, idx_code, idx_time = load_fix_data(start_date=20140801,end_date=20210531,factor_list=['zhy_fix_5'])

np.isclose(X,factor_df.loc[(20210406,1000),20])
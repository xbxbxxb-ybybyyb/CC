# @Time : 2022/3/15 19:42
# @Author : Zhichen Lu
# @File : tst_api.py
from dataApi.FixFactorRollPrepare import load_fix_data,feature_engineering
import pandas as pd
X, y, nolimit, idx_date, idx_code, idx_time = load_fix_data(20170101,20171231,['20201209152417623'],freq=48,address='/arch1/group/800442/800319/HFfactor/DTC2021/data/')
X, y, idx_date, idx_code, idx_time = feature_engineering(X, y, nolimit, idx_date, idx_code, idx_time)

index = pd.MultiIndex.from_tuples(list(zip(idx_date,idx_time,idx_code)))

df = pd.DataFrame(X,index=index,columns=['20201209152417623'])


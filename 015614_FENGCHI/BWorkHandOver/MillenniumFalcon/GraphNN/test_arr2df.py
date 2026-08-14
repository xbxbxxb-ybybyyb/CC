# @Time : 2021/11/18 11:25
# @Author : Zhichen Lu
# @File : test_arr2df.py
import pandas as pd
import numpy as np
import itertools
from dataApi.FixFactorRollPrepare import load_fix_data,feature_engineering,infer_nolimit_pool

factor_list = ['zhy_fix_313']

X, y, nolimit, idx_date, idx_code, idx_time = load_fix_data(factor_list=factor_list)
X, y, idx_date, idx_code, idx_time = feature_engineering(X, y, nolimit, idx_date, idx_code, idx_time)

index = pd.MultiIndex.from_tuples(list(zip(idx_date,idx_time,idx_code)))
factor_df = pd.DataFrame(X,index=index,columns=factor_list)

nolimit_pool, date_list, code_list, time_list, factor = infer_nolimit_pool(idx_date,idx_code,idx_time,X[:,0])
factor = factor.swapaxes(1,2).reshape(len(date_list)*len(time_list),len(code_list))
factor = pd.DataFrame(factor,
                      index=pd.MultiIndex.from_tuples(list(itertools.product(date_list,time_list))),
                      columns=code_list)
factor_df_unstack = factor_df[factor_list[0]].unstack()
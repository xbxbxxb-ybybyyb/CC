# @Time : 2021/1/20 11:09
# @Author : Zhichen Lu
# @File : predict_by_loaded_model.py


import pandas as pd
import os
from dataApi.FixFactorRollPrepare import FixFactorRollPrepare
import numpy as np
import xgboost as xgb
# from online_conf import local_config_path

factor_list = pd.read_pickle('/data/group/800319/strategy_local_path/ic_all_t_400_factor_list.pkl')
update_date = 20171115
test = (20171116, 20171129)

old_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTest/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40'
compare_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVFixRollCompare20210120/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40'


model_old = xgb.Booster()
model_old.load_model(old_file+'_model_conf/%d.json'%update_date)
model_old.set_param('predictor','cpu_predictor')
model_compare = xgb.Booster()
model_compare.load_model(compare_file+'_model_conf/%d.json'%update_date)
model_compare.set_param('predictor','cpu_predictor')

dp_old = FixFactorRollPrepare(start_date=test[0], end_date=test[1], freq=7, model_time_len=1, factor_list=factor_list,
                 load_address='/data/group/800319/HFfactor/FixRoll/data/')
dp_compare = FixFactorRollPrepare(start_date=test[0], end_date=test[1], freq=7, model_time_len=1, factor_list=factor_list,
                 load_address='/data/group/800319/HFfactor/FixRollCompare/data/')
X, y,nolimit, idx_date, idx_time, idx_code = dp_old.load_data(start_date=test[0], end_date=test[1], return_idx=True)
X, y, idx_date, idx_time, idx_code = dp_old.feature_engineering(X, y,nolimit, idx_date, idx_time, idx_code)
index = pd.MultiIndex.from_tuples(list(zip(idx_date,idx_time,idx_code)))

feature_old,label_old = pd.DataFrame(X,index,columns=factor_list),pd.DataFrame({'label_old':y},index)


X, y,nolimit, idx_date, idx_time, idx_code = dp_compare.load_data(start_date=test[0], end_date=test[1], return_idx=True)
X, y, idx_date, idx_time, idx_code = dp_compare.feature_engineering(X, y,nolimit, idx_date, idx_time, idx_code)
index = pd.MultiIndex.from_tuples(list(zip(idx_date,idx_time,idx_code)))

feature_compare,label_compare = pd.DataFrame(X,index,columns=factor_list),pd.DataFrame({'label_compare':y},index)

mae_series,corr_series = {}, {}
for col in feature_compare.columns:
    corr_series[col] = feature_compare[col].corr(feature_old[col])
    mae_series[col] = abs(feature_compare[col] - feature_old[col]).mean()

stat = pd.DataFrame({'corr':corr_series,'mae':mae_series})

sign = stat['corr']/abs(stat['corr'])


d_old,d_compare = xgb.DMatrix(feature_old),xgb.DMatrix(feature_compare)
label_compare['prediction_compare_from_old_model'],label_compare['prediction_compare_from_compare_model'] = \
    model_old.predict(xgb.DMatrix(feature_compare*sign)),model_compare.predict(xgb.DMatrix(feature_compare))
label_old['prediction_old_from_old_model'],label_old['prediction_old_from_compare_model'] = \
    model_old.predict(xgb.DMatrix(feature_old)),model_compare.predict(xgb.DMatrix(feature_old*sign))

check = pd.concat([label_compare,label_old],axis=1)

check_compare_model = check[['prediction_compare_from_compare_model','prediction_old_from_compare_model']]
check_old_model = check[['prediction_compare_from_old_model','prediction_old_from_old_model']]
diff = (check['prediction_compare_from_old_model']-check['prediction_old_from_old_model']).apply(abs).sort_values(ascending=False)


diff.index[0]

one_sample_compare = pd.DataFrame({'old':feature_old.loc[diff.index[0]],'compare':feature_compare.loc[diff.index[0]]*sign})
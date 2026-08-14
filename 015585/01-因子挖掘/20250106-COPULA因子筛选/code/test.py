import pandas as pd
import numpy as np
import IO
import xgboost as xgb
from sklearn.model_selection import GridSearchCV
from statsmodels.tsa.stattools import adfuller
import sys
'''
'''
start_date_in = '20160101'
end_date_in = '20181231'
start_date_out = '20190101'
end_date_out = '20191231'

# 读取因子全集
strategy = 'saturn'
path1 = '/data/user/023859/share_file/for_qyh/factor_df_s1_20160101_20191231.pkl'
df_ori = pd.read_pickle(path1)
label_columns = ['label_v2o10d1', 'label_o2o10d1', 'label_Tc2To10d1',
       'label_st_indicator', 'label_T_open_is_zt', 'label_T_open_is_dt',
       'label_T_first_trans_ZT', 'label_T_day_first_ZT_Time',
       'label_T_day_first_DT_Time', 'label_T_close_is_zt',]
df_factor = df_ori.drop(label_columns,axis=1)
df_ori_in = df_ori.loc[pd.Timestamp(start_date_in):pd.Timestamp(end_date_in)]
df_ori_out = df_ori.loc[pd.Timestamp(start_date_out):pd.Timestamp(end_date_out)]
df_factor_in = df_factor.loc[pd.Timestamp(start_date_in):pd.Timestamp(end_date_in)]
df_factor_out = df_factor.loc[pd.Timestamp(start_date_out):pd.Timestamp(end_date_out)]
# 随机抽取400个因子
import random
original_list = list(range(df_factor_in.shape[1]))

best_ic = {}
factor_dict = {}
for count in range(200):
    selected_numbers = random.sample(original_list, 400)
    factor_list_filter = df_factor_in.columns[selected_numbers]

    X_train = df_factor_in[factor_list_filter].copy()
    y_train = df_ori_in[['label_v2o10d1']].copy()
    X_test = df_factor_out[factor_list_filter].copy()
    y_test = df_ori_out[['label_v2o10d1']].copy()
    best_params = {'colsample_bytree': 0.3,
                   'gamma': 0.05,
                   'learning_rate': 0.01,
                   'max_depth': 6,
                   'min_child_weight': 40,
                   'n_estimators': 1400,
                   'reg_alpha': 0.1, 'reg_lambda': 0.1, 'seed': 0, 'subsample': 0.3}
    model_best_params = xgb.XGBRegressor(**best_params)
    model_best_params.fit(X_train, y_train)
    y_pred = model_best_params.predict(X_test)
    y_test['pred_label'] = y_pred
    best_ic[count] = y_test.corr(method='spearman').iloc[0, 1]
    factor_dict[count] = factor_list_filter
    print(count,y_test.corr(method='spearman').iloc[0, 1])

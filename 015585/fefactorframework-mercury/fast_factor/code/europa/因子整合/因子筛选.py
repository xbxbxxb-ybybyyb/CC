import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris
import sys
from itertools import product
money_tot = 60

df_europa = pd.read_hdf('/data/user/015585/01-因子挖掘/20240624 xdb数据探索/file/basic_europa_20150930_20250710.h5')
df2 = pd.read_pickle('/data/user/015585/01-因子挖掘/999-share/for zwh/test_factor4_oriname.pkl')

common_index = set(df2.index) & set(df_europa.index)

df2 = df2.reindex(common_index)
df2 = df2.sort_values(['dt','Ticker'])
df_europa = df_europa.reindex(common_index)
df_europa = df_europa.sort_values(['dt', 'trigger_time'])

dic_factor = {
    'qyh_ori': df2,
}
res = pd.DataFrame()
print('data_set shape:')
for factor_set_type in dic_factor.keys():
    print(factor_set_type, ':' ,dic_factor[factor_set_type].shape)
# ================ 特征重要度选因子 ================
train_start = '20170101'
train_end = '20211231'

fit_start = '20220101'
fit_end = '20240131'

df = dic_factor['qyh_ori']
df = df.reindex(df_europa.index)

X = df.drop(['label_twap'], axis=1)
y = df[['label_twap']]

X_train = X.loc[pd.Timestamp(train_start): pd.Timestamp(train_end)]
y_train = y.loc[pd.Timestamp(train_start): pd.Timestamp(train_end)]

X_fit = X.loc[pd.Timestamp(fit_start): pd.Timestamp(fit_end)]
y_fit = y.loc[pd.Timestamp(fit_start): pd.Timestamp(fit_end)]

# 默认参数
list_colsample_bytree = [0.1, 0.3, 0.5]
list_learning_rate = [0.05, 0.1, 0.2]
list_max_depth = [4, 5, 6]
list_n_estimators = [600, 1000, 1400]
list_subsample = [0.5, 0.7, 0.9]
list_gamma = [0, 0.03, 0.05]
list_seed = [0 ,5 ,10]

list_df_importance = []
for colsample_bytree, learning_rate, max_depth, n_estimators, subsample, gamma, seed \
        in product(list_colsample_bytree, list_learning_rate, list_max_depth, list_n_estimators, list_subsample, list_gamma, list_seed):

    model_best_params = xgb.XGBRegressor(**{'n_jobs': 30,
                                            'colsample_bytree': colsample_bytree,
                                            'gamma': gamma,
                                            'learning_rate': learning_rate,
                                            'max_depth': max_depth,
                                            'min_child_weight': 50,
                                            'n_estimators': n_estimators,
                                            'reg_alpha': 0.9,
                                            'reg_lambda': 0.7,
                                            'seed': seed,
                                            'subsample': subsample})
    model_best_params.fit(X_train, (y_train)['label_twap'].apply(
        lambda x: 0.2 if x > 0.2 else -0.2 + (x + 0.2) / 10 if x < -0.2 else x))
    name_para = f'para_{colsample_bytree}_{learning_rate}_{max_depth}_{n_estimators}_{subsample}_{gamma}_{seed}'
    print(name_para)
    df_importance_para = pd.DataFrame(model_best_params.feature_importances_,index = X_train.columns,columns=[name_para]).T
    list_df_importance.append(df_importance_para)

res_importance = pd.concat(list_df_importance)
res_importance.to_pickle('res_importance_20250924.pkl')

rank = res_importance.mean().sort_values().reset_index()
factor_type = pd.read_csv('/data/user/015585/fefactorframework-mercury/fast_factor/code/europa/因子整合/res_f_name.csv')
factor_type = pd.merge(factor_type,rank, left_on='name', right_on='index', how='left')
factor_type = factor_type[~factor_type['index'].isna()][['name','factor_type',0]].rename(columns={0:'importance'})
factor_type['rank'] = factor_type['importance'].rank(ascending=False)
factor_type.to_csv('/data/user/015585/fefactorframework-mercury/fast_factor/code/europa/因子整合/res_f_name_import.csv')

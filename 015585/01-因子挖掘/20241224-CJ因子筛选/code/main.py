import pandas as pd
import numpy as np
import IO
import xgboost as xgb
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris
import sys
'''
1、用CJ corr计算因子和label的关系
2、筛选出XX个因子
3、比较2个因子集合的label的IC
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
# 计算CJ CORR
def get_rank(x):
    sorted_indices = np.argsort(x)
    ranks = np.arange(1, len(x) + 1)[np.argsort(sorted_indices)]
    return ranks
def cj_corr(y):
    if len(y) == 0:
        return np.nan
    else:
        res = sum([abs(y[i + 1] - y[i]) for i in range(len(y) - 1)])
        res = 1 - 3/(len(y)**2-1)*res
        return res
def cj_corr2(x,y):
    tuples_list = list(zip(x,y))
    sorted_tuples = sorted(tuples_list, key=lambda x: x[0])
    y = [i[1] for i in sorted_tuples]
    y = get_rank(y)
    res = cj_corr(y)
    return res
def cj_corr3(x,y):
    # x为series，y为df
    res = pd.Series()
    for z in y.columns:
        res[z] = cj_corr2(x,y[z])
    return res
y = df_ori_in['label_v2o10d1'].values
corr_cj_in = df_factor_in.apply(lambda x : cj_corr2(x,y), axis=0)

# 因子筛选：相关性不得高于
# corr_ratio = 0.7
# corr_in = df_factor_in.rank().corr(method = 'pearson')
# corr_cj_in = pd.DataFrame(corr_cj_in)
# corr_cj_in.columns = ['corr_cj']
# corr_cj_in['is_corr_max'] = 0
# corr_cj_in = corr_cj_in.sort_values('corr_cj',ascending=False)
# factor_info = pd.read_excel('/data/user/023859/share_file/for_qyh/factor_bank_inf_s1.xlsx')
# for factor in corr_cj_in.index:
#     sys.stdout.write('\r'+str(factor))
#     sys.stdout.flush()
#     list_good_factor = list(corr_cj_in[corr_cj_in['is_corr_max']==1].index)
#     corr_in_factor = corr_in[factor]
#     corr_list_factor = list(set(corr_in_factor[abs(corr_in_factor) >= corr_ratio].index) & set(list_good_factor))
#     if len(corr_list_factor) == 0:
#         corr_cj_in.loc[factor,'is_corr_max'] = 1
# factor_list_filter_ori = list(corr_cj_in[corr_cj_in['is_corr_max']==1].head(400).index) # 不一定包括基础因子
## 使用CJ相关性判断
from joblib import Parallel, delayed
def get_corr2_in(col,df_factor_in):
    print(col)
    res = pd.DataFrame(cj_corr3(df_factor_in[col],df_factor_in))
    res.columns = [col]
    return res
factor_df_list = Parallel(n_jobs=30)(delayed(get_corr2_in)(col, df_factor_in) for col in df_factor_in.columns)
corr2_in = pd.concat(factor_df_list,axis=1)
corr2_in.to_pickle('/data/user/015585/01-因子挖掘/20241224-CJ因子筛选/code/corr2_in.pkl')
corr2_in = pd.read_pickle('/data/user/015585/01-因子挖掘/20241224-CJ因子筛选/code/corr2_in.pkl')

corr2_ratio = 0.5# 因子间的CJ相关系数阈值
corr_cj_in = pd.DataFrame(corr_cj_in)
corr_cj_in.columns = ['corr_cj']
corr_cj_in['is_corr2_max'] = 0
corr_cj_in['ic'] = abs(df_factor_in.corrwith(df_ori_in['label_v2o10d1']))
# corr_cj_in = corr_cj_in.sort_values('corr_cj',ascending=False)
corr_cj_in = corr_cj_in.sort_values('ic',ascending=False)
factor_info = pd.read_excel('/data/user/023859/share_file/for_qyh/factor_bank_inf_s1.xlsx')
for factor in corr_cj_in.index:
    sys.stdout.write('\r'+str(factor))
    sys.stdout.flush()
    list_good_factor = list(corr_cj_in[corr_cj_in['is_corr2_max']==1].index)
    corr_in_factor = corr2_in[factor]
    corr_list_factor = list(set(corr_in_factor[abs(corr_in_factor) >= corr2_ratio].index) & set(list_good_factor))
    if len(corr_list_factor) == 0:
        corr_cj_in.loc[factor,'is_corr2_max'] = 1
factor_list_filter_ori = list(corr_cj_in[corr_cj_in['is_corr2_max']==1].head(400).index) # 不一定包括基础因子
# 分层抽样
corr_cj_in['factor_type'] = factor_info[['factor_name','factor_type']].set_index('factor_name')
count_factor_type = corr_cj_in[corr_cj_in['is_corr2_max'] == 1].groupby('factor_type').count().sort_values('corr_cj')['corr_cj']
count_factor_type = count_factor_type/count_factor_type.sum()*420
corr_cj_in['is_corr2_max'] = 0

factor_list_filter_ori_sample = []
for factor_type in count_factor_type.index:
    corr_cj_in_type = corr_cj_in[corr_cj_in['factor_type'] == factor_type]
    for factor in corr_cj_in_type.index:
        sys.stdout.write('\r' + str(factor))
        sys.stdout.flush()
        list_good_factor = list(corr_cj_in_type[corr_cj_in_type['is_corr2_max'] == 1].index)
        corr_in_factor = corr2_in[factor]
        corr_list_factor = list(set(corr_in_factor[abs(corr_in_factor) >= corr2_ratio].index) & set(list_good_factor))
        if len(corr_list_factor) == 0:
            corr_cj_in_type.loc[factor, 'is_corr2_max'] = 1
    factor_list_filter_ori_type = list(corr_cj_in_type[corr_cj_in_type['is_corr2_max'] == 1].head(int(count_factor_type[factor_type])).index)
    factor_list_filter_ori_sample.append(factor_list_filter_ori_type)
factor_list_filter_ori_sample = [j for i in factor_list_filter_ori_sample for j in i]
#
list_basic_factor = factor_info[((factor_info['factor_owner'] == 'other_basic') | (factor_info['factor_owner'] == 'other'))& (factor_info['factor_type'] != 'label')]['factor_name']
factor_list_filter = list(set(factor_list_filter_ori) | set(list_basic_factor)) # 包括基础因子

# 训模型
## 全因子
X_train = df_factor_in.copy()
y_train = df_ori_in[['label_v2o10d1']].copy()
X_test = df_factor_out.copy()
y_test = df_ori_out[['label_v2o10d1']].copy()
xgb_train = xgb.DMatrix(X_train, label=y_train)
xgb_test = xgb.DMatrix(X_test, label=y_test)

# 进行预测
best_params = {'learning_rate': 0.01, 'n_estimators': 800, 'max_depth': 5, 'min_child_weight': 40, 'seed': 0,
                'subsample': 0.5, 'colsample_bytree': 0.9, 'gamma': 0.05, 'reg_alpha': 0.3, 'reg_lambda': 0.1}
model_best_params = xgb.XGBRegressor(**best_params)
model_best_params.fit(X_train, y_train)
y_pred = model_best_params.predict(X_test)
y_test['pred_label'] = y_pred
print(y_test.corr(method = 'spearman').iloc[0,1]) # 0.2512750347732314
## tmp 验证唐博的因子集合
# factor_list_filter_tsq = pd.read_excel('/data/user/023859/share_file/for_qyh/fsci_label_v2o10d1_20160101_20181231.xlsx')
# factor_list_filter_tsq = list(factor_list_filter_tsq[factor_list_filter_tsq['select'] == 1].sort_values('rank',ascending = True).head(408)['factor_name'])
# X_train = df_factor_in[factor_list_filter_tsq].copy()
# y_train = df_ori_in[['label_v2o10d1']].copy()
# X_test = df_factor_out[factor_list_filter_tsq].copy()
# y_test = df_ori_out[['label_v2o10d1']].copy()
# best_params = {'learning_rate': 0.01, 'n_estimators': 800, 'max_depth': 5, 'min_child_weight': 40, 'seed': 0,
#                 'subsample': 0.5, 'colsample_bytree': 0.9, 'gamma': 0.05, 'reg_alpha': 0.3, 'reg_lambda': 0.1}
# best_params = {'colsample_bytree': 0.3,
#                'gamma': 0.05,
#                'learning_rate': 0.01,
#                'max_depth': 6,
#                'min_child_weight': 40,
#                'n_estimators': 1400,
#                'reg_alpha': 0.1, 'reg_lambda': 0.1, 'seed': 0, 'subsample': 0.3}
# model_best_params_tsq = xgb.XGBRegressor(**best_params)
# model_best_params_tsq.fit(X_train, y_train)
# y_pred = model_best_params_tsq.predict(X_test)
# y_test['pred_label'] = y_pred
# print(y_test.corr(method = 'spearman').iloc[0,1]) # 0.2543399655794433
## 筛选后的因子
factor_list_filter = factor_list_filter_ori
X_train = df_factor_in[factor_list_filter].copy()
y_train = df_ori_in[['label_v2o10d1']].copy()
X_test = df_factor_out[factor_list_filter].copy()
y_test = df_ori_out[['label_v2o10d1']].copy()
# 调参
cv_params_all = {'n_estimators': [600, 800, 1000, 1200, 1400],
                 'max_depth': [5,6,7],
                 'min_child_weight':[30, 40, 60],
                 'gamma': [0.03,0.05,0.07],
                 'subsample': [0.3, 0.5, 0.7, 0.9],
                 'colsample_bytree': [0.1, 0.3, 0.5, 0.7],
                 'reg_alpha': [0.1,0.3], 'reg_lambda': [0.1, 0.3]
                 }
other_params = {'colsample_bytree': 0.3,
               'gamma': 0.05,
               'learning_rate': 0.01,
               'max_depth': 6,
               'min_child_weight': 40,
               'n_estimators': 1000,
               'reg_alpha': 0.1, 'reg_lambda': 0.1, 'seed': 0, 'subsample': 0.3}

def get_best_para(cv_params_all,other_params,X_train,y_train):
    para_list = ['n_estimators',
                 ['max_depth','min_child_weight'],
                 'gamma',
                 ['subsample','colsample_bytree'],
                 ['reg_alpha','reg_lambda']
                 ]
    for para in para_list:
        if type(para) == str:
            cv_params = {para: cv_params_all[para]}
        elif type(para) == list:
            cv_params = {key: cv_params_all[key] for key in para}
        else:
            raise ValueError
        model = xgb.XGBRegressor(**other_params)
        optimized_GBM = GridSearchCV(estimator=model, param_grid=cv_params, scoring='r2', cv=5, verbose=1, n_jobs=20)
        print(X_train.shape)
        optimized_GBM.fit(X_train, y_train)
        print('参数的最佳取值：{0}'.format(optimized_GBM.best_params_))
        print('最佳模型得分:{0}'.format(optimized_GBM.best_score_))
        for param in optimized_GBM.best_params_:
            other_params[param] = optimized_GBM.best_params_[param]
        print(para)
        print(other_params)
        print('==============================')
    return other_params
# 进行预测 filter后
# best_params = get_best_para(cv_params_all,other_params,X_train,y_train)
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
print(y_test.corr(method = 'spearman').iloc[0,1]) # 0.23706293952414728








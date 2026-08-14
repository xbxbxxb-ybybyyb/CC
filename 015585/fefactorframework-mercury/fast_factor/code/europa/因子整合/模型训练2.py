import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris
import sys

money_tot = 60
dic_train = {
    # 'Q0':['20170101', '20201231'],
    'Q1':['20170101', '20210630'],
    'Q2':['20170101', '20211231'],
    'Q3':['20170101', '20220630'],
    'Q4':['20170101', '20221231'],
    'Q5':['20170101', '20230630'],
    'Q6':['20170101', '20231231'],
    'Q7':['20170101', '20240630'],
    # 'Q8':['20170101', '20241231'],
}
df_europa = pd.read_hdf('/data/user/015585/01-因子挖掘/20240624 xdb数据探索/file/basic_europa_20150930_20250710.h5')

df1 = pd.read_pickle('/data/user/015585/01-因子挖掘/999-share/for zwh/test_factor_t_1.pkl')
df2 = pd.read_pickle('/data/user/015585/01-因子挖掘/999-share/for zwh/test_factor4_oriname_emo.pkl')
df3 = pd.read_pickle('/dfs/user/015585/00-草稿纸/group_level3_memory.pkl')
df3_type = pd.read_excel('/dfs/user/015585/00-草稿纸/kmeans-centroid.xlsx')
# list_df3_factor = list(df3_type[df3_type['factor_type'].isin(['T-1_factor','TTickab','TTransaction'])]['factor_name'])
# df3 = df3[list_df3_factor]
# drop label
print('drop df3 label')
drop_list = [i for i in df3.columns if 'label' in i]
df3 = df3.drop(drop_list, axis=1)

common_index = set(df2.index) & set(df3.index)
df1 = df1.reindex(common_index)
df1 = df1.sort_values(['dt','Ticker'])
df2 = df2.reindex(common_index)
df2 = df2.sort_values(['dt','Ticker'])
df3 = df3.reindex(common_index)
df3 = df3.sort_values(['dt','Ticker'])
df3['label_twap'] = df2['label_twap']
#
df_europa = df_europa.reindex(common_index)
df_europa = df_europa.sort_values(['dt', 'trigger_time'])

dic_factor = {
    'qyh_ori': df2,
    'zwh_all': df3
    # 'qyh_now': df2,
    # 'zwh_all': df3,
    # 'zwh_trade_t_1': df4,
    # 'zwh_trade_t_1_tick': df5,
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
# model_best_params = xgb.XGBRegressor(**{'n_jobs': 28, })
model_best_params = xgb.XGBRegressor(**{'n_jobs': 28, 'colsample_bytree': 0.1, 'gamma': 0.05, 'learning_rate': 0.01, 'max_depth': 5, 'min_child_weight': 50, 'n_estimators': 1000, 'reg_alpha': 0.9, 'reg_lambda': 0.7, 'seed': 0, 'subsample': 0.7})
model_best_params.fit(X_train, (y_train)['label_twap'].apply(
    lambda x: 0.2 if x > 0.2 else -0.2 + (x + 0.2) / 10 if x < -0.2 else x))
df_importance = pd.DataFrame(model_best_params.feature_importances_,index = X_train.columns,columns=['importance'])
factor_list_important = list(df_importance[df_importance['importance'] > 0.000135].index)
dic_factor['qyh_important'] = df2[factor_list_important + ['label_twap']]
# ================ 预测20230701~20250630 ==============
for factor_set_type in dic_factor.keys():
    train_start = '20170101'
    train_end = '20211231'

    fit_start = '20220101'
    fit_end = '20240131'

    df = dic_factor[factor_set_type]
    df = df.reindex(df_europa.index)

    X = df.drop(['label_twap'], axis=1)
    y = df[['label_twap']]

    X_train = X.loc[pd.Timestamp(train_start): pd.Timestamp(train_end)]
    y_train = y.loc[pd.Timestamp(train_start): pd.Timestamp(train_end)]

    X_fit = X.loc[pd.Timestamp(fit_start): pd.Timestamp(fit_end)]
    y_fit = y.loc[pd.Timestamp(fit_start): pd.Timestamp(fit_end)]

    # 默认参数
    # model_best_params = xgb.XGBRegressor(**{'n_jobs': 28,})
    model_best_params = xgb.XGBRegressor(
        **{'n_jobs': 28, 'colsample_bytree': 0.1, 'gamma': 0.05, 'learning_rate': 0.01, 'max_depth': 5,
           'min_child_weight': 50, 'n_estimators': 1000, 'reg_alpha': 0.9, 'reg_lambda': 0.7, 'seed': 0,
           'subsample': 0.7})
    # model_best_params.fit(X_train.append(X_test), (y_train.append(y_test))['label_twap'].apply(lambda x :0.2 if x > 0.2 else -0.2 + (x+0.2)/10 if x < -0.2 else x))
    model_best_params.fit(X_train, (y_train)['label_twap'].apply(lambda x :0.2 if x > 0.2 else -0.2 + (x+0.2)/10 if x < -0.2 else x))
    # model_best_params.fit(X_train.append(X_test), (y_train.append(y_test)))
    # fit
    y_pred = model_best_params.predict(X_fit)
    y_fit['pred_label'] = y_pred.copy()
    #
    pct70 = np.percentile(model_best_params.predict(X_train), 70)

    res_daily = y_fit[y_fit['pred_label'] >= pct70]['label_twap'].apply(lambda x : x - 0.002).groupby('dt').head(money_tot).groupby('dt').sum()
    sharp_df = y_fit[y_fit['pred_label'] >= pct70]['label_twap'].apply(lambda x : x - 0.002).groupby('dt').head(money_tot).groupby('dt').mean()
    # print('sharp:', (sharp_df.sum() - 0.03) / sharp_df.std())
    ## 最大回撤
    max_down_df = res_daily.to_frame(name = '每日盈亏比例') * 2000
    max_down_df['累计盈利'] = max_down_df['每日盈亏比例'].cumsum()
    max_down_df['最高盈利'] = max_down_df['累计盈利'].expanding().max()
    max_down_df['最大回撤'] = max_down_df['累计盈利'] - max_down_df['最高盈利']
    print(factor_set_type,[fit_start,fit_end])
    # print('rankIC:', y_fit.corr(method = 'spearman').iloc[0,1])
    # print('累计盈利：', max_down_df['累计盈利'].tail(1).values[0])
    # print('最大回撤：', max_down_df['最大回撤'].min())
    # print('收益风险比：',  max_down_df['累计盈利'].tail(1).values[0] / -max_down_df['最大回撤'].min())
    res.loc[f'{factor_set_type}', '区间'] = str([fit_start,fit_end])
    res.loc[f'{factor_set_type}', 'rankIC'] = y_fit.corr(method = 'spearman').iloc[0,1]
    res.loc[f'{factor_set_type}', '累计盈利'] = max_down_df['累计盈利'].tail(1).values[0]
    res.loc[f'{factor_set_type}', '最大回撤'] = max_down_df['最大回撤'].min()
    res.loc[f'{factor_set_type}', '收益风险比'] = max_down_df['累计盈利'].tail(1).values[0] / -max_down_df['最大回撤'].min()
    res.loc[f'{factor_set_type}', '参与率'] = len(y_fit[y_fit['pred_label'] >= pct70]) / len(y_fit)


# res_daily.to_excel('res_daily_factor4.xlsx')
raise
# ================ 最佳参数 ===================
df = dic_factor['qyh_ori']
X = df.drop(['label_twap'], axis=1)
y = df[['label_twap']]
train_start = '20170101'
train_end = '20211231'
X_train = X.loc[pd.Timestamp(train_start): pd.Timestamp(train_end)]
y_train = y.loc[pd.Timestamp(train_start): pd.Timestamp(train_end)]

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
        optimized_GBM = GridSearchCV(estimator=model, param_grid=cv_params, scoring='r2', cv=5, verbose=1, n_jobs=30)
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
cv_params_all = {'n_estimators': [600, 1000, 1400, 1800, 2200, 2600, 3000],
                 'max_depth': [3, 4, 5, 6],
                 'min_child_weight':[30, 40, 50],
                 'gamma': [0, 0.03, 0.05, 0.07],
                 'subsample': [0.3, 0.5, 0.7, 0.9],
                 'colsample_bytree': [0.1, 0.3, 0.5, 0.7],
                 'reg_alpha': [0, 0.3, 0.6, 0.9, 2, 5], 'reg_lambda': [0.1, 0.4, 0.7, 1, 2 ,5]
                 }
other_params = {'colsample_bytree': 0.3,
               'gamma': 0.05,
               'learning_rate': 0.01,
               'max_depth': 6,
               'min_child_weight': 40,
               'n_estimators': 1400,
               'reg_alpha': 0.1, 'reg_lambda': 0.1, 'seed': 0, 'subsample': 0.3}
best_params = get_best_para(cv_params_all,other_params,X_train,y_train)
print(best_params)
# {'colsample_bytree': 0.1, 'gamma': 0.05, 'learning_rate': 0.01, 'max_depth': 5, 'min_child_weight': 50, 'n_estimators': 1000, 'reg_alpha': 0.9, 'reg_lambda': 0.7, 'seed': 0, 'subsample': 0.7}
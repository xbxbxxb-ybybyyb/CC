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
    # 'Q5':['20170101', '20230630'],
    # 'Q6':['20170101', '20231231'],
    # 'Q7':['20170101', '20240630'],
    # 'Q8':['20170101', '20241231'],
}
df_europa = pd.read_hdf('/data/user/015585/01-因子挖掘/20240624 xdb数据探索/file/basic_europa_20150930_20250710.h5')

df1 = pd.read_pickle('/data/user/015585/01-因子挖掘/999-share/for zwh/test_factor2.pkl')
df2 = pd.read_pickle('/data/user/015585/01-因子挖掘/999-share/for zwh/test_factor4.pkl')
df3 = pd.read_pickle('/dfs/user/015585/00-草稿纸/group_level3_memory.pkl')
df3_type = pd.read_excel('/dfs/user/015585/00-草稿纸/kmeans-centroid.xlsx')
# drop label
print('drop df3 label')
drop_list = [i for i in df3.columns if 'label' in i]
df3 = df3.drop(drop_list, axis=1)

list_trade_t_1 = list(df3_type[df3_type['factor_type'].isin(['TTransaction','T-1_factor'])]['factor_name'])
df4 = df3[list_trade_t_1].copy()

list_trade_t_1_tick = list(df3_type[df3_type['factor_type'].isin(['TTransaction','T-1_factor','TTickab'])]['factor_name'])
df5 = df3[list_trade_t_1_tick].copy()

# =========test_type===========
test_type = 'no' # TTrade T-1
print(test_type)
if test_type == 'TTrade':
    list_ttrade = list(df3_type[df3_type['factor_type'] == 'TTransaction']['factor_name'])
    df3 = df3[list_ttrade]
elif test_type == 'T-1':
    list_t_1 = list(df3_type[df3_type['factor_type'] == 'T-1_factor']['factor_name'])
    df3 = df3[list_t_1]
# 补
if test_type == 'T-1': # 都补自己的Trade，看MD部分引发的差异
    df_trade = pd.read_pickle('/data/user/015585/01-因子挖掘/999-share/for zwh/test_factor_trade.pkl')
    df3 = pd.merge(df3, df_trade, left_index=True, right_index=True, how='left')
elif test_type == 'TTrade': # 都补自己的MD，看Trade部分引发的差异
    df_md = pd.read_pickle('/data/user/015585/01-因子挖掘/999-share/for zwh/test_factor_md.pkl')
    df3 = pd.merge(df3, df_md, left_index=True, right_index=True, how='left')

# same label
df3['label_twap'] = df2['label_twap']
df4['label_twap'] = df2['label_twap']
df5['label_twap'] = df2['label_twap']

common_index = set(df2.index) & set(df3.index)

df1 = df1.reindex(common_index)
df1 = df1.sort_values(['dt','Ticker'])
df2 = df2.reindex(common_index)
df2 = df2.sort_values(['dt','Ticker'])
df3 = df3.reindex(common_index)
df3 = df3.sort_values(['dt','Ticker'])
df4 = df4.reindex(common_index)
df4 = df4.sort_values(['dt','Ticker'])
df5 = df5.reindex(common_index)
df5 = df5.sort_values(['dt','Ticker'])

df_europa = df_europa.reindex(common_index)
df_europa = df_europa.sort_values(['dt', 'trigger_time'])

dic_factor = {
    'qyh_ori': df1,
    'qyh_now': df2,
    'zwh_all': df3,
    'zwh_trade_t_1': df4,
    'zwh_trade_t_1_tick': df5,
}
res = pd.DataFrame()
print('data_set shape:')
for factor_set_type in dic_factor.keys():
    print(factor_set_type, ':' ,dic_factor[factor_set_type].shape)
for factor_set_type in dic_factor.keys():
    for period in dic_train.keys():
        train_start = dic_train[period][0]
        train_end = dic_train[period][1]

        test_start = (pd.Timestamp(train_end)+pd.Timedelta(days=1)).strftime('%Y%m%d').split(' ')[0]
        test_end = test_start[:4]+'1231' if test_start[4:6]=='07' else test_start[:4]+'0630'

        fit_start = (pd.Timestamp(test_end)+pd.Timedelta(days=1)).strftime('%Y%m%d').split(' ')[0]
        fit_end = str(int(train_end[:4])+1) + train_end[4:8]

        df = dic_factor[factor_set_type]
        df = df.reindex(df_europa.index)
        need_1030 = False
        if need_1030:
            df_1030 = pd.read_pickle('/data/user/015585/01-因子挖掘/20240624 run/file/basic_europa_add1030_20150930_20250710.pkl')
            df['label_twap_1030'] = df_1030['label_twap_1030'].fillna(0)
        if need_1030:
            X = df.drop(['label_twap','label_twap_1030'], axis=1)
        else:
            X = df.drop(['label_twap'], axis=1)
        y = df[['label_twap']]

        X_train = X.loc[pd.Timestamp(train_start): pd.Timestamp(train_end)]
        y_train = y.loc[pd.Timestamp(train_start): pd.Timestamp(train_end)]
        X_test = X.loc[pd.Timestamp(test_start): pd.Timestamp(test_end)]
        y_test = y.loc[pd.Timestamp(test_start): pd.Timestamp(test_end)]
        X_fit = X.loc[pd.Timestamp(fit_start): pd.Timestamp(fit_end)]
        y_fit = y.loc[pd.Timestamp(fit_start): pd.Timestamp(fit_end)]

        # 默认参数
        model_best_params = xgb.XGBRegressor(**{'n_jobs': 28,})
        # model_best_params.fit(X_train.append(X_test), (y_train.append(y_test))['label_twap'].apply(lambda x :0.2 if x > 0.2 else -0.2 + (x+0.2)/10 if x < -0.2 else x))
        model_best_params.fit(X_train, (y_train)['label_twap'].apply(lambda x :0.2 if x > 0.2 else -0.2 + (x+0.2)/10 if x < -0.2 else x))
        # model_best_params.fit(X_train.append(X_test), (y_train.append(y_test)))
        # fit
        y_pred = model_best_params.predict(X_fit)
        y_fit['pred_label'] = y_pred.copy()
        # y_fit['label_twap'] = df['label_twap']

        #
        # pct70 = np.percentile(model_best_params.predict(X_train.append(X_test)), 70)
        pct70 = np.percentile(model_best_params.predict(X_test), 70)
        # print('总盈利:', y_fit[y_fit['pred_label'] >= pct70]['label_twap'].apply(lambda x : x - 0.002).groupby('dt').head(30).sum() * 2000)
        # y_fit[y_fit['pred_label'] >= pct70]['label_twap'].apply(lambda x : x - 0.002).sum() * 2000

        res_daily = y_fit[y_fit['pred_label'] >= pct70]['label_twap'].apply(lambda x : x - 0.002).groupby('dt').head(money_tot).groupby('dt').sum()
        res_daily_30 = y_fit[y_fit['pred_label'] >= y_fit['pred_label'].quantile(0.7)]['label_twap'].apply(lambda x: x - 0.002).groupby('dt').head(
            money_tot).groupby('dt').sum()
        ## 最大回撤
        max_down_df = res_daily.to_frame(name = '每日盈亏比例') * 2000
        max_down_df['累计盈利'] = max_down_df['每日盈亏比例'].cumsum()
        max_down_df['最高盈利'] = max_down_df['累计盈利'].expanding().max()
        max_down_df['最大回撤'] = max_down_df['累计盈利'] - max_down_df['最高盈利']

        max_down_df_30 = res_daily_30.to_frame(name = '每日盈亏比例') * 2000
        max_down_df_30['累计盈利'] = max_down_df_30['每日盈亏比例'].cumsum()
        max_down_df_30['最高盈利'] = max_down_df_30['累计盈利'].expanding().max()
        max_down_df_30['最大回撤'] = max_down_df_30['累计盈利'] - max_down_df['最高盈利']
        print(factor_set_type, period,[fit_start,fit_end])
        # print('rankIC:', y_fit.corr(method = 'spearman').iloc[0,1])
        # print('累计盈利：', max_down_df['累计盈利'].tail(1).values[0])
        # print('最大回撤：', max_down_df['最大回撤'].min())
        # print('收益风险比：',  max_down_df['累计盈利'].tail(1).values[0] / -max_down_df['最大回撤'].min())
        res.loc[f'{factor_set_type}_{period}', '区间'] = str([fit_start,fit_end])
        res.loc[f'{factor_set_type}_{period}', 'rankIC'] = y_fit.corr(method = 'spearman').iloc[0,1]
        res.loc[f'{factor_set_type}_{period}', '累计盈利'] = max_down_df['累计盈利'].tail(1).values[0]
        res.loc[f'{factor_set_type}_{period}', '最大回撤'] = max_down_df['最大回撤'].min()
        res.loc[f'{factor_set_type}_{period}', '收益风险比'] = max_down_df['累计盈利'].tail(1).values[0] / -max_down_df['最大回撤'].min()
        res.loc[f'{factor_set_type}_{period}', '参与率'] = len(y_fit[y_fit['pred_label'] >= pct70]) / len(y_fit)

        res.loc[f'{factor_set_type}_{period}', '收益风险比_30'] = max_down_df_30['累计盈利'].tail(1).values[0] / -max_down_df_30['最大回撤'].min()

    #
    # res_daily.to_excel(f'res_daily_{fit_start}_{fit_end}.xlsx')
# sys.exit()
raise
# 调参
cv_params_all = {'n_estimators': [1000, 1400, 1800, 2200, 2600, 3000],
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
# 进行预测 filter后
X = df.drop(['label_twap'], axis=1)
y = df[['label_twap']]
best_params = get_best_para(cv_params_all,other_params,X_train,y_train)
print(best_params)
raise
# best_params = {'colsample_bytree': 0.5,
#                'gamma': 0,
#                'learning_rate': 0.02,
#                'max_depth': 4,
#                'min_child_weight': 40,
#                'n_estimators': 2600,
#                'reg_alpha': 5, 'reg_lambda': 2, 'seed': 0, 'subsample': 0.6,
#                'n_jobs':24}
{'colsample_bytree': 0.3, 'gamma': 0, 'learning_rate': 0.01, 'max_depth': 3, 'min_child_weight': 50, 'n_estimators': 1400, 'reg_alpha': 2, 'reg_lambda': 0.4, 'seed': 0, 'subsample': 0.5}
model_best_params = xgb.XGBRegressor(**best_params)
model_best_params.fit(X_train.append(X_test), y_train.append(y_test))
# fit
y_pred = model_best_params.predict(X_fit)
y_fit['pred_label'] = y_pred
print(y_fit.corr(method = 'spearman').iloc[0,1])
#

print('70分位数', np.percentile(model_best_params.predict(X_train.append(X_test)), 70)) # 0.00282,0.004737591743469238
y_fit[y_fit['pred_label'] >= 0.00473759]['label_twap'].apply(lambda x : x - 0.003).groupby('dt').tail(40).sum() * 2000





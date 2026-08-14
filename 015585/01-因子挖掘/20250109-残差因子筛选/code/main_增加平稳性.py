import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import xgboost as xgb
import sys
import decimal
import IO
from statsmodels.tsa.stattools import adfuller
'''
1、选择一批基础因子：风格为主，相关性低
2、每个因子rank对基础因子rank取残差，计算残差和label的相关性
3、根据残差相关性排序，剔除本身高相关 或者 残差高相关 的因子
'''
def round_(x, n=0):
    x = x + 1e-10
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                     rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res
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
# 初始化因子信息
# corr_in = df_factor_in.rank().corr(method = 'pearson')
# corr_in.to_pickle('/data/user/015585/01-因子挖掘/20250106-COPULA因子筛选/code/corr_in.pkl')
corr_in = pd.read_pickle('/data/user/015585/01-因子挖掘/20250106-COPULA因子筛选/code/corr_in.pkl') # 因子spearman相关性
res_residual = pd.DataFrame() # 因子信息
for col in df_factor_in.columns:
    df_col = df_factor_in[[col]].copy()
    df_col['label'] = df_ori_in['label_v2o10d1']
    res_residual.loc[col, 'IC'] = abs(df_col.corr(method = 'spearman').iloc[0,1])
    res_residual.loc[col, 'IC_pearson'] = abs(df_col.corr(method='pearson').iloc[0, 1])
# 基础因子选择
## 方法1：直接指定
basic_factor_list1 = [
                     'saturn_float_shares',
                     'saturn_lzt_day_pattern',
                     'saturn_free_turn',
                     'saturn_Circu_Mkt',
                     'saturn_pre_close',
                     'saturn_t930_T_o2pre',
                     'saturn_Lzt_ZT_Time',
                     'saturn_high_before20',
                     'saturn_EFS_pct5_T1'
                      ]
## 方法2：根据IC和相关性选择9个因子
res_residual['is_corr_max'] = 0
corr_cj_in = res_residual.sort_values('IC',ascending=False)
for factor in corr_cj_in.index:
    list_good_factor = list(corr_cj_in[corr_cj_in['is_corr_max']==1].index)
    corr_in_factor = corr_in[factor]
    corr_list_factor = list(set(corr_in_factor[abs(corr_in_factor) >= 0.2].index) & set(list_good_factor))
    if len(corr_list_factor) == 0:
        corr_cj_in.loc[factor,'is_corr_max'] = 1
basic_factor_list2 = list(corr_cj_in[corr_cj_in['is_corr_max']==1].head(9).index) # IC因子列表
## 方法3：增加一些barra风格因子
pass
# barra_risk_in = IO.read_data([20151201, int(end_date_in)],
#                           alt='/data/group/800080/warehouseJG/prod/RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5')
# barra_risk_out = IO.read_data([20181201, int(end_date_out)],
#                           alt='/data/group/800080/warehouseJG/prod/RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5')
#
# for col in barra_risk_in.columns:
#     sys.stdout.write('\r'+str(col))
#     sys.stdout.flush()
#     barra_risk_in[col] = barra_risk_in[col].unstack().shift(1).stack()
#     barra_risk_out[col] = barra_risk_out[col].unstack().shift(1).stack()
# barra_risk_in = barra_risk_in.reindex(df_factor_in.index)
# barra_risk_out = barra_risk_out.reindex(df_factor_out.index)
# barra_risk_in.to_pickle('/data/user/015585/01-因子挖掘/20250109-残差因子筛选/code/barra_risk_in.pkl')
# barra_risk_out.to_pickle('/data/user/015585/01-因子挖掘/20250109-残差因子筛选/code/barra_risk_out.pkl')

barra_risk_in = pd.read_pickle('/data/user/015585/01-因子挖掘/20250109-残差因子筛选/code/barra_risk_in.pkl')
barra_risk_out = pd.read_pickle('/data/user/015585/01-因子挖掘/20250109-残差因子筛选/code/barra_risk_out.pkl')
df_factor_in = pd.merge(df_factor_in, barra_risk_in, left_index=True, right_index=True)
df_factor_in = df_factor_in.fillna(df_factor_in.mean())
df_factor_out = pd.merge(df_factor_out, barra_risk_out, left_index=True, right_index=True)
df_factor_out = df_factor_out.fillna(df_factor_out.mean())
basic_factor_list3 = basic_factor_list1 + list(barra_risk_in.columns)
##
basic_factor_list = basic_factor_list3
print('')
print('基础因子列表：')
print(basic_factor_list)
corr_basic_factor = df_factor_in[basic_factor_list].corr(method = 'spearman')
'''
注意如果是指定基础因子，价格、市值、换手率有一定的相关性；考虑做一次PCA，待定
'''
#
print('=====计算和基础因子的残差=====')
df_residual_in = pd.DataFrame()
df_basic_factor_in = df_factor_in[basic_factor_list]
# df_basic_factor_in = df_basic_factor_in.apply(lambda x : pd.cut(x,bins=20,labels=[i for i in range(0,20)]))
x = df_basic_factor_in.rank()
for col in df_factor_in.columns:
    sys.stdout.write('\r'+str(col))
    sys.stdout.flush()
    df_col = df_factor_in[[col]].copy()
    df_col['label'] = df_ori_in['label_v2o10d1']
    y = df_factor_in[col].rank()
    model = LinearRegression().fit(x,y)
    y_pred = model.predict(x)
    df_residual_in[col] = y - y_pred
    df_residual_in[col] = df_residual_in[col].apply(lambda x : round_(x,6))
print('')
print('=====计算残差和label的相关性=====')
res_residual['IC_residual'] = abs(df_residual_in.corrwith(df_ori_in['label_v2o10d1'],method = 'spearman')) # 做了绝对值处理
#
print('=====计算残差的平稳性=====')
res_month_IC_residual = pd.DataFrame()
for col in df_residual_in.columns:
    sys.stdout.write('\r'+str(col))
    sys.stdout.flush()
    df_col = df_residual_in[[col]].copy()
    df_col['label'] = df_ori_in['label_v2o10d1']
    df_col['year_month'] = list(pd.Series(df_col.index.get_level_values(0)).apply(lambda x : f'{x.year}_{str(x.month).zfill(2)}'))
    res_month_IC_residual[col] = df_col.groupby('year_month').apply(lambda x : x.corr(method = 'spearman').iloc[0,1]).fillna(0)
    res_residual.loc[col, 'adf_residual'] = adfuller(res_month_IC_residual[col])[1]  # p-value,越小越平稳，0.05为界
    res_residual.loc[col, 'IR_residual'] = res_month_IC_residual[col].mean() / res_month_IC_residual[col].std() if res_month_IC_residual[col].std() > 1e-5 else 0
#
print('')
print('添加因果分析结果')
tsq = pd.read_excel('/data/user/023859/share_file/for_qyh/fsci_label_v2o10d1_20160101_20181231.xlsx')
res_residual['tsq_rank'] = tsq.set_index('factor_name')['rank']
for col in res_residual:
    res_residual[col] = res_residual[col].astype(float)
# =======================================================================
# 因子筛选：相关性不得高于0.7
type_sort = 'rank_combine'
corr_ratio = 0.7
IC_ratio = 0.05
adf_ratio = 0.05
combine_ratio = {'rank_IC_residual':0.5,
                 'tsq_rank':0,
                 'rank_IR_residual':0.5
                 }
print('')
print(f'=====使用{type_sort}筛选因子，因子间相关性不得高于{corr_ratio}=====')
corr_cj_in = res_residual.copy()
corr_cj_in['rank_IC_residual'] = corr_cj_in['IC_residual'].rank(ascending = False) # 越高则排名越小
corr_cj_in['rank_IR_residual'] = abs(corr_cj_in['IR_residual']).rank(ascending = False) # 越高则排名越小
# 平稳性惩罚
# print('添加残差平稳性惩罚')
# corr_cj_in.loc[(corr_cj_in['adf_residual'] >= adf_ratio),'rank_IC_residual'] =\
#     corr_cj_in.loc[(corr_cj_in['adf_residual'] >= adf_ratio),'rank_IC_residual'] + \
#     6000 * (corr_cj_in.loc[(corr_cj_in['adf_residual'] >= adf_ratio),'adf_residual'] - adf_ratio) # 非线性信息不平稳的惩罚
#
corr_cj_in['rank_combine'] = 0
for key in combine_ratio:
    corr_cj_in['rank_combine'] += (corr_cj_in[key] * combine_ratio[key])

## 这里先计算IC与因果分析的因子列表，用于观察重复度
print('计算IC、因果分析的因子列表用于观察重复程度')
corr_cj_in['is_corr_max'] = 0
corr_cj_in = corr_cj_in.sort_values('IC',ascending=False)
if basic_factor_list == basic_factor_list3:
    corr_in = df_factor_in.rank().corr() # 要补充RISK中因子的相关性
    print('因为使用了RISK作为基础因子，重新计算因子相关性')
for factor in corr_cj_in.index:
    list_good_factor = list(corr_cj_in[corr_cj_in['is_corr_max']==1].index)
    corr_in_factor = corr_in[factor]
    corr_list_factor = list(set(corr_in_factor[abs(corr_in_factor) >= corr_ratio].index) & set(list_good_factor))
    if len(corr_list_factor) == 0:
        corr_cj_in.loc[factor,'is_corr_max'] = 1
factor_list_filter_ic = list(corr_cj_in[corr_cj_in['is_corr_max']==1].head(410).index) # IC因子列表
factor_list_filter_tsq = list(
    tsq[tsq['select'] == 1].sort_values('rank', ascending=True).head(410).tail(410)['factor_name'])
print('tsq与IC重合度：',len(set(factor_list_filter_tsq) & set(factor_list_filter_ic)),len(factor_list_filter_ic))
## 计算rank_combine的因子列表
print('计算rank_combine的因子列表')
# corr_in = df_residual_in.rank().corr()
# print('使用残差相关性代替因子spearman相关性，用于因子相关性剔除')
corr_cj_in['is_corr_max'] = 0
corr_cj_in = corr_cj_in.sort_values(type_sort,ascending=True)
factor_info = pd.read_excel('/data/user/023859/share_file/for_qyh/factor_bank_inf_s1.xlsx')
for factor in corr_cj_in.index:
    sys.stdout.write('\r'+str(factor))
    sys.stdout.flush()
    list_good_factor = list(corr_cj_in[corr_cj_in['is_corr_max']==1].index)
    corr_in_factor = corr_in[factor]
    corr_list_factor = list(set(corr_in_factor[abs(corr_in_factor) >= corr_ratio].index) & set(list_good_factor))
    if len(corr_list_factor) == 0:
        corr_cj_in.loc[factor,'is_corr_max'] = 1
# for n in [400,800,1200]:
for n in [400,800,1200]:
    factor_list_filter_ori = list(corr_cj_in[(corr_cj_in['is_corr_max']==1)].head(n).tail(400).index) # 不一定包括基础因子
    print('')
    print(f'一共{corr_cj_in[(corr_cj_in["is_corr_max"]==1)].shape[0]}符合条件的因子')
    print(f'选取{n-400}到{n}的因子')
    # print(corr_cj_in.corr(method='spearman')['rank_combine'])
    #
    factor_list_filter = list(set(factor_list_filter_ori) | set(basic_factor_list)) # 把基础因子合并回去
    print(f'合并基础因子后，共有{len(factor_list_filter)}个因子')
    ## 重合度
    print('')
    print('与tsq重合度：',len(set(factor_list_filter) & set(factor_list_filter_tsq)),len(factor_list_filter))
    print('与IC重合度：',len(set(factor_list_filter) & set(factor_list_filter_ic)),len(factor_list_filter))
    # 训模型
    ## 全因子
    # X_train = df_factor_in.copy()
    # y_train = df_ori_in[['label_v2o10d1']].copy()
    # X_test = df_factor_out.copy()
    # y_test = df_ori_out[['label_v2o10d1']].copy()
    # xgb_train = xgb.DMatrix(X_train, label=y_train)
    # xgb_test = xgb.DMatrix(X_test, label=y_test)
    #
    # # 进行预测
    # best_params = {'learning_rate': 0.01, 'n_estimators': 800, 'max_depth': 5, 'min_child_weight': 40, 'seed': 0,
    #                 'subsample': 0.5, 'colsample_bytree': 0.9, 'gamma': 0.05, 'reg_alpha': 0.3, 'reg_lambda': 0.1}
    # model_best_params = xgb.XGBRegressor(**best_params)
    # model_best_params.fit(X_train, y_train)
    # y_pred = model_best_params.predict(X_test)
    # y_test['pred_label'] = y_pred
    # print(y_test.corr(method = 'spearman').iloc[0,1]) # 0.2512750347732314
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
    print('使用筛选后的因子训练模型')
    ## 筛选后的因子
    X_train = df_factor_in[factor_list_filter].copy()
    y_train = df_ori_in[['label_v2o10d1']].copy()
    X_test = df_factor_out[factor_list_filter].copy()
    y_test = df_ori_out[['label_v2o10d1']].copy()
    # 调参
    # 进行预测 filter后
    # best_params = get_best_para(cv_params_all,other_params,X_train,y_train)
    best_params = {'colsample_bytree': 0.3,
                   'gamma': 0.05,
                   'learning_rate': 0.01,
                   'max_depth': 6,
                   'min_child_weight': 40,
                   'n_estimators': 1400,
                   'reg_alpha': 0.1, 'reg_lambda': 0.1, 'seed': 0, 'subsample': 0.3,
                   'n_jobs':24}
    model_best_params = xgb.XGBRegressor(**best_params)
    model_best_params.fit(X_train, y_train)
    y_pred = model_best_params.predict(X_test)
    y_test['pred_label'] = y_pred
    print(y_test.corr(method = 'spearman').iloc[0,1])
    print(y_test.sort_values('pred_label',ascending = False).head(int(len(y_test)/5))['label_v2o10d1'].mean())
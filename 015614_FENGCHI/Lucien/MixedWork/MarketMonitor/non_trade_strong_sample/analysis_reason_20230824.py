# coding: utf-8
# Author：fengchi863
# Date ：2023/8/23 21:48

"""
第二种分析强势股未成交的方式，使用LIME进行分析
依赖Europa第五个区间数据，模型等
"""

import pandas as pd
import numpy as np
np.random.seed(2008)
from Zeus.Europa.v2_0_18.path_conf import *
from xgboost import XGBRegressor
from dataApi.tradeDate import get_date_range

# param = {'booster': 'gbtree', 'colsample_bytree': 0.65, 'gamma': 0.1, 'learning_rate': 0.005, 'max_depth': 3, 'min_child_weight': 5.0, 'n_estimators': 900, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 1.0, 'reg_lambda': 0.3, 'scale_pos_weight': 3.0, 'seed': 2022, 'silent': True, 'subsample': 0.9, 'tree_method': 'gpu_hist'}
param = {'booster': 'gbtree', 'colsample_bytree': 0.9, 'gamma': 0.1, 'learning_rate': 0.005, 'max_depth': 3, 'min_child_weight': 4.0, 'n_estimators': 2500, 'n_jobs': -1, 'random_state': 2023, 'reg_alpha': 0.5, 'reg_lambda': 0.5, 'scale_pos_weight': 2.0, 'silent': True, 'subsample': 1.0, 'tree_method': 'gpu_hist'}
attend_ratio = 45
date_dict = date_config['period5']

"""获取基础训练数据"""
label = 'label_pct_graded'
samples = pd.read_pickle(data_test_fpath_with_label)
X = samples[filter(lambda x: x.find('label'), samples.columns.tolist())]
X = X.dropna(how='any', axis=0)
X = samples.loc[X.index]

y = pd.read_pickle('/data/group/800463/sunss/for_xly/europa/newProfit/LabelProfit_zt_twap_0.10_800_190_SH300_SZ30.pkl')
y = y[[label]]
y.columns = [label]
y = y.drop(np.isnan(y)[label][np.isnan(y)[label]].index)
X = X.reindex(index=list(set(X.index).intersection(y.index)))

"""根据时间进行切分"""
X_copy = X.copy()
y_copy = y.copy()
X_copy = X_copy.drop(X_copy.filter(regex='label*').columns.tolist(), axis=1)
y_copy = y_copy.reindex(index=X_copy.index)

filtered_factor = pd.read_excel(xgb_imptc_period5_fpath).query('corr_selected==1')['factor_name'].tolist()
if 't_emo_ask_amtpct_mean' in filtered_factor:
    filtered_factor.remove('t_emo_ask_amtpct_mean')
X_copy = X_copy[filtered_factor]

X_copy['trade_date'] = X_copy.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()
y_copy['trade_date'] = y_copy.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()

X_train = X_copy.query(f'trade_date >= {date_dict["train_start_date"]} & trade_date <= {date_dict["valid_end_date"]}')
y_train = y_copy.query(f'trade_date >= {date_dict["train_start_date"]} & trade_date <= {date_dict["valid_end_date"]}')
X_test = X_copy.query(f'trade_date >= {date_dict["test_start_date"]} & trade_date <= {date_dict["test_end_date"]}')
y_test = y_copy.query(f'trade_date >= {date_dict["test_start_date"]} & trade_date <= {date_dict["test_end_date"]}')

y_train = y_train[[label]]
y_test = y_test[[label]]

X_train = X_train.drop('trade_date', axis=1)
X_test = X_test.drop('trade_date', axis=1)

"""训练"""
xgb_model = XGBRegressor(**param)
xgb_model.fit(X_train.values, y_train.values.ravel())
y_test_pred = xgb_model.predict(X_test.values)
best_threshold = np.percentile(y_test_pred, 100 - attend_ratio)

"""特征解释"""
from lime.lime_tabular import LimeTabularExplainer
explainer = LimeTabularExplainer(X_train.values, feature_names=np.array(filtered_factor), mode='regression')
predict_fn_xgb = lambda x: xgb_model.predict(x).astype(float)

"""针对本周特殊样本进行测试"""
# week_start_date = 20230816
# week_end_date = 20230822
week_start_date = 20230823
week_end_date = 20230829
date_list = get_date_range(week_start_date, week_end_date)
date_str_list = list(map(lambda x: str(x)[:4] + '-' + str(x)[4:6] + '-' + str(x)[6:8], date_list))

trade_file = pd.read_excel(f'/data/group/800463/sunss/复盘/周度无信号强势股/week_noBuy_strong_samples_{week_start_date}_{week_end_date}.xlsx', index_col=0, sheet_name=None)
europa = trade_file['Europa_first2']
europa_factor = pd.read_pickle(f'/data/group/800463/sunss/复盘/周度无信号强势股/week_noBuy_strong_samples_{week_start_date}_{week_end_date}_europa_factor_value.pkl')
europa_data = europa_factor[filtered_factor]

weekly_pred_reg = xgb_model.predict(europa_data.values)
weekly_pred = pd.DataFrame(weekly_pred_reg > best_threshold, index=europa_data.index)

idx = 1
exp = explainer.explain_instance(europa_data.values[idx], predict_fn_xgb, num_features=30)
print('最大值:%.6f' % exp.max_value)
print('最小值:%.6f' % exp.min_value)
print('预测值:%.6f' % exp.predicted_value)
# europa_data.iloc[idx]['Vwap']
# print(exp.domain_mapper.discretized_feature_names)
fig = exp.as_pyplot_figure()
fig.show()
exp.show_in_notebook()
exp.as_list()


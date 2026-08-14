import pandas as pd
import numpy as np
import os
import xgboost as xgb
import shap
'''
1、对训练集的全部因子中，找出在训练集上“线性”的因子（absIC>0.06)，提取其在模型(全部因子参与训练）中的shap值，得到“每个线性因子的shap值和因子值的相关系数（根据IC统一符号）”
2、将线性因子按IC分为多个档位：0.06-0.08,0.08-0.1,...，对每个档位的所有因子，计算上述相关系数的均值、标准差
3、如若该因子偏离对应档位的均值（这里根据标准差大小适配，可以魔改），该因子纳入“待剔除列表”
4、对每个属于“待剔除列表”的因子，在因子全集（训练集）中选择和其相关性高于0.8的因子，也剔除
5、以剔除后的因子集合重新训练模型，比较其和原先因子集合训出模型的差异。
'''
# 这里将factor_df拆分为factor和label，to wj:你可以根据europa情况自行处理
path = '/data/user/015585/01-因子挖掘/09-因子评估/file/factor_df_s1_20160101_20191231.pkl'
all_factor_df = pd.read_pickle(path)
factor_list = [i for i in all_factor_df.columns if 'label' not in i]
factor_df = all_factor_df[factor_list]
label_df = all_factor_df[['label_v2o10d1']]
# 线性
corr_df = factor_df.corrwith(label_df['label_v2o10d1'],method = 'spearman')
linear_list = list(corr_df[abs(corr_df) >= 0.06].index)
# 划分数据集为训练集和测试集
X_train = factor_df.loc[:pd.Timestamp('20181231')]
X_test = factor_df.loc[pd.Timestamp('20190101'):]
y_train = label_df.loc[:pd.Timestamp('20181231')]
y_test = label_df.loc[pd.Timestamp('20190101'):]
# 训练模型&预测 to wj:这一块改一改
params = {
    'booster':'gbtree',
    'n_estimators': 50,
    'learning_rate': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.55,
    'max_depth': 5,
    'gamma': 0.1,
    'min_child_weight': 1,
    'reg_alpha': 0,
    'reg_lambda': 1,
    'scale_pos_weight': 1,
    'seed': 2000,
    'objective': 'reg:linear',
    'n_jobs': -1
}
model = xgb.XGBRegressor(**params)
print('开始训练')
model.fit(X_train,y_train)
y_pred = model.predict(X_test)
y_test['pred_label'] = y_pred
print(y_test.corr(method = 'spearman').iloc[0,1])
# shap_df
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_train)
shap_df = pd.DataFrame(shap_values)
shap_df.index = X_train.index
shap_df.columns = X_train.columns
# 每个线性因子的shap值和因子值的相关系数（根据IC统一符号）
corr_shap_value = {}
for factor in linear_list:
    corr_shap_value[factor] = shap_df[[factor]].corrwith(X_train[factor],method = 'spearman').values[0] * np.sign(corr_df[factor])
res = pd.DataFrame(corr_df.copy())
res.columns = ['label_corr']
res['shap_corr'] = pd.Series(corr_shap_value)
# 待删除因子
del_factor_list = []
mean1 = res[(abs(res['label_corr']) >= 0.06) & (abs(res['label_corr']) < 0.08)]['shap_corr'].mean()
std1 = res[(abs(res['label_corr']) >= 0.06) & (abs(res['label_corr']) < 0.08)]['shap_corr'].std()
mean2 = res[(abs(res['label_corr']) >= 0.08) & (abs(res['label_corr']) < 0.1)]['shap_corr'].mean()
std2 = res[(abs(res['label_corr']) >= 0.08) & (abs(res['label_corr']) < 0.1)]['shap_corr'].std()
mean3 = res[(abs(res['label_corr']) >= 0.1) & (abs(res['label_corr']) < 0.12)]['shap_corr'].mean()
std3 = res[(abs(res['label_corr']) >= 0.1) & (abs(res['label_corr']) < 0.12)]['shap_corr'].std()
mean4 = res[(abs(res['label_corr']) >= 0.12)]['shap_corr'].mean()
std4 = res[(abs(res['label_corr']) >= 0.12)]['shap_corr'].std()
res['pattern'] = 0
res.loc[(abs(res['label_corr']) >= 0.06) & (abs(res['label_corr']) < 0.08) , 'pattern'] = 1
res.loc[(abs(res['label_corr']) >= 0.08) & (abs(res['label_corr']) < 0.1) , 'pattern'] = 2
res.loc[(abs(res['label_corr']) >= 0.1) & (abs(res['label_corr']) < 0.12) , 'pattern'] = 3
res.loc[(abs(res['label_corr']) >= 0.12), 'pattern'] = 4
for factor in linear_list:
    shap_corr_i = res.loc[factor,'shap_corr']
    label_corr_i = res.loc[factor,'label_corr']
    pattern_i = res.loc[factor,'pattern']
    if shap_corr_i <= 0:
        del_factor_list.append(factor)
    elif pattern_i == 1 and shap_corr_i <= (mean1-std1):
        del_factor_list.append(factor)
    elif pattern_i == 2 and shap_corr_i <= (mean2-std2):
        del_factor_list.append(factor)
    elif pattern_i == 3 and shap_corr_i <= (mean3-std3):
        del_factor_list.append(factor)
    elif pattern_i == 4 and shap_corr_i <= (mean4-std4):
        del_factor_list.append(factor)
# 补充与其高相关的因子
del_factor_list_final = []
# corr_factor_df = X_train.corr(method = 'spearman')
for factor in del_factor_list:
    corr_factor_df_i = X_train.corrwith(X_train[factor],method = 'spearman')
    del_factor_list_final = del_factor_list_final + list(corr_factor_df_i[abs(corr_factor_df_i) >= 0.8].index)
del_factor_list_final = list(set(del_factor_list_final))
# 重新训练模型并预测
X_train_new = X_train.drop(del_factor_list_final,axis=1)
X_test_new = X_test.drop(del_factor_list_final,axis=1)
model = xgb.XGBRegressor(**params)
model.fit(X_train_new,y_train)
y_pred_new = model.predict(X_test_new)
y_test['pred_label_new'] = y_pred_new
print(y_test.corr(method = 'spearman').iloc[0])
# shap.plots.bar(shap_values, max_display=10)

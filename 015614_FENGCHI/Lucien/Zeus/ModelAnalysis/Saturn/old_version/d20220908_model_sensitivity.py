# coding: utf-8
# Author：fengchi863
# Date ：2022/9/2 13:42

"""
模型敏感性分析：
问题提出时间：20220902
问题来源：不同的模型，结果上来看，收益差不多，风险比差不多，但是他们的重合度只有70%
"""
from Zeus.Saturn.v3_0_7.DataPrepare import DataPrepare
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
warnings.filterwarnings("ignore")
plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']

dp = DataPrepare()
samples = dp.get_samples()
label = ['label_v2o10d1']
label_data = samples[label]

#%% 分析v3_0_7中生成的模型，其中V0830ModelV3 和 beforeChgModel 的 信号重合度在0.6838
pred_reg1 = '/data/user/015614/Zeus/pred/SaturnS1/lgb_reg_model/v3_0_7/20190102~20201231_lgbRegModel_v1.csv'    # lgb_reg_model
pred_reg2 = '/data/user/015614/Zeus/pred/SaturnS1/xgb_reg_model/v3_0_4/20190102~20201231_xgbRegModel_v1.csv'    # xgb_reg_model
threshold1 = 0.010149
threshold2 = 0.008142

pred_data1 = pd.read_csv(pred_reg1, index_col=0)
pred_data2 = pd.read_csv(pred_reg2, index_col=0)
pred_data1 = pred_data1.query('datelist >= 20200701 & datelist <= 20201231')
pred_data2 = pred_data2.query('datelist >= 20200701 & datelist <= 20201231')
pred_data1 = pred_data1.rename(columns={'prediction': 'prediction1', 'pred_Reg': 'pred_Reg1'})
pred_data2 = pred_data2.rename(columns={'prediction': 'prediction2', 'pred_Reg': 'pred_Reg2'})

label_data['stockID'] = label_data.index.get_level_values(1)
label_data['datelist'] = label_data.index.get_level_values(0).strftime('%Y%m%d')
label_data['Indexs'] = label_data['stockID'] + ' ' + label_data['datelist']
label_data = label_data.set_index('Indexs', drop=True)

concat_df = pd.concat([label_data.reindex(index=pred_data1.index), pred_data1, pred_data2], axis=1)
concat_df = concat_df.drop(['stockID', 'datelist'], axis=1)
compare = concat_df.copy()

compare['preg_Reg_diff_abs'] = (compare['pred_Reg1'] - compare['pred_Reg2']).map(abs)
compare['diff_flag'] = compare['prediction1'] != compare['prediction2']
compare_diff = compare.query('diff_flag == True')
compare['same_flag'] = compare['prediction1'] == compare['prediction2']
compare_same = compare.query('same_flag == True')
len(compare_same) - len(compare_diff)
compare_same_pos = compare_same.query('prediction1 == True')
compare_same_neg = compare_same.query('prediction1 == False')
compare_diff_pos = compare_diff.query('prediction1 == True')
compare_diff_neg = compare_diff.query('prediction1 == False')
len(compare_same_pos)   # 验证成功

# 输出分位数信息
compare_same_pos['preg_Reg_diff_abs'].describe()
compare_same_neg['preg_Reg_diff_abs'].describe()

plt.figure(figsize=(16, 9))
sns.distplot(compare_same_pos['preg_Reg_diff_abs'], bins=100, kde=True, hist=True, label='预测相同的样本的预测值差异分布')
sns.distplot(compare_same_neg['preg_Reg_diff_abs'], bins=100, kde=True, hist=True, label='预测不同的样本的预测值差异分布')
from Zeus.Saturn.v3_0_7.path_conf import junk_path
plt.title('第一张图')
plt.legend()
plt.savefig(junk_path + '预测值差异分布.png', bbox_inches='tight', pad_inches=0.1)
from dataApi.sendInfo import send_file
send_file(junk_path + '预测值差异分布.png')

plt.figure(figsize=(16, 9))
sns.distplot(compare_same['preg_Reg_diff_abs'], bins=100, kde=True, hist=True, label='预测相同的样本的预测值差异分布')
sns.distplot(compare_diff['preg_Reg_diff_abs'], bins=100, kde=True, hist=True, label='预测不同的样本的预测值差异分布')
from Zeus.Saturn.v3_0_7.path_conf import junk_path
plt.title('第四张图')   # 预测不同的
plt.legend()
plt.savefig(junk_path + '预测值差异分布.png', bbox_inches='tight', pad_inches=0.1)
from dataApi.sendInfo import send_file
send_file(junk_path + '预测值差异分布.png')

# 预测相同和不同的样本的收益分布情况
plt.figure(figsize=(16, 9))
sns.distplot(compare_same_pos['label_v2o10d1'], bins=100, kde=True, hist=True, label='预测相同的正样本的标签差异分布')
sns.distplot(compare_diff_pos['label_v2o10d1'], bins=100, kde=True, hist=True, label='预测不同的正样本的标签差异分布')
plt.title('第五张图')
plt.legend()
plt.savefig(junk_path + '标签差异分布.png', bbox_inches='tight', pad_inches=0.1)
send_file(junk_path + '标签差异分布.png')

# 预测相同和不同的样本的收益分布情况
plt.figure(figsize=(16, 9))
sns.distplot(compare_same_pos['label_v2o10d1'], bins=100, kde=True, hist=True, label='预测相同的样本的标签差异分布')
sns.distplot(compare_same_neg['label_v2o10d1'], bins=100, kde=True, hist=True, label='预测不同的样本的标签差异分布')
plt.title('第二张图')
plt.legend()
plt.savefig(junk_path + '标签差异分布.png', bbox_inches='tight', pad_inches=0.1)
send_file(junk_path + '标签差异分布.png')

# 整体预测值的分布情况
plt.figure(figsize=(16, 9))
sns.distplot(compare['pred_Reg1'], bins=100, kde=True, hist=True, label='prediction1')
sns.distplot(compare['pred_Reg2'], bins=100, kde=True, hist=True, label='prediction2')
plt.title('第三张图')
plt.legend()
plt.savefig(junk_path + '整体预测值的分布情况.png', bbox_inches='tight', pad_inches=0.1)
send_file(junk_path + '整体预测值的分布情况.png')

compare_same['label_v2o10d1_abs'] = compare_same['label_v2o10d1'].map(abs)
compare_diff['label_v2o10d1_abs'] = compare_diff['label_v2o10d1'].map(abs)
compare_same.query('label_v2o10d1_abs <= 0.05').shape, compare_same.shape
compare_diff.query('label_v2o10d1_abs <= 0.05').shape, compare_diff.shape

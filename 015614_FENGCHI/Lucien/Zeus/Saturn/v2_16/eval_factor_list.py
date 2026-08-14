# coding: utf-8
# Author：fengchi863
# Date ：2022/8/17 19:08

from Zeus.Saturn.v2_16.path_conf import factor_score_fpath, filter_factor_fpath, factor_path
from LucienUtil.FileUtil import FileUtil
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np

strategy_name = 'SaturnS1'
version = 'v2_16'
model_name = 'xgb_reg_model'

output_path = factor_path + f'{strategy_name}/{model_name}/{version}/'

scaler = StandardScaler()

print('开始进行因子排序')
factor_score = pd.read_excel(factor_score_fpath, index_col=0)
filter_factor = pd.read_excel(filter_factor_fpath, index_col=0)

xgb_imptc_factor = filter_factor.query('corr_selected==1')
xgb_imptc_factor = xgb_imptc_factor.sort_values('feature_importance', ascending=False).set_index('factor_name')
xgb_imptc_factor = xgb_imptc_factor.drop('corr_selected', axis=1)
# 采用标准化处理因子顺序
# xgb_imptc_factor = pd.DataFrame(scaler.fit_transform(xgb_imptc_factor.copy()), index=xgb_imptc_factor.index, columns=xgb_imptc_factor.columns)
# 使用rank排名
xgb_imptc_factor = pd.DataFrame(xgb_imptc_factor.rank(), index=xgb_imptc_factor.index, columns=xgb_imptc_factor.columns)

factor_score = factor_score.set_index('factor_name')
factor_score = factor_score.loc[~pd.isna(factor_score['区间1-out-value'])]
factor_score = factor_score.reindex(index=xgb_imptc_factor.index)
# 采用标准化处理因子顺序
# factor_score['区间1-out-value'] = scaler.fit_transform(factor_score['区间1-out-value'].values[:, None])
# 使用rank排名
factor_score['区间1-out-value_rank'] = factor_score['区间1-out-value'].rank()

score = pd.concat([xgb_imptc_factor, factor_score], axis=1)
score['total_score'] = score['feature_importance'] + score['区间1-out-value']
score = score.sort_values(['total_score'], ascending=False)
filtered_factor_list = score.index.tolist()
FileUtil.save_list2pkl(filtered_factor_list, output_path, 'factor_list.pkl')

"""
tmp_list = xgb_imptc_factor['factor_name'].tolist()
check1 = list(filter(lambda x: '93030' in x, tmp_list))
共607个因子，剔除后剩274个
其中有93030在内的70个，剔除后剩15个；

xgb_imptc_factor = xgb_imptc_factor.reindex(index=check1)
93030 8个在前150名(rank>150)，30s1 10个在前150名(rank>150)
"""
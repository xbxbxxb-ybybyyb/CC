# coding: utf-8
# Author：fengchi863
# Date ：2022/8/17 19:08

from Zeus.Saturn.v3_0_14.path_conf import filter_factor_fpath, factor_path
from LucienUtil.FileUtil import FileUtil
import pandas as pd

strategy_name = 'SaturnS1'
version = 'v3_0_14'
# model_name = 'xgb_reg_model'
model_name = 'lgb_reg_model'

#%% 第一种方式，只是用valid_shap_corr_positive_ratio指标
output_path = factor_path + f'{strategy_name}/{model_name}/{version}/'

print('开始进行因子排序')
filter_factor = pd.read_excel(filter_factor_fpath, index_col=0)

# _xgb_imptc_factor = filter_factor.query('corr_selected==1')
_xgb_imptc_factor = filter_factor.copy()
_xgb_imptc_factor = _xgb_imptc_factor.sort_values('valid_shap_corr_positive_ratio', ascending=False).set_index('factor_name')
xgb_imptc_factor = _xgb_imptc_factor.iloc[:271]

# 使用rank排名
# xgb_imptc_factor = pd.DataFrame(xgb_imptc_factor.rank(ascending=False), index=xgb_imptc_factor.index, columns=xgb_imptc_factor.columns)

score = xgb_imptc_factor.copy()
score = score.sort_values(['valid_shap_corr_positive_ratio'], ascending=False)
filtered_factor_list = score.index.tolist()
FileUtil.save_list2pkl(filtered_factor_list, output_path, 'factor_list.pkl')
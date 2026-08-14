# coding: utf-8
# Author：fengchi863
# Date ：2022/8/17 19:08

from Zeus.Saturn.v3_0_17.path_conf import filter_factor_fpath, factor_path
from LucienUtil.FileUtil import FileUtil
import pandas as pd

strategy_name = 'SaturnS1'
version = 'v3_0_17'
# model_name = 'xgb_reg_model'
model_name = 'lgb_reg_model'

#%% 第一种方式，只是用count指标
output_path = factor_path + f'{strategy_name}/{model_name}/{version}/'

print('开始进行因子排序')
filter_factor = pd.read_excel(filter_factor_fpath, index_col=0)

# _xgb_imptc_factor = filter_factor.query('corr_selected==1')
_xgb_imptc_factor = filter_factor.sort_values('feature_importance_rank_mean')
_xgb_imptc_factor = _xgb_imptc_factor.query('feature_importance_rank_mean < 320')

_xgb_imptc_factor = _xgb_imptc_factor.sort_values('feature_importance_rank_std', ascending=True).set_index('factor_name')
xgb_imptc_factor = _xgb_imptc_factor.iloc[:271]
filtered_factor_list = xgb_imptc_factor.index.tolist()
FileUtil.save_list2pkl(filtered_factor_list, output_path, 'factor_list.pkl')
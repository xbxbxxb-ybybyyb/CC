# coding: utf-8
# Author：fengchi863
# Date ：2022/8/17 19:08

from Zeus.Saturn.v3_0_18.path_conf import filter_factor_fpath, factor_path
from LucienUtil.FileUtil import FileUtil
import pandas as pd

strategy_name = 'SaturnS1'
version = 'v3_0_18'
# model_name = 'xgb_reg_model'
model_name = 'lgb_reg_model'

filter_factor = pd.read_excel(filter_factor_fpath, index_col=0)
emotion_factor_list = filter_factor.query('factor_owner == "emotion"')['factor_name'].tolist()

#%% 第二种方式，只是用valid_shap_corr_positive_ratio指标
output_path = factor_path + f'{strategy_name}/{model_name}/{version}/'

print('开始进行因子排序')
filter_factor = pd.read_excel(filter_factor_fpath, index_col=0)

# _xgb_imptc_factor = filter_factor.query('corr_selected==1')
xgb_imptc_factor = filter_factor.copy().set_index('factor_name')

_xgb_imptc_factor = xgb_imptc_factor.loc[emotion_factor_list]
_xgb_imptc_factor = _xgb_imptc_factor.sort_values('valid_shap_corr_positive_ratio', ascending=False)
emotion_ranked_factor_list = _xgb_imptc_factor.index.tolist()

xgb_imptc_factor = xgb_imptc_factor.drop(emotion_factor_list).sort_values('valid_shap_corr_positive_ratio', ascending=False)
filtered_factor_list = xgb_imptc_factor.iloc[:271].index.tolist()

# 不使用情绪因子，使用排序后的271个其他因子
FileUtil.save_list2pkl(filtered_factor_list, output_path, 'factor_list.pkl')
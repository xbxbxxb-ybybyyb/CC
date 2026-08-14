# coding: utf-8
# Author：fengchi863
# Date ：2022/8/17 19:08

from Zeus.Saturn.v3_0_15.path_conf import factor_score_fpath, filter_factor_fpath, factor_path
from LucienUtil.FileUtil import FileUtil
from sklearn.preprocessing import StandardScaler
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

strategy_name = 'SaturnS1'
version = 'v3_0_15'
# model_name = 'xgb_reg_model'
model_name = 'lgb_reg_model'

output_path = factor_path + f'{strategy_name}/{model_name}/{version}/'

scaler = StandardScaler()
print('开始进行因子排序')
filter_factor = pd.read_excel(filter_factor_fpath, index_col=0)

_xgb_imptc_factor = filter_factor.copy()
_xgb_imptc_factor = _xgb_imptc_factor.sort_values('count', ascending=False).set_index('factor_name')
xgb_imptc_factor = _xgb_imptc_factor
xgb_imptc_factor1 = pd.DataFrame(xgb_imptc_factor.rank(ascending=False), index=xgb_imptc_factor.index, columns=xgb_imptc_factor.columns)

_xgb_imptc_factor = filter_factor.copy()
_xgb_imptc_factor = _xgb_imptc_factor.sort_values('valid_shap_corr_positive_ratio', ascending=False).set_index('factor_name')
xgb_imptc_factor = _xgb_imptc_factor
xgb_imptc_factor2 = pd.DataFrame(xgb_imptc_factor.rank(ascending=False), index=xgb_imptc_factor.index, columns=xgb_imptc_factor.columns)

score = pd.concat([xgb_imptc_factor1['count'], xgb_imptc_factor2['valid_shap_corr_positive_ratio']], axis=1)
score['total_score'] = score['count'] + score['valid_shap_corr_positive_ratio']
# score = score.sort_values(['total_score'], ascending=False) # TODO:这里搞错了，应该是去掉这个ascending=False，前面已经从大到小排序了，这里再排一次就应该是选后面的了
score = score.sort_values(['total_score'])
filtered_factor_list = score.index.tolist()[:271]   # 越小越好应该
FileUtil.save_list2pkl(filtered_factor_list, output_path, 'factor_list.pkl')
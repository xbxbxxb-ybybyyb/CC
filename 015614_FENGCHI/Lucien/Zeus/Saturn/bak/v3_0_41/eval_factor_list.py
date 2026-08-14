# coding: utf-8
# Author：fengchi863
# Date ：2022/8/17 19:08

from Zeus.Saturn.v3_0_41.path_conf import factor_score_fpath, filter_factor_fpath, factor_path
from LucienUtil.FileUtil import FileUtil
from sklearn.preprocessing import StandardScaler
import pandas as pd

strategy_name = 'SaturnS1'
version = 'v3_0_41'
# model_name = 'xgb_reg_model'
model_name = 'lgb_reg_model'

output_path = factor_path + f'{strategy_name}/{model_name}/{version}/'

scaler = StandardScaler()
print('开始进行因子排序')
factor_score = pd.read_excel(factor_score_fpath, index_col=0)
filter_factor = pd.read_excel(filter_factor_fpath, index_col=0)

_xgb_imptc_factor = filter_factor.query('corr_selected==1')
filtered_factor_list = _xgb_imptc_factor['factor_name'].tolist()
drop_factor_list = ['saturn_30s1_sss_tk1mcs_ret931_cv',
                     'saturn_t931_sss_tk1mcs_ret931_skew',
                     'saturn_t93030_sss_tk1mcs_ret931_cv',
                     'saturn_30s1_sss_tk1mcs_ret931_skew',
                     'saturn_t93030_sss_tk1mcs_ret931_kurt',
                     'saturn_30s1_sss_tk1mcs_cl2hl_cv',
                     'saturn_sss_lastsample_ret_mean']   # 配合stats_emotion_factor_evaluate_test5.py的筛选
filtered_factor_list = list(set(filtered_factor_list).difference(set(drop_factor_list)))
print(f'因子数量有{len(filtered_factor_list)}个')
FileUtil.save_list2pkl(filtered_factor_list, output_path, 'factor_list.pkl')
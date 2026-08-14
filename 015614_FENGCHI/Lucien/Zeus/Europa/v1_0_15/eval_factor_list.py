# coding: utf-8
# Author：fengchi863
# Date ：2022/8/17 19:08

from Zeus.Europa.v1_0_15.path_conf import factor_score_fpath, filter_factor_fpath, factor_path
from LucienUtil.FileUtil import FileUtil
from sklearn.preprocessing import StandardScaler
import pandas as pd

strategy_name = 'Europa'
version = 'v1_0_15'
model_name = 'xgb_reg_model'
# model_name = 'lr_reg_model'
# model_name = 'lgb_reg_model'

output_path = factor_path + f'{strategy_name}/{model_name}/{version}/'

scaler = StandardScaler()
print('开始进行因子排序')
factor_score = pd.read_excel(factor_score_fpath, index_col=0)
filter_factor = pd.read_excel(filter_factor_fpath, index_col=0)

_xgb_imptc_factor = filter_factor.query('select==1')
filtered_factor_list = _xgb_imptc_factor.index.tolist()

print(f'因子数量有{len(filtered_factor_list)}个')
FileUtil.save_list2pkl(filtered_factor_list, output_path, 'factor_list.pkl')
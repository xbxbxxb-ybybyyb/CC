# coding: utf-8
# Author：fengchi863
# Date ：2022/8/17 19:08

from Zeus.Saturn.v3_0_32.path_conf import factor_score_fpath, filter_factor_fpath, factor_path
from Zeus.Saturn.v3_0_21.path_conf import factor_score_fpath as factor_score_fpath21
from LucienUtil.FileUtil import FileUtil
from sklearn.preprocessing import StandardScaler
import pandas as pd

strategy_name = 'SaturnS1'
version = 'v3_0_32'
# model_name = 'xgb_reg_model'
model_name = 'lgb_reg_model'

output_path = factor_path + f'{strategy_name}/{model_name}/{version}/'

scaler = StandardScaler()
print('开始进行因子排序')
factor_score = pd.read_excel(factor_score_fpath, index_col=0)
filter_factor = pd.read_excel(filter_factor_fpath, index_col=0)

_xgb_imptc_factor = filter_factor.query('corr_selected==1')

# 查询这次的T日因子
emotion_factor = pd.read_excel('/data/group/800463/sunss/for_xly/saturn/V6_20220927/V6_20220927_3period/factor_bank_inf_all_931_emotion.xlsx')
added_emotion_factor = emotion_factor.query('提交时间 >= 20220926 & emotion == 1')
# added_emotion_factor = added_emotion_factor[added_emotion_factor['区间1-out-value'] < 5]
# added_emotion_factor_list_less_5 = added_emotion_factor['factor_name'].tolist()
# filtered_factor_list = _xgb_imptc_factor['factor_name'].tolist()
# filtered_factor_list = list(set(filtered_factor_list).difference(set(added_emotion_factor_list_less_5)))

old_factor_score = pd.read_excel(factor_score_fpath21)
old_emotion_score = old_factor_score.query('factor_owner == "emotion"')
# old_emotion_score = old_emotion_score[old_emotion_score['区间1-out-value'] < 5]
# old_emotion_factor_list_less_5 = old_emotion_score['factor_name'].tolist()
# filtered_factor_list = list(set(filtered_factor_list).difference(set(old_emotion_factor_list_less_5)))

factor_list27 = FileUtil.read_list(factor_path + f'SaturnS1/lgb_reg_model/v3_0_25/', 'factor_list.pkl')
concat_emotion_factor = pd.concat([old_emotion_score, added_emotion_factor], axis=0)
emotion_factor_list = concat_emotion_factor['factor_name'].tolist()
filtered_emotion_factor = list(set(factor_list27).intersection(set(emotion_factor_list)))
concat_emotion_factor = concat_emotion_factor.set_index('factor_name').loc[filtered_emotion_factor]

concat_emotion_factor['total_score'] = concat_emotion_factor['区间1-in-value'] + concat_emotion_factor['区间1-out-value']
concat_emotion_factor = concat_emotion_factor.sort_values('total_score', ascending=False)
droped_factor_list = concat_emotion_factor.iloc[15:].index.tolist()

filtered_factor_list = _xgb_imptc_factor['factor_name'].tolist()
filtered_factor_list = list(set(filtered_factor_list).difference(set(droped_factor_list)))

print(f'因子数量有{len(filtered_factor_list)}个')
FileUtil.save_list2pkl(filtered_factor_list, output_path, 'factor_list.pkl')

watch_emotion_factor = concat_emotion_factor.iloc[3:]
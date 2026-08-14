# coding: utf-8
# Author：fengchi863
# Date ：2022/10/12 8:52

"""
20221014周五下午提交了新的因子FilterV1结果之后，双姐询问多增加了哪些因子，然后进行的统计
"""
import pandas as pd
from LucienUtil.FileUtil import FileUtil
from Zeus.Saturn.v3_0_15.path_conf import factor_path
from Zeus.Saturn.v3_0_24.path_conf import filter_factor_fpath, factor_score_fpath
from Zeus.Saturn.v3_0_25.DataPrepare import DataPrepare # 20220927版本的因子

old_filter_factor = pd.read_excel(filter_factor_fpath, index_col=0)
old_factor_score = pd.read_excel(factor_score_fpath)
old_emotion_factor = old_filter_factor.query('factor_owner == "emotion"')
old_emotion_score = old_factor_score.query('factor_owner == "emotion"')

# old_emotion_factor_list = old_filter_factor.query('factor_owner == "emotion"')['factor_name'].tolist()
# old_emotion_score = old_emotion_score.set_index('factor_name').loc[old_emotion_factor_list]
old_emotion_factor_list = old_emotion_score['factor_name'].tolist()

emotion_factor = pd.read_excel('/data/group/800463/sunss/for_xly/saturn/V6_20220927/V6_20220927_3period/factor_bank_inf_all_931_emotion.xlsx')
# added_emotion_factor = emotion_factor.query('提交时间 >= 20220926 & emotion == 1')
added_emotion_factor = emotion_factor.query('emotion == 1')
added_emotion_factor_list = added_emotion_factor['factor_name'].tolist()

factor_list23 = FileUtil.read_list(factor_path + f'SaturnS1/lgb_reg_model/v3_0_24/', 'factor_list.pkl')
factor_list27 = FileUtil.read_list(factor_path + f'SaturnS1/lgb_reg_model/v3_0_34/', 'factor_list.pkl')

# 看0927版本中情绪因子占据了多少
common_emotion_factor_list = list(set(factor_list27).intersection(set(old_emotion_factor_list)))
print(f'0927版本中原来的情绪因子有{len(common_emotion_factor_list)}个') # 全部纳入进来了
added_common_emotion_factor_list = list(set(factor_list27).intersection(set(added_emotion_factor_list)))
print(f'0927版本中新的情绪因子有{len(added_common_emotion_factor_list)}个')
print(f'0927版本中一共新增的情绪因子有{len(added_emotion_factor_list)}个')
all_emotion_factor = pd.concat([old_emotion_score, added_emotion_factor.set_index('factor_name').loc[added_common_emotion_factor_list]], axis=0)
all_emotion_factor_copy = all_emotion_factor.iloc[:, -12:]
#%% 统计这14个情绪因子与其他情绪因子的
dp = DataPrepare()
dataset = dp.get_samples()

emotion_factor_list27 = old_emotion_factor_list + added_common_emotion_factor_list

#%% 获取情绪因子的序列
start_date = 20160101
end_date = 20190930
dataset_factor = dataset.copy()[emotion_factor_list27]
dataset_factor['trade_date'] = dataset_factor.index.get_level_values(0).map(lambda x: int(x.strftime('%Y%m%d')))
X_train = dataset_factor.query('trade_date >= @start_date & trade_date <= @end_date')
X_train = X_train.groupby('trade_date').first()

corr_df = X_train.corr()
from dataApi.sendInfo import send_file
send_file(corr_df)


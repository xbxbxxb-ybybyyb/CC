import os
import pandas as pd
sample = pd.read_pickle('/data/user/015585/01-因子挖掘/20240812-Ceres新增买入时点/file/test_trigger1_3.pkl')
st_filter = sample['st_indicator'] != 1
open_filter = (sample['T_open_is_zt'] == False) & (sample['T_open_is_dt'] == False)
after_not_ul_len_filter = sample['after_not_ul_len'] > 10
can_buy_filter = sample['T_first_trans_ZT'] != 1
base_filter = st_filter & open_filter & after_not_ul_len_filter & can_buy_filter
sample_filter931 = sample[base_filter&((sample['T_day_first_ZT_Time'] <=93100000) == False)&((sample['T_day_first_DT_Time'] <=93100000) == False)&(~sample['label_v2o10d1'].isna())]
sample_filter_t = sample[base_filter&((sample['T_day_first_ZT_Time'] <=sample['trigger_time']) == False)&((sample['T_day_first_DT_Time'] <=sample['trigger_time']) == False)&(~sample['label_v2t10'].isna())]
print('筛选样本：',len(sample_filter931),len(sample_filter_t))
print('基准label:', sample_filter931['label_v2o10d1'].mean())
print('新时点label:', sample_filter_t['label_v2t10'].mean())
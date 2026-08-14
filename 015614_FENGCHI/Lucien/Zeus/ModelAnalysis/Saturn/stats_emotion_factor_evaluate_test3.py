# coding: utf-8
# Author：fengchi863
# Date ：2022/10/20 11:03

"""
目标在包含旧版本情绪因子的排名前50的因子基准上，测试14个因子的边际IC，剔除边际IC增幅小于0的因子
"""

import pandas as pd
import numpy as np
from Zeus.Saturn.v3_0_25.path_conf import filter_factor_fpath, factor_score_fpath
from LucienUtil.FileUtil import FileUtil
from sklearn.linear_model import LinearRegression
from Zeus.Saturn.v3_0_25.DataPrepare import DataPrepare
from scipy.stats import pearsonr
from dataApi.sendInfo import send_message
from tqdm import tqdm
from Zeus.Saturn.v3_0_25.path_conf import factor_path
import random
random.seed(2022)

def calc_ic(factor_list, data, train_start_date, train_end_date, test_start_date, test_end_date, label):
    data_copy = data.copy()
    train_samples = data_copy.query(f'trade_dt >= {train_start_date} & trade_dt <= {train_end_date}')
    train_samples = train_samples.loc[:, factor_list]
    train_label = data_copy.loc[:, label].reindex(index=train_samples.index)
    test_samples = data_copy.query(f'trade_dt >= {test_start_date} & trade_dt <= {test_end_date}')
    test_samples = test_samples.loc[:, factor_list]
    test_label = data_copy.loc[:, label].reindex(index=test_samples.index)
    linear_model = LinearRegression()
    model = linear_model.fit(train_samples, train_label)
    preds = model.predict(test_samples)
    ic = pearsonr(test_label.values, preds)[0]
    return ic

BASIC_NUM = 50
label_name = 'label_v2o10d1'
dp = DataPrepare()

filter_factor = pd.read_excel(filter_factor_fpath, index_col=0)
emotion_factor0927 = pd.read_excel('/data/group/800463/sunss/for_xly/saturn/V6_20220927/V6_20220927_3period/factor_bank_inf_all_931_emotion.xlsx', index_col=0)
emotion_factor0927 = emotion_factor0927.query('emotion == 1')   # 49个，旧版本上变成了有选出了13/24个情绪因子了，新版本上是14/25个

emotion_factor = filter_factor.query('corr_selected==1').set_index('factor_name').loc[emotion_factor0927['factor_name'].tolist()].reset_index()
emotion_factor = emotion_factor.loc[emotion_factor['corr_selected'].dropna().index] # 27个被选出的corr_selected==1的情绪因子

# 0927版本新增的corr_selected==1的因子
factor_list27 = FileUtil.read_list(factor_path + f'SaturnS1/lgb_reg_model/v3_0_25/', 'factor_list.pkl')
factor_list23 = FileUtil.read_list(factor_path + f'SaturnS1/lgb_reg_model/v3_0_21/', 'factor_list.pkl')
added_emotion_factor_list = list(set(emotion_factor['factor_name'].tolist()).difference(set(factor_list23)))    # 新增的corr_seleted==1的14个因子

other_factor = list(set(filter_factor['factor_name'].tolist()).difference(set(added_emotion_factor_list)))
other_factor = filter_factor.set_index('factor_name').loc[other_factor]

# 选非本轮增加的情绪因子前50名
ranked_other_factor = other_factor.sort_values('count', ascending=False)
basic_other_factor = ranked_other_factor.iloc[:BASIC_NUM].index.tolist()

#%% 开始进行测试
samples = dp.get_samples()
label_list = samples.filter(regex='label*').columns.tolist()
samples['trade_dt'] = samples.index.get_level_values(0).strftime('%Y%m%d').astype(int)

y = samples[[label_name]]
y = y.drop(np.isnan(y)[label_name][np.isnan(y)[label_name]].index)
samples = samples.reindex(index=y.index)

margin_ic_score = pd.DataFrame(index=added_emotion_factor_list)
for add_factor_name in tqdm(added_emotion_factor_list):
    ic = calc_ic(basic_other_factor, samples, 20160101, 20181231, 20190101, 20190930, label_name)
    ic2 = calc_ic(basic_other_factor + [add_factor_name], samples, 20160101, 20181231, 20190101, 20190930, label_name)

    margin_ic = np.sqrt(ic2 ** 2 - ic ** 2) if abs(ic2) > abs(ic) else np.nan
    margin_ic_pct = abs(ic2) / abs(ic) -1
    margin_ic_score.loc[add_factor_name, 'ic'] = ic
    margin_ic_score.loc[add_factor_name, 'ic2'] = ic2
    margin_ic_score.loc[add_factor_name, 'margin_ic'] = margin_ic
    margin_ic_score.loc[add_factor_name, 'margin_ic_pct'] = margin_ic_pct

# 根据原始没有0927新增的情绪因子基础上，添加这14个因子，然后进行模型训练观测结果
# 去掉了三个因子['saturn_sss_pct5_mean', 'saturn_t931_sss_tk1mcs_ret931_skew', 'saturn_30s1_sss_tk1mcs_ret931_kurt']
margin_ic_score.query('margin_ic_pct < 0').index.tolist()





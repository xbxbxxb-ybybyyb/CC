# coding: utf-8
# Author：fengchi863
# Date ：2022/10/20 11:03


import pandas as pd
import numpy as np
from Zeus.Saturn.v3_0_25.path_conf import filter_factor_fpath, factor_score_fpath
from LucienUtil.FileUtil import FileUtil
from sklearn.linear_model import LinearRegression
from Zeus.Saturn.v3_0_25.DataPrepare import DataPrepare
from scipy.stats import pearsonr
from dataApi.tradeDate import trade_months
from dataApi.sendInfo import send_message
from tqdm import tqdm
from Zeus.Saturn.v3_0_25.path_conf import factor_path
import random
random.seed(2022)

start_date = 20160101
end_date = 20190930

# 这种方式会造成存在未来信息，可能把一天的内容隔开了，并且函数也还没有调试好
# def get_rolling_train_test_date(data, window_num):
#     train_test_idx_list = list()
#     data_copy = data.copy()
#     data_len = len(data_copy)
#     window_len = data_len // window_num
#     train_start_idx = 0
#     train_end_idx = window_len
#     test_start_idx = window_len
#     test_end_idx = window_len + window_len
#     train_test_idx_list.append((train_start_idx, train_end_idx, test_start_idx, test_end_idx))
#     while train_end_idx < data_len:
#         train_start_idx += window_len
#         train_end_idx += window_len
#         test_start_idx += window_len
#         test_end_idx += window_len
#         train_test_idx_list.append((train_start_idx, train_end_idx, test_start_idx, test_end_idx))
#     if train_start_idx < data_len:
#         train_test_idx_list.append((train_start_idx, train_end_idx, test_start_idx, data_len))
#     return train_test_idx_list

trade_months = list(filter(lambda x: 201909 >= x >= 201601, list(map(lambda x: x // 100, trade_months))))
def get_rolling_train_test_date(window_month=3):
    train_test_idx_list = list()
    month_len = len(trade_months)
    train_start_idx = 0
    train_end_idx = window_month
    test_start_idx = window_month
    test_end_idx = window_month + window_month
    train_test_idx_list.append((train_start_idx, train_end_idx, test_start_idx, test_end_idx))
    while test_end_idx < month_len - 1:
        train_start_idx += window_month
        train_end_idx += window_month
        test_start_idx += window_month
        test_end_idx += window_month
        train_test_idx_list.append((train_start_idx, train_end_idx, test_start_idx, test_end_idx))
    if test_start_idx < window_month & test_end_idx != month_len:
        train_test_idx_list.append((train_start_idx, train_end_idx, test_start_idx, month_len))
    return train_test_idx_list

def calc_ic(factor_list, data, train_start_date, train_end_date, test_start_date, test_end_date, label):
    data_copy = data.copy()
    data_copy['trade_month'] = data_copy.index.get_level_values(0).strftime('%Y%m').astype(int)
    train_samples = data_copy.query(f'trade_month >= {train_start_date} & trade_month <= {train_end_date}')
    train_samples = train_samples.loc[:, factor_list]
    train_label = data_copy.loc[:, label].reindex(index=train_samples.index)
    test_samples = data_copy.query(f'trade_month >= {test_start_date} & trade_month <= {test_end_date}')
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

train_test_idx_list = get_rolling_train_test_date(window_month=3)

margin_ic_score = pd.DataFrame(index=pd.MultiIndex.from_product([added_emotion_factor_list, ['ic', 'ic2', 'margin_ic', 'margin_ic_pct']]))
for idx in tqdm(range(len(train_test_idx_list))):
    train_start_idx, train_end_idx, test_start_idx, test_end_idx = train_test_idx_list[idx]
    train_start_month, train_end_month = trade_months[train_start_idx:train_end_idx][0], trade_months[train_start_idx:train_end_idx][-1]
    test_start_month, test_end_month = trade_months[test_start_idx:test_end_idx][0], trade_months[test_start_idx:test_end_idx][-1]
    for add_factor_name in added_emotion_factor_list:
        ic = calc_ic(basic_other_factor, samples, train_start_month, train_end_month, test_start_month, test_end_month, label_name)
        ic2 = calc_ic(basic_other_factor + [add_factor_name], samples, train_start_month, train_end_month, test_start_month, test_end_month, label_name)

        margin_ic = np.sqrt(ic2 ** 2 - ic ** 2) if abs(ic2) > abs(ic) else -np.sqrt(ic ** 2 - ic2 ** 2)
        margin_ic_pct = abs(ic2) / abs(ic) - 1
        margin_ic_score.loc[(add_factor_name, 'ic'), f'{train_start_month}-{train_end_month}'] = ic
        margin_ic_score.loc[(add_factor_name, 'ic2'), f'{train_start_month}-{train_end_month}'] = ic2
        margin_ic_score.loc[(add_factor_name, 'margin_ic'), f'{train_start_month}-{train_end_month}'] = margin_ic
        margin_ic_score.loc[(add_factor_name, 'margin_ic_pct'), f'{train_start_month}-{train_end_month}'] = margin_ic_pct

margin_ic_score.index.names = ['factor_name', 'indicator']
# margin_ic_pct = margin_ic_score.reset_index().query('indicator == "margin_ic_pct"')
# margin_ic_pct = margin_ic_pct.drop('indicator',axis=1).set_index('factor_name')
margin_ic = margin_ic_score.reset_index().query('indicator == "margin_ic"')
margin_ic = margin_ic.drop('indicator',axis=1).set_index('factor_name')
margin_ic_mean = margin_ic.mean(axis=1)
margin_ic_ir = margin_ic.mean(axis=1) / margin_ic.std(axis=1)
margin_ic_pct = margin_ic > 0
margin_ic_pct_winrate = (margin_ic_pct.sum(axis=1) / margin_ic_pct.shape[1]).sort_values(ascending=False)

margin_ic_mean[margin_ic_mean < -0.01].index.tolist()
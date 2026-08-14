# coding: utf-8
# Author：fengchi863
# Date ：2022/10/17 9:45

"""
测试私募提供的方案
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
emotion_factor0927 = emotion_factor0927.query('emotion == 1')   # 49个，旧版本上变成了有13个情绪因子了
emotion_factor = filter_factor.query('corr_selected==1').set_index('factor_name').loc[emotion_factor0927['factor_name'].tolist()].reset_index()
emotion_factor = emotion_factor.loc[emotion_factor['corr_selected'].dropna().index]

other_factor = list(set(filter_factor['factor_name'].tolist()).difference(set(emotion_factor['factor_name'].tolist())))
score_factor = pd.read_excel(factor_score_fpath, index_col=0)
other_factor = filter_factor.set_index('factor_name').loc[other_factor]

ranked_other_factor = other_factor.sort_values('count', ascending=False)
basic_other_factor = ranked_other_factor.iloc[:BASIC_NUM].index.tolist()

samples = dp.get_samples()
label_list = samples.filter(regex='label*').columns.tolist()
samples['trade_dt'] = samples.index.get_level_values(0).strftime('%Y%m%d').astype(int)

y = samples[[label_name]]
y = y.drop(np.isnan(y)[label_name][np.isnan(y)[label_name]].index)
samples = samples.reindex(index=y.index)

margin_ic_score = pd.DataFrame(index=emotion_factor['factor_name'].tolist())
for add_factor_name in tqdm(emotion_factor['factor_name'].tolist()):
    ic = calc_ic(basic_other_factor, samples, 20160101, 20181231, 20190101, 20190930, label_name)
    ic2 = calc_ic(basic_other_factor + [add_factor_name], samples, 20160101, 20181231, 20190101, 20190930, label_name)

    margin_ic = np.sqrt(ic2 ** 2 - ic ** 2) if abs(ic2) > abs(ic) else np.nan
    margin_ic_score.loc[add_factor_name, 'ic'] = ic
    margin_ic_score.loc[add_factor_name, 'ic2'] = ic2
    margin_ic_score.loc[add_factor_name, 'margin_ic'] = margin_ic

# 判断是哪一次增加的因子
margin_ic_score.index.name = 'factor_name'
check = pd.merge(margin_ic_score, emotion_factor0927, on='factor_name').sort_values('margin_ic', ascending=False)
filtered_list = check.query('margin_ic > 0')['factor_name'].tolist()
print(f'数量有{len(filtered_list)}个')
FileUtil.save_list2pkl(filtered_list, '/data/user/015614/junkData/', f'count_{BASIC_NUM}.pkl')
filtered_list_out_value = FileUtil.read_list('/data/user/015614/junkData/', f'out_value_{BASIC_NUM}.pkl')
diff_factor_list1 = list(set(filtered_list).difference(filtered_list_out_value))
diff_factor_list2 = list(set(filtered_list_out_value).difference(filtered_list))
common_factor_list = list(set(filtered_list).intersection(filtered_list_out_value))
msg = f'共有{len(filtered_list)}个因子被选出，和区间1-out-value筛选方式对比，相同的因子有{len(common_factor_list)}个，不同的因子有{len(diff_factor_list1) + len(diff_factor_list2)}个，在区间1-out-value中不在count中的因子有{len(diff_factor_list2)}个，反之有{len(diff_factor_list1)}个。'
print(msg)
send_message(msg)

"""
# 0927全样本上的区间1-out-value筛选
BASIC_NUM = 80
label_name = 'label_v2o10d1'
dp = DataPrepare()

filter_factor = pd.read_excel(filter_factor_fpath, index_col=0)
emotion_factor0927 = pd.read_excel('/data/group/800463/sunss/for_xly/saturn/V6_20220927/V6_20220927_3period/factor_bank_inf_all_931_emotion.xlsx', index_col=0)
emotion_factor0927 = emotion_factor0927.query('emotion == 1')   # 49个，旧版本上变成了有13个情绪因子了
emotion_factor = filter_factor.query('corr_selected==1').set_index('factor_name').loc[emotion_factor0927['factor_name'].tolist()].reset_index()
emotion_factor = emotion_factor.loc[emotion_factor['corr_selected'].dropna().index]

other_factor = list(set(filter_factor['factor_name'].tolist()).difference(set(emotion_factor['factor_name'].tolist())))
score_factor = pd.read_excel(factor_score_fpath, index_col=0)
other_factor = score_factor.set_index('factor_name').loc[other_factor]

ranked_other_factor = other_factor.sort_values('区间1-out-value', ascending=False)
basic_other_factor = ranked_other_factor.iloc[:BASIC_NUM].index.tolist()

samples = dp.get_samples()
label_list = samples.filter(regex='label*').columns.tolist()
samples['trade_dt'] = samples.index.get_level_values(0).strftime('%Y%m%d').astype(int)

y = samples[[label_name]]
y = y.drop(np.isnan(y)[label_name][np.isnan(y)[label_name]].index)
samples = samples.reindex(index=y.index)

margin_ic_score = pd.DataFrame(index=emotion_factor['factor_name'].tolist())
for add_factor_name in tqdm(emotion_factor['factor_name'].tolist()):
    ic = calc_ic(basic_other_factor, samples, 20160101, 20181231, 20190101, 20190930, label_name)
    ic2 = calc_ic(basic_other_factor + [add_factor_name], samples, 20160101, 20181231, 20190101, 20190930, label_name)

    margin_ic = np.sqrt(ic2 ** 2 - ic ** 2) if abs(ic2) > abs(ic) else np.nan
    margin_ic_score.loc[add_factor_name, 'ic'] = ic
    margin_ic_score.loc[add_factor_name, 'ic2'] = ic2
    margin_ic_score.loc[add_factor_name, 'margin_ic'] = margin_ic

# 判断是哪一次增加的因子
margin_ic_score.index.name = 'factor_name'
check = pd.merge(margin_ic_score, emotion_factor0927, on='factor_name').sort_values('margin_ic', ascending=False)
filtered_list = check.query('margin_ic > 0')['factor_name'].tolist()
print(f'数量有{len(filtered_list)}个')
FileUtil.save_list2pkl(filtered_list, '/data/user/015614/junkData/', f'out_value_{BASIC_NUM}.pkl')
"""
"""
import pandas as pd
import numpy as np
from Zeus.Saturn.v3_0_34.path_conf import filter_factor_fpath, factor_score_fpath
from sklearn.linear_model import LinearRegression
from Zeus.Saturn.v3_0_34.DataPrepare import DataPrepare
from scipy.stats import pearsonr
from tqdm import tqdm

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

BASIC_NUM = 30
# label_name = 'label_v2o10d1'
label_name = 'label_pct_graded'
dp = DataPrepare()

filter_factor = pd.read_excel(filter_factor_fpath, index_col=0)
emotion_factor = filter_factor.query('emotion == 1')

other_factor = list(set(filter_factor['factor_name'].tolist()).difference(set(emotion_factor['factor_name'].tolist())))
other_factor = filter_factor.set_index('factor_name').loc[other_factor]

ranked_other_factor = other_factor.sort_values('count', ascending=False)
basic_other_factor = ranked_other_factor.iloc[:BASIC_NUM].index.tolist()

samples = dp.get_samples()
y = pd.read_pickle('/data/group/800463/sunss/for_xly/saturn/newProfit/p2_profit_931_0.20_0.10_500_1500_pct_graded.pkl')
y = y[['label_pct_graded']]
y.columns = ['label_pct_graded']
y = y.reindex(index=samples.index)
samples = pd.concat([samples, y], axis=1)
label_list = samples.filter(regex='label*').columns.tolist()
samples['trade_dt'] = samples.index.get_level_values(0).strftime('%Y%m%d').astype(int)

y = samples[[label_name]]
y = y.drop(np.isnan(y)[label_name][np.isnan(y)[label_name]].index)
samples = samples.reindex(index=y.index)

margin_ic_score = pd.DataFrame(index=emotion_factor['factor_name'].tolist())
for add_factor_name in tqdm(emotion_factor['factor_name'].tolist()):
    ic = calc_ic(basic_other_factor, samples, 20160101, 20181231, 20190101, 20190930, label_name)
    ic2 = calc_ic(basic_other_factor + [add_factor_name], samples, 20160101, 20181231, 20190101, 20190930, label_name)

    margin_ic = np.sqrt(ic2 ** 2 - ic ** 2) if abs(ic2) > abs(ic) else np.nan
    margin_ic_score.loc[add_factor_name, 'ic'] = ic
    margin_ic_score.loc[add_factor_name, 'ic2'] = ic2
    margin_ic_score.loc[add_factor_name, 'margin_ic'] = margin_ic

# 判断是哪一次增加的因子
emotion_factor0927 = pd.read_excel('/data/group/800463/sunss/for_xly/saturn/V6_20220927/V6_20220927_3period/factor_bank_inf_filter_v1_931_emotion.xlsx', index_col=0)
emotion_factor0927 = emotion_factor0927.query('emotion == 1')
margin_ic_score.index.name = 'factor_name'
check = pd.merge(margin_ic_score, emotion_factor0927, on='factor_name')
"""
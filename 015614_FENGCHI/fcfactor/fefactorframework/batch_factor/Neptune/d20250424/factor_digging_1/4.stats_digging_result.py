# coding: utf-8
# Author：fengchi863
# Date ：2024/3/21 16:49

import os
import pandas as pd
from scipy import stats
from fefactorframework.h5data.IO import IO


def save_dict2xls(data: dict, path=None, filename=None, verbose=True):
    os.makedirs(path, exist_ok=True)
    with pd.ExcelWriter(path + filename) as writer:
        for each in data:
            data[each].to_excel(writer, each)
    if verbose:
        print(f'{filename} has been saved in {path + filename}')

start_date = 20160101
end_date = 20191231
all_factor_fpath = '/data/group/800463/data/projectZZ_public/factor_lib/sft_basic_formal_931_20160101_20191231.h5'
if all_factor_fpath.endswith('.pkl'):
    all_factor_df = pd.read_pickle(all_factor_fpath)
else:
    all_factor_df = IO.read_data([start_date, end_date], alt=all_factor_fpath)

strategy = 'neptune'
d_date = os.getcwd().split('/')[-2]
digging_name = os.getcwd().split('/')[-1]
strategy_name = os.getcwd().split('/')[-3]
root_path = f'/data/user/015614/fefactorframework/{strategy}_{d_date}_{digging_name}/factor_test/neptune/'
factor_value = f'/data/user/015614/fefactorframework/{strategy}_{d_date}_{digging_name}/factor_value/neptune/'
note = 'all'
file_list = os.listdir(root_path)
value_list = os.listdir(factor_value)
batch = 50
start_num = 300
factor_fpath_list = list(filter(lambda x: x.endswith('.pkl'), sorted(file_list)))[start_num:start_num + batch]
factor_value_list = list(filter(lambda x: x.endswith('.h5'), sorted(value_list)))[start_num:start_num + batch]
res_list = []

for pkl in factor_fpath_list:
    bt_columns = ['nan_num', 'same_rate', 'value_diff_score', 'value_stability_score', 'mixed_diff_score',
                  'mixed_stability_score', 'score', 'corr_tot', 'high_corr_factor', 'high_corr_factor_corr', 'high_corr_s_num']
    res_df = pd.DataFrame(columns=bt_columns)
    factor_name = pkl[:-4]
    pkl_res = pd.read_pickle(root_path + pkl)

    nan_num = pkl_res['factor_information'].loc['Nan|Inf Count', 'Factor Info']
    same_rate = pkl_res['max_same_ratio'].loc['repeated_ratio', 'first']
    value_diff_score = pkl_res['check_score_res'].loc['score', 'value_diff_score']
    value_stability_score = pkl_res['check_score_res'].loc['score', 'value_stability_score']
    mixed_diff_score = pkl_res['check_score_res'].loc['score', 'class_diff_score']
    mixed_stability_score = pkl_res['check_score_res'].loc['score', 'class_stability_score']
    score = pkl_res['check_score_res'].loc['score', 'tot_score']
    corr_tot = pkl_res['corr_sta'].loc['corr_tot', 'value']

    high_corr_s = pkl_res['factor_corr'].query('factor_corr >= 0.685')
    high_corr_s_num = len(pkl_res['factor_corr_summary'])  # 分区间对比的 可为0、1、2
    if len(high_corr_s) == 0:
        high_corr_s = pkl_res['factor_corr'].iloc[:2]
    else:
        high_corr_s = pkl_res['factor_corr'].iloc[:len(high_corr_s) + 2]

    high_corr_factor_list_str = '，'.join(high_corr_s.index.tolist())
    high_corr_factor_corr_list_str = '，'.join(high_corr_s['factor_corr'].map(lambda x: round(x, 4)).map(str).tolist())
    res_df.loc[str(factor_name)] = [nan_num, same_rate, value_diff_score, value_stability_score,
                                    mixed_diff_score, mixed_stability_score, score, corr_tot, high_corr_factor_list_str, high_corr_factor_corr_list_str, high_corr_s_num]
    res_list.append(res_df)

print('开始拼接')
res_df = pd.concat(res_list, axis=0).sort_index()

# factor_df_list = []
# for factor_fpath in factor_fpath_list:
#     if factor_fpath != 'factor.pkl':
#         tmp = pd.read_pickle(root_path + factor_fpath)
#         factor_df_list.append(tmp)
#
# all_factor = pd.concat(factor_df_list, axis=1)

bt_factor_list = list(map(lambda x: x[:-4], factor_fpath_list))
factor_value_list = list(filter(lambda x: x[:-3] in bt_factor_list, factor_value_list))

factor_df_list = []
for factor_fpath in factor_value_list:

    if factor_fpath != 'factor.pkl':
        tmp = pd.read_hdf(factor_value + factor_fpath)
        if tmp.shape[0] != all_factor_df.shape[0]:
            print(f'{factor_fpath}样本长度不匹配')
        tmp = tmp.reindex(index=all_factor_df.index)
        factor_df_list.append(tmp)

#%% 计算和本周已提交因子的相关性
# week_submit_date = 20250314
# week_root_path = f'/data/user/015614/factor/d{week_submit_date}_Neptune/'
# os.makedirs(week_root_path, exist_ok=True)
# week_submit_factor_fpath_list = os.listdir(week_root_path)
# for factor_fpath in week_submit_factor_fpath_list:
#     if factor_fpath.endswith('h5'):
#         tmp = pd.read_hdf(week_root_path + factor_fpath)
#         tmp = tmp.reindex(index=all_factor_df.index)
#         factor_df_list.append(tmp)

has_submit_factors = [

]


for factor_fpath in has_submit_factors:
    tmp = pd.read_hdf(factor_fpath + '.h5')
    # tmp = pd.read_hdf(factor_value + factor_fpath + '.h5')
    if tmp.shape[0] != all_factor_df.shape[0]:
        print(f'{factor_fpath}样本长度不匹配')
    tmp = tmp.reindex(index=all_factor_df.index)
    factor_df_list.append(tmp)

print(f'开始拼接{len(factor_df_list)}个因子')
all_factor = pd.concat(factor_df_list, axis=1)
# all_factor = all_factor.T.drop_duplicates().T
print('拼接完成')

res_df['highest_corr'] = res_df['high_corr_factor_corr'].map(lambda x: float(x.split('，')[0]))
# 计算相关性
corr_res = pd.DataFrame(index=all_factor.columns.tolist(), columns=all_factor.columns.tolist())
for idx1, factor_name1 in enumerate(all_factor.columns.tolist()):
    for idx2, factor_name2 in enumerate(all_factor.columns.tolist()):
        print(f'{idx1}|{idx2}|{len(all_factor.columns.tolist())}')
        if idx1 > idx2:
            corr_res.iloc[idx1, idx2] = stats.spearmanr(all_factor[factor_name1].fillna(0), all_factor[factor_name2].fillna(0))[0]
            corr_res.iloc[idx2, idx1] = corr_res.iloc[idx1, idx2]

# corr_res = all_factor.corr()  # 计算耗时太高，采用分批计算方案

corr_res = corr_res.applymap(abs)
for index in res_df.index:
    self_highest_corr = corr_res.loc[index.replace('/', '%')].sort_values(ascending=False)
    res_df.loc[index, 'self_high_corr'] = ','.join(self_highest_corr[self_highest_corr > 0.685].index.tolist())
    res_df.loc[index, 'self_high_factor'] = ','.join(self_highest_corr[self_highest_corr > 0.685].map(lambda x: str(round(x, 3))).tolist())

# 挑选样本
res_df2 = res_df.copy()
import operator
# res_df2 = res_df2.loc[res_df2['self_high_corr'].apply(lambda x: not operator.contains(x, 'fc'))]
res_df2 = res_df2.sort_values('score', ascending=False).query('score > 12.5 & highest_corr < 0.695 & high_corr_s_num == 0')
res_df2['drop'] = 0
res_df2['commit'] = 0
for factor in has_submit_factors:
    factor_name = factor.split('/')[-1]
    for idx in range(len(res_df2)):
        row = res_df2.iloc[idx]
        name = res_df2.iloc[idx].name
        if factor in row['self_high_factor']:   # TODO: 这里要修改一下
            res_df2.loc[name, 'drop'] = 1
            print('drop成功!!!!!')
while True:
    tmp_res_df = res_df2.query('drop == 0 & commit == 0')

    if len(tmp_res_df) > 0:
        name = tmp_res_df.iloc[0].name
        res_df2.loc[name, 'commit'] = 1
        for idx2 in range(1, len(tmp_res_df)):
            row = tmp_res_df.iloc[idx2]
            name2 = tmp_res_df.iloc[idx2].name
            if name in row['self_high_corr']:
                res_df2.loc[name2, 'drop'] = 1
    else:
        break

output_dict = {'score': res_df,
               'corr': corr_res,
               'filter': res_df2}
save_dict2xls(output_dict, root_path, f'因子寻优结果_{note}.xlsx')

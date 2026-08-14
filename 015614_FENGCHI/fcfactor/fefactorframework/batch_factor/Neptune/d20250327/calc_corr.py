# coding: utf-8
# Author：fengchi863
# Date ：2025/3/27 16:01
import pandas as pd
from fefactorframework.h5data.IO import IO

factor_fpath_list = [
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_2/factor_value/neptune/fc_T1_n20240321_2',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_2/factor_value/neptune/fc_T1_n20240321_5',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_2/factor_value/neptune/fc_T1_n20240321_10',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_2/factor_value/neptune/fc_T1_n20240321_13',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_139',

    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_13',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_14',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_1',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_36',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_26',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_32',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_29',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_25',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_152',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_148',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_15',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_37',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_17',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_19',

    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_60',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_45',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_41',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_39',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_54',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_50',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_52',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_72',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_82',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_84',
    '/data/user/015614/fefactorframework/neptune_d20250403_factor_digging_1/factor_value/neptune/fc_n20250403_95',

    '/data/user/015614/fefactorframework/neptune_d20250410_factor_digging_1/factor_value/neptune/fc_n20250410_132',
    '/data/user/015614/fefactorframework/neptune_d20250410_factor_digging_1/factor_value/neptune/fc_n20250410_106',
    '/data/user/015614/fefactorframework/neptune_d20250410_factor_digging_1/factor_value/neptune/fc_n20250410_128',
    '/data/user/015614/fefactorframework/neptune_d20250410_factor_digging_1/factor_value/neptune/fc_n20250410_109',
    '/data/user/015614/fefactorframework/neptune_d20250410_factor_digging_1/factor_value/neptune/fc_n20250410_125',
    '/data/user/015614/fefactorframework/neptune_d20250410_factor_digging_1/factor_value/neptune/fc_n20250410_123',
    '/data/user/015614/fefactorframework/neptune_d20250410_factor_digging_1/factor_value/neptune/fc_n20250410_14',

    '/data/user/015614/fefactorframework/neptune_d20250410_factor_digging_1/factor_value/neptune/fc_n20250410_189',
    '/data/user/015614/fefactorframework/neptune_d20250410_factor_digging_1/factor_value/neptune/fc_n20250410_17',
    '/data/user/015614/fefactorframework/neptune_d20250410_factor_digging_1/factor_value/neptune/fc_n20250410_15',
]

start_date = 20160101
end_date = 20191231
all_factor_fpath = '/data/group/800463/data/projectZZ_public/factor_lib/sft_basic_formal_931_20160101_20191231.h5'
if all_factor_fpath.endswith('.pkl'):
    all_factor_df = pd.read_pickle(all_factor_fpath)
else:
    all_factor_df = IO.read_data([start_date, end_date], alt=all_factor_fpath)

factors_df = pd.DataFrame()
for factor_fpath in factor_fpath_list:
    tmp = pd.read_hdf(factor_fpath + '.h5').reindex(all_factor_df.index)
    factors_df = pd.concat([factors_df, tmp], axis=1)

corr_res = factors_df.fillna(0).corr()
corr_res = corr_res.applymap(abs)
res_df = pd.DataFrame(index=factors_df.columns)
corr_res = corr_res.replace(1.0, 0)
for index in factors_df.columns:
    self_highest_corr = corr_res.loc[index.replace('/', '%')].sort_values(ascending=False)
    res_df.loc[index, 'self_high_corr'] = ','.join(self_highest_corr[self_highest_corr > 0.685].index.tolist())
    res_df.loc[index, 'self_high_factor'] = ','.join(self_highest_corr[self_highest_corr > 0.685].map(lambda x: str(round(x, 3))).tolist())


# 挑选样本
res_df2 = res_df.copy()

res_df2['drop'] = 0
res_df2['commit'] = 0
# for factor in factors_df.columns:
#     for idx in range(len(res_df2)):
#         row = res_df2.iloc[idx]
#         name = res_df2.iloc[idx].name
#         if factor in row['self_high_corr']:
#             res_df2.loc[name, 'drop'] = 1
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
res_df2.to_excel('/data/user/015614/junkData/res_df2.xlsx')
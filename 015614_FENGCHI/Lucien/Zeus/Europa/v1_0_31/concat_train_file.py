# coding: utf-8
# Author：fengchi863
# Date ：2023/1/19 10:00

import pandas as pd
from Zeus.Europa.v1_0_31.path_conf import *

# 目标文件下的europa_v1是用来上一版的对比，搞错了

origin_file = pd.read_pickle(data_test_fpath_with_label)
future_file = pd.read_pickle('/data/user/015614/junkData/cheat/europa_v1_all_20220518_20220930.pkl')

# origin_file.loc[(pd.to_datetime('2022-5-18'), slice(None)), :]['T_o2pre']
# future_file.loc[(pd.to_datetime('2022-5-18'), slice(None)), :]['T_o2pre']

future_file['datelist'] = future_file.index.get_level_values(0).strftime('%Y%m%d').astype(int)
future_file = future_file.query('datelist >= 20220701')

# future_file中少了这么多因子
len(list(set(origin_file.columns.tolist()).difference(set(future_file.columns.tolist()))))
len(list(set(future_file.columns.tolist()).difference(set(origin_file.columns.tolist()))))

# 拼接起来放到目标路径
res = pd.concat([origin_file[future_file.columns], future_file], axis=0)
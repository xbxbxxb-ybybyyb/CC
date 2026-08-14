# coding: utf-8
# Author：fengchi863
# Date ：2025/4/24 15:57

import pandas as pd
import numpy as np
import pickle

bjs_df = pd.read_excel('/data/group/800463/fengc/for_all/北交所新代码对照表.xlsx', index_col=0)
bjs_dict1 = bjs_df[['旧代码', '新代码']].set_index('旧代码').to_dict()['新代码']

bjs_df['旧代码'] = bjs_df['旧代码'].map(lambda x: str(x) + '.BJ')
bjs_df['新代码'] = bjs_df['新代码'].map(lambda x: str(x) + '.BJ')
bjs_dict2 = bjs_df[['旧代码', '新代码']].set_index('旧代码').to_dict()['新代码']

bjs_dict1.update(bjs_dict2)
print(len(bjs_dict1))

with open('/data/group/800463/fengc/for_all/北交所代码转换字典.pkl', 'wb') as f:
    pickle.dump(bjs_dict1, f)

bjs_dict = pd.read_pickle('/data/group/800463/fengc/for_all/北交所代码转换字典.pkl')

def bjs_old2new(x):
    bjs_dict = pd.read_pickle('/data/group/800463/fengc/for_all/北交所代码转换字典.pkl')
    if x in bjs_dict.keys():
        new = bjs_dict[x]
    else:
        new = x
    return new

bjs_old2new(831010)
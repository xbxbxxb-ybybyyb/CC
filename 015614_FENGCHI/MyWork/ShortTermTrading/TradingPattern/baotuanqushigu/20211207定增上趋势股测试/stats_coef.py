# coding: utf-8
# Author：fengchi863
# Date ：2021/12/13 14:02

import itertools

import pandas as pd, numpy as np

from ShortTermTrading.conf.path_conf import junk_path
import statsmodels.api as sm

root_path = junk_path + 'trend_test/'
summary = pd.read_excel(root_path + 'summary.xlsx', index_col=0)

ma_types = {1: 'ma5>ma10>ma20>ma40>ma60',
            2: 'ma5>ma10>ma20>ma40',
            3: 'close>ma5>ma10>ma20',
            4: 'ma5>ma10>ma20',
            5: 'close>ma5>ma10',
            6: 'ma5>ma10',
            7: 'close>ma5',
            }
ma_types_reverse = dict((value, key) for key, value in  ma_types.items())
summary['type_num'] = summary['均线排列详细类型'].apply(lambda x: ma_types_reverse[x])
# 共五个条件，固定其他四个，最后一个求回归系数，放入列表
five_cond = ['60日均线得分', '120日均线得分', '60日均线距离', '20日内满足ma5<ma20的比例', 'type_num']
cond_enum = {'60日均线得分': [40, 50, 60, 70],
             '120日均线得分': [40, 50, 60, 70],
             '60日均线距离': [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4],
             '20日内满足ma5<ma20的比例': [0.4, 0.45, 0.5, 0.55, 0.6],
             'type_num': [1, 2, 3, 4, 5, 6, 7]
            }

coef_dict = dict()
for tmp_key in list(cond_enum.keys()):
    print(tmp_key)
    other_key = list(set(cond_enum.keys()) - set([tmp_key]))
    all_permutations = itertools.product(*[tuple(cond_enum[x]) for x in other_key])
    tmp_list = list()
    for perm in all_permutations:
        tmp_df = summary[(summary[other_key[0]] == perm[0]) &
                         (summary[other_key[1]] == perm[1]) &
                         (summary[other_key[2]] == perm[2]) &
                         (summary[other_key[3]] == perm[3])]
        tmp_df = tmp_df.sort_values([tmp_key])
        est = sm.OLS(tmp_df['日均趋势个股数量'].values, tmp_df[tmp_key]).fit()
        tmp_list.append(est.params[0])
    coef_dict[tmp_key] = np.mean(tmp_list)

print(coef_dict)
check = pd.DataFrame(coef_dict, index=['coef']).T

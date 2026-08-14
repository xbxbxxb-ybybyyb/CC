# coding: utf-8
# Author：fengchi863
# Date ：2021/7/19 11:09

'''
统计板块交叉数量
'''

from FaaMonitor.conf.path_conf import ths_path
from ShortTermTrading.conf.path_conf import junk_path
import pandas as pd
'''
ths_dict = pd.read_json(ths_path + '概念板块同花顺20210719.json', typ='dict')
res = pd.DataFrame(index=list(ths_dict.keys()), columns=list(ths_dict.keys()))
cnt = 0
col_list = list()
for col in res.columns:
    for idx in res.index:
        if idx in col_list:
            continue
        tmp1 = list(ths_dict[col].keys())
        tmp2 = list(ths_dict[idx].keys())
        tmp_len = len(set(tmp1) & set(tmp2))
        res.loc[idx, col] = tmp_len
        res.loc[col, idx] = tmp_len
        print(idx, col, tmp_len, cnt)
        cnt += 1
        col_list.append(col)
print(1)
res.to_excel(junk_path + 'ths_intersection.xlsx')

col_name = dict()
for key in res.columns:
    col_name.update({key: key+'('+str(res.loc[key, key]) +')'})

res = res.rename(columns=col_name)
res = res.rename(index=col_name)

res.to_excel(junk_path + 'ths_intersection.xlsx', sheet_name='板块交叉数量')
'''
res = pd.read_excel(junk_path + 'ths_intersection1.xlsx', index_col=0)
print(1)

col = res.columns.tolist()
def contain_strs(x, strs):
    for str in strs:
        if str in x[:x.find('(')]:
            return True
    return False

del_concept = ['融资融券','标普','深股通','半年报预增','沪股通','MSCI','新股与次新股','央企', '次新股', '创投', '参股']
del_col = list(filter(lambda x: contain_strs(x, del_concept), col))
res = res.drop(del_col, axis=1)
res = res.drop(del_col, axis=0)

res2 = res.copy()
for idx1 in range(res2.shape[0]):
    for idx2 in range(res2.shape[0]):
        print(idx1, idx2)
        if idx1 >= idx2:
            res2.iloc[idx1, idx2] = None

df2 = res2.stack(dropna=True)
df2 = df2.sort_values(ascending=False)
df2 = df2.reset_index()
df2.columns = ['主题1', '主题2', '交叉数量']
df2.to_excel(junk_path + 'ths_intersection1.xlsx')
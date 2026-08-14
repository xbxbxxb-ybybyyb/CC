# coding: utf-8
# Author：fengchi863
# Date ：2024/5/15 19:26

import pandas as pd
import os
path_user = '/data/user/015614/daily/灰名单生成/黑名单/'
file_paths = os.listdir(path_user)
file_paths = list(filter(lambda x: 'whiter_list_check' in x, file_paths))
file_paths.sort()

date_list = list(map(lambda x: x[-13:-5], file_paths))
leak_df = pd.DataFrame(index=date_list, columns=['leak_list', 'add', 'remove'])
old_not_white = []
for fpath in file_paths:
    tmp = pd.read_excel(path_user + fpath)
    cur_list = tmp['STOCK_NAME'].tolist()

    add = list(set(cur_list).difference(set(old_not_white)))
    remove = list(set(old_not_white).difference(set(cur_list)))
    leak_df.loc[fpath[-13:-5], 'leak_list'] = cur_list
    leak_df.loc[fpath[-13:-5], 'add'] = add
    leak_df.loc[fpath[-13:-5], 'remove'] = remove

    old_not_white = tmp['STOCK_NAME'].tolist()
from dataApi.sendInfo import send_file
send_file(leak_df)
# coding: utf-8
# Author：fengchi863
# Date ：2023/2/1 13:48

import pandas as pd
import numpy as np
from dataApi.tradeDate import get_date_range
from dataApi.stockList import trans_windcode2int as W2Int
from tqdm import tqdm

black_path = '/data/group/800463/stock_list/abnormal_notice_list/'
junk_path = '/data/user/015614/junkData/'
date_list = get_date_range(20220101, 20230131)
origin_count = pd.DataFrame(index=date_list, columns=['origin', 'param3', 'param4', 'param5', 'param6', 'param7'])

for dat in date_list:
    cur_black = pd.read_excel(black_path + f'abnormal_notice_list_{dat}.xlsx')
    param3 = pd.read_excel(junk_path + f'参数组合3/{dat}.xlsx')
    param4 = pd.read_excel(junk_path + f'参数组合4/{dat}.xlsx')
    origin_count.loc[dat, 'origin'] = len(cur_black)
    origin_count.loc[dat, 'param3'] = len(param3)
    origin_count.loc[dat, 'param4'] = len(param4)

set1 = set(param3['证券代码'].tolist())
set2 = set(cur_black['证券代码'].tolist())
list(set1.difference(set2))
from dataApi.sendInfo import send_file
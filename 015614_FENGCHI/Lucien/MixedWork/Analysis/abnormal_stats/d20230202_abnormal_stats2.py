# coding: utf-8
# Author：fengchi863
# Date ：2023/2/2 10:37

import pandas as pd
import numpy as np
from dataApi.tradeDate import get_date_range
from dataApi.stockList import trans_windcode2int as W2Int
from tqdm import tqdm

black_path = '/data/group/800463/stock_list/abnormal_notice_list/'
junk_path = '/data/user/015614/junkData/'
date_list = get_date_range(20220101, 20230131)
count_df = pd.DataFrame(index=date_list, columns=['origin', 'param3', 'param4', 'param5', 'param6'])

for dat in date_list:
    cur_black = pd.read_excel(black_path + f'abnormal_notice_list_{dat}.xlsx')
    # cur_black_out2 = pd.read_excel(black_path + f'abnormal_notice_list_{dat}.xlsx', sheet_name='备选检查')
    # cur_black_out2 = cur_black_out2.query('ycbd_20 + jyfxts_20 >= 1 & ycbd_10 + jyfxts_10 >= 1')
    cur_black['异常波动公告数'] = cur_black['异常波动公告数'].fillna(99)
    cur_black['风险提示公告数'] = cur_black['风险提示公告数'].fillna(99)

    count_df.loc[dat, 'origin'] = len(cur_black)
    count_df.loc[dat, 'param3'] = cur_black.query('异常波动公告数 + 风险提示公告数 >= 2').shape[0]
    count_df.loc[dat, 'param4'] = cur_black.query('异常波动公告数 + 风险提示公告数 >= 3').shape[0]
    count_df.loc[dat, 'param5'] = cur_black.query('异常波动公告数 + 风险提示公告数 >= 4').shape[0]
    count_df.loc[dat, 'param6'] = cur_black.query('异常波动公告数 >= 1 & 风险提示公告数 >= 1').shape[0]

from dataApi.sendInfo import send_file
send_file(count_df)

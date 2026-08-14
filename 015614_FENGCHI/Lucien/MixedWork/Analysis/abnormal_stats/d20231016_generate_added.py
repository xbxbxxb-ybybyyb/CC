# coding: utf-8
# Author：fengchi863
# Date ：2023/10/16 15:59

from dataApi import tradeDate
import pandas as pd
import numpy as np
from itertools import product
import time
from tqdm import tqdm

v1_path = '/data/user/015614/daily/灰名单生成/异常波动历史测试V20240817/'
v2_path = '/data/user/015614/daily/灰名单生成/异常波动历史测试V20240817_old/'

from dataApi import tradeDate, stockList

# date_list = tradeDate.get_date_range(20220101, 20230921)
# date_list = tradeDate.get_date_range(20200701, 20211231)
date_list = tradeDate.get_date_range(20230101, 20240820)
res = pd.DataFrame(index=date_list)

for dat in tqdm(date_list):
    # v1 = pd.read_excel(v1_path + f'abnormal_notice_list_{dat}.xlsx')
    v1 = pd.read_excel(v1_path + f'abnormal_notice_list_{dat}.xlsx')
    v2 = pd.read_excel(v2_path + f'abnormal_notice_list_{dat}.xlsx')

    v1_stk_list = v1['证券代码'].map(stockList.trans_windcode2int).tolist()
    v2_stk_list = v2['证券代码'].map(stockList.trans_windcode2int).tolist()

    diff1 = list(set(v1_stk_list).difference(set(v2_stk_list)))
    diff2 = list(set(v2_stk_list).difference(set(v1_stk_list)))

    res.loc[dat, 'v1_num'] = len(v1)
    res.loc[dat, 'v2_num'] = len(v2)
    res.loc[dat, 'not_in_v1_num'] = len(diff1)
    res.loc[dat, 'not_in_v2_num'] = len(diff2)
    res.loc[dat, 'not_in_v1'] = ','.join(list(map(lambda x: str(x), diff1)))
    res.loc[dat, 'not_in_v2'] = ','.join(list(map(lambda x: str(x), diff2)))

from dataApi.sendInfo import send_file
send_file(res, tmp_name='20230101-20240820_异常波动版本差异(v1为原版本)_v2.xlxs')
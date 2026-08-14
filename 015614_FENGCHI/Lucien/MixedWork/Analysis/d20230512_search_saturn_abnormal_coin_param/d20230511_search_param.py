# coding: utf-8
# Author：fengchi863
# Date ：2023/5/11 13:06
"""
这是去除st、去除开盘涨跌停、去除上市断版天数<=10，去除931前涨停，去除pattern为1和2的样本，也就是研究段的样本集合
如果涉及实盘，实盘会有是否有持仓，黑名单，白名单的筛选，问谢璐遥
"""
from dataApi import tradeDate
import pandas as pd
import numpy as np
from itertools import product
import time
from tqdm import tqdm

saturn_fpath = '/data/user/018107/share_file/for_fc/saturn_sample_20220101_20221231.pkl'
saturn = pd.read_pickle(saturn_fpath)

path_user = '/data/user/015614/JunkWorkList/灰名单生成/异常波动测试/'
date_list = tradeDate.get_date_range(20220101, 20221231)

paramA = list(np.arange(150, 200, 10) / 100)
paramB = list(np.arange(30, 41, 1) / 100)
paramC = [1, 2]
paramD = [1, 2]
param_list = [paramA, paramB, paramC, paramD]
param_product_list = list(product(*param_list))

save_df = pd.DataFrame(index=param_product_list, columns=['交集数量', 'grey数量', 'Saturn数量'])
for param_tuple in tqdm(param_product_list):
    t1 = time.time()
    coin_num = 0
    grey_num = 0
    saturn_num = 0
    paramA, paramB, paramC, paramD = param_tuple
    print(param_tuple)
    for dat in date_list:
        grey_df = pd.read_excel(path_user + f'abnormal_notice_{dat}.xlsx')
        # grey_stk_df = grey_df.loc[((grey_df['40日涨跌幅'] >= 1.5) & (grey_df['ycbd_20'] + grey_df['jyfxts_20'] >= 1)) | \
        #                         ((grey_df['10日最大涨跌幅'] >= 0.3) & (grey_df['ycbd_10'] + grey_df['jyfxts_10'] >= 1))]
        grey_stk_df = grey_df.loc[((grey_df['40日涨跌幅'] >= paramA) & (grey_df['ycbd_20'] + grey_df['jyfxts_20'] >= paramC)) | \
                                  ((grey_df['10日最大涨跌幅'] >= paramB) & (grey_df['ycbd_10'] + grey_df['jyfxts_10'] >= paramD))]
        grey_stk_list = grey_stk_df['Ticker'].tolist()
        # print(len(grey_stk_list))
        today_saturn_list = saturn.loc[pd.to_datetime(str(dat))].index.tolist()
        today_coin_list = list(set(grey_stk_list).intersection(set(today_saturn_list)))
        grey_num += len(grey_stk_list)
        saturn_num += len(today_saturn_list)
        coin_num += len(today_coin_list)
        # print(len(today_coin_list))
    print(param_tuple, coin_num)
    save_df.loc[param_tuple, '交集数量'] = coin_num
    save_df.loc[param_tuple, 'grey数量'] = grey_num
    save_df.loc[param_tuple, 'Saturn数量'] = saturn_num
    print('耗时:', time.time() - t1)

save_df.to_excel('/data/user/015614/junkData/Saturn与异常波动交集.xlsx')
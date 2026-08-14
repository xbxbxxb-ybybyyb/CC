# coding: utf-8
# Author：fengchi863
# Date ：2023/9/22 15:26

from dataApi import tradeDate
import pandas as pd
import numpy as np
from itertools import product
import time
from tqdm import tqdm

# saturn_fpath = '/data/user/018107/share_file/for_fc/saturn_sample_20220101_20230921.pkl'
# saturn_fpath = '/data/user/018107/share_file/for_fc/saturn_sample_20230101_20230921.pkl'
# saturn = pd.read_pickle(saturn_fpath)

path_user = '/data/user/015614/JunkWorkList/灰名单生成/异常波动测试/'
# date_list = tradeDate.get_date_range(20220101, 20221231)
# date_list = tradeDate.get_date_range(20220101, 20230921)
# date_list = tradeDate.get_date_range(20230922, 20231009)
date_list = tradeDate.get_date_range(20230101, 20240820)

# date_list = tradeDate.get_date_range(20200701, 20211231)
# NOTE：要求对创业板的涨跌幅限制50%
paramA, paramB, paramC, paramD, paramE, paramF = 1.5, 0.3, 2, 2, 1, 1

for dat in tqdm(date_list):
    grey_df = pd.read_excel(path_user + f'abnormal_notice_{dat}.xlsx')
    # grey_stk_df = grey_df.loc[((grey_df['40日涨跌幅'] >= 1.5) & (grey_df['ycbd_20'] + grey_df['jyfxts_20'] >= 1)) | \
    #                         ((grey_df['10日最大涨跌幅'] >= 0.3) & (grey_df['ycbd_10'] + grey_df['jyfxts_10'] >= 1))]
    grey_df['flag'] = (((grey_df['40日涨跌幅'] >= paramA) & ((grey_df['ycbd_20'] >= paramC) | (grey_df['jyfxts_20'] >= paramE))) | \
                    ((grey_df['10日最大涨跌幅'] >= paramB) & ((grey_df['ycbd_10'] >= paramD) | (grey_df['jyfxts_10'] >= paramF)))) & (~grey_df['Ticker'].map(lambda x: (x.startswith('3') or x.startswith('68'))))
    grey_df['flag2'] = (((grey_df['40日涨跌幅'] >= paramA) & ((grey_df['ycbd_20'] >= paramC) | (grey_df['jyfxts_20'] >= paramE))) | \
                   ((grey_df['10日最大涨跌幅'] >= 0.5) & ((grey_df['ycbd_10'] >= paramD) | (grey_df['jyfxts_10'] >= paramF)))) & (grey_df['Ticker'].map(lambda x: (x.startswith('3') or x.startswith('68'))))
    grey_df['flag'] = grey_df['flag'] | grey_df['flag2']
    grey_stk_df = grey_df[grey_df['flag'] == 1]
    grey_stk_list = grey_stk_df['Ticker'].tolist()
    # print(len(grey_stk_list))
    # today_saturn_list = saturn.loc[pd.to_datetime(str(dat))].index.tolist()
    # today_coin_list = list(set(grey_stk_list).intersection(set(today_saturn_list)))

    df = pd.DataFrame(sorted(grey_stk_list), columns=['证券代码'])
    # df.to_excel(f'/data/user/015614/shared/for_wys/d20230922_2022年新参数下异常波动个股每日列表/{dat}.xlsx')
    # df.to_excel(f'/data/user/015614/junkData/d20240821_2023-2024年新参数下异常波动个股每日列表/{dat}.xlsx')
    df.to_excel(f'/data/user/015614/junkData/d20240821_2023-2024年新参数下异常波动个股每日列表V2/{dat}.xlsx')
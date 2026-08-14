# coding: utf-8
# Author：fengchi863
# Date ：2023/5/12 22:49

from dataApi import tradeDate
import pandas as pd
import numpy as np
from itertools import product
import time
from tqdm import tqdm

# saturn_fpath = '/data/user/018107/share_file/for_fc/saturn_sample_20220101_20221231.pkl'
saturn_fpath = '/data/user/018107/share_file/for_fc/saturn_sample_20230101_20230625.pkl'
saturn = pd.read_pickle(saturn_fpath)

path_user = '/data/user/015614/JunkWorkList/灰名单生成/异常波动测试/'
# date_list = tradeDate.get_date_range(20220101, 20221231)
date_list = tradeDate.get_date_range(20230101, 20230625)

paramA = list(np.arange(150, 200, 10) / 100)
paramB = list(np.arange(30, 41, 1) / 100)
paramC = [1, 2]
paramD = [1, 2]
param_list = [paramA, paramB, paramC, paramD]
param_product_list = list(product(*param_list))

save_df = pd.DataFrame(index=param_product_list, columns=['交集数量', 'grey数量', 'Saturn数量'])

paramA, paramB, paramC, paramD = 1.5, 0.3, 1, 2

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

    df = pd.DataFrame(sorted(grey_stk_list), columns=['证券代码'])
    df.to_excel(f'/data/user/015614/shared/for_wys/d20230512_2022年新参数下异常波动个股每日列表/{dat}.xlsx')
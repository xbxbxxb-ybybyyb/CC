# coding: utf-8
# Author：fengchi863
# Date ：2022/4/19 14:02

"""
脚本，用于观察输出的对冲情况
"""

import pandas as pd
from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import *
from SimiStock.dataApi import getData, tradeDate, indName
from FaaMonitor.Util.MyUtil import MyUtil

#%% 用来测试前后文件的初始对冲序列是否一致

# filename1 = '滚动_7_(8, 10)_(120, 5)_v3_95_20180101_20200630_result.pkl'
# filename2 = '叠加风格5_14_(8, 10)_v3_95_20180101_20200630_result.pkl'
# check1 = pd.read_pickle(hedge_path + filename1)
# check2 = pd.read_pickle(hedge_path + filename2)
# for idx in range(20):
#     tmp1 = check1[idx]['hedge_list'][0]['hedge_list']
#     tmp2 = check2[idx]['hedge_list']
#     assert tmp1 == tmp2[:len(tmp1)]

#%% 用来检测数据一致性，检测基础数据
filename1 = '2nd叠加K线相似度2_7_(0.6, 1)_(0.7, 1)_(120, 120)_95_20170101_20201231_result.pkl'
filename2 = '2nd叠加K线相似度3_7_(0.6, 1)_(0.7, 1)_(120, 120)_95_20170101_20201231_result.pkl'
check1 = pd.read_pickle(hedge_path + filename1)
check2 = pd.read_pickle(hedge_path + filename2)
for idx in range(3000):
    tmp1 = check1[idx]['stk_id']
    trade_date = check1[idx]['date']
    has = False
    for idx in range(len(check2)):
        tmp2 = check2[idx]['stk_id']
        if tmp2 == tmp1:
            has = True
            break
    if has is False:
        print(tmp1, trade_date)
        # break
    # if tmp1 != tmp2:
    #     print(tmp1, tmp2)
#%% 存进文件
start_date = 20220520
filename1 = f'新版本_7_(0.8, 1)_(0.8, 1)_(120, 120)_95_{start_date}_{start_date}_part1_result.pkl'
filename2 = f'新版本_7_(0.6, 1)_(0.8, 1)_(120, 120)_95_{start_date}_{start_date}_part2_result.pkl'
filename3 = f'新版本_7_(0.6, 1)_(0.7, 0.8)_(120, 120)_95_{start_date}_{start_date}_part3_result.pkl'
# filename4 = f'新版本_7_(0.5, 1)_(0.5, 1)_(120, 120)_95_{start_date}_{start_date}_part4_result.pkl'
check1 = pd.read_pickle(hedge_path + filename1)
check2 = pd.read_pickle(hedge_path + filename2)
check3 = pd.read_pickle(hedge_path + filename3)
# check4 = pd.read_pickle(hedge_path + filename4)
print(len(check1), len(check2), len(check3))
# print(len(check1), len(check2), len(check3), len(check4))
ret_dict = dict()
for idx in range(len(check1)):
    tmp1 = check1[idx]['hedge_list'][0]['hedge_list']
    block_stk = MyUtil.get_1stock_name(check1[idx]['stk_id'])
    hedge_list = list(map(lambda x: MyUtil.get_1stock_name(x), tmp1))
    ret_dict[block_stk] = '，'.join(hedge_list)
    print(check1[idx]['stk_id'])
    print(tmp1)
ret_df = pd.Series(ret_dict)
ret_df.to_excel(hedge_path + '大宗交易预备池.xlsx')

filename4 = '新版本_7_(0.6, 1)_(0.7, 0.8)_(120, 120)_95_20220422_20220422_part3_result.pkl'
check4 = pd.read_pickle(hedge_path + filename4)
for idx in range(len(check4)):
    if check3[idx] not in check4:
        print(check3[idx])

# %% 检查数量
# filename1 = 'Corr版本_SW1_7_(0.5, 1)_(0.5, 1)_(120, 120)_95_20210101_20211231_result.pkl'
filename1 = 'Corr版本_SW1_7_(0.5, 1)_(0.5, 1)_(120, 120)_95_20170101_20201231_result.pkl'
check1 = pd.read_pickle(txTest_path + filename1)
print(len(check1))
count = 0
for _check in check1:
    if _check['hedge_list'][0]['start_date'] // 10000 == 2017:
        count += 1
print(count)


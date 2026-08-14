# coding: utf-8
# Author：fengchi863
# Date ：2023/1/18 19:23

import sys
sys.path.append('/data/user/015614/Lucien')

import os

import numpy as np
import pandas as pd
from xquant.factordata import FactorData
from MixedWork.GreyStockGenerator import IO
from dataApi.stockList import trans_int2windcode as Int2Wc
from dataApi.tradeDate import get_date_range

s = FactorData()
import datetime as dt
import time

path_user = '/data/user/015614/shared/sss_shared/sss_black_list/'
path_group = '/data/group/800463/stock_list/'
path_hold = '/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/'

date_list = get_date_range(20220101, 20220123)
for dat in date_list:
    # date = dt.datetime.now().strftime('%Y%m%d')
    date = str(dat)
    lastdate = s.tradingday(date, -2)[0]

    def int_2_stock_code(number):
        str_number = str(int(number))
        if number < 99999:
            while len(str_number) < 6:
                str_number = '0' + str_number
        if str_number[0] == '6':
            str_number = str_number + '.SH'
        else:
            str_number = str_number + '.SZ'
        return str_number


    pre_st_file = path_group + 'pre_st_list/pre_st_list_%s.xlsx' % lastdate
    defer_reply_file = path_group + 'defer_reply_list/defer_reply_list_%s.xlsx' % lastdate
    after_dt_file = path_group + 'after_dt_list/after_dt_list_%s.xlsx' % lastdate
    abnormal_file = path_group + 'abnormal_notice_list/abnormal_notice_list_%s.xlsx' % date
    manual_file = path_group + 'black_other_list/手动调整黑名单.xlsx'
    saturn_file = path_hold + 'saturn成交记录-%s.xlsx' % lastdate
    jupiter_file = path_hold + 'jupiter成交记录-%s.xlsx' % lastdate
    ceres_file = path_hold + 'ceres成交记录-%s.xlsx' % lastdate
    Europa_file = path_hold + 'Europa成交记录-%s.xlsx' % lastdate

    while not os.path.exists(pre_st_file):
        print('等待pre_st黑名单中')
        time.sleep(30)
    while not os.path.exists(defer_reply_file):
        print('等待defer_reply黑名单中')
        time.sleep(30)
    while not os.path.exists(after_dt_file):
        print('等待after_dt黑名单中')
        time.sleep(30)
    while not os.path.exists(abnormal_file):
        print('等待异常波动黑名单中')
        time.sleep(30)
    while not os.path.exists(saturn_file):
        print('等待saturn成交记录中')
        time.sleep(30)
    while not os.path.exists(jupiter_file):
        print('等待jupiter成交记录中')
        time.sleep(30)
    while not os.path.exists(ceres_file):
        print('等待ceres成交记录中')
        time.sleep(30)

    # pre_st
    pre_st_list = pd.read_excel(pre_st_file)
    # defer_reply
    defer_reply_list = pd.read_excel(defer_reply_file)
    # after_dt
    after_dt_list = pd.read_excel(after_dt_file)
    # abnormal_notice
    abnormal_list = pd.read_excel(abnormal_file)
    # manual
    manual_list = pd.read_excel(manual_file)
    manual_list['出池时间'] = manual_list['出池时间'].apply(lambda x: int(x.strftime('%Y%m%d')) if type(x) != pd._libs.tslibs.nattype.NaTType else np.nan)
    manual_list['入池时间'] = manual_list['入池时间'].apply(lambda x: int(x.strftime('%Y%m%d')) if type(x) != pd._libs.tslibs.nattype.NaTType else np.nan)
    manual_list['出池时间'] = manual_list['出池时间'].fillna(20990101)
    manual_list = manual_list[(manual_list['入池时间'] < dat) & (manual_list['出池时间'] > dat)]
    # 合并股票列表
    joined_black_list = []
    for stock_excel in [pre_st_list, defer_reply_list, after_dt_list, abnormal_list, manual_list]:
        if len(stock_excel) != 0:
            joined_black_list = joined_black_list + list(stock_excel['证券代码'].apply(int_2_stock_code))
    joined_black_list = list(set(joined_black_list))

    # 读取名称数据
    black = pd.DataFrame()
    black['股票代码'] = joined_black_list
    name_data = IO.read_data([lastdate, lastdate], alt='/data/group/800080/warehouse/prod/FCD/CHINA_STOCK/DAILY/SUNTIME/FCD_CHINA_STOCK_DAILY_SUNTIME.h5')
    for index, row in black.iterrows():
        if (lastdate, row['股票代码']) in name_data.index:
            black.loc[index, '证券名称'] = name_data.loc[lastdate, row['股票代码']]['STOCK_NAME'].values[0]
        else:
            black.loc[index, '证券名称'] = str(np.nan)

    # 筛选每日新增黑名单
    last_black_list = pd.read_excel(path_user + 'black_list_%s.xlsx' % lastdate, sheet_name='黑名单')
    last_black_list['股票代码'] = last_black_list['股票代码'].apply(int_2_stock_code)
    last_black_list['lastdate'] = 1
    black_list = pd.merge(black, last_black_list[['股票代码', 'lastdate']], how='left', on='股票代码')
    black_list['lastdate'] = black_list['lastdate'].fillna(0)
    for index, row in black_list.iterrows():
        if row['lastdate'] == 0:
            black_type = ''
            if row['股票代码'] in list(pre_st_list['证券代码'].apply(int_2_stock_code)):
                black_type += 'pre_ST；'
            if row['股票代码'] in list(defer_reply_list['证券代码'].apply(int_2_stock_code)):
                black_type += '延期回复；'
            if row['股票代码'] in list(after_dt_list['证券代码'].apply(int_2_stock_code)):
                black_type += '一字跌停；'
            if row['股票代码'] in list(abnormal_list['证券代码'].apply(int_2_stock_code)):
                black_type += '异常波动；'
            if row['股票代码'] in list(manual_list['证券代码'].apply(int_2_stock_code)):
                black_type += '手动调整；'
            black_list.loc[index, '类别'] = black_type
    black_list = black_list.sort_values(['lastdate', '类别', '股票代码'])
    black_list = black_list[['股票代码', '证券名称', 'lastdate', '类别']]
    black_list['股票代码'] = black_list['股票代码'].apply(lambda x: x[:~2])


    def excel_saver(output_dict, excel_name, index):
        writer = pd.ExcelWriter(excel_name, engine='xlsxwriter')
        for key in output_dict:
            output_dict[key].to_excel(writer, sheet_name=key, index=index)
        writer.save()


    black_list_nost = black_list[black_list['证券名称'].apply(lambda x: 'ST' not in x and '退' not in x and 'nan' not in x)]
    excel_saver({'黑名单(不包括ST)': black_list_nost, '黑名单': black_list},
                path_user + 'black_list_%s.xlsx' % date, index=False)
# coding: utf-8
# Author：fengchi863
# Date ：2020/8/26 10:49

import pandas as pd
from tqdm import tqdm
from BullClient.RecordDataSet.RecordDataSet import RecordDataSet
from StrongStockModel.dataApi.getData import get_daily_1factor, get_date_range

date_list = get_date_range(20140401, 20151231)
rds = RecordDataSet()
deliver = rds.get_clean_deliver_data()

close = get_daily_1factor('close', date_list=date_list)
deliver['当日收盘价'] = deliver[['委托日期', '证券代码']]. \
    apply(lambda x: close.loc[x['委托日期'], x['证券代码']], axis=1)
pre_close = get_daily_1factor('pre_close', date_list=date_list)
deliver['前收盘价'] = deliver[['委托日期', '证券代码']]. \
    apply(lambda x: pre_close.loc[x['委托日期'], x['证券代码']], axis=1)
mkt_cap = get_daily_1factor('a_mkt_cap', date_list=date_list)
deliver['当日市值'] = deliver[['委托日期', '证券代码']]. \
    apply(lambda x: mkt_cap.loc[x['委托日期'], x['证券代码']], axis=1) / 1e8

# 筛选出第一次买入的部分
deliver = deliver[deliver['成交数量'] == deliver['剩余股数']]

# TODO:此处画图

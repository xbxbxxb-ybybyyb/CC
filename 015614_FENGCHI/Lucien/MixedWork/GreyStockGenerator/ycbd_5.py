# coding: utf-8
# Author：fengchi863
# Date ：2022/8/18 16:23

import sys
import os
sys.path.append('/data/user/015614/Lucien')
import numpy as np
import pandas as pd
import datetime as dt
from xquant.factordata import FactorData
from MixedWork.GreyStockGenerator import IO
from dataApi.sendInfo import send_message
from dataApi import stockList
import time
import datetime as dt

def fun_append_next_tradingday(factor_df):
    # 实盘中需要在T日开盘之前取到T-1日的因子，为了shift之后能有T日的时间戳，所以先把T日的时间戳加上去，取历史数据则没有该问题
    factor_df_unstack = factor_df.unstack()
    last_timestamp = factor_df_unstack.index[-1]
    next_tradingday_timestamp = pd.Timestamp(s.tradingday(last_timestamp.strftime('%Y%m%d'), 2)[-1])
    next_tradingday_df = pd.DataFrame(np.zeros((1, factor_df_unstack.shape[1])), columns=factor_df_unstack.columns,
                                      index=[next_tradingday_timestamp])
    factor_df = (factor_df_unstack.append(next_tradingday_df)).stack()
    factor_df.index.names = ['dt', 'Ticker']
    return factor_df

s = FactorData()

def excel_saver(output_dict, excel_name, index):
    writer = pd.ExcelWriter(excel_name, engine='xlsxwriter')
    for key in output_dict:
        output_dict[key].to_excel(writer, sheet_name=key, index=index)
    writer.save()
    return

path_user = '/data/user/015614/daily/灰名单生成/黑名单/'
path_group = '/data/group/800463/stock_list/'

import sys
if len(sys.argv) < 2:
    nowdate = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), 1)[0]
    # nowdate = '20241009'
else:
    nowdate = sys.argv[1]

# nowdate = '20240821'
nextdate = nowdate
date = s.tradingday(nextdate, -2)[0]
lastdate = s.tradingday(date, -2)[0]
year = lastdate[:4]  # 当前年度
last_year = str(int(year) - 1)  # 上一年度
last_year_period = last_year + '0101'  # 上一年开始的日期

f_data = IO.read_data([s.tradingday(date, -50)[0], date], columns=['close', 'adjfactor'],
                      alt='/data/group/800080/warehouse_event/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
close_adj = f_data['close'] * f_data['adjfactor']
all_sample = list(f_data['close'].unstack().columns)

# 新闻文本
from xquant.textdata import NewsData

nd = NewsData()
ycbd_tot = pd.DataFrame(columns=['dt', 'Ticker', 'ORIGINALCODE', 'ycbd_indicator']).set_index(['dt', 'Ticker'])
for stock in all_sample:
    print(stock)
    data_info = nd.getAnnouncement([stock], str(last_year_period), str(nowdate))   # 采用最新的接口后，原本20240730 68只->57只
    if len(data_info) == 0:
        continue

    data_info = data_info.rename(columns={'PUBDATE': 'dt'})
    data_info['Ticker'] = stock
    data_info = data_info.reset_index().set_index(['dt', 'Ticker']).sort_index()
    data_info = data_info[data_info['TEXTTITLE'].apply(lambda x: x != None)]

    if len(data_info) != 0:
        data_info = data_info.loc[pd.Timestamp(s.tradingday(date, -30)[0]):, ]
        ycbd_warning = data_info[['ORIGINALCODE', 'TEXTTITLE']][
            data_info['TEXTTITLE'].apply(lambda x: (('异常波动' in x) | ('异动' in x)) & ('回复' not in x) & \
                                                   ('回复函' not in x) & ('复函' not in x) & \
                                                   ('回函' not in x) & ('补充' not in x) & ('说明' not in x) & ('海外' not in x))]
        ycbd_warning['ycbd_indicator'] = 1

        if len(ycbd_warning) != 0:
            ycbd_tot = pd.concat([ycbd_tot, ycbd_warning[['ORIGINALCODE', 'ycbd_indicator']]])
ycbd_tot = ycbd_tot.reset_index()
ycbd_tot['dt_old'] = ycbd_tot['dt']
ycbd_tot['dt'] = ycbd_tot['dt'].apply(lambda x: pd.Timestamp(s.tradingday(x.strftime('%Y%m%d'), 1)[0]))
ycbd_tot = ycbd_tot.set_index(['dt', 'Ticker']).sort_index()
ycbd_tot = ycbd_tot.loc[~ycbd_tot.index.duplicated(keep='first')].sort_index()

all_index = fun_append_next_tradingday(f_data).index
ycbd_5 = ycbd_tot['ycbd_indicator'].reindex(all_index).unstack().fillna(0).rolling(6, 6).sum().stack()

joined_condition = ycbd_5 >= 1

joined_condition_notice_date = pd.DataFrame(joined_condition).copy()
joined_condition_notice_date['dt_dummy'] = joined_condition.reset_index()['dt'].values

joined_condition_5_days = joined_condition.astype(float).unstack().fillna(0).rolling(1, 1).sum()
joined_condition_5_days_fulfilled = (joined_condition_5_days >= 1).stack().loc[nextdate]

joined_condition_5_days_fulfilled = pd.DataFrame(joined_condition_5_days_fulfilled[joined_condition_5_days_fulfilled],
                                                 columns=['banned_indicator'])
joined_condition_5_days_fulfilled['异常波动公告数'] = ycbd_5.reindex(joined_condition_5_days_fulfilled.index).fillna(0)

joined_condition_5_days_fulfilled['证券名称'] = np.nan
f_data1 = IO.read_data([lastdate, lastdate], alt='/data/group/800080/warehouse/prod/FCD/CHINA_STOCK/DAILY/SUNTIME/FCD_CHINA_STOCK_DAILY_SUNTIME.h5')
for index, row in joined_condition_5_days_fulfilled.iterrows():
    if (str(lastdate), row.name[1]) in f_data1.index:
        joined_condition_5_days_fulfilled.loc[index, '证券名称'] = \
            f_data1.loc[str(lastdate), row.name[1]]['STOCK_NAME'].values[0]
joined_condition_5_days_fulfilled['证券名称'] = joined_condition_5_days_fulfilled['证券名称'].astype(str)

joined_condition_5_days_fulfilled = joined_condition_5_days_fulfilled.reset_index()
joined_condition_5_days_fulfilled.columns = ['date', 'stk_code',  'banned_indicator', '异常波动公告数', '证券名称']
joined_condition_5_days_fulfilled['date'] = joined_condition_5_days_fulfilled['date'].apply(lambda x: x.strftime('%Y%m%d'))

#%% 20240429新增：abnormal数据同时进行交易
abnormal_fpath = f'/data/group/800463/stock_list/abnormal_notice_list/abnormal_notice_list_{nextdate}.xlsx'
while not os.path.exists(abnormal_fpath):
    time.sleep(60)
    print('abnormal文件未生成')
abnormal = pd.read_excel(abnormal_fpath)

abnormal['证券代码'] = abnormal['证券代码'].apply(lambda x: stockList.trans_int2windcode(x))
abnormal['date'] = nextdate
abnormal['banned_indicator'] = ''
abnormal['异常波动公告数'] = ''
abnormal['stk_code'] = abnormal['证券代码']

ycbd = joined_condition_5_days_fulfilled.copy()
concat_df = pd.concat([ycbd, abnormal[ycbd.columns]], axis=0).drop_duplicates('stk_code').reset_index(drop=True)

excel_saver({'Sheet1': concat_df},
            path_user + 'ycbd_list_%s.xlsx' % nextdate, index=True)
excel_saver({'Sheet1': concat_df},
            path_group + 'ycbd_list/ycbd_list_%s.xlsx' % nextdate, index=True)
send_message(f'{nowdate} 5日异常波动列表已生成：{len(concat_df)}只股票')
from dataApi.sendInfo import send_message
# send_message(f'5日异常波动列表已生成：{len(concat_df)}只股票', ['018107'])
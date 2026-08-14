import sys
sys.path.append('/data/user/015614/Lucien')

import pandas as pd
from xquant.factordata import FactorData

from MixedWork.GreyStockGenerator import IO

s = FactorData()
import datetime as dt
import numpy as np


def excel_saver(output_dict, excel_name):
    writer = pd.ExcelWriter(excel_name, engine='xlsxwriter')
    for key in output_dict:
        output_dict[key].to_excel(writer, sheet_name=key)
    writer.save()
    return

import sys
if len(sys.argv) < 2:
    date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]
    # date = '20241009'
else:
    date = sys.argv[1]

lastdate = s.tradingday(date, -2)[0]
start_date = s.tradingday(date, -10)[0]
year = lastdate[:4]  # 当前年度
last_year = str(int(year) - 1)  # 上一年度
last_year_period = last_year + '0101'  # 上一年开始的日期

f_data = IO.read_data([start_date, lastdate], columns=['close', 'adjfactor'],
                      alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
all_sample = list(f_data['close'].unstack().columns)

# 新闻文本
from xquant.textdata import NewsData

nd = NewsData()
ycbd_tot = pd.DataFrame()
notice_tot = pd.DataFrame()
for stock in all_sample:
    # 2023注册制后，修改为对全市场捕捉异常波动
    print(stock)
    data_info = nd.getAnnouncement([stock], str(last_year_period), str(date))
    if len(data_info) == 0:
        continue
    data_info = data_info.rename(columns={'PUBDATE': 'dt'})
    data_info['Ticker'] = stock
    data_info = data_info.set_index(['dt', 'Ticker']).sort_index()
    data_info = data_info[data_info['TEXTTITLE'].apply(lambda x: x != None)]
    if len(data_info) != 0:
        data_info = data_info.loc[pd.Timestamp(start_date):, ]
        ycbd_warning = data_info[['TEXTTITLE']][data_info['TEXTTITLE'].apply(lambda x: '严重异常波动' in x or '严重异动' in x)]
        if len(ycbd_warning) != 0:
            ycbd_warning['ycbd_indicator'] = 1
            ycbd_tot = pd.concat([ycbd_tot, ycbd_warning[['ycbd_indicator']]])
            notice_tot = pd.concat([notice_tot, ycbd_warning[['TEXTTITLE']]])

ycbd_tot = ycbd_tot.reset_index()
if len(ycbd_tot) == 0:
    tot_info_yzbd = pd.DataFrame()
else:
    ycbd_tot['dt_old'] = ycbd_tot['dt']
    ycbd_tot['dt'] = ycbd_tot['dt'].apply(lambda x: pd.Timestamp(s.tradingday(x.strftime('%Y%m%d'), 1)[0]))
    ycbd_tot = ycbd_tot.set_index(['dt', 'Ticker']).sort_index()
    ycbd_tot = ycbd_tot.loc[~ycbd_tot.index.duplicated(keep='first')].sort_index()

    notice_tot = notice_tot.reset_index()
    notice_tot['dt_old'] = notice_tot['dt']
    notice_tot['dt'] = notice_tot['dt'].apply(lambda x: pd.Timestamp(s.tradingday(x.strftime('%Y%m%d'), 1)[0]))
    notice_tot = notice_tot.set_index(['dt', 'Ticker']).sort_index()
    notice_tot = notice_tot.loc[~notice_tot.index.duplicated(keep='first')].sort_index()

    ycbd_need = ycbd_tot[(ycbd_tot.reset_index()['dt'] >= pd.Timestamp(start_date)).values][['ycbd_indicator']]
    notice_need = notice_tot[(notice_tot.reset_index()['dt'] >= pd.Timestamp(start_date)).values][['TEXTTITLE']]
    tot_info_yzbd = ycbd_need.join(notice_need)

from xquant.xqutils.helper import link

lm = link.LinkMessage()
message = date + '\n'
if len(tot_info_yzbd) == 0:
    message = message + '无严重异常波动个股，不用加入手动调整黑名单'
else:
    message = message + ' --------严重异常波动信息（检查是否已经加入手动调整黑名单）--------'
    for index, row in tot_info_yzbd.reset_index().iterrows():
        message = message + '\n'
        Ticker = row['dt'].strftime('%Y%m%d') + ',' + row['Ticker']
        text = row['TEXTTITLE']
        message = message + Ticker + ' ' + text
lm.sendMessage(message)
print('finished')
from dataApi.sendInfo import send_message
# send_message(message, ['018107'])

#%% 检测手动调整黑名单中是否已经有这个，如果没有，添加  NOTE:20240621 by fengc
manual_black_raw = pd.read_excel('/data/group/800463/stock_list/black_other_list/手动调整黑名单.xlsx')
manual_black = manual_black_raw.loc[manual_black_raw['出池时间'].isna()]

pre4d_date = s.tradingday(date, -4)[0]
tot_info_yzbd['pub_date'] = tot_info_yzbd.index.get_level_values(0).strftime('%Y%m%d').tolist()
today_new_super_notice = tot_info_yzbd.query(f'pub_date >= "{pre4d_date}"')
nan = manual_black['出池时间'].iloc[0]
if today_new_super_notice.shape[0] > 0:
    for idx in range(len(today_new_super_notice)):
        stock_code = today_new_super_notice.iloc[idx].name[1]
        stock_id = int(stock_code[:-3])
        stock_name = today_new_super_notice.iloc[idx].loc['TEXTTITLE'].split('：')[0]
        if stock_id not in manual_black['证券代码'].tolist() and \
                '*' not in stock_name and \
                '债券' not in today_new_super_notice.iloc[idx].loc['TEXTTITLE'] and \
                '转债' not in today_new_super_notice.iloc[idx].loc['TEXTTITLE']:
            send_message(f'手动调整黑名单中加入{stock_code} {stock_name}')
            manual_black_raw.loc[len(manual_black_raw)] = [stock_name, stock_id, pd.to_datetime(date), nan, '冯炽', '严重异常波动', '是']

    manual_black_raw['入池时间'] = manual_black_raw['入池时间'].apply(lambda x: pd.to_datetime(x).strftime('%Y/%m/%d'))
    manual_black_raw['出池时间'] = manual_black_raw['出池时间'].apply(lambda x: x.strftime('%Y/%m/%d') if type(x) == dt.datetime else x)
    manual_black_raw.to_excel('/data/group/800463/stock_list/black_other_list/手动调整黑名单.xlsx', index=False)

    send_message('已完成手动调整黑名单更新')

    # 再次校验
    new_black = pd.read_excel('/data/group/800463/stock_list/black_other_list/手动调整黑名单.xlsx')
    new_black = new_black.loc[new_black['出池时间'].isna()]
    msg = ', '.join(new_black.iloc[-8:]['证券名称'].tolist())
    send_message(f'当前手动调整黑名单中股票：{msg}')

    # import os
    # os.system('python3 /data/user/015614/Lucien/MixedWork/GreyStockGenerator/Grey_list.py')

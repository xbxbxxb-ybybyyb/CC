import sys
sys.path.append('/data/user/015614/Lucien')

import pandas as pd
from xquant.factordata import FactorData

from MixedWork.GreyStockGenerator import IO

s = FactorData()
import datetime as dt


def excel_saver(output_dict, excel_name):
    writer = pd.ExcelWriter(excel_name, engine='xlsxwriter')
    for key in output_dict:
        output_dict[key].to_excel(writer, sheet_name=key)
    writer.save()
    return


date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]
lastdate = s.tradingday(date, -2)[0]
start_date = s.tradingday(date, -10)[0]
f_data = IO.read_data([start_date, lastdate], columns=['close', 'adjfactor'],
                      alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
all_sample = list(f_data['close'].unstack().columns)

# 新闻文本
from xquant.textdata import NewsData

nd = NewsData()
ycbd_tot = pd.DataFrame()
notice_tot = pd.DataFrame()
for stock in all_sample:
    if stock[0] == '3':
        print(stock)
        data_info = nd.getNewsInfoByStockCode(stock[:~2])
        data_info = data_info[data_info['textcategory'].astype('str').str.startswith('2')]
        if len(data_info) == 0:
            continue
        data_info = data_info.rename(columns={'pubdate': 'dt'})
        data_info['Ticker'] = stock
        data_info = data_info.set_index(['dt', 'Ticker']).sort_index()
        data_info = data_info[data_info['texttitle'].apply(lambda x: x != None)]
        if len(data_info) != 0:
            data_info = data_info.loc[pd.Timestamp(start_date):, ]
            ycbd_warning = data_info[['texttitle']][data_info['texttitle'].apply(lambda x: ('严重异常波动' in x))]
            if len(ycbd_warning) != 0:
                ycbd_warning['ycbd_indicator'] = 1
                ycbd_tot = pd.concat([ycbd_tot, ycbd_warning[['ycbd_indicator']]])
                notice_tot = pd.concat([notice_tot, ycbd_warning[['texttitle']]])

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
    notice_need = notice_tot[(notice_tot.reset_index()['dt'] >= pd.Timestamp(start_date)).values][['texttitle']]
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
        text = row['texttitle']
        message = message + Ticker + ' ' + text
lm.sendMessage(message)
print('finished')

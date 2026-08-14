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

import sys
if len(sys.argv) < 2:
    date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]
    # date = '20241009'
else:
    date = sys.argv[1]

# date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]
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
fxts_tot = pd.DataFrame()
notice_tot = pd.DataFrame()
for stock in all_sample:
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
        fxts_warning = data_info[['TEXTTITLE']][
            data_info['TEXTTITLE'].apply(lambda x: ('撤销' in x) & ('风险警示' in x) & ('申请' not in x) & ('实施' not in x))]
        if len(fxts_warning) != 0:
            fxts_warning['fxts_indicator'] = 1
            fxts_tot = pd.concat([fxts_tot, fxts_warning[['fxts_indicator']]])
            notice_tot = pd.concat([notice_tot, fxts_warning[['TEXTTITLE']]])

fxts_tot = fxts_tot.reset_index()
if len(fxts_tot) == 0:
    tot_info_fxts = pd.DataFrame()
else:
    fxts_tot['dt_old'] = fxts_tot['dt']
    fxts_tot['dt'] = fxts_tot['dt'].apply(lambda x: pd.Timestamp(s.tradingday(x.strftime('%Y%m%d'), 1)[0]))
    fxts_tot = fxts_tot.set_index(['dt', 'Ticker']).sort_index()
    fxts_tot = fxts_tot.loc[~fxts_tot.index.duplicated(keep='first')].sort_index()
    fxts_need = fxts_tot[(fxts_tot.reset_index()['dt'] >= pd.Timestamp(lastdate)).values][['fxts_indicator']]
    notice_tot = notice_tot.reset_index()
    notice_tot['dt_old'] = notice_tot['dt']
    notice_tot['dt'] = notice_tot['dt'].apply(lambda x: pd.Timestamp(s.tradingday(x.strftime('%Y%m%d'), 1)[0]))
    notice_tot = notice_tot.set_index(['dt', 'Ticker']).sort_index()
    notice_tot = notice_tot.loc[~notice_tot.index.duplicated(keep='first')].sort_index()

    notice_need = notice_tot[(notice_tot.reset_index()['dt'] >= pd.Timestamp(lastdate)).values][['TEXTTITLE']]
    tot_info_fxts = fxts_need.join(notice_need)

from xquant.xqutils.helper import link

lm = link.LinkMessage()
message = date
if len(tot_info_fxts) == 0:
    message = message + ' 无摘帽个股'
else:
    message = message + '\n-----------------摘帽信息-----------------'
    for index, row in tot_info_fxts.reset_index().iterrows():
        message = message + '\n'
        Ticker = row['dt'].strftime('%Y%m%d') + ',' + row['Ticker']
        text = row['TEXTTITLE']
        message = message + Ticker + ' ' + text
lm.sendMessage(message)
print('finished')

# coding: utf-8
# Author：fengchi863
# Date ：2023/12/24 13:23
import sys
sys.path.append('/data/user/015614/Lucien')

import datetime as dt
import numpy as np
import pandas as pd
from xquant.factordata import FactorData
from MixedWork.GreyStockGenerator import IO

path_user = '/data/user/015614/daily/灰名单生成/黑名单/'
path_group = '/data/group/800463/stock_list/'

def excel_saver(output_dict, excel_name, index):
    writer = pd.ExcelWriter(excel_name, engine='xlsxwriter')
    for key in output_dict:
        output_dict[key].to_excel(writer, sheet_name=key, index=index)
    writer.save()
    return

s = FactorData()

date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), 1)[0]
lastdate = s.tradingday(date, -2)[0]

md = IO.read_data([s.tradingday(str(lastdate), -100)[0], lastdate], columns=['pre_close', 'close', 'amt']
                  , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md = md[md['amt'] > 0]  # 去除停牌的日期
md['zcz'] = (((md.reset_index()['Ticker'].apply(lambda x: x[0] == '3'))
              & (md.reset_index()['dt'] >= '2020-08-24')) | (md.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
md['dl_price'] = np.floor(md['pre_close'] * 100 * 0.9 + 0.5) / 100
md['dl_price'][md['zcz']] = np.floor(md['pre_close'] * 100 * 0.8 + 0.5) / 100
md['close_is_dt'] = md['close'] == md['dl_price']
md_last = md.groupby('Ticker').tail(1)  # 为了处理停牌前跌停的股票
dt_stock_list = md_last[md_last['close_is_dt']].reset_index()['Ticker'].unique()

# 加入股票名称
f_data = IO.read_data([lastdate, lastdate],
                       alt='/data/group/800080/warehouse/prod/FCD/CHINA_STOCK/DAILY/SUNTIME/FCD_CHINA_STOCK_DAILY_SUNTIME.h5')
pre_dt_df = pd.DataFrame(index=dt_stock_list, columns=['证券名称'])
for index, row in pre_dt_df.iterrows():
    if (str(lastdate), row.name) in f_data.index:
        pre_dt_df.loc[index, '证券名称'] = f_data.loc[str(lastdate), row.name]['STOCK_NAME'].values[0]
pre_dt_df['证券名称'] = pre_dt_df['证券名称'].astype(str)
pre_dt_df.index.names = ['证券代码']
pre_dt_df = pre_dt_df.reset_index()

excel_saver({'Sheet1': pre_dt_df}, path_user + 'abnormal_notice_list_%s.xlsx' % date, index=False)
excel_saver({'Sheet1': pre_dt_df}, path_group + 'pre_dt_list/pre_dt_list_%s.xlsx' % date, index=False)

from xquant.xqutils.helper import link

lm = link.LinkMessage()
message = '前日跌停股上传成功：' + str(len(pre_dt_df)) + '只股票'
lm.sendMessage(message)

from dataApi.sendInfo import send_message
# send_message(message, ['018107'])
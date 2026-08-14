# coding: utf-8
# Author：fengchi863
# Date ：2023/4/24 19:02

import sys
sys.path.append('/data/user/015614/Lucien')
from MixedWork.GreyStockGenerator import IO
import numpy as np
import pandas as pd
from xquant.factordata import FactorData
fd = FactorData()

import datetime as dt

def excel_saver(output_dict, excel_name, index):
    writer = pd.ExcelWriter(excel_name, engine='xlsxwriter')
    for key in output_dict:
        output_dict[key].to_excel(writer, sheet_name=key, index=index)
    writer.save()
    return

path_user = '/data/user/015614/daily/灰名单生成/黑名单/'
path_group = '/data/group/800463/stock_list/'

nowdate = fd.tradingday(dt.datetime.now().strftime('%Y%m%d'), 1)[0]
# nowdate = '20240506'
nextdate = fd.tradingday(nowdate, 2)[1]

f_data = IO.read_data([fd.tradingday(nowdate, -1000)[0], nowdate],
                      alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareCompRestricted/AShareCompRestricted.h5')

last_trading_days = fd.tradingday(nowdate, -4)
last_trading_days.extend([fd.tradingday(nowdate, 2)[1]])
last_trading_days = list(map(int, last_trading_days))

f_data = f_data.query(f'S_INFO_LISTDATE in {last_trading_days}')
comp_restrict_list = f_data.index.get_level_values(1).unique().tolist()
comp_restrict_list = list(filter(lambda x: x[:2] in ['60', '30', '00'], comp_restrict_list))

lastdate = fd.tradingday(nowdate, -2)[0]
f_data1 = IO.read_data([lastdate, lastdate],
                       alt='/data/group/800080/warehouse/prod/FCD/CHINA_STOCK/DAILY/SUNTIME/FCD_CHINA_STOCK_DAILY_SUNTIME.h5')
res_df = pd.DataFrame(index=comp_restrict_list)
res_df['证券名称'] = np.nan
for index in comp_restrict_list:
    if (str(lastdate), index) in f_data1.index:
        res_df.loc[index, '证券名称'] = f_data1.loc[str(lastdate), index]['STOCK_NAME'].values[0]
res_df['证券名称'] = res_df['证券名称'].astype(str)
res_df.index = res_df.index.map(lambda x: x[:6])
res_df.index.names = ['证券代码']

excel_saver({'Sheet1': res_df},
            path_user + 'share_comp_restrict_list_%s.xlsx' % nowdate, index=True)
excel_saver({'Sheet1':res_df},
            path_group + 'share_comp_restrict_list/share_comp_restrict_list_%s.xlsx' % nowdate, index=True)


from xquant.xqutils.helper import link

lm = link.LinkMessage()
message = '近5日限售解禁股上传成功：' + str(len(res_df)) + '只股票'
lm.sendMessage(message)
from dataApi.sendInfo import send_message
# send_message(message, ['018107'])
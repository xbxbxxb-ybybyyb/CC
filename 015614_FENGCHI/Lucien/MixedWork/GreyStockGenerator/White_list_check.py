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


path_user = '/data/user/015614/daily/灰名单生成/黑名单/'
path_group = '/data/group/800463/stock_list/'

date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]
# date = '20250417'
lastdate = s.tradingday(date, -2)[0]

white_file = path_group + 'white_list/%s.xls' % date
white_list = pd.read_excel(white_file)
name_data = IO.read_data([lastdate, lastdate], columns=['STOCK_NAME'], alt='/data/group/800080/warehouse/prod/FCD/CHINA_STOCK/DAILY/SUNTIME/FCD_CHINA_STOCK_DAILY_SUNTIME.h5')
name_data = name_data.groupby(['dt', 'Ticker']).first().reset_index()
name_data = name_data[name_data['STOCK_NAME'].apply(lambda x: 'ST' not in x and '退' not in x)]
name_data['证券代码'] = name_data['Ticker'].apply(lambda x: x[:-3])
# name_data = name_data[name_data['证券代码'].apply(lambda x: x[0] in ['0', '6', '3'] and x[:2] != '68')]
# name_data = name_data[name_data['证券代码'].apply(lambda x: x[0] in ['0', '6', '3'])]
name_data = name_data[name_data['证券代码'].apply(lambda x: x[0] in ['0', '6', '3'] or x[:2] in ['82', '83', '87', '88', '43'])]
name_data = name_data[name_data['证券代码'].apply(lambda x: x[0] in ['0', '6', '3'])]
leak = name_data[name_data['证券代码'].apply(lambda x: x not in white_list['证券代码'].unique())]

excel_saver({'缺失名单': leak}, path_user + 'whiter_list_check_%s.xlsx' % date)

print('finished')
from xquant.xqutils.helper import link

lm = link.LinkMessage()
message = '白名单缺失检验:' + str(len(leak))
lm.sendMessage(message)

from dataApi.sendInfo import send_file
send_file(path_user + 'whiter_list_check_%s.xlsx' % date)
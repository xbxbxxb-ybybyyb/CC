import sys
sys.path.append('/data/user/015614/Lucien')

import os

import numpy as np
import pandas as pd
from xquant.factordata import FactorData
from MixedWork.GreyStockGenerator import IO
from dataApi.stockList import trans_int2windcode as Int2Wc
from MixedWork.GreyStockGenerator.tools import trans_any2code
from xquant.xqutils.helper import link
lm = link.LinkMessage()

s = FactorData()
import datetime as dt
import time

path_user = '/data/user/015614/daily/灰名单生成/黑名单/'
path_group = '/data/group/800463/stock_list/'
path_hold = '/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/'
path_sold = '/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/'

# date = dt.datetime.now().strftime('%Y%m%d')
import sys
if len(sys.argv) < 2:
    date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), 1)[0]
    # date = '20241217'
else:
    date = sys.argv[1]

# date = '20250415'
lastdate = s.tradingday(date, -2)[0]

#
# def int_2_stock_code(number):
#     str_number = str(int(number))
#     if number < 99999:
#         while len(str_number) < 6:
#             str_number = '0' + str_number
#     if str_number[0] == '6':
#         str_number = str_number + '.SH'
#     else:
#         str_number = str_number + '.SZ'
#     return str_number


pre_st_file = path_group + 'pre_st_list/pre_st_list_%s.xlsx' % lastdate
defer_reply_file = path_group + 'defer_reply_list/defer_reply_list_%s.xlsx' % lastdate
after_dt_file = path_group + 'after_dt_list/after_dt_list_%s.xlsx' % lastdate
pre_dt_file = path_group + 'pre_dt_list/pre_dt_list_%s.xlsx' % date
abnormal_file = path_group + 'abnormal_notice_list/abnormal_notice_list_%s.xlsx' % date
share_comp_restrict_file = path_group + 'share_comp_restrict_list/share_comp_restrict_list_%s.xlsx' % date
manual_file = path_group + 'black_other_list/手动调整黑名单.xlsx'
saturn_file = path_hold + 'saturn成交记录-%s.xlsx' % lastdate
jupiter_file = path_sold + '日内强势股总卖出记录-%s.xlsx' % lastdate
jupiterBj_file = path_sold + '日内强势股总卖出记录Bj-%s.xlsx' % lastdate
# ceres_file = path_hold + 'ceres成交记录-%s.xlsx' % lastdate
Europa_file = path_hold + 'Europa成交记录-%s.xlsx' % lastdate
Metis_file = path_sold + '日内强势股总卖出记录Metis-%s.xlsx' % lastdate
Leda_file = path_sold + '日内强势股总卖出记录Leda-%s.xlsx' % lastdate
Ceres_file = path_sold + '日内强势股总卖出记录Ceres-%s.xlsx' % lastdate
P4_file = path_sold + '日内强势股总卖出记录P4-%s.xlsx' % lastdate
mimas_file = path_sold + '日内强势股总卖出记录Mimas-%s.xlsx' % lastdate

while not os.path.exists(pre_st_file):
    print('等待pre_st黑名单中')
    time.sleep(30)
while not os.path.exists(defer_reply_file):
    print('等待defer_reply黑名单中')
    time.sleep(30)
while not os.path.exists(after_dt_file):
    print('等待after_dt黑名单中')
    time.sleep(30)
while not os.path.exists(pre_dt_file):
    print('等待pre_dt黑名单中')
    time.sleep(30)
while not os.path.exists(abnormal_file):
    print('等待异常波动黑名单中')
    time.sleep(30)
while not os.path.exists(share_comp_restrict_file):
    print('等待限售股解禁黑名单中')
    time.sleep(30)
while not os.path.exists(saturn_file):
    print('等待saturn成交记录中')
    time.sleep(30)
while not os.path.exists(jupiter_file):
    print('等待jupiter成交记录中')
    time.sleep(30)
while not os.path.exists(Ceres_file):
    print('等待ceres成交记录中')
    time.sleep(30)
while not os.path.exists(P4_file):
    print('等待p4成交记录中')
    time.sleep(30)
while not os.path.exists(Europa_file):
    print('等待Europa成交记录中')
    time.sleep(30)
while not os.path.exists(Metis_file):
    print('等待Metis成交记录中')
    time.sleep(30)
while not os.path.exists(Leda_file):
    print('等待Leda成交记录中')
    time.sleep(30)
while not os.path.exists(jupiterBj_file):
    print('等待jupiter北交所成交记录中')
    time.sleep(30)

# pre_st
pre_st_list = pd.read_excel(pre_st_file)
# pre_dt
pre_dt_list = pd.read_excel(pre_dt_file)
pre_dt_list['证券代码'] = pre_dt_list['证券代码'].apply(lambda x: int(x[:-3]))
# defer_reply
defer_reply_list = pd.read_excel(defer_reply_file)
# after_dt
after_dt_list = pd.read_excel(after_dt_file)
# abnormal_notice
abnormal_list = pd.read_excel(abnormal_file)
# share_comp_restrict_file
share_comp_restrict_list = pd.read_excel(share_comp_restrict_file)
# manual
manual_list = pd.read_excel(manual_file)
manual_list = manual_list[manual_list['出池时间'].isna()]
# 合并股票列表
joined_black_list = []
# for stock_excel in [pre_st_list, pre_dt_list, defer_reply_list, after_dt_list, abnormal_list, manual_list, share_comp_restrict_list]:
for stock_excel in [pre_st_list, pre_dt_list, defer_reply_list, after_dt_list, manual_list, share_comp_restrict_list]:
    if len(stock_excel) != 0:
        joined_black_list = joined_black_list + list(stock_excel['证券代码'].apply(trans_any2code))
joined_black_list = list(set(joined_black_list))

# 读取名称数据
black = pd.DataFrame()
black['股票代码'] = joined_black_list
llast_data = s.tradingday(lastdate, -2)[0]
name_data = IO.read_data([llast_data, llast_data], alt='/data/group/800080/warehouse/prod/FCD/CHINA_STOCK/DAILY/SUNTIME/FCD_CHINA_STOCK_DAILY_SUNTIME.h5')
for index, row in black.iterrows():
    if (llast_data, row['股票代码']) in name_data.index:
        black.loc[index, '证券名称'] = name_data.loc[llast_data, row['股票代码']]['STOCK_NAME'].values[0]
    else:
        black.loc[index, '证券名称'] = str(np.nan)

# 筛选每日新增黑名单
last_black_list = pd.read_excel(path_user + 'black_list_%s.xlsx' % lastdate, sheet_name='黑名单')
last_black_list['股票代码'] = last_black_list['股票代码'].apply(trans_any2code)
last_black_list['lastdate'] = 1
black_list = pd.merge(black, last_black_list[['股票代码', 'lastdate']], how='left', on='股票代码')
black_list['lastdate'] = black_list['lastdate'].fillna(0)
for index, row in black_list.iterrows():
    if row['lastdate'] == 0:
        black_type = ''
        if row['股票代码'] in list(share_comp_restrict_list['证券代码'].apply(trans_any2code)):
            black_type += '限售解禁；'
        if row['股票代码'] in list(pre_st_list['证券代码'].apply(trans_any2code)):
            black_type += 'pre_ST；'
        if row['股票代码'] in list(defer_reply_list['证券代码'].apply(trans_any2code)):
            black_type += '延期回复；'
        if row['股票代码'] in list(after_dt_list['证券代码'].apply(trans_any2code)):
            black_type += '一字跌停；'
        if row['股票代码'] in list(abnormal_list['证券代码'].apply(trans_any2code)):
            black_type += '异常波动；'
        if row['股票代码'] in list(manual_list['证券代码'].apply(trans_any2code)):
            black_type += '手动调整；'
        if row['股票代码'] in list(pre_dt_list['证券代码'].apply(trans_any2code)):
            black_type += 'pre_dt；'
        black_list.loc[index, '类别'] = black_type
if '类别' not in black_list.columns.tolist():
    black_list['类别'] = ''
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
excel_saver({'黑名单(不包括ST)': black_list_nost, '黑名单': black_list},
            path_group + 'black_list/black_list_%s.xlsx' % date, index=False)
lm.sendMessage(f"今日黑名单：{','.join(black_list_nost['股票代码'].tolist())}")


# 生成图片
# _black_list_nost = black_list_nost.query('lastdate == 0.0')
# _black_list_nost['类别'] = _black_list_nost['类别'].apply(lambda x: x[:-1])
# _black_list_nost = _black_list_nost.drop(['lastdate'], axis=1)
# _black_list_nost = _black_list_nost.reset_index()

message = '黑名单新增：' + str(int(len(black_list) - black_list['lastdate'].sum())) + '只股票'
lm.sendMessage(message)

# 持仓
saturn_holding = pd.read_excel(saturn_file, sheet_name='累计卖出明细')
jupiter_solding = pd.read_excel(jupiter_file, sheet_name='总卖出记录')
# ceres_holding = pd.read_excel(ceres_file, sheet_name='累计卖出明细')
Europa_holding = pd.read_excel(Europa_file, sheet_name='累计卖出明细')
Metis_solding = pd.read_excel(Metis_file, sheet_name='总卖出记录')
leda_solding = pd.read_excel(Leda_file, sheet_name='总卖出记录')
jupiterBj_solding = pd.read_excel(jupiterBj_file, sheet_name='总卖出记录')
ceres_solding = pd.read_excel(Ceres_file, sheet_name='总卖出记录')
p4_solding = pd.read_excel(P4_file, sheet_name='总卖出记录')
mimas_solding = pd.read_excel(mimas_file, sheet_name='总卖出记录')
joined_holding = list(set(list(saturn_holding[saturn_holding['是否全部卖出'] != 1]['证券代码']) +
                          list(jupiter_solding[jupiter_solding['是否全部卖出'] != 1]['证券代码']) +
                          # list(ceres_holding[ceres_holding['是否全部卖出'] != 1]['证券代码']) +
                          list(Europa_holding[Europa_holding['是否全部卖出'] != 1]['证券代码']) +
                          list(Metis_solding[Metis_solding['是否全部卖出'] != 1]['证券代码']) +
                          list(leda_solding[leda_solding['是否全部卖出'] != 1]['证券代码']) +
                          list(jupiterBj_solding[jupiterBj_solding['是否全部卖出'] != 1]['证券代码']) +
                          list(ceres_solding[ceres_solding['是否全部卖出'] != 1]['证券代码']) +
                          list(p4_solding[p4_solding['是否全部卖出'] != 1]['证券代码']) +
                          list(mimas_solding[mimas_solding['是否全部卖出'] != 1]['证券代码'])))

# 黑名单中的持仓
grey_list = black[black['股票代码'].apply(lambda x: x in joined_holding)]
grey_list['股票代码'] = grey_list['股票代码'].apply(lambda x: x[:~2])
grey_list.to_excel(path_user + 'grey_list_%s.xlsx' % date, index=None)
grey_list.to_excel(path_group + 'grey_list/grey_list_%s.xlsx'%date,index = None)


from xquant.xqutils.helper import link

lm = link.LinkMessage()
message = '灰名单上传成功：' + str(len(grey_list)) + '只股票'
lm.sendMessage(message)

# 给link发送通知
def pad_len(string, length):
    return length - len(string.encode('GBK')) + len(string)

black_list = black_list.dropna(subset=['类别'])
black_list['股票代码'] = black_list['股票代码'].map(lambda x: trans_any2code(int(x)))

message = f'{date}黑名单池：\n'
for idx in range(len(black_list)):
    message += '\n' + '{0:<{len1}}\t{1:<{len2}}\t{2:{len3}}'.format(black_list.iloc[idx]['股票代码'],
                                                             black_list.iloc[idx]['证券名称'],
                                                             black_list.iloc[idx]['类别'][:-1],
                                                             len1=11, len2=6, len3=6)

# 另一种对齐方式（废弃）
# black_list['message'] = black_list['股票代码'] + chr(12288) + black_list['证券名称'].apply(lambda x: x.center(10)) + black_list['类别'].apply(lambda x: x[:-1].rjust(6))
# message = f'{date}黑名单池：\n' + '\n'.join(black_list['message'])

print(message)
lm.sendMessage(message)

# 交接给陈少森时这样弄
from dataApi.sendInfo import send_message
send_message(message, ['015585'])
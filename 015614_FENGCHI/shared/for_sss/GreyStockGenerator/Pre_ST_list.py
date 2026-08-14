import sys
sys.path.append('/data/user/015614/Lucien')

import datetime as dt
import re

import numpy as np
import pandas as pd
from xquant.factordata import FactorData
from xquant.textdata import NewsData

from MixedWork.GreyStockGenerator import IO

nd = NewsData()
s = FactorData()
path_user = '/data/user/015614/daily/灰名单生成/黑名单/'
path_group = '/data/group/800463/stock_list/'
# ST预警股票黑名单：当前年度，发布可能ST警示的股票，在预计年报发布前10天。

# 读取日期
# date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'),-1)[0] #该日开盘前早上运行
date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), 1)[0]
lastdate = s.tradingday(date, -2)[0]  # 上一交易日
year = lastdate[:4]  # 当前年度
last_year = str(int(year) - 1)  # 上一年度
last_year_period = last_year + '1231'  # 上一年度报告期
last_year_last_month_dt = pd.to_datetime(last_year + '1201')  # 公告读取区间

# 读取基本数据
data = IO.read_data([last_year_period, date], columns=['close']
                    , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
stock_list = data['close'].unstack().columns  # 股票列表

# 读取股票公告数据
info_list = []
for stock in stock_list:
    if stock[-2:] not in ['SZ', 'SH']:
        continue
    info = nd.getNewsInfoByStockCode(stock[:-3])
    # info = info[info['textcategory'].apply(lambda x: x not in [303604, 303605, 303606, 303607, 303608, 303609, 303610, 303611, 303612, 303613, 303614,303615])]
    info = info[info['textcategory'].astype('str').str.startswith('2')]
    if len(info) == 0:
        continue

    info = info[info['pubdate'] >= last_year_last_month_dt]
    info = info.rename(columns={'pubdate': 'dt'})
    info['Ticker'] = stock
    info['newsID'] = info.index.astype(str)
    info = info[['dt', 'Ticker', 'texttitle', 'newsID']]
    info_list.append(info)
news_info = pd.concat(info_list, ignore_index=True)

# ——————第一类：退市风险警示（年报可能ST）——————
# 处理公告数据
news_info_st0 = news_info[news_info['texttitle'].apply(lambda x: '可能' in x and '退市风险' in x)]
news_info_st0 = news_info_st0.sort_values(['Ticker', 'dt'])
stock_date0 = pd.DataFrame()
stock_date0['st_warning'] = news_info_st0.groupby('Ticker')['dt'].first()  # 可能风险警示的日期

# 读取年报公布日期
issuing_date = IO.read_data([last_year_period, last_year_period],
                            alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AShareIssuingDatePredict/AShareIssuingDatePredict.h5')
issuing_date = issuing_date.reset_index(level=['dt'])
stock_date0['predict_issuing'] = pd.to_datetime(issuing_date['S_STM_PREDICT_ISSUINGDATE'], format='%Y%m%d')  # 预计发布日期
stock_date0['issuing'] = pd.to_datetime(issuing_date['S_STM_ACTUAL_ISSUINGDATE'], format='%Y%m%d')  # 实际发布日期

# 计算时间区间
date_dt = pd.to_datetime(date)
stock_date0 = stock_date0.dropna(subset=['st_warning', 'predict_issuing'])  # 去除可能风险警示日期和预计发布日期为空的股票
stock_date0['predict_10day'] = stock_date0['predict_issuing'].apply(
    lambda x: s.tradingday(x.strftime('%Y%m%d'), -11)[0])  # 预计发布日期前十个交易日
stock_date0['predict_10day'] = pd.to_datetime(stock_date0['predict_10day'])
stock_date0['begin'] = stock_date0[['st_warning', 'predict_10day']].max(axis=1)  # 开始日期为可能风险警示的日期和预计前十个交易日的最大值
stock_date0['end'] = stock_date0['issuing'].apply(lambda x: x - dt.timedelta(days=1) if x <= date_dt else date_dt)  # 结束日期为实际发布日期和当前日期的最小值

# ——————第二类：其他风险警示（一月内不解决则ST）——————
# 处理公告数据
news_info_st1 = news_info[news_info['texttitle'].apply(lambda x: '可能' in x and '其他风险' in x)]
news_info_st1 = news_info_st1.sort_values(['Ticker', 'dt'])
stock_date1 = news_info_st1[['Ticker', 'dt']].copy()
stock_date1 = stock_date1.rename(columns={'dt': 'st_warning'})  # 可能风险警示的日期
stock_date1['month_later'] = stock_date1['st_warning'].apply(lambda x: x + dt.timedelta(days=31))  # 截止日期

# 对可能提到截止日期的股票单独处理
for index, row in news_info_st1.iterrows():
    day_max = row['dt']
    news_body = nd.getNewsBody([row['newsID']])['newsBody'].iloc[0]
    news_body = news_body.replace('\r', '').replace('\n', '').replace(' ', '')  # 去除换行符空白符
    for text in news_body.split('。'):
        if '其他风险警示' in text:
            sub = re.findall('(\d{4}年\d+月\d+日)', text)  # 含有其他风险警示的句子中，是否有日期
            for day_text in sub:
                day_dt = pd.to_datetime(day_text, format='%Y年%m月%d日')
                if day_dt > day_max:  # 日期需大于公告发布日
                    print(row['Ticker'], row['dt'].strftime('%Y%m%d'), text)
                    day_max = day_dt
    if day_max > row['dt']:
        stock_date1.loc[index, 'month_later'] = day_max
stock_date1['month_later'] = stock_date1['month_later'].apply(
    lambda x: pd.Timestamp(s.tradingday(x.strftime('%Y%m%d'), 1)[0]))
# 对重复提示的公告做剔除
ind_list = []
for i in range(len(stock_date1)):
    Ticker, st_warning, ind = stock_date1['Ticker'].iloc[i], stock_date1['st_warning'].iloc[i], stock_date1.index[i]
    for j in range(i):
        if stock_date1['Ticker'].iloc[j] == Ticker:
            if st_warning <= stock_date1['month_later'].iloc[j]:
                if stock_date1.index[j] not in ind_list:
                    ind_list.append(ind)
stock_date1 = stock_date1.drop(ind_list)
stock_date1 = stock_date1.set_index(['Ticker'])

stock_date1['begin'] = stock_date1['month_later'].apply(
    lambda x: s.tradingday(x.strftime('%Y%m%d'), -14)[0])  # 开始日期为截止日期前十个交易日（考虑到截止日期用31天，而月份最少28天，则11+3=14天）
stock_date1['begin'] = pd.to_datetime(stock_date1['begin'])
stock_date1['end'] = stock_date1['month_later'].apply(lambda x: x if x <= date_dt else date_dt)  # 结束日期为截止日期和当前日期的最小值

# 生成股票列表
stock_date = pd.concat([stock_date0, stock_date1])
r_list = []
for stock, row in stock_date.iterrows():
    begin = row['begin'].strftime('%Y%m%d')
    end = row['end'].strftime('%Y%m%d')
    if begin > end:
        continue
    r = pd.DataFrame()
    r['dt'] = s.tradingday(begin, end)
    r['Ticker'] = stock
    r_list.append(r)

if len(r_list) == 0:
    out = pd.DataFrame(columns=['证券代码', '证券名称'])
else:
    res = pd.concat(r_list, ignore_index=True).drop_duplicates()
    res['dt'] = pd.to_datetime(res['dt'])
    res['证券代码'] = res['Ticker'].apply(lambda x: x[:~2])
    # 加入名称
    name_data = IO.read_data([last_year_period, lastdate], universe=list(res['Ticker'].unique()),
                             columns=['STOCK_NAME'],
                             alt='/data/group/800080/warehouse/prod/FCD/CHINA_STOCK/DAILY/SUNTIME/FCD_CHINA_STOCK_DAILY_SUNTIME.h5')
    name_data = name_data.groupby(['dt', 'Ticker']).first()
    for stock in res['Ticker'].unique():
        if (pd.to_datetime(lastdate), stock) in name_data.index:
            name_data.loc[(pd.to_datetime(date), stock), 'STOCK_NAME'] = name_data.loc[
                (pd.to_datetime(lastdate), stock), 'STOCK_NAME']
    res = res.set_index(['dt', 'Ticker'])
    res['证券名称'] = name_data['STOCK_NAME']
    res['证券名称'] = res['证券名称'].astype(str)

    res_today = res.query('dt==@date_dt')
    if len(res_today) > 0:
        out = res_today[['证券代码', '证券名称']]
    else:
        out = pd.DataFrame(columns=['证券代码', '证券名称'])


def excel_saver(output_dict, excel_name, index):
    writer = pd.ExcelWriter(excel_name, engine='xlsxwriter')
    for key in output_dict:
        output_dict[key].to_excel(writer, sheet_name=key, index=index)
    writer.save()
    return


stock_date = stock_date.applymap(lambda x: '' if np.isnat(x.to_datetime64()) else x.strftime('%Y%m%d')).reset_index()
excel_saver({'黑名单': out,
             '备选检查': stock_date},
            path_user + 'pre_st_list_%s.xlsx' % lastdate, index=False)
excel_saver({'黑名单':out,
             '备选检查':stock_date},
            path_group+'pre_st_list/pre_st_list_%s.xlsx'%lastdate,index = False)


from xquant.xqutils.helper import link

lm = link.LinkMessage()
message = '风险警示黑名单上传成功：' + str(len(out)) + '只股票'
lm.sendMessage(message)

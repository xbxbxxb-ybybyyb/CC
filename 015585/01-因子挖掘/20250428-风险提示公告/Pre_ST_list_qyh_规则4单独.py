import datetime as dt
import re

import numpy as np
import pandas as pd
from xquant.factordata import FactorData
from xquant.textdata import NewsData
from tqdm import tqdm
import IO

s = FactorData()

path_user = '/data/user/015585/01-因子挖掘/20250428-风险提示公告/pre_st_qyh_规则4/'
# path_group = '/data/group/800463/stock_list/'
# ST预警股票黑名单：当前年度，发布可能ST警示的股票，在预计年报发布前10天。

# 读取日期
date_list = s.tradingday(20250101,20250415)
for date in date_list:
# def generate_pre_st_file(date):
    s = FactorData()
    nd = NewsData()
    print(date)
    # date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), 1)[0]
    # date = '20250415'
    date_dt = pd.to_datetime(date)
    lastdate = s.tradingday(date, -2)[0]  # 上一交易日
    year = lastdate[:4]  # 当前年度
    last_year = str(int(year) - 1)  # 上一年度
    last_year_period = last_year + '1231'  # 上一年度报告期
    # last_year_period = '20231231'  # 上一年度报告期    # 20250103：防止年初读取不到公告，读取内容为空
    last_year_last_month_dt = pd.to_datetime(last_year + '1201')  # 公告读取区间

    # 读取基本数据
    data = IO.read_data([last_year_period, date], columns=['close']
                        , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    stock_list = data['close'].unstack().columns  # 股票列表

    info_list = []
    for stock in stock_list:
        if stock[-2:] not in ['SZ', 'SH', 'BJ']:
            continue
        # if stock[-2:] in ['BJ']:
        #     print(1)
        info = nd.getAnnouncement([stock], str(last_year_period), str(date))
        # nd.getAnnouncement(['000040.SZ'], '20231231', '20240523')
        if len(info) == 0:
            continue

        info = info[info['PUBDATE'] >= last_year_last_month_dt]
        info = info.rename(columns={'PUBDATE': 'dt'})
        info['Ticker'] = stock
        info['newsID'] = info['ORIGINALCODE'].astype(str)
        info = info[['dt', 'Ticker', 'TEXTTITLE', 'newsID']]
        info_list.append(info)
    news_info = pd.concat(info_list, ignore_index=True)
    # ——————第四类：立案调查、退市（与年报无关）等情形——————
    '''
    1、获取标题中含有“风险提示”或“立案调查”或者"风险警示"的公告，获取其正文
    2、筛选出正文中有“退市”或“终止上市”或“ST”或“重大违法”或“其他风险警示”的部分
    '''
    # 处理公告数据
    news_info_st4 = news_info[news_info['TEXTTITLE'].apply(lambda x: type(x) == str \
                                                                     and (('风险提示' in x) or ('立案调查' in x) or ('风险警示' in x)) and ('撤销' not in x))]
    newID_list = news_info_st4['newsID'].map(int).tolist()
    if len(newID_list) == 0:
        news_bodies_df = pd.DataFrame()
    else:
        news_bodies_df = nd.getAnnouncementContent(newID_list).loc[newID_list]
    news_bodies_df = news_bodies_df.reset_index()
    news_info_st4['newsID_int'] = news_info_st4['newsID'].apply(int)
    news_info_st4 = pd.merge(news_info_st4,news_bodies_df,left_on='newsID_int',right_on='ORIGINALCODE')
    news_info_st4 = news_info_st4[(news_info_st4['CONTENT'].str.contains('退市'))
                                  | (news_info_st4['CONTENT'].str.contains('终止上市'))
                                  | (news_info_st4['CONTENT'].str.contains('ST'))
                                  | (news_info_st4['CONTENT'].str.contains('重大违法'))
                                  | (news_info_st4['CONTENT'].str.contains('其他风险警示'))]

    news_info_st4 = news_info_st4.sort_values(['Ticker', 'dt'])
    stock_date4 = news_info_st4[['Ticker', 'dt']].copy()
    stock_date4 = stock_date4.rename(columns={'dt': 'stop_warning'})
    stock_date4['15days_later'] = stock_date4['stop_warning'].apply(lambda x: pd.Timestamp(s.tradingday(x.strftime('%Y%m%d'), 15)[-1]))
    stock_date4['dt_today'] = date_dt
    stock_date4['begin'] = stock_date4['stop_warning']
    stock_date4['end'] = stock_date4[['15days_later','dt_today']].min(axis=1)

    stock_date4 = stock_date4.set_index('Ticker', drop=True)
    stock_date4 = stock_date4.dropna(axis=0)

    # 生成股票列表
    # stock_date = pd.concat([stock_date0, stock_date1, stock_date2, stock_date4])
    stock_date = pd.concat([stock_date4])
    r_list = []
    fd = FactorData()
    for stock, row in stock_date.iterrows():
        if type(row['begin']) == pd._libs.tslibs.nattype.NaTType:
             continue
        begin = row['begin'].strftime('%Y%m%d')
        end = row['end'].strftime('%Y%m%d')
        if begin > end:
            continue
        r = pd.DataFrame()
        r['dt'] = fd.tradingday(begin, end)
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
    print(path_user + 'pre_st_list_%s.xlsx' % lastdate,len(pd.read_excel(path_user + 'pre_st_list_%s.xlsx' % lastdate)))
    # return
    # excel_saver({'黑名单':out,
    #              '备选检查':stock_date},
    #             path_group+'pre_st_list/pre_st_list_%s.xlsx'%lastdate,index = False)
    #
    #
    # from xquant.xqutils.helper import link
    #
    # lm = link.LinkMessage()
    # message = '风险警示黑名单上传成功：' + str(len(out)) + '只股票'
    # lm.sendMessage(message)
# from joblib import Parallel, delayed
# factor_df_list = Parallel(n_jobs=28)(delayed(generate_pre_st_file)(date) for date in date_list)



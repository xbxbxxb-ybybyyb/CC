# -*- coding: utf-8 -*-

import datetime as dt

import numpy as np
import pandas as pd
from xquant.factordata import FactorData

from ProdWork.intra_strong.add_mimas.Util2Ceres import get_buyDfTotalInfo, get_buyDfTodayInfo, get_sellDfTotalInfo, get_sellDfTodayInfo
from ProdWork.intra_strong.add_mimas.recordUtil import write_excel_help, write_excel_helpTotal, write_excel_helpTotal_graph

s = FactorData()
from LucienUtil import IO
import sys
import time
import os

if __name__ == "__main__":
    t1 = time.time()
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]  # 判断当前的日期
        # date = '20250807' # 若未在当个交易日晚上运行程序，需要在次日早上修改date
    print('current date = %s' % date)

    Adate = date[0:4]+'-'+date[4:6]+'-'+date[6:8]
    lastdate = s.tradingday(date, -2)[0]
    Alastdate = lastdate[0:4]+'-'+lastdate[4:6]+'-'+lastdate[6:8]

    while (os.path.exists('/data/group/800463/日内强势股/实盘分析记录/日内强势股总买入记录/日内强势股总买入记录P4-%s.xlsx'% date)==False) |\
          (os.path.exists('/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/日内强势股总卖出记录P4-%s.xlsx'% date)==False):
        print(f'日内强势股总买入记录P4-{date}.xlsx 等待中')
        time.sleep(60)

    # ------------------------------------------------------新加模块结束------------------------------------------------------------
    buyDf = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/日内强势股总买入记录/日内强势股总买入记录P4-%s.xlsx'% date)
    sellDf = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/日内强势股总卖出记录P4-%s.xlsx'% date)
    buysellDf_joined = sellDf.set_index(['买入日期', '证券代码']) \
        .join(buyDf.rename(columns={'发生日期': '买入日期'}).set_index(['买入日期', '证券代码'])[['回归信号', '买入当天持仓金额', '委托金额']])
    buysellDf_joined_columns_need = list(buysellDf_joined.columns)
    buysellDf_joined_columns_need.remove('买入当天开盘价')
    buysellDf_joined_columns_need.remove('买入当天涨停价')
    buysellDf_joined = buysellDf_joined[buysellDf_joined_columns_need].reset_index()
    buysellDf_joined['TN日收益率(%)'] = ((1 + buysellDf_joined['卖出部分收益率(%)'] / 100) / (1 + buysellDf_joined['买入当日收益率(%)'] / 100) - 1) * 100
    buysellDf_joined = buysellDf_joined[['买入日期', '证券代码', '证券名称', '卖出日期', '买入数量', '买入金额','买入当天持仓金额', '买入成交均价', '买入当天开盘涨幅(%)',
                                           '买入当天盘中是否涨停', '买入当天是否收盘涨停', '买入当日收益率(%)', '卖出数量', '卖出成交均价', '卖出金额',
                                           '是否全部卖出', '卖出比例', '卖出部分盈利金额', 'TN日收益率(%)', '卖出部分收益率(%)', '实际是否正收益', '卖出日期开盘价',
                                           '卖出金额占市场比', '总卖出数量', 'TN_v2o10nd1', '回归信号','委托金额']]

    writePath = f'/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/P4成交记录-{date}.xlsx'

    f_data = IO.read_data(['20201201',date], columns=['close','pre_close'], alt = '/data/group/800080/warehouse_event/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    f_data['zcz'] = (((f_data.reset_index()['Ticker'].apply(lambda x: x[0:3] == '300')) & (f_data.reset_index()['dt'] >= '2020-08-24')) |
                      (f_data.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    is_zt = (f_data['close'] == np.floor(f_data['pre_close'] * 100 * 1.1 + 0.5) / 100)
    is_zt[f_data['zcz']] = (f_data['close'] == np.floor(f_data['pre_close'] * 100 * 1.2 + 0.5) / 100)
    last_is_zt = is_zt.unstack().shift().stack()
    sellDf_copy = sellDf.copy()
    sellDf_copy['买入日期'] = sellDf_copy['买入日期'].apply(lambda x:pd.Timestamp(x))
    sellDf_copy = sellDf_copy.rename(columns = {'买入日期':'dt','证券代码':'Ticker'}).set_index(['dt','Ticker'])

    buyResDf, fig = get_buyDfTotalInfo(buyDf.copy(), Adate, strategy='P4')
    todayBuyResDf = get_buyDfTodayInfo(buyDf.copy(), Adate, strategy='P4')
    sellResDf = get_sellDfTotalInfo(sellDf.copy(), Adate, fig, strategy='P4')
    todaySellResDf = get_sellDfTodayInfo(sellDf.copy(), Adate)

    return_path = "/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/收益画图/%s_%s_p4.png" % (Adate, '生产环境')

    dropSellColumns = []

    def write_excel(path):
        import xlsxwriter
        buysellDf_joined.replace(np.nan, '', inplace=True)
        workbook = xlsxwriter.Workbook(path)
        wformat1 = workbook.add_format({'border': 2, 'align': 'center', 'valign': 'vcenter'})
        wformat2 = workbook.add_format({'border': 2, 'align': 'center', 'valign': 'vcenter', 'num_format': 2})
        wformat3 = workbook.add_format({'align': 'left', 'bg_color': 'yellow'})
        merge_format = workbook.add_format({'border': 2, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#FFCC99'})

        worksheet2 = workbook.add_worksheet('今日汇总情况')
        end_idx = 0

        if todayBuyResDf is not None:
            end_idx = write_excel_helpTotal(worksheet2, todayBuyResDf, 2, 0, date + '买入汇总', wformat1, merge_format)
        if todaySellResDf is not None:
            end_idx = write_excel_helpTotal(worksheet2, todaySellResDf, 2, 3, date + '卖出汇总', wformat1, merge_format)

        end_idx = write_excel_helpTotal(worksheet2, buyResDf, 2, 6, '累计买入汇总', wformat1, merge_format)
        end_idx = write_excel_helpTotal_graph(worksheet2, sellResDf, 2, 9, '累计卖出汇总', wformat1, merge_format, return_path) # NOTE:需要运行天数满足 by fengc，否则注释掉

        worksheet3 = workbook.add_worksheet('累计卖出明细')
        end_idx = write_excel_help(worksheet3, buysellDf_joined, 1, '', wformat1, wformat2)
        workbook.close()

    path = writePath
    write_excel(writePath)

    print(f'5-7.p4_record_generate运行耗时{round(time.time() - t1, 2)}秒')

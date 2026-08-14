# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 17:45:05 2019

@author: 013551
"""

import pandas as pd
import numpy as np
from ProdWork.intra_strong.add_mimas.recordUtil import write_excel_help, write_excel_helpTotal, write_excel_helpTotal_graph
from ProdWork.intra_strong.add_mimas.Util4ZT import get_buyDfTotalInfo,get_buyDfTodayInfo,get_sellDfTotalInfo,get_sellDfTodayInfo,get_lztDfTotalInfo,get_lnonztDfTotalInfo,get_DfTodayInfo
import datetime as dt
from xquant.factordata import FactorData
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
        # date = '20240802'  # 若未在当个交易日晚上运行程序，需要在次日早上修改date
    print('current date = %s' % date)

    Adate = date[0:4] + '-' + date[4:6] + '-' + date[6:8]
    lastdate = s.tradingday(date, -2)[0]
    Alastdate = lastdate[0:4] + '-' + lastdate[4:6] + '-' + lastdate[6:8]
    print('date=%s, lastdate=%s'%(date,lastdate))
    while (os.path.exists('/data/group/800463/日内强势股/实盘分析记录/日内强势股总买入记录/日内强势股总买入记录-%s.xlsx'%(date))==False) |\
          (os.path.exists('/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/日内强势股总卖出记录-%s.xlsx'%(date))==False):
        print('calESRate-v4等待标签汇总中')
        time.sleep(60)

    buyDf = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/日内强势股总买入记录/日内强势股总买入记录-%s.xlsx' % date)
    sellDf = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/日内强势股总卖出记录-%s.xlsx' % date)
    # cybsellDf = sellDf[sellDf['证券代码'].apply(lambda x:x[0:3] == '300') & (sellDf['买入日期'] >= '2020-08-24')]
    writePath = '/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/jupiter成交记录-%s.xlsx' % date
    logFile = '/data/group/800463/日内强势股/实盘分析记录/每日突破/每日突破_%s_%s.xlsx'%(date, 'prod')

    last_is_zt = pd.read_pickle('/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/前置数据/last_is_zt/updating.pkl')
    sellDf_copy = sellDf.copy()
    sellDf_copy['买入日期'] = sellDf_copy['买入日期'].apply(lambda x:pd.Timestamp(x))
    sellDf_copy = sellDf_copy.rename(columns = {'买入日期':'dt','证券代码':'Ticker'}).set_index(['dt','Ticker'])
    sellDf['last_is_zt'] = last_is_zt.reindex(sellDf_copy.index).values
    lnonztsellDf = sellDf[sellDf['last_is_zt']==False]
    lztsellDf = sellDf[sellDf['last_is_zt']==True]

    buyResDf,fig, all_zt_df = get_buyDfTotalInfo(buyDf.copy(), Adate)
    todayResDf = get_DfTodayInfo(buyDf.copy(), Adate)
    todayBuyResDf = get_buyDfTodayInfo(buyDf.copy(), Adate)
    sellResDf = get_sellDfTotalInfo(sellDf.copy(), Adate, fig)
    _, fig_thisyear, _ = get_buyDfTotalInfo(buyDf[buyDf['发生日期'] > '2022-01-01'].copy(), Adate)
    _ = get_sellDfTotalInfo(sellDf[sellDf['买入日期'] > '2022-01-01'].copy(), Adate, fig_thisyear)
    todaySellResDf = get_sellDfTodayInfo(sellDf.copy(), Adate)
    lnonzt_sellResDf = get_lnonztDfTotalInfo(lnonztsellDf.copy(), Adate)
    # lzt_sellResDf = get_lztDfTotalInfo(lztsellDf.copy(), Adate)
    # lzt_sellResDf.to_excel('/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/前置数据/JupiterZ卖出数据持久化/lzt_sellResDf.xlsx')
    lzt_sellResDf = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/前置数据/JupiterZ卖出数据持久化/lzt_sellResDf.xlsx', index_col=0)

    buyDf['买入当日突破时间'] = buyDf['买入当日突破时间'].astype(str)
    buyDf.rename(columns={'涨跌幅(%)':'买入当日涨跌幅(%)'}, inplace=True)

    return_path = "/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/收益画图/%s_%s.png" % (Adate, '生产环境')
    return_path_2022 = "/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/收益画图/%s_%s_2022.png" % (Adate, '生产环境')
    # trade_path = "/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/成交画图/%s_%s.png"%(date,'生产环境')
    sell_path = "/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/卖出画图/%s_%s.png"%(date,'生产环境')

    dropSellColumns = []
    selldropcols = ['卖出挂单笔数','卖出成交笔数','卖出开始时间','卖出结束时间']
    def write_excel(path):
        import xlsxwriter
        buyDf.replace(np.nan, '', inplace=True)
        sellDf.replace(np.nan, '', inplace=True)
        workbook = xlsxwriter.Workbook(path)
        wformat1 = workbook.add_format({'border':2,'align':'center','valign':'vcenter'})
        wformat2 = workbook.add_format({'border':2,'align':'center','valign':'vcenter','num_format':2})
        wformat3 = workbook.add_format({'align':'left','bg_color':'yellow'})
        merge_format = workbook.add_format({'border':2, 'align':'center', 'valign':'vcenter', 'bg_color':'#FFCC99'})
        worksheet1 = workbook.add_worksheet('今日汇总情况')
        end_idx = 0
        if todayResDf is not None:
            end_idx = write_excel_helpTotal(worksheet1,todayResDf,1,0,date+'基础汇总',wformat1,merge_format)
        if todayBuyResDf is not None:
            # end_idx = write_excel_helpTotal_graph(worksheet1,todayBuyResDf,1,2,date+'买入汇总',wformat1,merge_format,trade_path)
            end_idx = write_excel_helpTotal_graph(worksheet1,todayBuyResDf,1,2,date+'买入汇总',wformat1,merge_format)
        if todaySellResDf is not None:
            end_idx = write_excel_helpTotal(worksheet1,todaySellResDf,end_idx+3,0,date+'卖出汇总',wformat1,merge_format)#这里可以加卖出画图
        worksheet2 = workbook.add_worksheet('累计汇总情况')
        end_idx = write_excel_helpTotal(worksheet2,buyResDf,2,0,'累计买入汇总',wformat1,merge_format)
        end_idx = write_excel_helpTotal_graph(worksheet2,lnonzt_sellResDf,2,3,'JupiterN卖出汇总',wformat1,merge_format,return_path)
        end_idx = write_excel_helpTotal_graph(worksheet2,lzt_sellResDf,2,6,'JupiterZ卖出汇总',wformat1,merge_format,return_path)
        # end_idx = write_excel_helpTotal_graph(worksheet2,cyb_sellResDf,2,9,'创业板注册制汇总',wformat1,merge_format,return_path_2022)
        worksheet3 = workbook.add_worksheet('累计买入明细')
        savebuyDf = buyDf
        end_idx = write_excel_help(worksheet3, savebuyDf, 1, '',wformat1,wformat2)
        # end_idx = write_excel_help_buy(worksheet3,buyDf,end_idx+2,wformat3)
        worksheet4 = workbook.add_worksheet('累计卖出明细')
        savesellDf = sellDf.drop(columns=selldropcols)
        print('Jupiter成交记录中存在持仓：')
        print(savesellDf[(savesellDf['卖出比例'] != '100.00%') & (savesellDf['买入日期'] != Adate)][
            ['买入日期', '证券代码', '证券名称', '买入数量','卖出比例']])
        end_idx = write_excel_help(worksheet4, savesellDf, 1, '',wformat1,wformat2)
        all_zt_save = all_zt_df.fillna(0).reset_index()
        all_zt_save.rename(columns = {'Buy_Date':'买入日期'}, inplace=True)
        worksheet5 = workbook.add_worksheet('样本统计')
        end_idx = write_excel_help(worksheet5, all_zt_save, 1, '', wformat1, wformat2)
        workbook.close()

    path = writePath
    write_excel(writePath)
    print(f'5-2.jup_record_generate运行耗时{round(time.time() - t1, 2)}秒')


# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 17:45:05 2019

@author: 013551
"""

import pandas as pd
import numpy as np
from ProdWork.intra_strong.add_ceres.recordUtil import write_excel_help, write_excel_helpTotal, write_excel_helpTotal_graph
from ProdWork.intra_strong.add_ceres.Util2Saturn import get_buyDfTotalInfo, get_buyDfTodayInfo, get_sellDfTotalInfo, get_sellDfTodayInfo
import datetime as dt
from xquant.factordata import FactorData
s = FactorData()
from LucienUtil import IO
import openpyxl
import sys
import time
import os

if __name__ == "__main__":
    t1 = time.time()
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]  # 判断当前的日期
        # date = '20240802' # 若未在当个交易日晚上运行程序，需要在次日早上修改date
    print('current date = %s' % date)

    Adate = date[0:4]+'-'+date[4:6]+'-'+date[6:8]
    lastdate = s.tradingday(date, -2)[0]
    Alastdate = lastdate[0:4]+'-'+lastdate[4:6]+'-'+lastdate[6:8]

    while (os.path.exists('/data/group/800463/日内强势股/实盘分析记录/日内强势股总买入记录/项目二总买入记录-%s.xlsx'%(date))==False) |\
          (os.path.exists('/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/项目二总卖出记录-%s.xlsx'%(date))==False):
        print('calESRate-v6等待标签汇总中')
        time.sleep(60)

    # ------------------------------------------------------新加模块结束------------------------------------------------------------
    buyDf = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/日内强势股总买入记录/项目二总买入记录-%s.xlsx'%(date))
    sellDf = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/项目二总卖出记录-%s.xlsx'%(date))
    buysellDf_joined = sellDf.set_index(['买入日期', '证券代码']) \
        .join(buyDf.rename(columns={'发生日期': '买入日期'}).set_index(['买入日期', '证券代码'])[['回归信号', '分类信号','买入当天持仓金额','委托金额']])
    buysellDf_joined_columns_need = list(buysellDf_joined.columns)
    buysellDf_joined_columns_need.remove('买入当天开盘价')
    #buysellDf_joined_columns_need.remove('买入当天收盘价')
    buysellDf_joined_columns_need.remove('买入当天涨停价')
    buysellDf_joined = buysellDf_joined[buysellDf_joined_columns_need].reset_index()
    buysellDf_joined['TN日收益率(%)'] = ((1 + buysellDf_joined['卖出部分收益率(%)'] / 100) / (1 + buysellDf_joined['买入当日收益率(%)'] / 100) - 1) * 100
    buysellDf_joined = buysellDf_joined[['买入日期', '证券代码', '证券名称', '卖出日期', '买入数量', '买入金额','买入当天持仓金额', '买入成交均价', '买入当天开盘涨幅(%)',
                                           '买入当天盘中是否涨停', '买入当天是否收盘涨停', '买入当日收益率(%)', '卖出数量', '卖出成交均价', '卖出金额',
                                           '是否全部卖出', '卖出比例', '卖出部分盈利金额', 'TN日收益率(%)', '卖出部分收益率(%)', '实际是否正收益', '卖出日期开盘价',
                                           '卖出金额占市场比', '总卖出数量', '前日形态', 'TN_v2o10', '买入时点',
                                           '回归信号', '分类信号','930信号','931信号','委托金额']]
    # today_930_signal = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate, sheet_name = '项目二930样本')
    # today_931_signal = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate, sheet_name = '项目二931样本')
    # buysellDf_joined_today = buysellDf_joined[buysellDf_joined['买入日期'] == Adate]
    # if len(today_930_signal) != 0:
    #     buysellDf_joined.loc[buysellDf_joined_today.index,'930信号'] = today_930_signal.set_index('Unnamed: 0').reindex(buysellDf_joined_today.rename(columns = {'证券代码':'Unnamed: 0'}).set_index('Unnamed: 0').index)\
    #     ['p2shouldBuySignal'].values
    # if len(today_931_signal) != 0:
    #     buysellDf_joined.loc[buysellDf_joined_today.index,'931信号'] = today_931_signal.set_index('Unnamed: 0').reindex(buysellDf_joined_today.rename(columns = {'证券代码':'Unnamed: 0'}).set_index('Unnamed: 0').index)\
    #     ['p2shouldBuySignal'].values

    writePath = '/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/saturn成交记录-%s.xlsx'%(date)
    # writePath_bak = '/data/user/013550/文件检查/日内强势股成交记录/项目二成交记录-%s.xlsx'%(date)
    f_data = IO.read_data(['20201201',date],columns = ['close','pre_close'],alt = '/data/group/800080/warehouse_event/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    f_data['zcz'] = (((f_data.reset_index()['Ticker'].apply(lambda x: x[0:3] == '300')) & (f_data.reset_index()['dt'] >= '2020-08-24')) |
                      (f_data.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    is_zt = (f_data['close'] == np.floor(f_data['pre_close'] * 100 * 1.1 + 0.5) / 100)
    is_zt[f_data['zcz']] = (f_data['close'] == np.floor(f_data['pre_close'] * 100 * 1.2 + 0.5) / 100)
    last_is_zt = is_zt.unstack().shift().stack()
    sellDf_copy = sellDf.copy()
    sellDf_copy['买入日期'] = sellDf_copy['买入日期'].apply(lambda x:pd.Timestamp(x))
    sellDf_copy = sellDf_copy.rename(columns = {'买入日期':'dt','证券代码':'Ticker'}).set_index(['dt','Ticker'])

    # 将930的数据保留在表格中
    # buyResDf_930,fig_930 = get_buyDfTotalInfo(buyDf[buyDf['买入时点'] == 930].copy(),Adate,930)
    # todayBuyResDf_930 = get_buyDfTodayInfo(buyDf[buyDf['买入时点'] == 930].copy(),Adate,930)
    # sellResDf_930 = get_sellDfTotalInfo(sellDf.copy(),Adate,fig_930,930)
    # todaySellResDf_930 = get_sellDfTodayInfo(sellDf.copy(),Adate,930)
    # buyResDf_930.to_excel('/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/前置数据/SaturnS0用数据及绘图/Saturn930buy_summary_df_before20240229.xlsx')
    # sellResDf_930.to_excel('/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/前置数据/SaturnS0用数据及绘图/Saturn930sell_summary_df_before20240229.xlsx')
    buyResDf_930 = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/前置数据/SaturnS0用数据及绘图/Saturn930buy_summary_df_before20240229.xlsx', index_col=0)
    sellResDf_930 = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/前置数据/SaturnS0用数据及绘图/Saturn930sell_summary_df_before20240229.xlsx', index_col=0)

    buyResDf_931,fig_931 = get_buyDfTotalInfo(buyDf[buyDf['买入时点'] == 931].copy(),Adate,931)
    todayBuyResDf_931 = get_buyDfTodayInfo(buyDf[buyDf['买入时点'] == 931].copy(),Adate,931)
    sellResDf_931 = get_sellDfTotalInfo(sellDf.copy(),Adate,fig_931,931)
    todaySellResDf_931 = get_sellDfTodayInfo(sellDf.copy(), Adate, 931)

    return_path_930 = "/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/收益画图/%s_%s_p2_930.png" % ('2024-01-04', '生产环境')
    return_path_931 = "/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/收益画图/%s_%s_p2_931.png" % (Adate, '生产环境')

    dropSellColumns = []

    def write_excel(path):
        import xlsxwriter
        buysellDf_joined.replace(np.nan,'',inplace=True)
        workbook = xlsxwriter.Workbook(path)
        wformat1 = workbook.add_format({'border':2,'align':'center','valign':'vcenter'})
        wformat2 = workbook.add_format({'border':2,'align':'center','valign':'vcenter','num_format':2})
        wformat3 = workbook.add_format({'align':'left','bg_color':'yellow'})
        merge_format = workbook.add_format({'border':2,'align':'center','valign':'vcenter','bg_color':'#FFCC99'})
        worksheet2 = workbook.add_worksheet('今日S1汇总情况')
        worksheet1 = workbook.add_worksheet('今日S0汇总情况')
        end_idx = 0
        # if todayBuyResDf_930 is not None:
        #     end_idx = write_excel_helpTotal(worksheet1,todayBuyResDf_930,2,0,date+'买入汇总',wformat1,merge_format)
        # if todaySellResDf_930 is not None:
        #     end_idx = write_excel_helpTotal(worksheet1,todaySellResDf_930,2,3,date+'卖出汇总',wformat1,merge_format)
        if todayBuyResDf_931 is not None:
            end_idx = write_excel_helpTotal(worksheet2,todayBuyResDf_931,2,0,date+'买入汇总',wformat1,merge_format)
        if todaySellResDf_931 is not None:
            end_idx = write_excel_helpTotal(worksheet2,todaySellResDf_931,2,3,date+'卖出汇总',wformat1,merge_format)
        end_idx = write_excel_helpTotal(worksheet1,buyResDf_930,2,6,'累计买入汇总',wformat1,merge_format)
        end_idx = write_excel_helpTotal_graph(worksheet1,sellResDf_930,2,9,'累计卖出汇总',wformat1,merge_format,return_path_930)
        end_idx = write_excel_helpTotal(worksheet2,buyResDf_931,2,6,'累计买入汇总',wformat1,merge_format)
        end_idx = write_excel_helpTotal_graph(worksheet2,sellResDf_931,2,9,'累计卖出汇总',wformat1,merge_format,return_path_931)
        worksheet3 = workbook.add_worksheet('累计卖出明细')
        end_idx = write_excel_help(worksheet3, buysellDf_joined, 1, '',wformat1,wformat2)
        workbook.close()

    path = writePath
    write_excel(writePath)

    # import xlsxwriter
    # def copy_worksheets(source_file, target_file, sheet_name):
    #     df = pd.ExcelFile(source_file)
    #     sheet = df.parse(sheet_name)
    #     sheet.to_excel(target_file, sheet_name=sheet_name, index=False, header=False)
    # TODO: 添加S0汇总情况

    # 添加S0这一个sheet
    # sheet1 = pd.read_excel(writePath, sheet_name='今日S1汇总情况')
    # sheet2 = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/saturn成交记录-20231229.xlsx', sheet_name='今日S0汇总情况')
    # sheet3 = pd.read_excel(writePath, sheet_name='累计卖出明细')
    # new_excel = {'今日S1汇总情况': sheet1,
    #              '今日S0汇总情况': sheet2,
    #              '累计卖出明细': sheet3}
    # from LucienUtil.FileUtil import FileUtil
    # FileUtil.save_dict2xls(new_excel, '/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/', f'saturn成交记录-{date}-test.xlsx')

    # copy_worksheets('/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/saturn成交记录-20240102.xlsx',
    #                 f'/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/saturn成交记录-{date}-test.xlsx',
    #                 sheet_name='今日S0汇总情况')

    # 以上两种方式尝试都不行


    print(f'5-1.sat_record_generate运行耗时{round(time.time() - t1, 2)}秒')

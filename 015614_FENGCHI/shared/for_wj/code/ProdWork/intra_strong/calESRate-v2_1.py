# -*- coding: utf-8 -*-

"""
Created on Tue Apr 30 10:32:35 2019
生成总卖出信息汇总文件
@author: 013551
"""

import os

import numpy as np
import pandas as pd
from xquant.marketdata import MarketData

from LucienUtil import IO
from ProdWork.intra_strong.calESRateHelpV2 import getExtraBuyInfo, getExtraSellInfo, calProfit, calProfit_pj2
from ProdWork.intra_strong.func_Basic_zt import cal_Basic_zt

mdp = MarketData()
import datetime as dt
from xquant.factordata import FactorData
import sys

s = FactorData()
if __name__ == "__main__":
    buy_commonInfoColumns = ['证券名称','证券代码','发生日期','买入当日收益率(%)','买入当天涨停价','买入当天收盘价','买入当天是否收盘涨停']
    buy_commonInfoColumns_rename = ['证券名称','证券代码','买入日期','买入当日收益率(%)','买入当天涨停价','买入当天收盘价','买入当天是否收盘涨停']

    needColumns = ['买入日期','卖出日期','买入数量','买入金额','买入成交均价',
                   '买入当天是否收盘涨停','买入当天收盘价','买入当日收益率','卖出数量','卖出成交均价',
                   '卖出金额','是否全部卖出','卖出部分盈利金额','卖出部分收益率','实际是否正收益','卖出日期开盘价','理论是否正收益','理论是否预测正确']
    resDf = pd.DataFrame(columns=needColumns)

    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]  # 判断当前的日期
        # date = '20230606'# # 若未在当个交易日晚上运行程序，需要在次日早上修改date
    print('current date = %s' % date)

    Adate = date[0:4] + '-' + date[4:6] + '-' + date[6:8]
    lastdate = s.tradingday(date, -2)[0]
    Alastdate = lastdate[0:4] + '-' + lastdate[4:6] + '-' + lastdate[6:8]
    IO_mother_dir = '/data/group/800080/warehouse_event'
    MD_data_prod_dir = IO_mother_dir + '/prod/LOCAL_DATA/FLAG/%s/' % date
    import time
    while not os.path.exists(MD_data_prod_dir + '%s_MD.success' % date):
        print('等待MD或RDF或RISK或5分钟数据中')
        time.sleep(60)

    nowFile = '/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/综合信息查询_成交回报_%s.xls' % date
    historyFile = '/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/日内强势股总卖出记录-%s.xlsx' % lastdate
    historyFile001 = '/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/日内强势股总卖出记录New-%s.xlsx' % lastdate
    historyFile_pj2 = '/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/项目二总卖出记录-%s.xlsx' % lastdate
    historyFile_pj3 = '/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/项目三总卖出记录-%s.xlsx' % lastdate
    logFile = '/data/group/800463/日内强势股/实盘分析记录/每日突破/每日突破_%s_%s.xlsx'%(date, 'prod')
    while not os.path.exists(nowFile):
        print('wait %s !!!!!!!!!!'%nowFile)
        time.sleep(60)

    todayRecordDf = pd.read_excel(nowFile)
    todayRecordDf = todayRecordDf #[(todayRecordDf['组合编号'] == 4719)|(todayRecordDf['组合编号'] == 370301)|(todayRecordDf['组合编号'] == 2000000200)|(todayRecordDf['组合编号'] == 2000000100)|(todayRecordDf['组合编号'] == 2000000201)|(todayRecordDf['组合编号'] == 2000000101)]
    if date == '20210702':
        vwap=todayRecordDf.loc[todayRecordDf[todayRecordDf['证券代码']==2892].index,'成交均价']
        todayRecordDf.loc[todayRecordDf[todayRecordDf['证券代码']==2892].index,'成交数量'] = 32600
        todayRecordDf.loc[todayRecordDf[todayRecordDf['证券代码']==2892].index,'成交均价'] = vwap * 45640 / 32600

    def deal_Unnamed(data):
        history_need_columns = list(data.columns)
        if 'Unnamed: 0' in history_need_columns:
            history_need_columns.remove('Unnamed: 0')
        data = data[history_need_columns]
        return data

    historySellDf = deal_Unnamed(pd.read_excel(historyFile, sheet_name='总卖出记录'))
    if os.path.exists(historyFile001):
        historySellDf001 = deal_Unnamed(pd.read_excel(historyFile001, sheet_name='总卖出记录'))
    else:
        historySellDf001 = pd.DataFrame(columns = historySellDf.columns)
    historySellDf_pj2 = deal_Unnamed(pd.read_excel(historyFile_pj2, sheet_name='总卖出记录'))
    if os.path.exists(historyFile_pj3):
        historySellDf_pj3 = deal_Unnamed(pd.read_excel(historyFile_pj3, sheet_name='总卖出记录'))
        #historyBuyDf_pj3 = historyBuyDf_pj3[historyBuyDf_pj3['证券名称'].notnull()]
    else:
        historySellDf_pj3 = pd.DataFrame(columns = historySellDf_pj2.columns)
    if os.path.exists(logFile):
        logDf = pd.read_excel(logFile, sheet_name = '每日突破')
        if len(logDf)>0:
            logDf = logDf[logDf['ZT_Time']!=0]
            logDf['actionSource'] = 'Jupiter'
        logDf001 = pd.read_excel(logFile, sheet_name='每日突破New')
        if len(logDf001) > 0:
            logDf001 = logDf001[logDf001['ZT_Time'] != 0]
            logDf001['actionSource'] = 'JupiterNew'
        logDf_saturn = pd.read_excel(logFile, sheet_name = '每日项目二')
        if len(logDf_saturn)>0:
            logDf_saturn = logDf_saturn[logDf_saturn['quantity']!=0]
        logDf_ceres = pd.read_excel(logFile, sheet_name='每日项目三')
        if len(logDf_ceres) > 0:
            logDf_ceres = logDf_ceres[logDf_ceres['quantity'] != 0]
        orderDf = pd.read_excel(logFile, sheet_name = '每日订单')
        orderDf[['lastQty', 'lastPx']] = orderDf[['lastQty', 'lastPx']].astype(float)
        orderDf['lastAmt'] = orderDf['lastQty'] * orderDf['lastPx']
        if len(orderDf) > 0:
            orderDf = orderDf[orderDf['transactionTime'].apply(lambda x:x[11:13]) != '00']
            sell_orderDf = orderDf[orderDf['orderSide'] == 'Sell']
            buy_orderDf = orderDf[orderDf['orderSide'] == 'Buy']
        else:
            sell_orderDf = pd.DataFrame()
            buy_orderDf = pd.DataFrame()
    else:
        logDf = pd.DataFrame()
        logDf001 = pd.DataFrame()
        logDf_saturn = pd.DataFrame()
        logDf_ceres = pd.DataFrame()
        buy_orderDf = pd.DataFrame()
        sell_orderDf = pd.DataFrame()

    def number2stockcode(x):
        x_str = str(int(x))
        while len(x_str) < 6:
            x_str = '0'+ x_str
        if x_str[0] == '6':
            x_str = x_str+'.SH'
        else: x_str = x_str+'.SZ'
        return x_str

    CommonInfoColumns = ['发生日期','成交均价','卖出日期开盘价']

    todaySellDf = todayRecordDf[todayRecordDf['委托方向']=='卖出']
    c_index = todaySellDf[(todaySellDf['证券代码'] == 2201) & (todaySellDf['发生日期'] == '2021-06-16')].index
    todaySellDf.loc[c_index, '成交均价'] = todaySellDf.loc[c_index, '成交金额'] / 50430
    todaySellDf.loc[c_index, '成交数量'] = 50430
    todayBuyDf = todayRecordDf[todayRecordDf['委托方向']=='买入']
    todayBuyDf['证券代码'] = todayBuyDf['证券代码'].apply(number2stockcode)
    orderDf_jupiter = orderDf[(orderDf['actionSource'] != 'JupiterNew') & (
                (orderDf['orderType'] == 'SplitLastShot') | (orderDf['orderType'] == 'MRiskSplitShot') | (
                    orderDf['orderType'] == 'JupiterFirstOrder') | (orderDf['orderType'] == 'MRiskSplitLastShotBuy') | (
                            orderDf['orderType'] == 'MRiskSplitShotBuy'))]

    orderDf_jupiter001 = orderDf[(orderDf['actionSource'] == 'JupiterNew')&(
            (orderDf['orderType'] == 'SplitLastShot')|(orderDf['orderType']  == 'MRiskSplitShot')|(
            orderDf['orderType'] == 'JupiterFirstOrder')| (orderDf['orderType']  == 'MRiskSplitLastShotBuy')| (
            orderDf['orderType']  == 'MRiskSplitShotBuy'))]
    orderDf_saturn = orderDf[orderDf['orderType'] == 'SaturnBuy']
    orderDf_ceres = orderDf[orderDf['orderType'] == 'CeresBuy']
    todayBuyDf_jupiter = todayBuyDf[todayBuyDf['证券代码'].apply(lambda x:x in list(np.unique(orderDf_jupiter['stockcode'])))]
    todayBuyDf_jupiter001 = todayBuyDf[todayBuyDf['证券代码'].apply(lambda x: x in list(np.unique(orderDf_jupiter001['stockcode'])))]
    todayBuyDf_saturn = todayBuyDf[todayBuyDf['证券代码'].apply(lambda x:x in list(np.unique(orderDf_saturn['stockcode'])))]
    todayBuyDf_ceres = todayBuyDf[todayBuyDf['证券代码'].apply(lambda x: x in list(np.unique(orderDf_ceres['stockcode'])))]

    resDf = historySellDf.copy()

    if '买入时形态' not in resDf.columns:
        resDf['买入时形态'] = np.nan

    resDf001 = historySellDf001.copy()

    if '买入时形态' not in resDf001.columns:
        resDf001['买入时形态'] = np.nan

    resDf_pj2 = historySellDf_pj2.copy()
    if '前日形态' not in resDf_pj2.columns:
        resDf_pj2['前日形态'] = np.nan

    resDf_pj3 = historySellDf_pj3.copy()
    if '前日形态' not in resDf_pj3.columns:
        resDf_pj3['前日形态'] = np.nan

    buyDf = todayBuyDf.copy()
    sellDf_tot = todaySellDf.copy()

    # def updatePositionBuy(buyDf,resDf,resDf_pj2,logDf,buy_orderDf):
    #     # 更改逻辑，改为使用日志中的信息作为买入的量计算
    #     if len(logDf) == 0: buy_log_Df_jupiter = pd.DataFrame()
    #     else: buy_log_Df_jupiter = logDf[logDf['order_direction'] == 'SplitLastShot']
    #     if len(logDf_saturn) == 0: buy_log_Df_saturn = pd.DataFrame()
    #     else: buy_log_Df_saturn = logDf_saturn[logDf_saturn['order_direction'] == 'A']
    #     # 先从日志中的信息里计算 买入额、买入量
    #     buy_orderDf_jupiter = buy_orderDf[buy_orderDf['orderType'] == 'SplitLastShot']
    #     buy_orderDf_saturn = buy_orderDf[buy_orderDf['orderType'] == 'SaturnBuy']
    #     def get_buy_amt_volume(data):
    #         data = data.sort_values(by = ['transactionTime'])
    #         len_buy = (data['ordStatus'] == 'NEW').sum()
    #         len_filled = (data['ordStatus'] == 'FILLED').sum()
    #         data_filled = data[data['ordStatus'] == 'FILLED']
    #         if len_buy != len_filled:
    #             if data.iloc[~0]['ordStatus'] == 'PARTIALLY_FILLED':
    #                 addition_vol = data.iloc[~0]['cumQty']
    #                 addition_amt = data.iloc[~0]['cumQty']*data.iloc[~0]['avgPx']
    #             else:
    #                 addition_vol, addition_amt = 0,0
    #         else:
    #             addition_vol, addition_amt = 0, 0
    #         deal_amt = (data_filled['quantity']*data_filled['avgPx']).sum() + addition_amt
    #         deal_vol = data_filled['quantity'].sum() + addition_vol
    #         deal_vwap = deal_amt/deal_vol if deal_vol!=0 else 0
    #         return pd.Series({'deal_amt':deal_amt,'deal_vol':deal_vol,'deal_vwap':deal_vwap})
    #     buy_orderDf_tot_info = buyDf.rename(columns = {'证券代码':'stockcode','成交数量':'deal_vol','成交金额':'deal_amt'})[['deal_vol','deal_amt','stockcode']]
    #     buy_orderDf_tot_info['deal_vwap'] = buy_orderDf_tot_info['deal_amt']/buy_orderDf_tot_info['deal_vol']
    #     # buy_orderDf_jupiter_info = buy_orderDf_jupiter.groupby('stockcode').apply(get_buy_amt_volume)
    #     # buy_orderDf_saturn_info = buy_orderDf_saturn.groupby('stockcode').apply(get_buy_amt_volume)
    #     buy_orderDf_jupiter_info = buy_orderDf_tot_info[buy_orderDf_tot_info['stockcode'].apply(lambda x:x in set(buy_orderDf_jupiter['stockcode']))].set_index('stockcode')
    #     buy_orderDf_saturn_info = buy_orderDf_tot_info[buy_orderDf_tot_info['stockcode'].apply(lambda x:x in set(buy_orderDf_saturn['stockcode']))].set_index('stockcode')
    #     if (date == '20210331'): buy_orderDf_saturn_info.loc['600888.SH',['deal_amt','deal_vol','deal_vwap']] = np.array([49494.00,7300.0,6.78])
    #     if (date == '20210415'): buy_orderDf_saturn_info.loc['605268.SH',['deal_amt','deal_vol','deal_vwap']] = np.array([994768.00,55800.0,994768/55800])
    #     buy_orderDf_saturn_info = buy_orderDf_saturn_info[buy_orderDf_saturn_info['deal_amt']!=0]
    #     # 在日志中有jupiter买入或者jupiter尝试买入才会进行输出，saturn只有买入不为0才会进行输出
    #     buyDf_jupiter = buyDf[buyDf['证券代码'].apply(lambda x:x in list(buy_orderDf_jupiter_info.index))]
    #     buyDf_saturn = buyDf[buyDf['证券代码'].apply(lambda x:x in list(buy_orderDf_saturn_info.index))]
    #     # commonInfoColumns是成交回报中直接有的信息、buyExtraColumns是通过计算重新获取的信息
    #     buyDf_jupiter = getExtraBuyInfo(buyDf_jupiter)
    #     for index,row in buyDf_jupiter.iterrows():
    #         dummy_resDfindex = len(resDf)
    #         stock_code = row['证券代码']
    #         resDf.loc[dummy_resDfindex,buy_commonInfoColumns_rename] = row[buy_commonInfoColumns].values
    #         resDf.loc[dummy_resDfindex,['买入数量','买入金额','买入成交均价']] = buy_orderDf_jupiter_info.loc[stock_code][['deal_vol','deal_amt','deal_vwap']].values
    #     buyExtraColumns = ['买入当天开盘涨幅(%)','买入当天开盘价','买入当天盘中是否涨停']
    #     buyDf_saturn = getExtraBuyInfo(buyDf_saturn)
    #     for index,row in buyDf_saturn.iterrows():
    #         dummy_resDfpj2_index = len(resDf_pj2)
    #         stock_code = row['证券代码']
    #         resDf_pj2.loc[dummy_resDfpj2_index,buy_commonInfoColumns_rename+buyExtraColumns] = row[buy_commonInfoColumns+buyExtraColumns].values
    #         resDf_pj2.loc[dummy_resDfpj2_index,['买入数量','买入金额','买入成交均价']] = buy_orderDf_saturn_info.loc[stock_code][['deal_vol','deal_amt','deal_vwap']].values
    #     md_close_pre_close = IO.read_data([date, date], columns=['pre_close', 'close']
    #                  , alt=IO_mother_dir + '/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #     # name_data = IO.read_data([lastdate, lastdate], alt='/data/group/800080/warehouse/prod/FCD/CHINA_STOCK/DAILY/SUNTIME/FCD_CHINA_STOCK_DAILY_SUNTIME.h5')
    #     # 针对日内强势股进行额外信息的填充
    #     for index,row in buy_log_Df_jupiter.iterrows():
    #         stockCode = row['Unnamed: 0']
    #         resDfIndex = resDf[resDf['证券代码']==stockCode].index
    #         # 其他columns，计算买入日形态和突破时间
    #         pre_close, close = md_close_pre_close.loc[date, stockCode].values
    #         resDf.loc[resDfIndex, '买入时形态'] = cal_Basic_zt(mdp, stockCode, date, pre_close, close)['label_pattern'].values[0]
    #     # 针对项目二930进行额外信息的填充
    #     if len(buy_log_Df_saturn) == 0:
    #         pass
    #     else:
    #         buy_log_Df_saturn = buy_log_Df_saturn.loc[~buy_log_Df_saturn['Unnamed: 0'].duplicated(keep='first')]
    #     saturn_basic_info = pd.read_hdf('/data/user/013550/project2_prod/everyday_Basic_v2/%s_%s/Basic_night_finish_%s_%s.h5'%(date,date,date,date))
    #     for index,row in buy_log_Df_saturn.iterrows():
    #         stockCode = row['Unnamed: 0']
    #         if (len(resDf_pj2[resDf_pj2['买入日期']==Adate])>0) and \
    #             (stockCode in resDf_pj2[resDf_pj2['买入日期']==Adate]['证券代码'].values):
    #             resDfpj2Index = resDf_pj2[resDf_pj2['证券代码']==stockCode].index
    #             if len(resDfpj2Index)>1:
    #                 resDfpj2Index = resDfpj2Index[-1:]
    #         # else: # 如果存在正常的数据
    #         #     # 针对当天在o32中没有但在log中有的票进行数据填充
    #         #     resDfpj2Index,stockCode = len(resDf_pj2),row['Unnamed: 0']
    #             resDf_pj2.loc[resDfpj2Index, '前日形态'] = saturn_basic_info.loc[date,stockCode]['lzt_label_pattern']
    #             resDf_pj2.loc[resDfpj2Index, '买入时点'] = '930'
    #     return resDf, resDf_pj2

    def updatePositionBuy(buyDf,resDf,resDf_pj2,resDf_pj3,logDf,buy_orderDf,resDf001):
        signal_info_pj2_930 = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate, sheet_name='项目二930样本')
        signal_info_pj2_931 = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate, sheet_name='项目二931样本')
        signal_info_pj3_931 = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate,sheet_name='Ceres931样本')
        # 添加买入的分钟数据
        buy_orderDf['buy_Time'] = buy_orderDf['transactionTime'].apply(lambda x:x[11:13]+x[14:16])
        # 更改逻辑，改为使用日志中的信息作为买入的量计算
        if len(logDf) == 0: buy_log_Df_jupiter = pd.DataFrame()
        else: buy_log_Df_jupiter = logDf[(logDf['order_direction'] == 'SplitLastShot') | (logDf['order_direction'] == 'JupiterFirstOrder')| (logDf['order_direction'] == 'MRiskSplitLastShotBuy')|(logDf['order_direction']  == 'MRiskSplitShotBuy')]
        if len(logDf001) == 0: buy_log_Df_jupiter001 = pd.DataFrame()
        else: buy_log_Df_jupiter001 = logDf001[(logDf001['order_direction'] == 'SplitLastShot') | (logDf001['order_direction'] == 'JupiterFirstOrder')| (logDf001['order_direction'] == 'MRiskSplitLastShotBuy')|(logDf001['order_direction']  == 'MRiskSplitShotBuy')]

        if len(logDf_saturn) == 0: buy_log_Df_saturn = pd.DataFrame()
        else: buy_log_Df_saturn = logDf_saturn[logDf_saturn['order_direction'] == 'A']
        if len(logDf_ceres) == 0: buy_log_Df_ceres = pd.DataFrame()
        else: buy_log_Df_ceres = logDf_ceres[logDf_ceres['order_direction'] == 'A']
        # 先从日志中的信息里计算 买入额、买入量
        buy_orderDf_jupiter = buy_orderDf[(buy_orderDf['actionSource'] != 'JupiterNew')&((buy_orderDf['orderType'] == 'SplitLastShot')|(buy_orderDf['orderType']  == 'MRiskSplitShot')|(buy_orderDf['orderType'] == 'JupiterFirstOrder')| (buy_orderDf['orderType'] == 'MRiskSplitLastShotBuy')|(buy_orderDf['orderType']  == 'MRiskSplitShotBuy'))]
        buy_orderDf_jupiter001 = buy_orderDf[(buy_orderDf['actionSource'] == 'JupiterNew') & (
                    (buy_orderDf['orderType'] == 'SplitLastShot') | (buy_orderDf['orderType'] == 'MRiskSplitShot') | (
                        buy_orderDf['orderType'] == 'JupiterFirstOrder') | (
                                buy_orderDf['orderType'] == 'MRiskSplitLastShotBuy') | (
                                buy_orderDf['orderType'] == 'MRiskSplitShotBuy'))]

        buy_orderDf_saturn = buy_orderDf[buy_orderDf['orderType'] == 'SaturnBuy']
        buy_orderDf_ceres = buy_orderDf[buy_orderDf['orderType'] == 'CeresBuy']

        def get_buy_amt_volume(data):
            data = data.sort_values(by = ['transactionTime'])
            len_buy = (data['ordStatus'] == 'NEW').sum()
            len_filled = (data['ordStatus'] == 'FILLED').sum()
            data_filled = data[data['ordStatus'] == 'FILLED']
            if len_buy != len_filled:
                if data.iloc[~0]['ordStatus'] == 'PARTIALLY_FILLED':
                    addition_vol = data.iloc[~0]['cumQty']
                    addition_amt = data.iloc[~0]['cumQty']*data.iloc[~0]['avgPx']
                else:
                    addition_vol, addition_amt = 0,0
            else:
                addition_vol, addition_amt = 0, 0
            deal_amt = (data_filled['quantity']*data_filled['avgPx']).sum() + addition_amt
            deal_vol = data_filled['quantity'].sum() + addition_vol
            deal_vwap = deal_amt/deal_vol if deal_vol!=0 else 0
            return pd.Series({'deal_amt':deal_amt,'deal_vol':deal_vol,'deal_vwap':deal_vwap})

        if len(buyDf)==0:
            print('今天成交回报没有买入！！！！！！')
            buyDf_jupiter = pd.DataFrame()
            buyDf_jupiter001 = pd.DataFrame()
            buyDf_saturn = pd.DataFrame()
            buyDf_ceres = pd.DataFrame()
        else:
            # buyDf['证券代码'] = buyDf['证券代码'].apply(number2stockcode)
            buy_orderDf_tot_info = buyDf.rename(columns = {'证券代码':'stockcode','成交数量':'deal_vol','成交金额':'deal_amt'})[['deal_vol','deal_amt','stockcode']]
            buy_orderDf_tot_info['deal_vwap'] = buy_orderDf_tot_info['deal_amt']/buy_orderDf_tot_info['deal_vol']
            buy_orderDf_jupiter_info = buy_orderDf_tot_info[buy_orderDf_tot_info['stockcode'].apply(lambda x:x in set(buy_orderDf_jupiter['stockcode']))].set_index('stockcode')
            buy_orderDf_jupiter_info001 = buy_orderDf_tot_info[buy_orderDf_tot_info['stockcode'].apply(
                lambda x: x in set(buy_orderDf_jupiter001['stockcode']))].set_index('stockcode')
            buy_orderDf_saturn_info = buy_orderDf_tot_info[buy_orderDf_tot_info['stockcode'].apply(lambda x:x in set(buy_orderDf_saturn['stockcode']))].set_index('stockcode')
            buy_orderDf_saturn_info = buy_orderDf_saturn_info[buy_orderDf_saturn_info['deal_amt']!=0]

            buy_orderDf_ceres_info = buy_orderDf_tot_info[buy_orderDf_tot_info['stockcode'].apply(lambda x: x in set(buy_orderDf_ceres['stockcode']))].set_index( 'stockcode')
            buy_orderDf_ceres_info = buy_orderDf_ceres_info[buy_orderDf_ceres_info['deal_amt'] != 0]

            # 在日志中有jupiter买入或者jupiter尝试买入才会进行输出
            buyDf_jupiter = buyDf[buyDf['证券代码'].apply(lambda x:x in list(buy_orderDf_jupiter_info.index))]
            buyDf_jupiter001 = buyDf[buyDf['证券代码'].apply(lambda x: x in list(buy_orderDf_jupiter_info001.index))]
            buyDf_saturn = buyDf[buyDf['证券代码'].apply(lambda x:x in list(buy_orderDf_saturn_info.index))]
            buyDf_ceres = buyDf[buyDf['证券代码'].apply(lambda x: x in list(buy_orderDf_ceres_info.index))]

            # commonInfoColumns是成交回报中直接有的信息、buyExtraColumns是通过计算重新获取的信息
            buyDf_jupiter = getExtraBuyInfo(buyDf_jupiter)
            buyDf_jupiter001 = getExtraBuyInfo(buyDf_jupiter001)
            buyDf_saturn = getExtraBuyInfo(buyDf_saturn)
            buyDf_ceres = getExtraBuyInfo(buyDf_ceres)

        for index, row in buyDf_jupiter.iterrows():
            dummy_resDfindex = len(resDf)
            stock_code = row['证券代码']
            resDf.loc[dummy_resDfindex,buy_commonInfoColumns_rename] = row[buy_commonInfoColumns].values
            #resDf.loc[dummy_resDfindex,['买入数量','买入金额','买入成交均价']] = buy_orderDf_jupiter_info.loc[stock_code][['deal_vol','deal_amt','deal_vwap']].values
            '''if stock_code not in resDf001[resDf001['买入日期']==Adate]['证券代码'].tolist():
                resDf.loc[dummy_resDfindex,['买入数量','买入金额','买入成交均价']] = buy_orderDf_jupiter_info.loc[stock_code][['deal_vol','deal_amt','deal_vwap']].values
            else:
                resDf.loc[dummy_resDfindex, '买入数量'] = float(buy_orderDf_jupiter_info.loc[stock_code]['deal_vol'])- float(resDf001[(resDf001['买入日期']==Adate)&(resDf001['证券代码']==stock_code)]['买入数量'])
                resDf.loc[dummy_resDfindex,  '买入金额'] = float(buy_orderDf_jupiter_info.loc[stock_code]['deal_amt'])- float(resDf001[(resDf001['买入日期'] == Adate) & (resDf001['证券代码'] == stock_code)][ '买入金额'])'''

            sel_order = buy_orderDf_jupiter[((buy_orderDf_jupiter['ordStatus'] == 'PARTIALLY_FILLED') | (buy_orderDf_jupiter['ordStatus'] == 'FILLED')) & (
                                                        buy_orderDf_jupiter['stockcode'] == stock_code)]
            resDf.loc[dummy_resDfindex, ['买入数量','买入金额']] = sel_order[['lastQty', 'lastAmt']].sum().values
            resDf.loc[dummy_resDfindex, '买入成交均价'] = resDf.loc[dummy_resDfindex, '买入金额'] / resDf.loc[dummy_resDfindex, '买入数量']
        for index,row in buyDf_jupiter001.iterrows():
            dummy_resDfindex = len(resDf001)
            stock_code = row['证券代码']
            resDf001.loc[dummy_resDfindex,buy_commonInfoColumns_rename] = row[buy_commonInfoColumns].values
            #resDf001.loc[dummy_resDfindex,['买入数量','买入金额','买入成交均价']] = buy_orderDf_jupiter_info001.loc[stock_code][['deal_vol','deal_amt','deal_vwap']].values
            if stock_code not in resDf[resDf['买入日期']==Adate]['证券代码'].tolist():
               resDf001.loc[dummy_resDfindex,['买入数量','买入金额','买入成交均价']] = buy_orderDf_jupiter_info001.loc[stock_code][['deal_vol','deal_amt','deal_vwap']].values
            else:
               resDf001.loc[dummy_resDfindex, '买入数量'] = float(buy_orderDf_jupiter_info001.loc[stock_code]['deal_vol'])- float(resDf[(resDf['买入日期']==Adate)&(resDf['证券代码']==stock_code)]['买入数量'])
               resDf001.loc[dummy_resDfindex,  '买入金额'] = float(buy_orderDf_jupiter_info001.loc[stock_code]['deal_amt'])- float(resDf[(resDf['买入日期'] == Adate) & (resDf['证券代码'] == stock_code)][ '买入金额'])
            '''sel_order = buy_orderDf_jupiter001[((buy_orderDf_jupiter001['ordStatus'] == 'PARTIALLY_FILLED') | (
                    buy_orderDf_jupiter001['ordStatus'] == 'FILLED')) & (
                                                    buy_orderDf_jupiter001['stockcode'] == stock_code)]
            resDf001.loc[dummy_resDfindex, ['买入数量', '买入金额']] = sel_order[['lastQty', 'lastAmt']].sum().values'''
            resDf001.loc[dummy_resDfindex, '买入成交均价'] = resDf001.loc[dummy_resDfindex, '买入金额'] / resDf001.loc[dummy_resDfindex, '买入数量']
        buyExtraColumns = ['买入当天开盘涨幅(%)','买入当天开盘价','买入当天盘中是否涨停']

        for index,row in buyDf_saturn.iterrows():
            dummy_resDfpj2_index = len(resDf_pj2)
            stock_code = row['证券代码']
            if stock_code in list(signal_info_pj2_930['Unnamed: 0']):
                signal_pj2_930 = False#signal_info_pj2_930[signal_info_pj2_930['Unnamed: 0']==stock_code]['p2shouldBuySignal'].values[0] == True
            else: signal_pj2_930 = False
            if len(signal_info_pj2_931) != 0:
                if stock_code in list(signal_info_pj2_931['Unnamed: 0']):
                    signal_pj2_931 = signal_info_pj2_931[signal_info_pj2_931['Unnamed: 0']==stock_code]['p2shouldBuySignal'].values[0] == True
                else: signal_pj2_931 = False
            else: signal_pj2_931 = False
            if signal_pj2_930:
                if (not signal_pj2_931) | (len(buy_orderDf[(buy_orderDf['stockcode'] == stock_code) & (buy_orderDf['buy_Time']>='0931')]) != 0):
                    resDf_pj2.loc[dummy_resDfpj2_index,buy_commonInfoColumns_rename+buyExtraColumns] = row[buy_commonInfoColumns+buyExtraColumns].values
                    resDf_pj2.loc[dummy_resDfpj2_index,['买入数量','买入金额','买入成交均价']] = buy_orderDf_saturn_info.loc[stock_code][['deal_vol','deal_amt','deal_vwap']].values
                    resDf_pj2.loc[dummy_resDfpj2_index, ['买入时点']] = '930'
                else:
                    tot_vol, tot_amt , tot_vwap = buy_orderDf_saturn_info.loc[stock_code][['deal_vol','deal_amt','deal_vwap']].values
                    post_931_info = buy_orderDf[(buy_orderDf['stockcode'] == stock_code) & (buy_orderDf['buy_Time']>='0931')]
                    post_931_amt, post_931_vol, post_931_vwap = get_buy_amt_volume(post_931_info)
                    pre_931_amt, pre_931_vol, pre_931_vwap = tot_amt - post_931_amt, tot_vol - post_931_vol,(tot_amt - post_931_amt) / (tot_vol - post_931_vol)
                    resDf_pj2.loc[dummy_resDfpj2_index,buy_commonInfoColumns_rename+buyExtraColumns] = row[buy_commonInfoColumns+buyExtraColumns].values
                    resDf_pj2.loc[dummy_resDfpj2_index,['买入数量','买入金额','买入成交均价']] = np.array([pre_931_vol, pre_931_amt, pre_931_vwap])
                    resDf_pj2.loc[dummy_resDfpj2_index, ['买入时点']] = '930'
                    if post_931_amt != 0:
                        pj2_extra_index = dummy_resDfpj2_index + 1
                        resDf_pj2.loc[pj2_extra_index,buy_commonInfoColumns_rename+buyExtraColumns] = row[buy_commonInfoColumns+buyExtraColumns].values
                        resDf_pj2.loc[pj2_extra_index,['买入数量','买入金额','买入成交均价']] = np.array([post_931_vol, post_931_amt, post_931_vwap])
                        resDf_pj2.loc[pj2_extra_index, ['买入时点']] = '931'
            else:
                resDf_pj2.loc[dummy_resDfpj2_index, buy_commonInfoColumns_rename + buyExtraColumns] = row[buy_commonInfoColumns + buyExtraColumns].values
                resDf_pj2.loc[dummy_resDfpj2_index, ['买入数量','买入金额','买入成交均价']] = buy_orderDf_saturn_info.loc[stock_code][['deal_vol', 'deal_amt', 'deal_vwap']].values
                resDf_pj2.loc[dummy_resDfpj2_index, ['买入时点']] = '931'
        if len(resDf_pj3) == 0:
            resDf_pj3 = pd.DataFrame(columns = resDf_pj2.columns.tolist())
        for index, row in buyDf_ceres.iterrows():
            dummy_resDfpj3_index = len(resDf_pj3)
            stock_code = row['证券代码']
            signal_pj3_930 = False
            # if stock_code in list(signal_info_pj3_930['Unnamed: 0']):
            #     signal_pj2_930 = \
            #     signal_info_pj2_930[signal_info_pj2_930['Unnamed: 0'] == stock_code]['p2shouldBuySignal'].values[
            #         0] == True
            # else:
            #     signal_pj2_930 = False
            if len(signal_info_pj3_931) != 0:
                if stock_code in list(signal_info_pj3_931['Unnamed: 0']):
                    signal_pj3_931 = signal_info_pj3_931[signal_info_pj3_931['Unnamed: 0'] == stock_code]['p3shouldBuySignal'].values[0] == True
                else:
                    signal_pj3_931 = False
            else:
                signal_pj3_931 = False
            if signal_pj3_930:
                print('！！！！！！！！！！should not enter this place！！！！！！！！！！')
                if (not signal_pj3_931) | (len(buy_orderDf[(buy_orderDf['stockcode'] == stock_code) & (
                        buy_orderDf['buy_Time'] >= '0931')]) != 0):
                    resDf_pj3.loc[dummy_resDfpj3_index, buy_commonInfoColumns_rename + buyExtraColumns] = row[
                        buy_commonInfoColumns + buyExtraColumns].values
                    resDf_pj3.loc[dummy_resDfpj3_index, ['买入数量', '买入金额', '买入成交均价']] = \
                    buy_orderDf_ceres_info.loc[stock_code][['deal_vol', 'deal_amt', 'deal_vwap']].values
                    resDf_pj3.loc[dummy_resDfpj3_index, ['买入时点']] = '930'
                else:
                    tot_vol, tot_amt, tot_vwap = buy_orderDf_ceres_info.loc[stock_code][
                        ['deal_vol', 'deal_amt', 'deal_vwap']].values
                    post_931_info = buy_orderDf[
                        (buy_orderDf['stockcode'] == stock_code) & (buy_orderDf['buy_Time'] >= '0931')]
                    post_931_amt, post_931_vol, post_931_vwap = get_buy_amt_volume(post_931_info)
                    pre_931_amt, pre_931_vol, pre_931_vwap = tot_amt - post_931_amt, tot_vol - post_931_vol, (
                                tot_amt - post_931_amt) / (tot_vol - post_931_vol)
                    resDf_pj3.loc[dummy_resDfpj3_index, buy_commonInfoColumns_rename + buyExtraColumns] = row[
                        buy_commonInfoColumns + buyExtraColumns].values
                    resDf_pj3.loc[dummy_resDfpj3_index, ['买入数量', '买入金额', '买入成交均价']] = np.array(
                        [pre_931_vol, pre_931_amt, pre_931_vwap])
                    resDf_pj3.loc[dummy_resDfpj3_index, ['买入时点']] = '930'
                    if post_931_amt != 0:
                        pj3_extra_index = dummy_resDfpj3_index + 1
                        resDf_pj3.loc[pj3_extra_index, buy_commonInfoColumns_rename + buyExtraColumns] = row[
                            buy_commonInfoColumns + buyExtraColumns].values
                        resDf_pj3.loc[pj3_extra_index, ['买入数量', '买入金额', '买入成交均价']] = np.array(
                            [post_931_vol, post_931_amt, post_931_vwap])
                        resDf_pj3.loc[pj3_extra_index, ['买入时点']] = '931'
            else:
                resDf_pj3.loc[dummy_resDfpj3_index, buy_commonInfoColumns_rename + buyExtraColumns] = row[
                    buy_commonInfoColumns + buyExtraColumns].values
                resDf_pj3.loc[dummy_resDfpj3_index, ['买入数量', '买入金额', '买入成交均价']] = \
                buy_orderDf_ceres_info.loc[stock_code][['deal_vol', 'deal_amt', 'deal_vwap']].values
                resDf_pj3.loc[dummy_resDfpj3_index, ['买入时点']] = '931'
        return resDf[resDf['买入数量']>0], resDf_pj2,resDf_pj3,resDf001[resDf001['买入数量']>0]

    resDf1, resDf1_pj2,resDf1_pj3,resDf1001 = updatePositionBuy(todayBuyDf.copy(),historySellDf.copy(),historySellDf_pj2.copy(),historySellDf_pj3.copy(),logDf,buy_orderDf,historySellDf001.copy())
    print('updatePositionBuy:resdf1:', resDf1.shape,resDf1.iloc[0])
    print('updatePositionBuy:resdf1New:', resDf1001.shape, resDf1001.iloc[0])
    h_resDf1,h_resDf1_pj2,h_resDf1_pj3,h_resDf1001 = resDf1.copy(),resDf1_pj2.copy(),resDf1_pj3.copy(),resDf1001.copy()
    # resDf1,resDf1_pj2 = h_resDf1.copy(),h_resDf1_pj2.copy()
    sellDf = todaySellDf.copy()
    def updatePositionSell(sellDf,resDf1,resDf1_pj2,resDf1_pj3,date,resDf1001):
        sellCommonColumns = ['卖出日期','卖出成交均价','卖出日期开盘价']
        sellDf['证券代码'] = sellDf['证券代码'].apply(number2stockcode)
        sellDf = getExtraSellInfo(sellDf)
        resDf1.replace(np.nan,'',inplace=True)
        resDf1001.replace(np.nan, '', inplace=True)
        resDf1_pj2.replace(np.nan,'',inplace=True)
        if len(resDf1_pj3)==0:
            resDf1_pj3 = pd.DataFrame(columns = resDf1_pj2.columns.tolist())
        resDf1_pj3.replace(np.nan, '', inplace=True)
        market_volume = IO.read_data([date, date], columns=['volume']
                                     , alt=IO_mother_dir + '/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
        for index,row in sellDf.iterrows():
            stockCode = row['证券代码']
            print(index,stockCode)
            sold_qty = sellDf.loc[index, '成交数量']
            def jupiter_sell_one_day_holding(sold_qty, resDf1):  # 对一天的jupiter进行卖出
                historyIndex = resDf1[(resDf1['证券代码'] == stockCode) & (resDf1['是否全部卖出'] != 1)].index[0]
                totalSold_indicator = resDf1.loc[historyIndex]['是否全部卖出']
                if resDf1.loc[historyIndex, '总卖出数量'] == '':
                    sold_already = 0
                else:
                    sold_already = resDf1.loc[historyIndex, '总卖出数量']
                qty_allocate_here = min((int(resDf1.loc[historyIndex, '买入数量']) - sold_already), sold_qty)
                if totalSold_indicator == '':  # 没卖出过
                    resDf1.loc[historyIndex, sellCommonColumns] = sellDf.loc[index, CommonInfoColumns].values
                    resDf1.loc[historyIndex, '卖出数量'] = qty_allocate_here
                    resDf1.loc[historyIndex, '卖出金额'] = qty_allocate_here * sellDf.loc[index, '成交均价']
                    resDf1.loc[historyIndex, '总卖出数量'] = qty_allocate_here
                    resDf1.loc[historyIndex, '卖出金额占市场比'] = qty_allocate_here / market_volume['volume'].loc[date,stockCode]
                elif totalSold_indicator == 0:  # 之前未全部卖出
                    resDf1.loc[historyIndex, '卖出日期'] += ',' + str(sellDf.loc[index, '发生日期'])
                    resDf1.loc[historyIndex, '卖出数量'] = str(resDf1.loc[historyIndex, '卖出数量']) + ',' + str(qty_allocate_here)
                    resDf1.loc[historyIndex, '卖出成交均价'] = str(resDf1.loc[historyIndex, '卖出成交均价']) + ',' + str(sellDf.loc[index, '成交均价'])
                    resDf1.loc[historyIndex, '卖出金额'] = str(resDf1.loc[historyIndex, '卖出金额']) + ',' + str(qty_allocate_here * sellDf.loc[index, '成交均价'])
                    resDf1.loc[historyIndex, '卖出日期开盘价'] = str(resDf1.loc[historyIndex, '卖出日期开盘价']) + ',' + str(sellDf.loc[index, '卖出日期开盘价'])
                    resDf1.loc[historyIndex, '总卖出数量'] = resDf1.loc[historyIndex, '总卖出数量'] + qty_allocate_here
                    resDf1.loc[historyIndex, '卖出金额占市场比'] = str(resDf1.loc[historyIndex, '卖出金额占市场比']) + ',' + str(qty_allocate_here / market_volume['volume'].loc[date,stockCode])
                if resDf1.loc[historyIndex, '总卖出数量'] == resDf1.loc[historyIndex, '买入数量']:
                    resDf1.loc[historyIndex, '是否全部卖出'] = 1
                volume_left_to_be_sell = sold_qty - qty_allocate_here
                return volume_left_to_be_sell, resDf1

            def saturn_sell_one_day_holding(sold_qty, resDf1_pj2):  # 对一天的saturn进行卖出
                historyIndex = resDf1_pj2[(resDf1_pj2['证券代码'] == stockCode) & (resDf1_pj2['是否全部卖出'] != 1)].index[0]
                totalSold_indicator = resDf1_pj2.loc[historyIndex]['是否全部卖出']
                if resDf1_pj2.loc[historyIndex, '总卖出数量'] == '':
                    sold_already = 0
                else:
                    sold_already = resDf1_pj2.loc[historyIndex, '总卖出数量']
                qty_allocate_here = min((int(resDf1_pj2.loc[historyIndex, '买入数量']) - sold_already), sold_qty)
                if totalSold_indicator == '':  # 没卖出过
                    resDf1_pj2.loc[historyIndex, sellCommonColumns] = sellDf.loc[index, CommonInfoColumns].values
                    resDf1_pj2.loc[historyIndex, '卖出数量'] = qty_allocate_here
                    resDf1_pj2.loc[historyIndex, '卖出金额'] = qty_allocate_here * sellDf.loc[index, '成交均价']
                    resDf1_pj2.loc[historyIndex, '总卖出数量'] = qty_allocate_here
                    resDf1_pj2.loc[historyIndex, '卖出金额占市场比'] = qty_allocate_here / market_volume['volume'].loc[date,stockCode]
                elif totalSold_indicator == 0:  # 之前未全部卖出
                    resDf1_pj2.loc[historyIndex, '卖出日期'] += ',' + str(sellDf.loc[index, '发生日期'])
                    resDf1_pj2.loc[historyIndex, '卖出数量'] = str(resDf1_pj2.loc[historyIndex, '卖出数量']) + ',' + str(qty_allocate_here)
                    resDf1_pj2.loc[historyIndex, '卖出成交均价'] = str(resDf1_pj2.loc[historyIndex, '卖出成交均价']) + ',' + str(sellDf.loc[index, '成交均价'])
                    resDf1_pj2.loc[historyIndex, '卖出金额'] = str(resDf1_pj2.loc[historyIndex, '卖出金额']) + ',' + str(
                        qty_allocate_here * sellDf.loc[index, '成交均价'])
                    resDf1_pj2.loc[historyIndex, '卖出日期开盘价'] = str(resDf1_pj2.loc[historyIndex, '卖出日期开盘价']) + ',' + str(sellDf.loc[index, '卖出日期开盘价'])
                    resDf1_pj2.loc[historyIndex, '总卖出数量'] = resDf1_pj2.loc[historyIndex, '总卖出数量'] + qty_allocate_here
                    resDf1_pj2.loc[historyIndex, '卖出金额占市场比'] = str(resDf1_pj2.loc[historyIndex, '卖出金额占市场比']) + ',' + str(qty_allocate_here / market_volume['volume'].loc[date,stockCode])
                if resDf1_pj2.loc[historyIndex, '总卖出数量'] == resDf1_pj2.loc[historyIndex, '买入数量']:
                    resDf1_pj2.loc[historyIndex, '是否全部卖出'] = 1
                volume_left_to_be_sell = sold_qty - qty_allocate_here
                return volume_left_to_be_sell, resDf1_pj2
            volume_left_to_be_sell = sold_qty
             ## 需要细致修改
            while volume_left_to_be_sell > 1e-5:
                if stockCode == '002063.SZ':
                    print('debug!!')
                if len(resDf1[(resDf1['证券代码'] == stockCode) & (resDf1['是否全部卖出'] != 1)]['买入日期']) > 0:
                    jupiter_min_date = resDf1[(resDf1['证券代码'] == stockCode) & (resDf1['是否全部卖出'] != 1)]['买入日期'].min()
                else:
                    jupiter_min_date= '2030-12-31'
                if len(resDf1001[(resDf1001['证券代码'] == stockCode) & (resDf1001['是否全部卖出'] != 1)]['买入日期']) > 0:
                    jupiter_min_date001 = resDf1001[(resDf1001['证券代码'] == stockCode) & (resDf1001['是否全部卖出'] != 1)]['买入日期'].min()
                else:
                    jupiter_min_date001 = '2030-12-31'
                if len(resDf1_pj2[(resDf1_pj2['证券代码'] == stockCode) & (resDf1_pj2['是否全部卖出'] != 1)]['买入日期'])>0:
                    saturn_min_date = resDf1_pj2[(resDf1_pj2['证券代码'] == stockCode) & (resDf1_pj2['是否全部卖出'] != 1)]['买入日期'].min()
                else:
                    saturn_min_date = '2030-12-31'
                if len(resDf1_pj3[(resDf1_pj3['证券代码'] == stockCode) & (resDf1_pj3['是否全部卖出'] != 1)]['买入日期'])>0:
                    ceres_min_date = resDf1_pj3[(resDf1_pj3['证券代码'] == stockCode) & (resDf1_pj3['是否全部卖出'] != 1)]['买入日期'].min()
                else:
                    ceres_min_date = '2030-12-31'#pd.DataFrame(columns = resDf2_pj2.columns.tolist())
                if (len(resDf1[(resDf1['证券代码'] == stockCode) & (resDf1['是否全部卖出'] != 1)&(resDf1['买入日期'] != Adate)]['买入日期'])>0)and (len(resDf1001[(resDf1001['证券代码'] == stockCode) & (resDf1001['是否全部卖出'] != 1)&(resDf1001['买入日期'] != Adate)]['买入日期']) == 0) and (len(resDf1_pj2[(resDf1_pj2['证券代码'] == stockCode) & (resDf1_pj2['是否全部卖出'] != 1)&(resDf1_pj2['买入日期'] != Adate)]['买入日期']) == 0) and (len(resDf1_pj3[(resDf1_pj3['证券代码'] == stockCode) & (resDf1_pj3['是否全部卖出'] != 1)&(resDf1_pj3['买入日期'] != Adate)]['买入日期']) == 0):
                    print('该标的%s只有jup存在持仓'%str(stockCode))
                    volume_left_to_be_sell, resDf1 = jupiter_sell_one_day_holding(volume_left_to_be_sell, resDf1)
                #elif (len(resDf1[(resDf1['证券代码'] == stockCode) & (resDf1['是否全部卖出'] != 1)&(resDf1['买入日期'] != Adate)]['买入日期']) == 0) and (len(resDf1_pj2[(resDf1_pj2['证券代码'] == stockCode) & (resDf1_pj2['是否全部卖出'] != 1)&(resDf1_pj2['买入日期'] != Adate)]['买入日期']) == 0) and (len(resDf1_pj3[(resDf1_pj3['证券代码'] == stockCode) & (resDf1_pj3['是否全部卖出'] != 1)&(resDf1_pj3['买入日期'] != Adate)]['买入日期']) == 0):
                elif (len(resDf001[(resDf1001['证券代码'] == stockCode) & (resDf001['是否全部卖出'] != 1)&(resDf001['买入日期'] != Adate)]['买入日期'])>0) and (len(resDf1[(resDf1['证券代码'] == stockCode) & (resDf1['是否全部卖出'] != 1)&(resDf1['买入日期'] != Adate)]['买入日期']) == 0) and (len(resDf1_pj2[(resDf1_pj2['证券代码'] == stockCode) & (resDf1_pj2['是否全部卖出'] != 1)&(resDf1_pj2['买入日期'] != Adate)]['买入日期']) == 0) and (len(resDf1_pj3[(resDf1_pj3['证券代码'] == stockCode) & (resDf1_pj3['是否全部卖出'] != 1)&(resDf1_pj3['买入日期'] != Adate)]['买入日期']) == 0):
                    print('该标的%s只有jupNew存在持仓'%str(stockCode))
                    if stockCode=='600085.SH':
                        print('pASS!!!')
                    volume_left_to_be_sell, resDf1001 = jupiter_sell_one_day_holding(volume_left_to_be_sell, resDf1001)
                elif (len(resDf1001[(resDf1001['证券代码'] == stockCode) & (resDf1001['是否全部卖出'] != 1)&(resDf1001['买入日期'] != Adate)]['买入日期']) == 0) and (len(resDf1[(resDf1['证券代码'] == stockCode) & (resDf1['是否全部卖出'] != 1)&(resDf1['买入日期'] != Adate)]['买入日期']) == 0) and (len(resDf1_pj3[(resDf1_pj3['证券代码'] == stockCode) & (resDf1_pj3['是否全部卖出'] != 1)&(resDf1_pj3['买入日期'] != Adate)]['买入日期']) == 0)and (len(resDf1_pj2[(resDf1_pj2['证券代码'] == stockCode) & (resDf1_pj2['是否全部卖出'] != 1)&(resDf1_pj2['买入日期'] != Adate)]['买入日期']) > 0) :
                    print('该标的%s只有sat存在持仓' % str(stockCode))
                    volume_left_to_be_sell, resDf1_pj2 = saturn_sell_one_day_holding(volume_left_to_be_sell, resDf1_pj2)
                elif (len(resDf1001[(resDf1001['证券代码'] == stockCode) & (resDf1001['是否全部卖出'] != 1)&(resDf1001['买入日期'] != Adate)]['买入日期']) == 0) and (len(resDf1[(resDf1['证券代码'] == stockCode) & (resDf1['是否全部卖出'] != 1)&(resDf1['买入日期'] != Adate)&(resDf1['买入日期'] != Adate)]['买入日期']) == 0) and (len(resDf1_pj2[(resDf1_pj2['证券代码'] == stockCode) & (resDf1_pj2['是否全部卖出'] != 1)&(resDf1_pj2['买入日期'] != Adate)]['买入日期']) == 0)and (len(resDf1_pj3[(resDf1_pj3['证券代码'] == stockCode) & (resDf1_pj3['是否全部卖出'] != 1)&(resDf1_pj3['买入日期'] != Adate)]['买入日期']) > 0) :
                    print('该标的%s只有ceres存在持仓' % str(stockCode))
                    volume_left_to_be_sell, resDf1_pj3 = saturn_sell_one_day_holding(volume_left_to_be_sell, resDf1_pj3)
                else:
                    print('！！！！！！！！！！ should not enter this place！！！！！！！！！！')
                    # 该标的至少2个策略存在持仓,先卖早买入的部分
                    if (jupiter_min_date<saturn_min_date) and (jupiter_min_date<ceres_min_date) and (jupiter_min_date<jupiter_min_date001) :
                        volume_left_to_be_sell, resDf1 = jupiter_sell_one_day_holding(volume_left_to_be_sell, resDf1)
                    elif (jupiter_min_date001<saturn_min_date) and (jupiter_min_date001<ceres_min_date) and (jupiter_min_date001<jupiter_min_date) :
                        volume_left_to_be_sell, resDf1001 = jupiter_sell_one_day_holding(volume_left_to_be_sell, resDf1001)
                    elif (saturn_min_date<jupiter_min_date) and (saturn_min_date<ceres_min_date) and (saturn_min_date < jupiter_min_date001):
                        volume_left_to_be_sell, resDf1_pj2 = saturn_sell_one_day_holding(volume_left_to_be_sell, resDf1_pj2)
                    elif (ceres_min_date<jupiter_min_date) and (ceres_min_date<saturn_min_date)and (ceres_min_date < jupiter_min_date001):
                        volume_left_to_be_sell, resDf1_pj3 = saturn_sell_one_day_holding(volume_left_to_be_sell, resDf1_pj3)
                    elif (jupiter_min_date<saturn_min_date) and (jupiter_min_date<ceres_min_date) and (jupiter_min_date==jupiter_min_date001):
                        volume_left_to_be_sell, resDf1001 = jupiter_sell_one_day_holding(volume_left_to_be_sell, resDf1001)
                    else:
                        print('error!')
                        print('jupiter mindate:%s, jupiterNew mindate:%s, saturn mindate:%s, ceres mindate:%s'%(str(jupiter_min_date),str(jupiter_min_date001),str(saturn_min_date),str(ceres_min_date)))
                        break
        return resDf1, resDf1_pj2,resDf1_pj3,resDf1001


    resDf2, resDf2_pj2, resDf2_pj3, resDf2001 = updatePositionSell(todaySellDf.copy(), resDf1, resDf1_pj2, resDf1_pj3, date, resDf1001)
    print('updatePositionSell:resdf2:', resDf2.shape,resDf2.iloc[0])
    resDf2.replace('', np.nan, inplace=True)
    resDf2001.replace('', np.nan, inplace=True)
    resDf2_pj2.replace('', np.nan, inplace=True)
    resDf2_pj3.replace('', np.nan, inplace=True)

    # --------------------------添加JupiterNew买入形态和o2ul信息------------------------------
    if True in resDf2001['买入时形态'].isnull():
        unfilled_pattern = resDf2001[resDf2001['买入时形态'].isnull()]
        for index,row in unfilled_pattern.iterrows():
            stock_code,pre_date = row[['证券代码','买入日期']].values
            pre_date = pre_date[0:4]+pre_date[5:7]+pre_date[8:]
            print(stock_code,pre_date)
            pre_close, close,ul_price = IO.read_data([pre_date, pre_date], columns=['pre_close', 'close','high']
                ,alt=IO_mother_dir + '/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5').loc[pre_date, stock_code].values
            resDf2001.loc[index,'买入时形态'] = cal_Basic_zt(mdp, stock_code, pre_date, pre_close, close)['label_pattern'].values[0]

    # --------------------------添加Jupiter买入形态和o2ul信息------------------------------
    if True in resDf2['买入时形态'].isnull():
        unfilled_pattern = resDf2[resDf2['买入时形态'].isnull()]
        for index, row in unfilled_pattern.iterrows():
            stock_code, pre_date = row[['证券代码', '买入日期']].values
            pre_date = pre_date[0:4] + pre_date[5:7] + pre_date[8:]
            print(stock_code, pre_date)
            pre_close, close, ul_price = IO.read_data([pre_date, pre_date], columns=['pre_close', 'close', 'high']
                                                      ,
                                                      alt=IO_mother_dir + '/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5').loc[
                pre_date, stock_code].values
            if stock_code in resDf2001[resDf2001['买入日期']==pre_date]['证券代码'].tolist():
                resDf2.loc[index, '买入时形态'] = resDf2001[(resDf2001['证券代码']==stock_code)&(resDf2001['买入日期']==pre_date)]['买入时形态'].values[0]
            else:
                resDf2.loc[index, '买入时形态'] = cal_Basic_zt(mdp, stock_code, pre_date, pre_close, close)['label_pattern'].values[0]

    #----------给resDf2001和resDf2添加TN_o2ul列，给resDf2_pj2和resDf2_pj3添加TN_v2o10列------------
    if 'TN_o2ul' not in resDf2001.columns:
        resDf2001['TN_o2ul'] = np.nan
    o2ul_nan_samples001 = resDf2001[resDf2001['TN_o2ul'].isnull()]

    if len(o2ul_nan_samples001)!=0:
        date_ini = o2ul_nan_samples001['买入日期'].apply(lambda x: x[:4] + x[5:7] + x[8:10]).min()
        end_date = o2ul_nan_samples001['买入日期'].apply(lambda x: x[:4] + x[5:7] + x[8:10]).max()
        end_date_ = int(s.tradingday(end_date, 30)[-1])
        md_data = IO.read_data([date_ini, end_date_], columns=['pre_close', 'open', 'high', 'low','close','vwap', 'adjfactor'],
                                    alt=IO_mother_dir+'/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
        md_data['ul_price'] = np.floor(md_data['pre_close'] * 100 * 1.1 + 0.5) / 100
        md_deal_temp = md_data.reset_index()
        md_deal_temp = md_deal_temp[md_deal_temp['Ticker'].apply(lambda x:x[0]=='3') & (md_deal_temp['dt']>='20200824')].set_index(['dt','Ticker'])
        md_data['ul_price'].loc[md_deal_temp.index] = np.floor(md_deal_temp['pre_close'] * 100 * 1.2 + 0.5) / 100
        md_data['open'], md_data['close'] = md_data['open'] * md_data['adjfactor'], md_data['close'] * md_data['adjfactor']
        md_data['vwap'], md_data['pre_close'] = md_data['vwap'] * md_data['adjfactor'], md_data['pre_close'] * md_data['adjfactor']
        md_data['high'], md_data['low'] = md_data['high'] * md_data['adjfactor'], md_data['low'] * md_data['adjfactor']
        md_data['ul_price'] = md_data['ul_price'] * md_data['adjfactor']
        md_data['label_T_o2ul'] = md_data['open'].unstack().shift(-1).stack() / md_data['ul_price'] - 1
        md_data.loc[md_data['high'] == md_data['low'], 'open'] = np.nan
        md_data.loc[md_data['high'] == md_data['low'], 'vwap'] = np.nan
        md_data['next_open'] = md_data['open'].unstack().shift(-1).stack()
        md_data['next_vwap'] = md_data['vwap'].unstack().shift(-1).stack()
        md_data['next_open'] = md_data['next_open'].unstack().fillna(method='bfill', axis=0).stack()
        md_data['next_vwap'] = md_data['next_vwap'].unstack().fillna(method='bfill', axis=0).stack()
        md_data['label_TN_o2ul'] = md_data['next_open'] / md_data['ul_price'] - 1
        resDf2001_copy = resDf2001.copy()
        resDf2001_copy['买入日期'] = resDf2001_copy['买入日期'].apply(lambda x:pd.Timestamp(x[:4]+x[5:7]+x[8:10]))
        for i in o2ul_nan_samples001.index:
            buy_date = resDf2001.loc[i]['买入日期']
            stock = resDf2001.loc[i]['证券代码']
            resDf2001.loc[i,'TN_o2ul'] = 100*md_data.reindex(resDf2001_copy.rename(columns = {'买入日期':'dt',
                                      '证券代码':'Ticker'}).set_index(['dt','Ticker']).index)['label_TN_o2ul'].loc[buy_date,stock]

    if 'TN_o2ul' not in resDf2.columns:
        resDf2['TN_o2ul'] = np.nan
    o2ul_nan_samples = resDf2[resDf2['TN_o2ul'].isnull()]

    if len(o2ul_nan_samples)!=0:
        date_ini = o2ul_nan_samples['买入日期'].apply(lambda x: x[:4] + x[5:7] + x[8:10]).min()
        end_date = o2ul_nan_samples['买入日期'].apply(lambda x: x[:4] + x[5:7] + x[8:10]).max()
        end_date_ = int(s.tradingday(end_date, 30)[-1])
        md_data = IO.read_data([date_ini, end_date_], columns=['pre_close', 'open', 'high', 'low','close','vwap', 'adjfactor'],
                                    alt=IO_mother_dir+'/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
        md_data['ul_price'] = np.floor(md_data['pre_close'] * 100 * 1.1 + 0.5) / 100
        md_deal_temp = md_data.reset_index()
        md_deal_temp = md_deal_temp[md_deal_temp['Ticker'].apply(lambda x:x[0]=='3') & (md_deal_temp['dt']>='20200824')].set_index(['dt','Ticker'])
        md_data['ul_price'].loc[md_deal_temp.index] = np.floor(md_deal_temp['pre_close'] * 100 * 1.2 + 0.5) / 100
        md_data['open'], md_data['close'] = md_data['open'] * md_data['adjfactor'], md_data['close'] * md_data['adjfactor']
        md_data['vwap'], md_data['pre_close'] = md_data['vwap'] * md_data['adjfactor'], md_data['pre_close'] * md_data['adjfactor']
        md_data['high'], md_data['low'] = md_data['high'] * md_data['adjfactor'], md_data['low'] * md_data['adjfactor']
        md_data['ul_price'] = md_data['ul_price'] * md_data['adjfactor']
        md_data['label_T_o2ul'] = md_data['open'].unstack().shift(-1).stack() / md_data['ul_price'] - 1
        md_data.loc[md_data['high'] == md_data['low'], 'open'] = np.nan
        md_data.loc[md_data['high'] == md_data['low'], 'vwap'] = np.nan
        md_data['next_open'] = md_data['open'].unstack().shift(-1).stack()
        md_data['next_vwap'] = md_data['vwap'].unstack().shift(-1).stack()
        md_data['next_open'] = md_data['next_open'].unstack().fillna(method='bfill', axis=0).stack()
        md_data['next_vwap'] = md_data['next_vwap'].unstack().fillna(method='bfill', axis=0).stack()
        md_data['label_TN_o2ul'] = md_data['next_open'] / md_data['ul_price'] - 1
        resDf2_copy = resDf2.copy()
        resDf2_copy['买入日期'] = resDf2_copy['买入日期'].apply(lambda x:pd.Timestamp(x[:4]+x[5:7]+x[8:10]))
        for i in o2ul_nan_samples.index:
            buy_date = resDf2.loc[i]['买入日期']
            stock = resDf2.loc[i]['证券代码']
            resDf2.loc[i,'TN_o2ul'] = 100*md_data.reindex(resDf2_copy.rename(columns = {'买入日期':'dt',
                                      '证券代码':'Ticker'}).set_index(['dt','Ticker']).index)['label_TN_o2ul'].loc[buy_date,stock]

    if 'TN_v2o10' not in resDf2_pj2.columns:
        resDf2_pj2['TN_v2o10'] = np.nan
    v2o10_nan_samples_not_today = resDf2_pj2[resDf2_pj2['TN_v2o10'].isnull() & (resDf2_pj2['买入日期']!=Adate)]
    if len(v2o10_nan_samples_not_today) !=0:
        date_ini = v2o10_nan_samples_not_today['买入日期'].apply(lambda x:x[:4]+x[5:7]+x[8:10]).min()
        end_date = v2o10_nan_samples_not_today['买入日期'].apply(lambda x:x[:4]+x[5:7]+x[8:10]).max()
        end_date_ = int(s.tradingday(end_date, 30)[-1])
        md_data = IO.read_data([date_ini, end_date_], columns=['pre_close', 'open', 'high', 'low','close','vwap', 'adjfactor'],
                                    alt=IO_mother_dir+'/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
        md_data['ul_price'] = np.floor(md_data['pre_close'] * 100 * 1.1 + 0.5) / 100
        md_deal_temp = md_data.reset_index()
        md_deal_temp = md_deal_temp[md_deal_temp['Ticker'].apply(lambda x: x[0] == '3') & (md_deal_temp['dt'] >= '20200824')].set_index(['dt', 'Ticker'])
        md_data['ul_price'].loc[md_deal_temp.index] = np.floor(md_deal_temp['pre_close'] * 100 * 1.2 + 0.5) / 100
        md_data['vwap'], md_data['pre_close'] = md_data['vwap'] * md_data['adjfactor'], md_data['pre_close'] * md_data['adjfactor']
        md_data['high'], md_data['low'] = md_data['high'] * md_data['adjfactor'], md_data['low'] * md_data['adjfactor']
        md_data['ul_price'] = md_data['ul_price'] * md_data['adjfactor']
        md_data.loc[md_data['high'] == md_data['low'], 'vwap'] = np.nan
        md_data['next_vwap'] = md_data['vwap'].unstack().shift(-1).fillna(method='bfill', axis=0).stack()
        for index, row in v2o10_nan_samples_not_today.iterrows():
            stock = row['证券代码']
            buy_A_date = row['买入日期']
            buy_date = buy_A_date[0:4]+buy_A_date[5:7]+buy_A_date[8:10]
            #saturn_basic_hf_info = pd.read_hdf('/data/group/800463/project/project2_prod/everyday_Basic_v2/%s_%s/Basic_closed_hf_finish_%s_%s.h5' % (buy_date, buy_date, buy_date, buy_date))
            saturn_basic_hf_info = pd.read_hdf('/data/group/800463/project/project2_prod/daily_data/Basic/Basic_closed_hf_finish.h5')
            T_day_930_10_twap_before_ZT = saturn_basic_hf_info['T_day_930_10_twap_before_ZT'].loc[buy_date, stock]
            this_buy_price = md_data['adjfactor'].loc[buy_date,stock] * T_day_930_10_twap_before_ZT
            this_v2o10 = (md_data['next_vwap'].loc[buy_date,stock]/this_buy_price - 1)*100
            if T_day_930_10_twap_before_ZT == -1:
                this_v2o10 = -1
            if T_day_930_10_twap_before_ZT == -3:
                this_v2o10 = -3
            resDf2_pj2.loc[index,'TN_v2o10'] = this_v2o10

    if 'TN_v2o10d1' not in resDf2_pj3.columns:
        resDf2_pj3['TN_v2o10d1'] = np.nan
    v2o10_nan_samples_not_today = resDf2_pj3[resDf2_pj3['TN_v2o10d1'].isnull() & (resDf2_pj3['买入日期']!=Adate)]
    if len(v2o10_nan_samples_not_today) !=0:
        date_ini = v2o10_nan_samples_not_today['买入日期'].apply(lambda x:x[:4]+x[5:7]+x[8:10]).min()
        end_date = v2o10_nan_samples_not_today['买入日期'].apply(lambda x:x[:4]+x[5:7]+x[8:10]).max()
        end_date_ = int(s.tradingday(end_date, 30)[-1])
        md_data = IO.read_data([date_ini, end_date_], columns=['pre_close', 'open', 'high', 'low','close','vwap', 'adjfactor'],
                                    alt=IO_mother_dir+'/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
        md_data['ul_price'] = np.floor(md_data['pre_close'] * 100 * 1.1 + 0.5) / 100
        md_deal_temp = md_data.reset_index()
        md_deal_temp = md_deal_temp[md_deal_temp['Ticker'].apply(lambda x: x[0] == '3') & (md_deal_temp['dt'] >= '20200824')].set_index(['dt', 'Ticker'])
        md_data['ul_price'].loc[md_deal_temp.index] = np.floor(md_deal_temp['pre_close'] * 100 * 1.2 + 0.5) / 100
        md_data['vwap'], md_data['pre_close'] = md_data['vwap'] * md_data['adjfactor'], md_data['pre_close'] * md_data['adjfactor']
        md_data['high'], md_data['low'] = md_data['high'] * md_data['adjfactor'], md_data['low'] * md_data['adjfactor']
        md_data['ul_price'] = md_data['ul_price'] * md_data['adjfactor']
        md_data.loc[md_data['high'] == md_data['low'], 'vwap'] = np.nan
        md_data['next_vwap'] = md_data['vwap'].unstack().shift(-1).fillna(method='bfill', axis=0).stack()
        for index, row in v2o10_nan_samples_not_today.iterrows():
            stock = row['证券代码']
            buy_A_date = row['买入日期']
            buy_date = buy_A_date[0:4]+buy_A_date[5:7]+buy_A_date[8:10]
            ceres_basic_hf_info = pd.read_hdf('/data/group/800463/project/project3_prod/daily_data/%s_v2/Basic_closed_hf_finish_%s_%s.h5'
                                               % (buy_date, buy_date, buy_date))
            T_day_930_10_twap_before_ZT = ceres_basic_hf_info['T_day_931_10_twap_before_ZT'].loc[buy_date, stock]
            this_buy_price = md_data['adjfactor'].loc[buy_date,stock] * T_day_930_10_twap_before_ZT
            this_v2o10 = (md_data['next_vwap'].loc[buy_date,stock]/this_buy_price - 1)*100
            if T_day_930_10_twap_before_ZT == -1:
                this_v2o10 = -1
            if T_day_930_10_twap_before_ZT == -3:
                this_v2o10 = -3
            resDf2_pj3.loc[index,'TN_v2o10d1'] = this_v2o10
    # -------------------------------------------------

    # 计算收益情况
    resDf3 = calProfit(resDf2.copy())
    print('calProfit:resdf3:', resDf3.shape, resDf3.iloc[0])
    resDf3001 = calProfit(resDf2001.copy())
    print('calProfit:resdf3001:', resDf3001.shape, resDf3001.iloc[0])
    resDf3_pj2 = calProfit_pj2(resDf2_pj2.copy())
    resDf3_pj3 = calProfit_pj2(resDf2_pj3.copy(), 'ceres')
    resDf3.replace('', np.nan, inplace=True)
    resDf3001.replace('', np.nan, inplace=True)
    resDf3_pj2.replace('', np.nan, inplace=True)
    resDf3_pj3.replace('', np.nan, inplace=True)

    def cal_sum(data):
        if (type(data) == int) | (type(data) == np.int64):
            return float(data)
        elif type(data) == float:
            return data
        elif type(data) == str:
            data_list = data.split(',')
            total = 0
            for data in data_list:
                total += float(data)
            return total
        elif np.isnan(data):
            return data
        else:
            return data

    resDf3001['卖出比例'] = (resDf3001['卖出数量'].apply(cal_sum).astype(float)/resDf3001['买入数量']).fillna(0).apply(lambda x:'%.2f%%'%(x*100))
    resDf3001.replace(np.nan,'',inplace=True)
    resDf3['卖出比例'] = (resDf3['卖出数量'].apply(cal_sum).astype(float) / resDf3['买入数量']).fillna(0).apply(
        lambda x: '%.2f%%' % (x * 100))
    resDf3.replace(np.nan, '', inplace=True)
    resDf3_pj2['卖出比例'] = (resDf3_pj2['卖出数量'].apply(cal_sum).astype(float)/resDf3_pj2['买入数量']).fillna(0).apply(lambda x:'%.2f%%'%(x*100))
    resDf3_pj2.replace(np.nan,'',inplace=True)
    resDf3_pj3['卖出比例'] = (resDf3_pj3['卖出数量'].apply(cal_sum).astype(float) / resDf3_pj3['买入数量']).fillna(0).apply(lambda x: '%.2f%%' % (x * 100))
    resDf3_pj2.replace(np.nan, '', inplace=True)
    resDf3_pj3.replace(np.nan, '', inplace=True)

    # -----------------------------20230510 by fengc增加sell1、sell3信号模块---------------------------------------
    today_jup_signal = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate, sheet_name='因子耗时', index_col=0)
    today_jup_signal = today_jup_signal.loc[today_jup_signal.filter(regex='ZT.*?_probability').dropna(how='all', axis=0).index]
    today_jup001_signal = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate, sheet_name='因子耗时New')
    today_sell1_signal = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate, sheet_name='Sell1样本', index_col=0)
    today_sell3_signal = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate, sheet_name='Sell3样本', index_col=0)

    # 以下几行只在第一次20230509第一次加入这三列时使用，当前面的卖出记录有了这三列，后面就不用再加了，不然会覆盖前面的内容
    # resDf3['JupiterZ信号'] = ''
    # resDf3['Sell1信号'] = ''
    # resDf3['Sell3信号'] = ''
    #
    # resDf3001['JupiterZ信号'] = ''
    # resDf3001['Sell1信号'] = ''
    # resDf3001['Sell3信号'] = ''
    #
    # resDf3_pj2['JupiterZ信号'] = ''
    # resDf3_pj2['Sell1信号'] = ''
    # resDf3_pj2['Sell3信号'] = ''
    # resDf3_sold_signal_today = resDf3[resDf3['卖出日期'].apply(lambda x:Adate in x)] # 不能根据卖出日期进行筛选
    resDf3_holding_today = resDf3.loc[(resDf3['卖出日期'].apply(lambda x:Adate in x) | (resDf3['是否全部卖出'] != 1)) & (resDf3['买入日期'] != Adate)]
    for i in resDf3_holding_today.index:
        stk_code = resDf3_holding_today.loc[i, '证券代码']
        if stk_code in today_jup_signal.index:
            if not np.isnan(today_jup_signal.loc[stk_code, 'sum_signals']):
                if not resDf3.loc[i, 'JupiterZ信号']:
                    resDf3.loc[i, 'JupiterZ信号'] = str(int(today_jup_signal.loc[stk_code, 'sum_signals']))
                else:
                    resDf3.loc[i, 'JupiterZ信号'] = str(resDf3.loc[i, 'JupiterZ信号']) + ',' + str(int(today_jup_signal.loc[stk_code, 'sum_signals']))
        if stk_code in today_sell1_signal.index:
            if not np.isnan(today_sell1_signal.loc[stk_code, 'sum_signals']):
                if not resDf3.loc[i, 'Sell1信号']:
                    resDf3.loc[i, 'Sell1信号'] = str(int(today_sell1_signal.loc[stk_code, 'sum_signals']))
                else:
                    resDf3.loc[i, 'Sell1信号'] = str(resDf3.loc[i, 'Sell1信号']) + ',' + str(today_sell1_signal.loc[stk_code, 'sum_signals'])
        if stk_code in today_sell3_signal.index:
            if not np.isnan(today_sell3_signal.loc[stk_code, 'sum_signals']):
                if not resDf3.loc[i, 'Sell3信号']:
                    resDf3.loc[i, 'Sell3信号'] = str(int(today_sell3_signal.loc[stk_code, 'sum_signals']))
                else:
                    resDf3.loc[i, 'Sell3信号'] = str(resDf3.loc[i, 'Sell3信号']) + ',' + str(int(today_sell3_signal.loc[stk_code, 'sum_signals']))

    resDf3001_holding_today = resDf3001[resDf3001['卖出日期'].apply(lambda x: Adate in x) | ((resDf3001['是否全部卖出'] != 1) & (resDf3001['买入日期'] != Adate))]
    for i in resDf3001_holding_today.index:
        stk_code = resDf3001_holding_today.loc[i, '证券代码']
        if stk_code in today_jup_signal.index:
            if not np.isnan(today_jup_signal.loc[stk_code, 'sum_signals']):
                if not resDf3001.loc[i, 'JupiterZ信号']:  # 不为''
                    resDf3001.loc[i, 'JupiterZ信号'] = str(int(today_jup_signal.loc[stk_code, 'sum_signals']))
                else:
                    resDf3001.loc[i, 'JupiterZ信号'] = str(resDf3001.loc[i, 'JupiterZ信号']) + ',' + str(int(today_jup_signal.loc[stk_code, 'sum_signals']))
        if stk_code in today_sell1_signal.index:
            if not np.isnan(today_sell1_signal.loc[stk_code, 'sum_signals']):
                if not resDf3001.loc[i, 'Sell1信号']:
                    resDf3001.loc[i, 'Sell1信号'] = str(int(today_sell1_signal.loc[stk_code, 'sum_signals']))
                else:
                    resDf3001.loc[i, 'Sell1信号'] = str(resDf3001.loc[i, 'Sell1信号']) + ',' + str(today_sell1_signal.loc[stk_code, 'sum_signals'])
        if stk_code in today_sell3_signal.index:
            if not np.isnan(today_sell3_signal.loc[stk_code, 'sum_signals']):
                if not resDf3001.loc[i, 'Sell3信号']:
                    resDf3001.loc[i, 'Sell3信号'] = str(int(today_sell3_signal.loc[stk_code, 'sum_signals']))
                else:
                    resDf3001.loc[i, 'Sell3信号'] = str(resDf3001.loc[i, 'Sell3信号']) + ',' + str(int(today_sell3_signal.loc[stk_code, 'sum_signals']))

    resDf3_pj2_holding_today = resDf3_pj2[resDf3_pj2['卖出日期'].apply(lambda x: Adate in x) | ((resDf3_pj2['是否全部卖出'] != 1) & (resDf3_pj2['买入日期'] != Adate))]
    for i in resDf3_pj2_holding_today.index:
        stk_code = resDf3_pj2_holding_today.loc[i, '证券代码']
        if stk_code in today_jup_signal.index:
            if not np.isnan(today_jup_signal.loc[stk_code, 'sum_signals']):
                if not resDf3_pj2.loc[i, 'JupiterZ信号']:  # 不为''
                    resDf3_pj2.loc[i, 'JupiterZ信号'] = str(int(today_jup_signal.loc[stk_code, 'sum_signals']))
                else:
                    resDf3_pj2.loc[i, 'JupiterZ信号'] = str(resDf3_pj2.loc[i, 'JupiterZ信号']) + ',' + str(int(today_jup_signal.loc[stk_code, 'sum_signals']))
        if stk_code in today_sell1_signal.index:
            if not np.isnan(today_sell1_signal.loc[stk_code, 'sum_signals']):
                if not resDf3_pj2.loc[i, 'Sell1信号']:
                    resDf3_pj2.loc[i, 'Sell1信号'] = str(int(today_sell1_signal.loc[stk_code, 'sum_signals']))
                else:
                    resDf3_pj2.loc[i, 'Sell1信号'] = str(resDf3_pj2.loc[i, 'Sell1信号']) + ',' + str(today_sell1_signal.loc[stk_code, 'sum_signals'])
        if stk_code in today_sell3_signal.index:
            if not np.isnan(today_sell3_signal.loc[stk_code, 'sum_signals']):
                if not resDf3_pj2.loc[i, 'Sell3信号']:
                    resDf3_pj2.loc[i, 'Sell3信号'] = str(int(today_sell3_signal.loc[stk_code, 'sum_signals']))
                else:
                    resDf3_pj2.loc[i, 'Sell3信号'] = str(resDf3_pj2.loc[i, 'Sell3信号']) + ',' + str(int(today_sell3_signal.loc[stk_code, 'sum_signals']))

    # -----------------------------增加930和931信号模块---------------------------------------
    today_930_signal = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate, sheet_name = '项目二930样本')
    today_931_signal = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate, sheet_name = '项目二931样本')

    buysellDf_joined_today = resDf3_pj2[resDf3_pj2['买入日期'] == Adate]
    if len(today_930_signal) != 0 and 'p2shouldBuySignal' in today_930_signal.columns.tolist():
        resDf3_pj2.loc[buysellDf_joined_today.index,'930信号'] = today_930_signal.set_index('Unnamed: 0').reindex(buysellDf_joined_today.rename(columns = {'证券代码':'Unnamed: 0'}).set_index('Unnamed: 0').index)\
        ['p2shouldBuySignal'].values * 1
    if len(today_931_signal) != 0:
        resDf3_pj2.loc[buysellDf_joined_today.index,'931信号'] = today_931_signal.set_index('Unnamed: 0').reindex(buysellDf_joined_today.rename(columns = {'证券代码':'Unnamed: 0'}).set_index('Unnamed: 0').index)\
        ['p2shouldBuySignal'].values * 1

    resDf3_pj2[['证券名称','证券代码','买入日期','卖出日期','买入数量','买入金额','买入成交均价','买入当天开盘价','买入当天开盘涨幅(%)',
            '买入当天涨停价','买入当天盘中是否涨停','买入当天收盘价','买入当天是否收盘涨停','买入当日收益率(%)','卖出数量','卖出成交均价','卖出金额',
            '是否全部卖出','卖出比例','卖出部分盈利金额','卖出部分收益率(%)','实际是否正收益','卖出日期开盘价','理论是否正收益','理论是否预测正确',
            '卖出金额占市场比','总卖出数量','前日形态','TN_v2o10','买入时点','930信号','931信号','JupiterZ信号', 'Sell1信号', 'Sell3信号']].to_excel('/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/项目二总卖出记录-%s.xlsx'%(date),sheet_name='总卖出记录',index = False)

    print('create sheet 总卖出记录 for  %s'%'/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/项目二总卖出记录-%s.xlsx'%(date))

    # -----------------------------增加ceres930和931信号模块---------------------------------------
    today_930_ceres_signal = pd.DataFrame()
    today_931_ceres_signal = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate, sheet_name='Ceres931样本')

    buysellDf_joined_today = resDf3_pj3[resDf3_pj3['买入日期'] == Adate]
    if len(today_930_ceres_signal) != 0:
        resDf3_pj3.loc[buysellDf_joined_today.index, '930信号'] = today_930_ceres_signal.set_index('Unnamed: 0').reindex(
            buysellDf_joined_today.rename(columns={'证券代码': 'Unnamed: 0'}).set_index('Unnamed: 0').index) \
                                                                    ['p3shouldBuySignal'].values * 1
    if len(today_931_ceres_signal) != 0:
        resDf3_pj3.loc[buysellDf_joined_today.index, '931信号'] = today_931_ceres_signal.set_index('Unnamed: 0').reindex(
            buysellDf_joined_today.rename(columns={'证券代码': 'Unnamed: 0'}).set_index('Unnamed: 0').index) \
                                                                    ['p3shouldBuySignal'].values * 1

    resDf3_pj3[['证券名称', '证券代码', '买入日期', '卖出日期', '买入数量', '买入金额', '买入成交均价', '买入当天开盘价', '买入当天开盘涨幅(%)',
                '买入当天涨停价', '买入当天盘中是否涨停', '买入当天收盘价', '买入当天是否收盘涨停', '买入当日收益率(%)', '卖出数量', '卖出成交均价', '卖出金额',
                '是否全部卖出', '卖出比例', '卖出部分盈利金额', '卖出部分收益率(%)', '实际是否正收益', '卖出日期开盘价', '理论是否正收益', '理论是否预测正确',
                '卖出金额占市场比', '总卖出数量', '前日形态', 'TN_v2o10d1', '买入时点', '931信号']].to_excel(
        '/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/项目三总卖出记录-%s.xlsx' % (date), sheet_name='总卖出记录', index=False)

    print('create sheet 总卖出记录 for  %s' % '/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/项目三总卖出记录-%s.xlsx' % (date))

    if '卖出日信号' not in resDf3.columns:
        resDf3['卖出日信号'] = np.nan
    if '卖出日信号' not in resDf3001.columns:
        resDf3001['卖出日信号'] = np.nan
    if 'p2shouldBuySignal' in today_930_signal.columns.tolist():
        today_930_signal_re = today_930_signal[['Unnamed: 0','p2shouldBuySignal']].set_index('Unnamed: 0').rename(columns = {'p2shouldBuySignal':'930_signal'})
    else:
        today_930_signal_re = pd.DataFrame(columns = ['930_signal'])
    if len(today_931_signal) == 0:
        today_931_signal_re = pd.DataFrame(columns = ['931_signal'])
    else:
        today_931_signal_re = today_931_signal[['Unnamed: 0','p2shouldBuySignal']].set_index('Unnamed: 0').rename(columns = {'p2shouldBuySignal':'931_signal'})
    if len(today_930_signal_re)>0:
        today_or_signal = today_930_signal_re.join(today_931_signal_re)
    else:
        today_or_signal = today_931_signal_re.join(today_930_signal_re)#today_931_signal_re
    for i, row in today_or_signal.iterrows():
        today_or_signal.loc[i,'or_signal'] = str(today_or_signal.loc[i,'930_signal']*1) + ',' + str(today_or_signal.loc[i,'931_signal']*1)


    '''today_930_ceres_signal_re = today_930_ceres_signal[['Unnamed: 0','p3shouldBuySignal']].set_index('Unnamed: 0').rename(columns = {'p2shouldBuySignal':'930_signal'})
    if len(today_931_signal) == 0:
        today_931_signal_re = pd.DataFrame(columns = ['931_signal'])
    else:'''
    if len(today_931_ceres_signal)>0:
        today_931_ceres_signal_re = today_931_ceres_signal[['Unnamed: 0','p3shouldBuySignal']].set_index('Unnamed: 0').rename(columns = {'p3shouldBuySignal':'931_signal'})
        today_or_ceres_signal = today_931_ceres_signal_re#today_930_ceres_signal_re.join(today_931_ceres_signal_re)
        for i, row in today_or_ceres_signal.iterrows():
            today_or_ceres_signal.loc[i,'or_signal'] =str(today_or_ceres_signal.loc[i,'931_signal']*1)# str(today_or_ceres_signal.loc[i,'930_signal']*1) + ',' + str(today_or_ceres_signal.loc[i,'931_signal']*1)
    else:
        today_or_ceres_signal = pd.DataFrame()

    resDf3_not_sold_signal_today = resDf3[(resDf3['证券代码'].apply(lambda x:x in (list(today_or_signal.index) + list(today_or_ceres_signal.index.tolist()))) &
                                          resDf3['卖出日期'].apply(lambda x:Adate in x)) |
                                          ((resDf3['是否全部卖出'] != 1) & (resDf3['买入日期'] != Adate))]

    if len(resDf3_not_sold_signal_today) != 0:

        # 策略间辅助卖出
        for index, row in resDf3_not_sold_signal_today.iterrows():
            stock = row['证券代码']
            print('策略间辅助卖出票:%s'%stock)
            if stock not in today_or_signal.index or stock not in today_or_ceres_signal.index:
                pass
            elif stock in today_or_signal.index:
                print('！！！！！！！！！！ should not enter this place ！！！！！！！！！！')
                old_signal = resDf3.loc[index,'卖出日信号']
                if type(old_signal) != str:
                    resDf3.loc[index, '卖出日信号'] = str({date:today_or_signal.loc[stock,'or_signal']*1})
                else:
                    resDf3.loc[index, '卖出日信号'] = old_signal + str({date:today_or_signal.loc[stock,'or_signal']*1})
            else:
                print('！！！！！！！！！！ should not enter this place ！！！！！！！！！！')
                old_signal = resDf3.loc[index, '卖出日信号']
                if type(old_signal) != str:
                    resDf3.loc[index, '卖出日信号'] = str({date: today_or_ceres_signal.loc[stock, 'or_signal'] * 1})
                else:
                    resDf3.loc[index, '卖出日信号'] = old_signal + str({date: today_or_ceres_signal.loc[stock, 'or_signal'] * 1})

    resDf3[['证券名称', '证券代码', '买入日期', '卖出日期', '买入数量', '买入金额', '买入成交均价', '买入当天涨停价',
           '买入当天是否收盘涨停', '买入当天收盘价', '买入当日收益率(%)', '卖出数量', '卖出成交均价', '卖出金额',
           '是否全部卖出', '卖出比例', '卖出部分盈利金额', '卖出部分收益率(%)', '实际是否正收益', '卖出日期开盘价', '理论是否正收益',
           '理论是否预测正确', '卖出挂单笔数', '卖出成交笔数', '卖出开始时间', '卖出结束时间', '卖出金额占市场比', '未完成原因',
           '总卖出数量', '买入时形态', 'TN_o2ul', '卖出日信号', 'JupiterZ信号', 'Sell1信号', 'Sell3信号']].to_excel('/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/日内强势股总卖出记录-%s.xlsx'%(date),sheet_name='总卖出记录',index = False)

    # resDf3['卖出日信号']
    print('create sheet 总卖出记录 for  %s' %'/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/日内强势股总卖出记录-%s.xlsx'%(date))

    resDf3001[['证券名称', '证券代码', '买入日期', '卖出日期', '买入数量', '买入金额', '买入成交均价', '买入当天涨停价',
            '买入当天是否收盘涨停', '买入当天收盘价', '买入当日收益率(%)', '卖出数量', '卖出成交均价', '卖出金额',
            '是否全部卖出', '卖出比例', '卖出部分盈利金额', '卖出部分收益率(%)', '实际是否正收益', '卖出日期开盘价', '理论是否正收益',
            '理论是否预测正确', '卖出挂单笔数', '卖出成交笔数', '卖出开始时间', '卖出结束时间', '卖出金额占市场比', '未完成原因',
            '总卖出数量', '买入时形态', 'TN_o2ul', '卖出日信号', 'JupiterZ信号', 'Sell1信号', 'Sell3信号']].to_excel(
        '/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/日内强势股总卖出记录New-%s.xlsx' % (date), sheet_name='总卖出记录', index=False)

    # resDf3['卖出日信号']
    print('create sheet 总卖出记录 for  %s' % '/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/日内强势股总卖出记录New-%s.xlsx' % (date))
    """
    日内强势股不需要判断是否突破即涨停
    def updateBreakZT(resDf):
        logFile = 'A:\wangwd\data_file\LOG\每日突破\\'+date+'-生产环境.xlsx'
        if os.path.exists(logFile):
            logDf = pd.read_excel(logFile)
        else:
            logDf = pd.DataFrame()
        if len(logDf)>0:    
            logDf = logDf[logDf['btTime']!=0]
            stockCodeColumn = '证券代码'
            for index,row in logDf.iterrows():
                stockCode = row['code']
                if stockCode in resDf[resDf['买入日期']==Adate][stockCodeColumn].values:
                    resDfIndex = resDf[resDf[stockCodeColumn]==stockCode].index
                    if len(resDfIndex)>1:
                        #如果有多次买入，取最后一次买入的Index
                        resDfIndex = resDfIndex[-1:]
                else:
                    continue
                if row['突破价格']==row['涨停价格']:
                    resDf.loc[resDfIndex,'是否突破即涨停'] = 1
                else:
                    resDf.loc[resDfIndex,'是否突破即涨停'] = 0
        return resDf
    resDf4 = updateBreakZT(resDf3.copy())
    """



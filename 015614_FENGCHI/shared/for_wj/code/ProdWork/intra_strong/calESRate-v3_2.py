# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 15:34:21 2019
生成总买入信息汇总文件
@author: 013551
"""
import numpy as np
import pandas as pd
from xquant.marketdata import MarketData

from ProdWork.Param_config_data import param, thred_dict_pj3_931, thred_dict_pj2_931
from ProdWork.intra_strong.calESRateHelpV2 import getExtraBuyInfo, write_excel
from ProdWork.intra_strong.func_Basic_zt import cal_Basic_zt

mdp = MarketData()
import os
from LucienUtil import IO
import sys

from xquant.factordata import FactorData
s = FactorData()
import datetime as dt
from xquant.xqutils.helper import link
lm = link.LinkMessage()
from ProdWork.CommonTools import cal_time_delta,number2stockcode,judge_updatedate


def cal_querymetric(jupsz_queryFile,jupsh_queryFile):
    jupsz = pd.read_excel(jupsz_queryFile, sheet_name='所有查询轮次').set_index(['date', 'stock'])    # 20230518 by fengc  从查询结果sheet改读所有查询轮次sheet
    jupsz = jupsz.loc[~jupsz.index.duplicated(keep='first')]
    jupsh = pd.read_excel(jupsh_queryFile, sheet_name='所有查询轮次').set_index(['date', 'stock'])
    jupsh = jupsh.loc[~jupsh.index.duplicated(keep='first')]
    jup_query = pd.concat([jupsh, jupsz]).reset_index()
    jup_query['发生日期'] = jup_query['date'].apply(lambda x: pd.Timestamp(str(x)).strftime('%Y-%m-%d'))
    jup_query.set_index(['发生日期', 'stock'], inplace=True)
    jup_query['Flag_query'] = 1
    jup_query['Flag_has_trade_last3min'] = jup_query['time_gap'].apply(lambda x: 1 if x<185000 else 0)
    return jup_query


if __name__ == "__main__":
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]  # 判断当前的日期
        # date = '20230606'# # 若未在当个交易日晚上运行程序，需要在次日早上修改date
    print('current date = %s' % date)

    # Adate = '2021-08-03'
    # lastdate = '20210802'
    # Alastdate = '2021-08-02'
    Adate = date[0:4] + '-' + date[4:6] + '-' + date[6:8]
    lastdate = s.tradingday(date, -2)[0]
    Alastdate = lastdate[0:4] + '-' + lastdate[4:6] + '-' + lastdate[6:8]
    IO_mother_dir = '/data/group/800080/warehouse_event'
    MD_data_prod_dir = IO_mother_dir + '/prod/LOCAL_DATA/FLAG/%s/' % date
    jup_conceptFile = '/data/group/800463/fengc/daily/concept/jupiter_concept.h5'#jupiter_concept.h5'
    eur_conceptFile = '/data/group/800463/fengc/daily/concept/europa_concept.h5'
    jupsz_queryFile = '/data/group/800463/xiely/daily-track/%s-SZEX/接口查询统计_20211202_%s_SZEX.xlsx' % (date, date)
    jupsh_queryFile = '/data/group/800463/xiely/daily-track/%s-SHEX/接口查询统计_20211220_%s_SHEX.xlsx' % (date, date)
    eursz_queryFile = '/data/group/800463/xiely/daily-track/%s-SZEX/接口查询统计_20220518_%s_SZEX_Europa.xlsx' % (date, date)
    eursh_queryFile = '/data/group/800463/xiely/daily-track/%s-SHEX/接口查询统计_20220518_%s_SHEX_Europa.xlsx' % (date, date)
    factor_model_signal = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate, sheet_name='因子耗时').set_index(['Unnamed: 0'])
    factor_time_cost001 = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate, sheet_name='因子耗时New')
    flag_jupconp = judge_updatedate(jup_conceptFile,date)#True#
    flag_eurconp = judge_updatedate(eur_conceptFile, date)
    flag_jupsz = os.path.exists(jupsz_queryFile)
    flag_jupsh = os.path.exists(jupsh_queryFile)
    flag_eursz = os.path.exists(eursz_queryFile)
    flag_eursh = os.path.exists(eursh_queryFile)
    import time
    now_time = dt.datetime.now()
    import os
    while not os.path.exists(MD_data_prod_dir + '%s_MD.success' % date):
        print('等待MD或RDF或RISK或5分钟数据中！！！！！！')
        time.sleep(60)
    while flag_jupsz == False or flag_jupsh == False or flag_eursz == False or flag_eursh == False:
        flag_jupsz = os.path.exists(jupsz_queryFile)
        flag_jupsh = os.path.exists(jupsh_queryFile)
        flag_eursz = os.path.exists(eursz_queryFile)
        flag_eursh = os.path.exists(eursh_queryFile)
        now_time = dt.datetime.now()
        now_time_int = int(now_time.strftime('%H%M%S'))
        now_time_str = now_time.strftime('%H:%M:%S')
        # print(now_time_str)
        print('%s, 等待接口查询数据中！！！！！！' % now_time_str)
        print(flag_jupsz, flag_jupsh, flag_eursz, flag_eursh)
        if now_time_int > 181000:
            message = '等待接口查询数据未成功生成！！！！%s' % now_time
            lm.sendMessage(message)
        time.sleep(60)
    message = '接口查询数据已成功生成~~~~~~~~~~%s' % now_time
    lm.sendMessage(message)
    # jupsz = pd.read_excel(jupsz_queryFile, sheet_name='查询结果').set_index(['date','stock'])
    # jupsh = pd.read_excel(jupsh_queryFile, sheet_name = '查询结果').set_index(['date','stock'])
    # jup_query = pd.concat([jupsh, jupsz]).reset_index()
    # eursz = pd.read_excel(eursz_queryFile, sheet_name='查询结果').set_index(['date', 'stock'])
    # eursh = pd.read_excel(eursh_queryFile, sheet_name='查询结果').set_index(['date', 'stock'])
    # eur_query = pd.concat([eursh, eursz]).reset_index()
    # jup_query['发生日期'] = jup_query['date'].apply(lambda x: pd.Timestamp(str(x)).strftime('%Y-%m-%d'))
    # jup_query.set_index(['发生日期', 'stock'], inplace=True)
    # eur_query['发生日期'] = eur_query['date'].apply(lambda x: pd.Timestamp(str(x)).strftime('%Y-%m-%d'))
    # eur_query.set_index(['发生日期', 'stock'], inplace=True)
    jup_query = cal_querymetric(jupsz_queryFile, jupsh_queryFile)
    eur_query = cal_querymetric(eursz_queryFile, eursh_queryFile)
    while flag_eurconp == False or flag_jupconp == False:
        flag_jupconp = judge_updatedate(jup_conceptFile, date)
        flag_eurconp = judge_updatedate(eur_conceptFile, date)
        now_time = dt.datetime.now()
        now_time_int = int(now_time.strftime('%H%M%S'))
        now_time_str = now_time.strftime('%H:%M:%S')
        #print(now_time_str)
        print('%s, 等待概念数据中！！！！！！'%now_time_str)
        print(flag_jupconp,flag_eurconp)
        if now_time_int > 182000:
            message = '等待概念数据未成功生成！！！！%s'%now_time
            lm.sendMessage(message)
        time.sleep(60)
    message = '概念数据已成功生成~~~~~~~~~~%s' % now_time
    lm.sendMessage(message)

    nowFile = '/data/group/800463/日内强势股/实盘分析记录/实盘成交回报/综合信息查询_成交回报_%s.xls' % date

    historyFile = '/data/group/800463/日内强势股/实盘分析记录/日内强势股总买入记录/日内强势股总买入记录-%s.xlsx' % lastdate
    historyFile001 = '/data/group/800463/日内强势股/实盘分析记录/日内强势股总买入记录/日内强势股总买入记录New-%s.xlsx' % lastdate
    historyFile_pj2 = '/data/group/800463/日内强势股/实盘分析记录/日内强势股总买入记录/项目二总买入记录-%s.xlsx' % lastdate
    historyFile_pj3 = '/data/group/800463/日内强势股/实盘分析记录/日内强势股总买入记录/项目三总买入记录-%s.xlsx' % lastdate

    logFile = '/data/group/800463/日内强势股/实盘分析记录/每日突破/每日突破_%s_%s.xlsx' % (date, 'prod')

    todayBuyDf = pd.DataFrame()
    todayRecordDf = pd.DataFrame()
    if os.path.exists(nowFile):
        todayRecordDf = pd.read_excel(nowFile)
        todayRecordDf = todayRecordDf #[(todayRecordDf['组合编号'] == 4719)|(todayRecordDf['组合编号'] == 370301)|(todayRecordDf['组合编号'] == 370301) | (todayRecordDf['组合编号'] == 2000000200)|(todayRecordDf['组合编号'] == 2000000100)| (todayRecordDf['组合编号'] == 2000000201)|(todayRecordDf['组合编号'] == 2000000101)]
        todayBuyDf = todayRecordDf[todayRecordDf['委托方向']=='买入']

    print(todayRecordDf.shape, todayBuyDf.shape)
    historyBuyDf = pd.read_excel(historyFile,sheet_name = '总买入记录')
    if os.path.exists(historyFile001):
        historyBuyDf001 = pd.read_excel(historyFile001, sheet_name='总买入记录')
        historyBuyDf001 = historyBuyDf001[historyBuyDf001['证券名称'].notnull()]
    else:
        historyBuyDf001 = pd.DataFrame(columns = historyBuyDf.columns)
    historyBuyDf_pj2 = pd.read_excel(historyFile_pj2,sheet_name = '总买入记录')
    historyBuyDf_pj2 = historyBuyDf_pj2[historyBuyDf_pj2['证券名称'].notnull()]
    if os.path.exists(historyFile_pj3):
        historyBuyDf_pj3 = pd.read_excel(historyFile_pj3, sheet_name='总买入记录')
        historyBuyDf_pj3 = historyBuyDf_pj3[historyBuyDf_pj3['证券名称'].notnull()]
    else:
        historyBuyDf_pj3 = pd.DataFrame(columns = historyBuyDf_pj2.columns)
    if os.path.exists(logFile):
        logDf = pd.read_excel(logFile,sheet_name = '每日突破')
        logDf['actionSource'] = 'JupiterN'
        logDf001 = pd.read_excel(logFile, sheet_name='每日突破New')
        logDf001['actionSource'] = 'JupiterNew'
        if len(logDf)>0:
            logDf = logDf[logDf['ZT_Time']!=0]
        if len(logDf001)>0:
            logDf001 = logDf001[logDf001['ZT_Time']!=0]
        logDf_saturn = pd.read_excel(logFile,sheet_name = '每日项目二')
        if len(logDf_saturn)>0:
            logDf_saturn = logDf_saturn[logDf_saturn['quantity']!=0]
        logDf_ceres = pd.read_excel(logFile, sheet_name='每日项目三')
        if len(logDf_ceres) > 0:
            logDf_ceres = logDf_ceres[logDf_ceres['quantity'] != 0]
        orderDf = pd.read_excel(logFile,sheet_name = '每日订单')
        orderDf[['lastQty', 'lastPx']] = orderDf[['lastQty', 'lastPx']].astype(float)
        orderDf['lastAmt'] = orderDf['lastQty'] * orderDf['lastPx']
        if len(orderDf)>0:
            orderDf = orderDf[orderDf['transactionTime'].apply(lambda x:x[11:13])!= '00']
            buy_orderDf = orderDf[orderDf['orderSide']=='Buy']
        else: buy_orderDf = pd.DataFrame()
        rejectDf = pd.read_excel(logFile,sheet_name = '每日拒绝')
        if len(rejectDf)>0:
            rejectDf = rejectDf[rejectDf['transactTime'].apply(lambda x:x[11:13])!= '00']
            buy_rejectDf = rejectDf[rejectDf['orderSide']=='Buy']
        else: buy_rejectDf = pd.DataFrame()
    else:
        logDf = pd.DataFrame()
        logDf001 = pd.DataFrame()
        logDf_saturn = pd.DataFrame()
        logDf_ceres = pd.DataFrame()
        buy_orderDf = pd.DataFrame()
        buy_rejectDf = pd.DataFrame()

    """
    总共需要的columns
    已有：['证券名称','证券代码','发生日期','委托方向','成交数量','成交金额','成交均价','涨跌幅(%)']
    getExtraBuyInfo处理：['买入当天是否收盘涨停','买入当天收盘价','买入当日收益率(%)','买入当天涨停价']
    额外处理：['买入当日突破时间', '买入当日挂单笔数','买入当日成交笔数']
    """

    commonInfoColumns = ['证券名称','证券代码','发生日期','委托方向','成交数量','成交金额','成交均价','涨跌幅(%)','买入当天是否收盘涨停','买入当天收盘价','买入当日收益率(%)','买入当天涨停价']

    resDf = historyBuyDf.copy()
    resDf001 = historyBuyDf001.copy()
    resDf_pj2 = historyBuyDf_pj2.copy()
    resDf_pj3 = historyBuyDf_pj3.copy()
    buyDf = todayBuyDf.copy()
    # buyDf,resDf,resDf_pj2,logDf,buy_orderDf = todayBuyDf.copy(),historyBuyDf.copy(),historyBuyDf_pj2.copy(),logDf.copy(),buy_orderDf
    def updatePositionBuy(buyDf,resDf,resDf_pj2,resDf_pj3,logDf,buy_orderDf,resDf001,logDf001):
        #signal_info_jup001 = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate,sheet_name='因子耗时New')
        signal_info_pj2_930 = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate, sheet_name='项目二930样本')
        signal_info_pj2_931 = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate, sheet_name='项目二931样本')
        signal_info_pj3_931 = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate,sheet_name='Ceres931样本')

        # 添加买入的分钟数据
        buy_orderDf['buy_Time'] = buy_orderDf['transactionTime'].apply(lambda x:x[11:13]+x[14:16])
        # 更改逻辑，改为使用日志中的信息作为买入的量计算
        if len(logDf) == 0: buy_log_Df_jupiter = pd.DataFrame()
        else: buy_log_Df_jupiter = logDf[(logDf['order_direction'] == 'SplitLastShot')|(logDf['order_direction'] == 'JupiterFirstOrder')| (logDf['order_direction']  == 'MRiskSplitLastShotBuy')|(logDf['order_direction']  == 'MRiskSplitShotBuy')]
        if len(logDf001) == 0: buy_log_Df_jupiter001 = pd.DataFrame()
        else: buy_log_Df_jupiter001 = logDf001[(logDf001['order_direction'] == 'SplitLastShot')|(logDf001['order_direction'] == 'JupiterFirstOrder')| (logDf001['order_direction']  == 'MRiskSplitLastShotBuy')|(logDf001['order_direction']  == 'MRiskSplitShotBuy')]
        if len(logDf_saturn) == 0: buy_log_Df_saturn = pd.DataFrame()
        else: buy_log_Df_saturn = logDf_saturn[(logDf_saturn['order_direction'] == 'A')]
        if len(logDf_ceres) == 0: buy_log_Df_ceres = pd.DataFrame()
        else: buy_log_Df_ceres = logDf_ceres[logDf_ceres['order_direction'] == 'A']
        # 先从日志中的信息里计算 买入额、买入量

        buy_orderDf_jupiter = buy_orderDf[(buy_orderDf['actionSource'] != 'JupiterNew')&((buy_orderDf['orderType'] == 'SplitLastShot')|(buy_orderDf['orderType']  == 'MRiskSplitShot')|(buy_orderDf['orderType'] == 'JupiterFirstOrder')| (buy_orderDf['orderType'] == 'MRiskSplitLastShotBuy')| (buy_orderDf['orderType'] == 'MRiskSplitShot')|(buy_orderDf['orderType']  == 'MRiskSplitShotBuy'))]
        buy_orderDf_jupiter001 = buy_orderDf[(buy_orderDf['actionSource'] == 'JupiterNew')&(
            (buy_orderDf['orderType'] == 'SplitLastShot') | (buy_orderDf['orderType'] == 'MRiskSplitShot') | (
                        buy_orderDf['orderType'] == 'JupiterFirstOrder') | (
                        buy_orderDf['orderType'] == 'MRiskSplitLastShotBuy') | (
                        buy_orderDf['orderType'] == 'MRiskSplitShot') | (
                        buy_orderDf['orderType'] == 'MRiskSplitShotBuy'))]

        buy_orderDf_saturn = buy_orderDf[buy_orderDf['orderType'] == 'SaturnBuy']
        buy_orderDf_ceres = buy_orderDf[buy_orderDf['orderType'] == 'CeresBuy']
        def get_buy_amt_volume(data):
            data = data.sort_values(by = ['transactionTime'])
            len_buy = (data['ordStatus'] == 'NEW').sum()
            len_filled = (data['ordStatus'] == 'FILLED').sum()
            data_filled = data[data['ordStatus'] == 'FILLED']
            if len_buy != len_filled:
                if data.iloc[~0]['ordStatus'] == 'PARTIALLY_FILLED': # ~0=-1, 表示最后一个或者倒数第一个
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
            buyDf['证券代码'] = buyDf['证券代码'].apply(number2stockcode)
            buy_orderDf_tot_info = buyDf.rename(columns = {'证券代码':'stockcode','成交数量':'deal_vol','成交金额':'deal_amt'})[['deal_vol','deal_amt','stockcode']]
            buy_orderDf_tot_info['deal_vwap'] = buy_orderDf_tot_info['deal_amt']/buy_orderDf_tot_info['deal_vol']
            buy_orderDf_jupiter_info = buy_orderDf_tot_info[buy_orderDf_tot_info['stockcode'].apply(lambda x:x in set(buy_orderDf_jupiter['stockcode']))].set_index('stockcode')
            buy_orderDf_jupiter001_info = buy_orderDf_tot_info[buy_orderDf_tot_info['stockcode'].apply(lambda x: x in set(buy_orderDf_jupiter001['stockcode']))].set_index('stockcode')
            buy_orderDf_saturn_info = buy_orderDf_tot_info[buy_orderDf_tot_info['stockcode'].apply(lambda x:x in set(buy_orderDf_saturn['stockcode']))].set_index('stockcode')
            buy_orderDf_saturn_info = buy_orderDf_saturn_info[buy_orderDf_saturn_info['deal_amt']!=0]

            buy_orderDf_ceres_info = buy_orderDf_tot_info[buy_orderDf_tot_info['stockcode'].apply(lambda x: x in set(buy_orderDf_ceres['stockcode']))].set_index('stockcode')
            buy_orderDf_ceres_info = buy_orderDf_ceres_info[buy_orderDf_ceres_info['deal_amt'] != 0]

            # 在日志中有jupiter买入或者jupiter尝试买入才会进行输出
            buyDf_jupiter = buyDf[buyDf['证券代码'].apply(lambda x:x in list(buy_orderDf_jupiter_info.index))]
            buyDf_jupiter001 = buyDf[buyDf['证券代码'].apply(lambda x: x in list(buy_orderDf_jupiter001_info.index))]
            buyDf_saturn = buyDf[buyDf['证券代码'].apply(lambda x:x in list(buy_orderDf_saturn_info.index))]
            buyDf_ceres = buyDf[buyDf['证券代码'].apply(lambda x: x in list(buy_orderDf_ceres_info.index))]

            # commonInfoColumns是成交回报中直接有的信息、buyExtraColumns是通过计算重新获取的信息
            buyDf_jupiter = getExtraBuyInfo(buyDf_jupiter)
            buyDf_jupiter001 = getExtraBuyInfo(buyDf_jupiter001)
            buyDf_saturn = getExtraBuyInfo(buyDf_saturn)
            buyDf_ceres = getExtraBuyInfo(buyDf_ceres)
        for index,row in buyDf_jupiter.iterrows():
            dummy_resDfindex = len(resDf)
            stock_code = row['证券代码']
            resDf.loc[dummy_resDfindex,commonInfoColumns] = row[commonInfoColumns].values
            #resDf.loc[dummy_resDfindex,['成交数量','成交金额','成交均价']] = buy_orderDf_jupiter_info.loc[stock_code][['deal_vol','deal_amt','deal_vwap']].values
            sel_order = buy_orderDf_jupiter[((buy_orderDf_jupiter['ordStatus']=='PARTIALLY_FILLED')|(buy_orderDf_jupiter['ordStatus']=='FILLED'))&(buy_orderDf_jupiter['stockcode']==stock_code)]
            resDf.loc[dummy_resDfindex, ['成交数量','成交金额']] = sel_order[['lastQty','lastAmt']].sum().values
            resDf.loc[dummy_resDfindex, '成交均价'] = resDf.loc[dummy_resDfindex, '成交金额']/resDf.loc[dummy_resDfindex, '成交数量']

        for index,row in buyDf_jupiter001.iterrows():
            dummy_resDfindex = len(resDf001)
            stock_code = row['证券代码']
            resDf001.loc[dummy_resDfindex,commonInfoColumns] = row[commonInfoColumns].values
            if stock_code not in resDf[resDf['发生日期']==Adate]['证券代码'].tolist():
                resDf001.loc[dummy_resDfindex,['成交数量','成交金额','成交均价']] = buy_orderDf_jupiter001_info.loc[stock_code][['deal_vol','deal_amt','deal_vwap']].values
            else:
                resDf001.loc[dummy_resDfindex, '成交数量'] = float(buy_orderDf_jupiter001_info.loc[stock_code]['deal_vol'])- float(resDf[(resDf['发生日期']==Adate)&(resDf['证券代码']==stock_code)]['成交数量'])
                resDf001.loc[dummy_resDfindex,  '成交金额'] = float(buy_orderDf_jupiter001_info.loc[stock_code]['deal_amt'])- float(resDf[(resDf['发生日期'] == Adate) & (resDf['证券代码'] == stock_code)][ '成交金额'])

            '''sel_order = buy_orderDf_jupiter001[(
                        (buy_orderDf_jupiter001['ordStatus'] == 'PARTIALLY_FILLED') | (
                            buy_orderDf_jupiter001['ordStatus'] == 'FILLED')) & (
                                                        buy_orderDf_jupiter001['stockcode'] == stock_code)]
            resDf001.loc[dummy_resDfindex, ['成交数量', '成交金额']] = sel_order[['lastQty', 'lastAmt']].sum().values'''
            resDf001.loc[dummy_resDfindex, '成交均价'] = resDf001.loc[dummy_resDfindex, '成交金额'] / resDf001.loc[dummy_resDfindex, '成交数量']
        buyExtraColumns = ['买入当天开盘涨幅(%)','买入当天开盘价','买入当天盘中是否涨停']
        #buyDf_saturn = getExtraBuyInfo(buyDf_saturn)
        for index,row in buyDf_saturn.iterrows():
            dummy_resDfpj2_index = len(resDf_pj2)
            stock_code = row['证券代码']
            if stock_code in list(signal_info_pj2_930['Unnamed: 0']):
                signal_pj2_930 = False#signal_info_pj2_930[signal_info_pj2_930['Unnamed: 0']==stock_code]['p2shouldBuySignal'].values[0] == True
            else: signal_pj2_930 = False
            if len(signal_info_pj2_931)!=0:
                if stock_code in list(signal_info_pj2_931['Unnamed: 0']):
                    signal_pj2_931 = signal_info_pj2_931[signal_info_pj2_931['Unnamed: 0']==stock_code]['p2shouldBuySignal'].values[0] == True
                else: signal_pj2_931 = False
            else: signal_pj2_931 = False
            if signal_pj2_930:
                if (not signal_pj2_931) | (len(buy_orderDf[(buy_orderDf['stockcode'] == stock_code) & (buy_orderDf['buy_Time']>='0931')]) != 0):
                    resDf_pj2.loc[dummy_resDfpj2_index,commonInfoColumns+buyExtraColumns] = row[commonInfoColumns+buyExtraColumns].values
                    resDf_pj2.loc[dummy_resDfpj2_index,['成交数量','成交金额','成交均价']] = buy_orderDf_saturn_info.loc[stock_code][['deal_vol','deal_amt','deal_vwap']].values
                    resDf_pj2.loc[dummy_resDfpj2_index, ['买入时点']] = '930'
                else:
                    tot_amt, tot_vol, tot_vwap = buy_orderDf_saturn_info.loc[stock_code][['deal_vol','deal_amt','deal_vwap']].values
                    post_931_info = buy_orderDf[(buy_orderDf['stockcode'] == stock_code) & (buy_orderDf['buy_Time']>='0931')]
                    post_931_amt, post_931_vol, post_931_vwap = get_buy_amt_volume(post_931_info)
                    pre_931_amt, pre_931_vol, pre_931_vwap = tot_amt - post_931_amt, tot_vol - post_931_vol,(tot_amt - post_931_amt) / (tot_vol - post_931_vol)
                    resDf_pj2.loc[dummy_resDfpj2_index,commonInfoColumns+buyExtraColumns] = row[commonInfoColumns+buyExtraColumns].values
                    resDf_pj2.loc[dummy_resDfpj2_index,['成交数量','成交金额','成交均价']] = np.array([pre_931_amt, pre_931_vol, pre_931_vwap])
                    resDf_pj2.loc[dummy_resDfpj2_index, ['买入时点']] = '930'
                    if post_931_amt != 0:
                        pj2_extra_index = dummy_resDfpj2_index + 1
                        resDf_pj2.loc[pj2_extra_index,commonInfoColumns+buyExtraColumns] = row[commonInfoColumns+buyExtraColumns].values
                        resDf_pj2.loc[pj2_extra_index,['成交数量','成交金额','成交均价']] = np.array([post_931_amt, post_931_vol, post_931_vwap])
                        resDf_pj2.loc[pj2_extra_index, ['买入时点']] = '931'
            else:
                resDf_pj2.loc[dummy_resDfpj2_index, commonInfoColumns + buyExtraColumns] = row[commonInfoColumns + buyExtraColumns].values
                resDf_pj2.loc[dummy_resDfpj2_index, ['成交数量', '成交金额', '成交均价']] = buy_orderDf_saturn_info.loc[stock_code][['deal_vol', 'deal_amt', 'deal_vwap']].values
                resDf_pj2.loc[dummy_resDfpj2_index, ['买入时点']] = '931'
                index_in_timecost = signal_info_pj2_931[signal_info_pj2_931['Unnamed: 0'] == stock_code].index.tolist()[0]
                resDf_pj2.loc[dummy_resDfpj2_index, ['委托金额']] = float(signal_info_pj2_931.loc[index_in_timecost][['totalOrderAmt']])
        for index,row in buyDf_ceres.iterrows():
            dummy_resDfpj3_index = len(resDf_pj3)
            stock_code = row['证券代码']
            signal_pj3_930 = False

            '''if stock_code in list(signal_info_pj3_930['Unnamed: 0']):
                signal_pj3_930 = signal_info_pj3_930[signal_info_pj3_930['Unnamed: 0']==stock_code]['p3shouldBuySignal'].values[0] == True
            else: signal_pj3_930 = False'''
            if len(signal_info_pj3_931)!=0:
                if stock_code in list(signal_info_pj3_931['Unnamed: 0']):
                    signal_pj3_931 = signal_info_pj3_931[signal_info_pj3_931['Unnamed: 0']==stock_code]['p3shouldBuySignal'].values[0] == True
                else: signal_pj3_931 = False
            else: signal_pj3_931 = False
            if signal_pj3_930:
                if (not signal_pj3_931) | (len(buy_orderDf[(buy_orderDf['stockcode'] == stock_code) & (buy_orderDf['buy_Time']>='0931')]) != 0):
                    resDf_pj3.loc[dummy_resDfpj3_index,commonInfoColumns+buyExtraColumns] = row[commonInfoColumns+buyExtraColumns].values
                    resDf_pj3.loc[dummy_resDfpj3_index,['成交数量','成交金额','成交均价']] = buy_orderDf_ceres_info.loc[stock_code][['deal_vol','deal_amt','deal_vwap']].values
                    resDf_pj3.loc[dummy_resDfpj3_index, ['买入时点']] = '930'
                else:
                    tot_amt, tot_vol, tot_vwap = buy_orderDf_ceres_info.loc[stock_code][['deal_vol','deal_amt','deal_vwap']].values
                    post_931_info = buy_orderDf[(buy_orderDf['stockcode'] == stock_code) & (buy_orderDf['buy_Time']>='0931')]
                    post_931_amt, post_931_vol, post_931_vwap = get_buy_amt_volume(post_931_info)
                    pre_931_amt, pre_931_vol, pre_931_vwap = tot_amt - post_931_amt, tot_vol - post_931_vol,(tot_amt - post_931_amt) / (tot_vol - post_931_vol)
                    resDf_pj2.loc[dummy_resDfpj2_index,commonInfoColumns+buyExtraColumns] = row[commonInfoColumns+buyExtraColumns].values
                    resDf_pj2.loc[dummy_resDfpj2_index,['成交数量','成交金额','成交均价']] = np.array([pre_931_amt, pre_931_vol, pre_931_vwap])
                    resDf_pj2.loc[dummy_resDfpj2_index, ['买入时点']] = '930'
                    if post_931_amt != 0:
                        pj2_extra_index = dummy_resDfpj2_index + 1
                        resDf_pj2.loc[pj2_extra_index,commonInfoColumns+buyExtraColumns] = row[commonInfoColumns+buyExtraColumns].values
                        resDf_pj2.loc[pj2_extra_index,['成交数量','成交金额','成交均价']] = np.array([post_931_amt, post_931_vol, post_931_vwap])
                        resDf_pj2.loc[pj2_extra_index, ['买入时点']] = '931'
            else:
                resDf_pj3.loc[dummy_resDfpj3_index, commonInfoColumns + buyExtraColumns] = row[commonInfoColumns + buyExtraColumns].values
                resDf_pj3.loc[dummy_resDfpj3_index, ['成交数量', '成交金额', '成交均价']] = buy_orderDf_ceres_info.loc[stock_code][['deal_vol', 'deal_amt', 'deal_vwap']].values
                resDf_pj3.loc[dummy_resDfpj3_index, ['买入时点']] = '931'
                index_in_timecost = signal_info_pj3_931[signal_info_pj3_931['Unnamed: 0'] == stock_code].index.tolist()[0]
                resDf_pj3.loc[dummy_resDfpj3_index, ['委托金额']] = float(signal_info_pj3_931.loc[index_in_timecost][['totalOrderAmt']])

        md_close_pre_close = IO.read_data([date, date], columns=['pre_close', 'close','high']
                     , alt=IO_mother_dir+'/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')

        name_data = IO.read_data([lastdate, lastdate], alt='/data/group/800080/warehouse/prod/FCD/CHINA_STOCK/DAILY/SUNTIME/FCD_CHINA_STOCK_DAILY_SUNTIME.h5')
        # 针对日内强势股进行额外信息的填充
        for index,row in buy_log_Df_jupiter.iterrows():
            stockCode = row['Unnamed: 0']
            ZT_Time = row['ZT_Time']
            print(stockCode,ZT_Time)
            if (len(resDf[resDf['发生日期']==Adate])>0) and \
                (stockCode in resDf[resDf['发生日期']==Adate]['证券代码'].values):
                resDfIndex = resDf[resDf['证券代码']==stockCode].index
                if len(resDfIndex)>1:
                    resDfIndex = resDfIndex[-1:]
            else: # 如果存在正常的数据
                # 针对当天在o32中没有但在log中有的票进行数据填充
                resDfIndex,stock_code = len(resDf),row['Unnamed: 0']
                resDf.loc[resDfIndex, ['证券代码','证券名称']] = stock_code,name_data.loc[lastdate,stock_code]['STOCK_NAME'].values[0]
                resDf.loc[resDfIndex, ['发生日期','委托方向','成交数量','成交金额']] = Adate,'买入', 0, 0
            # 其他columns，计算买入日形态和突破时间
            pre_close, close,ul_price = md_close_pre_close.loc[date, stockCode].values
            resDf.loc[resDfIndex, '形态'] = cal_Basic_zt(mdp, stockCode, date, pre_close, close)['label_pattern'].values[0]
            resDf.loc[resDfIndex, '买入当日突破时间'] = ZT_Time
            resDf.loc[resDfIndex, '委托金额'] = buy_log_Df_jupiter.loc[index,'totalOrderAmt']
        # 针对jupNew进行额外信息的填充
        for index, row in buy_log_Df_jupiter001.iterrows():
            stockCode = row['Unnamed: 0']
            ZT_Time = row['ZT_Time']
            if (len(resDf001[resDf001['发生日期'] == Adate]) > 0) and \
                    (stockCode in resDf001[resDf001['发生日期'] == Adate]['证券代码'].values):
                resDfIndex = resDf001[resDf001['证券代码'] == stockCode].index
                if len(resDfIndex) > 1:
                    resDfIndex = resDfIndex[-1:]
            else:  # 如果存在正常的数据
                # 针对当天在o32中没有但在log中有的票进行数据填充
                resDfIndex, stock_code = len(resDf001), row['Unnamed: 0']
                resDf001.loc[resDfIndex, ['证券代码', '证券名称']] = stock_code, \
                                                          name_data.loc[lastdate, stock_code]['STOCK_NAME'].values[
                                                              0]
                resDf001.loc[resDfIndex, ['发生日期', '委托方向', '成交数量', '成交金额']] = Adate, '买入', 0, 0
            # 其他columns，计算买入日形态和突破时间
            pre_close, close, ul_price = md_close_pre_close.loc[date, stockCode].values
            if stockCode in resDf[resDf['发生日期']==Adate]['证券代码'].tolist():
                resDf001.loc[resDfIndex, '形态'] = resDf[(resDf['证券代码']==stockCode)&(resDf['发生日期']==Adate)]['形态'].values[0]
            else:
                print('only trigger jupiterNew: %s, %s' % (stockCode, Adate))
                resDf001.loc[resDfIndex, '形态'] = cal_Basic_zt(mdp, stockCode, date, pre_close, close)['label_pattern'].values[0]
            resDf001.loc[resDfIndex, '买入当日突破时间'] = ZT_Time
            resDf001.loc[resDfIndex, '委托金额'] = buy_log_Df_jupiter001.loc[index, 'totalOrderAmt']
        # 针对项目二930进行额外信息的填充
        if len(buy_log_Df_saturn) == 0:
            pass
        else:
            buy_log_Df_saturn = buy_log_Df_saturn.loc[~buy_log_Df_saturn['Unnamed: 0'].duplicated(keep='first')]
        saturn_basic_info = pd.read_hdf('/data/group/800463/project/project2_prod/daily_data/%s_v5/Basic_night_finish_%s_%s.h5'%(date,date,date))
        #saturn_basic_info = pd.read_hdf('/data/group/800463/project/project2_prod/daily_data/Basic/Basic_closed_hf_finish.h5')  #
        for index,row in buy_log_Df_saturn.iterrows():
            stockCode = row['Unnamed: 0']
            if (len(resDf_pj2[resDf_pj2['发生日期']==Adate])>0) and \
                (stockCode in resDf_pj2[resDf_pj2['发生日期']==Adate]['证券代码'].values):
                resDfpj2Index = resDf_pj2[resDf_pj2['证券代码']==stockCode].index
                if len(resDfpj2Index)>1:
                    resDfpj2Index = resDfpj2Index[-1:]
                resDf_pj2.loc[resDfpj2Index, '前日形态'] = saturn_basic_info.loc[date,stockCode]['lzt_label_pattern']

        # 针对项目三931进行额外信息的填充
        if len(buy_log_Df_ceres) == 0:
            pass
        else:
            buy_log_Df_ceres = buy_log_Df_ceres.loc[~buy_log_Df_ceres['Unnamed: 0'].duplicated(keep='first')]
        ceres_basic_info = pd.read_hdf(
            '/data/group/800463/project/project3_prod/daily_data/%s_v3/Basic_night_finish_%s_%s.h5' % (date, date, date))
        for index, row in buy_log_Df_ceres.iterrows():
            stockCode = row['Unnamed: 0']
            if (len(resDf_pj3[resDf_pj3['发生日期'] == Adate]) > 0) and \
                    (stockCode in resDf_pj3[resDf_pj3['发生日期'] == Adate]['证券代码'].values):
                resDfpj3Index = resDf_pj3[resDf_pj3['证券代码'] == stockCode].index
                if len(resDfpj3Index) > 1:
                    resDfpj3Index = resDfpj3Index[-1:]
                resDf_pj3.loc[resDfpj3Index, '前日形态'] = ceres_basic_info.loc[date, stockCode][
                    'lcb_label_pattern']
        resDf['涨跌幅(%)'] = resDf['涨跌幅(%)'].astype(float)
        resDf_pj2['涨跌幅(%)'] = resDf_pj2['涨跌幅(%)'].astype(float)
        resDf_pj3['涨跌幅(%)'] = resDf_pj3['涨跌幅(%)'].astype(float)
        return resDf, resDf_pj2,resDf_pj3, resDf001

    def model_lnzt_stack_v3(data):
        data['reg_vote'] = data['回归信号'].astype(int)
        data['cla_vote'] = data['分类信号'].astype(int)
        data['sum_vote'] = data['reg_vote'] + data['cla_vote']

        condition1 = data['sum_vote'] >= 5  # (reg_stacking + cla_stacking) >= 5
        condition2 = (data['cla_vote'] == 2) & (data['reg_vote'] == 2)  # (cla_stacking == 2) & (reg_stacking == 2)
        condition3 = (data['cla_vote'] == 1) & (data['reg_vote'] == 4)  # (cla_stacking == 1) & (reg_stacking == 4)
        condition4 = (data['cla_vote'] == 0) & (data['reg_vote'] >= 5)  # (cla_stacking == 0) & (reg_stacking >= 5)
        #data['shouldBuySignal'] = (condition1 | condition2) & (condition3 == False) & (condition4 == False)
        '''level4_con1 = (data['sum_vote']>=7)
        level4_con2 = ((data['cla_vote']==4)&(data['reg_vote']==2))
        level4_con3 = ~((data['cla_vote']==1)&(data['reg_vote']==6))
        level4 = ((level4_con1 | level4_con2) & (level4_con3))'''
        level4 = (~((data['cla_vote'] == 1) & (data['reg_vote'] == 6))) & (
                    (data['sum_vote'] >= 7) | ((data['cla_vote'] == 4) & (data['reg_vote'] == 2)))
        level3_con1 = (data['reg_vote'] >= 5)
        level3_con2 = ((data['cla_vote'] == 2) & (data['reg_vote'] == 2))
        level3_con3 = ~((data['cla_vote'] == 1) & (data['reg_vote'] == 4))
        level3_con3 = ~((data['cla_vote'] == 0) & (data['reg_vote'] >= 5))
        level3_con5 = (level4 == False)
        level3 = (~((data['cla_vote'] == 1) & (data['reg_vote'] == 4))) & (
            ~((data['cla_vote'] == 0) & (data['reg_vote'] >= 5))) & (level4 == False) & (
                         (data['sum_vote'] >= 5) | ((data['cla_vote'] == 2) & (data['reg_vote'] == 2)))
        #data['shouldBuySignal_34'] = (level3 | level4)
        data['level_3'] = 3 * (level3.astype(int))
        data['level_4'] = 4 * (level4.astype(int))
        data['level'] = data['level_3'] + data['level_4']  # data.apply(lambda x: 3 if x['level_3']==1 )
        #data.drop(columns = ['reg_vote','cla_vote','sum_vote','level_3','level_4'], inplace = True)
        # '''
        return data['level']
    def writeExcel(resDf):
        writePath = '/data/group/800463/日内强势股/实盘分析记录/日内强势股总买入记录/日内强势股总买入记录-%s.xlsx'%(date)
        sheetname = '总买入记录'
        resDf.replace(np.nan,'',inplace=True)
        print('write sheet %s for %s!!!!!!!'%(sheetname,writePath))
        write_excel(resDf, writePath, sheetname)
    def writeExcel001(resDf):
        writePath = '/data/group/800463/日内强势股/实盘分析记录/日内强势股总买入记录/日内强势股总买入记录New-%s.xlsx'%(date)
        sheetname = '总买入记录'
        resDf.replace(np.nan,'',inplace=True)
        print('write sheet %s for %s!!!!!!!'%(sheetname,writePath))
        write_excel(resDf, writePath, sheetname)
    def writeExcel_pj2(resDf):
        writePath = '/data/group/800463/日内强势股/实盘分析记录/日内强势股总买入记录/项目二总买入记录-%s.xlsx'%(date)
        sheetname = '总买入记录'
        resDf.replace(np.nan,'',inplace=True)
        print('write sheet %s for %s!!!!!!!' % (sheetname, writePath))
        write_excel(resDf, writePath, sheetname)
    def writeExcel_pj3(resDf):
        writePath = '/data/group/800463/日内强势股/实盘分析记录/日内强势股总买入记录/项目三总买入记录-%s.xlsx'%(date)
        sheetname = '总买入记录'
        resDf.replace(np.nan,'',inplace=True)
        print('write sheet %s for %s!!!!!!!' % (sheetname, writePath))
        write_excel(resDf, writePath, sheetname)
    def orderrejectlog2reason(buy_orderDf,buy_rejectDf):
        # 若包含“PARTIALLY_FILLED” 则一定是部分未成交，若不包含“FILLED",则一定是未成交，成交不能只使用”FILLED"
        #buy_orderDf['未成交金额'] = buy_orderDf['委托金额'].astype(float) - buy_orderDf['成交金额'].astype(float)
        if (len(buy_orderDf) == len(buy_rejectDf)) & (len(buy_rejectDf) == 0):
            return pd.DataFrame()
        else:
            buy_orderDf_for_reject = buy_orderDf[buy_orderDf['orderType'] != 'SmallTest']
            #buy_orderDf_for_reject = buy_orderDf_for_rejectall[buy_orderDf_for_rejectall['actionSource'] != 'JupiterNew']
            #buy_orderDf_for_rejectjup001 = buy_orderDf_for_reject[buy_orderDf_for_reject['actionSource'] == 'JupiterNew']
            #buy_orderDf_for_reject = pd.concat
            filled_stocks = buy_orderDf_for_reject.groupby('stockcode').apply(lambda x:'FILLED' in list(x['ordStatus']))
            #filled_stocks001 = buy_orderDf_for_rejectjup001.groupby('stockcode').apply(lambda x: 'FILLED' in list(x['ordStatus']))
            #filled_stocks = pd.concat([filled_stocks,filled_stocks001])
            partially_filled_stocks = buy_orderDf_for_reject.groupby('stockcode').apply(lambda x:'PARTIALLY_FILLED' in list(x['ordStatus']))
            partially_filled_stocks = list(partially_filled_stocks[partially_filled_stocks].index)
            unfilled_stocks = filled_stocks[filled_stocks == False] # 不是filled( )也不是partially filled，那就unfilled
            unfilled_info = pd.DataFrame()
            unfilled_stocks_not_rejected = list(unfilled_stocks.index)
            if len(buy_rejectDf) > 0:
                #reject_summary = buy_rejectDf.groupby('stockcode').apply(lambda x:str(list(np.unique(x['riskSummary'])))).reindex(unfilled_stocks.index)
                #reject_operation = buy_rejectDf.groupby('stockcode').apply(lambda x:str(list(np.unique(x['riskOperation'])))).reindex(unfilled_stocks.index)
                #reject_type = buy_rejectDf.groupby('stockcode').apply(lambda x: str(list(np.unique(x['riskType'])))).reindex(unfilled_stocks.index)
                #reject_mrisk = buy_rejectDf.groupby('stockcode').apply(lambda x: str(list(np.unique(x['MriskFlag'])))).reindex(unfilled_stocks.index)
                #reject_info = buy_orderDf[buy_orderDf['未成交金额'] > 500000]

                # change by fengc 20230525，防止出现nan
                # change by fengc 20230606，增加合规风控的一个日志字段改变，隔离池
                # buy_rejectDf['riskSummary'] = buy_rejectDf['riskSummary'].fillna('')
                buy_rejectDf['riskSummary'] = buy_rejectDf['riskSummary'].fillna(buy_rejectDf['riskViolateRemark'])
                reject_info = buy_rejectDf.groupby('stockcode').apply(lambda x: str(list(np.unique(x['riskSummary'].astype(str)))) + ',' +
                                                                                str(list(np.unique(x['MriskFlag'].astype(str))))).reindex(unfilled_stocks.index)
                reject_info = reject_info.fillna('未成交')
                reject_info.loc[list(set(partially_filled_stocks).intersection(set(reject_info.index)))] = '部分未成交'
                print('部分未成交:', reject_info.loc[list(set(partially_filled_stocks).intersection(set(reject_info.index)))])
                reject_info = reject_info.reset_index().rename(columns = {'stockcode':'证券代码', 0:'未完成原因'})
                reject_info['发生日期'] = Adate
                for stock in np.unique(buy_rejectDf['stockcode']):
                    if stock in unfilled_stocks_not_rejected:
                        unfilled_stocks_not_rejected.remove(stock)

            else:
                reject_info = pd.DataFrame()
                for stock in unfilled_stocks_not_rejected:
                    # stock = unfilled_stocks.index[0]
                    unfilled_dic = {'证券代码':stock,
                                    '未完成原因':'未成交',
                                    '发生日期':Adate}
                    if stock in partially_filled_stocks:
                        unfilled_dic['未完成原因'] = '部分未成交'
                    unfilled_info = pd.concat([unfilled_info,pd.Series(unfilled_dic)],sort = False,axis = 1)
            unfilled_info_df = unfilled_info.T
            reject_info_out = pd.concat([reject_info,unfilled_info_df],axis = 0)
            return reject_info_out

    resDf1, resDf1_pj2, resDf1_pj3,resDf1001 = updatePositionBuy(todayBuyDf.copy(),historyBuyDf.copy(),historyBuyDf_pj2.copy(),historyBuyDf_pj3.copy(),logDf.copy(),buy_orderDf.copy(),historyBuyDf001.copy(),logDf001.copy())
    #resDf1, resDf1_pj2 = updatePositionBuy(todayBuyDf.copy(), historyBuyDf.copy(), historyBuyDf_pj2.copy(),pd.DataFrame(), pd.DataFrame())
    if True in resDf1001['形态'].isnull():
        unfilled_pattern = resDf1001[resDf1001['形态'].isnull()]
        for index,row in unfilled_pattern.iterrows():
            # index = unfilled_pattern.index[0]
            # row = unfilled_pattern.iloc[0]
            stock_code,pre_date= row[['证券代码','发生日期']].values
            pre_date = pre_date[0:4]+pre_date[5:7]+pre_date[8:]
            print(stock_code,pre_date)
            pre_close, close,ul_price  = IO.read_data([pre_date, pre_date], columns=['pre_close', 'close','high']
            ,alt=IO_mother_dir+'/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5').loc[pre_date, stock_code].values
            resDf1001.loc[index,'形态'] = cal_Basic_zt(mdp, stock_code, pre_date, pre_close, close)['label_pattern'].values[0]

    if True in resDf1['形态'].isnull():
        unfilled_pattern = resDf1[resDf1['形态'].isnull()]
        for index,row in unfilled_pattern.iterrows():
            # index = unfilled_pattern.index[0]
            # row = unfilled_pattern.iloc[0]
            stock_code,pre_date= row[['证券代码','发生日期']].values
            pre_date = pre_date[0:4]+pre_date[5:7]+pre_date[8:]
            print(stock_code,pre_date)
            pre_close, close,ul_price  = IO.read_data([pre_date, pre_date], columns=['pre_close', 'close','high']
            ,alt=IO_mother_dir+'/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5').loc[pre_date, stock_code].values
            if stock_code in resDf1001['证券代码'].tolist():
                if len(resDf1001[(resDf1001['证券代码'] == stock_code) & (resDf1001['发生日期'] == pre_date)]['形态'].values)>0:
                    resDf1.loc[index, '形态'] = \
                resDf1001[(resDf1001['证券代码'] == stock_code) & (resDf1001['发生日期'] == pre_date)]['形态'].values[0]
                else:
                    resDf1.loc[index, '形态'] = 0
            else:
                print('only trigger jupiter: %s, %s'%(stock_code,pre_date))
                resDf1.loc[index,'形态'] = cal_Basic_zt(mdp, stock_code, pre_date, pre_close, close)['label_pattern'].values[0]


    rjf = orderrejectlog2reason(buy_orderDf,buy_rejectDf)
    if len(rjf) != 0:
        rjf = rjf.reset_index()[['证券代码','未完成原因','发生日期']]
    for i in rjf.index:
        # 如果项目二买了则jupiter不买，所以先判断是否在今日的项目二中
        if len(resDf1_pj2[((resDf1_pj2['证券代码'] == rjf.loc[i]['证券代码']) & (resDf1_pj2['发生日期'] == rjf.loc[i]['发生日期']))]) != 0:
            buy_index_pj2 = resDf1_pj2[((resDf1_pj2['证券代码'] == rjf.loc[i]['证券代码']) & (resDf1_pj2['发生日期'] == rjf.loc[i]['发生日期']))].index
            resDf1_pj2.loc[buy_index_pj2,'未完成原因'] = rjf.loc[i]['未完成原因']
        # 如果项目三买了则jupiter不买，所以先判断是否在今日的项目三
        elif len(resDf1_pj3[((resDf1_pj3['证券代码'] == rjf.loc[i]['证券代码']) & (resDf1_pj3['发生日期'] == rjf.loc[i]['发生日期']))]) != 0:
            buy_index_pj3 = resDf1_pj3[((resDf1_pj3['证券代码'] == rjf.loc[i]['证券代码']) & (resDf1_pj3['发生日期'] == rjf.loc[i]['发生日期']))].index
            resDf1_pj3.loc[buy_index_pj3,'未完成原因'] = rjf.loc[i]['未完成原因']

        else:
            print('jupiter or jupiterNew')
            if len(resDf1[((resDf1['证券代码'] == rjf.loc[i]['证券代码']) & (resDf1['发生日期'] == rjf.loc[i]['发生日期']))]) == 0:
                print('不在jupiter中:%s'%rjf.loc[i]['证券代码'])
                buy_index001 = resDf1001[((resDf1001['证券代码'] == rjf.loc[i]['证券代码']) & (resDf1001['发生日期'] == rjf.loc[i]['发生日期']))].index
                resDf1001.loc[buy_index001, '未完成原因'] = rjf.loc[i]['未完成原因']
            elif len(resDf1001[((resDf1001['证券代码'] == rjf.loc[i]['证券代码']) & (resDf1001['发生日期'] == rjf.loc[i]['发生日期']))]) == 0:
                print('不在jupiterNew中:%s' % rjf.loc[i]['证券代码'])
                buy_index = resDf1[((resDf1['证券代码'] == rjf.loc[i]['证券代码']) & (resDf1['发生日期'] == rjf.loc[i]['发生日期']))].index
                resDf1.loc[buy_index,'未完成原因'] = rjf.loc[i]['未完成原因']
            else:
                print('Both jupiter and jupiterNew:%s' % rjf.loc[i]['证券代码'])
                buy_index = resDf1[((resDf1['证券代码'] == rjf.loc[i]['证券代码']) & (resDf1['发生日期'] == rjf.loc[i]['发生日期']))].index
                resDf1.loc[buy_index, '未完成原因'] = rjf.loc[i]['未完成原因']
                buy_index001 = resDf1001[
                    ((resDf1001['证券代码'] == rjf.loc[i]['证券代码']) & (resDf1001['发生日期'] == rjf.loc[i]['发生日期']))].index
                resDf1001.loc[buy_index001, '未完成原因'] = rjf.loc[i]['未完成原因']

    # --------------------------添加各个模型的预测并汇总到回归模型和分类模型---------------------
    # 读取因子耗时文件
    factor_time_cost = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx'%Adate,sheet_name='因子耗时')

    from ProdWork.Param_config_data import thred_dict_jup_v9 as thred_dict
    model_list = list(thred_dict.keys())
    today_index = resDf1[resDf1['发生日期']==Adate].index
    if '拉抬打压信息' not in resDf1.columns.tolist():
        resDf1['拉抬打压信息'] = np.nan
    for i in today_index:
        stock = resDf1.loc[i,'证券代码']
        this_stock_cla_model_score = 0
        this_stock_reg_model_score = 0
        this_stock_ZT_model_score = 0
        for model in model_list:
            if model+'_probability' in factor_time_cost.columns:
                model_res = (factor_time_cost[factor_time_cost['Unnamed: 0'] == stock][model+'_probability'].values>=thred_dict[model]).sum()
                if 'ZTBysModel_probability' not in factor_time_cost[factor_time_cost['Unnamed: 0'] == stock].columns:
                    if 'Cla' in model:
                        this_stock_cla_model_score += model_res
                    else:
                        this_stock_reg_model_score += model_res
                else:
                    if factor_time_cost[factor_time_cost['Unnamed: 0'] == stock]['ZTBysModel_probability'].isnull().sum() != 1:
                        if ('ZT' in model):
                            this_stock_ZT_model_score += model_res
                    else:
                        if 'Cla' in model:
                            this_stock_cla_model_score += model_res
                        else:
                            this_stock_reg_model_score += model_res
        resDf1.loc[i,'回归信号'] = this_stock_reg_model_score
        resDf1.loc[i,'分类信号'] = this_stock_cla_model_score
        resDf1.loc[i,'前涨停信号'] = this_stock_ZT_model_score
        # if np.isnan(factor_time_cost[factor_time_cost['Unnamed: 0'] == stock]['MRisk_info'].values[0])==False:
        if 'MRisk_info' in factor_time_cost.columns.tolist():
            resDf1.loc[i,'拉抬打压信息'] = factor_time_cost[factor_time_cost['Unnamed: 0'] == stock]['MRisk_info'].values[0]
    #resDf1['level'] = np.nan

    resDf1['level'] = model_lnzt_stack_v3(resDf1[(resDf1['发生日期'] >= '2021-08-25')&(resDf1['发生日期'] <= '2022-02-21')&(resDf1['前涨停信号']==0)].copy()).reindex(resDf1.index)
    resDf1['买入当天持仓金额'] = resDf1['成交数量'] * resDf1['买入当天收盘价']

    from ProdWork.Param_config_data import thred_dict_jup001_v2 as thred_dict001
    model_list001 = list(thred_dict001.keys())
    today_index001 = resDf1001[resDf1001['发生日期'] == Adate].index
    factor_time_cost001 = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate,
                                     sheet_name='因子耗时New')
    if '拉抬打压信息' not in resDf1001.columns.tolist():
        resDf1001['拉抬打压信息'] = np.nan

    for i in today_index001:
        stock = resDf1001.loc[i, '证券代码']
        this_stock_cla_model_score = 0
        this_stock_reg_model_score = 0
        this_stock_ZT_model_score = 0
        for model in model_list001:
            if model + '_probability' in factor_time_cost001.columns:
                factor_time_cost001[model + '_probability'] = factor_time_cost001[model + '_probability'].astype(float)
                model_res = (factor_time_cost001[factor_time_cost001['Unnamed: 0'] == stock][model + '_probability'].values >=
                             thred_dict001[model]).sum()
                if 'ZTBysModel_probability' not in factor_time_cost001[factor_time_cost001['Unnamed: 0'] == stock].columns:
                    if 'Cla' in model:
                        this_stock_cla_model_score += model_res
                    else:
                        this_stock_reg_model_score += model_res
                else:
                    if factor_time_cost001[factor_time_cost001['Unnamed: 0'] == stock][
                        'ZTBysModel_probability'].isnull().sum() != 1:
                        if ('ZT' in model):
                            this_stock_ZT_model_score += model_res
                    else:
                        if 'Cla' in model:
                            this_stock_cla_model_score += model_res
                        else:
                            this_stock_reg_model_score += model_res
        resDf1001.loc[i, '回归信号'] = this_stock_reg_model_score
        resDf1001.loc[i, '分类信号'] = this_stock_cla_model_score
        #resDf1001.loc[i, '前涨停信号'] = this_stock_ZT_model_score
        # if np.isnan(factor_time_cost001[factor_time_cost001['Unnamed: 0'] == stock]['MRisk_info'].values[0]) == False:
        if 'MRisk_info' in factor_time_cost001.columns.tolist():
            resDf1001.loc[i, '拉抬打压信息'] = factor_time_cost001[factor_time_cost001['Unnamed: 0'] == stock]['MRisk_info'].values[0]
    # resDf1['level'] = np.nan

    resDf1001['买入当天持仓金额'] = resDf1001['成交数量'] * resDf1001['买入当天收盘价']

    IO_mother_dir = '/data/group/800080/warehouse_event/'

    f_data = IO.read_data(['20200301', date], columns=['close', 'pre_close'],
                          alt=IO_mother_dir+'prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    print('md_data',f_data.sort_index().tail())
    f_data['zcz'] = (((f_data.reset_index()['Ticker'].apply(lambda x: x[0:3] == '300')) & (
                f_data.reset_index()['dt'] >= '2020-08-24')) |
                     (f_data.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    is_zt = (f_data['close'] == np.floor(f_data['pre_close'] * 100 * 1.1 + 0.5) / 100)
    is_zt[f_data['zcz']] = (f_data['close'] == np.floor(f_data['pre_close'] * 100 * 1.2 + 0.5) / 100)
    last_is_zt = is_zt.unstack().shift().stack()
    sellDf_copy = resDf1.copy()
    sellDf_copy['买入日期'] = sellDf_copy['发生日期'].apply(lambda x: pd.Timestamp(x))
    sellDf_copy = sellDf_copy.rename(columns={'买入日期': 'dt', '证券代码': 'Ticker'}).set_index(['dt', 'Ticker'])
    resDf1['last_is_zt'] = last_is_zt.reindex(sellDf_copy.index).values

    sellDf_copy001 = resDf1001.copy()
    sellDf_copy001['买入日期'] = sellDf_copy001['发生日期'].apply(lambda x: pd.Timestamp(x))
    sellDf_copy001 = sellDf_copy001.rename(columns={'买入日期': 'dt', '证券代码': 'Ticker'}).set_index(['dt', 'Ticker'])
    resDf1001['last_is_zt'] = last_is_zt.reindex(sellDf_copy001.index).values

    # --------------------------添加项目二各个模型的预测并汇总到回归模型和分类模型---------------------
    # 读取因子耗时文件



    # for t_date in s.tradingday('20210621','20210803'):
    #     Adate = t_date[0:4] +'-'+t_date[4:6]+'-'+t_date[6:8]
    #     print(Adate)
    today_index_pj2 = resDf1_pj2[(resDf1_pj2['发生日期']==Adate)].index
    # today_index_pj2 = resDf1_pj2[(resDf1_pj2['发生日期']==Adate) & ((resDf1_pj2['买入时点'].apply(lambda x:int(x))==int(trade_time))).values].index
    for trade_time in ['930','931'][1:]:
        factor_time_cost_pj2 = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate, sheet_name='项目二%s样本'%trade_time)
        model_list_pj2 = list(eval('thred_dict_pj2_%s'%trade_time).keys())
        for i in today_index_pj2:
            stock = resDf1_pj2.loc[i,'证券代码']
            this_stock_cla_model_score,this_stock_reg_model_score = 0,0
            for model in model_list_pj2:
                if model+'_probability' in factor_time_cost_pj2.columns:
                    factor_time_cost_pj2[model + '_probability'] = factor_time_cost_pj2[model + '_probability'].astype(float)
                    model_res = (factor_time_cost_pj2[factor_time_cost_pj2['Unnamed: 0'] == stock][model+'_probability'].values>=eval('thred_dict_pj2_%s'%trade_time)[model]).sum()
                    if 'Cla' in model:
                        this_stock_cla_model_score += model_res
                    else:
                        this_stock_reg_model_score += model_res
            if trade_time == '931':
                resDf1_pj2.loc[i,'回归信号'] = this_stock_reg_model_score
            elif trade_time == '930':
                resDf1_pj2.loc[i,'分类信号'] = this_stock_cla_model_score
    model_rename_pj3_dict1 = {'ceres931cbMoreDjModel': 'cbMoreDjModel',
                         'ceres931cbOneDjModel': 'cbOneDjModel',
                         'ceres931Pct5HighDjModel': 'highPct5DjModel',
                         'ceres931Pct5HighWjModel': 'highPct5XgbModel',
                         'ceres931inTimeXlyModel': 'inTimePMMLModel',
                         'ceres931Pct5LowDjModel': 'lowPct5DjModel',
                         'ceres931Pct5LowWjModel': 'lowPct5XgbModel',
                         'ceres931outTimeXlyModel': 'outTimePMMLModel',
                         'ceres931t1PctHighXlyModel': 't1PctHighPMMLModel',
                         'ceres931t1PctLowXlyModel': 't1PctLowPMMLModel',
                         'ceres931TotalDjModel': 'totalDjModel',
                         'ceres931totalOpenDjModel': 'totalOpenDjModel',
                         'ceres931totalXlyModel': 'totalPMMLModel',
                         'ceres931TotalWjModel': 'totalXgbModel',
                         'ceres931ulLongXlyModel': 'ulLongPMMLModel',
                         'ceres931ulShortXlyModel': 'ulShortPMMLModel'}
    model_rename_pj3_dict = {'ceres931cbMoreDjModel': 'cbMoreDjModel',
                             'ceres931cbOneDjModel': 'cbOneDjModel',
                             'ceres931Pct5HighDjModel': 'highPct5DjModel',
                             'ceres931Pct5HighWjModel': 'highPct5XgbModel',
                             'ceres931inTimeXlyModel': 'inTimePMMLModel',
                             'ceres931Pct5LowDjModel': 'lowPct5DjModel',
                             'ceres931Pct5LowWjModel': 'lowPct5XgbModel',
                             'ceres931outTimeXlyModel': 'outTimePMMLModel',
                             'ceres931t1PctHighXlyModel': 't1PctHighXgbModel',
                             'ceres931t1PctLowXlyModel': 't1PctLowXgbModel',
                             'ceres931TotalDjModel': 'totalDjModel',
                             'ceres931totalOpenDjModel': 'totalOpenDjModel',
                             'ceres931totalXlyModel': 'totalXgbModel',
                            # 'ceres931TotalWjModel': 'totalXgbModel',
                             'ceres931OpenOthWjModel': 'othOpenXgbModel',
                             'ceres931OpenMedWjModel': 'medOpenXgbModel',
                             'ceres931ulLongXlyModel': 'ulLongXgbModel',
                             'ceres931ulShortXlyModel': 'ulShortXgbModel'}
    #thred_dict_pj3_931 = dict(zip())
    today_index_pj3 = resDf1_pj3[(resDf1_pj3['发生日期'] == Adate)].index
    # today_index_pj2 = resDf1_pj2[(resDf1_pj2['发生日期']==Adate) & ((resDf1_pj2['买入时点'].apply(lambda x:int(x))==int(trade_time))).values].index
    for trade_time in ['930', '931'][1:]:
        factor_time_cost_pj3 = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate,
                                             sheet_name='Ceres%s样本' % trade_time)
        model_list_pj3 = list(eval('thred_dict_pj3_%s' % trade_time).keys())
        for i in today_index_pj3:
            stock = resDf1_pj3.loc[i, '证券代码']
            this_stock_cla_model_score, this_stock_reg_model_score = 0, 0
            for model in model_list_pj3:
                model_name = model_rename_pj3_dict[model]
                if model_name + '_probability' in factor_time_cost_pj3.columns:
                    factor_time_cost_pj3[model + '_probability'] = factor_time_cost_pj3[model + '_probability'].astype(
                        float)
                    model_res = (factor_time_cost_pj3[factor_time_cost_pj3['Unnamed: 0'] == stock][
                                     model_name + '_probability'].values >= eval('thred_dict_pj3_%s' % trade_time)[
                                     model]).sum()
                    if 'Cla' in model_name:
                        this_stock_cla_model_score += model_res
                    else:
                        this_stock_reg_model_score += model_res
                else:
                    print(model)
            if trade_time == '931':
                resDf1_pj3.loc[i, '回归信号'] = this_stock_reg_model_score
                resDf1_pj3.loc[i, '分类信号'] = this_stock_cla_model_score
            elif trade_time == '930':
                resDf1_pj3.loc[i, '分类信号'] = this_stock_cla_model_score

    # -------------------------在jupiter买入汇总中添加o2ul的计算-------------------------------------------
    if 'TN_o2ul' not in resDf1.columns:
        resDf1['TN_o2ul'] = np.nan
    o2ul_nan_samples = resDf1[resDf1['TN_o2ul'].isnull()]

    date_ini = o2ul_nan_samples['发生日期'].apply(lambda x:x[:4]+x[5:7]+x[8:10]).min()
    end_date = o2ul_nan_samples['发生日期'].apply(lambda x:x[:4]+x[5:7]+x[8:10]).max()
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
    resDf1_copy = resDf1.copy()
    resDf1_copy['发生日期'] = resDf1_copy['发生日期'].apply(lambda x:pd.Timestamp(x[:4]+x[5:7]+x[8:10]))
    for i in o2ul_nan_samples.index:
        buy_date = resDf1.loc[i]['发生日期']
        stock = resDf1.loc[i]['证券代码']
        resDf1.loc[i,'TN_o2ul'] = 100*md_data.reindex(resDf1_copy.rename(columns = {'发生日期':'dt',
                                  '证券代码':'Ticker'}).set_index(['dt','Ticker']).index)['label_TN_o2ul'].loc[buy_date,stock]
    # -------------------------在jupiterNew买入汇总中添加o2ul的计算-------------------------------------------
    if 'TN_o2ul' not in resDf1001.columns:
        resDf1001['TN_o2ul'] = np.nan
    o2ul_nan_samples001 = resDf1001[resDf1001['TN_o2ul'].isnull()]
    date_ini001 = o2ul_nan_samples001['发生日期'].apply(lambda x: x[:4] + x[5:7] + x[8:10]).min()
    end_date001 = o2ul_nan_samples001['发生日期'].apply(lambda x: x[:4] + x[5:7] + x[8:10]).max()
    end_date001_ = int(s.tradingday(end_date001, 30)[-1])
    md_data = IO.read_data([date_ini001, end_date001_],
                           columns=['pre_close', 'open', 'high', 'low', 'close', 'vwap', 'adjfactor'],
                           alt=IO_mother_dir + '/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    md_data['ul_price'] = np.floor(md_data['pre_close'] * 100 * 1.1 + 0.5) / 100
    md_deal_temp = md_data.reset_index()
    md_deal_temp = md_deal_temp[
        md_deal_temp['Ticker'].apply(lambda x: x[0] == '3') & (md_deal_temp['dt'] >= '20200824')].set_index(
        ['dt', 'Ticker'])
    md_data['ul_price'].loc[md_deal_temp.index] = np.floor(md_deal_temp['pre_close'] * 100 * 1.2 + 0.5) / 100
    md_data['open'], md_data['close'] = md_data['open'] * md_data['adjfactor'], md_data['close'] * md_data['adjfactor']
    md_data['vwap'], md_data['pre_close'] = md_data['vwap'] * md_data['adjfactor'], md_data['pre_close'] * md_data[
        'adjfactor']
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
    resDf1001_copy = resDf1001.copy()
    resDf1001_copy['发生日期'] = resDf1001_copy['发生日期'].apply(lambda x: pd.Timestamp(x[:4] + x[5:7] + x[8:10]))
    for i in o2ul_nan_samples001.index:
        buy_date = resDf1001.loc[i]['发生日期']
        stock = resDf1001.loc[i]['证券代码']
        resDf1001.loc[i, 'TN_o2ul'] = 100 * md_data.reindex(resDf1001_copy.rename(columns={'发生日期': 'dt',
                                                                                     '证券代码': 'Ticker'}).set_index(
            ['dt', 'Ticker']).index)['label_TN_o2ul'].loc[buy_date, stock]


    if 'TN_v2o10' not in resDf1_pj2.columns:
        resDf1_pj2['TN_v2o10'] = np.nan
    if 'TN_v2o10d1' not in resDf1_pj2.columns:
        resDf1_pj2['TN_v2o10d1'] = np.nan
    resDf1_pj2['买入当天持仓金额'] = resDf1_pj2['成交数量'] * resDf1_pj2['买入当天收盘价']
    v2o10_nan_samples_not_today = resDf1_pj2[resDf1_pj2['TN_v2o10'].isnull() & (resDf1_pj2['发生日期']!=Adate) & (resDf1_pj2['买入时点']=='930')]
    v2o10d1_nan_samples_not_today = resDf1_pj2[resDf1_pj2['TN_v2o10d1'].isnull() & (resDf1_pj2['发生日期']!=Adate) & (resDf1_pj2['买入时点']=='931')]

    trade_time_list = ['930', '931']
    need_sample_list = [v2o10_nan_samples_not_today,v2o10d1_nan_samples_not_today]
    for i in range(2):
        nan_samples_here = need_sample_list[i]
        trade_time_here = trade_time_list[i]
        if len(v2o10_nan_samples_not_today) !=0:
            date_ini = nan_samples_here['发生日期'].apply(lambda x:x[:4]+x[5:7]+x[8:10]).min()
            end_date = nan_samples_here['发生日期'].apply(lambda x:x[:4]+x[5:7]+x[8:10]).max()
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
            md_data['next_vwap'] = md_data['vwap'].unstack().shift(-1).stack()
            for index, row in nan_samples_here.iterrows():
                stock = row['证券代码']
                buy_A_date = row['发生日期']
                buy_date = buy_A_date[0:4]+buy_A_date[5:7]+buy_A_date[8:10]
                #saturn_basic_hf_info = pd.read_hdf('/data/group/800463/project/project2_prod/everyday_Basic_v2/%s_%s/Basic_closed_hf_finish_%s_%s.h5' % (buy_date, buy_date, buy_date, buy_date))
                saturn_basic_hf_info = pd.read_hdf(
                    '/data/group/800463/project/project2_prod/daily_data/Basic/Basic_closed_hf_finish.h5')  #
                T_day_x_10_twap_before_ZT = saturn_basic_hf_info['T_day_%s_10_twap_before_ZT'%trade_time_here].loc[buy_date, stock]
                this_buy_price = md_data['adjfactor'].loc[buy_date,stock] * T_day_x_10_twap_before_ZT
                this_label = (md_data['next_vwap'].loc[buy_date,stock]/this_buy_price - 1)*100
                if T_day_x_10_twap_before_ZT == -1:
                    this_label = -1
                if T_day_x_10_twap_before_ZT == -3:
                    this_label = -3
                if trade_time == '930':
                    resDf1_pj2.loc[index,'TN_v2o10'] = this_label
                elif trade_time == '931':
                    resDf1_pj2.loc[index,'TN_v2o10d1'] = this_label
    if 'TN_v2o10' not in resDf1_pj3.columns:
        resDf1_pj3['TN_v2o10'] = np.nan
    if 'TN_v2o10d1' not in resDf1_pj3.columns:
        resDf1_pj3['TN_v2o10d1'] = np.nan
    resDf1_pj3['买入当天持仓金额'] = resDf1_pj3['成交数量'] * resDf1_pj3['买入当天收盘价']
    v2o10_nan_samples_not_today = resDf1_pj3[resDf1_pj3['TN_v2o10'].isnull() & (resDf1_pj3['发生日期'] != Adate) & (resDf1_pj3['买入时点'] == '930')]
    v2o10d1_nan_samples_not_today = resDf1_pj3[
        resDf1_pj3['TN_v2o10d1'].isnull() & (resDf1_pj3['发生日期'] != Adate) & (resDf1_pj3['买入时点'] == '931')]

    trade_time_list = ['930', '931']
    need_sample_list = [v2o10_nan_samples_not_today, v2o10d1_nan_samples_not_today]
    for i in range(1,2):
        nan_samples_here = need_sample_list[i]
        trade_time_here = trade_time_list[i]
        if len(v2o10d1_nan_samples_not_today) != 0:
            date_ini = nan_samples_here['发生日期'].apply(lambda x: x[:4] + x[5:7] + x[8:10]).min()
            end_date = nan_samples_here['发生日期'].apply(lambda x: x[:4] + x[5:7] + x[8:10]).max()
            end_date_ = int(s.tradingday(end_date, 30)[-1])
            md_data = IO.read_data([date_ini, end_date_],
                                   columns=['pre_close', 'open', 'high', 'low', 'close', 'vwap', 'adjfactor'],
                                   alt=IO_mother_dir + '/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
            md_data['ul_price'] = np.floor(md_data['pre_close'] * 100 * 1.1 + 0.5) / 100
            md_deal_temp = md_data.reset_index()
            md_deal_temp = md_deal_temp[
                md_deal_temp['Ticker'].apply(lambda x: x[0] == '3') & (md_deal_temp['dt'] >= '20200824')].set_index(
                ['dt', 'Ticker'])
            md_data['ul_price'].loc[md_deal_temp.index] = np.floor(md_deal_temp['pre_close'] * 100 * 1.2 + 0.5) / 100
            md_data['vwap'], md_data['pre_close'] = md_data['vwap'] * md_data['adjfactor'], md_data['pre_close'] * \
                                                    md_data['adjfactor']
            md_data['high'], md_data['low'] = md_data['high'] * md_data['adjfactor'], md_data['low'] * md_data[
                'adjfactor']
            md_data['ul_price'] = md_data['ul_price'] * md_data['adjfactor']
            md_data.loc[md_data['high'] == md_data['low'], 'vwap'] = np.nan
            md_data['next_vwap'] = md_data['vwap'].unstack().shift(-1).stack()
            for index, row in nan_samples_here.iterrows():
                stock = row['证券代码']
                buy_A_date = row['发生日期']
                buy_date = buy_A_date[0:4] + buy_A_date[5:7] + buy_A_date[8:10]
                ceres_basic_hf_info = pd.read_hdf(
            '/data/group/800463/project/project3_prod/daily_data/%s_v2/Basic_closed_hf_finish_%s_%s.h5' % (buy_date, buy_date, buy_date))
                T_day_x_10_twap_before_ZT = ceres_basic_hf_info['T_day_%s_10_twap_before_ZT' % trade_time_here].loc[
                    buy_date, stock]
                this_buy_price = md_data['adjfactor'].loc[buy_date, stock] * T_day_x_10_twap_before_ZT
                this_label = (md_data['next_vwap'].loc[buy_date, stock] / this_buy_price - 1) * 100
                if T_day_x_10_twap_before_ZT == -1:
                    this_label = -1
                if T_day_x_10_twap_before_ZT == -3:
                    this_label = -3
                if trade_time == '930':
                    resDf1_pj3.loc[index, 'TN_v2o10'] = this_label
                elif trade_time == '931':
                    resDf1_pj3.loc[index, 'TN_v2o10d1'] = this_label



    # -----------------------------增加模拟是否买入模块---------------------------------------
    import pickle
    import datetime as dt
    import numpy as np
    import sys
    sys.path.append("../../")
    sys.path.append("/../..")
    from xquant.factordata import FactorData
    from xquant.xqutils.xqfile import HDFSFile
    import pandas as pd
    # import LabelProfit_zt.spark_LabelBuy_zt as splz
    s = FactorData()
    hf = HDFSFile()
    def change_param(basicDf, input_param_dic):
        today = dt.datetime.now().strftime('%Y%m%d')
        date_list = pd.Series(basicDf.index.get_level_values(0)).apply(lambda x: x.strftime('%Y%m%d'))
        start_date, end_date = min(date_list), max(date_list)
        md_data_path = '/data/group/800080/warehouse_event/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5'
        md_data = IO.read_data([start_date, today], columns=['pre_close', 'close'], alt=md_data_path)
        basicDf['close'], basicDf['pre_close'] = md_data['close'], md_data['pre_close']

        basicDf = basicDf.reset_index()
        basicDf['dt'] = basicDf['dt'].apply(lambda x: x.strftime('%Y%m%d'))
        basicDf['date'] = basicDf['dt'].copy()
        basicDf = basicDf.reset_index().set_index(['date', 'Ticker'])
        basicDf['sell_vol_pct'] = input_param_dic['sell_vol_pct']  # 0.2
        basicDf['max_amt'] = input_param_dic['max_amt']#1000 0000
        basicDf['lag_ms'] = list(pd.Series(basicDf.index.get_level_values(1)).apply(
            lambda x: input_param_dic['lag_ms_SH'] if x[-2:] == 'SH' else input_param_dic['lag_ms_SZ']))
        param_dic = {}
        for index, value in basicDf.iterrows():
            param_dic[index] = dict(value[['sell_vol_pct', 'max_amt', 'lag_ms']])

        for index, value in basicDf.iterrows():
            stock = value.name[1]
            date = value.name[0]
            param_dic[index]['close_price'] = value['close']
            param_dic[index]['ul_price'] = np.floor(value['pre_close'] * 100 * 1.1 + 0.5) / 100
            if (date >= '20200824') & (stock[0] == '3'):
                param_dic[index]['ul_price'] = np.floor(value['pre_close'] * 100 * 1.2 + 0.5) / 100
            else:
                param_dic[index]['ul_price'] = np.floor(value['pre_close'] * 100 * 1.1 + 0.5) / 100

        return param_dic
    def factor_LabelProfit_zt(param, basic_file):
        basic_df = basic_file.copy()
        input_param = change_param(basic_df, param)
        basic_df = basic_df.reset_index()
        # interval_list = list(set(basic_file.reset_index()['dt'].apply(lambda x:x.strftime('%Y%m%d'))))
        from xquant.marketdata import MarketData
        mdp = MarketData()
        import ProdWork.intra_strong.func_LabelBuy_zt as func
        data_list = []
        for index, d in basic_df.iterrows():
            print(d['Ticker'], d['dt'])
            if d['Ticker'] in [ '002131.SZ','000989.SZ']:
                print(d['dt'])
                #pass
            else:
                tradingday_str = d['dt'].strftime('%Y%m%d')
                res_df = func.cal_LabelProfit_zt(d['Ticker'], tradingday_str, d['ZT_Time'], mdp, input_param[(tradingday_str, d['Ticker'])])
                data_list.append(res_df)
        factor_df = pd.concat(data_list, axis=0)
        for factor in ['pct_t1', 'sell_length', 'pct','buy_vol','buy_amt', 'pct_t', 'delta_ms']:
            if factor in factor_df.columns:
                factor_df[factor] = factor_df[factor].astype(float)

        return factor_df

    #param = {'sell_vol_pct': 0.1, 'max_amt': 800 * 10000, 'lag_ms_SH': 450, 'lag_ms_SZ': 100}

    basic_file_raw = resDf1.copy()
    if '模拟是否部成' not in basic_file_raw.columns:
        basic_file_raw['模拟是否部成'] = np.nan
    basic_file_raw.replace('',np.nan,inplace=True)
    basic_file_need = basic_file_raw[basic_file_raw['模拟是否部成'].isnull()]
    def buy_info_2_dt_ticker(basic):
        basic['dt'] = basic['发生日期'].apply(lambda x: pd.Timestamp(str(x)))
        basic['Ticker'] = basic['证券代码']

        basic['ZT_Time'] = basic['买入当日突破时间']
        #basic['ZT_Time'].fillna(93000000,inplace=True)
        # if np.isnan(basic['买入当日突破时间']):
        #     print()
        #     basic['ZT_Time'] = 93100000
        basic = basic.set_index(['dt', 'Ticker'])[['ZT_Time']]
        return basic
    basic_file = buy_info_2_dt_ticker(basic_file_need)
    basic_file_raw_add = basic_file_raw.copy()
    if len(basic_file_need) > 0 and len(basic_file) > 0:
        factor_df = factor_LabelProfit_zt(param, basic_file)
        basic_file_raw.loc[basic_file_need.index,'模拟是否部成'] = (factor_df.reindex(basic_file.index).reset_index()['buy_amt']!=0).values
        unfilled_left = basic_file_raw[(basic_file_raw['发生日期']==Adate)&(basic_file_raw['成交数量']==0)&(basic_file_raw['未完成原因'].isna())&(basic_file_raw['last_is_zt']==0)].index.tolist()
        basic_file_raw.loc[unfilled_left,'未完成原因'] = '未成交'
        # -----------------------------增加下单时间与ZT_Time差别模块---------------------------------------
        basic_file_raw_add = basic_file_raw.copy()
        if '大约下单时间' not in basic_file_raw_add.columns:
            basic_file_raw_add['大约下单时间'] = np.nan
            order_time_basic_file_need = basic_file_raw_add[basic_file_raw_add['大约下单时间'].isnull()]
            order_time_basic_file_need_n = buy_info_2_dt_ticker(order_time_basic_file_need)
            dates_need = np.unique(basic_file_raw_add[basic_file_raw_add['大约下单时间'].isnull()]['发生日期'])
        else:
            order_time_basic_file_need = basic_file_raw_add[basic_file_raw_add['发生日期'] == Adate]
            order_time_basic_file_need_n = buy_info_2_dt_ticker(order_time_basic_file_need)
            dates_need = [Adate]
        tot_res_o = pd.DataFrame()
        for o_tday in dates_need:
            print(o_tday)
            o_tday_s = o_tday[0:4]+o_tday[5:7]+o_tday[8:10]
            tupo_file = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/每日突破/每日突破_%s_prod.xlsx'%o_tday_s,sheet_name='每日订单')
            jupiter_order = tupo_file[tupo_file['orderType'].apply(lambda x:'Shot' in x) &  tupo_file['actionSource'].apply(lambda x:'JupiterNew' not in x) &tupo_file['ordStatus'].apply(lambda x:'PENDING_NEW' in x)]
            jupiter_order['lastMatchTime'] = jupiter_order['lastMatchTime'].apply(lambda x:int(x[11:13]+x[14:16]+x[17:19]+x[20:23]))
            jupiter_order = jupiter_order.groupby('stockcode')['lastMatchTime'].max().reset_index()
            jupiter_order['dt'] = pd.Timestamp(o_tday_s)
            jupiter_order = jupiter_order.rename(columns ={'stockcode':'Ticker'}).set_index(['dt','Ticker'])
            tot_res_o = pd.concat([tot_res_o,jupiter_order])
        tot_res_o['ZT_Time'] = order_time_basic_file_need_n['ZT_Time']
        for index, row in tot_res_o.iterrows():
            ZT_Time = row['ZT_Time']
            lastMatchTime = row['lastMatchTime']
            tot_res_o.loc[index,'大约下单时间'] = cal_time_delta(int(ZT_Time),int(lastMatchTime))
        basic_file_raw_add.loc[order_time_basic_file_need.index,'大约下单时间'] = \
            (tot_res_o['大约下单时间'].reindex(order_time_basic_file_need_n.index).reset_index()['大约下单时间']).values

    basic_file_raw_add_jup = basic_file_raw_add.copy()
    concept_jup = pd.read_hdf(jup_conceptFile).reset_index()
    # lastday_df = concept_jup[concept_jup['dt']==pd.Timestamp('20221128')]
    # lastday_df['dt'] = pd.Timestamp(str(date))
    # concept_jup = pd.concat([concept_jup,lastday_df])
    concept_jup['发生日期'] = concept_jup['dt'].apply(lambda x: pd.Timestamp(x).strftime('%Y-%m-%d'))

    concept_jup.set_index(['发生日期', 'Ticker'], inplace=True)
    basic_file_raw_add_jup = basic_file_raw_add_jup.set_index(['发生日期', '证券代码'])
    basic_file_raw_add_jup['概念名称'] = concept_jup.loc[basic_file_raw_add_jup.index, '概念名称']
    #basic_file_raw_add['拉抬打压信息']
    sel_indx = list(set(basic_file_raw_add_jup.index.tolist())&set(jup_query.index.tolist()))
    basic_file_raw_add_jup['是否触发查询'] = 0
    basic_file_raw_add_jup.loc[sel_indx,'是否触发查询'] = jup_query.loc[sel_indx, 'Flag_query']
    basic_file_raw_add_jup['是否之前有成交'] = 0
    basic_file_raw_add_jup.loc[sel_indx,'是否之前有成交'] = jup_query.loc[sel_indx, 'Flag_has_trade_last3min']
    #basic_file_raw_add_jup = basic_file_raw_add_jup.reset_index()
    writeExcel(basic_file_raw_add_jup.reset_index())

    writeExcel_pj2(resDf1_pj2)
    writeExcel_pj3(resDf1_pj3)

    basic_file_raw = resDf1001.copy()
    if '模拟是否部成' not in basic_file_raw.columns:
        basic_file_raw['模拟是否部成'] = np.nan
    basic_file_raw.replace('',np.nan,inplace=True)
    basic_file_need = basic_file_raw[basic_file_raw['模拟是否部成'].isnull()]

    basic_file = buy_info_2_dt_ticker(basic_file_need)
    factor_df = factor_LabelProfit_zt(param, basic_file)
    basic_file_raw.loc[basic_file_need.index,'模拟是否部成'] = (factor_df.reindex(basic_file.index).reset_index()['buy_amt']!=0).values
    unfilled_left = basic_file_raw[
        (basic_file_raw['发生日期'] == Adate) & (basic_file_raw['成交数量'] == 0) & (basic_file_raw['未完成原因'].isna()) & (
                    basic_file_raw['last_is_zt'] == 0)].index.tolist()
    basic_file_raw.loc[unfilled_left, '未完成原因'] = '本策略未成交'
    # -----------------------------增加下单时间与ZT_Time差别模块---------------------------------------
    basic_file_raw_add = basic_file_raw.copy()
    if '大约下单时间' not in basic_file_raw_add.columns:
        basic_file_raw_add['大约下单时间'] = np.nan
        order_time_basic_file_need = basic_file_raw_add[basic_file_raw_add['大约下单时间'].isnull()]
        order_time_basic_file_need_n = buy_info_2_dt_ticker(order_time_basic_file_need)
        dates_need = np.unique(basic_file_raw_add[basic_file_raw_add['大约下单时间'].isnull()]['发生日期'])
    else:
        order_time_basic_file_need = basic_file_raw_add[basic_file_raw_add['发生日期'] == Adate]
        order_time_basic_file_need_n = buy_info_2_dt_ticker(order_time_basic_file_need)
        dates_need = [Adate]
    tot_res_o = pd.DataFrame()
    for o_tday in dates_need:
        print(o_tday)
        o_tday_s = o_tday[0:4]+o_tday[5:7]+o_tday[8:10]
        tupo_file = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/每日突破/每日突破_%s_prod.xlsx'%o_tday_s,sheet_name='每日订单')
        #
        jupiter_order001 = tupo_file[tupo_file['orderType'].apply(lambda x:'Shot' in x) & tupo_file['actionSource'].apply(lambda x:'JupiterNew' in x) &tupo_file['ordStatus'].apply(lambda x:'PENDING_NEW' in x)]
        jupiter_order001['lastMatchTime'] = jupiter_order001['lastMatchTime'].apply(lambda x:int(x[11:13]+x[14:16]+x[17:19]+x[20:23]))
        jupiter_order001 = jupiter_order001.groupby('stockcode')['lastMatchTime'].min().reset_index()
        jupiter_order001['dt'] = pd.Timestamp(o_tday_s)
        jupiter_order001 = jupiter_order001.rename(columns ={'stockcode':'Ticker'}).set_index(['dt','Ticker'])
        tot_res_o = pd.concat([tot_res_o,jupiter_order001])
    tot_res_o['ZT_Time'] = order_time_basic_file_need_n['ZT_Time']
    for index, row in tot_res_o.iterrows():
        ZT_Time = row['ZT_Time']
        lastMatchTime = row['lastMatchTime'] # if np.isnan(ZT_Time).
        tot_res_o.loc[index,'大约下单时间'] = cal_time_delta(int(ZT_Time),int(lastMatchTime))
    basic_file_raw_add.loc[order_time_basic_file_need.index,'大约下单时间'] = \
        (tot_res_o['大约下单时间'].reindex(order_time_basic_file_need_n.index).reset_index()['大约下单时间']).values
    basic_file_raw_add_jup = basic_file_raw_add_jup.reset_index()
    basic_file_raw_add[(basic_file_raw_add_jup['发生日期'] == Adate)]['Jupiter投票数量'] = np.nan
    basic_file_raw_add[(basic_file_raw_add_jup['发生日期'] == Adate)]['Jupiter成交金额'] = np.nan
    both_buy_stock = list(set(basic_file_raw_add_jup[(basic_file_raw_add_jup['发生日期']==Adate)]['证券代码'].tolist())&set(basic_file_raw_add[(basic_file_raw_add['发生日期']==Adate)]['证券代码'].tolist()))
    for cur_stock in both_buy_stock:
        cur_index = basic_file_raw_add_jup[(basic_file_raw_add_jup['发生日期'] == Adate) & (basic_file_raw_add_jup['证券代码'] == cur_stock)].index
        cur_index001 = basic_file_raw_add[(basic_file_raw_add['发生日期']==Adate)&(basic_file_raw_add['证券代码']==cur_stock)].index
        basic_file_raw_add.loc[cur_index001, ['Jupiter投票数量','Jupiter成交金额']] = basic_file_raw_add_jup.loc[cur_index, ['回归信号','成交金额']].values

    both_trigger_stock = list(set(factor_model_signal.index.tolist())&set(basic_file_raw_add[(basic_file_raw_add['发生日期']==Adate)]['证券代码'].tolist()))
    for cur_stock in both_trigger_stock:
        cur_index001 = basic_file_raw_add[
            (basic_file_raw_add['发生日期'] == Adate) & (basic_file_raw_add['证券代码'] == cur_stock)].index
        basic_file_raw_add.loc[cur_index001, ['Jupiter投票数量']] = factor_model_signal.loc[cur_stock, ['sum_signals']].values
    concept_eur=pd.read_hdf(eur_conceptFile).reset_index()
    # lastday_df = concept_eur[concept_eur['dt'] == pd.Timestamp('20221128')]
    # lastday_df['dt'] = pd.Timestamp(str(date))
    # concept_eur = pd.concat([concept_eur, lastday_df])
    concept_eur['发生日期']=concept_eur['dt'].apply(lambda x: pd.Timestamp(x).strftime('%Y-%m-%d'))
    concept_eur.set_index(['发生日期','Ticker'],inplace=True)
    basic_file_raw_add = basic_file_raw_add.set_index(['发生日期','证券代码'])
    basic_file_raw_add['概念名称']=concept_eur.loc[basic_file_raw_add.index,'概念名称']
    sel_indx = list(set(basic_file_raw_add.index.tolist()) & set(eur_query.index.tolist()))
    basic_file_raw_add['是否触发查询'] = 0
    basic_file_raw_add['是否之前有成交'] = 0
    basic_file_raw_add.loc[sel_indx,'是否触发查询'] = eur_query.loc[sel_indx, 'Flag_query']
    basic_file_raw_add.loc[sel_indx,'是否之前有成交'] = eur_query.loc[sel_indx, 'Flag_has_trade_last3min']
    # basic_file_raw_add['成交金额']- basic_file_raw_add['委托金额']
    writeExcel001(basic_file_raw_add.reset_index())



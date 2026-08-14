# -*- coding: utf-8 -*-
"""
Created on Wed May 22 19:30:47 2019
用于Ceres,包括绘图,Ceres和P4共用这一个
@author: 015614
"""
import pandas as pd
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei'] # 指定默认字体
mpl.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题
fig_width, fig_height = 24, 8
rolldays_num = 5

today_date = dt.datetime.today().strftime('%Y%m%d')
# year_start_date = today_date[:4] + '0101'
year_start_date = '20250101'

# 全部买入信息
def get_buyDfTotalInfo(buyDf, Adate, strategy='Ceres'):
    if len(buyDf)==0:
        return

    if strategy == 'Ceres':
        label_v = 'TN_v2o10d1'
        Label_summary = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发Ceres标签汇总_%s.xlsx' % Adate)
        signal_info_ceres = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate, sheet_name='Ceres样本')
        if len(signal_info_ceres) != 0:
            today_signal_number = signal_info_ceres['shouldBuySignal'].sum()
        else:
            today_signal_number = 0
    elif strategy == 'P4':
        label_v = 'TN_v2o10nd1'
        Label_summary = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发P4标签汇总_%s.xlsx' % Adate)
        signal_info_ceres = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate, sheet_name='P4样本')
        if len(signal_info_ceres) != 0:
            today_signal_number = signal_info_ceres['shouldBuySignal'].sum()
        else:
            today_signal_number = 0
    elif strategy == 'Mimas':
        label_v = 'TN_v2o10dh1'
        Label_summary = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发Mimas标签汇总_%s.xlsx' % Adate)
        signal_info_p4 = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate, sheet_name='Mimas样本')
        if len(signal_info_p4) != 0:
            today_signal_number = signal_info_p4['shouldBuySignal'].sum()
        else:
            today_signal_number = 0

    tot_buy_dt = sorted(list(buyDf['发生日期'].unique()))
    buyResDf = pd.DataFrame(columns=['value'])
    buyResDf.loc['累计交易天数'] = len(buyDf.groupby('发生日期'))
    buyResDf.loc['累计实盘预测为1样本数'] = Label_summary['shouldBuySignal'].sum() + today_signal_number
    buyResDf.loc['累计实盘交易样本数'] = len(buyDf[buyDf['成交数量']!=0])
    buyResDf.loc['次均买入当日收益率'] = '%.2f%%'%(buyDf['买入当日收益率(%)'].mean())
    condition1 = (~np.isnan(buyDf['买入当日收益率(%)']))
    buyResDf.loc['次均成交额加权买入当日收益率'] = '%.2f%%'%((buyDf[condition1]['买入当日收益率(%)']*buyDf[condition1]['成交金额']).sum()/buyDf[condition1]['成交金额'].sum())
    buyResDf.loc['次均成交额均值'] = buyDf['成交金额'].mean()
#    --------------------------------------------------画图------------------------------------------------
    plt.clf()
    fig = plt.figure(figsize = (fig_width, fig_height))
    plt.rcParams['font.size'] = 7
    ABM = fig.add_subplot(2,5,1)
    title_cus_day = "Average Buy Money"
    Average_Daily_Buy_Money = pd.DataFrame(buyDf.groupby('发生日期')['成交金额'].mean())
    Average_Daily_Buy_Money.columns = ['buy_money']
    Average_Daily_Buy_Money.index.name='Date'
    ABM.bar(Average_Daily_Buy_Money.index, Average_Daily_Buy_Money['buy_money'],label = 'buy_money')
    # ---------------------------让坐标看得清---------------------------
    ax = plt.gca()
    for label in ax.get_xticklabels():
        label.set_visible(False)
    for label in ax.get_xticklabels()[::10]:
        label.set_visible(True)
    plt.xticks(rotation=45)
    # ---------------------------让坐标看得清---------------------------
    plt.title(title_cus_day)
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)

    DPS = fig.add_subplot(2,5,2)
    title_cus_day = "Daily Positive Stocks"
    Daily_Positive_Stocks = pd.DataFrame(buyDf.groupby('发生日期').apply(len))
    Daily_Positive_Stocks.columns = ['positive_stocks']
    Daily_Positive_Stocks.index.name = 'Date'
    DPS.bar(Daily_Positive_Stocks.index,Daily_Positive_Stocks['positive_stocks'],label = 'positive_stocks')
    # ---------------------------让坐标看得清---------------------------
    ax = plt.gca()
    for label in ax.get_xticklabels():
        label.set_visible(False)
    for label in ax.get_xticklabels()[::10]:
        label.set_visible(True)
    plt.xticks(rotation=45)
    # ---------------------------让坐标看得清---------------------------
    plt.title(title_cus_day)
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)

    DHA = fig.add_subplot(2, 5, 5)
    title_cus_day = "Daily hold amount"
    Daily_hold_amt = pd.DataFrame(buyDf.groupby('发生日期')['买入当天持仓金额'].sum()).reindex(tot_buy_dt).fillna(0)
    Daily_hold_amt.columns = ['hold_amount']
    Daily_hold_amt.index.name = 'Date'
    DHA.bar(Daily_hold_amt.index, Daily_hold_amt['hold_amount'], label='hold_amount')
    Daily_hold_amt_roll = pd.DataFrame(Daily_hold_amt['hold_amount'].rolling(rolldays_num, 1).mean()).reindex(Daily_hold_amt.index)
    Daily_hold_amt_roll.columns = ['hold_amount_roll%ddays'%rolldays_num]
    Daily_hold_amt_roll.index.name = 'Date'
    DHA.plot(Daily_hold_amt_roll.index, Daily_hold_amt_roll['hold_amount_roll%ddays'%rolldays_num], color='r', label='hold_amount_roll%ddays'%rolldays_num)
    DHA.legend(loc='best')
    # ---------------------------让坐标看得清---------------------------
    ax = plt.gca()
    for label in ax.get_xticklabels():
        label.set_visible(False)
    for label in ax.get_xticklabels()[::10]:
        label.set_visible(True)
    plt.xticks(rotation=45)
    # ---------------------------让坐标看得清---------------------------
    plt.title(title_cus_day)
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)

    return (buyResDf.reset_index()), fig

# 今日买入信息
def get_buyDfTodayInfo(buyDf, buyDate, strategy='Ceres'):
    if strategy=='Ceres':
        today_tot_sample = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % buyDate, sheet_name='Ceres样本')
    elif strategy == 'P4':
        today_tot_sample = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % buyDate, sheet_name='P4样本')
    elif strategy == 'Mimas':
        today_tot_sample = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % buyDate, sheet_name='Mimas样本')
    todayBuyDf = buyDf[(buyDf['发生日期']==buyDate) & (buyDf['成交数量']!=0)]
    if len(todayBuyDf)==0: return
    else:
        todayBuyResDf = pd.DataFrame(columns=['value'])
        todayBuyResDf.loc['样本数量'] = len(today_tot_sample)
        todayBuyResDf.loc['预测为1股票数'] = today_tot_sample['shouldBuySignal'].sum()
        todayBuyResDf.loc['实际买入股票数'] = len(todayBuyDf[todayBuyDf['成交数量']!=0])
        todayBuyResDf.loc['实际买入参与率'] = '%.2f%%'%(100*len(todayBuyDf[todayBuyDf['成交数量']!=0])/len(today_tot_sample))
        todayBuyResDf.loc['总成交额（元）'] = todayBuyDf['成交金额'].sum()
        todayBuyResDf.loc['次均买入当日收益率'] = '%.2f%%' % (todayBuyDf['买入当日收益率(%)'].mean())
        condition1 = (~np.isnan(todayBuyDf['买入当日收益率(%)']))
        todayBuyResDf.loc['次均成交额加权买入当日收益率'] = '%.2f%%'%((todayBuyDf[condition1]['买入当日收益率(%)']*todayBuyDf[condition1]['成交金额']).sum()/todayBuyDf[condition1]['成交金额'].sum())
        todayBuyResDf.loc['次均成交额均值'] = np.nanmean(todayBuyDf['成交金额'])
        todayBuyDf.replace(np.nan,'',inplace=True)
        return todayBuyResDf.reset_index()

# 全部卖出信息
def get_sellDfTotalInfo(sellDf, Adate, fig, strategy='Ceres'):
    if strategy == 'Ceres':
        label_v = 'TN_v2o10d1'
        Label_summary = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发Ceres标签汇总_%s.xlsx' % Adate)
    elif strategy == 'P4':
        label_v = 'TN_v2o10nd1'
        Label_summary = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发P4标签汇总_%s.xlsx' % Adate)
    elif strategy == 'Mimas':
        label_v = 'TN_v2o10dh1'
        Label_summary = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发Mimas标签汇总_%s.xlsx' % Adate)

    sellDf_this = sellDf.copy()
    sellResDf = pd.DataFrame(columns=['value'])
    sellSampleDf = sellDf_this[(sellDf_this['是否全部卖出']==1) | (sellDf_this['是否全部卖出']==0)]
    sellSampleDf['加权收益率'] = sellSampleDf['买入金额']*sellSampleDf['卖出部分收益率(%)']
    sellResDf.loc['累计全部卖出样本数'] = len(sellSampleDf)
    sellResDf.loc['累计盈利'] = sellDf_this[(sellDf_this['是否全部卖出']==1)|(sellDf_this['是否全部卖出']==0)]['卖出部分盈利金额'].sum()
    sellResDf.loc['次均等权卖出收益率(%)'] = '%.2f%%'%(sellSampleDf['卖出部分收益率(%)'].mean())
    sellResDf.loc['次均成交额加权收益率(%)'] = '%.2f%%'%(sellSampleDf['加权收益率'].sum()/sellSampleDf['买入金额'].sum())
    sellResDf.loc['累计参与率'] = '%.2f%%' % (Label_summary['shouldBuySignal'].sum() / len(Label_summary) * 100)
    sellResDf.loc['累计交易胜率'] = '' if len(sellSampleDf)==0 else '%.2f%%' % (len(sellSampleDf[sellSampleDf['实际是否正收益'] == 1]) / len(sellSampleDf) * 100)

    #    --------------------------------------------------画图------------------------------------------------
    if len(Label_summary.dt.unique())<=rolldays_num:
        print('%s目前运行天数不足, %d天！！！！！！！！！！'%(strategy,len(Label_summary.dt.unique())))
    else:
        CPs = fig.add_subplot(2,5,4)
        title_cus_day = "Cumulated Profit"
        Label_summary['real_positive'] = (Label_summary[label_v]>0)
        Label_summary['dt'] = Label_summary['dt'].apply(lambda x:x.strftime('%Y-%m-%d'))
        Label_summary_stats_dummy = Label_summary.groupby(['dt']).apply(lambda x:len(x))
        tempDf = sellDf_this[(sellDf_this['是否全部卖出']==1)|(sellDf_this['是否全部卖出']==0)].groupby(['买入日期'])['卖出部分盈利金额'].sum().cumsum().reindex(Label_summary_stats_dummy.index).fillna(method = 'ffill')
        tempDf = pd.DataFrame(tempDf)
        tempDf.columns = ['cumulated_profit']
        tempDf.index.name = 'Buy_Date'

        if strategy == 'Ceres':
            CPs.plot(tempDf[['cumulated_profit']], 'b')
            CPs.legend(['931'], loc='best')
        elif strategy == 'P4':
            CPs.plot(tempDf[['cumulated_profit']], 'b')
            CPs.legend(['931'], loc='best')
        # ---------------------------让坐标看得清---------------------------
        ax = plt.gca()
        for label in ax.get_xticklabels():
            label.set_visible(False)
        for label in ax.get_xticklabels()[::10]:
            label.set_visible(True)
        plt.xticks(rotation=45)
        # ---------------------------让坐标看得清---------------------------
        plt.title(title_cus_day)

        MWDAP = fig.add_subplot(2,5,3)
        title_cus_day = "Money Weighted Daily Average Profit(%)"
        Daily_Average_Sell_Profit = pd.DataFrame(np.divide(sellSampleDf.groupby('买入日期')['加权收益率'].sum(),sellSampleDf.groupby('买入日期')['买入金额'].sum()))
        Daily_Average_Sell_Profit.columns = ['average_profit']

        Daily_Average_Sell_Profit_positive = Daily_Average_Sell_Profit[Daily_Average_Sell_Profit['average_profit'] >= 0].reindex(Daily_Average_Sell_Profit.index).fillna(0)
        Daily_Average_Sell_Profit_positive.columns = ['postive_average']
        MWDAP.bar(Daily_Average_Sell_Profit_positive.index, Daily_Average_Sell_Profit_positive['postive_average'],label='postive_average')
        MWDAP.hold(True)
        Daily_Average_Sell_Profit_negative = Daily_Average_Sell_Profit[ Daily_Average_Sell_Profit['average_profit'] < 0].reindex(Daily_Average_Sell_Profit.index).fillna(0)
        Daily_Average_Sell_Profit_negative.columns = ['negtive_average']
        MWDAP.bar(Daily_Average_Sell_Profit_negative.index, Daily_Average_Sell_Profit_negative['negtive_average'],color='r',label='negtive_average')
        Daily_Average_Sell_Profit_roll5 = pd.DataFrame(
            Daily_Average_Sell_Profit['average_profit'].rolling(rolldays_num, 1).mean())
        Daily_Average_Sell_Profit_roll5.columns = ['average_roll%sdays' % str(rolldays_num)]
        Daily_Average_Sell_Profit_roll5.index.name = 'Date'
        # MWDAP.plot(Daily_Average_Sell_Profit_roll5['average_profit_roll%sdays'%str(rolldays_num)],'g',Daily_Average_Sell_Profit_positive['average_profit'].rolling(rolldays_num, 1).mean(),'b',Daily_Average_Sell_Profit_negative['average_profit'].rolling(rolldays_num, 1).mean(),'r' )
        MWDAP.plot(Daily_Average_Sell_Profit_roll5.index,
                   Daily_Average_Sell_Profit_roll5['average_roll%sdays' % str(rolldays_num)], color='g',
                   label='average_roll%sdays' % str(rolldays_num))
        MWDAP.legend(loc='best')

        if strategy == 'Ceres':
            plt.savefig("/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/收益画图/%s_%s_ceres.png" % (Adate, '生产环境'), dpi=120)
        elif strategy == 'P4':
            plt.savefig("/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/收益画图/%s_%s_p4.png" % (Adate, '生产环境'), dpi=120)
        elif strategy == 'Mimas':
            plt.savefig("/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/收益画图/%s_%s_mimas.png" % (Adate, '生产环境'), dpi=120)
    return sellResDf.reset_index()

def get_sellDfTodayInfo(sellDf, sellDate):
    todaySellDf = sellDf[sellDf['卖出日期'].notnull()][sellDf['卖出日期'].dropna().apply(lambda x: sellDate in x)]
    if len(todaySellDf) == 0:
        return
    todaySellDf.replace(np.nan, '', inplace=True)
    todaySellResDf = pd.DataFrame(columns=['value'])
    todaySellResDf.loc['全部卖出股票数'] = len(todaySellDf)

    def return_last_comma(data):
        if (type(data) == float) | (type(data) == int):
            return data
        else:
            return float(data.split(',')[~0])

    todaySellResDf.loc['卖出盈利（元）'] = ((todaySellDf['卖出成交均价'].apply(return_last_comma) * 0.9995 - todaySellDf['买入成交均价']) *
                                     todaySellDf['卖出数量'].apply(return_last_comma)).sum()

    todaySellResDf.loc['次均等权卖出收益率(%)'] = '%.2f%%' % ((todaySellDf['卖出成交均价'].apply(return_last_comma) / todaySellDf['买入成交均价'] - 1).mean() * 100)
    todaySellResDf.loc['次均成交额加权收益率(%)'] = '%.2f%%' % (
                100 * ((todaySellDf['买入成交均价'] * todaySellDf['卖出数量'].apply(return_last_comma)) * (todaySellDf['卖出成交均价'].apply(return_last_comma) / todaySellDf['买入成交均价'] - 1)).sum() / \
                ((todaySellDf['买入成交均价'] * todaySellDf['卖出数量'].apply(return_last_comma)).sum()))
    todaySellResDf.loc['今日卖出胜率'] = '%.2f%%' % (((todaySellDf['卖出成交均价'].apply(return_last_comma) - todaySellDf['买入成交均价']) > 0).sum() / len(todaySellDf) * 100)
    return todaySellResDf.reset_index()
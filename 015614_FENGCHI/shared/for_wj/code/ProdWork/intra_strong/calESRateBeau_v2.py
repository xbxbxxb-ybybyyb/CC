# -*- coding: utf-8 -*-
"""
Created on Wed May 22 19:30:47 2019
用于saturn,包括绘图
@author: 013551
"""
import pandas as pd
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei'] # 指定默认字体
mpl.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题
fig_width, fig_height = 24,8
rolldays_num = 5
# 全部买入信息
def get_buyDfTotalInfo(buyDf,Adate,trade_time,strategy='saturn'):
    if len(buyDf)==0:
        return
    if trade_time == 930:
        label_v, label_c = 'TN_v2o10', 'T_c2o10'
        Label_summary = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发项目二标签汇总_%s.xlsx' % Adate)

    elif trade_time == 931:
        label_v , label_c = 'TN_v2o10d1', 'T_c2o10d1'
        Label_summary = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发项目二931标签汇总_%s.xlsx' % Adate)
        if strategy == 'ceres':
            if os.path.exists('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发项目三931标签汇总_%s.xlsx' % Adate):
                Label_summary = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发项目三931标签汇总_%s.xlsx' % Adate)
            else:
                Label_summary = pd.DataFrame()
    signal_info_pj2 = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate, sheet_name='项目二%d样本'%trade_time)
    if trade_time == 930:
        signal_info_pj2['p2shouldBuySignal'] = False
    if strategy == 'ceres':
        signal_info_pj2 = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Adate,
                                        sheet_name='Ceres%d样本' % trade_time)
    if len(signal_info_pj2) != 0:
        if strategy == 'saturn':
            today_signal_number = signal_info_pj2['p2shouldBuySignal'].sum()
        elif strategy == 'ceres':
            today_signal_number = signal_info_pj2['p3shouldBuySignal'].sum()
    else:
        today_signal_number = 0
    tot_buy_dt = sorted(list(buyDf['发生日期'].unique()))
    buyResDf = pd.DataFrame(columns=['value'])
    buyResDf.loc['累计交易天数'] = len(buyDf.groupby('发生日期'))
    if strategy == 'saturn':
        buyResDf.loc['累计实盘预测为1样本数'] = Label_summary['p2shouldBuySignal'].sum() + today_signal_number
    elif strategy == 'ceres':
        buyResDf.loc['累计实盘预测为1样本数'] = Label_summary['p3shouldBuySignal'].sum() + today_signal_number
    buyResDf.loc['累计实盘交易样本数'] = len(buyDf[buyDf['成交数量']!=0])
    buyResDf.loc['次均买入当日收益率'] = '%.2f%%'%(buyDf['买入当日收益率(%)'].mean())
    condition1 = (~np.isnan(buyDf['买入当日收益率(%)']))
    buyResDf.loc['次均成交额加权买入当日收益率'] = '%.2f%%'%((buyDf[condition1]['买入当日收益率(%)']*buyDf[condition1]['成交金额']).sum()/buyDf[condition1]['成交金额'].sum())
    buyResDf.loc['次均成交额均值'] = buyDf['成交金额'].mean()
    buyResDf.loc['累计下单收盘涨停比例'] = '%.2f%%' % (buyDf['买入当天是否收盘涨停'].sum() / len(buyDf) * 100)
#    --------------------------------------------------画图------------------------------------------------
    plt.clf()
    fig = plt.figure(figsize = (fig_width, fig_height))
    plt.rcParams['font.size'] = 7
    ABM = fig.add_subplot(2,5,1)
    title_cus_day = "Average Buy Money"
    Average_Daily_Buy_Money = pd.DataFrame(buyDf.groupby('发生日期')['成交金额'].mean())
    Average_Daily_Buy_Money.columns = ['buy_money']
    Average_Daily_Buy_Money.index.name='Date'
    ABM.bar(Average_Daily_Buy_Money.index,Average_Daily_Buy_Money['buy_money'],label = 'buy_money')
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
    #buyDf['买入当天持仓金额']=buyDf['买入当天持仓金额'].astype(float)
    Daily_hold_amt = pd.DataFrame(buyDf.groupby('发生日期')['买入当天持仓金额'].sum()).reindex(tot_buy_dt).fillna(0)#.rolling(rolldays_num,1).mean()
    Daily_hold_amt.columns = ['hold_amount']
    Daily_hold_amt.index.name = 'Date'
    DHA.bar(Daily_hold_amt.index, Daily_hold_amt['hold_amount'], label='hold_amount')
    Daily_hold_amt_roll = pd.DataFrame(Daily_hold_amt['hold_amount'].rolling(rolldays_num, 1).mean()).reindex(Daily_hold_amt.index)
    Daily_hold_amt_roll.columns = ['hold_amount_roll%ddays'%rolldays_num]
    Daily_hold_amt_roll.index.name = 'Date'
    DHA.plot(Daily_hold_amt_roll.index, Daily_hold_amt_roll['hold_amount_roll%ddays'%rolldays_num], color='r', label='hold_amount_roll%ddays'%rolldays_num)
    # actbuyday.vlines('2020-06-03', ymin=0, ymax=1.2, colors='r', linestyles='--')
    DHA.legend(loc='best')
    #DPS.set_ylim(0, 1.2)
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


    #    --------------------------------------------------画图------------------------------------------------
    # 我们买的样本信息
    # 填补项目2买入记录中TN_v2o10为nan的问题
    buyDf_tmp = buyDf.copy()
    #buyDf_tmp['dt'] = buyDf['发生日期'].apply(lambda x: pd.Timestamp(x))
    buyDf_tmp.set_index(['发生日期','证券代码'],inplace=True)
    Label_summary_tmp = Label_summary.copy()
    Label_summary_tmp['dt'] = Label_summary_tmp['dt'].apply(lambda x: x.strftime('%Y-%m-%d'))
    Label_summary_tmp.set_index(['dt', 'Ticker'], inplace=True)
    indexset = list(set(buyDf_tmp[buyDf_tmp[label_v].isna()].index.tolist())&set(Label_summary_tmp.index.tolist()))
    print('before fill, v2o10 nan num is:', buyDf[buyDf[label_v].isna()].shape[0])
    if len(indexset)>0:
        print('%s 存在 nan，数量为%d。'%(label_v,len(indexset)))
        buyDf_tmp.loc[indexset,label_v] = Label_summary_tmp.loc[indexset,label_v]
        buyDf = buyDf_tmp.copy()
    print('after fill, v2o10 nan num is:',buyDf[buyDf[label_v].isna()].shape[0])
    signal_label = buyDf.groupby('发生日期').apply(lambda x:pd.Series({'信号总数':len(x)
                                                                      ,'收盘涨停数量':(x['买入当天是否收盘涨停']==1).sum()
                                                                      ,'盘中涨停数量':(x['买入当天盘中是否涨停']==1).sum()
                                                                      ,'买入当日收益率总和':x['买入当日收益率(%)'].sum()
                                                                      ,'买入当日开盘涨幅总和':x['买入当天开盘涨幅(%)'].sum()
                                                                      ,'高开数量':(x['买入当天开盘涨幅(%)']>0).sum()
                                                                   ,'高开样本买入日收益率总和':(x[x['买入当天开盘涨幅(%)']>0]['买入当日收益率(%)']).sum()
                                                                   ,'低开样本买入日收益率总和':(x[x['买入当天开盘涨幅(%)']<=0]['买入当日收益率(%)']).sum()
                                                                      , '高开样本收益率总和': (x[x['买入当天开盘涨幅(%)'] > 0][label_v]).sum()
                                                                      , '低开样本收益率总和': (x[x['买入当天开盘涨幅(%)'] <= 0][label_v]).sum()
                                                                   }))

    # 全部触发样本信息
    import datetime as dt
    from xquant.factordata import FactorData
    s = FactorData()
    # date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'),-1)[0]
    # Adate = date[0:4]+'-'+date[4:6]+'-'+date[6:8]
    date = str(Adate).replace('-', '')
    print('current date = %s' % date)
    lastdate = s.tradingday(date, -2)[0]
    Alastdate = lastdate[0:4]+'-'+lastdate[4:6]+'-'+lastdate[6:8]
    # date = '20210628'
    # Adate = '2021-06-28'
    # lastdate = '20210625'
    # Alastdate = '2021-06-25'

    Label_summary['real_positive'] = (Label_summary[label_v]>0)
    Label_summary['dt'] = Label_summary['dt'].apply(lambda x:x.strftime('%Y-%m-%d'))
    Label_summary_stats = Label_summary.groupby('dt').apply(lambda x:pd.Series({'触发总数':len(x)
                                                                                ,'收盘涨停数量': x['close_zt'].sum()
                                                                                ,'盘中涨停数量': x['high_zt'].sum()
                                                                                ,'买入当日收益率总和': x[label_c].sum()
                                                                                ,'买入当日开盘涨幅总和': x['T_o2pre'].sum()
                                                                                ,'高开数量':(x['T_o2pre']>0).sum()
                                                                               , '高开样本买入日收益率总和': (x[x['T_o2pre'] > 0][label_c]).sum()
                                                                                , '低开样本买入日收益率总和': (x[x['T_o2pre'] <= 0][label_c]).sum()
                                                                               , '高开样本收益率总和': (x[x['T_o2pre'] > 0][label_v]).sum()
                                                                                , '低开样本收益率总和': (x[x['T_o2pre'] <= 0][label_v]).sum()}))
    signal_label_rolling_3 = signal_label.reindex(Label_summary_stats.index).fillna(0).rolling(rolldays_num,1).sum()
    Label_summary_stats_rolling_3 = Label_summary_stats.rolling(rolldays_num,1).sum()
    if len(Label_summary_stats_rolling_3)<=rolldays_num or len(signal_label_rolling_3)<=rolldays_num:
        print('%s,第一天没有足够的数据，不足%d日！！！！！！！！！！'%(strategy,rolldays_num))
        pass
    else:
        RZTs = fig.add_subplot(2,5,9)
        title_cus_day = 'High-Low Open ' + label_v + '(%) '+'(Rolling %s days)'%str(rolldays_num)
        Ho_TNv2o10_rolling_3 = pd.DataFrame(signal_label_rolling_3['高开样本收益率总和']/signal_label_rolling_3['信号总数']).loc[:Alastdate]
        Ho_TNv2o10_rolling_3.columns = ['Ho_%s'%label_v]
        Ho_TNv2o10_rolling_3.index.name = 'Buy_Date'

        Lo_TNv2o10_rolling_3 = pd.DataFrame(signal_label_rolling_3['低开样本收益率总和']/signal_label_rolling_3['信号总数']).loc[:Alastdate]
        Lo_TNv2o10_rolling_3.columns = ['Lo_%s'%label_v]
        Lo_TNv2o10_rolling_3.index.name = 'Buy_Date'

        all_Ho_TNv2o10_rolling_3 = pd.DataFrame(Label_summary_stats_rolling_3['高开样本收益率总和']/Label_summary_stats_rolling_3['触发总数'])
        all_Ho_TNv2o10_rolling_3.columns = ['Ho_%s'%label_v]
        all_Ho_TNv2o10_rolling_3.index.name = 'Buy_Date'

        all_Lo_TNv2o10_rolling_3 = pd.DataFrame(Label_summary_stats_rolling_3['低开样本收益率总和']/Label_summary_stats_rolling_3['触发总数'])
        all_Lo_TNv2o10_rolling_3.columns = ['Lo_%s'%label_v]
        all_Lo_TNv2o10_rolling_3.index.name = 'Buy_Date'

        RZTs.plot(Ho_TNv2o10_rolling_3[['Ho_%s'%label_v]],'r',
                     Lo_TNv2o10_rolling_3[['Lo_%s'%label_v]],'b',
                     all_Ho_TNv2o10_rolling_3[['Ho_%s'%label_v]],'r--',
                     all_Lo_TNv2o10_rolling_3[['Lo_%s'%label_v]],'b--')
        RZTs.legend(['Ho_%s'%label_v,'Lo_%s'%label_v,'triggered_Ho_%s'%label_v,'triggered_Lo_%s'%label_v],loc = 'best')
        # L4O2ULs.vlines('2020-06-03',ymin = -4,ymax = 6,colors = 'black',linestyles = '--')
        # ---------------------------让坐标看得清---------------------------
        ax = plt.gca()
        for label in ax.get_xticklabels():
            label.set_visible(False)
        for label in ax.get_xticklabels()[::10]:
            label.set_visible(True)
        plt.xticks(rotation=45)
        # ---------------------------让坐标看得清---------------------------
        plt.title(title_cus_day)

        PTs = fig.add_subplot(2,5,6)
        title_cus_day = 'Signal Triggered High Open (Rolling %s days)'%str(rolldays_num)
        pre_10_zt = pd.DataFrame(signal_label_rolling_3['高开数量']/signal_label_rolling_3['信号总数']).loc[:Alastdate]
        pre_10_zt.columns = ['high_open']
        pre_10_zt.index.name = 'Buy_Date'
        pre_10_zt_all = pd.DataFrame(Label_summary_stats_rolling_3['高开数量'] / Label_summary_stats_rolling_3['触发总数'])
        pre_10_zt_all.columns = ['high_open_all']
        pre_10_zt_all.index.name = 'Buy_Date'
        PTs.plot(pre_10_zt['high_open'],'b',
                 pre_10_zt_all['high_open_all'],'b--')
        PTs.legend(['signal','all_triggered'],loc = 'best')
        # ---------------------------让坐标看得清---------------------------
        ax = plt.gca()
        for label in ax.get_xticklabels():
            label.set_visible(False)
        for label in ax.get_xticklabels()[::10]:
            label.set_visible(True)
        plt.xticks(rotation=45)
        # ---------------------------让坐标看得清---------------------------
        plt.title(title_cus_day)

        L4O2ULs = fig.add_subplot(2,5,8)
        title_cus_day = 'High-Low Open ' + label_c + '(%) '+'(Rolling %s days)'%str(rolldays_num)
        Ho_Tc2o10_rolling_3 = pd.DataFrame(signal_label_rolling_3['高开样本买入日收益率总和']/signal_label_rolling_3['信号总数']).loc[:Alastdate]
        Ho_Tc2o10_rolling_3.columns = ['Ho_%s'%label_c]
        Ho_Tc2o10_rolling_3.index.name = 'Buy_Date'

        Lo_Tc2o10_rolling_3 = pd.DataFrame(signal_label_rolling_3['低开样本买入日收益率总和']/signal_label_rolling_3['信号总数']).loc[:Alastdate]
        Lo_Tc2o10_rolling_3.columns = ['Lo_%s'%label_c]
        Lo_Tc2o10_rolling_3.index.name = 'Buy_Date'

        all_Ho_Tc2o10_rolling_3 = pd.DataFrame(Label_summary_stats_rolling_3['高开样本买入日收益率总和']/Label_summary_stats_rolling_3['触发总数'])
        all_Ho_Tc2o10_rolling_3.columns = ['Ho_%s'%label_c]
        all_Ho_Tc2o10_rolling_3.index.name = 'Buy_Date'

        all_Lo_Tc2o10_rolling_3 = pd.DataFrame(Label_summary_stats_rolling_3['低开样本买入日收益率总和']/Label_summary_stats_rolling_3['触发总数'])
        all_Lo_Tc2o10_rolling_3.columns = ['Lo_%s'%label_c]
        all_Lo_Tc2o10_rolling_3.index.name = 'Buy_Date'

        L4O2ULs.plot(Ho_Tc2o10_rolling_3[['Ho_%s'%label_c]],'r',
                     Lo_Tc2o10_rolling_3[['Lo_%s'%label_c]],'b',
                     all_Ho_Tc2o10_rolling_3[['Ho_%s'%label_c]],'r--',
                     all_Lo_Tc2o10_rolling_3[['Lo_%s'%label_c]],'b--')
        L4O2ULs.legend(['Ho_%s'%label_c,'Lo_%s'%label_c,'triggered_Ho_%s'%label_c,'triggered_Lo_%s'%label_c],loc = 'best')
        # L4O2ULs.vlines('2020-06-03',ymin = -4,ymax = 6,colors = 'black',linestyles = '--')
        # ---------------------------让坐标看得清---------------------------
        ax = plt.gca()
        for label in ax.get_xticklabels():
            label.set_visible(False)
        for label in ax.get_xticklabels()[::10]:
            label.set_visible(True)
        plt.xticks(rotation=45)
        # ---------------------------让坐标看得清---------------------------
        plt.title(title_cus_day)

        MRWs = fig.add_subplot(2,5,7)
        title_cus_day = 'Model Performance (Rolling %s days)'%str(rolldays_num)
        if strategy=='saturn':
            Recal_raw = Label_summary.groupby(['dt']).apply(lambda x:pd.Series({'总正样本数量':x['real_positive'].sum(),
                                                                        '预测正确正样本数量':(x['real_positive']&x['p2shouldBuySignal']).sum(),
                                                                        '预测正样本数量':x['p2shouldBuySignal'].sum()}))
        elif strategy=='ceres':
            Recal_raw = Label_summary.groupby(['dt']).apply(lambda x: pd.Series({'总正样本数量': x['real_positive'].sum(),
                                                                                 '预测正确正样本数量': (x['real_positive'] & x[
                                                                                     'p3shouldBuySignal']).sum(),
                                                                                 '预测正样本数量': x[
                                                                                     'p3shouldBuySignal'].sum()}))
        Recal_raw_rolling_3_sum = Recal_raw.rolling(rolldays_num,rolldays_num).sum()

        Recal_rolling_3 = pd.DataFrame(Recal_raw_rolling_3_sum['预测正确正样本数量']/Recal_raw_rolling_3_sum['总正样本数量'])
        Recal_rolling_3.columns = ['Recall_rolling_3']
        Recal_rolling_3.index.name = 'Buy_Date'
        Wining_rolling_3 = pd.DataFrame(Recal_raw_rolling_3_sum['预测正确正样本数量']/Recal_raw_rolling_3_sum['预测正样本数量'])
        Wining_rolling_3.columns = ['Wining_rolling_3']
        Wining_rolling_3.index.name = 'Buy_Date'

        MRWs.plot(Recal_rolling_3[['Recall_rolling_3']]
                  .join(Wining_rolling_3[['Wining_rolling_3']]))

        # MRWs.vlines('2020-06-03',ymin = 0,ymax = 1,colors = 'r',linestyles = '--')
        MRWs.legend(['recall','winning'],loc = 'best')
        # ---------------------------让坐标看得清---------------------------
        ax = plt.gca()
        for label in ax.get_xticklabels():
            label.set_visible(False)
        for label in ax.get_xticklabels()[::10]:
            label.set_visible(True)
        plt.xticks(rotation=45)
        # ---------------------------让坐标看得清---------------------------
        plt.title(title_cus_day)


    # plt.savefig("/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/收益画图/%s/%s_%s.png" % (Adate,'trial', Adate))
    #plt.savefig("/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/收益画图/%s/%s_%s.png" % (Adate,title_cus_day, Adate))

#    --------------------------------------------------画图------------------------------------------------
    return (buyResDf.reset_index()),fig
# 今日买入信息
def get_buyDfTodayInfo(buyDf,buyDate,trade_time,strategy='saturn'):
    buyDf = buyDf[buyDf['买入时点']==trade_time]
    today_tot_sample = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx'%buyDate,sheet_name='项目二%d样本'%trade_time)
    if strategy=='ceres':
        today_tot_sample = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % buyDate,
                                         sheet_name='Ceres%d样本' % trade_time)
    todayBuyDf = buyDf[(buyDf['发生日期']==buyDate) & (buyDf['成交数量']!=0)]
    if len(todayBuyDf)==0: return
    else:
        todayBuyResDf = pd.DataFrame(columns=['value'])
        todayBuyResDf.loc['样本数量'] = len(today_tot_sample)
        if strategy=='saturn':
            todayBuyResDf.loc['预测为1股票数'] = today_tot_sample['p2shouldBuySignal'].sum()
        elif strategy=='ceres':
            todayBuyResDf.loc['预测为1股票数'] = today_tot_sample['p3shouldBuySignal'].sum()
        todayBuyResDf.loc['实际买入股票数'] = len(todayBuyDf[todayBuyDf['成交数量']!=0])
        todayBuyResDf.loc['实际买入参与率'] = '%.2f%%'%(100*len(todayBuyDf[todayBuyDf['成交数量']!=0])/len(today_tot_sample))
        todayBuyResDf.loc['总成交额（元）'] = todayBuyDf['成交金额'].sum()
        todayBuyResDf.loc['次均买入当日收益率'] = ('%.2f%%')%(todayBuyDf['买入当日收益率(%)'].mean())
        condition1 = (~np.isnan(todayBuyDf['买入当日收益率(%)']))
        todayBuyResDf.loc['次均成交额加权买入当日收益率'] = '%.2f%%'%((todayBuyDf[condition1]['买入当日收益率(%)']*todayBuyDf[condition1]['成交金额']).sum()/todayBuyDf[condition1]['成交金额'].sum())
        todayBuyResDf.loc['次均成交额均值'] = np.nanmean(todayBuyDf['成交金额'])
        todayBuyDf.replace(np.nan,'',inplace=True)
        todayBuyResDf.loc['实际买入股票当日收盘涨停比例'] = format(len(todayBuyDf[todayBuyDf['买入当天是否收盘涨停']==1])/len(todayBuyDf[todayBuyDf['买入当天是否收盘涨停']!='']),'.00%')
        return todayBuyResDf.reset_index()

# 全部卖出信息
def get_sellDfTotalInfo(sellDf,Adate,fig,trade_time,strategy='saturn'):
    # import datetime as dt
    # Adate = dt.datetime.now().strftime('%Y') + '-' + dt.datetime.now().strftime('%m') + '-' + dt.datetime.now().strftime('%d')
    # date = '20210319'
    # Adate = '2021-03-19'
    if trade_time == 930:
        label_v = 'TN_v2o10'
        Label_summary = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发项目二标签汇总_%s.xlsx' % Adate)
    elif trade_time == 931:
        label_v = 'TN_v2o10d1'

        Label_summary = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发项目二931标签汇总_%s.xlsx' % Adate)
        if strategy == 'ceres':
            Label_summary = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发项目三931标签汇总_%s.xlsx' % Adate)
    sellDf_this = sellDf[sellDf['买入时点']==trade_time]
    if strategy=='saturn':
        labels_p2 = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发项目二标签汇总_%s.xlsx' % Adate)
    elif strategy=='ceres':
        labels_p2 = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发项目三931标签汇总_%s.xlsx' % Adate)
    sellResDf = pd.DataFrame(columns=['value'])
    sellSampleDf = sellDf_this[(sellDf_this['是否全部卖出']==1) | (sellDf_this['是否全部卖出']==0)]
    sellSampleDf['加权收益率'] = sellSampleDf['买入金额']*sellSampleDf['卖出部分收益率(%)']
    sellResDf.loc['累计全部卖出样本数'] = len(sellSampleDf)
    sellResDf.loc['累计盈利'] = sellDf_this[(sellDf_this['是否全部卖出']==1)|(sellDf_this['是否全部卖出']==0)]['卖出部分盈利金额'].sum()
    sellResDf.loc['次均等权卖出收益率(%)'] = '%.2f%%'%(sellSampleDf['卖出部分收益率(%)'].mean())
    sellResDf.loc['次均成交额加权收益率(%)'] = '%.2f%%'%(sellSampleDf['加权收益率'].sum()/sellSampleDf['买入金额'].sum())
    if strategy=='saturn':
        sellResDf.loc['累计参与率'] = '%.2f%%' % (labels_p2['p2shouldBuySignal'].sum() / len(labels_p2) * 100)
    elif strategy == 'ceres':
        sellResDf.loc['累计参与率'] = ''if len(labels_p2)==0 else '%.2f%%' % (labels_p2['p3shouldBuySignal'].sum() / len(labels_p2) * 100)
    sellResDf.loc['累计胜率'] = ''if len(sellSampleDf)==0 else '%.2f%%' % (len(sellSampleDf[(sellSampleDf['理论是否正收益'] == 1)]) / len(sellSampleDf) * 100)
    sellResDf.loc['累计交易胜率'] = ''if len(sellSampleDf)==0 else '%.2f%%' % (len(sellSampleDf[sellSampleDf['实际是否正收益'] == 1]) / len(sellSampleDf) * 100)
    sellResDf.loc['预测为1实际为1平均买入金额'] = str(round(sellSampleDf[sellSampleDf['理论是否预测正确']==1]['买入金额'].mean(),2))
    sellResDf.loc['预测为1实际为1平均卖出收益率（%）'] = '%.2f%%'%(sellSampleDf[sellSampleDf['理论是否预测正确']==1]['卖出部分收益率(%)'].mean())
    sellResDf.loc['预测为1实际为1次均成交额加权卖出收益率（%）'] = ''if len(sellSampleDf)==0 else '%.2f%%'%(sellSampleDf[sellSampleDf['理论是否预测正确']==1]['卖出部分盈利金额'].sum()/sellSampleDf[sellSampleDf['理论是否预测正确']==1]['买入金额'].sum()*100)

    sellResDf.loc['预测为1实际为0平均买入金额'] = str(round(sellSampleDf[sellSampleDf['理论是否预测正确']==0]['买入金额'].mean(),2))
    sellResDf.loc['预测为1实际为0平均卖出收益率（%）'] = '%.2f%%'%(sellSampleDf[sellSampleDf['理论是否预测正确']==0]['卖出部分收益率(%)'].mean())
    sellResDf.loc['预测为1实际为0次均成交额加权卖出收益率（%）'] =''if len(sellSampleDf)==0 else  '%.2f%%'%(sellSampleDf[sellSampleDf['理论是否预测正确']==0]['卖出部分盈利金额'].sum()/sellSampleDf[sellSampleDf['理论是否预测正确']==0]['买入金额'].sum()*100)
    sellResDf.loc['预测为1样本盈亏比'] =''if len(sellSampleDf)==0 else  str(abs(round((sellSampleDf[sellSampleDf['理论是否预测正确']==1]['卖出部分盈利金额'].mean())/sellSampleDf[sellSampleDf['理论是否预测正确']==0]['卖出部分盈利金额'].mean(),2)))
    #    --------------------------------------------------画图------------------------------------------------
    if len(Label_summary.dt.unique())<=rolldays_num:
        print('%s目前运行天数不足, %d天！！！！！！！！！！'%(strategy,len(Label_summary.dt.unique())))
    else:
        CPs = fig.add_subplot(2,5,4)
        title_cus_day = "Cumulated Profit"
        # Label_summary = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发项目二标签汇总_%s.xlsx'%Adate)
        Label_summary['real_positive'] = (Label_summary[label_v]>0)
        Label_summary['dt'] = Label_summary['dt'].apply(lambda x:x.strftime('%Y-%m-%d'))
        Label_summary_stats_dummy = Label_summary.groupby(['dt']).apply(lambda x:len(x))
        tempDf = sellDf_this[(sellDf_this['是否全部卖出']==1)|(sellDf_this['是否全部卖出']==0)].groupby(['买入日期'])['卖出部分盈利金额'].sum().cumsum().reindex(Label_summary_stats_dummy.index).fillna(method = 'ffill')
        tempDf = pd.DataFrame(tempDf)
        tempDf.columns = ['cumulated_profit']
        tempDf.index.name = 'Buy_Date'

        if trade_time == 930:
            CPs.plot(tempDf[['cumulated_profit']], 'b')
            CPs.legend(['930'], loc='best')
        elif trade_time == 931:
            sellDf_931_single = sellDf[sellDf['931信号'] == 1]
            tempDf_931_single = sellDf_931_single[(sellDf_931_single['是否全部卖出'] == 1) | (sellDf_931_single['是否全部卖出'] == 0)].groupby(['买入日期'])['卖出部分盈利金额'].sum().cumsum().reindex(
                Label_summary_stats_dummy.index).fillna(method='ffill')
            tempDf_931_single = pd.DataFrame(tempDf_931_single)
            tempDf_931_single.columns = ['cumulated_profit_931_single']
            tempDf_931_single.index.name = 'Buy_Date'
            if strategy == 'saturn':
                CPs.plot(tempDf[['cumulated_profit']], 'b', tempDf_931_single[['cumulated_profit_931_single']], 'b--')
                CPs.legend(['931','931_single'], loc='best')
            elif strategy == 'ceres':
                CPs.plot(tempDf[['cumulated_profit']], 'b')
                CPs.legend(['931'], loc='best')
        # print(tempDf['cumulated_profit'])
        # CPs.vlines('2020-06-03',ymin = -4,ymax = 6,colors = 'red',linestyles = '--')
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

        '''Daily_Average_Sell_Profit_positive = Daily_Average_Sell_Profit[Daily_Average_Sell_Profit>=0]
        MWDAP.bar(Daily_Average_Sell_Profit_positive.index,Daily_Average_Sell_Profit_positive['average_profit'],label = 'average_profit')
        MWDAP.hold(True)
        Daily_Average_Sell_Profit_negative= Daily_Average_Sell_Profit[Daily_Average_Sell_Profit < 0]
        MWDAP.bar(Daily_Average_Sell_Profit_negative.index, Daily_Average_Sell_Profit_negative['average_profit'],color = 'r', label='average_profit')
        Daily_Average_Sell_Profit.index.name = 'Date'
        '''
        # ---------------------------让坐标看得清---------------------------
        ax = plt.gca()
        for label in ax.get_xticklabels():
            label.set_visible(False)
        for label in ax.get_xticklabels()[::10]:
            label.set_visible(True)
        plt.xticks(rotation=45)
        # ---------------------------让坐标看得清---------------------------
        plt.title(title_cus_day)
        plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.2, wspace=0.3, hspace=0.5)

    if strategy=='saturn':
        plt.savefig("/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/收益画图/%s_%s_p2_%d.png" % (Adate, '生产环境', trade_time),dpi=120)
    elif strategy=='ceres':
        plt.savefig("/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/收益画图/%s_%s_p3_%d.png" % (Adate, '生产环境', trade_time),
                    dpi=120)
    #    --------------------------------------------------画图------------------------------------------------
    return sellResDf.reset_index()
# 今日卖出信息
def get_sellDfTodayInfo(sellDf,sellDate,trade_time):
    sellDf = sellDf[sellDf['买入时点'] == trade_time]
    todaySellDf = sellDf[sellDf['卖出日期'].notnull()][sellDf['卖出日期'].dropna().apply(lambda x:sellDate in x)]
    if len(todaySellDf)==0:
        return
    todaySellDf.replace(np.nan,'',inplace=True)
    todaySellResDf = pd.DataFrame(columns=['value'])
    todaySellResDf.loc['全部卖出股票数'] = len(todaySellDf)
    def return_last_comma(data):
        if (type(data) == float) | (type(data) == int):
            return data
        else:
            return float(data.split(',')[~0])
    todaySellResDf.loc['卖出盈利（元）'] = ((todaySellDf['卖出成交均价'].apply(return_last_comma)*0.999 - todaySellDf['买入成交均价'])*
            todaySellDf['卖出数量'].apply(return_last_comma)).sum()

    todaySellResDf.loc['次均等权卖出收益率(%)'] = '%.2f%%'%((todaySellDf['卖出成交均价'].apply(return_last_comma)/todaySellDf['买入成交均价'] - 1).mean()*100)
    todaySellResDf.loc['次均成交额加权收益率(%)'] = '%.2f%%'%(100*((todaySellDf['买入成交均价']*todaySellDf['卖出数量'].apply(return_last_comma))*(todaySellDf['卖出成交均价'].apply(return_last_comma)/todaySellDf['买入成交均价'] - 1)).sum()/\
        ((todaySellDf['买入成交均价']*todaySellDf['卖出数量'].apply(return_last_comma)).sum()))
    todaySellResDf.loc['今日卖出胜率'] = '%.2f%%'%(((todaySellDf['卖出成交均价'].apply(return_last_comma) - todaySellDf['买入成交均价'])>0).sum()/len(todaySellDf)*100)
    return todaySellResDf.reset_index()






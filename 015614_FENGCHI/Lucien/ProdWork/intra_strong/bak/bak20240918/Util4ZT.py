# -*- coding: utf-8 -*-
"""
Created on Wed May 22 19:30:47 2019
用于Jupiter，包括绘图

@author: 013551
"""
import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
from pylab import mpl
from ProdWork.CommonTools import cal_cumsum_mean
from xquant.marketdata import MarketData
mdp = MarketData()
mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei'] # 指定默认字体
mpl.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题
fig_width, fig_height = 30, 12
rolldays_num, xtick_stepnum, rollnums_num = 5, 20, 200
IO_mother_dir = '/data/group/800080/warehouse_event'
# jupiter成交记录：sheet：累计汇总情况，表格：累计买入汇总。买入信息，这里会对‘jupiter成交记录’里面的‘累计汇总情况’中的图画一部分，并输出

today_date = dt.datetime.today().strftime('%Y%m%d')
year_start_date = today_date[:4] + '0101'

def get_buyDfTotalInfo(buyDf, Adate,strategy='jupiter'):
    if len(buyDf)==0:
        return
    buyDf['买入当日突破时间'] = buyDf['买入当日突破时间'].astype(str)
    buyResDf = pd.DataFrame (columns=['value'])
    buyResDf.loc['累计交易天数'] = len(buyDf.groupby('发生日期'))
    buyResDf.loc['累计实盘预测为1样本数'] = len(buyDf)
    buyResDf.loc['累计实盘交易样本数'] = len(buyDf[buyDf['成交数量']!=0])
    buyResDf.loc['次均买入当日收益率'] = '%.2f%%' % (buyDf['买入当日收益率(%)'].mean())
    condition1 = (~np.isnan(buyDf['买入当日收益率(%)']))
    buyResDf.loc['次均成交额加权买入当日收益率'] = '%.2f%%'%((buyDf[condition1]['买入当日收益率(%)']*buyDf[condition1]['成交金额']).sum()/buyDf[condition1]['成交金额'].sum())
    buyResDf.loc['次均成交额均值'] = buyDf[buyDf['成交数量']>0]['成交金额'].mean()
    buyResDf.loc['10点前突破比例'] = '%.2f%%'%(len(buyDf[buyDf['买入当日突破时间'].apply(lambda x:float(x))<100000000])/len(buyDf)*100)
    buyResDf.loc['累计下单收盘涨停比例'] = '%.2f%%' % ((buyDf['形态'] != 2).sum() / len(buyDf) * 100)
    buyResDf.loc['累计下单形态4比例'] = '%.2f%%' % ((buyDf['形态'] == 4).sum() / len(buyDf) * 100)
    buyResDf.loc['累计形态4下单完全未成交比例'] = '%.2f%%'%((1-(buyDf[buyDf['成交金额'] != 0]['形态'] == 4).sum()/(buyDf['形态'] == 4).sum())*100)

#    --------------------------------------------------画图------------------------------------------------
    tot_buy_dt = sorted(list(buyDf['发生日期'].unique()))
    fig = plt.figure(figsize = (fig_width, fig_height))
    plt.rcParams['font.size'] = 7
    ABM = fig.add_subplot(3, 7,1)
    title_cus_day = "Average Buy Money"
    Average_Daily_Buy_Money = pd.DataFrame(buyDf[buyDf['成交数量']>0].groupby('发生日期')['成交金额'].mean()).reindex(tot_buy_dt).fillna(0)
    Average_Daily_Buy_Money.columns = ['buy_money']
    ABM.bar(Average_Daily_Buy_Money.index,Average_Daily_Buy_Money['buy_money'], label='buy_money')
    Average_Daily_Buy_Money.index.name = 'Date'
    # ---------------------------让坐标看得清---------------------------
    ax = plt.gca()
    for label in ax.get_xticklabels():
        label.set_visible(False)
    for label in ax.get_xticklabels()[::xtick_stepnum]:
        label.set_visible(True)
    plt.xticks(rotation=45)
    # ---------------------------让坐标看得清---------------------------
    plt.title(title_cus_day)
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)

    DPS = fig.add_subplot(3, 7,2)
    title_cus_day = "Daily Positive Stocks"
    Daily_Positive_Stocks = pd.DataFrame(buyDf.groupby('发生日期').apply(len))
    Daily_Positive_Stocks.columns = ['positive_stocks']
    Daily_Positive_Stocks.index.name = 'Date'
    DPS.bar(Daily_Positive_Stocks.index,Daily_Positive_Stocks['positive_stocks'],label = 'positive_stocks')
    DPS.hold(True)
    if strategy == 'jupiter':
        Daily_lzt_Positive_Stocks = pd.DataFrame(buyDf[(buyDf['前涨停信号']!=0) & (buyDf['前涨停信号'].notnull())].groupby('发生日期').apply(len)).reindex(Daily_Positive_Stocks.index)
        Daily_lzt_Positive_Stocks.columns = ['lzt_positive_stocks']
        DPS.bar(Daily_lzt_Positive_Stocks.index, Daily_lzt_Positive_Stocks['lzt_positive_stocks'],color = 'r', label='lzt_positive_stocks')
    DPS.legend(loc='best')

    # ---------------------------让坐标看得清---------------------------
    ax = plt.gca()
    for label in ax.get_xticklabels():
        label.set_visible(False)
    for label in ax.get_xticklabels()[::xtick_stepnum]:
        label.set_visible(True)
    plt.xticks(rotation=45)
    # ---------------------------让坐标看得清---------------------------
    plt.title(title_cus_day)
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)

    DHA = fig.add_subplot(3, 7, 6)
    title_cus_day = "Daily hold amount"
    Daily_hold_amt = pd.DataFrame(buyDf.groupby('发生日期')['买入当天持仓金额'].sum()).reindex(tot_buy_dt).fillna(0)
    Daily_hold_amt.columns = ['hold_amount']
    Daily_hold_amt.index.name = 'Date'
    DHA.bar(Daily_hold_amt.index, Daily_hold_amt['hold_amount'], label='hold_amount')
    Daily_hold_amt_roll = pd.DataFrame(Daily_hold_amt['hold_amount'].rolling(rolldays_num, 1).mean()).reindex(
        Daily_hold_amt.index)
    Daily_hold_amt_roll.columns = ['hold_amount_roll%ddays' % rolldays_num]
    Daily_hold_amt_roll.index.name = 'Date'
    DHA.plot(Daily_hold_amt_roll.index, Daily_hold_amt_roll['hold_amount_roll%ddays' % rolldays_num], color='r',
             label='hold_amount_roll%ddays' % rolldays_num)
    # actbuyday.vlines('2020-06-03', ymin=0, ymax=1.2, colors='r', linestyles='--')
    DHA.legend(loc='best')
    # ---------------------------让坐标看得清---------------------------
    ax = plt.gca()
    for label in ax.get_xticklabels():
        label.set_visible(False)
    for label in ax.get_xticklabels()[::xtick_stepnum]:
        label.set_visible(True)
    plt.xticks(rotation=45)
    # ---------------------------让坐标看得清---------------------------
    plt.title(title_cus_day)
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)

    DAR = fig.add_subplot(3, 7, 13)
    title_cus_day = "Daily Deal Ratio (Rolling %d days)" % rolldays_num
    if strategy != 'Leda':
        buy_lnzt = buyDf[buyDf['last_is_zt']==False]
    else:
        buy_lnzt = buyDf[buyDf['last_is_zt']==True]
    daily_pred_sum5 = buy_lnzt.groupby('发生日期')['委托方向'].count().reindex(tot_buy_dt).fillna(0).rolling(rolldays_num,rolldays_num).sum().dropna()
    daily_attend_sum5 = buy_lnzt[buy_lnzt['成交数量'] > 0].groupby('发生日期')['委托方向'].count().reindex(tot_buy_dt).fillna(0).rolling(rolldays_num,rolldays_num).sum().dropna()
    daily_attend_ratio = pd.DataFrame(daily_attend_sum5/daily_pred_sum5).sort_index()
    daily_attend_ratio.columns = ['deal_ratio_roll%ddays'%rolldays_num]
    daily_attend_ratio.index.name = 'Date'
    DAR.plot(daily_attend_ratio.index, daily_attend_ratio['deal_ratio_roll%ddays'%rolldays_num], color='r',
             label='deal_ratio_roll%ddays' % rolldays_num)
    # actbuyday.vlines('2020-06-03', ymin=0, ymax=1.2, colors='r', linestyles='--')
    DAR.legend(loc='best')
    DAR.set_ylim(0.2, 1.2)
    # ---------------------------让坐标看得清---------------------------
    ax = plt.gca()
    for label in ax.get_xticklabels():
        label.set_visible(False)
    for label in ax.get_xticklabels()[::xtick_stepnum]:
        label.set_visible(True)
    plt.xticks(rotation=45)
    # ---------------------------让坐标看得清---------------------------
    plt.title(title_cus_day)
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)
    """
    20200610更新形态画图
    """
    #    --------------------------------------------------画图------------------------------------------------
    # 我们买的样本信息
    signal_label = buyDf.groupby('发生日期').apply(lambda x:pd.Series({'形态4数量':(x['形态']==4).sum()
                                                       ,'形态3数量':(x['形态']==3).sum()
                                                        ,'形态2数量': (x['形态'] == 2).sum()
                                                       ,'收盘涨停数量':((x['形态']==3) | (x['形态']==4)).sum()
                                                       ,'信号总数':len(x)
                                                       ,'形态2_o2ul_总和': x[x['形态'] == 2]['TN_o2ul'].sum()
                                                       ,'形态4_o2ul_总和':x[x['形态']==4]['TN_o2ul'].sum()
                                                       ,'形态3_o2ul_总和':x[x['形态']==3]['TN_o2ul'].sum()
                                                       ,'买入当日十点前突破数量':x['买入当日突破时间'].apply(lambda x:float(x)<100000000).sum()}))


    # 全部触发样本信息
    from xquant.factordata import FactorData
    s = FactorData()
    date = str(Adate).replace('-','')
    # print('current date = %s' % date)
    lastdate = s.tradingday(date, -2)[0]
    Alastdate = lastdate[0:4]+'-'+lastdate[4:6]+'-'+lastdate[6:8]
    if strategy == 'jupiter':
        Label_summary = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发标签汇总_%s.xlsx'%Adate)
        #Label_summary = Label_summary[Label_summary['ZTBysModel_local_prob'].isna()]
    elif strategy == 'jupiterNew':
        Label_summary = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发标签汇总New_%s.xlsx' % Adate)
    elif strategy == 'Metis':
        Label_summary = pd.read_excel('/data/group/800463/日内强势股/metis_log_parse/因子耗时/实盘触发标签汇总Metis_%s.xlsx' % Adate)
    elif strategy == 'Leda':
        Label_summary = pd.read_excel('/data/group/800463/日内强势股/leda_log_parse/因子耗时/实盘触发标签汇总Leda_%s.xlsx' % Adate)
    Label_summary = Label_summary[Label_summary['dt'] >= pd.Timestamp(buyDf['发生日期'].min())]
    Label_summary['label_T_is_zt'] = (Label_summary['买入时形态'] >= 3).astype(int)
    Label_summary['label_zt_lianxu_in3days'] = 0
    Label_summary.loc[Label_summary.query('label_T_is_zt==1 and label_T1_zt==0').index, 'label_zt_lianxu_in3days'] = 1
    Label_summary.loc[Label_summary.query('label_T_is_zt==1 and label_T1_zt==1').index, 'label_zt_lianxu_in3days'] = 2

    if 'ZTBysModel_local_prob' in Label_summary.columns.tolist():
        Label_summary = Label_summary[Label_summary['ZTBysModel_local_prob'].isna()]

    # print(Label_summary.label_zt_lianxu_in3days.value_counts())
    Label_summary['real_positive'] = (Label_summary['买入时形态']==4)&(Label_summary['TN_o2ul']>0)
    Label_summary['dt'] = Label_summary['dt'].apply(lambda x:x.strftime('%Y-%m-%d'))
    Label_summary_stats = Label_summary.groupby('dt').apply(lambda x:pd.Series({'触发总数':len(x)
                                                        ,'形态4数量': (x['买入时形态'] == 4).sum()
                                                        ,'形态3数量': (x['买入时形态'] == 3).sum()
                                                        ,'形态2数量': (x['买入时形态'] == 2).sum()
                                                        ,'收盘涨停数量': ((x['买入时形态'] == 3) | (x['买入时形态'] == 4)).sum()
                                                        ,'形态2_o2ul_总和': x[x['买入时形态'] == 2]['TN_o2ul'].sum()
                                                        ,'形态4_o2ul_总和':x[x['买入时形态']==4]['TN_o2ul'].sum()
                                                        ,'形态3_o2ul_总和':x[x['买入时形态']==3]['TN_o2ul'].sum()
                                                        ,'买入当日十点前突破数量':x['ZT_Time'].apply(lambda x:int(x)<100000000).sum()
                                                        ,'首板_o2ul_总和': x[x['label_zt_lianxu_in3days'] == 1]['TN_o2ul'].sum()
                                                        ,'二连板_o2ul_总和': x[x['label_zt_lianxu_in3days'] == 2]['TN_o2ul'].sum()
                                                        ,'三连板_o2ul_总和': x[x['label_zt_lianxu_in3days'] == 3]['TN_o2ul'].sum()
                                                        ,'首板数量': (x['label_zt_lianxu_in3days'] == 1).sum()
                                                        ,'二连板数量': (x['label_zt_lianxu_in3days'] == 2).sum()
                                                        ,'三连板数量': (x['label_zt_lianxu_in3days'] == 3).sum()
                                                                                }))

    signal_label_rolling_3 = signal_label.reindex(Label_summary_stats.index).fillna(0).rolling(rolldays_num,1).sum()
    Label_summary_stats_rolling_3 = Label_summary_stats.rolling(rolldays_num,1).sum()
    Label_summary_stats_rolling_3['触发总数_roll%ddays'%rolldays_num] = Label_summary_stats['触发总数'].rolling(rolldays_num,1).mean()
    Label_summary_basic = Label_summary.copy()
    Label_summary_basic = Label_summary_basic.set_index(['dt','Ticker']).sort_index()
    if 'ZTBysModel_local_prob' in Label_summary_basic.columns.tolist():
        Label_summary_basic = Label_summary_basic[(Label_summary_basic['ZTBysModel_local_prob'].isna())]
    Label_summary_basic_stats = Label_summary_basic.groupby('dt').apply(lambda x: pd.Series({'触发总数': len(x),
                                                                                     'Tc2Tul': (x['label_Tc2Tul'].fillna(0)).sum(),
                                                                                     'T1o2Tc': (x['label_T1o2Tc'].fillna(0)).sum(),
                                                                                     'T1c2Tc': (x['label_T1c2Tc'].fillna(0)).sum(),
                                                                                     '收盘涨停数量': ((x['买入时形态'] == 3) | (x['买入时形态'] == 4)).sum()}
                                                                                     ))
    daily_basic_metrics = Label_summary_basic_stats.copy()#[['触发总数','收盘涨停数量']]
    daily_basic_metrics['封板率'] = (daily_basic_metrics['收盘涨停数量']/daily_basic_metrics['触发总数']).fillna(0)

    daily_basic_metrics['Tc2Tul均值'] = 100*(daily_basic_metrics['Tc2Tul'] / daily_basic_metrics['触发总数']).fillna(0)
    daily_basic_metrics['T1o2Tc均值'] = 100*(daily_basic_metrics['T1o2Tc'] / daily_basic_metrics['触发总数']).fillna(0)
    daily_basic_metrics['T1c2Tc均值'] = 100*(daily_basic_metrics['T1c2Tc'] / daily_basic_metrics['触发总数']).fillna(0)
    daily_basic_metrics.drop(columns=['收盘涨停数量','Tc2Tul','T1o2Tc','T1c2Tc'], inplace=True)

    # if strategy =='jupiter':
    RZTs = fig.add_subplot(3, 7, 11)
    # 各个形态样本占比，2，3，4；zt样本占比，形态4样本占比
    title_cus_day = 'Signal Label Pattern Ratio (Rolling %s days)'%str(rolldays_num)
    signal_label_all_rolling_3 = pd.DataFrame(signal_label_rolling_3['信号总数']/signal_label_rolling_3['信号总数']).dropna().loc[:Alastdate]
    signal_label_all_rolling_3.columns = ['rolling_pattern_2']
    signal_label_all_rolling_3.index.name = 'Buy_Date'
    RZTs.bar(signal_label_all_rolling_3.index,signal_label_all_rolling_3['rolling_pattern_2'],color = 'r',label = ['rolling_pattern_2'])
    RZTs.hold(True)

    signal_label_zt_rolling_3 = pd.DataFrame(signal_label_rolling_3['收盘涨停数量']/signal_label_rolling_3['信号总数']).dropna().loc[:Alastdate]
    signal_label_zt_rolling_3.columns = ['rolling_pattern_3']
    signal_label_zt_rolling_3.index.name = 'Buy_Date'
    RZTs.bar(signal_label_zt_rolling_3.index,signal_label_zt_rolling_3['rolling_pattern_3'],color = 'g',label = ['rolling_pattern_3'])
    RZTs.hold(True)

    signal_label_4_rolling_3 = pd.DataFrame(signal_label_rolling_3['形态4数量']/signal_label_rolling_3['信号总数']).dropna().loc[:Alastdate]
    signal_label_4_rolling_3.columns = ['rolling_pattern_4']
    signal_label_4_rolling_3.index.name = 'Buy_Date'
    RZTs.bar(signal_label_4_rolling_3.index,signal_label_4_rolling_3['rolling_pattern_4'],color = 'b',label = ['rolling_pattern_4'])

    all_label_4_rolling_3 = pd.DataFrame(Label_summary_stats_rolling_3['形态4数量']/Label_summary_stats_rolling_3['触发总数']).loc[:Alastdate]
    all_label_4_rolling_3.columns = ['rolling_pattern_4']
    all_label_4_rolling_3.index.name = 'Buy_Date'
    all_label_zt_rolling_3 = pd.DataFrame(Label_summary_stats_rolling_3['收盘涨停数量']/Label_summary_stats_rolling_3['触发总数']).loc[:Alastdate]
    all_label_zt_rolling_3.columns = ['rolling_pattern_zt']
    all_label_zt_rolling_3.index.name = 'Buy_Date'

    RZTs.plot(all_label_4_rolling_3['rolling_pattern_4'],'orange',
              all_label_zt_rolling_3['rolling_pattern_zt'],'m')
    if strategy == 'jupiter':
        RZTs.vlines('2020-06-03',ymin = 0,ymax = 1,colors = 'black',linestyles = '--')
        RZTs.vlines('2021-08-25', ymin=0, ymax=1, colors='black', linestyles='--')
        RZTs.vlines('2022-02-22', ymin=0, ymax=1, colors='black', linestyles='--')
    # ---------------------------让坐标看得清---------------------------
    ax = plt.gca()
    for label in ax.get_xticklabels():
        label.set_visible(False)
    for label in ax.get_xticklabels()[::xtick_stepnum]:
        label.set_visible(True)
    plt.xticks(rotation=45)
    # ---------------------------让坐标看得清---------------------------
    plt.title(title_cus_day)

    actbuyday = fig.add_subplot(3, 7, 5)
    title_cus_day = 'Daily ZT Ratio'
    zt_df = pd.DataFrame(buyDf[buyDf['成交数量'] > 0].groupby('发生日期')['买入当天是否收盘涨停'].mean()).reindex(tot_buy_dt).fillna(0)
    zt_df.columns = ['ZT_ratio']
    zt_df.index.name = 'Buy_Date'
    actbuyday.bar(zt_df.index, zt_df['ZT_ratio'], label='ZT_ratio')
    actbuyday.hold(True)
    zt_df_roll = pd.DataFrame(zt_df['ZT_ratio'].rolling(rolldays_num, 1).mean()).reindex(zt_df.index)
    zt_df_roll.columns = ['ZT_ratio_roll5days']
    zt_df_roll.index.name = 'Buy_Date'
    actbuyday.plot(zt_df_roll.index, zt_df_roll['ZT_ratio_roll5days'],color='r',label='ZT_ratio_roll5days')
    #actbuyday.vlines('2020-06-03', ymin=0, ymax=1.2, colors='r', linestyles='--')
    actbuyday.legend(loc='best')
    actbuyday.set_ylim(0, 1.2)

    # ---------------------------让坐标看得清---------------------------
    ax = plt.gca()
    for label in ax.get_xticklabels():
        label.set_visible(False)
    for label in ax.get_xticklabels()[::xtick_stepnum]:
        label.set_visible(True)
    plt.xticks(rotation=45)
    # ---------------------------让坐标看得清---------------------------
    plt.title(title_cus_day)
    STN = fig.add_subplot(3, 7,7)
    title_cus_day = 'Signal Triggered Number(Rolling %s days)'%str(rolldays_num)

    triggered_all = pd.DataFrame(Label_summary_stats_rolling_3['触发总数_roll%ddays'%rolldays_num])
    triggered_all.columns = ['triggered_all']
    triggered_all.index.name = 'Buy_Date'
    STN.plot(triggered_all['triggered_all'],'b-')
    if strategy == 'jupiter':
        STN.vlines('2020-06-03',ymin = 0,ymax = 1,colors = 'r',linestyles = '--')
        STN.vlines('2021-08-25', ymin=0, ymax=1, colors='r', linestyles='--')
        STN.vlines('2022-02-22', ymin=0, ymax=1, colors='r', linestyles='--')
    STN.legend(['all_triggered'],loc = 'best')
    # ---------------------------让坐标看得清---------------------------
    ax = plt.gca()
    for label in ax.get_xticklabels():
        label.set_visible(False)
    for label in ax.get_xticklabels()[::xtick_stepnum]:
        label.set_visible(True)
    plt.xticks(rotation=45)
    # ---------------------------让坐标看得清---------------------------
    plt.title(title_cus_day)

    PTs = fig.add_subplot(3, 7, 8)
    title_cus_day = 'Signal Triggered Before 10 (Rolling %s days)' % str(rolldays_num)
    pre_10_zt = pd.DataFrame(signal_label_rolling_3['买入当日十点前突破数量'] / signal_label_rolling_3['信号总数']).loc[:Alastdate]
    pre_10_zt.columns = ['pre_10_zt']
    pre_10_zt.index.name = 'Buy_Date'
    pre_10_zt_all = pd.DataFrame(Label_summary_stats_rolling_3['买入当日十点前突破数量'] / Label_summary_stats_rolling_3['触发总数'])
    pre_10_zt_all.columns = ['pre_10_zt_all']
    pre_10_zt_all.index.name = 'Buy_Date'
    PTs.plot(pre_10_zt['pre_10_zt'], 'b',
             pre_10_zt_all['pre_10_zt_all'], 'b--')
    if strategy == 'jupiter':
        PTs.vlines('2020-06-03', ymin=0, ymax=1, colors='r', linestyles='--')
        PTs.vlines('2021-08-25', ymin=0, ymax=1, colors='r', linestyles='--')
        PTs.vlines('2022-02-22', ymin=0, ymax=1, colors='r', linestyles='--')
    PTs.legend(['signal', 'all_triggered'], loc='best')
    # ---------------------------让坐标看得清---------------------------
    ax = plt.gca()
    for label in ax.get_xticklabels():
        label.set_visible(False)
    for label in ax.get_xticklabels()[::xtick_stepnum]:
        label.set_visible(True)
    plt.xticks(rotation=45)
    # ---------------------------让坐标看得清---------------------------
    plt.title(title_cus_day)


    L4O2ULs = fig.add_subplot(3, 7,10)
    title_cus_day = 'Signal Pattern o2ul(%) (Rolling 5 days)'
    label_2_o2ul_rolling_3 = pd.DataFrame(signal_label_rolling_3['形态2_o2ul_总和']/signal_label_rolling_3['信号总数']).loc[:Alastdate]
    label_2_o2ul_rolling_3.columns = ['label_2_o2ul']
    label_2_o2ul_rolling_3.index.name = 'Buy_Date'

    label_4_o2ul_rolling_3 = pd.DataFrame(signal_label_rolling_3['形态4_o2ul_总和']/signal_label_rolling_3['信号总数']).loc[:Alastdate]
    label_4_o2ul_rolling_3.columns = ['label_4_o2ul']
    label_4_o2ul_rolling_3.index.name = 'Buy_Date'

    label_3_o2ul_rolling_3 = pd.DataFrame(signal_label_rolling_3['形态3_o2ul_总和']/signal_label_rolling_3['信号总数']).loc[:Alastdate]
    label_3_o2ul_rolling_3.columns = ['label_3_o2ul']
    label_3_o2ul_rolling_3.index.name = 'Buy_Date'

    all_label_2_o2ul_rolling_3 = pd.DataFrame(Label_summary_stats_rolling_3['形态2_o2ul_总和']/Label_summary_stats_rolling_3['触发总数'])
    all_label_2_o2ul_rolling_3.columns = ['label_2_o2ul']
    all_label_2_o2ul_rolling_3.index.name = 'Buy_Date'

    all_label_4_o2ul_rolling_3 = pd.DataFrame(Label_summary_stats_rolling_3['形态4_o2ul_总和']/Label_summary_stats_rolling_3['触发总数'])
    all_label_4_o2ul_rolling_3.columns = ['label_4_o2ul']
    all_label_4_o2ul_rolling_3.index.name = 'Buy_Date'

    all_label_3_o2ul_rolling_3 = pd.DataFrame(Label_summary_stats_rolling_3['形态3_o2ul_总和']/Label_summary_stats_rolling_3['触发总数'])
    all_label_3_o2ul_rolling_3.columns = ['label_3_o2ul']
    all_label_3_o2ul_rolling_3.index.name = 'Buy_Date'

    L4O2ULs.plot(label_2_o2ul_rolling_3[['label_2_o2ul']],'r',label_3_o2ul_rolling_3[['label_3_o2ul']],'g',
                 label_4_o2ul_rolling_3[['label_4_o2ul']],'b',
                 all_label_2_o2ul_rolling_3[['label_2_o2ul']],'r--',all_label_3_o2ul_rolling_3[['label_3_o2ul']],'g--',
                 all_label_4_o2ul_rolling_3[['label_4_o2ul']],'b--')
    L4O2ULs.legend(['signal_2_o2ul','signal_3_o2ul', 'signal_4_o2ul','triggered_2_o2ul','triggered_3_o2ul', 'triggered_4_o2ul'],loc = 'best')
    if strategy == 'jupiter':
        L4O2ULs.vlines('2020-06-03',ymin = -4,ymax = 6,colors = 'black',linestyles = '--')
        L4O2ULs.vlines('2021-08-25', ymin=-4, ymax=6, colors='black', linestyles='--')
        L4O2ULs.vlines('2022-02-22', ymin=4, ymax=6, colors='black', linestyles='--')
    # ---------------------------让坐标看得清---------------------------
    ax = plt.gca()
    for label in ax.get_xticklabels():
        label.set_visible(False)
    for label in ax.get_xticklabels()[::xtick_stepnum]:
        label.set_visible(True)
    plt.xticks(rotation=45)
    # ---------------------------让坐标看得清---------------------------
    plt.title(title_cus_day)

    ZT3O2UL  = fig.add_subplot(3, 7,14)
    title_cus_day = 'Triggered CZT o2ul(%)'

    tmp_start_date = s.tradingday(date, -20)[0]
    tmp_start_date = tmp_start_date[:4] + '-' + tmp_start_date[4:6] + '-' + tmp_start_date[6:]
    Label_summary_stats_rolling_3_2021 = Label_summary_stats.loc[tmp_start_date:].sort_index()  # 2021-01-04
    all_zt_1_o2ul = pd.DataFrame(Label_summary_stats_rolling_3_2021['首板_o2ul_总和'] / Label_summary_stats_rolling_3_2021['首板数量'])
    all_zt_1_o2ul.columns = ['CZT1']

    all_zt_2o2ul = pd.DataFrame(Label_summary_stats_rolling_3_2021['二连板_o2ul_总和'] / Label_summary_stats_rolling_3_2021['二连板数量'])
    all_zt_2o2ul.columns = ['CZT2']
    all_zt_df = pd.concat([all_zt_1_o2ul, all_zt_2o2ul],axis=1).fillna(0)

    Label_summary_stats_rolling_3_2022 = Label_summary_stats.loc[tmp_start_date:].sort_index()    # 2022-01-04
    x = np.arange(len(Label_summary_stats_rolling_3_2022))
    total_width, n = 0.8, 2
    width = total_width / n
    x = x - (total_width - width) / 2
    all_zt_1_o2ul_rolling_3 = pd.DataFrame(Label_summary_stats_rolling_3_2022['首板_o2ul_总和'] / Label_summary_stats_rolling_3_2022['首板数量']).fillna(0)
    all_zt_1_o2ul_rolling_3.columns = ['label_1_zt_o2ul']
    all_zt_1_o2ul_rolling_3.index.name = 'Buy_Date'

    all_zt_2_o2ul_rolling_3 = pd.DataFrame(Label_summary_stats_rolling_3_2022['二连板_o2ul_总和'] / Label_summary_stats_rolling_3_2022['二连板数量']).fillna(0)
    all_zt_2_o2ul_rolling_3.columns = ['label_2_zt_o2ul']
    all_zt_2_o2ul_rolling_3.index.name = 'Buy_Date'

    all_zt_3_o2ul_rolling_3 = pd.DataFrame(Label_summary_stats_rolling_3_2022['三连板_o2ul_总和'] / Label_summary_stats_rolling_3_2022['三连板数量']).fillna(0)
    all_zt_3_o2ul_rolling_3.columns = ['label_3_zt_o2ul']
    all_zt_3_o2ul_rolling_3.index.name = 'Buy_Date'
    if strategy == 'jupiter':
        #ZT3O2UL.bar(all_zt_1_o2ul_rolling_3.index, all_zt_1_o2ul_rolling_3['label_1_zt_o2ul'], color = 'b', label='CZT1')
        ZT3O2UL.bar(x,  all_zt_1_o2ul_rolling_3['label_1_zt_o2ul'].reindex(Label_summary_stats_rolling_3_2022.index).tolist(), width=width,color='b', label='CZT1')
        #ZT3O2UL.hold(True)
        ZT3O2UL.bar(x + width, all_zt_2_o2ul_rolling_3['label_2_zt_o2ul'].reindex(Label_summary_stats_rolling_3_2022.index).tolist(),  width=width,color='r', label='CZT2')
        #ZT3O2UL.hold(True)
        #ZT3O2UL.bar(x + 2 * width, all_zt_3_o2ul_rolling_3['label_3_zt_o2ul'].reindex(Label_summary_stats_rolling_3_2022.index).tolist(),  width=width,color='g',label='CZT3')
        ZT3O2UL.legend(['CZT1','CZT2'], loc='best') # ,'CZT3'
    else:
        #ZT3O2UL.plot(all_zt_1_o2ul_rolling_3[['label_1_zt_o2ul']], 'r')
        ZT3O2UL.bar(x, all_zt_1_o2ul_rolling_3['label_1_zt_o2ul'].reindex(Label_summary_stats_rolling_3_2022.index).tolist(),  color='b', label='CZT1')
        ZT3O2UL.legend(['CZT1'], loc='best')
    xticks = ZT3O2UL.set_xticks(range(len(Label_summary_stats_rolling_3_2022)))
    xticks_label = ZT3O2UL.set_xticklabels(Label_summary_stats_rolling_3_2022.index.tolist())
    #ZT3O2UL.set_xticklabels(Label_summary_stats_rolling_3_2022.index.tolist())

    # ---------------------------让坐标看得清---------------------------
    ax = plt.gca()
    for label in ax.get_xticklabels():
        label.set_visible(False)
    for label in ax.get_xticklabels()[::int(xtick_stepnum/2)]:
        label.set_visible(True)
    plt.xticks(rotation=45)
    # ---------------------------让坐标看得清---------------------------
    plt.title(title_cus_day)


    MRWs = fig.add_subplot(3, 7, 9)
    title_cus_day = 'Model Performance (Rolling %s days)'%str(rolldays_num)

    Recal_raw = Label_summary.groupby(['dt']).apply(lambda x:pd.Series({'总正样本数量':x['real_positive'].sum(),
                                                            '预测正确正样本数量':(x['real_positive']&x['shouldBuySignal']).sum(),
                                                            '预测正样本数量':x['shouldBuySignal'].sum()}))
    Recal_raw_rolling_3_sum = Recal_raw.rolling(rolldays_num,rolldays_num).sum()

    Recal_rolling_3 = pd.DataFrame(Recal_raw_rolling_3_sum['预测正确正样本数量']/Recal_raw_rolling_3_sum['总正样本数量'])
    Recal_rolling_3.columns = ['Recall_rolling_3']
    Recal_rolling_3.index.name = 'Buy_Date'
    Wining_rolling_3 = pd.DataFrame(Recal_raw_rolling_3_sum['预测正确正样本数量']/Recal_raw_rolling_3_sum['预测正样本数量'])
    Wining_rolling_3.columns = ['Wining_rolling_3']
    Wining_rolling_3.index.name = 'Buy_Date'

    MRWs.plot(Recal_rolling_3[['Recall_rolling_3']].join(Wining_rolling_3[['Wining_rolling_3']]))
    if strategy == 'jupiter':
        MRWs.vlines('2020-06-03', ymin=0, ymax=1,colors = 'r',linestyles = '--')
        MRWs.vlines('2021-08-25', ymin=0, ymax=1, colors='r', linestyles='--')
        MRWs.vlines('2022-02-22', ymin=0, ymax=1, colors='r', linestyles='--')
    MRWs.legend(['recall','winning'],loc = 'best')
    # ---------------------------让坐标看得清---------------------------
    ax = plt.gca()
    for label in ax.get_xticklabels():
        label.set_visible(False)
    for label in ax.get_xticklabels()[::xtick_stepnum]:
        label.set_visible(True)
    plt.xticks(rotation=45)
    # ---------------------------让坐标看得清---------------------------
    plt.title(title_cus_day)
    all_zt_df.rename(columns = {'CZT1':'CZT1_o2ul','CZT2':'CZT2_o2ul'},inplace=True)

    # daily_basic_metrics['dt'] = [pd.Timestamp(x) for x in all_zt_df.index.tolist()]
    # all_zt_df.set_index(['dt'],inplace=True)
    daily_basic_metrics = daily_basic_metrics.loc['2021-01-01':].sort_index()
    all_stats_df = pd.concat([all_zt_df, daily_basic_metrics],axis=1,join_axes=[daily_basic_metrics.index])

#    --------------------------------------------------画图------------------------------------------------
    return (buyResDf.reset_index()), fig, all_stats_df#,daily_basic_metrics

# 今日基础信息：Jupiter成交记录。sheet：今日汇总情况
def get_DfTodayInfo(buyDf, buyDate, strategy='jupiter'):
    from xquant.factordata import FactorData
    s = FactorData()
    Adate = buyDate[:4] + buyDate[5:7] + buyDate[8:]
    md_data_wind_path = '/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/前置数据/md_data_wind/'
    start_date = s.tradingday(Adate, -20)[0]
    md_close_pre_close = pd.read_pickle(md_data_wind_path + f'{start_date}-{Adate}.pkl')

    if strategy == 'jupiter':
        today_tot_sample = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx'%buyDate)
        if 'ZTBysModel_probability' in today_tot_sample.columns.tolist():
            today_tot_sample = today_tot_sample[today_tot_sample['ZTBysModel_probability'].isna()]
    else:
        today_tot_sample = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % buyDate, sheet_name = '因子耗时New')
    new_pct_basic_file = today_tot_sample.copy()
    new_pct_basic_file['dt'] = pd.Timestamp(str(buyDate))
    new_pct_basic_file['Ticker'] = new_pct_basic_file['Unnamed: 0']
    new_pct_basic_file.set_index(['dt','Ticker'], inplace= True)
    # TODO：更改当日收盘价/买入均价
    today_tot_sample['pct_T'] = md_close_pre_close['pct_t'].reindex(new_pct_basic_file.index).values

    tot_pattern_df = pd.read_pickle(f'/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/前置数据/历史交易日样本形态数据/{Adate}.pkl')
    for index, row in today_tot_sample.iterrows():
        stockCode = row['Unnamed: 0']
        if (pd.to_datetime(Adate), stockCode) in tot_pattern_df.index:
            today_tot_sample.loc[index, '买入时形态'] = tot_pattern_df.loc[(pd.to_datetime(Adate), stockCode), 'label_pattern']
    # if strategy == 'jupiter':
    #     today_tot_sample.reset_index().to_excel('/data/group/800463/日内强势股/log_parse/中间数据/jupiter每日触发样本_%s.xlsx'%str(Adate))
    # else:
    #     today_tot_sample.reset_index().to_excel('/data/group/800463/日内强势股/log_parse/中间数据/jupiter每日触发样本New_%s.xlsx' % str(Adate))
    if len(today_tot_sample)==0:
        return
    today_tot_sample.reset_index().to_excel('/data/group/800463//日内强势股/实盘分析记录/分析文件/%s_%s.xlsx'%(strategy, Adate))
    todayBuyResDf = pd.DataFrame(columns=['value'])
    todayBuyResDf.loc['基础样本数量'] = len(today_tot_sample)
    todayBuyResDf.loc['次均买入当日收益率（%）'] = '%.2f%%' % (100*today_tot_sample['pct_T'].mean())
    todayBuyResDf.loc['今日形态4比例'] = '%.2f%%' % ((today_tot_sample['买入时形态'] == 4).sum() / len(today_tot_sample) * 100)
    return todayBuyResDf.reset_index()

# 今日买入信息：Jupiter成交记录。sheet：今日汇总情况
def get_buyDfTodayInfo(buyDf,buyDate,strategy='jupiter'):
    if strategy=='jupiter':
        today_tot_sample = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx'%buyDate)
        if 'ZTBysModel_probability' in today_tot_sample.columns.tolist():
            today_tot_sample = today_tot_sample[today_tot_sample['ZTBysModel_probability'].isna()]
        buyDf = buyDf[buyDf['last_is_zt'] == False]
    else:
        today_tot_sample = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx' % buyDate, sheet_name ='因子耗时New')

    todayOrderDf= buyDf[(buyDf['发生日期']==buyDate)]
    todayBuyDf = buyDf[(buyDf['发生日期']==buyDate) & (buyDf['成交数量']!=0)]
    todaynotBuyDf = buyDf[(buyDf['发生日期'] == buyDate) & (buyDf['成交数量'] == 0)]
    if len(todayOrderDf)==0:
        return
    todayBuyResDf = pd.DataFrame(columns=['value'])
    #todayBuyResDf.loc['样本数量'] = len(today_tot_sample)
    todayBuyResDf.loc['预测为1股票数'] = len(todayOrderDf)
    todayBuyResDf.loc['实际买入股票数'] = len(todayOrderDf[todayOrderDf['成交数量']!=0])
    todayBuyResDf.loc['实际买入参与率'] = '0.00%' if len(todayBuyDf)==0 else '%.2f%%'%(100*len(todayBuyDf[todayBuyDf['成交数量']!=0])/len(today_tot_sample))#len(buyDf[buyDf['发生日期']==buyDate]))
    todayBuyResDf.loc['总成交额（元）'] = 0 if len(todayBuyDf)==0 else todayBuyDf['成交金额'].sum()
    todayBuyResDf.loc['次均买入当日收益率（%）'] = '0.00%' if len(todayBuyDf)==0 else ('%.2f%%')%(todayBuyDf['买入当日收益率(%)'].mean())
    if len(todayBuyDf)==0:
        todayBuyResDf.loc['次均成交额加权买入当日收益率'] = '0.00%'
    else:
        condition1 = (~np.isnan(todayBuyDf['买入当日收益率(%)']))
        todayBuyResDf.loc['次均成交额加权买入当日收益率'] = '%.2f%%'%((todayBuyDf[condition1]['买入当日收益率(%)']*todayBuyDf[condition1]['成交金额']).sum()/todayBuyDf[condition1]['成交金额'].sum())
    todayBuyResDf.loc['次均成交额均值'] = 0 if len(todayBuyDf)==0 else np.nanmean(todayBuyDf['成交金额'])
    # todayBuyResDf.loc['次均成交笔数/挂单笔数'] = format(todayBuyDf['成交笔数/挂单笔数'].mean(),'.00%')
    todayBuyDf.replace(np.nan,'',inplace=True)
    todayBuyResDf.loc['实际买入股票当日收盘涨停比例'] = '0.00%' if len(todayBuyDf)==0 else format(len(todayBuyDf[todayBuyDf['买入当天是否收盘涨停']==1])/len(todayBuyDf[todayBuyDf['买入当天是否收盘涨停']!='']),'.00%')
    todayBuyResDf.loc['10点前突破比例'] = '0.00%' if len(todayBuyDf)==0 else format(len(todayBuyDf[todayBuyDf['买入当日突破时间'].apply(lambda x:float(x) if type(x) != str else 0)<100000000])/len(todayBuyDf), '.00%')
    todayBuyResDf.loc['今日成交形态4比例'] = '0.00%' if len(todayBuyDf)==0 else '%.2f%%' % ((todayBuyDf['形态'] == 4).sum() / len(todayBuyDf) * 100)
    todayBuyResDf.loc['实际未成交'] = len(todaynotBuyDf[(todaynotBuyDf['未完成原因']=='未成交')|(todaynotBuyDf['未完成原因']=='本策略未成交')])
    #todayBuyResDf.loc['mrisk导致未成交'] = 0 if len(todaynotBuyDf)==0 else len(list(filter(lambda x: str(x).find('拉抬打压控制')>0, todaynotBuyDf['未完成原因'].tolist())))
    todayBuyResDf.loc['mrisk导致未成交'] = 0 if len(todaynotBuyDf) == 0 else len(
        list(filter(lambda x: str(x).find('Mrisk') >= 0, todaynotBuyDf['未完成原因'].tolist())))
    todayBuyResDf.loc['其余导致未成交'] = 0 if len(todaynotBuyDf)==0 else len(todaynotBuyDf) - todayBuyResDf.loc['实际未成交'] - todayBuyResDf.loc['mrisk导致未成交']
#   buyResDf.to_excel(commonPath+r'\买入汇总.xlsx')
    return todayBuyResDf.reset_index()

# 全部卖出信息的计算（用于计算JupiterN和jupiterZ的卖出汇总），这里会对‘jupiter成交记录’里面的‘累计汇总情况’中的之前输出的图进行补充，并输出
def get_sellDfTotalInfo(sellDf,Adate,fig,strategy='jupiter'):
    if strategy == 'jupiter':
        labels_zt = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发标签汇总_%s.xlsx' % Adate)
    elif strategy == 'jupiterNew':
        labels_zt = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发标签汇总New_%s.xlsx' % Adate)
    elif strategy == 'Metis':
        labels_zt = pd.read_excel('/data/group/800463/日内强势股/metis_log_parse/因子耗时/实盘触发标签汇总Metis_%s.xlsx' % Adate)
    elif strategy == 'Leda':
        labels_zt = pd.read_excel('/data/group/800463/日内强势股/leda_log_parse/因子耗时/实盘触发标签汇总Leda_%s.xlsx' % Adate)
    sellResDf = pd.DataFrame(columns=['value'])
    sellSampleDf = sellDf[sellDf['是否全部卖出']==1]
    sellSampleDf['加权收益率'] = sellSampleDf['买入金额']*sellSampleDf['卖出部分收益率(%)']
    sellResDf.loc['累计全部卖出样本数'] = len(sellSampleDf)
    sellResDf.loc['累计盈利'] = sellDf[(sellDf['是否全部卖出']==1)|(sellDf['是否全部卖出']==0)]['卖出部分盈利金额'].sum()
    sellDf_2021 = sellDf[(sellDf['买入日期']>='2023-12-30') & (sellDf['买入日期']<'2024-12-31')]
    sellResDf.loc['2024累计盈利'] = sellDf_2021[(sellDf_2021['是否全部卖出']==1)|(sellDf_2021['是否全部卖出']==0)]['卖出部分盈利金额'].sum()
    sellResDf.loc['次均等权卖出收益率(%)'] = '%.2f%%'%(sellSampleDf['卖出部分收益率(%)'].mean())
    sellResDf.loc['次均成交额加权收益率(%)'] = '%.2f%%'%(sellSampleDf['加权收益率'].sum()/sellSampleDf['买入金额'].sum())

    sellResDf.loc['累计参与率'] = '0.00%' if len(labels_zt)==0 else '%.2f%%' % (len(labels_zt[labels_zt['shouldBuySignal']==1]) / len(labels_zt) * 100)
    sellResDf.loc['累计交易胜率'] = '0.00%'if len(sellSampleDf)==0 else '%.2f%%' % (len(sellSampleDf[sellSampleDf['实际是否正收益'] == 1]) / len(sellSampleDf) * 100)

    #    --------------------------------------------------画图------------------------------------------------
    tot_sell_dt = sorted(list(sellSampleDf['买入日期'].unique()))
    CPs = fig.add_subplot(3, 7, 4)
    title_cus_day = "Cumulated Profit"
    if strategy=='jupiter':
        Label_summary = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发标签汇总_%s.xlsx'%Adate)
    else:
        Label_summary = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发标签汇总New_%s.xlsx' % Adate)
    Label_summary = Label_summary[Label_summary['dt'] >= pd.Timestamp(sellDf['买入日期'].min())]
    Label_summary['real_positive'] = (Label_summary['买入时形态']==4)&(Label_summary['TN_o2ul']>0)
    Label_summary['dt'] = Label_summary['dt'].apply(lambda x:x.strftime('%Y-%m-%d'))
    Label_summary_stats_dummy =Label_summary.groupby(['dt']).apply(lambda x:len(x))
    tempDf = sellDf[(sellDf['是否全部卖出']==1)|(sellDf['是否全部卖出']==0)].groupby(['买入日期'])['卖出部分盈利金额'].sum().cumsum().reindex(Label_summary_stats_dummy.index).fillna(method = 'ffill')
    tempDf = pd.DataFrame(tempDf)
    tempDf.columns = ['cumulated_profit']
    tempDf.index.name = 'Buy_Date'

    lzt_sellDf = sellDf[((sellDf['是否全部卖出']==1)|(sellDf['是否全部卖出']==0)) & (sellDf['last_is_zt']==True)].groupby(['买入日期'])['卖出部分盈利金额'].sum().cumsum().reindex(Label_summary_stats_dummy.index).fillna(method = 'ffill')
    lzt_sellDf = pd.DataFrame(lzt_sellDf)
    lzt_sellDf.columns = ['lzt_cumulated_profit']
    lzt_sellDf.index.name = 'Buy_Date'

    lnonzt_sellDf = sellDf[((sellDf['是否全部卖出']==1)|(sellDf['是否全部卖出']==0)) & (sellDf['last_is_zt']==False)].groupby(['买入日期'])['卖出部分盈利金额'].sum().cumsum().reindex(Label_summary_stats_dummy.index).fillna(method = 'ffill')
    lnonzt_sellDf = pd.DataFrame(lnonzt_sellDf)
    lnonzt_sellDf.columns = ['lnonzt_cumulated_profit']
    lnonzt_sellDf.index.name = 'Buy_Date'

    CPs.plot(tempDf[['cumulated_profit']],'b',lnonzt_sellDf[['lnonzt_cumulated_profit']],'r',
                 lzt_sellDf[['lzt_cumulated_profit']],'g')

    CPs.legend(['tot','non_lzt','lzt'],loc = 'best')

    # ---------------------------让坐标看得清---------------------------
    ax = plt.gca()
    for label in ax.get_xticklabels():
        label.set_visible(False)
    for label in ax.get_xticklabels()[::xtick_stepnum]:
        label.set_visible(True)
    plt.xticks(rotation=45)
    # ---------------------------让坐标看得清---------------------------
    plt.title(title_cus_day)

    MWDAP = fig.add_subplot(3, 7,3)
    title_cus_day = "Money Weighted Daily Average Profit(%)"

    Daily_Average_Sell_Profit = pd.DataFrame(
        np.divide(sellSampleDf.groupby('买入日期')['加权收益率'].sum(), sellSampleDf.groupby('买入日期')['买入金额'].sum())).reindex(tot_sell_dt).fillna(0)
    Daily_Average_Sell_Profit.columns = ['average_profit']
    Daily_Average_Sell_Profit_positive = Daily_Average_Sell_Profit[Daily_Average_Sell_Profit['average_profit'] >= 0].reindex(Daily_Average_Sell_Profit.index).fillna(0)
    Daily_Average_Sell_Profit_positive.columns = ['postive_average']
    MWDAP.bar(Daily_Average_Sell_Profit_positive.index, Daily_Average_Sell_Profit_positive['postive_average'],
              label='postive_average')
    MWDAP.hold(True)
    Daily_Average_Sell_Profit_negative = Daily_Average_Sell_Profit[Daily_Average_Sell_Profit['average_profit'] < 0].reindex(Daily_Average_Sell_Profit.index).fillna(0)
    Daily_Average_Sell_Profit_negative.columns = ['negtive_average']
    MWDAP.bar(Daily_Average_Sell_Profit_negative.index, Daily_Average_Sell_Profit_negative['negtive_average'], color='r',
              label='negtive_average')
    MWDAP.hold(True)
    Daily_Average_Sell_Profit_roll5 = pd.DataFrame(
        Daily_Average_Sell_Profit['average_profit'].rolling(rolldays_num, 1).mean())
    Daily_Average_Sell_Profit_roll5.columns = ['average_roll%sdays'%str(rolldays_num)]
    Daily_Average_Sell_Profit_roll5.index.name = 'Date'
    #MWDAP.plot(Daily_Average_Sell_Profit_roll5['average_profit_roll%sdays'%str(rolldays_num)],'g',Daily_Average_Sell_Profit_positive['average_profit'].rolling(rolldays_num, 1).mean(),'b',Daily_Average_Sell_Profit_negative['average_profit'].rolling(rolldays_num, 1).mean(),'r' )
    MWDAP.plot(Daily_Average_Sell_Profit_roll5.index, Daily_Average_Sell_Profit_roll5['average_roll%sdays'%str(rolldays_num)], color='g', label='average_roll%sdays'%str(rolldays_num))
    MWDAP.legend(loc='best')
    # MWDAP.vlines('2020-06-03', ymin=0, ymax=1, colors='black', linestyles='--')


    # ---------------------------让坐标看得清---------------------------
    ax = plt.gca()
    for label in ax.get_xticklabels():
        label.set_visible(False)
    for label in ax.get_xticklabels()[::xtick_stepnum]:
        label.set_visible(True)
    plt.xticks(rotation=45)
    # ---------------------------让坐标看得清---------------------------
    plt.title(title_cus_day)
    #plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.2, wspace=0.3, hspace=0.5)

    actsellsample = fig.add_subplot(3, 7, 12)
    title_cus_day = 'Average Profit(%)'+ ' (Rolling %s samples)'%str(rollnums_num)
    #sellSampleDf.sort_values(by=['买入日期'],inplace=True)
    sellSampleDf['Sample'] = list(range(1, len(sellSampleDf) + 1))
    #sellSampleDf['Sample_str'] = sellSampleDf['Sample'].astype(str)
    sellSampleDf.set_index(['Sample'], inplace=True)

    # sell_df = pd.DataFrame(sellSampleDf['卖出部分收益率(%)'].rolling(rollnums_num, 5).mean().dropna())   # todo: 改回成5天
    sell_df = pd.DataFrame(sellSampleDf['卖出部分收益率(%)'].rolling(rollnums_num, 2).mean().dropna())

    # print(len(sell_df))

    sell_df.columns = ['average_by_sample']
    sell_df.index.name = 'Sample'
    actsellsample.bar(sell_df.index, sell_df['average_by_sample'], label='average_by_sample')

    if strategy == 'Leda':
        sell_df_roll = cal_cumsum_mean(sellSampleDf['卖出部分收益率(%)'], 10)  # 因为Leda样本数量太少
    else:
        sell_df_roll = cal_cumsum_mean(sellSampleDf['卖出部分收益率(%)'], rollnums_num)
    sell_df_roll = sell_df_roll.loc[sell_df.index].reindex(sell_df.index)
    sell_df_roll.columns = ['cumulated_average_by_sample']
    sell_df_roll.index.name = 'Sample'
    actsellsample.plot(sell_df_roll.index,sell_df_roll['cumulated_average_by_sample'], color='r',label='cumulated_average_by_sample')
    #actsellsample.vlines('2020-06-03', ymin=-5, ymax=7, colors='r', linestyles='--')
    actsellsample.legend(loc='best')
    actsellsample.set_ylim(-3.5, 6.5)

    # ---------------------------让坐标看得清---------------------------
    ax = plt.gca()
    for label in ax.get_xticklabels():
        label.set_visible(False)
    for label in ax.get_xticklabels()[::200]:
        label.set_visible(True)
    plt.xticks(rotation=90)
    # ---------------------------让坐标看得清---------------------------
    plt.title(title_cus_day)

    # 20240805 绘制参与率折线图
    ATTEND = fig.add_subplot(3, 7, 15)
    title = 'Sample Participation Rate'
    Label_summary = Label_summary[Label_summary['dt'] >= pd.to_datetime(year_start_date).strftime('%Y-%m-%d')]
    signal_label = Label_summary[['dt', 'shouldBuySignal']].groupby('dt').apply(lambda x: x['shouldBuySignal'].sum() / x.count())[['shouldBuySignal']]
    signal_label.columns = ['Participation Rate']
    signal_label.index.name = 'Buy_Date'
    ATTEND.plot(signal_label.index, signal_label['Participation Rate'], color='r', label='Participation Rate')
    ATTEND.legend(loc='best')
    ATTEND.set_ylim(0, 1.2)
    ax = plt.gca()
    for label in ax.get_xticklabels():
        label.set_visible(False)
    for label in ax.get_xticklabels()[::xtick_stepnum]:
        label.set_visible(True)
    plt.xticks(rotation=45)
    # ---------------------------让坐标看得清---------------------------
    plt.title(title)

    plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.2, wspace=0.3, hspace=0.5)
    if strategy == 'jupiter':
        if sellDf['买入日期'].min()<'2022-01-01':
            plt.savefig("/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/收益画图/%s_%s.png" % (Adate, '生产环境'),dpi=120)
        else:
            plt.savefig("/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/收益画图/%s_%s_2022.png" % (Adate, '生产环境'), dpi=120)
    elif strategy == 'jupiterNew':
        plt.savefig("/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/收益画图/%s_New_%s.png" % (Adate, '生产环境'), dpi=120)
    elif strategy == 'Metis':
        plt.savefig("/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/收益画图/%s_Metis_%s.png" % (Adate, '生产环境'), dpi=120)
    elif strategy == 'Leda':
        plt.savefig("/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/收益画图/%s_Leda_%s.png" % (Adate, '生产环境'), dpi=120)
    #    --------------------------------------------------画图------------------------------------------------
    return sellResDf.reset_index()

# 今日卖出信息
def get_sellDfTodayInfo(sellDf,sellDate):
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
            # print('变换前：',data,'变换后：', float(data.split(',')[~0]))
            return float(data.split(',')[~0])
    todaySellResDf.loc['卖出盈利（元）'] = ((0.9995*todaySellDf['卖出成交均价'].apply(return_last_comma) - todaySellDf['买入成交均价'])* todaySellDf['卖出数量'].apply(return_last_comma)).sum()-((0.0000641*(todaySellDf['卖出成交均价'].apply(return_last_comma)+todaySellDf['买入成交均价']))* todaySellDf['卖出数量'].apply(return_last_comma)).sum()
    todaySellResDf.loc['次均等权卖出收益率(%)'] = '%.2f%%'%((todaySellDf['卖出成交均价'].apply(return_last_comma)/todaySellDf['买入成交均价'] - 1).mean()*100)
    todaySellResDf.loc['次均成交额加权收益率(%)'] = '%.2f%%'%(100*((todaySellDf['买入成交均价']*todaySellDf['卖出数量'].apply(return_last_comma))*(todaySellDf['卖出成交均价'].apply(return_last_comma)/todaySellDf['买入成交均价'] - 1)).sum()/\
        ((todaySellDf['买入成交均价']*todaySellDf['卖出数量'].apply(return_last_comma)).sum()))
    todaySellResDf.loc['今日卖出胜率'] = '%.2f%%'%(((todaySellDf['卖出成交均价'].apply(return_last_comma) - todaySellDf['买入成交均价'])>0).sum()/len(todaySellDf)*100)
    return todaySellResDf.reset_index()

# 创业板信息
def get_cybDfTotalInfo(cybsellDf,Adate,strategy='jupiter'):
    if len(cybsellDf)==0:
        return
    # cybsellDf.replace(np.nan,'',inplace=True)
    cybsellResDf = pd.DataFrame(columns=['value'])
    sellSampleDf = cybsellDf[cybsellDf['是否全部卖出'] == 1]
    sellSampleDf['加权收益率'] = sellSampleDf['买入金额'] * sellSampleDf['卖出部分收益率(%)']
    cybsellResDf.loc['累计全部卖出样本数'] = len(sellSampleDf)
    cybsellResDf.loc['累计盈利'] = cybsellDf[(cybsellDf['是否全部卖出'] == 1) | (cybsellDf['是否全部卖出'] == 0)]['卖出部分盈利金额'].sum()
    cybsellResDf.loc['次均等权卖出收益率(%)'] = '%.2f%%' % (sellSampleDf['卖出部分收益率(%)'].mean())
    cybsellResDf.loc['次均成交额加权收益率(%)'] = '%.2f%%' % (sellSampleDf['加权收益率'].sum() / sellSampleDf['买入金额'].sum())

    if len(sellSampleDf) == 0:
        cybsellResDf.loc['累计胜率'] = 0
    else:
        cybsellResDf.loc['累计胜率'] = '%.2f%%' % (len(sellSampleDf[sellSampleDf['理论是否预测正确'] == 1]) / len(sellSampleDf) * 100)
    #    sellResDf.to_excel(commonPath+r'\卖出汇总.xlsx')
    cybsellResDf.loc['预测为1实际为1平均买入金额'] = str(round(sellSampleDf[sellSampleDf['理论是否预测正确'] == 1]['买入金额'].mean(), 2))
    cybsellResDf.loc['预测为1实际为1平均卖出收益率（%）'] = '%.2f%%' % (sellSampleDf[sellSampleDf['理论是否预测正确'] == 1]['卖出部分收益率(%)'].mean())
    cybsellResDf.loc['预测为1实际为1次均成交额加权卖出收益率（%）'] = '%.2f%%' % (
                sellSampleDf[sellSampleDf['理论是否预测正确'] == 1]['卖出部分盈利金额'].sum() / sellSampleDf[sellSampleDf['理论是否预测正确'] == 1]['买入金额'].sum() * 100)

    cybsellResDf.loc['预测为1实际为0平均买入金额'] = str(round(sellSampleDf[sellSampleDf['理论是否预测正确'] == 0]['买入金额'].mean(), 2))
    cybsellResDf.loc['预测为1实际为0平均卖出收益率（%）'] = '%.2f%%' % (sellSampleDf[sellSampleDf['理论是否预测正确'] == 0]['卖出部分收益率(%)'].mean())
    cybsellResDf.loc['预测为1实际为0次均成交额加权卖出收益率（%）'] = '%.2f%%' % (
                sellSampleDf[sellSampleDf['理论是否预测正确'] == 0]['卖出部分盈利金额'].sum() / sellSampleDf[sellSampleDf['理论是否预测正确'] == 0]['买入金额'].sum() * 100)
    cybsellResDf.loc['预测为1样本盈亏比'] = str(abs(
        round((sellSampleDf[sellSampleDf['理论是否预测正确'] == 1]['卖出部分盈利金额'].mean()) / sellSampleDf[sellSampleDf['理论是否预测正确'] == 0]['卖出部分盈利金额'].mean(), 2)))

    return cybsellResDf.reset_index()

# 前日涨停信息
def get_lztDfTotalInfo(cybsellDf,Adate,strategy='jupiter'):
    if len(cybsellDf)==0:
        return
    if strategy == 'jupiter':
        labels_zt = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发标签汇总_%s.xlsx' % Adate)
    elif strategy == 'jupiterNew':
        labels_zt = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发标签汇总New_%s.xlsx' % Adate)
    elif strategy == 'Metis':
        labels_zt = pd.read_excel('/data/group/800463/日内强势股/metis_log_parse/因子耗时/实盘触发标签汇总Metis_%s.xlsx' % Adate)
    elif strategy == 'Leda':
        labels_zt = pd.read_excel('/data/group/800463/日内强势股/leda_log_parse/因子耗时/实盘触发标签汇总Leda_%s.xlsx' % Adate)
    # cybsellDf.replace(np.nan,'',inplace=True)
    cybsellResDf = pd.DataFrame(columns=['value'])
    sellSampleDf = cybsellDf[cybsellDf['是否全部卖出'] == 1]
    sellSampleDf['加权收益率'] = sellSampleDf['买入金额'] * sellSampleDf['卖出部分收益率(%)']
    cybsellResDf.loc['累计全部卖出样本数'] = len(sellSampleDf)
    cybsellResDf.loc['累计盈利'] = cybsellDf[(cybsellDf['是否全部卖出'] == 1) | (cybsellDf['是否全部卖出'] == 0)]['卖出部分盈利金额'].sum()
    cybsellDf_2021 = cybsellDf[(cybsellDf['买入日期']>='2023-12-30') & (cybsellDf['买入日期']<'2024-12-31')]
    cybsellResDf.loc['2024累计盈利'] = cybsellDf_2021[(cybsellDf_2021['是否全部卖出']==1)|(cybsellDf_2021['是否全部卖出']==0)]['卖出部分盈利金额'].sum()
    cybsellResDf.loc['次均等权卖出收益率(%)'] = '%.2f%%' % (sellSampleDf['卖出部分收益率(%)'].mean())
    cybsellResDf.loc['次均成交额加权收益率(%)'] = '%.2f%%' % (sellSampleDf['加权收益率'].sum() / sellSampleDf['买入金额'].sum())
    cybsellResDf.loc['累计参与率'] = '%.2f%%' % (len(labels_zt[(labels_zt['shouldBuySignal']==1)]) / len(labels_zt) * 100)
    cybsellResDf.loc['累计交易胜率'] = '%.2f%%' % (len(sellSampleDf[sellSampleDf['实际是否正收益'] == 1]) / len(sellSampleDf) * 100)

    #    sellResDf.to_excel(commonPath+r'\卖出汇总.xlsx')
    cybsellResDf.loc['预测为1实际为1平均买入金额'] = str(round(sellSampleDf[sellSampleDf['理论是否预测正确'] == 1]['买入金额'].mean(), 2))
    cybsellResDf.loc['预测为1实际为1平均卖出收益率（%）'] = '%.2f%%' % (sellSampleDf[sellSampleDf['理论是否预测正确'] == 1]['卖出部分收益率(%)'].mean())
    cybsellResDf.loc['预测为1实际为1次均成交额加权卖出收益率（%）'] = '%.2f%%' % (
                sellSampleDf[sellSampleDf['理论是否预测正确'] == 1]['卖出部分盈利金额'].sum() / sellSampleDf[sellSampleDf['理论是否预测正确'] == 1]['买入金额'].sum() * 100)

    cybsellResDf.loc['预测为1实际为0平均买入金额'] = str(round(sellSampleDf[sellSampleDf['理论是否预测正确'] == 0]['买入金额'].mean(), 2))
    cybsellResDf.loc['预测为1实际为0平均卖出收益率（%）'] = '%.2f%%' % (sellSampleDf[sellSampleDf['理论是否预测正确'] == 0]['卖出部分收益率(%)'].mean())
    cybsellResDf.loc['预测为1实际为0次均成交额加权卖出收益率（%）'] = '%.2f%%' % (
                sellSampleDf[sellSampleDf['理论是否预测正确'] == 0]['卖出部分盈利金额'].sum() / sellSampleDf[sellSampleDf['理论是否预测正确'] == 0]['买入金额'].sum() * 100)
    cybsellResDf.loc['预测为1样本盈亏比'] = str(abs(
        round((sellSampleDf[sellSampleDf['理论是否预测正确'] == 1]['卖出部分盈利金额'].mean()) / sellSampleDf[sellSampleDf['理论是否预测正确'] == 0]['卖出部分盈利金额'].mean(), 2)))

    return cybsellResDf.reset_index()

# 前日非涨停信息
def get_lnonztDfTotalInfo(cybsellDf,Adate,strategy= 'jupiter'):
    if len(cybsellDf)==0:
        return
    if strategy == 'jupiter':
        labels_zt = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发标签汇总_%s.xlsx' % Adate)
    elif strategy == 'jupiterNew':
        labels_zt = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发标签汇总New_%s.xlsx' % Adate)
    elif strategy == 'Metis':
        labels_zt = pd.read_excel('/data/group/800463/日内强势股/metis_log_parse/因子耗时/实盘触发标签汇总Metis_%s.xlsx' % Adate)
    elif strategy == 'Leda':
        labels_zt = pd.read_excel('/data/group/800463/日内强势股/leda_log_parse/因子耗时/实盘触发标签汇总Leda_%s.xlsx' % Adate)
    # cybsellDf.replace(np.nan,'',inplace=True)
    cybsellResDf = pd.DataFrame(columns=['value'])
    sellSampleDf = cybsellDf[cybsellDf['是否全部卖出'] == 1]
    sellSampleDf['加权收益率'] = sellSampleDf['买入金额'] * sellSampleDf['卖出部分收益率(%)']
    cybsellResDf.loc['累计全部卖出样本数'] = len(sellSampleDf)
    cybsellDf['卖出部分盈利金额'] = cybsellDf['卖出部分盈利金额'].replace('', 0)
    sellSampleDf['卖出部分盈利金额'] = sellSampleDf['卖出部分盈利金额'].replace('', 0)
    cybsellResDf.loc['累计盈利'] = cybsellDf[(cybsellDf['是否全部卖出'] == 1) | (cybsellDf['是否全部卖出'] == 0)]['卖出部分盈利金额'].sum()
    cybsellDf_2021 = cybsellDf[(cybsellDf['买入日期']>='2023-12-30') & (cybsellDf['买入日期']<'2024-12-31')]
    cybsellResDf.loc['2024累计盈利'] = cybsellDf_2021[(cybsellDf_2021['是否全部卖出']==1)|(cybsellDf_2021['是否全部卖出']==0)]['卖出部分盈利金额'].sum()
    cybsellResDf.loc['次均等权卖出收益率(%)'] = '%.2f%%' % (sellSampleDf['卖出部分收益率(%)'].mean())
    cybsellResDf.loc['次均成交额加权收益率(%)'] = '%.2f%%' % (sellSampleDf['加权收益率'].sum() / sellSampleDf['买入金额'].sum())

    cybsellResDf.loc['累计参与率'] = '%.2f%%' % (len(labels_zt[labels_zt['shouldBuySignal']==1 ]) / len(labels_zt) * 100)

    cybsellResDf.loc['累计交易胜率'] = '%.2f%%' % (len(sellSampleDf[sellSampleDf['实际是否正收益'] == 1]) / len(sellSampleDf) * 100)

    return cybsellResDf.reset_index()
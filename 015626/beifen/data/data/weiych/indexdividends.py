# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 16:24:12 2019

@author: 013547
"""

import pandas as pd
from WindPy import *
import numpy as np
import datetime as dt
import math
import random

random.seed(123)
w.start()


def Repair_Code(code_list):
    l = []
    for code in code_list:
        code = str(code)
        if len(code) < 6:
            code = '0' * (6 - len(code)) + code
        if code[0] == '6':
            code += '.SH'
        else:
            code += '.SZ'
        l.append(code)
    return l

# def Date_Ctrl():
#     tradingDates = w.tdays((dt.datetime(2019, 12, 6, 6, 29, 35, 837332) - dt.timedelta(30)).strftime('%Y%m%d'),
#                            (dt.datetime(2019, 12, 6, 6, 29, 35, 837332) + dt.timedelta(30)).strftime('%Y%m%d'), "").Data[0]
#     # print(w.tdays((dt.datetime(2019, 12, 6, 6, 29, 35, 837332) - dt.timedelta(30)).strftime('%Y%m%d'),
#     #                        (dt.datetime(2019, 12, 6, 6, 29, 35, 837332) + dt.timedelta(30)).strftime('%Y%m%d'), ""))
#     tradingDates = [d.strftime('%Y%m%d') for d in tradingDates]
#     print(tradingDates)
#     least_trading_date = \
#     w.tdays((dt.datetime(2019, 12, 6, 6, 29, 35, 837332) - dt.timedelta(30)).strftime('%Y%m%d'), dt.datetime(2019, 12, 6, 6, 29, 35, 837332).strftime('%Y%m%d'), "").Data[
#         0][-1].strftime('%Y%m%d')
#     date = tradingDates[tradingDates.index(least_trading_date) - 1]
#     year = int(date[: 4])
#     weeklater = tradingDates[tradingDates.index(date) + 5]
#     return least_trading_date, date, weeklater, year

def Date_Ctrl():
    dtnowtime = dt.datetime(2019, 12, 6, 6, 29, 35, 837332)
    tradingDates = w.tdays((dtnowtime - dt.timedelta(30)).strftime('%Y%m%d'),
                           (dtnowtime + dt.timedelta(30)).strftime('%Y%m%d'), "").Data[0]
    # print(w.tdays((dt.datetime(2019, 12, 6, 6, 29, 35, 837332) - dt.timedelta(30)).strftime('%Y%m%d'),
    #                        (dt.datetime(2019, 12, 6, 6, 29, 35, 837332) + dt.timedelta(30)).strftime('%Y%m%d'), ""))
    tradingDates = [d.strftime('%Y%m%d') for d in tradingDates]
    print(tradingDates)
    least_trading_date = \
    w.tdays((dtnowtime - dt.timedelta(30)).strftime('%Y%m%d'), dtnowtime.strftime('%Y%m%d'), "").Data[
        0][-1].strftime('%Y%m%d')
    date = tradingDates[tradingDates.index(least_trading_date) - 1]
    year = int(date[: 4])
    weeklater = tradingDates[tradingDates.index(date) + 5]
    return least_trading_date, date, weeklater, year


least_trading_date, date, weeklater, year = Date_Ctrl()
# print(least_trading_date, date, weeklater, year)
# exit()

# 获取每支成分股的权重数据，以及当日指数收盘价
def Index_Info(aim, date):
    if aim == 'HS300':
        future_code = 'IF.CFE'
        tmp = '000300.SH'
    elif aim == 'ZZ500':
        future_code = 'IC.CFE'
        tmp = '000905.SH'
    elif aim == 'SH50':
        future_code = 'IH.CFE'
        tmp = '000016.SH'
    data = pd.read_excel('Z:\\warehouse\\prod\\LOCAL_DATA\\INDEX_BACKUP\\excel_raw\\%s\\%sweightnextday%s.xls' % (
    tmp[: -3], tmp[: -3], date))
    tickers = Repair_Code(list(data['成分券代码\nConstituent Code']))
    weights = list(data['权重(%)\nWeight(%)'] / 100)
    idx_close = w.wsd(tmp, "close", date, date, "").Data[0][0]
    return tickers, weights, future_code, idx_close


def Predict_Div_Exdate(tickers, year, date, weeklater0):
    try:
        dates = [x.strftime('%Y%m%d') for x in w.tdays(weeklater0, str(year) + "-08-15", "").Data[0]]
    except:
        dates = []
    tmp = []
    # 获取除权除息日
    year1 = w.wss(tickers, "div_exdate", "rptDate=%s1231" % (str(year - 2))).Data[0]
    for i in range(len(tickers)):
        if year1[i].year < year - 1:
            year1[i] = np.nan
        else:
            year1[i] = year1[i].strftime('%Y%m%d')
    year2 = w.wss(tickers, "div_exdate", "rptDate=%s1231" % (str(year - 3))).Data[0]
    for i in range(len(tickers)):
        if year2[i].year < year - 2:
            year2[i] = np.nan
        else:
            year2[i] = year2[i].strftime('%Y%m%d')

    for i in range(len(tickers)):
        if (year * 10000 + 430) <= int(date) <= (year * 10000 + 731):
            weeklater = dates[random.randint(0, len(dates) - 1)]
        else:
            weeklater = weeklater0
        # 都以远的时间为准
        # case1.1  上年有分红，上上年无分红，则比较上年时间和一周后
        if (type(year1[i]) != type(np.nan)) and (type(year2[i]) == type(np.nan)):
            if int(year1[i][4:]) >= int(weeklater0[4:]):
                tmp.append(weeklater[: 4] + year1[i][4:])
            else:
                tmp.append(weeklater)
        # case1.2  上年无分红，上上年有分红，则比较上上年时间和一周后
        elif (type(year1[i]) == type(np.nan)) and (type(year2[i]) != type(np.nan)):
            if int(year2[i][4:]) >= int(weeklater0[4:]):
                tmp.append(weeklater[: 4] + year2[i][4:])
            else:
                tmp.append(weeklater)
        # case1.3  上年无分红，上上年无分红，则认为今年分红日期随机
        elif (type(year1[i]) == type(np.nan)) and (type(year2[i]) == type(np.nan)):
            tmp.append(weeklater)
        else:
            d0 = int(date[4:])
            dw = int(weeklater0[4:])
            d1 = int(year1[i][4:])
            d2 = int(year2[i][4:])
            # case2.1  两年都在今天之前，则认为一周后会分红。时间为一周后随机
            if d1 <= d0 and d2 <= d0:
                tmp.append(weeklater)
            # case2.2  上年都在今天之前，上上年在今天之后，则比较一周后和上上年
            elif d1 <= d0 <= d2:
                if d2 <= dw:
                    tmp.append(weeklater0)
                else:
                    tmp.append(str(year) + year2[i][4:])
            # case2.3  上上年都在今天之前，上年在今天之后，则比较一周后和上年
            elif d2 <= d0 <= d1:
                if d1 <= dw:
                    tmp.append(weeklater0)
                else:
                    tmp.append(str(year) + year1[i][4:])
            # case2.4  两年都在今天之后，则比较一周后、上年、上上年
            elif d0 <= d1 and d0 <= d2:
                mx = max(d1, d2, dw)
                if len(str(mx)) < 4:
                    tmp.append(str(year) + '0' + str(mx))
                else:
                    tmp.append(str(year) + str(mx))
    dic = {tickers[x]: tmp[x] for x in range(len(tickers))}
    predict_div_exdate = dic
    return predict_div_exdate


def Div_Info(year, date, predict_div_exdate):
    # 分红实施
    data = w.wset("bonus", "orderby=报告期;year=%s;period=y1;sectorid=a001010100000000" % (str(year - 1)))
    df = pd.DataFrame(data.Data).T
    if len(df) == 0:
        return pd.DataFrame(columns=['dividendsper_share_pretax', 'exrights_exdividend_date', 'wind_code'])
    df.columns = data.Fields
    df = df[(df['dividendsper_share_pretax'] > 0) & (df['dividend_object'] == '普通股股东')]
    a = list(df['exrights_exdividend_date'])
    a = [x.strftime('%Y%m%d') for x in a]
    res1 = pd.DataFrame({'dividendsper_share_pretax': df['dividendsper_share_pretax'], 'exrights_exdividend_date': a})
    res1['wind_code'] = df['wind_code']

    data = w.wset("dividendproposal",
                  "ordertype=1;startdate=%s-01-01;enddate=%s;sectorid=a001010100000000" % (str(year), date))
    df = pd.DataFrame(data.Data).T
    df.columns = data.Fields
    df = df[(df['progress'] == '董事会预案') | (df['progress'] == '股东大会通过')]
    tmp = []
    for code in list(df['wind_code']):
        if code in predict_div_exdate.keys():
            tmp.append(predict_div_exdate[code])
        else:
            tmp.append(np.nan)
    res2 = pd.DataFrame({'dividendsper_share_pretax': df['cash_dividend'], 'exrights_exdividend_date': tmp})
    res2['wind_code'] = list(df['wind_code'])

    div_info = res1.append(res2).drop_duplicates(subset='wind_code', keep='first').set_index('wind_code', drop=True)
    return div_info


def Total_Shares_Info(tickers, date):
    data = w.wss(tickers, "total_shares", "unit=1;tradeDate=%s" % date).Data[0]
    dic = {tickers[x]: int(data[x]) for x in range(len(tickers))}
    return dic


def Predict_Net_Profit(year, date):
    path = 'Z:\warehouse\\prod\\LOCAL_DATA\\CSV\\gogoal_htsc\\con_forecast_stk\\%s.csv' % (date)
    data = pd.read_csv(path, header=0)
    data = data[(data['RPT_DATE'] == year - 1) & (data['RPT_TYPE'] == 4)]
    #    data = data[['Ticker', 'C4']]  #C4单位为万元
    #    data = data.set_index('Ticker', drop = True)
    a = list(data['Ticker'])
    b = list(data['C4'] * 10000)
    dic = {a[x]: b[x] for x in range(len(data))}
    return dic

# 年度现金分红比例
def Predict_Dividend_Payoutratio(tickers, year):
    pdpr = []
    dp1 = w.wss(tickers, "div_payoutratio", "year=%s" % (str(year - 2))).Data[0]
    dp2 = w.wss(tickers, "div_payoutratio", "year=%s" % (str(year - 3))).Data[0]
    dp3 = w.wss(tickers, "div_payoutratio", "year=%s" % (str(year - 4))).Data[0]
    for i in range(len(tickers)):
        pdpr.append(np.nanmean([dp1[i], dp2[i], dp3[i]]) / 100)
    dic = {tickers[x]: pdpr[x] for x in range(len(tickers))}
    return dic


def Combine_Info(idx_close, tickers, div_info, predict_net_profit, predict_dividend_payoutratio, total_shares_info):
    res = pd.DataFrame()
    for i in range(len(tickers)):
        ticker = tickers[i]
        if ticker in list(div_info.index):
            res = res.append(div_info.loc[ticker, :])
        else:
            if (predict_net_profit[ticker] < 0) | (int(date) > int(date[: 4] + '0430')):
                res = res.append(pd.DataFrame([[0, np.nan]], index=[ticker],
                                              columns=['dividendsper_share_pretax', 'exrights_exdividend_date']))
            else:
                tmp = predict_net_profit[ticker] * predict_dividend_payoutratio[ticker] / total_shares_info[ticker]
                res = res.append(pd.DataFrame([[tmp, predict_div_exdate[ticker]]], index=[ticker],
                                              columns=['dividendsper_share_pretax', 'exrights_exdividend_date']))
    res = res.reset_index()
    res['close'] = w.wsd(tickers, "close", date, date, "").Data[0]
    res['weights'] = weights
    res['point'] = res['dividendsper_share_pretax'] / res['close'] * res['weights'] * idx_close
    df = res[['point', 'exrights_exdividend_date', 'dividendsper_share_pretax']]
    df = df.sort_values(by='exrights_exdividend_date').dropna()
    return df


def Futures_Info(future_code, year, least_trading_date, date, combine_info):
    if future_code[: 2] == 'IF':
        index = '000300.SH'
    elif future_code[: 2] == 'IC':
        index = '000905.SH'
    elif future_code[: 2] == 'IH':
        index = '000016.SH'
    data = w.wset("futurecc", "startdate=%s-01-01;enddate=%s-12-31;wind_code=%s" % (str(year), str(year), future_code))
    df = pd.DataFrame(data.Data).T
    df.columns = data.Fields
    a = df['last_trade_date']
    a = [int(x.strftime('%Y%m%d')) for x in a]
    res = df[['wind_code']]
    res['last_trade_date'] = a
    res = res[res['last_trade_date'] >= int(least_trading_date)]

    tmp = []
    last_trade_date = list(res['last_trade_date'])
    last_trade_date.sort()
    combine_info['exrights_exdividend_date'] = combine_info['exrights_exdividend_date'].astype(int)
    for i in range(len(last_trade_date)):
        sdate = least_trading_date
        edate = last_trade_date[i]
        tmp_df = combine_info[combine_info['exrights_exdividend_date'] > int(sdate)]
        tmp_df = tmp_df[tmp_df['exrights_exdividend_date'] < edate]
        tmp.append(sum(tmp_df['point']))
    res['point'] = tmp
    res['future_close'] = w.wsd(list(res['wind_code']), "close", date, date, "").Data[0]
    res['idx_close'] = w.wsd(index, "close", date, date, "").Data[0][0]
    res['PD'] = res['future_close'] - res['idx_close']
    res['PD_with_div'] = res['PD'] + res['point']
    return res


futures_info_dic = {}
future_detail_info_dic = {}
aims = ['HS300', 'ZZ500', 'SH50']
for aim in aims:
# aim = 'HS300'
    # 获取每支成分股的权重数据，以及当日指数收盘价
    tickers, weights, future_code, idx_close = Index_Info(aim, date)
    # 预测今年每支股票的除权除息日
    predict_div_exdate = Predict_Div_Exdate(tickers, year, least_trading_date, weeklater)
    # 获取分红详细信息
    div_info = Div_Info(year, least_trading_date, predict_div_exdate)
    # 获取总股本
    total_shares_info = Total_Shares_Info(tickers, least_trading_date)
    # 获取预测利润
    predict_net_profit = Predict_Net_Profit(year, date)
    # 获取年度现金分红比例
    predict_dividend_payoutratio = Predict_Dividend_Payoutratio(tickers, year)
    combine_info = Combine_Info(idx_close, tickers, div_info, predict_net_profit, predict_dividend_payoutratio,
                                total_shares_info)
    future_detail_info_dic[aim] = combine_info
    futures_info = Futures_Info(future_code, year, least_trading_date, date, combine_info)
    futures_info_dic[aim] = futures_info


# ------------------------------------------------------------------------------
# 公共信息

def Fetch_Info(futures_info_dic, aim):
    data = futures_info_dic[aim]
    exp_dic = {}
    point_acc_dic = {}
    codes = list(data['wind_code'])
    last_trade_date = list(data['last_trade_date'])
    for i in range(len(codes)):
        # exp_dic[codes[i]] = (dt.datetime.strptime(str(last_trade_date[i]), '%Y%m%d').date() - dt.datetime(2019, 12, 6, 6, 29, 35, 837332).date()).days
        exp_dic[codes[i]] = (dt.datetime.strptime(str(last_trade_date[i]), '%Y%m%d').date() - dt.datetime(2019, 12, 6, 6, 29, 35, 837332).date()).days
        point_acc_dic[codes[i]] = list(data['point'])[i]
    return exp_dic, point_acc_dic, codes


look_back = 5
# import pdb;pdb.set_trace()
# 中国国债到期收益率（10年）
risk_free_rate = w.edb("M1000166", least_trading_date, least_trading_date, "Fill = Previous").Data[0][0] / 100


# ------------------------------------------------------------------------------

# 套利
def FetchTheoreticalPriceDelta_TL(codes, risk_free_rate, exp_dic, point_acc_dic):
    # etime = dt.datetime(2019, 12, 6, 6, 29, 35, 837332).date()
    etime = dt.datetime(2019, 12, 6, 6, 29, 35, 837332).date()
    stime = etime - dt.timedelta(30)

    res = []
    for code in codes:
        if code[: 2] == 'IF':
            index = '000300.SH'
        elif code[: 2] == 'IC':
            index = '000905.SH'
        elif code[: 2] == 'IH':
            index = '000016.SH'
        index_close = w.wsd(index, "pre_close", stime, etime, "").Data[0][-1]
        tmp = risk_free_rate * exp_dic[code] / 365
        res0 = (index_close - point_acc_dic[code]) * (math.exp(tmp)) - index_close
        res.append(res0)
    return res


def FetchHistoricalInfo_TL(codes, look_back):
    time_now = dt.datetime(2019, 12, 6, 6, 29, 35, 837332)
    trading_dates = \
    w.tdays((dt.datetime(2019, 12, 6, 6, 29, 35, 837332) - dt.timedelta(30)).strftime('%Y%m%d'), dt.datetime(2019, 12, 6, 6, 29, 35, 837332).strftime('%Y%m%d'), "").Data[0]
    trading_dates = [d.strftime('%Y%m%d') for d in trading_dates]
    mean = []
    sigma = []
    for code in codes:
        if code[: 2] == 'IF':
            index = '000300.SH'
        elif code[: 2] == 'IC':
            index = '000905.SH'
        elif code[: 2] == 'IH':
            index = '000016.SH'
        stime = trading_dates[-look_back]
        data = w.wst(code, "bid1", stime, time_now, '')
        df_future = pd.DataFrame()
        df_future['Timestamp'] = data.Times
        try:
            df_future[code] = data.Data[0]
            data = w.wst(index, "last", stime, time_now, '')
            df_index = pd.DataFrame()
            df_index['Timestamp'] = data.Times
            df_index[index] = data.Data[0]
            df_index = df_index.fillna(method='ffill')
            tmp = pd.merge(df_index, df_future, how='outer', on='Timestamp').sort_values('Timestamp')
            tmp[aim] = tmp[code].fillna(method='ffill')
            tmp = tmp.dropna()
            tmp = tmp.loc[(tmp[code] > 0)]
            priceDelta = np.array(tmp[code]) - np.array(tmp[index])
            mean.append(np.mean(priceDelta))
            sigma.append(np.std(priceDelta))
        except:
            mean.append(-1)
            sigma.append(-1)
    return mean, sigma


def CheckOI(codes, look_back):
    trading_dates = \
    w.tdays((dt.datetime(2019, 12, 6, 6, 29, 35, 837332) - dt.timedelta(30)).strftime('%Y%m%d'), dt.datetime(2019, 12, 6, 6, 29, 35, 837332).strftime('%Y%m%d'), "").Data[0]
    trading_dates = [d.strftime('%Y%m%d') for d in trading_dates]

    def oi(code):
        ddd = w.wsd(code, "oi", trading_dates[0], trading_dates[-1], "").Data[0]
        try:
            res = np.nansum(ddd[-look_back:])
        except:
            res = -1
        return res

    res = []
    for code in codes:
        res.append(int(oi(code)))
    return res


writer = pd.ExcelWriter('A:\\weiyc\\每日股指期货分红预测\\股指期货分红预测_%s.xlsx' % least_trading_date)
futures = ['HS300', 'ZZ500', 'SH50']
for aim in futures:
# aim = 'HS300'
    exp_dic, point_acc_dic, codes = Fetch_Info(futures_info_dic, aim)
    theoretical_price_delta = FetchTheoreticalPriceDelta_TL(codes, risk_free_rate, exp_dic, point_acc_dic)
    mean, sigma = FetchHistoricalInfo_TL(codes, look_back)
    res = futures_info_dic[aim].copy()
    res.columns = ['证券代码', '交割日', '分红点数', '合约收盘价', '指数收盘价', '实际基差', '含分红基差']
    res['5日基差均值'] = mean
    res['5日基差波动率'] = sigma
    res['持仓量'] = CheckOI(codes, look_back)
    with pd.option_context('display.max_columns', 15):
        print(res)
    res.to_excel(writer, aim, index=False)
    future_detail_info_dic[aim].to_excel(writer, aim + '_details', index=True)
writer.save()


# ------------------------------------------------------------------------------
# 展期

def FetchTheoreticalPriceDelta_ZQ(codes, exp_dic, point_acc_dic, futures_info):
    def Cal(code0, code1):
        futures_info1 = futures_info.set_index('wind_code', drop=True)
        rt = risk_free_rate * exp_dcit0[code0][code1] / 365
        s = futures_info1.loc[code0]['future_close']
        point = point_acc_dic0[code0][code1]
        tpd = (s - point) * math.exp(rt) - s
        return tpd

    exp_dcit0 = {}
    exp_dcit0[codes[0]] = {}
    exp_dcit0[codes[0]][codes[1]] = exp_dic[codes[1]] - exp_dic[codes[0]]
    exp_dcit0[codes[0]][codes[2]] = exp_dic[codes[2]] - exp_dic[codes[0]]
    exp_dcit0[codes[1]] = {}
    exp_dcit0[codes[1]][codes[2]] = exp_dic[codes[2]] - exp_dic[codes[1]]
    exp_dcit0[codes[1]][codes[3]] = exp_dic[codes[3]] - exp_dic[codes[1]]
    exp_dcit0[codes[2]] = {}
    exp_dcit0[codes[2]][codes[3]] = exp_dic[codes[3]] - exp_dic[codes[2]]

    point_acc_dic0 = {}
    point_acc_dic0[codes[0]] = {}
    point_acc_dic0[codes[0]][codes[1]] = point_acc_dic[codes[1]] - point_acc_dic[codes[0]]
    point_acc_dic0[codes[0]][codes[2]] = point_acc_dic[codes[2]] - point_acc_dic[codes[0]]
    point_acc_dic0[codes[1]] = {}
    point_acc_dic0[codes[1]][codes[2]] = point_acc_dic[codes[2]] - point_acc_dic[codes[1]]
    point_acc_dic0[codes[1]][codes[3]] = point_acc_dic[codes[3]] - point_acc_dic[codes[1]]
    point_acc_dic0[codes[2]] = {}
    point_acc_dic0[codes[2]][codes[3]] = point_acc_dic[codes[3]] - point_acc_dic[codes[2]]

    res = {}
    res[codes[0]] = {}
    res[codes[0]][codes[1]] = Cal(codes[0], codes[1])
    res[codes[0]][codes[2]] = Cal(codes[0], codes[2])
    res[codes[1]] = {}
    res[codes[1]][codes[2]] = Cal(codes[1], codes[2])
    res[codes[1]][codes[3]] = Cal(codes[1], codes[3])
    res[codes[2]] = {}
    res[codes[2]][codes[3]] = Cal(codes[2], codes[3])

    return res


futures = ['HS300', 'ZZ500', 'SH50']
for aim in futures:
    futures_info = futures_info_dic[aim]
    exp_dic, point_acc_dic, codes = Fetch_Info(futures_info_dic, aim)
    theoretical_price_delta_ZQ = FetchTheoreticalPriceDelta_ZQ(codes, exp_dic, point_acc_dic, futures_info)
    print(theoretical_price_delta_ZQ)









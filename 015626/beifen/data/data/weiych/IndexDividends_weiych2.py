# -*- coding: utf-8 -*-
"""
Created on 20200107
@author: 015626
"""

import pandas as pd
from WindPy import *
import numpy as np
import datetime as dt
import math
import random
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from multifactor.data.utils import *
from multifactor.utility.dt import *

random.seed(123)
w.start()

class IndexDividends(object):

    def __init__(self, date, futures = ['HS300', 'ZZ500', 'SH50'], lookback = 5, writepath = 'A:\\weiyc\\data\\IndexDividends\\'):
        self.date = str(date)
        self.futures = futures
        self.writepath = writepath
        nowtime = dt.datetime.strptime(self.date,'%Y%m%d')
        tradingDates = get_trading_date_range((nowtime - dt.timedelta(30)).strftime('%Y%m%d'),(nowtime + dt.timedelta(30)).strftime('%Y%m%d'))
        tradingDates = [d.strftime('%Y%m%d') for d in tradingDates]

        self.tradingdays_in_fore30 = tradingDates[ : tradingDates.index(self.date) + 1]
        self.now_trading_date = tradingDates[tradingDates.index(self.date) + 1]
        self.year = int(self.date[: 4])
        self.weeklater = tradingDates[tradingDates.index(self.date) + 5]
        self.lookback = lookback
        self.risk_free_rate = w.edb("M1000166", self.date, self.date, "Fill = Previous").Data[0][0] / 100

    # 获取每支成分股的权重数据，以及当日指数收盘价
    def Index_Info(self, aim):
        if aim == 'HS300':
            future_code = 'IF.CFE'
            tmp = '000300.SH'
        elif aim == 'ZZ500':
            future_code = 'IC.CFE'
            tmp = '000905.SH'
        elif aim == 'SH50':
            future_code = 'IH.CFE'
            tmp = '000016.SH'
        data = pd.read_csv('Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\stock_universe\\%s\\%s.csv' % (aim, self.date))
        tickers = list(data['Ticker'])
        weights = list(data[aim] / 100)
        idx_close = w.wsd(tmp, "close", self.date, self.date, "").Data[0][0]
        return tickers, weights, future_code, idx_close

    # 预测除权除息日
    def Predict_Div_Exdate(self, tickers):
        dates = [] if int(self.weeklater[-4:]) > 815 else [x.strftime('%Y%m%d') for x in get_trading_date_range(self.weeklater, str(self.year) + '0815')]
        tmp = []
        # 获取上年及上上年除权除息日
        year1 = w.wss(tickers, "div_exdate", "rptDate=%s1231" % (str(self.year - 2))).Data[0]
        for i in range(len(tickers)):
            if year1[i].year < self.year - 1:
                year1[i] = np.nan
            else:
                year1[i] = year1[i].strftime('%Y%m%d')
        year2 = w.wss(tickers, "div_exdate", "rptDate=%s1231" % (str(self.year - 3))).Data[0]
        for i in range(len(tickers)):
            if year2[i].year < self.year - 2:
                year2[i] = np.nan
            else:
                year2[i] = year2[i].strftime('%Y%m%d')

        for i in range(len(tickers)):
            if (self.year * 10000 + 430) <= int(self.date) <= (self.year * 10000 + 731):
                weeklater_new = dates[random.randint(0, len(dates) - 1)]
            else:
                weeklater_new = self.weeklater
            # 都以远的时间为准
            # case1.1  上年有分红，上上年无分红，则比较上年时间和一周后
            if (type(year1[i]) != type(np.nan)) and (type(year2[i]) == type(np.nan)):
                if int(year1[i][4:]) >= int(self.weeklater[4:]):
                    tmp.append(weeklater_new[: 4] + year1[i][4:])
                else:
                    tmp.append(weeklater_new)
            # case1.2  上年无分红，上上年有分红，则比较上上年时间和一周后
            elif (type(year1[i]) == type(np.nan)) and (type(year2[i]) != type(np.nan)):
                if int(year2[i][4:]) >= int(self.weeklater[4:]):
                    tmp.append(weeklater_new[: 4] + year2[i][4:])
                else:
                    tmp.append(weeklater_new)
            # case1.3  上年无分红，上上年无分红，则认为今年分红日期随机
            elif (type(year1[i]) == type(np.nan)) and (type(year2[i]) == type(np.nan)):
                tmp.append(weeklater_new)
            else:
                d0 = int(self.date[4:])
                dw = int(self.weeklater[4:])
                d1 = int(year1[i][4:])
                d2 = int(year2[i][4:])
                # case2.1  两年都在今天之前，则认为一周后会分红。时间为一周后随机
                if d1 <= d0 and d2 <= d0:
                    tmp.append(weeklater_new)
                # case2.2  上年都在今天之前，上上年在今天之后，则比较一周后和上上年
                elif d1 <= d0 <= d2:
                    tmp.append(self.weeklater if d2 <= dw else str(self.year) + year2[i][4:])
                # case2.3  上上年都在今天之前，上年在今天之后，则比较一周后和上年
                elif d2 <= d0 <= d1:
                    tmp.append(self.weeklater if d1 <= dw else str(self.year) + year1[i][4:])
                # case2.4  两年都在今天之后，则比较一周后、上年、上上年
                elif d0 <= d1 and d0 <= d2:
                    mx = max(d1, d2, dw)
                    tmp.append(str(self.year) + '0' + str(mx) if len(str(mx)) < 4 else str(self.year) + str(mx))

        dic = {tickers[x]: tmp[x] for x in range(len(tickers))}
        predict_div_exdate = dic
        return predict_div_exdate

    def Div_Info(self, predict_div_exdate):
        # 分红实施
        data = w.wset("bonus", "orderby=报告期;year=%s;period=y1;sectorid=a001010100000000" % (str(self.year - 1)))
        df = pd.DataFrame(data.Data).T
        df.columns = data.Fields
        if len(df) == 0:
            res1 =  pd.DataFrame(columns=['dividendsper_share_pretax', 'exrights_exdividend_date', 'wind_code'])
        else:
            df = df[(df['dividendsper_share_pretax'] > 0) & (df['dividend_object'] == '普通股股东')]
            a = list(df['exrights_exdividend_date'])
            a = [x.strftime('%Y%m%d') for x in a]
            res1 = pd.DataFrame(
                {'dividendsper_share_pretax': df['dividendsper_share_pretax'], 'exrights_exdividend_date': a})
            res1['wind_code'] = df['wind_code']

        data = w.wset("dividendproposal",
                      "ordertype=1;startdate=%s-01-01;enddate=%s;sectorid=a001010100000000" % (str(self.year), self.date))
        df = pd.DataFrame(data.Data).T
        df.columns = data.Fields
        if len(df) == 0:
            res2 = pd.DataFrame(columns=['dividendsper_share_pretax', 'exrights_exdividend_date', 'wind_code'])
        else:
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

    # 获取股票对应的总股数，单位为（股）
    def Total_Shares_Info(self, tickers):
        data = w.wss(tickers, "total_shares", "unit=1;tradeDate=%s" % self.date).Data[0]
        dic = {tickers[x]: int(data[x]) for x in range(len(tickers))}
        return dic

    # 获取公司的净利润
    def Predict_Net_Profit(self):
        # 一致预期归母净利润
        path = 'Z:\warehouse\\prod\\LOCAL_DATA\\CSV\\gogoal_htsc\\con_forecast_stk\\%s.csv' % (self.date)
        data = pd.read_csv(path, header=0)
        data = data[(data['RPT_DATE'] == self.year - 1) & (data['RPT_TYPE'] == 4)]
        a = list(data['Ticker'])
        b = list(data['C4'] * 10000)
        dic = {a[x]: b[x] for x in range(len(data))}

        # 净利润以年报为准，年报没有就用一致预期净利润，这里年报里使用的是（净利润(不含少数股东损益)）
        # yearreport = IO.read_data([str(self.year - 1) + '1231'], columns = ['STATEMENT_TYPE','NET_PROFIT_EXCL_MIN_INT_INC'],
        #                           alt = 'Z:/warehouse/prod/DATABASE/WIND/AShareIncome/AShareIncome.h5')
        # if len(yearreport) > 0:
        #     yearreport = yearreport[yearreport.STATEMENT_TYPE == 408001000.0].reset_index() # 合并报表
        #     yearreport = yearreport[['Ticker', 'NET_PROFIT_EXCL_MIN_INT_INC']].set_index('Ticker')
        #     reportdict = yearreport.to_dict()['NET_PROFIT_EXCL_MIN_INT_INC']
        #     for key in dic.keys():
        #         if key in reportdict.keys():
        #             dic[key] = reportdict[key]
        return dic

    # 年度现金分红比例
    def Predict_Dividend_Payoutratio(self, tickers):
        dp1 = w.wss(tickers, "div_payoutratio", "year=%s" % (str(self.year - 2))).Data[0]
        dp2 = w.wss(tickers, "div_payoutratio", "year=%s" % (str(self.year - 3))).Data[0]
        dp3 = w.wss(tickers, "div_payoutratio", "year=%s" % (str(self.year - 4))).Data[0]
        # 如果超额分红，则不计入
        for i in range(len(tickers)):
            if dp1[i] > 100:
                dp1[i] = np.nan
            if dp2[i] > 100:
                dp2[i] = np.nan
            if dp3[i] > 100:
                dp3[i] = np.nan
        return {tickers[i]: np.nanmean([dp1[i], dp2[i], dp3[i]]) / 100 for i in range(len(tickers))}

    def Combine_Info(self, weights, predict_div_exdate, idx_close, tickers, div_info, predict_net_profit, predict_dividend_payoutratio, total_shares_info):
        res = pd.DataFrame()
        for i in range(len(tickers)):
            ticker = tickers[i]
            # 已经获取到准确的分红信息
            if ticker in list(div_info.index):
                res = res.append(div_info.loc[ticker, :])
            else:
                # 如果净利润为负，或者已经过了4月30年报发布日则认为不分红
                if (predict_net_profit[ticker] < 0) | (int(self.date) > int(self.date[: 4] + '0430')):
                    res = res.append(pd.DataFrame([[0, np.nan]], index=[ticker],
                                                  columns=['dividendsper_share_pretax', 'exrights_exdividend_date']))
                else:
                    # 每股税前分红 = 预测归母净利润 * 分红比例 / 总股本
                    tmp = predict_net_profit[ticker] * predict_dividend_payoutratio[ticker] / total_shares_info[ticker]
                    res = res.append(pd.DataFrame([[tmp, predict_div_exdate[ticker]]], index=[ticker],
                                                  columns=['dividendsper_share_pretax', 'exrights_exdividend_date']))

        res['close'] = w.wsd(tickers, "close", self.date, self.date, "").Data[0]
        res['weights'] = weights
        res['point'] = res['dividendsper_share_pretax'] / res['close'] * res['weights'] * idx_close
        df = res[['point', 'exrights_exdividend_date', 'dividendsper_share_pretax']]
        df = df.sort_values(by='exrights_exdividend_date').dropna()
        return df

    def Futures_Info(self, future_code, combine_info):
        if future_code[: 2] == 'IF':
            index = '000300.SH'
        elif future_code[: 2] == 'IC':
            index = '000905.SH'
        elif future_code[: 2] == 'IH':
            index = '000016.SH'
        # 获取期货合约列表
        data = w.wset("futurecc", "startdate=%s-01-01;enddate=%s-12-31;wind_code=%s" % (str(self.year), str(self.year), future_code))
        df = pd.DataFrame(data.Data).T
        df.columns = data.Fields
        a = df['last_trade_date']
        a = [int(x.strftime('%Y%m%d')) for x in a]
        res = df[['wind_code']]
        res['last_trade_date'] = a
        res = res[res['last_trade_date'] >= int(self.now_trading_date)]

        tmp = []
        last_trade_date = list(res['last_trade_date'])
        last_trade_date.sort()
        combine_info['exrights_exdividend_date'] = combine_info['exrights_exdividend_date'].astype(int)
        for i in range(len(last_trade_date)):
            sdate = self.now_trading_date
            edate = last_trade_date[i]
            tmp_df = combine_info[combine_info['exrights_exdividend_date'] > int(sdate)]
            tmp_df = tmp_df[tmp_df['exrights_exdividend_date'] < edate]
            tmp.append(sum(tmp_df['point']))
        res['point'] = tmp
        res['future_close'] = w.wsd(list(res['wind_code']), "close", self.date, self.date, "").Data[0]
        res['idx_close'] = w.wsd(index, "close", self.date, self.date, "").Data[0][0]
        res['PD'] = res['future_close'] - res['idx_close']
        res['PD_with_div'] = res['PD'] + res['point']
        return res

    def Fetch_Info(self, futures_info_dic, aim):
        data = futures_info_dic[aim]
        exp_dic = {}
        point_acc_dic = {}
        codes = list(data['wind_code'])
        last_trade_date = list(data['last_trade_date'])
        for i in range(len(codes)):
            exp_dic[codes[i]] = (dt.datetime.strptime(str(last_trade_date[i]), '%Y%m%d').date()
                                 - dt.datetime.strptime(self.date, '%Y%m%d').date()).days
            point_acc_dic[codes[i]] = list(data['point'])[i]
        return exp_dic, point_acc_dic, codes

    def FetchHistoricalInfo_TL(self, codes, aim):
        time_now = dt.datetime.strptime(self.now_trading_date, '%Y%m%d')
        mean = []
        sigma = []
        for code in codes:
            if code[: 2] == 'IF':
                index = '000300.SH'
            elif code[: 2] == 'IC':
                index = '000905.SH'
            elif code[: 2] == 'IH':
                index = '000016.SH'
            stime = self.tradingdays_in_fore30[-self.lookback]
            data = w.wst(code, "last", stime, time_now, '')
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

    def CheckOI(self, codes):
        def oi(code):
            ddd = w.wsd(code, "oi", self.tradingdays_in_fore30[0], self.tradingdays_in_fore30[-1], "").Data[0]
            try:
                res = np.nansum(ddd[-1 * self.lookback :])
            except:
                res = -1
            return res

        res = []
        for code in codes:
            res.append(int(oi(code)))
        return res

    # 无风险利率成本
    def FetchRiskFreeCosts(self, codes, exp_dic):
        riskfree_costs = []
        for code in codes:
            if code[: 2] == 'IF':
                index = '000300.SH'
            elif code[: 2] == 'IC':
                index = '000905.SH'
            elif code[: 2] == 'IH':
                index = '000016.SH'
            index_close = w.wsd(index, "close", self.date, self.date, "").Data[0][-1]
            tmp = self.risk_free_rate * exp_dic[code] / 365
            res0 = index_close * tmp
            riskfree_costs.append(res0)
        return riskfree_costs

    def run(self):
        futures_info_dic = {}
        future_detail_info_dic = {}
        writer = pd.ExcelWriter(os.path.join(self.writepath, 'IndexDividends_%s.xlsx') % self.now_trading_date)

        for aim in self.futures:
            # aim = 'HS300'
            # 获取每支成分股的权重数据，以及当日指数收盘价
            tickers, weights, future_code, idx_close = self.Index_Info(aim)
            # 预测今年每支股票的除权除息日
            predict_div_exdate = self.Predict_Div_Exdate(tickers)
            # 获取分红详细信息
            div_info = self.Div_Info(predict_div_exdate)
            # 获取总股本
            total_shares_info = self.Total_Shares_Info(tickers)
            # 获取预测利润
            predict_net_profit = self.Predict_Net_Profit()
            # 获取年度现金分红比例
            predict_dividend_payoutratio = self.Predict_Dividend_Payoutratio(tickers)
            # 获取每支成分股对指数点位影响的详细信息
            combine_info = self.Combine_Info(weights, predict_div_exdate, idx_close, tickers, div_info, predict_net_profit, predict_dividend_payoutratio,
                                        total_shares_info)
            future_detail_info_dic[aim] = combine_info
            # 获取分红对每个指数点位影响的信息
            futures_info = self.Futures_Info(future_code, combine_info)
            futures_info_dic[aim] = futures_info

        for aim in self.futures:
            exp_dic, point_acc_dic, codes = self.Fetch_Info(futures_info_dic, aim)
            mean, sigma = self.FetchHistoricalInfo_TL(codes, aim)
            res = futures_info_dic[aim].copy()
            res.columns = ['证券代码', '交割日', '分红点数', '合约收盘价', '指数收盘价', '实际基差', '含分红基差']
            res['无风险利率成本'] = self.FetchRiskFreeCosts(codes, exp_dic)
            res['5日基差均值'] = mean
            res['5日基差波动率'] = sigma
            res['5日持仓量总和'] = self.CheckOI(codes)
            with pd.option_context('display.max_columns', 15):
                print(res)
            res.to_excel(writer, aim, index=False)
            future_detail_info_dic[aim].to_excel(writer, aim + '_details', index=True)
        writer.save()

# sdate, edate, _ = check_update_date()
# id = IndexDividends(sdate)
# id.run()
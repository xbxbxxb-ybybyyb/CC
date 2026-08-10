# =  -*- coding: utf-8 -*-
"""
Created on 20200107
@author: 015626
"""
# from WindPy import *
import datetime
import random
import pandas as pd
import os
import glob
from multifactor.data.utils import *
from multifactor.utility.dt import *
from multifactor.IO import IO
from xquant.factordata import FactorData
s = FactorData()

import warnings

warnings.filterwarnings('ignore')

random.seed(123)
# w.start()

def update_holders_meeting_date():
    rootpath = '/data/user/015626/data/share/IndexDividends/holders_meeting_date/'
    csvpath = '/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/WIND_AShareholdersmeeting/'

    updatedate = str(datetime.datetime.now().date()).replace('-','')
    csvlist = glob.glob(csvpath + updatedate[:4] + '*.csv')
#     print(csvlist)

    df = pd.DataFrame()
    for csv in csvlist:
        csvdf = pd.read_csv(csv)
        df = df.append(csvdf)

    df = df[(df.MEETING_TYPE == '股东大会') & (df.IS_NEW == 1)]
    df = df.rename(columns={'ANN_DT': 'dt', 'S_INFO_WINDCODE': 'Ticker'})
    df = df.sort_values('MEETING_DT').drop_duplicates(subset='Ticker', keep='last')
    df = df[['dt','Ticker','MEETING_DT']]
    df.to_csv(os.path.join(rootpath, updatedate + '.csv'), index = False)

def ticker_match(ticker_num): # jit slow
    ticker_num = int(ticker_num)
    suffix = '.SH' if ticker_num>=600000 else '.SZ'
    pre_fill = (6 - len(str(ticker_num)))*'0'
    ticker = pre_fill + str(ticker_num) + suffix
    return ticker

class IndexDividends(object):

    def __init__(self, date, futures=['HS300', 'ZZ500', 'SH50', 'ZZ1000'], lookback=5,
                 writepath='/data/user/015626/data/share/IndexDividends/'):

        self.date = str(date)
        self.futures = futures
        self.writepath = writepath
        nowtime = dt.datetime.strptime(self.date, '%Y%m%d')

        tradingDates = get_trading_date_range((nowtime - dt.timedelta(30)).strftime('%Y%m%d'),
                                              (nowtime + dt.timedelta(30)).strftime('%Y%m%d'))
        tradingDates = [d.strftime('%Y%m%d') for d in tradingDates]

        self.tradingdays_in_fore30 = tradingDates[: tradingDates.index(self.date) + 1]
        self.now_trading_date = tradingDates[tradingDates.index(self.date) + 1]
        self.year = int(self.date[: 4])
        self.weeklater = tradingDates[tradingDates.index(self.date) + 5]
        self.lookback = lookback
#         self.risk_free_rate = w.edb("M1000166", self.date, self.date, "Fill = Previous").Data[0][0] / 100
#        self.risk_free_rate = s.get_factor_value('WIND_CGBbenchmark',factors=['S_DQ_CLOSE'],TRADE_DT=self.date, S_INFO_WINDCODE='TB10Y.WI').iloc[0]['S_DQ_CLOSE']
        self.risk_free_rate = s.get_factor_value('WIND_CGBbenchmark',factors=['S_DQ_CLOSE','TRADE_DT'], S_INFO_WINDCODE='TB10Y.WI').sort_values(by = 'TRADE_DT').iloc[-1]['S_DQ_CLOSE']

        sdate, _, _ = check_update_date(None, None)
        self.last_trading_date = str(sdate)


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
        elif aim == 'ZZ1000':
            future_code = 'IM.CFE'
            tmp = '000852.SH'
        data = pd.read_csv('/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/stock_universe/%s/%s.csv' % (aim, self.last_trading_date))
        tickers = list(data['Ticker'])
        weights = list(data[aim] / 100)
#         idx_close = w.wsd(tmp, "close", self.date, self.date, "").Data[0][0]
        try:
            index_data = IO.read_data(self.date, columns = ['S_DQ_CLOSE'],  alt = '/data/group/800080/warehouse/prod/DATABASE/WIND/AIndexEODPrices/AIndexEODPrices.h5')
            idx_close = index_data.loc[(self.date,tmp)]['S_DQ_CLOSE']
        except:
            index_data = IO.read_data(columns = ['S_DQ_CLOSE'],  alt = '/data/group/800080/warehouse/prod/DATABASE/WIND/AIndexEODPrices/AIndexEODPrices.h5')
            idx_close = index_data.xs(tmp, level = 1).iloc[-1]['S_DQ_CLOSE']
        return tickers, weights, future_code, idx_close

    # 预测除权除息日
    # 思路：股东大会公告日距离分红日期之间的天数往往变化不大，取前三年间隔均值与今年股东大会公告日加起来预测为今年分红日期
    # 如今年股东大会召开日没公布，则使用过去三年分红日期的中值进行估算
    # 股东大会公告日在股东大会召开日后一天
    def Predict_Div_Exdate(self, tickers):
        tmp = []
        # 获取上年及上上年,上上上年除权除息日
#         year1 = w.wss(tickers, "div_exdate, div_smtgdate", "rptDate=%s1231" % (str(self.year - 2)))
#         year1df = pd.DataFrame(data=year1.Data, columns=year1.Codes, index=year1.Fields).T
        year1df = s.get_factor_value('WIND_AShareDividend',factors=['S_INFO_WINDCODE','EX_DT','S_DIV_SMTGDATE'], REPORT_PERIOD='%s1231'% (str(self.year - 2)), S_INFO_WINDCODE=tickers)
        year1df = year1df.drop_duplicates(subset='S_INFO_WINDCODE', keep = 'first')
        year1df = year1df.rename(columns = {'EX_DT':'DIV_EXDATE','S_DIV_SMTGDATE':'DIV_SMTGDATE'}).set_index('S_INFO_WINDCODE').loc[tickers].fillna(pd.to_datetime('19010101').date())
        year1df['DIV_EXDATE'] = pd.to_datetime(year1df['DIV_EXDATE'])
        year1df['DIV_SMTGDATE'] = pd.to_datetime(year1df['DIV_SMTGDATE'])
        year1df['timedelta'] = year1df.DIV_EXDATE - year1df.DIV_SMTGDATE
        year1df['timedelta'] = year1df.timedelta.apply(lambda x: x.days)
        year1df.to_csv('/data/user/015626/data/share/IndexDividends/holders_meeting_date/year1_new.csv')

#         year2 = w.wss(tickers, "div_exdate, div_smtgdate", "rptDate=%s1231" % (str(self.year - 3)))
#         year2df = pd.DataFrame(data=year2.Data, columns=year2.Codes, index=year2.Fields).T
        year2df = s.get_factor_value('WIND_AShareDividend',factors=['S_INFO_WINDCODE','EX_DT','S_DIV_SMTGDATE'], REPORT_PERIOD='%s1231'% (str(self.year - 3)), S_INFO_WINDCODE=tickers)
        year2df = year2df.drop_duplicates(subset='S_INFO_WINDCODE', keep = 'first')
        year2df = year2df.rename(columns = {'EX_DT':'DIV_EXDATE','S_DIV_SMTGDATE':'DIV_SMTGDATE'}).set_index('S_INFO_WINDCODE').loc[tickers].fillna(pd.to_datetime('19010101').date())
        year2df['DIV_EXDATE'] = pd.to_datetime(year2df['DIV_EXDATE'])
        year2df['DIV_SMTGDATE'] = pd.to_datetime(year2df['DIV_SMTGDATE'])
        year2df['timedelta'] = year2df.DIV_EXDATE - year2df.DIV_SMTGDATE
        year2df['timedelta'] = year2df.timedelta.apply(lambda x: x.days)
        year2df.to_csv('/data/user/015626/data/share/IndexDividends/holders_meeting_date/year2_new.csv')

#         year3 = w.wss(tickers, "div_exdate, div_smtgdate", "rptDate=%s1231" % (str(self.year - 4)))
#         year3df = pd.DataFrame(data=year3.Data, columns=year3.Codes, index=year3.Fields).T
        year3df = s.get_factor_value('WIND_AShareDividend',factors=['S_INFO_WINDCODE','EX_DT','S_DIV_SMTGDATE'], REPORT_PERIOD='%s1231'% (str(self.year - 4)), S_INFO_WINDCODE=tickers)
        year3df = year3df.drop_duplicates(subset='S_INFO_WINDCODE', keep = 'first')
        year3df = year3df.rename(columns = {'EX_DT':'DIV_EXDATE','S_DIV_SMTGDATE':'DIV_SMTGDATE'}).set_index('S_INFO_WINDCODE').loc[tickers].fillna(pd.to_datetime('19010101').date())
        year3df['DIV_EXDATE'] = pd.to_datetime(year3df['DIV_EXDATE'])
        year3df['DIV_SMTGDATE'] = pd.to_datetime(year3df['DIV_SMTGDATE'])
        year3df['timedelta'] = year3df.DIV_EXDATE - year3df.DIV_SMTGDATE
        year3df['timedelta'] = year3df.timedelta.apply(lambda x: x.days)
        year3df.to_csv('/data/user/015626/data/share/IndexDividends/holders_meeting_date/year3_new.csv')

        year1_delta = year1df.timedelta.tolist()
        year1_smtg = year1df.DIV_SMTGDATE.tolist()
        year1 = year1df.DIV_EXDATE.tolist()

        year2_delta = year2df.timedelta.tolist()
        year2_smtg = year2df.DIV_SMTGDATE.tolist()
        year2 = year2df.DIV_EXDATE.tolist()

        year3_delta = year3df.timedelta.tolist()
        year3_smtg = year3df.DIV_SMTGDATE.tolist()
        year3 = year3df.DIV_EXDATE.tolist()

        # 判断时间是否符合规范，清洗数据
        for i in range(len(tickers)):

            year1[i] = np.nan if year1[i].year < self.year - 1 else year1[i].strftime('%Y%m%d')
            year1_smtg[i] = np.nan if year1_smtg[i].year < self.year - 1 else year1_smtg[i].strftime('%Y%m%d')

            year2[i] = np.nan if year2[i].year < self.year - 2 else year2[i].strftime('%Y%m%d')
            year2_smtg[i] = np.nan if year2_smtg[i].year < self.year - 2 else year2_smtg[i].strftime('%Y%m%d')

            year3[i] = np.nan if year3[i].year < self.year - 3 else year3[i].strftime('%Y%m%d')
            year3_smtg[i] = np.nan if year3_smtg[i].year < self.year - 3 else year3_smtg[i].strftime('%Y%m%d')

            if year1_delta[i] < 0:
                year1_delta[i] = np.nan
            if year2_delta[i] < 0:
                year2_delta[i] = np.nan
            if year3_delta[i] < 0:
                year3_delta[i] = np.nan

            if (year1[i] != year1[i]) or (year1_smtg[i] != year1_smtg[i]):
                year1_delta[i] = np.nan
            if (year2[i] != year2[i]) or (year2_smtg[i] != year2_smtg[i]):
                year2_delta[i] = np.nan
            if (year3[i] != year3[i]) or (year3_smtg[i] != year3_smtg[i]):
                year3_delta[i] = np.nan

        last3yearsdf = pd.DataFrame({'div_date_year1': year1, 'smtg_Date_year1': year1_smtg, 'year1_delta': year1_delta,
                                     'div_date_year2': year2, 'smtg_Date_year2': year2_smtg, 'year2_delta': year2_delta,
                                     'div_date_year3': year3, 'smtg_Date_year3': year3_smtg,
                                     'year3_delta': year3_delta},
                                    index=tickers)
        last3yearsdf.to_csv('/data/user/015626/data/share/IndexDividends/holders_meeting_date/last3yearsdf_new.csv')

        # 取前三年分红日距离股东大会公告日均值
        div_date_delta_dict = {tickers[i]: np.nanmean([year1_delta[i], year2_delta[i], year3_delta[i]]) for i in
                               range(len(tickers))}
        pd.DataFrame(div_date_delta_dict, index=['num']).T.to_csv('/data/user/015626/data/share/IndexDividends/holders_meeting_date/div_date_delta_dict_new.csv')

        # 先取前三年日期中值，之后会根据股东大会召开日进行覆盖
        def get_mid_date(date1, date2, date3=0):
            dd1 = datetime.datetime(self.year, date1 // 100, date1 % 100)
            dd2 = datetime.datetime(self.year, date2 // 100, date2 % 100)

            startdate = datetime.datetime(self.year, 1, 1)
            dsum = datetime.timedelta(0)
            if date3 > 0:
                dd3 = datetime.datetime(self.year, date3 // 100, date3 % 100)
                for x in [dd1, dd2, dd3]:
                    dsum += x - startdate
                return int((startdate + dsum / 3).strftime('%Y%m%d')[4:])
            else:
                for x in [dd1, dd2]:
                    dsum += x - startdate
                return int((startdate + dsum / 2).strftime('%Y%m%d')[4:])

        dw = int(self.weeklater[4:])
        # 比较日期中值与一周后，如果前三年都没有分红，则比较一周后与7月1日，都以远的日期作为估计值
        for i in range(len(tickers)):
            d1 = 0 if type(year1[i]) == type(np.nan) else int(year1[i][4:])
            d2 = 0 if type(year2[i]) == type(np.nan) else int(year2[i][4:])
            d3 = 0 if type(year3[i]) == type(np.nan) else int(year3[i][4:])
            if d1 == 0:
                if d2 == 0:
                    if d3 == 0:
                        mx = max(701, dw)
                    elif d3 != 0:
                        mx = max(d3, dw)
                elif d2 != 0:
                    if d3 == 0:
                        mx = max(d2, dw)
                    elif d3 != 0:
                        mx = max(get_mid_date(d2, d3), dw)
            else:
                if d2 == 0:
                    if d3 == 0:
                        mx = max(d1, dw)
                    elif d3 != 0:
                        mx = max(get_mid_date(d1, d3), dw)
                elif d2 != 0:
                    if d3 == 0:
                        mx = max(get_mid_date(d1, d2), dw)
                    else:
                        mx = max(get_mid_date(d1, d2, d3), dw)

            tmp.append(str(self.year) + '0' + str(mx) if len(str(mx)) < 4 else str(self.year) + str(mx))

        dic = {tickers[x]: tmp[x] for x in range(len(tickers))}

        # d0 = int(self.date[4:])
        # 获取股东大会召开时间
        try:
            meetingdate_df = pd.read_csv(os.path.join(self.writepath, 'holders_meeting_date', self.now_trading_date + '.csv'))[['Ticker', 'MEETING_DT']]
            meetingdate_df = meetingdate_df[meetingdate_df.MEETING_DT > (self.year * 10000)]
            meetingdate_dict = meetingdate_df.set_index('Ticker').to_dict()['MEETING_DT']
        except:
            meetingdate_dict = {}

        # 存储最终的预测结果
        predict_div_exdate = {}
        for key in tickers:
            # 如果前三年无分红，则估计分红日距离股东大会公告日15天
            if div_date_delta_dict[key] != div_date_delta_dict[key]:
                div_date_delta_dict[key] = 15
            # 如果目前已经公布股东大会日期
            if key in meetingdate_dict.keys():
                meeting_date = datetime.datetime.strptime(str(int(meetingdate_dict[key])), '%Y%m%d')
                # +1是因为股东大会公告日在股东大会召开日后一天
                preddate = (meeting_date + datetime.timedelta(int(div_date_delta_dict[key]) + 1)).strftime('%Y%m%d')

            # 如果目前没有公布股东大会日期，则将股东大会日期预设为一个月后加上间隔得出一个预测结果，并与中值预测的结果进行比较
            # 取晚的那个，此举是为了防止年初时都没有公布股东大会日期
            else:
                meeting_date = datetime.datetime.strptime(self.now_trading_date, '%Y%m%d') + datetime.timedelta(30)
                preddate = (meeting_date + datetime.timedelta(int(div_date_delta_dict[key]) + 1)).strftime('%Y%m%d')

                median_preddate = dic[key]
                if int(median_preddate[4:]) > int(preddate[4:]):
                    preddate = median_preddate

            dp = int(preddate[4:])
            # 如果根据股东大会预测的日期在今天之前，则预测今天之后5天为分红日
            d0 = int(str(self.now_trading_date)[-4:])
            if dp > d0:
                predict_div_exdate[key] = preddate
            else:
                predict_div_exdate[key] = self.weeklater

        return predict_div_exdate

    def Div_Info(self, predict_div_exdate):
        # 分红实施
    #         data = w.wset("bonus", "orderby=报告期;year=%s;period=y1;sectorid=a001010100000000" % (str(self.year - 1)))
    #         df = pd.DataFrame(data.Data).T
    #         df.columns = data.Fields
        _df = s.get_factor_value('WIND_AShareDividend',factors=['S_INFO_WINDCODE','CASH_DVD_PER_SH_PRE_TAX','EX_DT','S_DIV_OBJECT','S_DIV_PROGRESS'], REPORT_PERIOD='%s1231'% (str(self.year - 1)))
        if len(_df) == 0:
            res1 = pd.DataFrame(
                columns=['dividendsper_share_pretax', 'exrights_exdividend_date', 'wind_code', 'date_is_true_data', 'dividends_is_true_data'])
        else:
            df = _df.rename(columns = {'S_INFO_WINDCODE':'wind_code','CASH_DVD_PER_SH_PRE_TAX':'dividendsper_share_pretax','EX_DT':'exrights_exdividend_date','S_DIV_OBJECT':'dividend_object'}).copy()
            df = df[(df['dividendsper_share_pretax'] > 0) & (df['dividend_object'] == '普通股股东')]
            df = df.dropna(subset=['exrights_exdividend_date'])
            df['exrights_exdividend_date'] = pd.to_datetime(df['exrights_exdividend_date'])
            a = list(df['exrights_exdividend_date'])
            a = [x.strftime('%Y%m%d') for x in a]
            res1 = pd.DataFrame(
                {'dividendsper_share_pretax': df['dividendsper_share_pretax'], 'exrights_exdividend_date': a})
            res1['wind_code'] = df['wind_code']
            res1['date_is_true_data'] = 'true'
            res1['dividends_is_true_data'] = 'true'

    #     data = w.wset("dividendproposal",
    #                   "ordertype=1;startdate=%s-01-01;enddate=%s;sectorid=a001010100000000" % (
    #                   str(self.year), self.date))
    #     df = pd.DataFrame(data.Data).T
    #     df.columns = data.Fields
        if len(_df) == 0:
            res2 = pd.DataFrame(columns=['dividendsper_share_pretax', 'exrights_exdividend_date', 'wind_code'])
        else:
            df = _df[((_df['S_DIV_PROGRESS'] == '1') | (_df['S_DIV_PROGRESS'] == '2')) & (_df['CASH_DVD_PER_SH_PRE_TAX']>0)]
            df = df.rename(columns = {'S_INFO_WINDCODE':'wind_code','CASH_DVD_PER_SH_PRE_TAX':'dividendsper_share_pretax'})
            tmp = []
            for code in list(df['wind_code']):
                if code in predict_div_exdate.keys():
                    tmp.append(predict_div_exdate[code])
                else:
                    tmp.append(np.nan)
            res2 = pd.DataFrame({'dividendsper_share_pretax': df['dividendsper_share_pretax'], 'exrights_exdividend_date': tmp})
            res2['wind_code'] = list(df['wind_code'])
            res2['dividends_is_true_data'] = 'true'

        div_info = res1.append(res2).drop_duplicates(subset='wind_code', keep='first').set_index('wind_code', drop=True)
        return div_info

        # 获取股票对应的总股数，单位为（股）

    def Total_Shares_Info(self, tickers):
#         data = w.wss(tickers, "total_shares", "unit=1;tradeDate=%s" % self.date).Data[0]
#         dic = {tickers[x]: int(data[x]) for x in range(len(tickers))}
        adf = s.get_factor_value('WIND_AShareCapitalization',factors=['S_INFO_WINDCODE','TOT_SHR','CHANGE_DT'], S_INFO_WINDCODE=tickers)
        adf = adf.sort_values(by = 'CHANGE_DT', ascending=True)
        dic = (adf.groupby(['S_INFO_WINDCODE'])['TOT_SHR'].last()*10000).astype('int').to_dict()
        return dic

        # 获取公司的净利润

    def Predict_Net_Profit(self):
        # 一致预期归母净利润
#         path = '/data/group/800002/basic_data/full/financial_data/LOCAL_DATA/CSV/gogoal_htsc/con_forecast_stk/%s.csv' % (self.last_trading_date)
#         data = pd.read_csv(path, header=0)
#         data = data[(data['RPT_DATE'] == self.year - 1) & (data['RPT_TYPE'] == 4)]
#         a = list(data['Ticker'])
#         b = list(data['C4'] * 10000)
#         dic = {a[x]: b[x] for x in range(len(data))}
        
        data = s.get_factor_value('GOGOAL_con_forecast_stk',factors = ['TDATE','STOCK_CODE','RPT_DATE','C4'], tdate=[self.last_trading_date],RPT_DATE=[str(self.year - 1)],RPT_TYPE=['4'])
        data['STOCK_CODE'] = data.STOCK_CODE.apply(lambda x:ticker_match(x))
        data['C4'] = data['C4'] * 10000
        dic = data.set_index('STOCK_CODE')['C4'].to_dict()
        return dic

    # 年度现金分红比例
    def Predict_Dividend_Payoutratio(self, tickers):
        
        clist = []
        dlist = []
        for i in range(3):
            # 找到上一年的最后一个交易日，此时上上年的年报归母净利润是准确的 20220428这一天要看2020,2019,2018年的年报
            last_tday_lastyear = get_trading_day_offset((self.year - i) * 10000 + 101,0)[0].strftime('%Y%m%d')
            dlist.append(str((self.year - i - 2) * 10000 + 1231))
            clist.append(s.get_factor_value('GOGOAL_con_forecast_stk',factors = ['TDATE','STOCK_CODE','RPT_DATE','C4'], tdate=[last_tday_lastyear],RPT_DATE=[str(self.year - i - 2)],RPT_TYPE=['4']))

        con_forecast_stk = pd.concat(clist, axis = 0)
        con_forecast_stk = con_forecast_stk.rename(columns = {'TDATE':'dt','STOCK_CODE':'Ticker','C4':'net_profit_belongs_to_its_mother','RPT_DATE':'REPORT_PERIOD'})
        con_forecast_stk['net_profit_belongs_to_its_mother'] = con_forecast_stk['net_profit_belongs_to_its_mother'] * 10000
        con_forecast_stk['REPORT_PERIOD'] = (con_forecast_stk['REPORT_PERIOD'] * 10000 + 1231).astype('str')
        con_forecast_stk['Ticker'] = con_forecast_stk.Ticker.apply(lambda x:ticker_match(x))

        con_forecast_stk = con_forecast_stk[con_forecast_stk.Ticker.isin(tickers)]
        con_forecast_stk = con_forecast_stk.set_index(['Ticker','REPORT_PERIOD'])

        asd = s.get_factor_value('WIND_AShareDividend',factors=['S_INFO_WINDCODE','CASH_DVD_PER_SH_PRE_TAX','S_DIV_BASESHARE','REPORT_PERIOD'], S_INFO_WINDCODE = tickers, REPORT_PERIOD=dlist)
        asd = asd.rename(columns = {'S_INFO_WINDCODE':'Ticker'}).set_index(['Ticker','REPORT_PERIOD'])
        asd['TOT_CASH_DVD'] = asd['CASH_DVD_PER_SH_PRE_TAX'] * asd['S_DIV_BASESHARE'] * 10000

        divdf = con_forecast_stk.join(asd, how = 'outer')
        divdf['cash_div_ratio'] = divdf['TOT_CASH_DVD'] / divdf['net_profit_belongs_to_its_mother']
        divdf = divdf.loc[~divdf.index.duplicated()]
        divdf = divdf.sort_index()['cash_div_ratio'].unstack()

        return divdf.mean(axis = 1).to_dict()
#         dp1 = w.wss(tickers, "div_payoutratio", "year=%s" % (str(self.year - 2))).Data[0]
#         dp2 = w.wss(tickers, "div_payoutratio", "year=%s" % (str(self.year - 3))).Data[0]
#         dp3 = w.wss(tickers, "div_payoutratio", "year=%s" % (str(self.year - 4))).Data[0]
#         # 如果超额分红，则不计入
#         for i in range(len(tickers)):
#             if dp1[i] > 100:
#                 dp1[i] = np.nan
#             if dp2[i] > 100:
#                 dp2[i] = np.nan
#             if dp3[i] > 100:
#                 dp3[i] = np.nan
#         return {tickers[i]: np.nanmean([dp1[i], dp2[i], dp3[i]]) / 100 for i in range(len(tickers))}

    def Combine_Info(self, weights, predict_div_exdate, idx_close, tickers, div_info, predict_net_profit,
                     predict_dividend_payoutratio, total_shares_info):
        res = pd.DataFrame()
        for i in range(len(tickers)):
            ticker = tickers[i]
            # 已经获取到准确的分红信息
            if ticker in list(div_info.index):
                res = res.append(div_info.loc[ticker, :])
            else:
                # 如果净利润为负，或者已经过了4月30年报发布日则认为不分红
                if (predict_net_profit[ticker] < 0) | (int(self.date) > int(self.date[: 4] + '0430')) | (ticker in ['689009.SH']):
                    res = res.append(pd.DataFrame([[0, np.nan]], index=[ticker],
                                                  columns=['dividendsper_share_pretax', 'exrights_exdividend_date']))
                else:
                    # 每股税前分红 = 预测归母净利润 * 分红比例 / 总股本
                    tmp = predict_net_profit[ticker] * predict_dividend_payoutratio[ticker] / total_shares_info[ticker]
                    res = res.append(pd.DataFrame([[tmp, predict_div_exdate[ticker]]], index=[ticker],
                                                  columns=['dividendsper_share_pretax', 'exrights_exdividend_date']))

#         res['close'] = w.wsd(tickers, "close", self.date, self.date, "").Data[0]
        try:
            stk_data = IO.read_data(self.date, columns = ['close'], alt = '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
            stk_data = stk_data.reset_index(level = 0, drop = True)
            res['close'] = stk_data.loc[tickers]['close'].tolist()
        except:
            stk_data = IO.dipping(10000,columns = ['close'], alt = '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
            stk_data = stk_data.loc[stk_data.index.get_level_values(0)[-1]]
            res['close'] = stk_data.loc[tickers]['close'].tolist()
        res['weights'] = weights
        res['point'] = res['dividendsper_share_pretax'] / res['close'] * res['weights'] * idx_close
        if 'date_is_true_data' not in res.columns.tolist():
            res['date_is_true_data'] = np.nan
        if 'dividends_is_true_data' not in res.columns.tolist():
            res['dividends_is_true_data'] = np.nan
        df = res[['point', 'exrights_exdividend_date', 'date_is_true_data', 'dividendsper_share_pretax',
                  'dividends_is_true_data']]
        df = df.sort_values(by='exrights_exdividend_date').dropna(
            subset=['point', 'exrights_exdividend_date', 'dividendsper_share_pretax'])
        return df

    def Futures_Info(self, future_code, combine_info):
        if future_code[: 2] == 'IF':
            index = '000300.SH'
        elif future_code[: 2] == 'IC':
            index = '000905.SH'
        elif future_code[: 2] == 'IH':
            index = '000016.SH'
        elif future_code[: 2] == 'IM':
            index = '000852.SH'
#         # 获取期货合约列表
#         data = w.wset("futurecc", "startdate=%s-01-01;enddate=%s-12-31;wind_code=%s" % (
#             str(self.year), str(self.year), future_code))
#         df = pd.DataFrame(data.Data).T
#         df.columns = data.Fields
#         a = df['last_trade_date']
#         a = [int(x.strftime('%Y%m%d')) for x in a]
#         res = df[['wind_code']]
#         res['last_trade_date'] = a
#         res = res[res['last_trade_date'] >= int(self.now_trading_date)]
        
        res = s.get_factor_value('WIND_CFuturesDescription',factors=['S_INFO_WINDCODE','S_INFO_DELISTDATE'], FS_INFO_SCCODE=[future_code[:2]],S_INFO_DELISTDATE=['>=%s' % self.now_trading_date])
        res = res.rename(columns = {'S_INFO_WINDCODE':'wind_code','S_INFO_DELISTDATE':'last_trade_date'})
        res['last_trade_date'] = res['last_trade_date'].astype('int')
        res = res.sort_values(by = 'last_trade_date')

        tmp = []
        last_trade_date = list(res['last_trade_date'])
        last_trade_date.sort()
        combine_info['exrights_exdividend_date'] = combine_info['exrights_exdividend_date'].astype(int)
        for i in range(len(last_trade_date)):
            sdate = self.now_trading_date
            edate = last_trade_date[i]
            tmp_df = combine_info[combine_info['exrights_exdividend_date'] >= int(sdate)]
            tmp_df = tmp_df[tmp_df['exrights_exdividend_date'] <= edate]
            tmp.append(sum(tmp_df['point']))
        res['point'] = tmp
#         res['future_close'] = w.wsd(list(res['wind_code']), "close", self.date, self.date, "").Data[0]
        try:
            _close = s.get_factor_value('WIND_CIndexFuturesEODPrices',factors=['S_INFO_WINDCODE','S_DQ_CLOSE'], S_INFO_WINDCODE=res.wind_code.tolist(),TRADE_DT=[self.date])
            res['future_close'] = _close.set_index('S_INFO_WINDCODE').loc[res.wind_code.tolist()]['S_DQ_CLOSE'].tolist()
            index_data = IO.read_data(self.date, columns = ['S_DQ_CLOSE'],  alt = '/data/group/800080/warehouse/prod/DATABASE/WIND/AIndexEODPrices/AIndexEODPrices.h5')
            idx_close = index_data.loc[(self.date,index)]['S_DQ_CLOSE']
        except:
            _close = s.get_factor_value('WIND_CIndexFuturesEODPrices',factors=['S_INFO_WINDCODE','S_DQ_CLOSE'], S_INFO_WINDCODE=res.wind_code.tolist(),TRADE_DT=[self.last_trading_date])
            res['future_close'] = _close.set_index('S_INFO_WINDCODE').loc[res.wind_code.tolist()]['S_DQ_CLOSE'].tolist()
            index_data = IO.read_data(self.last_trading_date, columns = ['S_DQ_CLOSE'], alt = '/data/group/800080/warehouse/prod/DATABASE/WIND/AIndexEODPrices/AIndexEODPrices.h5')
            idx_close = index_data.loc[(self.last_trading_date,index)]['S_DQ_CLOSE']
#         res['idx_close'] = w.wsd(index, "close", self.date, self.date, "").Data[0][0]
        
        res['idx_close'] = idx_close
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
            elif code[: 2] == 'IM':
                index = '000852.SH'
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
#             ddd = w.wsd(code, "oi", self.tradingdays_in_fore30[0], self.tradingdays_in_fore30[-1], "").Data[0]
            try:
                _oi = s.get_factor_value('WIND_CIndexFuturesEODPrices',factors=['S_INFO_WINDCODE','S_DQ_OI','TRADE_DT'], S_INFO_WINDCODE=code,TRADE_DT=['>=%s'%self.tradingdays_in_fore30[0],'<=%s'%self.tradingdays_in_fore30[-1]])
                _oi = _oi.sort_values(by='TRADE_DT')
                ddd = _oi['S_DQ_OI'].to_list()
            
                res = np.nansum(ddd[-1 * self.lookback:])
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
            elif code[: 2] == 'IM':
                index = '000852.SH'
#             index_close = w.wsd(index, "close", self.date, self.date, "").Data[0][-1]
            try:
                index_data = IO.read_data(self.date, columns = ['S_DQ_CLOSE'],  alt = '/data/group/800080/warehouse/prod/DATABASE/WIND/AIndexEODPrices/AIndexEODPrices.h5')
                idx_close = index_data.loc[(self.date,index)]['S_DQ_CLOSE']
            except:
                index_data = IO.read_data(columns = ['S_DQ_CLOSE'], alt = '/data/group/800080/warehouse/prod/DATABASE/WIND/AIndexEODPrices/AIndexEODPrices.h5')
                idx_close = index_data.xs(index, level = 1).iloc[-1]['S_DQ_CLOSE']
            tmp = self.risk_free_rate * exp_dic[code] / 365
            res0 = idx_close * tmp
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
            combine_info = self.Combine_Info(weights, predict_div_exdate, idx_close, tickers, div_info,
                                             predict_net_profit, predict_dividend_payoutratio,
                                             total_shares_info)
            future_detail_info_dic[aim] = combine_info
            # 获取分红对每个指数点位影响的信息
            futures_info = self.Futures_Info(future_code, combine_info)
            futures_info_dic[aim] = futures_info

        for aim in self.futures:
            exp_dic, point_acc_dic, codes = self.Fetch_Info(futures_info_dic, aim)
#             mean, sigma = self.FetchHistoricalInfo_TL(codes, aim)
            res = futures_info_dic[aim].copy()
            res.columns = ['证券代码', '交割日', '分红点数', '合约收盘价', '指数收盘价', '实际基差', '含分红基差']
            res['无风险利率成本'] = self.FetchRiskFreeCosts(codes, exp_dic)
#             res['5日基差均值'] = mean
#             res['5日基差波动率'] = sigma
            res['5日持仓量总和'] = self.CheckOI(codes)
            with pd.option_context('display.max_columns', 15):
                print(res)
            res.to_excel(writer, aim, index=False)
            future_detail_info_dic[aim].to_excel(writer, aim + '_details', index=True)
        writer.save()
        
update_holders_meeting_date()
sdate, edate, _ = check_update_date()
ids = IndexDividends(sdate)
ids.run()

# 以下是计算第二年的分红，如果四个合约中出现了次年的合约

now_trading_date = int(ids.now_trading_date)
now_year = now_trading_date // 10000
next_year = now_year + 1

# 获取目前合约，如果有次年合约，则计算次年合约的分红
# data = w.wset("futurecc", "startdate=%s;enddate=%s;wind_code=%s" % (str(now_trading_date),str(now_trading_date),'IF.CFE'))
# df = pd.DataFrame(data.Data).T
# df.columns = data.Fields
df = s.get_factor_value('WIND_CFuturesDescription',factors=['S_INFO_WINDCODE','S_INFO_DELISTDATE'], FS_INFO_SCCODE=['IF'],S_INFO_DELISTDATE=['>=%s' % str(now_trading_date)])
df = df.rename(columns = {'S_INFO_WINDCODE':'wind_code','S_INFO_DELISTDATE':'last_trade_date'})
df = df.sort_values(by = 'wind_code')
if int(df['wind_code'].tolist()[-1][2:4]) > int(str(sdate)[2:4]):
    fdate_list_dt = IO.read_data([next_year * 10000 + 101, next_year * 10000 + 110], ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i, '%Y%m%d')) for i in fdate_list_dt]
    adate = fdate_list[-1]
    ids = IndexDividends(adate)
    ids.run()

    target_excel_date = int(ids.now_trading_date)

    print(now_trading_date, target_excel_date)
    writepath = ids.writepath

    writer = pd.ExcelWriter(os.path.join(writepath, 'IndexDividends_%s.xlsx') % str(now_trading_date))
    # aim = 'HS300'
    for aim in ['HS300', 'ZZ500', 'SH50', 'ZZ1000']:
        d1 = pd.read_excel(writepath + 'IndexDividends_' + str(now_trading_date) + '.xlsx', sheet_name=aim,
                           index_col='证券代码')
        d2 = pd.read_excel(writepath + 'IndexDividends_' + str(target_excel_date) + '.xlsx', sheet_name=aim,
                           index_col='证券代码')

        d1_details = pd.read_excel(writepath + 'IndexDividends_' + str(now_trading_date) + '.xlsx',
                                   sheet_name=aim + '_details', index_col=0)
        d2_details = pd.read_excel(writepath + 'IndexDividends_' + str(target_excel_date) + '.xlsx',
                                   sheet_name=aim + '_details', index_col=0)

        contract_list = d1.index.tolist()
        count = 0
        for contract in contract_list:
            if int(contract[2:4]) > (now_year % 100):
                count += 1
        assert count > 0
        for contract in contract_list:
            if int(contract[2:4]) > (now_year % 100):
                d1.loc[contract, '分红点数'] = d2.loc[contract, '分红点数'] + d1.iloc[4 - count - 1]['分红点数']
        print(d1)
        d1.to_excel(writer, aim, index=True)
        d1_details.to_excel(writer, aim + '_details', index=True)
        d2_details.to_excel(writer, aim + '_details_' + str(next_year), index=True)

    writer.save()
    os.remove(writepath + 'IndexDividends_' + str(target_excel_date) + '.xlsx')

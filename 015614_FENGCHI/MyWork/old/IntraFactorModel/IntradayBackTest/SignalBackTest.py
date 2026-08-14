# @Time : 2020/6/4 15:32
# @Author : Zhichen Lu
# @File : SignalBackTest.py


import time
import traceback
from abc import abstractmethod
from collections import OrderedDict
from multiprocessing import Pool

import numpy as np
import pandas as pd

from dataApi.getData import get_daily_1factor, get_date_range, get_pre_trade_date, trans_windcode2int
from dataApi.tradeDate import trade_months


class SignalBackTestBase:

    def __init__(self, start_date=20170103, end_date=20181231):
        self.start_date = start_date
        self.end_date = end_date

    def load_data(self, year_month, factor):
        data = pd.read_pickle('/data/group/800080/PanelMinDataForZT/stock/%s/%s_%s.pkl' % (factor, year_month, factor))
        return data

    def reformate_id(self, df):
        if isinstance(df.index[0], tuple):
            df.index = [x[0] * 10000 + x[1] for x in df.index]
        df.index = pd.to_datetime(df.index.astype(str))
        df.columns = [str(stk).zfill(6) + '.SZ' if int(stk) < 400000 else str(stk) + '.SH' for stk in df.columns]

    def backtest(self, signal, target, verbose=False, kernal_num=10):
        month = None
        data = None
        result = {}
        para_dict = {}
        record_dict = OrderedDict()

        self.start_date = pd.to_datetime(str(self.start_date) + '092500')
        self.end_date = pd.to_datetime(str(self.end_date) + '150000')
        if self.start_date < signal.index[0]:
            self.start_date = signal.index[0]
        if self.end_date > signal.index[-1]:
            self.end_date = signal.index[-1]
        signal = signal.loc[self.start_date:self.end_date]

        target = target.loc[signal.index[0].strftime('%Y%m%d'):signal.index[-1].strftime('%Y%m%d')]
        avg_price, deal_vol = pd.DataFrame(index=target.index, columns=target.columns), pd.DataFrame(index=target.index,
                                                                                                     columns=target.columns)
        for day in target.index:
            # print(day)
            if day.strftime('%Y%m') != month:
                month = day.strftime('%Y%m')
                print(month)
                data = pd.Panel({x: self.load_data(month, x) for x in ['close', 'high', 'low', 'open', 'volume']})
                para_dict = {}
                result = {}
            temp_stk = target.loc[day].replace(0, np.nan).dropna()
            nan_list = []
            for stk in temp_stk.index:
                if stk not in signal.columns:
                    para_dict['_'.join([stk, day.strftime('%Y%m%d')])] = None
                    continue
                if stk not in data.minor_axis:
                    para_dict['_'.join([stk, day.strftime('%Y%m%d')])] = None
                    continue
                para_dict['_'.join([stk, day.strftime('%Y%m%d')])] = (
                    stk, day, temp_stk[stk], data.loc[:, day.strftime('%Y%m%d'), stk],
                    signal.loc[day.strftime('%Y%m%d'), stk])
                # self.calc_stk_day(*para_dict['_'.join([stk, day.strftime('%Y%m%d')])])
                # print('done')
                if signal.loc[day.strftime('%Y%m%d'), stk].count() < 200:
                    nan_list.append(stk)
            if verbose:
                print(day, len(nan_list))

            if int(day.strftime('%Y%m%d')) in trade_months or day == target.index[-1]:
                if len(para_dict) > 0:
                    e = time.time()
                    pool = Pool(kernal_num)
                    for para in para_dict:
                        if para_dict[para] is None:
                            result[para] = None
                            continue
                        result[para] = pool.apply_async(self.calc_stk_day, (*para_dict[para],))
                    pool.close()
                    pool.join()
                    temp_result = []
                    for para in result:
                        if result[para] is None:
                            vol, price, record = np.nan, np.nan, np.nan
                        else:
                            try:
                                vol, price, record = result[para].get()
                            except Exception as e:
                                vol, price, record = np.nan, np.nan, np.nan
                                # 这个是输出错误类别的，如果捕捉的是通用错误，其实这个看不出来什么
                                print('-------------', para, '------------------')
                                print('str(Exception):\t', str(Exception))  # 输出  str(Exception):	<type 'exceptions.Exception'>
                                # 这个是输出错误的具体原因，这步可以不用加str，输出
                                print('str(e):\t\t', str(e))  # 输出 str(e):		integer division or modulo by zero
                                print('repr(e):\t', repr(e))  # 输出 repr(e):	ZeroDivisionError('integer division or modulo by zero',)
                                print('traceback.print_exc():')
                                # 以下两步都是输出错误的具体位置的
                                traceback.print_exc()
                                print('traceback.format_exc():\n%s' % traceback.format_exc())

                        stk_id, date = para.split('_')
                        temp_result.append([stk_id, date, price, vol])
                        record_dict.update({(stk_id, date): record})
                    temp_result = pd.DataFrame(temp_result, columns=['stk_id', 'date', 'price', 'vol'])
                    temp_result['date'] = pd.to_datetime(temp_result['date'])
                    temp_price = temp_result.pivot_table(index='date', columns='stk_id', values='price')
                    temp_vol = temp_result.pivot_table(index='date', columns='stk_id', values='vol')
                    deal_vol.loc[temp_vol.index, temp_vol.columns] = temp_vol
                    avg_price.loc[temp_price.index, temp_price.columns] = temp_price
                    if verbose:
                        print(time.time() - e)
        return avg_price, deal_vol, record_dict

    def calc_performance(self, signal, target, avg_price=None, deal_vol=None):
        if avg_price is None or deal_vol is None:
            avg_price, deal_vol = self.backtest(signal, target)
        excuted_target = target.loc[deal_vol.index]
        start, end = excuted_target.index[0], excuted_target.index[-1]
        date_list = get_date_range(get_pre_trade_date(int(start.strftime('%Y%m%d'))), int(end.strftime('%Y%m%d')))
        daily_close = get_daily_1factor('close', date_list=date_list,
                                        code_list=[trans_windcode2int(code) for code in excuted_target.columns])
        daily_twap = get_daily_1factor('twap', date_list=date_list,
                                       code_list=[trans_windcode2int(code) for code in excuted_target.columns])
        self.reformate_id(daily_close)
        self.reformate_id(daily_twap)
        turnover_part = {'buy': excuted_target > 0, 'sell': excuted_target < 0, 'all': excuted_target != 0}

        fulfill_percent = {}
        for signal in turnover_part:
            target_cap = abs(excuted_target[turnover_part[signal]]) * daily_close.shift(1).loc[excuted_target.index][
                turnover_part[signal]]
            fulfill_cap = abs(deal_vol[turnover_part[signal]]) * daily_close.shift(1).loc[excuted_target.index][
                turnover_part[signal]]
            target_cap[fulfill_cap.isnull()] = np.nan
            fulfill_percent[signal] = fulfill_cap.sum(axis=1) / target_cap.sum(axis=1)
        fulfill_percent['stockly'] = deal_vol[turnover_part['all']] / excuted_target[turnover_part['all']]

        outperformance_by_stk = deal_vol * daily_twap.loc[deal_vol.index] - deal_vol * avg_price
        outperformance = {'buy': outperformance_by_stk[turnover_part['buy']],
                          'sell': outperformance_by_stk[turnover_part['sell']],
                          'all': outperformance_by_stk[turnover_part['all']]}
        return fulfill_percent, outperformance

    @staticmethod
    def get_available_vol(price, date_time, mk_data_, spread_, trade_direciton):
        mk_data = mk_data_.shift(-1)
        spread = spread_.shift(-1)
        if spread[date_time] == 0:
            available_vol = 0.5 * mk_data.loc[date_time, 'volume']
        elif trade_direciton is 'B':
            available_vol = max(
                0.5 * mk_data.loc[date_time, 'volume'] * (price - mk_data.loc[date_time, 'low']) / spread[date_time], 0)
        else:
            available_vol = max(
                0.5 * mk_data.loc[date_time, 'volume'] * (mk_data.loc[date_time, 'high'] - price) / spread[date_time],
                0)
        available_vol = round(available_vol, -2)
        return available_vol

    @abstractmethod
    def calc_stk_day(self, stk_id, day, vol, mk_data, signal):
        pass

# @Time : 2020/7/15 10:09
# @Author : Zhichen Lu
# @File : StrategyBase.py
from abc import abstractmethod
from multiprocessing import Pool, Manager

import gc
import pandas as pd

from dataApi.getData import get_date_range
from dataApi.tradeDate import trade_minutes


class StrategyBases:

    def __init__(self):
        self.data = None
        self.date_list = Manager().list()
        self.stk_list = None
        self.month = None
        self.record = {}
        self.data = Manager().dict()
        # self.strong_universe = Manager().dict()

    def load_data(self, year_month, factor):
        data = pd.read_pickle('/data/group/800080/PanelMinDataForZT/stock/%s/%s_%s.pkl' % (factor, year_month, factor))
        return data

    def backtest(self, stk_list, start_date, end_date, kernel_num=10):

        date_list = get_date_range(start_date, end_date)
        for date in date_list:
            self.date_list.append(date)
        self.monthly_update(date_list[0] // 100)
        month_list = list(set([x // 100 for x in date_list]))
        month_list.sort()
        record_dict = {x: [] for x in stk_list}
        status = {x: None for x in stk_list}
        for month in month_list:
            if month is None or month != self.month:
                self.monthly_update(month)
            pool = Pool(kernel_num)
            pool_dict = {}
            for stk in stk_list:
                temp = self.run_stk_by_month(*(stk, month, status[stk]))
                # pool_dict[stk] = pool.apply_async(self.run_stk_by_month,args=(*(stk,month,status[stk]),))
            # pool.close()
            # pool.join()
            for stk in pool_dict:
                try:
                    record_dict[stk] += pool_dict[stk].get()
                except:
                    print(month, stk, 'Wrong')
                    self.run_stk_by_month(stk, status[stk])
                    raise Exception('Wrong bu re-run through %d %s' % (month, stk))
                temp_record = record_dict[stk]
                if temp_record:
                    _, holding, available = temp_record
                    status[stk] = {'holding': holding, 'available': available}

    def run_stk_by_month(self, stk_id, month, status=None, last_month=False):

        if status == None:
            status = {'holding': 0, 'available': 0}
        record = []
        date_list = list(filter(lambda x: x <= month * 100 + 31, self.date_list._getvalue()))
        for date in date_list:
            for bar in trade_minutes:
                print(bar)
                status, temp_record = self.bar_handler(stk_id, (date, bar), status)
                if temp_record:
                    record.append(temp_record)
        return record

    @abstractmethod
    def bar_handler(self, stk, date_time):
        pass

    @abstractmethod
    def monthly_update(self, month):
        self.month = month
        del self.data
        gc.collect()
        self.data = Manager().dict()
        self.data['close'] = self.load_data(month, 'close')

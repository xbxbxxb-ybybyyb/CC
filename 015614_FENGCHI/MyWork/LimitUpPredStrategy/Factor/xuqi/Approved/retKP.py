# author: kiki_777
# date: 2021/7/28
import sys

sys.path.append('/data/group/800442/800319/')
from dataApi.getData import *
from dataApi.stockList import *
from dataApi.tradeDate import *
import bottleneck as bn
from backtest.factor_backtest.TickDataPrepare2 import TickDataPrepare, search_index

dp = TickDataPrepare(address='/arch1/group/800442/800319/LimitTickData2')


class retKP(object):

    def __init__(self, start_date=20210615, end_date=20210715):
        date_list = get_date_range(start_date, end_date)
        start_date = date_list[0]
        end_date = date_list[-1]
        self.start_date = start_date
        self.end_date = end_date

    def calculate(self, factor_name, save_path=None):
        LimitPool = dp.get_data_by_date_list(item='LimitPool',
                                             start_date=self.start_date,
                                             end_date=self.end_date,
                                             date_list=None,
                                             start_tick=91500,
                                             end_tick=150000,
                                             tick_list=None,
                                             return_idx=True
                                             )

        LastPx = dp.get_data_by_date_list(item='LastPx',
                                          start_date=self.start_date,
                                          end_date=self.end_date,
                                          date_list=None,
                                          start_tick=91500,
                                          end_tick=150000,
                                          tick_list=None,
                                          return_idx=True
                                          )

        date_list = get_date_range(self.start_date, self.end_date)
        open = get_daily_1factor('open', date_list)
        open = open.stack().reset_index().rename(columns={0: 'open', 'level_1': 'code', 'mddate': 'date'}).set_index(['date', 'code'])

        pct_kp = LastPx.div(open.loc[LastPx.index, 'open'], axis=0) - 1
        factor = pct_kp[LimitPool].stack()

        if save_path:
            factor.to_pickle(save_path + factor_name + '.pkl')

        return factor


fc = retKP(start_date=20140102, end_date=20210715)
test = fc.calculate('retKP', '/arch1/group/800442/800319/ZTfactors/Approved_2021/')

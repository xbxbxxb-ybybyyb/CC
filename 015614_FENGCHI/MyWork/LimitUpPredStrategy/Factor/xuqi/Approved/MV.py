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


class MV(object):

    def __init__(self, start_date=20210615, end_date=20210715):
        date_list = get_date_range(start_date, end_date)
        start_date = date_list[0]
        end_date = date_list[-1]
        self.start_date = start_date
        self.end_date = end_date

    def calculate(self, factor_name, save_path=None):

        date_list = get_date_range(get_pre_trade_date(self.start_date, 10), self.end_date)
        float_share = get_daily_1factor('float_a_shares', date_list)


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

        float_tick = pd.DataFrame(np.repeat(float_share.shift(1).stack().loc[LimitPool.index].values, LimitPool.shape[1]).reshape(LimitPool.shape[0],LimitPool.shape[1]),
                                  index=LimitPool.index, columns=LimitPool.columns)
        factor = (float_tick*LastPx)[LimitPool].stack()

        if save_path:
            factor.to_pickle(save_path + factor_name + '.pkl')

        return factor


fc = MV(start_date=20140102, end_date=20210715)
test = fc.calculate('MV', '/arch1/group/800442/800319/ZTfactors/Approved_2021/')

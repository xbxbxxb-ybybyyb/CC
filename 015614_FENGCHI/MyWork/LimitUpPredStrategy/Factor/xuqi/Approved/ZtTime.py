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


class ZtTime(object):

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

        test = LimitPool[LimitPool].stack().reset_index().rename(columns={'level_2': 'tick'})
        common_ticks = LimitPool.columns.tolist()
        test['zt_time'] = test['tick'].apply(lambda x: common_ticks.index(x))
        factor = test[['date','code','tick', 'zt_time']].set_index(['date','code','tick'])['zt_time']

        if save_path:
            factor.to_pickle(save_path+factor_name+'.pkl')

        return factor


fc = ZtTime(start_date=20210615, end_date=20210715)
test = fc.calculate('ZtTime')

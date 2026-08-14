# author: kiki_777
# date: 2021/7/28
import sys
sys.path.append('/data/group/800442/800319/')
from dataApi.getData import *
from dataApi.stockList import *
from dataApi.tradeDate import *
from backtest.factor_backtest.TickDataPrepare2 import TickDataPrepare, search_index
dp = TickDataPrepare(address='/arch1/group/800442/800319/LimitTickData2')


class w_vwap2C(object):

    def __init__(self, start_date=20210615, end_date=20210715):

        date_list = get_date_range(start_date, end_date)
        start_date = date_list[0]
        end_date = date_list[-1]
        self.start_date = start_date
        self.end_date = end_date

    def calculate(self, factor_name, save_path=None):

        date_list = get_date_range(get_pre_trade_date(self.start_date, 40), self.end_date)
        vwap = get_daily_1factor('vwap', date_list)
        preclose = get_daily_1factor('pre_close', date_list)
        free_turn = get_daily_1factor('free_turn', date_list)
        w_vwap2C = ((vwap * free_turn).rolling(30, min_periods=1).apply(lambda x: np.nansum(x))/(free_turn.rolling(30, min_periods=1).apply(lambda x: np.nansum(x))))/preclose

        factor = w_vwap2C.shift(1)

        LimitPool = dp.get_data_by_date_list(item='LimitPool',
                                             start_date=self.start_date,
                                             end_date=self.end_date,
                                             date_list=None,
                                             start_tick=91500,
                                             end_tick=150000,
                                             tick_list=None,
                                             return_idx=True
                                             )
        factor = pd.DataFrame(np.repeat(factor.stack().loc[LimitPool.index].values, LimitPool.shape[1]).reshape(LimitPool.shape[0],LimitPool.shape[1]),
                              index=LimitPool.index, columns=LimitPool.columns)
        factor = factor[LimitPool].stack()

        if save_path:
            factor.to_pickle(save_path+factor_name+'.pkl')

        return factor


fc = w_vwap2C(start_date=20210615, end_date=20210715)
test = fc.calculate('w_vwap2C')

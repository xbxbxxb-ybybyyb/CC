# author: kiki_777
# date: 2021/7/28
import sys
sys.path.append('/data/group/800442/800319/')
from dataApi.getData import *
from dataApi.stockList import *
from dataApi.tradeDate import *
from backtest.factor_backtest.TickDataPrepare2 import TickDataPrepare, search_index
dp = TickDataPrepare(address='/arch1/group/800442/800319/LimitTickData2')


class SHhist(object):

    def __init__(self, start_date=20210615, end_date=20210715):

        date_list = get_date_range(start_date, end_date)
        start_date = date_list[0]
        end_date = date_list[-1]
        self.start_date = start_date
        self.end_date = end_date

    def calc_macd(self, data, short, long, m):
        diff = data.ewm(adjust=False, alpha=2 / (short + 1), ignore_na=True).mean() - \
               data.ewm(adjust=False, alpha=2 / (long + 1), ignore_na=True).mean()
        dea = diff.ewm(adjust=False, alpha=2 / (m + 1), ignore_na=True).mean()
        macd = 2 * (diff - dea)
        return macd



    def calculate(self, factor_name, save_path=None):

        date_list = get_date_range(get_pre_trade_date(self.start_date, 40), self.end_date)
        idx_close = get_daily_1factor('close', date_list, type='bench')
        idx_macd = self.calc_macd(idx_close, 12, 26, 9)
        factor = idx_macd['SZZZ'].shift(1)

        LimitPool = dp.get_data_by_date_list(item='LimitPool',
                                             start_date=self.start_date,
                                             end_date=self.end_date,
                                             date_list=None,
                                             start_tick=91500,
                                             end_tick=150000,
                                             tick_list=None,
                                             return_idx=True
                                             )

        stock_stack = LimitPool[LimitPool].stack()

        factor = pd.Series(factor.loc[stock_stack.index.get_level_values('date')].values, index=stock_stack.index)

        if save_path:
            factor.to_pickle(save_path + factor_name + '.pkl')

        return factor


fc = SHhist(start_date=20140102, end_date=20210715)
test = fc.calculate('SHhist', '/arch1/group/800442/800319/ZTfactors/Approved_2021/')

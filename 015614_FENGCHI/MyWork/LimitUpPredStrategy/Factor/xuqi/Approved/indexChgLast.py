# author: kiki_777
# date: 2021/7/28
import sys
sys.path.append('/data/group/800442/800319/')
from dataApi.getData import *
from dataApi.stockList import *
from dataApi.tradeDate import *
from backtest.factor_backtest.TickDataPrepare2 import TickDataPrepare, search_index
dp = TickDataPrepare(address='/arch1/group/800442/800319/LimitTickData2')


class indexChgLast(object):

    def __init__(self, start_date=20210615, end_date=20210715):

        date_list = get_date_range(start_date, end_date)
        start_date = date_list[0]
        end_date = date_list[-1]
        self.start_date = start_date
        self.end_date = end_date

    def calculate(self, factor_name, save_path=None):

        date_list = get_date_range(get_pre_trade_date(self.start_date, 5), self.end_date)
        idx_close = get_daily_1factor('close', date_list, type='bench')
        idx_pctLast = idx_close.pct_change(1)

        high = get_daily_1factor('high', date_list)
        stk_class = pd.DataFrame(index=high.index, columns=high.columns)
        stk_class.columns = stk_class.columns.map(trans_int2windcode)

        stk_class[stk_class.columns[stk_class.columns.str.endswith('SZ')]] = 1
        stk_class[stk_class.columns[stk_class.columns.str.endswith('SH')]] = 2
        stk_class.columns = stk_class.columns.map(trans_windcode2int)

        factor = ((stk_class == 1) * (high > 0)).mul(idx_pctLast['SZCZ'], axis=0) + \
                 ((stk_class == 2) * (high > 0)).mul(idx_pctLast['SZZZ'], axis=0)

        LimitPool = dp.get_data_by_date_list(item='LimitPool',
                                             start_date=self.start_date,
                                             end_date=self.end_date,
                                             date_list=None,
                                             start_tick=91500,
                                             end_tick=150000,
                                             tick_list=None,
                                             return_idx=True
                                             )

        factor = pd.DataFrame(np.repeat(factor.shift(1).stack().loc[LimitPool.index].values, LimitPool.shape[1]).reshape(LimitPool.shape[0], LimitPool.shape[1]),
                              index=LimitPool.index, columns=LimitPool.columns)
        factor = factor[LimitPool].stack()

        if save_path:
            factor.to_pickle(save_path + factor_name + '.pkl')

        return factor


fc = indexChgLast(start_date=20140102, end_date=20210715)
test = fc.calculate('indexChgLast', '/arch1/group/800442/800319/ZTfactors/Approved_2021/')

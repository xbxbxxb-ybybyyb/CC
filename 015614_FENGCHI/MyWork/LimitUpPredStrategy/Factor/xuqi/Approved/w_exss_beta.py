# author: kiki_777
# date: 2021/7/28
import sys
sys.path.append('/data/group/800442/800319/')
from dataApi.getData import *
from dataApi.stockList import *
from dataApi.tradeDate import *
from backtest.factor_backtest.TickDataPrepare2 import TickDataPrepare, search_index
dp = TickDataPrepare(address='/arch1/group/800442/800319/LimitTickData2')


class w_exss_beta(object):

    def __init__(self, start_date=20210615, end_date=20210715):

        date_list = get_date_range(start_date, end_date)
        start_date = date_list[0]
        end_date = date_list[-1]
        self.start_date = start_date
        self.end_date = end_date

    def rolling_beta(self, x, y, period):

        cx = x.rolling(period).mean()
        cy = y.rolling(period).mean()
        cx2 = (x ** 2).rolling(period).sum()
        cxy = (x * y).rolling(period).sum()

        return (cxy - period * cx * cy) / (cx2 - period * (cx ** 2))

    def calculate(self, factor_name, save_path=None):

        date_list = get_date_range(get_pre_trade_date(self.start_date, 40), self.end_date)
        pct = get_daily_1factor('pct_chg', date_list)
        idx_close = get_daily_1factor('close', date_list, type='bench')
        idx_pct = idx_close.pct_change(1)

        idx_pct_df = pd.DataFrame(np.repeat(np.array(idx_pct['SZZZ']).reshape(-1, 1), pct.shape[1], axis=1),
                                  index=pct.index, columns=pct.columns)
        w_exss_beta = self.rolling_beta(idx_pct_df, pct / 100, 30)
        factor = w_exss_beta.shift(1)

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


fc = w_exss_beta(start_date=20140102, end_date=20210715)
test = fc.calculate('w_exss_beta', '/arch1/group/800442/800319/ZTfactors/Approved_2021/')

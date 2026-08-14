import pandas as pd
import numpy as np
import bottleneck
from dataApi.stockList import clean_stock_list
from dataApi.tradeDate import get_date_range, get_pre_trade_date, trade_minutes
from dataApi.getData import get_minute_1factor, get_daily_1factor

class SimpleFactorBackTest(object):


    def __init__(self, stock_pool='COMMON', start_date=20170103, end_date=20191231,
                 adj_freq=5, adj_minutes=None):

        if isinstance(stock_pool, str):
            stock_pool = clean_stock_list(stock_pool)
        elif not isinstance(stock_pool, pd.DataFrame):
            raise TypeError('stock_pool must be str or DataFrame')

        start_date = get_pre_trade_date(start_date, -1) if get_pre_trade_date(start_date, 0) != start_date else start_date
        end_date = get_pre_trade_date(end_date, 0)
        trade_dates = get_date_range(start_date, end_date)

        if adj_minutes == None:
            adj_minutes = trade_minutes[1:-4][::adj_freq]
        adj_minute_index = [trade_minutes.index(x) for x in adj_minutes]

        stock_list = clean_stock_list(no_limit_down=True, no_limit_up=True).shift(1).reindex(trade_dates)
        stock_list = (stock_list > 0.5) & (stock_pool.shift(1).reindex_like(stock_list) > 0.5) if stock_pool is not None else stock_list
        stock_list = stock_list.reindex(columns=sorted(stock_list.sum()[stock_list.sum() > 0.5].index.tolist()))

        close = get_minute_1factor('close', start_date, end_date, code_list=stock_list.columns.to_list())
        close = close.values.reshape(close.shape[0] // 242, 242, close.shape[1]).transpose(1, 0, 2)
        close[:, ~ stock_list] = np.nan
        daily_close = close[-1]
        close = close[adj_minute_index]

        ret_interval = np.concatenate((close[1:], daily_close[None, :, :])) / close - 1
        ret_interval_rank = bottleneck.nanrankdata(ret_interval, axis=2)

        twap = get_daily_1factor('twap', date_list=trade_dates, code_list=stock_list.columns.to_list()).values
        ret_twap = twap / close - 1
        ret_twap_rank = bottleneck.nanrankdata(ret_twap, axis=2)

        self.start_date = start_date
        self.end_date = end_date
        self.adj_minute_index = adj_minute_index
        self.stock_list = stock_list
        self.stocks = stock_list.columns.to_list()
        self.ret_twap_rank = ret_twap_rank
        self.ret_interval_rank = ret_interval_rank

    def load_factor(self, factor, group=10):

        factor_rank = factor[self.adj_minute_index]
        factor_rank[:, ~ self.stock_list] = np.nan
        factor_rank = bottleneck.nanrankdata(factor_rank, axis=2)
        factor_rank = factor_rank.transpose(2, 0, 1)
        factor_rank /= (~ np.isnan(factor_rank)).sum(axis=0) / group
        factor_rank = factor_rank.transpose(1, 2, 0)
        self.factor = factor_rank
        self.group = group
        del factor_rank

    def calc_ic(self, ret_type='interval'):

        ret_rank = {'twap': self.ret_twap_rank, 'interval': self.ret_interval_rank}[ret_type].copy()
        notnull = ~ (np.isnan(ret_rank) | np.isnan(self.factor))
        factor_rank = self.factor.copy()
        ret_rank[~ notnull] = 0
        factor_rank[~ notnull] = 0
        cxy = (factor_rank * ret_rank).sum(axis=2)
        cx = factor_rank.sum(axis=2)
        cx2 = (factor_rank ** 2).sum(axis=2)
        cy = ret_rank.sum(axis=2)
        cy2 = (ret_rank ** 2).sum(axis=2)
        n = notnull.sum(axis=2)
        ic = (n * cxy - cx * cy) / np.sqrt((n * cx2 - cx ** 2) * (n * cy2 - cy ** 2))
        del ret_rank, factor_rank, cxy, cx, cy, cx2, cy2
        ic = np.nanmean(ic)
        return ic

    def simple_test(self, factor, group=10):

        self.load_factor(factor, group=group)
        ic_interval = self.calc_ic('interval')
        ic_twap = self.calc_ic('twap')
        return ic_interval, ic_twap

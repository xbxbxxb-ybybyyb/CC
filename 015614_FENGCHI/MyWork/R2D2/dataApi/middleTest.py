import itertools
import pandas as pd
import numpy as np
import bottleneck
from dataApi.stockList import clean_stock_list
from dataApi.tradeDate import get_date_range, get_pre_trade_date, trade_minutes
from dataApi.getData import get_minute_1factor, get_daily_1factor

class MiddleFactorBackTest(object):


    def __init__(self, stock_pool='COMMON', start_date=20170103, end_date=20191231,
                 adj_freq=5, adj_minutes=None, benchmark='ZZ500'):

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

        trade_datetime = list(itertools.product(trade_dates, adj_minutes))

        stock_list = clean_stock_list(no_limit_down=True, no_limit_up=True).shift(1).reindex(trade_dates)
        stock_list = (stock_list > 0.5) & (stock_pool.shift(1).reindex_like(stock_list) > 0.5) if stock_pool is not None else stock_list
        stock_list = stock_list.reindex(columns=sorted(stock_list.sum()[stock_list.sum() > 0.5].index.tolist()))

        close = get_minute_1factor('close', start_date, end_date, code_list=stock_list.columns.to_list())
        close = close.values.reshape(close.shape[0] // 242, 242, close.shape[1]).transpose(1, 0, 2)
        close[:, ~ stock_list] = np.nan
        daily_close = close[-1]
        close = close[adj_minute_index]

        ret_close = daily_close / close - 1
        ret_close_rank = bottleneck.nanrankdata(ret_close, axis=2)

        ret_interval = np.concatenate((close[1:], daily_close[None, :, :])) / close - 1
        ret_interval_rank = bottleneck.nanrankdata(ret_interval, axis=2)

        twap = get_daily_1factor('twap', date_list=trade_dates, code_list=stock_list.columns.to_list()).values
        ret_twap = twap / close - 1
        ret_twap_rank = bottleneck.nanrankdata(ret_twap, axis=2)

        bench = get_minute_1factor('close', start_date, end_date, code_list=[benchmark], type='bench')
        bench = bench.values[:,0].reshape(bench.shape[0] // 242, 242).T
        ret_bench = bench[-1] / bench[adj_minute_index] - 1
        ret_excess = (ret_close.transpose(2, 0, 1) - ret_bench).transpose(1, 2, 0)
        ret_excess_rank = bottleneck.nanrankdata(ret_excess, axis=2)

        self.start_date = start_date
        self.end_date = end_date
        self.adj_minute_index = adj_minute_index
        self.stock_list = stock_list
        self.stocks = stock_list.columns.to_list()
        self.trade_datetime = trade_datetime
        self.ret_twap_rank = ret_twap_rank
        self.ret_interval_rank = ret_interval_rank
        self.ret_close_rank = ret_close_rank
        self.ret_excess_rank = ret_excess_rank
        self.ret_close = ret_close
        self.ret_interval = ret_interval
        self.ret_excess = ret_excess
        self.ret_twap = ret_twap

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

        ret_rank = {'twap': self.ret_twap_rank, 'interval': self.ret_interval_rank, 'close': self.ret_close_rank,
                    'excess': self.ret_excess_rank}[ret_type].copy()
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
        return ic

    def calc_group_ret(self, ret_type):

        factor_rank = np.floor(self.factor)
        ret = {'twap': self.ret_twap, 'close': self.ret_close, 'excess': self.ret_excess, 'interval': self.ret_interval}[ret_type]
        mean_ret = pd.DataFrame({x: np.nanmean(np.ma.array(ret, mask=(factor_rank != x)), axis=2).data.T.reshape(
            len(self.trade_datetime)) for x in np.arange(self.group)}, index=self.trade_datetime)
        return mean_ret

    def middle_test(self, factor, address, file_name, group=10):

        self.load_factor(factor, group=group)

        ic_interval = self.calc_ic('interval')
        ic_twap = self.calc_ic('twap')
        ic_close = self.calc_ic('close')
        ic_excess = self.calc_ic('excess')

        group_interval = self.calc_group_ret('interval')
        group_twap = self.calc_group_ret('twap')
        group_close = self.calc_group_ret('close')
        group_excess = self.calc_group_ret('excess')

        with pd.ExcelWriter(address + '/' + file_name + '.xlsx') as writer:
            pd.DataFrame(np.concatenate([ic_interval.T.reshape(len(self.trade_datetime), 1),
                                         ic_twap.T.reshape(len(self.trade_datetime), 1),
                                         ic_close.T.reshape(len(self.trade_datetime), 1),
                                         ic_excess.T.reshape(len(self.trade_datetime), 1)], axis=1),
                         index=self.trade_datetime, columns=['interval', 'twap', 'close', 'excess']
                         ).to_excel(writer, 'ic')
            group_interval.to_excel(writer, 'interval')
            group_twap.to_excel(writer, 'twap')
            group_close.to_excel(writer, 'close')
            group_excess.to_excel(writer, 'excess')

        return np.nanmean(ic_interval), np.nanmean(ic_twap), np.nanmean(ic_close), np.nanmean(ic_excess), \
               np.nanmean(np.abs(np.nanmean(ic_excess, axis=0))), np.nanmean(np.nanmean(ic_excess, axis=0) > 0)

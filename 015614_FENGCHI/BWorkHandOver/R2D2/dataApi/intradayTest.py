import itertools
import pandas as pd
import numpy as np
from dataApi.stockList import clean_stock_list
from dataApi.tradeDate import get_date_range, get_pre_trade_date, trade_minutes
from dataApi.getData import get_minute_1factor, get_daily_1factor

class FactorBackTest(object):


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

        stock_list = clean_stock_list(no_limit_down=True, no_limit_up=True).reindex(trade_dates)
        stock_list = (stock_list > 0.5) & (stock_pool.reindex_like(stock_list) > 0.5) if stock_pool is not None else stock_list
        stock_list = stock_list.reindex(columns=sorted(stock_list.sum()[stock_list.sum() > 0.5].index.tolist()))

        close = get_minute_1factor('close', start_date, end_date, code_list=stock_list.columns.to_list())
        close = close.values.reshape(close.shape[0] // 242, 242, close.shape[1]).transpose(1, 0, 2)
        close[:, ~ stock_list] = np.nan
        daily_close = close[-1]
        close = close[adj_minute_index]
        ret_close = daily_close / close - 1

        ret_interval = np.concatenate((close[1:], daily_close[None, :, :])) / close - 1
        ret_interval_rank = np.argsort(np.argsort(ret_interval, axis=2), axis=2).astype(float)
        ret_interval_rank[np.isnan(ret_interval)] = np.nan

        bench = get_minute_1factor('close', start_date, end_date, code_list=[benchmark], type='bench')
        bench = bench.values[:,0].reshape(bench.shape[0] // 242, 242).T
        ret_bench = bench[-1] / bench[adj_minute_index] - 1
        ret_excess = (ret_close.transpose(2, 0, 1) - ret_bench).transpose(1, 2, 0)

        twap = get_daily_1factor('twap', date_list=trade_dates, code_list=stock_list.columns.to_list()).values
        ret_twap = twap / close - 1
        ret_twap_rank = np.argsort(np.argsort(ret_twap, axis=2), axis=2).astype(float)
        ret_twap_rank[np.isnan(ret_twap)] = np.nan

        self.trade_dates = trade_dates
        self.adj_minutes = adj_minutes
        self.trade_datetime = trade_datetime
        self.stock_list = stock_list
        self.stocks = stock_list.columns.to_list()
        self.ret_twap_rank = ret_twap_rank
        self.ret_interval_rank = ret_interval_rank
        self.ret_close = ret_close
        self.ret_excess = ret_excess
        self.ret_twap = ret_twap
        self.ret_interval = ret_interval

    def load_factor(self, factor, group=10):

        if type(factor.index[0]) == tuple:
            factor = factor.reindex(index=self.trade_datetime, columns=self.stocks)
        elif type(factor.index[0]) in (int, np.int64):
            trade_datetime = [10000 * x[0] + x[1] for x in self.trade_datetime]
            factor = factor.reindex(index=trade_datetime, columns=self.stocks)
        elif type(factor.index[0]) == str:
            trade_datetime = [str(10000 * x[0] + x[1]) for x in self.trade_datetime]
            factor = factor.reindex(index=trade_datetime, columns=self.stocks)
        else:
            raise TypeError('factor index type error')

        factor = factor.values.reshape(len(self.trade_dates), len(self.adj_minutes), len(self.stocks)).transpose(1, 0, 2)
        factor[:, ~ self.stock_list] = np.nan
        factor_rank = np.argsort(np.argsort(factor, axis=2), axis=2).astype(float)
        factor_rank[np.isnan(factor)] = np.nan
        factor_rank = factor_rank.transpose(2, 0, 1)
        factor_rank /= (~ np.isnan(factor_rank)).sum(axis=0) / group
        factor_rank = factor_rank.transpose(1, 2, 0)
        self.factor = factor_rank
        self.group = group
        del factor_rank, factor

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
        ic = np.nanmean(ic, axis=0)
        ic = pd.Series(ic, index=self.trade_dates)
        return ic

    def calc_group_ret(self, ret_type, win_ret=0.0012):

        factor_rank = np.floor(self.factor)
        ret = {'twap': self.ret_twap, 'close': self.ret_close, 'excess': self.ret_excess, 'interval': self.ret_interval}[ret_type]
        win = ret > win_ret
        win[np.isnan(ret)] = np.nan
        mean_ret = pd.DataFrame({x: np.nanmean(np.nanmean(np.ma.array(ret, mask=(factor_rank != x)), axis=2).data, axis=0)
                                 for x in np.arange(self.group)}, index=self.trade_dates)
        mean_win = pd.DataFrame({x: np.nanmean(np.nanmean(np.ma.array(win, mask=(factor_rank != x)), axis=2).data, axis=0)
                                 for x in np.arange(self.group)}, index=self.trade_dates)
        return mean_ret, mean_win

    def report(self, factor, only_ic=False, group=10, output=True, address=None, file_name=None,
               win_ret=0.0012, ret_list=('interval', 'twap', 'close', 'excess')):

        self.load_factor(factor, group=group)

        self.ic_interval = self.calc_ic('interval')
        self.ic_interval.name = self.ic_interval.mean()
        self.ic_interval.index.name = 'ic_interval_mean'

        self.ic_twap = self.calc_ic('twap')
        self.ic_twap.name = self.ic_twap.mean()
        self.ic_twap.index.name = 'ic_twap_mean'

        if only_ic:
            if output:
                with pd.ExcelWriter(address + '/' + file_name + '.xlsx') as writer:
                    pd.DataFrame().to_excel(writer, 'miss_road')
                    self.ic_interval.to_excel(writer, 'ic_interval')
                    self.ic_twap.to_excel(writer, 'ic_twap')
            return self.ic_interval.mean()
        else:
            with pd.ExcelWriter(address + '/' + file_name + '.xlsx') as writer:
                df = pd.DataFrame()
                df.to_excel(writer, 'miss_road')
                dic = {}
                for ret_type in ret_list:
                    dic[ret_type + '_ret'], dic[ret_type + '_win'] = self.calc_group_ret(ret_type, win_ret)
                    df = pd.concat([df, dic[ret_type + '_ret'].mean().rename(ret_type + '_mean_ret'),
                                    dic[ret_type + '_win'].mean().rename(ret_type + '_mean_win')], axis=1)
                df.to_excel(writer, 'summary')
                self.ic_interval.to_excel(writer, 'ic_interval')
                self.ic_twap.to_excel(writer, 'ic_twap')
                for key in dic.keys():
                    dic[key].to_excel(writer, key)
            self.result = df

if __name__ == '__main__':

    ft = FactorBackTest()#65.71
    factor = pd.read_hdf('/data/user/hanxu/factor.h5', 'factor')
    ft.load_factor(factor)#15.40
    ft.calc_ic.mean()#4.21
    mean_ret, mean_win = ft.calc_group_ret('twap')#40.00
    ft.report(factor=factor, address='/data/user/hanxu/junk_factor.xlsx')#141.65


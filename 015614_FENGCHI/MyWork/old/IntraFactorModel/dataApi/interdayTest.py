# coding: utf-8
# Author：fengchi863
# Date ：2020/3/19 15:02

import numpy as np
import pandas as pd

from dataApi.getData import get_daily_1factor
from dataApi.stockList import clean_stock_list
from dataApi.tradeDate import get_date_range, get_pre_trade_date


class FactorBackTest:

    def __init__(self, stock_pool='COMMON', start_date=20170101, end_date=20191231, group=10):
        if isinstance(stock_pool, str):
            stock_pool = clean_stock_list(stock_pool)
        elif not isinstance(stock_pool, pd.DataFrame):
            raise TypeError('stock_pool must be str or DataFrame')

        start_date = get_pre_trade_date(start_date, -1)
        end_date = get_pre_trade_date(end_date, 0)
        trade_dates = get_date_range(start_date, end_date)

        stock_list = clean_stock_list(no_limit_down=True, no_limit_up=True).reindex(trade_dates)
        stock_list = (stock_list > 0.5) & (
                stock_pool.reindex_like(stock_list) > 0.5) if stock_pool is not None else stock_list
        stock_list = stock_list.reindex(columns=sorted(stock_list.sum()[stock_list.sum() > 0.5].index.tolist()))

        close = get_daily_1factor('close_badj')
        close[~ stock_list] = np.nan
        daily_ret = close.pct_change(1).shift(-1).loc[start_date:end_date]

        self.start_date = start_date
        self.end_date = end_date
        self.group = group
        self.stock_list = stock_list
        self.stocks = stock_list.columns.to_list()
        self.trade_dates = trade_dates
        self.daily_ret = daily_ret

    def load_factor(self, factor):
        if type(factor.index[0]) == np.int64:
            factor = factor.reindex(index=self.trade_dates, columns=self.stocks)
        else:
            raise TypeError('factor index type error')

        factor_rank = (factor.rank(pct=True) * self.group).applymap(np.ceil)
        self.factor = factor
        self.factor_rank = factor_rank

    def calc_ic(self):
        factor = self.factor.copy()
        daily_ret = self.daily_ret.copy()
        ic = self.daily_ret.corrwith(factor, axis=1)
        del factor, daily_ret
        return ic

    def calc_group_ret(self):
        factor_rank = self.factor_rank.copy()
        daily_ret = self.daily_ret.copy()
        group_ret = pd.concat([factor_rank.stack(), daily_ret.stack()], axis=1)
        group_ret = group_ret.reset_index()
        group_ret.columns = ['date', 'stock', 'group', 'ret']
        group_ret = group_ret.groupby(['date', 'group'])['ret'].mean()
        group_ret_result = group_ret.unstack()
        new_row = group_ret_result.mean()
        index = group_ret_result.index.tolist()
        index = index + ['mean']
        group_ret_result = group_ret_result.append(new_row, ignore_index=True)
        group_ret_result.index = index
        self.group_ret_result = group_ret_result
        return group_ret_result

    def report(self, factor, address=None, file_name=None, ):
        self.load_factor(factor)

        self.ic_close = self.calc_ic()
        self.ic_close.name = self.ic_close.mean()
        self.ic_close.index.name = 'ic_close_mean'

        with pd.ExcelWriter(address + '/' + file_name + '.xlsx') as writer:
            df = pd.DataFrame()
            df.to_excel(writer, 'factor_description')
            self.ic_close.index = self.ic_close.index.astype(str)
            self.group_ret_result.index = self.group_ret_result.index.astype(str)
            self.ic_close.to_excel(writer, 'ic_close')
            self.group_ret_result.to_excel(writer, 'group_ret')


if __name__ == '__main__':
    at = FactorBackTest(group=10)
    root_path = '/data/group/800319/junkData/temp_factor_by_fc/'
    factor = pd.read_hdf(root_path + 'alpha_test.h5', 'factor')
    at.load_factor(factor)
    at.calc_group_ret()
    print(at.calc_ic().mean())
    at.report(factor=factor, address=root_path, file_name='junk_factor')

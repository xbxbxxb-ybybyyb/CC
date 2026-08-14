import numba
import bottleneck
import numpy as np
import pandas as pd
from dataApi.getData import get_daily_1factor, get_modified_ind_mv
from dataApi.stockList import clean_stock_list
from dataApi.tradeDate import get_date_range, get_pre_trade_date

def winsorize(arr, axis=-1):

    arr = arr.swapaxes(0, axis).astype(float)
    median = np.nanmedian(arr, axis=0)
    mad = np.nanmedian(np.abs(arr - median), axis=0)
    arr_nan = np.isnan(arr)
    up_bound = median + 4.449 * mad
    down_bound = median - 4.449 * mad
    up_mask = (arr <= up_bound) | arr_nan
    down_mask = (arr >= down_bound) | arr_nan
    arr_up = np.ma.array(arr, mask=up_mask, fill_value=np.nan)
    arr_down = np.ma.array(arr, mask=down_mask, fill_value=np.nan)
    arr[~ up_mask] = (up_bound + 0.7415 * mad * bottleneck.nanrankdata(
        arr_up.filled(), axis=0) / arr_up.count(axis=0))[~ up_mask]
    arr[~ down_mask] = (down_bound - 0.7415 * mad * (1 + (1 - bottleneck.nanrankdata(
        arr_down.filled(), axis=0)) / arr_down.count(axis=0)))[~ down_mask]
    arr = arr.swapaxes(0, axis)
    return arr

def standardize(arr, axis=-1):

    arr = arr.swapaxes(0, axis)
    arr -= np.nanmean(arr, axis=0)
    arr /= np.nanstd(arr, ddof=1, axis=0)
    arr = arr.swapaxes(0, axis)
    return arr

def neutralize(X, miss, y):

    mask = np.isnan(y) | miss
    y[mask] = 0
    z = np.vectorize(lambda x, y: x @ y, signature='(m,n),(n)->(n)')(X, y)
    z[mask] = np.nan
    return z

@numba.jit(nopython=True)
def _core_ols_X_residual(X):

    Y = np.empty((X.shape[0], X.shape[1], X.shape[1]))
    for i in range(Y.shape[0]):
        Y[i] = - X[i] @ np.linalg.inv(X[i].T @ X[i]) @ X[i].T
    Y += np.eye(X.shape[1])
    return Y

@numba.jit(nopython=True)
def _core_ols_X_beta(X):

    Y = np.empty((X.shape[0], X.shape[2], X.shape[1]))
    for i in range(Y.shape[0]):
        Y[i] = np.linalg.inv(X[i].T @ X[i]) @ X[i].T
    return Y

def ols_X(X, out='residual', k_axis=-2, n_axis=-1):

    X = X.swapaxes(-1, k_axis).swapaxes(-2, n_axis if n_axis != -1 else k_axis)
    shape = X.shape
    X = X.reshape(int(np.prod(shape[:-2])), shape[-2], shape[-1])
    miss = np.any(np.isnan(X), axis=2)
    X.transpose(2, 0, 1)[:, miss] = 0
    miss = miss.reshape(shape[:-1])
    if out == 'residual':
        Y = _core_ols_X_residual(X)
    elif out == 'beta':
        Y = _core_ols_X_beta(X)
    else:
        raise ValueError("It is too hard for me to calculate.")
    Y = Y.reshape(shape[:-2] + Y.shape[-2:])
    return Y, miss

class NonFactorTest(object):


    def __init__(self, start_date=20170103, end_date=20191231, stock_pool='COMMON', future_days=10,
                 ind_type='SW', bench='ZZ500', price_type='twap', pre_neutralize=True):

        start_date = get_pre_trade_date(start_date, -1) if get_pre_trade_date(start_date, 0) != start_date else start_date
        end_date = get_pre_trade_date(end_date, 0)
        date_list = get_date_range(start_date, end_date)

        if isinstance(stock_pool, str):
            stock_pool = clean_stock_list(stock_pool).reindex(date_list)
        elif isinstance(stock_pool, pd.DataFrame):
            stock_pool = stock_pool.reindex(date_list)
        else:
            raise TypeError('stock_pool must be str or DataFrame')
        code_list = stock_pool.columns.to_list()

        if isinstance(future_days, int):
            future_days = list(range(1, future_days + 1))
        elif not isinstance(future_days, list):
            raise TypeError('future_days must be int or list')
        future_days_max = max(future_days)
        future_date_num = len(future_days)

        price_raw_dates = get_date_range(get_pre_trade_date(start_date, -1),
                                         get_pre_trade_date(end_date, -future_days_max - 1))
        price = get_daily_1factor(price_type, price_raw_dates, code_list) * get_daily_1factor(
            'adjfactor', price_raw_dates, code_list)
        future = np.concatenate(tuple(np.atleast_3d(price.pct_change(x).shift(-x).values) for x in future_days),
                                axis=2).transpose(2, 0, 1)[:, :-future_days_max]
        future[np.arange(future_date_num)[:, None, None], ~stock_pool.values] = np.nan
        future_mask = np.isnan(future)
        stock_pool_num = len(code_list)

        ind, mv = get_modified_ind_mv(date_list, code_list, ind_type)

        price_bench = get_daily_1factor(price_type, price_raw_dates, [bench], type='bench')
        future_bench = np.concatenate(
            tuple(np.atleast_2d(price_bench.pct_change(x).shift(-x).values) for x in future_days),
            axis=1).T[:, :-future_days_max]
        future_bench_ret = ((1 + future_bench.T) ** (1 / np.array(future_days))).T
        future_bench_val = np.nancumprod(future_bench_ret, axis=1)

        bench_stk_wgt = get_daily_1factor(bench + '_exdiv_weight', date_list, code_list).fillna(0).values
        bench_ind_wgt = np.r_['0,2', tuple(np.ma.array(bench_stk_wgt, mask=~ind[x]).sum(axis=1).data
                                           for x in range(ind.shape[0]))]

        if pre_neutralize:
            self.X_mv_ind, self.miss_mv_ind = ols_X(np.r_[mv[None, :, :], ind].swapaxes(0, 1), 'residual')

        self.date_list = date_list
        self.code_list = code_list
        self.stock_pool = stock_pool
        self.stock_pool_num = stock_pool_num
        self.future_days = future_days
        self.future_date_num = future_date_num
        self.future_days_max = future_days_max
        self.future = future
        self.future_mask = future_mask
        self.future_bench_val = future_bench_val
        self.future_bench_ret = future_bench_ret
        self.bench_ind_wgt = bench_ind_wgt
        self.ind = ind
        self.mv = mv

    def load_factor(self, factor, neutral=True, diy_address=None):

        if isinstance(factor, str):
            factor = get_daily_1factor(factor, self.date_list, self.code_list, diy_address=diy_address).values
        elif isinstance(factor, pd.DataFrame):
            factor = factor.reindex(self.date_list, self.code_list).values
        elif isinstance(factor, np.ndarray):
            if factor.shape != (len(self.date_list), len(self.code_list)):
                raise ValueError("Be careful! Do not try to use future data to create a wonderful factor.")
            factor = factor.copy()
        else:
            raise TypeError("factor must be str or pd.DataFrame.")
        if neutral:
            factor = neutralize(self.X_mv_ind, self.miss_mv_ind, standardize(winsorize(factor)))

        factor[~self.stock_pool.values] = np.nan

        factor_rank = factor[None, :, :].repeat(self.future_date_num, axis=0)
        factor_rank[self.future_mask] = np.nan
        factor_rank = bottleneck.nanrankdata(factor_rank, axis=2)
        mask = np.isnan(factor_rank)
        valid_num = self.stock_pool_num - mask.sum(axis=2)

        future_rank = self.future.copy()
        future_rank[mask] = np.nan
        future_rank = bottleneck.nanrankdata(future_rank, axis=2)

        self.factor = factor
        self.factor_rank = factor_rank
        self.future_rank = future_rank
        self.valid_num = valid_num
        self.mask = mask

    def calc_ic(self):

        cxy = np.nansum(self.factor_rank * self.future_rank, axis=2)
        cx2 = np.nansum(self.factor_rank ** 2, axis=2)
        cy2 = np.nansum(self.future_rank ** 2, axis=2)
        cx = np.nansum(self.factor_rank, axis=2)
        cy = np.nansum(self.future_rank, axis=2)
        rank_ic = ((self.valid_num * cxy - cx * cy) /
                   np.sqrt((self.valid_num * cx2 - cx ** 2) * (self.valid_num * cy2 - cy ** 2)))
        ic = np.c_[np.nanmean(rank_ic, axis=1), np.nanmean(np.abs(rank_ic), axis=1),
                   np.nanmean(rank_ic > 0, axis=1), np.nanmean(rank_ic, axis=1) / np.nanstd(rank_ic, axis=1)]
        ic = pd.DataFrame(ic, columns=['IC', 'IC_abs', 'IC_prob', 'IC_IR'],
                          index=pd.Index(self.future_days, name='future'))
        self.rank_ic = rank_ic
        return ic

    def calc_group_ret(self, groups=10):

        factor_group = np.ceil(self.factor_rank.transpose(2, 0, 1) / self.valid_num * groups).transpose(1, 2, 0)
        future_group = np.c_['0,3', tuple(np.ma.array(self.future, mask=self.mask | (factor_group != x))
                                          .mean(axis=2).data for x in range(1, groups + 1))]
        future_group = ((future_group.transpose(0, 2, 1) + 1) ** (1 / np.array(self.future_days))).transpose(2, 1, 0)
        future_group_val = np.nancumprod(future_group, axis=1)
        future_group_rank = bottleneck.nanrankdata(future_group, axis=2) - (groups + 1) / 2
        sequence = np.arange(1, groups + 1) - (groups + 1) / 2
        ic_group = np.nanmean((future_group_rank * sequence).sum(axis=2) /
                              np.sqrt((future_group_rank ** 2).sum(axis=2) * (sequence ** 2).sum()), axis=1)
        monotone = bottleneck.nanrankdata(future_group_val[:, -1], axis=1) - (groups + 1) / 2
        monotone = (monotone * sequence).sum(axis=1) / np.sqrt((monotone ** 2).sum(axis=1) * (sequence ** 2).sum())
        long_short_ret = (future_group_val[:, -1, -1] ** (244 / future_group_val.shape[1]) -
                          future_group_val[:, -1, 0] ** (244 / future_group_val.shape[1]))
        top_excess_ret = (future_group_val[:, -1, -1] ** (244 / future_group_val.shape[1]) -
                          self.future_bench_val[:, -1] ** (244 / self.future_bench_val.shape[1]))
        group_result = pd.DataFrame(np.c_[ic_group, monotone, long_short_ret, top_excess_ret],
                                    columns=['ic_group', 'monotone', 'long_short_ret', 'top_excess_ret'],
                                    index=pd.Index(self.future_days, name='future'))
        self.future_group = future_group
        return group_result

    def calc_strategy_ret(self, strategy_stock_num=200, buy_fee=0, sell_fee=0.002):

        bench_ind_stk_num = np.round(self.bench_ind_wgt * strategy_stock_num)

        strategy_pool = np.any(np.r_['0,3', tuple(bottleneck.nanrankdata(np.ma.filled(np.ma.array(
            -self.factor, mask=~self.ind[x], fill_value=np.nan)), axis=1).T <= bench_ind_stk_num[x]
                                                  for x in range(self.ind.shape[0]))], axis=0).T

        future_strategy_ret = self.future.copy()
        future_strategy_ret[:, ~strategy_pool] = np.nan
        future_strategy_ret = np.nanmean(future_strategy_ret, axis=2)

        buy_turn = tuple((~strategy_pool[:-x] & strategy_pool[x:]).sum(axis=1) for x in self.future_days)
        buy_turn = np.r_['0,2', tuple(
            np.pad(buy_turn[x], (self.future_days[x], 0), mode='constant', constant_values=np.nanmean(
                buy_turn[x])) for x in range(len(self.future_days)))] / strategy_stock_num
        sell_turn = tuple((strategy_pool[:-x] & ~strategy_pool[x:]).sum(axis=1) for x in self.future_days)
        sell_turn = np.r_['0,2', tuple(
            np.pad(sell_turn[x], (self.future_days[x], 0), mode='constant', constant_values=np.nanmean(
                sell_turn[x])) for x in range(self.future_date_num))] / strategy_stock_num

        strategy_turn = (buy_turn + sell_turn).mean(axis=1) / np.array(self.future_days) / 2
        strategy_long_ret = (((1 + future_strategy_ret) * (1 - buy_turn * buy_fee) * (1 - sell_turn * sell_fee)
                              ).T ** (1 / np.array(self.future_days))).T
        strategy_long_val = np.nancumprod(strategy_long_ret, axis=1)
        #strategy_val = strategy_long_val - self.future_bench_val
        strategy_ret = strategy_long_ret - self.future_bench_ret
        strategy_val = np.nancumprod(1 + strategy_ret, axis=1)
        strategy_excess_gain = (strategy_long_val[:, -1] ** (244 / strategy_long_val.shape[1]) -
                                self.future_bench_val[:, -1] ** (244 / self.future_bench_val.shape[1]))
        strategy_mdd = (1 - strategy_val / np.maximum.accumulate(strategy_val, axis=1)).max(axis=1)

        strategy_win_rate = (strategy_ret > 0).sum(axis=1) / ((strategy_ret > 0).sum(axis=1) + (strategy_ret < 0).sum(axis=1))
        strategy_earn_loss = - (np.ma.array(strategy_ret, mask=(strategy_ret <= 0) | np.isnan(strategy_ret)).mean(axis=1) /
                                np.ma.array(strategy_ret, mask=(strategy_ret >= 0) | np.isnan(strategy_ret)).mean(axis=1)).data
        strategy_IR = strategy_excess_gain / np.nanstd(strategy_ret, axis=1) / (244 ** 0.5)
        strategy_result = pd.DataFrame(
            np.c_[strategy_excess_gain, strategy_turn, strategy_mdd, strategy_win_rate, strategy_earn_loss, strategy_IR],
            columns=['excess_ret', 'turn', 'mdd', 'win_rate', 'earn_loss', 'IR'],
            index=pd.Index(self.future_days, name='future'))

        self.bench_ind_stk_num = bench_ind_stk_num
        self.strategy_pool = strategy_pool
        self.buy_turn = buy_turn
        self.sell_turn = sell_turn
        self.strategy_long_ret = strategy_long_ret - 1
        self.strategy_ret = strategy_ret
        self.strategy_val = strategy_val
        return strategy_result

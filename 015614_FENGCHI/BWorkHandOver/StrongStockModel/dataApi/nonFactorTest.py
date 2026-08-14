import numba
import bottleneck
import numpy as np
import pandas as pd
from dataApi.getData import get_daily_1factor, get_modified_ind_mv
from dataApi.stockList import clean_stock_list
from dataApi.tradeDate import get_date_range, get_pre_trade_date, get_sub_date_index

def winsorize(arr, axis=-1):

    arr = arr.swapaxes(0, axis).astype(float)
    arr_nan = np.isnan(arr)
    median = np.nanmedian(arr, axis=0)
    arr[(np.sum(arr == median, axis=0) / (~arr_nan).sum(axis=0) >= 0.5) & (arr == median)] = np.nan
    arr_nan = np.isnan(arr)
    median = np.nanmedian(arr, axis=0)
    mad = np.nanmedian(np.abs(arr - median), axis=0)
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

def stats_range(date_index, date_list):

    date_list = np.asanyarray(date_list)
    date_index = np.asanyarray(date_index + [len(date_list)])
    start = date_list[date_index[:-1]]
    end = date_list[date_index[1:] - 1]
    return start, end

def stats_mean(arr, date_index, axis=-1):

    arr = arr.copy().swapaxes(0, axis)
    arr[~ np.isfinite(arr)] = 0

    cx = np.add.reduceat(arr, date_index)
    n = np.add.reduceat(arr != 0, date_index)

    return cx / n

def stats_ret(arr, date_index, axis=-1):

    arr = arr.copy().swapaxes(0, axis)
    arr[~ np.isfinite(arr)] = 0

    exist = arr != 0
    win = arr > 0
    lose = arr < 0

    win_gain = arr * win
    lose_loss = - arr * lose

    cx = np.add.reduceat(arr, date_index)
    cx2 = np.add.reduceat(arr ** 2, date_index)
    n = np.add.reduceat(exist, date_index)

    win_n = np.add.reduceat(win, date_index)
    lose_n = np.add.reduceat(lose, date_index)

    win_cx = np.add.reduceat(win_gain, date_index)
    loss_cx = np.add.reduceat(lose_loss, date_index)

    mean = cx / n * 244
    std = np.sqrt(cx2 / (n - 1) - cx ** 2 / (n * (n - 1))) * 244 ** 0.5
    sp = mean / std
    win_rate = win_n / n
    gain_loss = (win_cx / win_n) / (loss_cx / lose_n)

    return mean, std, sp, win_rate, gain_loss

def stats_mdd(arr, date_index, date_list, axis=-1):

    arr = arr.copy().swapaxes(0, axis)
    arr[~ np.isfinite(arr)] = 0
    n = np.add.reduceat(arr != 0, date_index).max()
    _arr = np.zeros((n, len(date_index)) + arr.shape[1:])

    for i, i_start in enumerate(date_index):
        i_end = arr.shape[0] if i == len(date_index) - 1 else date_index[i+1]
        length = i_end - i_start
        _arr[:length, i] = arr[i_start : i_end]

    np.cumsum(_arr, axis=0, out=_arr)
    arr = np.maximum.accumulate(_arr, axis=0)
    dd = arr - _arr

    mdd = np.max(dd, axis=0)
    mdd_end = np.argmax(dd, axis=0)
    mdd_start = arr[(mdd_end,) + tuple(np.arange(arr.shape[x])[(None,) * x + (slice(None),) + (None,) * (
            arr.ndim - x - 1)] for x in range(1, arr.ndim))][0]

    mdd_start = ((_arr == mdd_start).swapaxes(0, -1) * np.arange(_arr.shape[0])).swapaxes(0, -1)
    mdd_start[mdd_start > mdd_end] = 0
    mdd_start = mdd_start.max(axis=0)

    mdd_duration = mdd_end - mdd_start

    mdd_start = np.asanyarray(date_list)[(mdd_start.swapaxes(0, -1) + np.asanyarray(date_index)).swapaxes(0, -1)]
    mdd_end = np.asanyarray(date_list)[(mdd_end.swapaxes(0, -1) + np.asanyarray(date_index)).swapaxes(0, -1)]

    return mdd, mdd_duration, mdd_start, mdd_end

class NonFactorTest(object):


    def __init__(self, start_date=20160104, end_date=20181228, stock_pool='ALL', future_days=10,
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
        future[np.arange(future_date_num)[:, None, None], ~stock_pool.values.astype(bool)] = np.nan
        future_mask = np.isnan(future)
        stock_pool_num = len(code_list)

        ind, mv = get_modified_ind_mv(date_list, code_list, ind_type)

        future_bench = get_daily_1factor(price_type, price_raw_dates, [bench], type='bench')
        future_bench = np.concatenate(
            tuple(np.atleast_2d(future_bench.pct_change(x).shift(-x).values) for x in future_days),
            axis=1).T[:, :-future_days_max]
        future_bench = ((1 + future_bench.T) ** (1 / np.array(future_days))).T - 1
        future_bench_val = np.nancumsum(future_bench, axis=1)

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
        self.future_bench = future_bench
        self.future_bench_val = future_bench_val
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

        factor_repeat = factor[None, :, :].repeat(self.future_date_num, axis=0)
        factor_repeat[self.future_mask] = np.nan
        factor_rank = bottleneck.nanrankdata(factor_repeat, axis=2)
        mask = np.isnan(factor_rank)
        valid_num = self.stock_pool_num - mask.sum(axis=2)

        future_repeat = self.future.copy()
        future_repeat[mask] = np.nan
        future_rank = bottleneck.nanrankdata(future_repeat, axis=2)

        self.factor = factor
        self.factor_repeat = factor_repeat
        self.future_repeat = future_repeat
        self.factor_rank = factor_rank
        self.future_rank = future_rank
        self.valid_num = valid_num
        self.mask = mask

    def calc_ic(self):

        cxy = np.nansum(self.factor_repeat * self.future_repeat, axis=2)
        cx2 = np.nansum(self.factor_repeat ** 2, axis=2)
        cy2 = np.nansum(self.future_repeat ** 2, axis=2)
        cx = np.nansum(self.factor_repeat, axis=2)
        cy = np.nansum(self.future_repeat, axis=2)
        ic = ((self.valid_num * cxy - cx * cy) /
                   np.sqrt((self.valid_num * cx2 - cx ** 2) * (self.valid_num * cy2 - cy ** 2)))
        self.ic = ic

    def calc_rank_ic(self):

        cxy = np.nansum(self.factor_rank * self.future_rank, axis=2)
        cx2 = np.nansum(self.factor_rank ** 2, axis=2)
        cy2 = np.nansum(self.future_rank ** 2, axis=2)
        cx = np.nansum(self.factor_rank, axis=2)
        cy = np.nansum(self.future_rank, axis=2)
        rank_ic = ((self.valid_num * cxy - cx * cy) /
                   np.sqrt((self.valid_num * cx2 - cx ** 2) * (self.valid_num * cy2 - cy ** 2)))
        self.rank_ic = rank_ic

    def _calc_group_ret(self, groups=10):

        factor_group = np.ceil(self.factor_rank.transpose(2, 0, 1) / self.valid_num * groups).transpose(1, 2, 0)
        future_group = np.c_['0,3', tuple(np.ma.array(self.future, mask=self.mask | (factor_group != x))
                                          .mean(axis=2).data for x in range(1, groups + 1))]
        future_group = ((future_group.transpose(0, 2, 1) + 1) ** (1 / np.array(self.future_days))).transpose(2, 1, 0) - 1

        future_group_rank = bottleneck.nanrankdata(future_group, axis=2) - (groups + 1) / 2
        sequence = np.arange(1, groups + 1) - (groups + 1) / 2
        group_ic = ((future_group_rank * sequence).sum(axis=2) /
                    np.sqrt((future_group_rank ** 2).sum(axis=2) * (sequence ** 2).sum()))

        if np.all(np.nanmean(group_ic, axis=1) < 0):
            group_top = 1
        elif np.all(np.nanmean(group_ic, axis=1) > 0):
            group_top = groups
        else:
            raise ValueError("You are so boring to waste my time to test an ineffective factor !")

        long_short = future_group[..., group_top - 1] - future_group[..., groups - group_top]
        future_top = future_group[..., group_top - 1]
        active_gross_top = future_top - self.future_bench
        top_pool = (factor_group == group_top).astype(float)
        top_pool_num = top_pool.sum(axis=2)

        turn_top = tuple(np.abs(top_pool[x, self.future_days[x]:] - top_pool[x, :-self.future_days[x]]).sum(axis=1) /
                         (top_pool[x, self.future_days[x]:].sum(axis=1) + top_pool[x, :-self.future_days[x]].sum(axis=1))
                         / self.future_days[x] for x in range(self.future_date_num))
        turn_top = tuple(np.pad(turn_top[x], ((self.future_days[x], 0),), mode='constant', constant_values=np.nanmean(
            turn_top[x][:self.future_days[x]])) for x in range(self.future_date_num))
        turn_top = np.r_['0,2', turn_top]

        self.group_ic = group_ic
        self.long_short = long_short
        self.future_top = future_top
        self.top_pool = top_pool
        self.top_pool_num = top_pool_num
        self.active_gross_top = active_gross_top
        self.turn_top = turn_top

    def calc_group_ret(self, groups=10, fee=0.002):

        if not hasattr(self, 'active_gross_top') or not hasattr(self, 'turn_top'):
            self._calc_group_ret(groups=groups)

        self.active_net_top = self.active_gross_top - fee * self.turn_top

    def _calc_strategy_ret(self, strategy_stock_num=200):

        bench_ind_stk_num = np.round(self.bench_ind_wgt * strategy_stock_num)

        strategy_pool = np.any(np.r_['0,3', tuple(bottleneck.nanrankdata(np.ma.filled(np.ma.array(
            -self.factor, mask=~self.ind[x], fill_value=np.nan)), axis=1).T <= bench_ind_stk_num[x]
                                                  for x in range(self.ind.shape[0]))], axis=0).T
        strategy_pool_num = strategy_pool.sum(axis=1)

        _pool = strategy_pool.astype(float)
        turn_strategy = tuple(np.abs(_pool[self.future_days[x]:] - _pool[:-self.future_days[x]]).sum(
            axis=1) / (_pool[self.future_days[x]:].sum(axis=1) + _pool[self.future_days[x]:].sum(
            axis=1)) / self.future_days[x] for x in range(self.future_date_num))
        turn_strategy = tuple(np.pad(turn_strategy[x], ((self.future_days[x], 0),), mode='constant',
                                     constant_values=np.nanmean(turn_strategy[x][:self.future_days[x]]))
                              for x in range(self.future_date_num))
        turn_strategy = np.r_['0,2', turn_strategy]

        future_strategy = self.future.copy()
        future_strategy[:, ~strategy_pool] = np.nan
        future_strategy = np.nanmean(future_strategy, axis=2)
        future_strategy = ((future_strategy.T + 1) ** (1 / np.array(self.future_days))).T - 1

        active_gross_strategy = future_strategy - self.future_bench

        self.strategy_pool = strategy_pool
        self.strategy_pool_num = strategy_pool_num
        self.future_strategy = future_strategy
        self.active_gross_strategy = active_gross_strategy
        self.turn_strategy = turn_strategy

    def calc_strategy_ret(self, strategy_stock_num=200, fee=0.002):

        if not hasattr(self, 'active_gross_strategy') or not hasattr(self, 'turn_strategy'):
            self._calc_strategy_ret(strategy_stock_num=strategy_stock_num)

        self.active_net_strategy = self.active_gross_strategy - fee * self.turn_strategy

    def test_factor(self, period='Y', IC=True, rank_IC=True, groups=10, group_IC=True, long_short_ret=True,
                    long_short_mdd=True, fee=0.002, top_num=True, top_turn=True, top_ret=True, top_mdd=True,
                    strategy_stock_num=200, strategy_num=True, strategy_turn=True, strategy_ret=True,
                    strategy_mdd=True, redo=False, output=False, file=None):

        date_index = get_sub_date_index(self.date_list, period)
        start, end = stats_range(date_index, self.date_list)

        if IC and (not hasattr(self, 'ic') or redo):
            self.calc_ic()

        if rank_IC and (not hasattr(self, 'ic') or redo):
            self.calc_rank_ic()

        if (group_IC or long_short_ret or long_short_mdd or top_num or top_turn or top_ret or top_mdd) and (
                not hasattr(self, 'group_ic') or redo):
            self._calc_group_ret(groups=groups)
            if (top_ret or top_mdd) and (not hasattr(self, 'active_net_top') or redo):
                self.calc_group_ret(groups=groups, fee=fee)

        if (strategy_num or strategy_turn or strategy_ret or strategy_mdd) and (
                not hasattr(self, 'strategy_pool_num') or redo):
            self._calc_strategy_ret(strategy_stock_num=strategy_stock_num)
            if (strategy_ret or strategy_mdd) and (not hasattr(self, 'active_net_strategy') or redo):
                self.calc_strategy_ret(strategy_stock_num=strategy_stock_num, fee=fee)

        stats = {}

        if IC:
            stats['IC'], _, stats['ICIR'], stats['IC_pos'], _ = stats_ret(self.ic, date_index)
            stats['IC'] /= 244

        if rank_IC:
            stats['rank_IC'], _, stats['rank_ICIR'], stats['rank_IC_pos'], _ = stats_ret(self.ic, date_index)
            stats['rank_IC'] /= 244

        if group_IC:
            stats['group_IC'], _, stats['group_ICIR'], stats['group_IC_pos'], _ = stats_ret(self.ic, date_index)
            stats['group_IC'] /= 244

        if long_short_ret:
            (stats['long_short_ret'], stats['long_short_std'], stats['long_short_sp'], stats['long_short_win_rate'],
             stats['long_short_gain_loss']) = stats_ret(self.long_short, date_index)

        if long_short_mdd:
            (stats['long_short_mdd'], stats['long_short_mdd_duration'], stats['long_short_mdd_start'],
             stats['long_short_mdd_end']) = stats_mdd(self.long_short, date_index, self.date_list)

        if top_num:
            stats['top_num'] = stats_mean(self.top_pool_num, date_index)

        if top_turn:
            stats['top_turn'] = stats_mean(self.turn_top, date_index)

        if top_ret:
            (stats['top_active'], stats['top_std'], stats['top_sp'], stats['top_win_rate'], stats['top_gain_loss']
             ) = stats_ret(self.active_net_top, date_index)

        if top_mdd:
            stats['top_mdd'], stats['top_mdd_duration'], stats['top_mdd_start'], stats['top_mdd_end'] = stats_mdd(
                self.active_net_top, date_index, self.date_list)

        if strategy_num:
            stats['strategy_num'] = stats_mean(self.strategy_pool_num, date_index)[:,
                                    None].repeat(self.future_date_num, axis=1)

        if strategy_turn:
            stats['strategy_turn'] = stats_mean(self.turn_strategy, date_index)

        if strategy_ret:
            (stats['strategy_active'], stats['strategy_std'], stats['strategy_sp'], stats['strategy_win_rate'],
             stats['strategy_gain_loss']) = stats_ret(self.active_net_strategy, date_index)

        if strategy_mdd:
            (stats['strategy_mdd'], stats['strategy_mdd_duration'], stats['strategy_mdd_start'],
             stats['strategy_mdd_end']) = stats_mdd(self.active_net_strategy, date_index, self.date_list)

        columns = pd.MultiIndex.from_arrays([start, end], names=['start_date', 'end_date'])
        index = list(stats.keys())
        values = np.r_['0,3', tuple(stats.values())]
        df_dict = {self.future_days[i] : pd.DataFrame(values[..., i], index=index, columns=columns)
                   for i in range(self.future_date_num)}

        if output:
            with pd.ExcelWriter(file) as writer:
                for key in df_dict.keys():
                    df_dict[key].to_excel(writer, 'future%d' % key)
            self.test_result = df_dict
        else:
            return df_dict


if __name__ == '__main__':

    compound_address = '/data/user/hanxu/model/compound/'
    middle_address = '/data/user/hanxu/model/temp20200527/'

    compound = pd.read_hdf('%s%s' % (compound_address, 'compound74'), 'compound74')
    stock_pool = pd.read_hdf('%s%s.h5' % (middle_address, 'stock_pool'), 'stock_pool')

    future_days = 5
    compound = pd.read_hdf('%s%s' % (compound_address, 'compound74'), 'compound74')
    self.test_factor(redo=True, output=True, file='/data/user/hanxu/ddd.xlsx')
    self = NonFactorTest(start_date=20140709, end_date=20181228, bench='HS300',
                         future_days=future_days, pre_neutralize=True)
    self.load_factor(compound, diy_address='/data/group/800319/', neutral=True)
    import time
    t = time.time()
    time.time() - t
    self.calc_ic()
    self.calc_rank_ic()
    self.calc_group_ret()
    self.calc_strategy_ret()

    result = pd.concat([nft.calc_ic(), nft.calc_group_ret(), nft.calc_strategy_ret(buy_fee=0.000, sell_fee=0.002)],
                       axis=1)
    # print((factor_multi_period_weight != 0).sum(axis=1).mean())
    result[['IC', 'IC_IR', 'ic_group', 'top_excess_ret', 'excess_ret', 'turn', 'mdd', 'IR']].stack()

    np.add.reduceat([1,2,3], [2])


    aaa = pd.read_hdf('/data/group/800319/error_data.h5', key='error_data')

    factor = pd.read_hdf(address + 'Elastic_y3.h5', 'Elastic_y3').astype('float64')
    assert factor.iloc[-1].notnull().any()
    factor = factor.dropna(how='all')
    date_list = factor.index.to_list()

    nft = NonFactorTest(start_date=date_list[0], end_date=date_list[-1], pre_neutralize=True)
    nft.load_factor(factor, neutral=True)
    strategy_ret = nft.calc_strategy_ret()
    code_list = nft.stock_pool.columns.to_list()
    from dataApi.indName import sw_level1, sw_level2

    ind = get_daily_1factor('SW1', date_list, code_list).values
    ind2 = get_daily_1factor('SW2', date_list, code_list).values
    ind[ind == 6134] = ind2[ind == 6134]
    ind_codes = list(sw_level1.keys())
    ind_codes.remove(6134)
    ind_codes += [613401, 613402, 613403]
    sw_level = sw_level1.copy()
    sw_level.update(sw_level2)
    sw_level1 = sw_level
    ind_names = [sw_level1[x] for x in ind_codes]

    ind_weight = pd.DataFrame((nft.bench_ind_stk_num / nft.bench_ind_stk_num.sum(axis=0)).T,
                              index=date_list, columns=ind_names).sort_index(axis=1)

    bench_percent = pd.DataFrame(np.r_['0,2', ((get_daily_1factor('SZ50_exdiv_weight', date_list, code_list).values > 0)
                                               & nft.strategy_pool).sum(axis=1),
                                       tuple(((pd.read_hdf('/data/group/800319/junkData/daily/common_stock_list.h5', x)
                                               .reindex(date_list, code_list).values > 0) & nft.strategy_pool).sum(axis=1)
                                             for x in ('HS300', 'ZZ500', 'ZZ1000'))] / nft.strategy_pool.sum(axis=1),
                                 index=['SZ50', 'HS300', 'ZZ500', 'ZZ1000'], columns=date_list).T
    bench_percent['NO1800'] = 1 - bench_percent[['HS300', 'ZZ500', 'ZZ1000']].sum(axis=1)

    strategy_pool = pd.DataFrame(nft.strategy_pool, index=date_list, columns=code_list).replace(False, np.nan).stack()
    strategy_pool = pd.DataFrame(ind, index=date_list, columns=code_list).stack().reindex(
        strategy_pool.index).map(int).map(sw_level1).reset_index()
    strategy_pool.columns = ['date', 'code', 'ind']
    strategy_pool = strategy_pool.sort_values(['date', 'ind', 'code']).set_index('date')

    with pd.ExcelWriter('/data/user/hanxu/model/Elastic_y3.xlsx') as writer:

        pd.DataFrame().to_excel(writer, 'logic')
        strategy_ret.to_excel(writer, 'perform')
        ind_weight.to_excel(writer, 'ind_weight')
        bench_percent.to_excel(writer, 'index_weight')
        strategy_pool.to_excel(writer, 'stock')

import pandas as pd
import numpy as np
import cvxpy as cp
from tqdm import tqdm
from dataApi.nonFactorTest import stats_ret, stats_mdd, stats_range
from dataApi.tradeDate import get_pre_trade_date, get_date_range, get_sub_date_index
from dataApi.dividend import getEXRightDividend
from dataApi.getData import get_daily_1factor

def prepare_ind(ind_type='SW', ind_modify=False, date_list=None, code_list=None, ind_address=None):

    if ind_modify:

        if ind_type == 'SW1':
            ind = get_daily_1factor('SW1', date_list, code_list, diy_address=ind_address)
            ind2 = get_daily_1factor('SW2', date_list, code_list, diy_address=ind_address)
            ind[ind == 6134] = ind2[ind == 6134]
            ind_codes = np.unique(ind)
            ind_codes = sorted(list(ind_codes[np.isfinite(ind_codes)]))

        elif ind_type == 'CITICS1':
            ind = get_daily_1factor('CITICS1', date_list, code_list, diy_address=ind_address).replace(np.nan, 'nan')
            ind2 = get_daily_1factor('CITICS2', date_list, code_list, diy_address=ind_address).replace(np.nan, 'nan')
            ind[ind == 'b10m'] = ind2[ind == 'b10m']
            ind_codes = np.unique(ind)
            ind_codes = sorted(list(ind_codes[ind_codes != 'nan']))

        else:
            raise ValueError("Only SW1 or CITICS1 can be modified.")

    else:

        ind = get_daily_1factor(ind_type, date_list, code_list, diy_address=ind_address)
        if np.dtype('O') in np.unique(ind.dtypes):
            ind = ind.replace(np.nan, 'nan')
            ind_codes = np.unique(ind)
            ind_codes = sorted(list(ind_codes[ind_codes != 'nan']))
        else:
            ind_codes = np.unique(ind)
            ind_codes = sorted(list(ind_codes[np.isfinite(ind_codes)]))

    return ind, ind_codes

def prepare_factor(factor):

    factor = factor.rank(axis=1, pct=True) * 2 - 1
    return factor

def stats_result(sr, period='Y'):

    date_list = sr.index.to_list()
    arr = sr.values
    date_index = get_sub_date_index(date_list, period)
    start, end = stats_range(date_index, date_list)
    mean, std, sp, win_rate, gain_loss = stats_ret(arr, date_index)
    mdd, mdd_duration, mdd_start, mdd_end = stats_mdd(arr, date_index, date_list)
    values = np.r_['0,2', mean, std, sp, win_rate, gain_loss, mdd, mdd_duration, mdd_start, mdd_end]
    index = ['ret', 'std', 'sp', 'win_rate', 'gain_loss', 'mdd', 'mdd_duration', 'mdd_start', 'mdd_end']
    columns = pd.MultiIndex.from_arrays([start, end], names=['start_date', 'end_date'])
    df = pd.DataFrame(values, index, columns)
    return df

class portfolioOptimization(object):

    def __init__(self, config):

        keys = [
             'factor_address',
             'stock_pool_address',
             'limitation_address',
             'ind_address',
             'real_group_address',
             'target_group_address',
             'optimal_group_address',
             'simulate_group_address',
             'adjust_group_address',
             'start_date',
             'end_date',
             'factor_name',
             'bench',
             'ind_type',
             'ind_modify',
             'amt_limit_days',
             'amt_limit_ratio',
             'period',
             'money',
             'fee_buy',
             'fee_sell',
             's_max',
             's_min',
             's_b_abs_max',
             's_b_abs_min',
             's_b_rel_max',
             's_b_rel_min',
             'g_max',
             'g_min',
             'g_b_abs_max',
             'g_b_abs_min',
             'g_b_rel_max',
             'g_b_rel_min',
             'mv_max',
             'mv_min',
             'tho'
        ]

        for key in keys:
            setattr(self, key, config[key])

        money_scale = 1.0 * 10 ** round(np.log10(self.money))
        money0 = self.money / money_scale

        date_list = get_date_range(get_pre_trade_date(self.start_date), self.end_date)
        stock_list = get_daily_1factor('stock_list', date_list)
        code_list = stock_list.columns.to_list()

        pause = get_daily_1factor('pause', date_list, code_list) == True
        bench_weight = get_daily_1factor('%s_exdiv_weight' % self.bench, date_list, code_list).fillna(0)
        mv = np.log(get_daily_1factor('mkt_cap_ard', date_list, code_list)).fillna(0)
        twap = get_daily_1factor('twap', date_list, code_list).fillna(0)
        pre_close = get_daily_1factor('pre_close', date_list, code_list).fillna(0)
        share_ratio = getEXRightDividend().pivot('date', 'code', 'shareRatio').reindex(date_list, code_list).fillna(0)
        ind, ind_codes = prepare_ind(self.ind_type, self.ind_modify, date_list, code_list)
        stock_pool = get_daily_1factor('stock_pool', date_list, code_list, diy_address=self.stock_pool_address) == True
        factor = prepare_factor(get_daily_1factor(self.factor_name, date_list, code_list,
                                                  diy_address=self.factor_address)[stock_pool])

        amt = get_daily_1factor('amt', code_list=code_list) * 1e3
        amt_roll = amt.replace(0, np.nan).apply(
            lambda x: x.dropna().rolling(self.amt_limit_days).mean().reindex(date_list)).fillna(0)
        amt = amt.reindex(date_list)
        amt_roll[(~stock_list) | pause] = 0
        amt_roll *= self.amt_limit_ratio

        adjfactor = get_daily_1factor('adjfactor', date_list, code_list).fillna(0)
        close = get_daily_1factor('close', date_list, code_list).fillna(0)
        bench_ret = get_daily_1factor('close', date_list, [self.bench], type='bench').iloc[:, 0].pct_change()

        if self.limitation_address is None:
            stock_limit = pd.DataFrame(
                columns=['s_max', 's_min', 's_b_abs_max', 's_b_abs_min', 's_b_rel_max', 's_b_rel_min'])
        else:
            stock_limit = pd.read_excel('%s/portfolioLimitation.xlsx' % self.limitation_address,
                                        parse_cols='B:H', skiprows=1, index_col=0).dropna(how='all')
        stock_limit.index = stock_limit.index.map(int)
        stock_limit_fill = {'s_max': self.s_max, 's_min': self.s_min, 's_b_abs_max': self.s_b_abs_max, 's_b_abs_min':
            self.s_b_abs_min, 's_b_rel_max': self.s_b_rel_max, 's_b_rel_min': self.s_b_rel_min}
        stock_limit = stock_limit.reindex(code_list).fillna(stock_limit_fill)

        if self.limitation_address is None:
            ind_limit = pd.DataFrame(columns=['g_max', 'g_min', 'g_b_abs_max',
                                              'g_b_abs_min', 'g_b_rel_max', 'g_b_rel_min'])
        else:
            ind_limit = pd.read_excel('%s/portfolioLimitation.xlsx' % self.limitation_address,
                                      parse_cols='K:Q', skiprows=1, index_col=0).dropna(how='all')
        ind_limit_fill = {'g_max': self.g_max, 'g_min': self.g_min, 'g_b_abs_max': self.g_b_abs_max, 'g_b_abs_min':
            self.g_b_abs_min, 'g_b_rel_max': self.g_b_rel_max, 'g_b_rel_min': self.g_b_rel_min}
        ind_limit = ind_limit.reindex(ind_codes).fillna(ind_limit_fill)

        if self.real_group_address is None:
            real_group = pd.DataFrame(0, index=date_list, columns=code_list)
        else:
            real_group = get_daily_1factor('real_group', date_list, code_list,
                                           diy_address=self.real_group_address).fillna(0)

        if self.target_group_address is None:
            target_group = pd.DataFrame(0, index=date_list, columns=code_list)
        else:
            target_group = get_daily_1factor('target_group', date_list, code_list,
                                             diy_address=self.target_group_address).fillna(0)

        if self.optimal_group_address is None:
            optimal_group = pd.DataFrame(0, index=date_list, columns=code_list)
        else:
            optimal_group = get_daily_1factor('optimal_group', date_list, code_list,
                                              diy_address=self.optimal_group_address).fillna(0)

        if self.simulate_group_address is None:
            simulate_group = pd.DataFrame(0, index=date_list, columns=code_list)
        else:
            simulate_group = get_daily_1factor('simulate_group', date_list, code_list,
                                               diy_address=self.simulate_group_address).fillna(0)

        if self.adjust_group_address is None:
            adjust_group = pd.DataFrame(0, index=date_list, columns=code_list)
        else:
            adjust_group = get_daily_1factor('adjust_group', date_list, code_list,
                                              diy_address=self.adjust_group_address).fillna(0)

        simulate_finish_ratio = pd.Series(index=date_list)

        self.money_scale = money_scale
        self.money0 = money0
        self.date_list = date_list
        self.stock_list = stock_list
        self.code_list = code_list
        self.pause = pause
        self.bench_weight = bench_weight
        self.mv = mv
        self.close = close
        self.twap = twap
        self.pre_close = pre_close
        self.share_ratio = share_ratio
        self.ind = ind
        self.ind_codes = ind_codes
        self.stock_pool = stock_pool
        self.factor = factor
        self.amt = amt
        self.amt_roll = amt_roll
        self.adjfactor = adjfactor
        self.bench_ret = bench_ret
        self.stock_limit = stock_limit
        self.ind_limit = ind_limit
        self.real_group = real_group
        self.target_group = target_group
        self.optimal_group = optimal_group
        self.simulate_group = simulate_group
        self.adjust_group = adjust_group
        self.simulate_finish_ratio = simulate_finish_ratio

    def set_last_group(self, last_date, mode):

        if mode == 'reset':
            self._last_group = pd.Series(0., index=self.code_list)

        elif mode == 'optimal':
            if self.optimal_group.loc[last_date].sum() == 0:
                print('no optimal group %s provided, using reset mode instead.' % last_date)
                self.set_last_group(last_date, 'reset')
            else:
                self._last_group = self.optimal_group.loc[last_date]

        elif mode == 'simulate':
            if self.simulate_group.loc[last_date].sum() == 0:
                print('no simulate group %s provided, using optimal mode instead.' % last_date)
                self.set_last_group(last_date, 'optimal')
            else:
                self._last_group = self.simulate_group.loc[last_date]

        elif mode == 'target':
            if self.target_group.loc[last_date].sum() == 0:
                print('no target group %s provided, using simulate mode instead.' % last_date)
                self.set_last_group(last_date, 'simulate')
            else:
                self._last_group = self.target_group.loc[last_date]

        elif mode == 'real':
            if self.real_group.loc[last_date].sum() == 0:
                print('no real group %s provided, using target mode instead.' % last_date)
                self.set_last_group(last_date, 'target')
            else:
                self._last_group = self.real_group.loc[last_date]

        else:
            raise ValueError("mode must be reset, optimal, simulate, target or real.")

        self._last_date = last_date

    def calc_opt_group(self, date):

        _opt_date = date
        _pre_date = get_pre_trade_date(_opt_date)

        _share_ratio = self.share_ratio.loc[self._last_date : date].iloc[1:]
        _last_group_exdiv = self._last_group * (_share_ratio + 1).prod()

        _pre_close = self.pre_close.loc[_opt_date]
        _amt_roll = self.amt_roll.loc[_pre_date] / self.money_scale
        _bench_weight = self.bench_weight.loc[_pre_date]
        _ind = self.ind.loc[_pre_date]
        _factor = self.factor.loc[_pre_date].fillna(-1.)
        _mv = self.mv.loc[_pre_date]

        _val_last = _last_group_exdiv * _pre_close / self.money_scale
        _val_max = _val_last + _amt_roll
        _val_min = np.fmax(_val_last - _amt_roll, 0)

        _stock_max = np.fmin(np.fmax(_bench_weight + self.stock_limit['s_b_abs_max'], (
                1 + self.stock_limit['s_b_rel_max']) * _bench_weight), self.stock_limit['s_max'])
        _stock_max = np.fmin(_val_max, _stock_max * self.money0)

        _stock_min = np.fmax(np.fmin(_bench_weight + self.stock_limit['s_b_abs_min'], (
                1 + self.stock_limit['s_b_rel_min']) * _bench_weight), self.stock_limit['s_min'])
        _stock_min = np.fmax(_val_min, _stock_min * self.money0)

        _bench_ind = pd.concat([_bench_weight.rename('wgt'), _ind.rename('ind')], axis=1).replace(
            'nan', np.nan).dropna().groupby('ind')['wgt'].sum().reindex(self.ind_codes).fillna(0)

        _X_ind = np.r_['0,2', tuple((_ind == x).values for x in self.ind_codes)]
        _ind_max = np.fmin(np.fmax(_bench_ind + self.ind_limit['g_b_abs_max'], (
                1 + self.ind_limit['g_b_rel_max']) * _bench_ind), self.ind_limit['g_max']) * self.money0

        _ind_min = np.fmax(np.fmin(_bench_ind + self.ind_limit['g_b_abs_min'], (
                1 + self.ind_limit['g_b_rel_min']) * _bench_ind), self.ind_limit['g_min']) * self.money0

        w = cp.Variable(len(self.code_list))
        obj = cp.Maximize(_factor.values @ w - self.tho * cp.sum(cp.abs(w - _val_last.values)))
        cons = [w >= _stock_min.values, w <= _stock_max.values, cp.sum(w) == self.money0,
                _X_ind @ w >= _ind_min.values, _X_ind @ w <= _ind_max.values,
                _mv.values @ (w - _bench_weight.values * self.money0) >= self.mv_min * self.money0,
                _mv.values @ (w - _bench_weight.values * self.money0) <= self.mv_max * self.money0]
        prob = cp.Problem(obj, cons)
        prob.solve('ECOS', verbose=False)
        if w.value is None:
            raise Exception('%s：约束条件冲突，组合优化的解无效' % date)
        w = w.value * self.money_scale
        w[w < 1.] = 0.
        _vol_opt = pd.Series(w / _pre_close, index=self.code_list).replace([np.inf, -np.inf, np.nan], 0.)
        _vol_adj = round(_vol_opt - _last_group_exdiv, -2)
        _vol_target = _vol_adj + _last_group_exdiv

        self.optimal_group.loc[_opt_date] = _vol_target
        self.adjust_group.loc[_opt_date] = _vol_adj

        self._opt_date = _opt_date
        self._pre_date = _pre_date
        self._share_ratio = _share_ratio
        self._last_group_exdiv = _last_group_exdiv
        self._pre_close = _pre_close
        self._amt_roll = _amt_roll
        self._bench_weight = _bench_weight
        self._ind = _ind
        self._factor = _factor
        self._mv = _mv
        self._val_last = _val_last
        self._val_max = _val_max
        self._val_min = _val_min
        self._stock_max = _stock_max
        self._stock_min = _stock_min
        self._bench_ind = _bench_ind
        self._X_ind = _X_ind
        self._ind_max = _ind_max
        self._ind_min = _ind_min
        self._vol_opt = _vol_opt
        self._vol_adj = _vol_adj
        self._vol_target = _vol_target

    def calc_simulate_group(self, date):

        if self.adjust_group.loc[date].sum() == 0:
            print("no adjust group found, we calculate it first.")
            self.calc_opt_group(date)

        _amt = self.amt.loc[date]
        _twap = self.twap.loc[date]
        _close = self.close.loc[date]
        _bench_ret = self.bench_ret.loc[date]
        _vol_adj = self.adjust_group.loc[date]
        _bench_ret = self.bench_ret.loc[date]

        _real_max_vol = (_amt * self.amt_limit_ratio / _twap).replace([np.inf, -np.inf, np.nan], 0.)
        _vol_simulate = np.clip(_vol_adj, -_real_max_vol, _real_max_vol)
        _finish_ratio = _vol_simulate.dot(_twap) / _vol_adj.dot(_twap)
        _simulate_gain = (self._last_group_exdiv.dot(_close - self._pre_close) + _vol_simulate.dot(_close - _twap) -
                          np.fmax(_vol_simulate, 0).dot(_twap) * self.fee_buy +
                          np.fmin(_vol_simulate, 0).dot(_twap) * self.fee_sell)
        _simulate_size = (self._last_group_exdiv.dot(self._pre_close) + max(_vol_simulate.dot(_twap), 0))
        _simulate_ret = _simulate_gain / _simulate_size
        _simulate_active_ret = _simulate_ret - _bench_ret

        self.simulate_group.loc[date] = _vol_simulate + self._last_group_exdiv
        self.simulate_finish_ratio.loc[date] = _finish_ratio

        self._simulate_gain = _simulate_gain
        self._simulate_size = _simulate_size
        self._simulate_ret = _simulate_ret
        self._simulate_active_ret = _simulate_active_ret

    def single_tunnel_simulate(self):

        reset_date_list = self.date_list[1 :: self.period]
        simulate_ret = pd.Series(index=self.date_list[1:])
        simulate_active_ret = pd.Series(index=self.date_list[1:])

        for date in tqdm(reset_date_list):

            if date == self.date_list[1]:
                last_date = self.date_list[0]

            self.set_last_group(last_date, 'simulate')
            self.calc_opt_group(date)
            self.calc_simulate_group(date)

            simulate_ret[date] = self._simulate_ret
            simulate_active_ret[date] = self._simulate_active_ret

            next_date = min(self.end_date, get_pre_trade_date(date, - self.period + 1))
            addition_date_list = [x for x in self.date_list if date < x <= next_date]

            for _date in addition_date_list:

                self.simulate_group.loc[_date] = self.simulate_group.loc[get_pre_trade_date(_date)] * (
                        1 + self.share_ratio.loc[_date])
                simulate_ret.loc[_date] = (self.simulate_group.loc[_date].dot(self.close.loc[_date]) /
                                       self.simulate_group.loc[_date].dot(self.pre_close.loc[_date])) - 1
                simulate_active_ret.loc[_date] = simulate_ret.loc[_date] - self.bench_ret.loc[_date]

            last_date = date

        return simulate_ret, simulate_active_ret


if __name__ == '__main__':

    config = dict(

        factor_address='/data/user/015836/model/compound/',
        stock_pool_address='/data/user/015836/model/temp20200527/',
        limitation_address=None,
        ind_address=None,
        real_group_address=None,
        target_group_address=None,
        optimal_group_address=None,
        simulate_group_address=None,
        adjust_group_address=None,

        start_date=20181101,
        end_date=20181228,
        factor_name='compound106',
        bench='HS300',
        ind_type='SW1',
        ind_modify=True,

        amt_limit_days=5,
        amt_limit_ratio=0.25,

        period=1,
        money=2e8,

        fee_buy=0,
        fee_sell=0.002,

        s_max=1.,
        s_min=0.,
        s_b_abs_max=0.01,
        s_b_abs_min=-1.,
        s_b_rel_max=0.0,
        s_b_rel_min=-0.0,

        g_max=1.,
        g_min=0.,
        g_b_abs_max=0.01,
        g_b_abs_min=-0.01,
        g_b_rel_max=0.0,
        g_b_rel_min=-0.0,

        mv_max=0.3,
        mv_min=-0.3,
        tho=0.6,
    )

    self = portfolioOptimization(config)
    ret, active_ret = self.single_tunnel_simulate()
    ret_result = stats_result(ret)
    active_ret_result = stats_result(active_ret)
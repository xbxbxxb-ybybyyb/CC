import pandas as pd
import numpy as np
import cvxpy as cp
from dataApi.tradeDate import get_pre_trade_date, get_date_range
from dataApi.dividend import getEXRightDividend
from dataApi.getData import get_daily_1factor

factor_address = '/data/user/015836/model/compound/'
stock_pool_address = '/data/user/015836/model/temp20200527/'
limitation_address = None
real_group_address = None
optimal_group_address = None

start_date = 20150105
end_date = 20181228
factor_name = 'compound106'
bench = 'HS300'
ind_type = 'SW1'
ind_modify = True

amt_limit_days = 5
amt_limit_ratio = 0.25

s_max = 1
s_min = 0.
s_b_abs_max = 0.005
s_b_abs_min = -1.
s_b_rel_max = 0.0
s_b_rel_min = -0.0

g_max = 1
g_min = 0.
g_b_abs_max = 0.01
g_b_abs_min = -0.01
g_b_rel_max = 0.0
g_b_rel_min = -0.0

mv_max = 0.3
mv_min = -0.3
tho = 0.6

period = 5  # 调仓频率
money = 2e8 # 单通道规模

fee_buy = 0
fee_sell = 0.002

config = dict(

    factor_address = '/data/user/015836/model/compound/',
    stock_pool_address = '/data/user/015836/model/temp20200527/',
    limitation_address = None,
    ind_address = None,
    real_group_address = None,
    optimal_group_address = None,

    start_date = 20150105,
    end_date = 20181228,
    factor_name = 'compound106',
    bench = 'HS300',
    ind_type = 'SW1',
    ind_modify = True,

    amt_limit_days = 5,
    amt_limit_ratio = 0.25,

    period = 5,  # 调仓频率
    money = 2e8, # 单通道规模

    fee_buy = 0,
    fee_sell = 0.002,

    s_max=1.,
    s_min = 0.,
    s_b_abs_max = 0.005,
    s_b_abs_min = -1.,
    s_b_rel_max = 0.0,
    s_b_rel_min = -0.0,

    g_max=1.,
    g_min = 0.,
    g_b_abs_max = 0.01,
    g_b_abs_min = -0.01,
    g_b_rel_max = 0.0,
    g_b_rel_min = -0.0,
    
    mv_max = 0.3,
    mv_min = -0.3,
    tho = 0.6,
)

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



money_scale = 1.0 * 10 ** round(np.log10(money))
_money = money / money_scale

date_list = get_date_range(get_pre_trade_date(start_date), end_date)
stock_list = get_daily_1factor('stock_list', date_list)
code_list = stock_list.columns.to_list()
pause = get_daily_1factor('pause', date_list, code_list) == True
bench_weight = get_daily_1factor('%s_exdiv_weight' % bench, date_list, code_list).fillna(0)
mv = np.log(get_daily_1factor('mkt_cap_ard', date_list, code_list)).fillna(0)
close = get_daily_1factor('close', date_list, code_list).fillna(0)
twap = get_daily_1factor('twap', date_list, code_list).fillna(0)
pre_close = get_daily_1factor('pre_close', date_list, code_list).fillna(0)
share_ratio = getEXRightDividend().pivot('date', 'code', 'shareRatio').reindex(date_list, code_list).fillna(0)
ind, ind_codes = prepare_ind(ind_type, ind_modify, date_list, code_list)
stock_pool = get_daily_1factor('stock_pool', date_list, code_list, diy_address=stock_pool_address) == True
factor = prepare_factor(get_daily_1factor(factor_name, date_list, code_list, diy_address=factor_address)[stock_pool])

amt = get_daily_1factor('amt', code_list=code_list) * 1e3
amt_roll = amt.replace(0, np.nan).apply(lambda x: x.dropna().rolling(amt_limit_days).mean().reindex(date_list)).fillna(0)
amt = amt.reindex(date_list)
amt_roll[(~stock_list) | pause] = 0
amt_roll *= amt_limit_ratio

adjfactor = get_daily_1factor('adjfactor', date_list, code_list)
bench_ret = get_daily_1factor('close', date_list, [bench], type='bench').iloc[:, 0].pct_change()

if limitation_address is None:
    stock_limit = pd.DataFrame(columns=['s_max', 's_min', 's_b_abs_max', 's_b_abs_min', 's_b_rel_max', 's_b_rel_min'])
else:
    stock_limit = pd.read_excel('%s/portfolioLimitation.xlsx' % limitation_address,
                                parse_cols='B:H', skiprows=1, index_col=0).dropna(how='all')
stock_limit.index = stock_limit.index.map(int)
stock_limit_fill = {'s_max': s_max, 's_min': s_min, 's_b_abs_max': s_b_abs_max, 's_b_abs_min': s_b_abs_min,
                    's_b_rel_max': s_b_rel_max, 's_b_rel_min': s_b_rel_min}
stock_limit = stock_limit.reindex(code_list).fillna(stock_limit_fill)

if limitation_address is None:
    ind_limit = pd.DataFrame(columns=['g_max', 'g_min', 'g_b_abs_max', 'g_b_abs_min', 'g_b_rel_max', 'g_b_rel_min'])
else:
    ind_limit = pd.read_excel('%s/portfolioLimitation.xlsx' % limitation_address,
                                parse_cols='K:Q', skiprows=1, index_col=0).dropna(how='all')
ind_limit_fill = {'g_max': g_max, 'g_min': g_min, 'g_b_abs_max': g_b_abs_max, 'g_b_abs_min': g_b_abs_min,
                  'g_b_rel_max': g_b_rel_max, 'g_b_rel_min': g_b_rel_min}
ind_limit = ind_limit.reindex(ind_codes).fillna(ind_limit_fill)


#last_date = get_pre_trade_date(opt_date, period)  # 上个调仓日
# 情景1 新建仓
last_group = pd.Series(0., index=code_list)
###

opt_date = 20181010  # 调仓日
pre_date = get_pre_trade_date(opt_date)

_share_ratio = share_ratio.loc[opt_date]
_pre_close = pre_close.loc[opt_date]
_amt_roll = amt_roll.loc[pre_date] / money_scale
_bench_weight = bench_weight.loc[pre_date]
_ind = ind.loc[pre_date]
_factor = factor.loc[pre_date].fillna(-1.)
_mv = mv.loc[pre_date]
_last_group = last_group * (_share_ratio + 1)

val_last = _last_group * _pre_close / money_scale
val_max = val_last + _amt_roll
val_min = np.fmax(val_last - _amt_roll, 0)

stock_max = np.fmin(np.fmax(bench_weight.loc[pre_date] + stock_limit['s_b_abs_max'], (1 + stock_limit['s_b_rel_max'])
                            * bench_weight.loc[pre_date]), stock_limit['s_max'])
stock_max = np.fmin(val_max, stock_max * _money)

stock_min = np.fmax(np.fmin(_bench_weight + stock_limit['s_b_abs_min'], (1 + stock_limit['s_b_rel_min'])
                            * _bench_weight), stock_limit['s_min'])
stock_min = np.fmax(val_min, stock_min * _money)

bench_ind = pd.concat([_bench_weight.rename('wgt'), _ind.rename('ind')], axis=1).replace(
    'nan', np.nan).dropna().groupby('ind')['wgt'].sum().reindex(ind_codes).fillna(0)

X_ind = np.r_['0,2', tuple((_ind == x).values for x in ind_codes)]
ind_max = np.fmin(np.fmax(bench_ind + ind_limit['g_b_abs_max'], (1 + ind_limit['g_b_rel_max']) * bench_ind),
                  ind_limit['g_max']) * _money

ind_min = np.fmax(np.fmin(bench_ind + ind_limit['g_b_abs_min'], (1 + ind_limit['g_b_rel_min']) * bench_ind),
                  ind_limit['g_min']) * _money


w = cp.Variable(len(code_list))
obj = cp.Maximize(_factor.values @ w - tho * cp.sum(cp.abs(w - val_last.values)))
cons = [w >= stock_min.values, w <= stock_max.values, cp.sum(w) == _money,
        X_ind @ w >= ind_min.values, X_ind @ w <= ind_max.values,
        _mv.values @ (w - _bench_weight.values * _money) >= mv_min * _money,
        _mv.values @ (w - _bench_weight.values * _money) <= mv_max * _money]
prob = cp.Problem(obj, cons)
prob.solve('ECOS', verbose=True)
if w.value is None:
    raise Exception('组合优化的解无效')
w = w.value * money_scale
w[w < 1.] = 0.
vol_opt = pd.Series(w / _pre_close, index=code_list).replace([np.inf, -np.inf, np.nan], 0.)
vol_adj = round(vol_opt - _last_group, -2)
vol_target = vol_adj + _last_group

_amt = amt.loc[opt_date]
_twap = twap.loc[opt_date]
_close = close.loc[opt_date]
_bench_ret = bench_ret.loc[opt_date]
real_max_vol = (_amt * amt_limit_ratio / _twap).replace([np.inf, -np.inf, np.nan], 0.)
vol_real = np.clip(vol_target, -real_max_vol, real_max_vol)
finish_ratio = vol_real.dot(_twap) / vol_target.dot(_twap)
ret = (_last_group.dot(_close - _pre_close) + vol_real.dot(_close - _twap) -
       np.fmax(vol_real, 0).dot(_twap) * fee_buy + np.fmin(vol_real, 0).dot(_twap) * fee_sell) / (
        _last_group.dot(_pre_close) + max(vol_real.dot(_twap), 0))
ret_active = ret - _bench_ret
"""The functions used to create programs.
The :mod:`gplearn.functions` module contains all of the functions used by
gplearn programs. It also contains helper methods for a user to define their
own custom functions.
"""

# Author: Trevor Stephens <trevorstephens.com>
#
# License: BSD 3 clause
import numpy as np
from joblib import wrap_non_picklable_objects
from utils_wsc.operators_wsc import *
from utils_wsc.operators_temp import *
from utils_wsc.technical_index import *
from utils_wsc.help_functions_wsc import replace_zero

__all__ = ['_Function', 'make_function', '_function_map']


class _Function(object):
    """A representation of a mathematical relationship, a node in a program.
    This object is able to be called with NumPy vectorized arguments and return
    a resulting vector based on a mathematical relationship.
    Parameters
    ----------
    function : callable
        A function with signature function(x1, *args) that returns a Numpy
        array of the same shape as its arguments.
    name : str
        The name for the function as it should be represented in the program
        and its visualizations.
    arity : int
        The number of arguments that the ``function`` takes.
    const_arity : int
        The number of constant arguments that the ``function`` takes.    
    """

    def __init__(self, function, name, arity, const_arity):
        self.function = function
        self.name = name
        self.arity = arity
        self.const_arity = const_arity

    def __call__(self, *args):
        return self.function(*args)


def make_function(function, name, arity, const_arity, wrap=True):
    """Make a function node, a representation of a mathematical relationship.
    This factory function creates a function node, one of the core nodes in any
    program. The resulting object is able to be called with NumPy vectorized
    arguments and return a resulting vector based on a mathematical
    relationship.
    Parameters
    ----------
    function : callable
        A function with signature `function(x1, *args)` that returns a Numpy
        array of the same shape as its arguments.
    name : str
        The name for the function as it should be represented in the program
        and its visualizations.
    arity : int
        The number of arguments that the `function` takes.
    const_arity : int
        The number of constant arguments that the `function` takes.
    wrap : bool, optional (default=True)
        When running in parallel, pickling of custom functions is not supported
        by Python's default pickler. This option will wrap the function using
        cloudpickle allowing you to pickle your solution, but the evolution may
        run slightly more slowly. If you are running single-threaded in an
        interactive Python session or have no need to save the model, set to
        `False` for faster runs.
    """
    if not isinstance(arity, int):
        raise ValueError('arity must be an int, got %s' % type(arity))
    if not isinstance(const_arity, int):
        raise ValueError('const arity must be an int, got %s' % type(arity))
    if not isinstance(function, np.ufunc):
        if function.__code__.co_argcount != arity:
            raise ValueError('arity %d does not match required number of '
                             'function arguments of %d.'
                             % (arity, function.__code__.co_argcount))
    if not isinstance(name, str):
        raise ValueError('name must be a string, got %s' % type(name))
    if not isinstance(wrap, bool):
        raise ValueError('wrap must be an bool, got %s' % type(wrap))

    # Check output shape
    args = [np.ones(10) for _ in range(arity)]
    try:
        function(*args)
    except ValueError:
        raise ValueError('supplied function %s does not support arity of %d.'
                         % (name, arity))
    if not hasattr(function(*args), 'shape'):
        raise ValueError('supplied function %s does not return a numpy array.'
                         % name)
    if function(*args).shape != (10,):
        raise ValueError('supplied function %s does not return same shape as '
                         'input vectors.' % name)

    # Check closure for zero & negative input arguments
    args = [np.zeros(10) for _ in range(arity)]
    if not np.all(np.isfinite(function(*args))):
        raise ValueError('supplied function %s does not have closure against '
                         'zeros in argument vectors.' % name)
    args = [-1 * np.ones(10) for _ in range(arity)]
    if not np.all(np.isfinite(function(*args))):
        raise ValueError('supplied function %s does not have closure against '
                         'negatives in argument vectors.' % name)

    if wrap:
        return _Function(function=wrap_non_picklable_objects(function),
                         name=name,
                         arity=arity,
                         const_arity=const_arity)
    return _Function(function=function,
                     name=name,
                     arity=arity,
                     const_arity=const_arity)


def _sigmoid(x1):
    """Special case of logistic function to transform to probabilities."""
    with np.errstate(over='ignore', under='ignore'):
        return 1 / (1 + np.exp(-x1))


def _bbands_up(price, time_period=5, a=1.5):
    return bbands(price, time_period, a)[1]


def _bbands_down(price, time_period=5, a=1.5):
    return bbands(price, time_period, a)[2]


def _dema(price, time_period=30):
    price_ema = ts_mean(price, time_period)
    price_dema = 2 * price_ema - ts_mean(price_ema, time_period)
    return price_dema


def _kama(price, time_period=10, n1=2, n2=30):
    _n1 = min(n1, n2)
    _n2 = max(n1, n2)
    change = abs(ts_delta(price, time_period))
    volatility = ts_sum(abs(ts_delta(price, 1)), time_period)
    er = change / volatility
    fast_sc = 2 / (_n1 + 1)
    slow_sc = 2 / (_n2 + 1)
    smooth_constant = er * (fast_sc - slow_sc) + slow_sc
    cof = smooth_constant ** 2
    price_kama = ts_mean(price, int(2 / cof - 1))
    return price_kama


def _mavp(price, va_time_period, min_period, max_period):
    _min_period = min(min_period, max_period)
    _max_period = max(min_period, max_period)
    return mavp(price, va_time_period, _min_period, _max_period)


def _distance_to_variation_abs(data, d):
    return distance_to_variation(data, d, need_abs=True)


def _midprice(price_high, price_low, time_period):
    _price_high = np.maximum(price_high, price_low)
    _price_low = np.minimum(price_high, price_low)
    return midprice(_price_high, _price_low, time_period)


def _atr(price_high, price_low, price_close, time_period=14):
    _price_high = np.maximum(np.maximum(price_high, price_low), price_close)
    _price_low = np.minimum(np.minimum(price_high, price_low), price_close)
    return atr(_price_high, _price_low, price_close, time_period)


def _di_plus(price_high, price_low, price_close, time_period=14):
    _price_high = np.maximum(np.maximum(price_high, price_low), price_close)
    _price_low = np.minimum(np.minimum(price_high, price_low), price_close)
    return di(_price_high, _price_low, price_close, time_period)[0]


def _di_minus(price_high, price_low, price_close, time_period=14):
    _price_high = np.maximum(np.maximum(price_high, price_low), price_close)
    _price_low = np.minimum(np.minimum(price_high, price_low), price_close)
    return di(_price_high, _price_low, price_close, time_period)[1]


def _dx(price_high, price_low, price_close, time_period=14):
    _price_high = np.maximum(np.maximum(price_high, price_low), price_close)
    _price_low = np.minimum(np.minimum(price_high, price_low), price_close)
    return dx(_price_high, _price_low, price_close, time_period)


def _aroon(price_high, price_low, time_period=14):
    _price_high = np.maximum(price_high, price_low)
    _price_low = np.minimum(price_high, price_low)
    return aroon(_price_high, _price_low, time_period)[2]


def _bop(price_open, price_high, price_low, price_close, time_period=14):
    _price_high = np.maximum(np.maximum(np.maximum(price_open, price_high), price_low), price_close)
    _price_low = np.minimum(np.minimum(np.minimum(price_open, price_high), price_low), price_close)
    return bop(price_open, _price_high, _price_low, price_close, time_period)


def _cci(typical_price, time_period=14):
    """
    CCI(commodity channel index)指标用来衡量典型价格与其一段时间的移动平均的偏离程度，可以用来反映市场的超买超卖状态；
    一般认为，CCI超过100则市场处于超买状态，低于-100则市场处于超卖状态。
    """
    typical_price_ma = ts_mean(typical_price, time_period)
    typical_price_mean_deviation = ts_mean(abs(typical_price - typical_price_ma), time_period)
    price_cci = (typical_price - typical_price_ma) / (0.015 * typical_price_mean_deviation)
    return price_cci


def _macd(price_close, fast_period=12, slow_period=26, signal_period=9):
    return macd(price_close, fast_period, slow_period, signal_period)[2]


def _mfi(typical_price, volume, time_period=14):
    money_flow_pos = typical_price * volume
    money_flow_pos[ts_delta(typical_price, 1) < 0] = 0
    money_flow_neg = typical_price * volume
    money_flow_neg[ts_delta(typical_price, 1) > 0] = 0
    money_flow_pos_sum = ts_sum(money_flow_pos, time_period)
    money_flow_neg_sum = ts_sum(money_flow_neg, time_period)
    price_mfi = money_flow_pos_sum / replace_zero(money_flow_pos_sum + money_flow_neg_sum)
    return price_mfi


abs1 = _Function(function=np.abs, name='abs', arity=1, const_arity=0)
add2 = _Function(function=add2, name='add2', arity=2, const_arity=0)
div2 = _Function(function=div2, name='div2', arity=2, const_arity=0)
inv1 = _Function(function=inv1, name='inv1', arity=1, const_arity=0)
log = _Function(function=log, name='log', arity=1, const_arity=0)
mul2 = _Function(function=mul2, name='mul2', arity=2, const_arity=0)
max2 = _Function(function=max2, name='max2', arity=2, const_arity=0)
min2 = _Function(function=min2, name='min2', arity=2, const_arity=0)
neg1 = _Function(function=np.negative, name='neg1', arity=1, const_arity=0)
rolling_norm = _Function(function=rolling_norm, name='rolling_norm', arity=1, const_arity=1)
sqrt = _Function(function=sqrt, name='sqrt', arity=1, const_arity=0)
square = _Function(function=square, name='square', arity=1, const_arity=0)
sub2 = _Function(function=np.subtract, name='sub2', arity=2, const_arity=0)
ts_argmax = _Function(function=ts_argmax, name='ts_argmax', arity=1, const_arity=1)
ts_argmin = _Function(function=ts_argmin, name='ts_argmin', arity=1, const_arity=1)
ts_corr = _Function(function=ts_corr, name='ts_corr', arity=2, const_arity=1)
ts_cov = _Function(function=ts_cov, name='ts_cov', arity=2, const_arity=1)
ts_decay_linear = _Function(function=ts_decay_linear, name='ts_decay_linear', arity=1, const_arity=1)
ts_delay = _Function(function=ts_delay, name='ts_delay', arity=1, const_arity=1)
ts_delta = _Function(function=ts_delta, name='ts_delta', arity=1, const_arity=1)
ts_max = _Function(function=ts_max, name='ts_max', arity=1, const_arity=1)
ts_mean = _Function(function=ts_mean, name='ts_mean', arity=1, const_arity=1)
ts_median = _Function(function=ts_median, name='ts_median', arity=1, const_arity=1)
ts_min = _Function(function=ts_min, name='ts_min', arity=1, const_arity=1)
ts_pct_change = _Function(function=ts_pct_change, name='ts_pct_change', arity=1, const_arity=1)
ts_position = _Function(function=ts_position, name='ts_position', arity=1, const_arity=1)
ts_pred = _Function(function=ts_pred, name='ts_pred', arity=1, const_arity=1)
ts_pred_delta = _Function(function=ts_pred_delta, name='ts_pred_delta', arity=1, const_arity=1)
ts_rank = _Function(function=ts_rank, name='ts_rank', arity=1, const_arity=1)
ts_reg_alpha = _Function(function=ts_reg_alpha, name='ts_reg_alpha', arity=1, const_arity=1)
ts_reg_beta = _Function(function=ts_reg_beta, name='ts_reg_beta', arity=1, const_arity=1)
ts_reg_residual = _Function(function=ts_reg_residual, name='ts_reg_residual', arity=1, const_arity=1)
ts_skew = _Function(function=ts_skew, name='ts_skew', arity=1, const_arity=1)
# ts_ema_span = _Function(function=ts_ema_span, name='ts_ema_span', arity=1, const_arity=1)
ts_std = _Function(function=ts_std, name='ts_std', arity=1, const_arity=1)
ts_sum = _Function(function=ts_sum, name='ts_sum', arity=1, const_arity=1)

sin1 = _Function(function=np.sin, name='sin', arity=1, const_arity=0)
cos1 = _Function(function=np.cos, name='cos', arity=1, const_arity=0)
tan1 = _Function(function=np.tan, name='tan', arity=1, const_arity=0)
sigmoid = _Function(function=_sigmoid, name='sigmoid', arity=1, const_arity=0)

auto_corr = _Function(function=auto_corr, name='auto_corr', arity=1, const_arity=2)
up_outlier_ratio = _Function(function=up_outlier_ratio, name='up_outlier_ratio', arity=1, const_arity=2)
down_outlier_ratio = _Function(function=down_outlier_ratio, name='down_outlier_ratio', arity=1, const_arity=2)
outlier_ratio = _Function(function=outlier_ratio, name='outlier_ratio', arity=1, const_arity=2)
coefficient_of_variation = _Function(function=coefficient_of_variation, name='coefficient_of_variation', arity=1,
                                     const_arity=1)
long_short_ma_ratio = _Function(function=long_short_ma_ratio, name='long_short_ma_ratio', arity=1, const_arity=2)
up_down_ratio = _Function(function=up_down_ratio, name='up_down_ratio', arity=1, const_arity=2)
cross_hub_num = _Function(function=cross_hub_num, name='cross_hub_num', arity=1, const_arity=1)

bbands_up_ = _Function(function=_bbands_up, name='bbands_up', arity=1, const_arity=1)
bbands_down_ = _Function(function=_bbands_down, name='bbands_down', arity=1, const_arity=1)
dema_ = _Function(function=_dema, name='dema', arity=1, const_arity=1)
kama_ = _Function(function=_kama, name='kama', arity=1, const_arity=3)
mavp_ = _Function(function=_mavp, name='mavp', arity=2, const_arity=2)
midpoint_ = _Function(function=midpoint, name='midpoint', arity=1, const_arity=1)
midprice_ = _Function(function=_midprice, name='midprice', arity=2, const_arity=1)
trima_ = _Function(function=trima, name='trima', arity=1, const_arity=1)
atr_ = _Function(function=_atr, name='atr', arity=3, const_arity=1)
di_plus_ = _Function(function=_di_plus, name='di_plus', arity=3, const_arity=1)
di_minus_ = _Function(function=_di_minus, name='di_minus', arity=3, const_arity=1)
dx_ = _Function(function=_dx, name='dx', arity=3, const_arity=1)
# adx_ = _Function(function=adx, name='adx', arity=3, const_arity=1)
# adxr_ = _Function(function=adxr, name='adxr', arity=3, const_arity=1)
po_ = _Function(function=po, name='po', arity=1, const_arity=2)
aroon_ = _Function(function=_aroon, name='aroon', arity=2, const_arity=1)
# bop_ = _Function(function=_bop, name='bop', arity=4, const_arity=1)
cci_ = _Function(function=_cci, name='cci', arity=1, const_arity=1)
cmo_ = _Function(function=cmo, name='cmo', arity=1, const_arity=1)
macd_ = _Function(function=_macd, name='macd', arity=1, const_arity=3)
mfi_ = _Function(function=_mfi, name='mfi', arity=2, const_arity=1)
ppo_ = _Function(function=ppo, name='ppo', arity=1, const_arity=2)
rocr_ = _Function(function=rocr, name='rocr', arity=1, const_arity=1)
rsi_ = _Function(function=rsi, name='rsi', arity=1, const_arity=1)

distance_to_variation_ = _Function(function=distance_to_variation, name='distance_to_variation', arity=1, const_arity=1)
distance_to_variation_abs_ = _Function(function=_distance_to_variation_abs, name='distance_to_variation_abs', arity=1,
                                       const_arity=1)
ts_midpoint_ = _Function(function=ts_midpoint, name='ts_midpoint', arity=1, const_arity=1)
ts_maxmin_distance_ = _Function(function=ts_maxmin_distance, name='ts_maxmin_distance', arity=1, const_arity=1)
ts_distance_from_mean_ = _Function(function=ts_distance_from_mean, name='ts_distance_from_mean', arity=1, const_arity=1)
ts_ratio_from_mean_ = _Function(function=ts_ratio_from_mean, name='ts_ratio_from_mean', arity=1, const_arity=1)
ts_zscore_ = _Function(function=ts_zscore, name='ts_zscore', arity=1, const_arity=1)

_function_map = {'abs': abs1,
                 'add2': add2,
                 'div2': div2,
                 'inv1': inv1,
                 'log': log,
                 'mul2': mul2,
                 'max2': max2,
                 'min2': min2,
                 'neg1': neg1,
                 'rolling_norm': rolling_norm,
                 'sqrt': sqrt,
                 'square': square,
                 'sub2': sub2,
                 'ts_argmax': ts_argmax,
                 'ts_argmin': ts_argmin,
                 'ts_corr': ts_corr,
                 'ts_cov': ts_cov,
                 'ts_decay_linear': ts_decay_linear,
                 'ts_delay': ts_delay,
                 'ts_delta': ts_delta,
                 # 'ts_ema_span': ts_ema_span,
                 'ts_max': ts_max,
                 'ts_mean': ts_mean,
                 'ts_median': ts_median,
                 'ts_min': ts_min,
                 'ts_pct_change': ts_pct_change,
                 'ts_position': ts_position,
                 'ts_pred': ts_pred,
                 'ts_rank': ts_rank,
                 'ts_reg_alpha': ts_reg_alpha,
                 'ts_reg_beta': ts_reg_beta,
                 'ts_skew': ts_skew,
                 'ts_std': ts_std,
                 'ts_sum': ts_sum,
                 'sigmoid': sigmoid,
                 'auto_corr': auto_corr,
                 'up_outlier_ratio': up_outlier_ratio,
                 'down_outlier_ratio': down_outlier_ratio,
                 'outlier_ratio': outlier_ratio,
                 'coefficient_of_variation': coefficient_of_variation,
                 'long_short_ma_ratio': long_short_ma_ratio,
                 'up_down_ratio': up_down_ratio,
                 'cross_hub_num': cross_hub_num,
                 'bbands_up': bbands_up_,
                 'bbands_down': bbands_down_,
                 'dema': dema_,
                 # 'kama': kama_,
                 # 'mavp': mavp_,
                 'midpoint': midpoint_,
                 'midprice': midprice_,
                 'trima': trima_,
                 'dx': dx_,
                 'po': po_,
                 'aroon': aroon_,
                 'cci': cci_,
                 'cmo': cmo_,
                 'ppo': ppo_,
                 'rocr': rocr_,
                 'rsi': rsi_,
                 'distance_to_variation': distance_to_variation_,
                 'distance_to_variation_abs': distance_to_variation_abs_,
                 'ts_midpoint': ts_midpoint_,
                 'ts_maxmin_distance': ts_maxmin_distance_,
                 'ts_distance_from_mean': ts_distance_from_mean_,
                 'ts_ratio_from_mean': ts_ratio_from_mean_,
                 'ts_pred_delta': ts_pred_delta,
                 'macd': macd_,
                 'atr': atr_,
                 'ts_reg_residual': ts_reg_residual,
                 'di_plus': di_plus_,
                 'di_minus': di_minus_,
                 'mfi': mfi_,
                 'ts_zscore': ts_zscore_
                 }

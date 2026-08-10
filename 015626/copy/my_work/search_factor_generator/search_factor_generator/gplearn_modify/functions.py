"""The functions used to create programs.
The :mod:`gplearn.functions` module contains all of the functions used by
gplearn programs. It also contains helper methods for a user to define their
own custom functions.
"""

# Author: Trevor Stephens <trevorstephens.com>
#
# License: BSD 3 clause
import sys
sys.path.insert(4, '/data/user/017024')


import numpy as np
from joblib import wrap_non_picklable_objects
from code_wsc.operators_wsc_1_1 import *

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
    """

    def __init__(self, function, name, arity, need_const=False):
        self.function = function
        self.name = name
        self.arity = arity
        self.need_const = need_const

    def __call__(self, *args):
        return self.function(*args)


def make_function(function, name, arity, need_const=False, wrap=True):
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
    need_const : bool, optional (default=False)
        If the function need constant parameters.
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
                         need_const=need_const)
    return _Function(function=function,
                     name=name,
                     arity=arity,
                     need_const=need_const)


# def _protected_division(x1, x2):
#     """Closure of division (x1/x2) for zero denominator."""
#     with np.errstate(divide='ignore', invalid='ignore'):
#         return np.where(np.abs(x2) > 0.001, np.divide(x1, x2), 1.)


# def _protected_sqrt(x1):
#     """Closure of square root for negative arguments."""
#     return np.sqrt(np.abs(x1))


# def _protected_log(x1):
#     """Closure of log for zero arguments."""
#     with np.errstate(divide='ignore', invalid='ignore'):
#         return np.where(np.abs(x1) > 0.001, np.log(np.abs(x1)), 0.)


# def _protected_inverse(x1):
#     """Closure of log for zero arguments."""
#     with np.errstate(divide='ignore', invalid='ignore'):
#         return np.where(np.abs(x1) > 0.001, 1. / x1, 0.)


def _sigmoid(x1):
    """Special case of logistic function to transform to probabilities."""
    with np.errstate(over='ignore', under='ignore'):
        return 1 / (1 + np.exp(-x1))


abs1 = _Function(function=np.abs, name='abs', arity=1, need_const=False)
add2 = _Function(function=add2, name='add2', arity=2, need_const=False)
div2 = _Function(function=div2, name='div2', arity=2, need_const=False)
inv1 = _Function(function=inv1, name='inv', arity=1, need_const=False)
log = _Function(function=log, name='log', arity=1, need_const=False)
mul2 = _Function(function=mul2, name='mul2', arity=2, need_const=False)
max2 = _Function(function=max2, name='max2', arity=2, need_const=False)
min2 = _Function(function=min2, name='min2', arity=2, need_const=False)
neg1 = _Function(function=np.negative, name='neg', arity=1, need_const=False)
rolling_norm = _Function(function=rolling_norm, name='rolling_norm', arity=1, need_const=True)
sqrt = _Function(function=sqrt, name='sqrt', arity=1, need_const=False)
square = _Function(function=square, name='square', arity=1, need_const=False)
sub2 = _Function(function=np.subtract, name='sub2', arity=2, need_const=False)
ts_argmax = _Function(function=ts_argmax, name='ts_argmax', arity=1, need_const=True)
ts_argmin = _Function(function=ts_argmin, name='ts_argmin', arity=1, need_const=True)
ts_corr = _Function(function=ts_corr, name='ts_corr', arity=2, need_const=True)
ts_cov = _Function(function=ts_cov, name='ts_cov', arity=2, need_const=True)
ts_decay_linear = _Function(function=ts_decay_linear, name='ts_decay_linear', arity=1, need_const=True)
ts_delay = _Function(function=ts_delay, name='ts_delay', arity=1, need_const=True)
ts_delta = _Function(function=ts_delta, name='ts_delta', arity=1, need_const=True)
ts_max = _Function(function=ts_max, name='ts_max', arity=1, need_const=True)
ts_mean = _Function(function=ts_mean, name='ts_mean', arity=1, need_const=True)
ts_median = _Function(function=ts_median, name='ts_median', arity=1, need_const=True)
ts_min = _Function(function=ts_min, name='ts_min', arity=1, need_const=True)
ts_pct_change = _Function(function=ts_pct_change, name='ts_pct_change', arity=1, need_const=True)
ts_position = _Function(function=ts_position, name='ts_position', arity=1, need_const=True)
ts_pred = _Function(function=ts_pred, name='ts_pred', arity=1, need_const=True)
ts_pred_delta = _Function(function=ts_pred_delta, name='ts_pred_delta', arity=1, need_const=True)
ts_rank = _Function(function=ts_rank, name='ts_rank', arity=1, need_const=True)
ts_reg_alpha = _Function(function=ts_reg_alpha, name='ts_reg_alpha', arity=1, need_const=True)
ts_reg_beta = _Function(function=ts_reg_beta, name='ts_reg_beta', arity=1, need_const=True)
ts_reg_residual = _Function(function=ts_reg_residual, name='ts_reg_residual', arity=1, need_const=True)
ts_skew = _Function(function=ts_skew, name='ts_skew', arity=1, need_const=True)
# ts_ema_span = _Function(function=ts_ema_span, name='ts_ema_span', arity=1, need_const=True)
ts_std = _Function(function=ts_std, name='ts_std', arity=1, need_const=True)
ts_sum = _Function(function=ts_sum, name='ts_sum', arity=1, need_const=True)

sin1 = _Function(function=np.sin, name='sin', arity=1, need_const=False)
cos1 = _Function(function=np.cos, name='cos', arity=1, need_const=False)
tan1 = _Function(function=np.tan, name='tan', arity=1, need_const=False)
sigmoid = _Function(function=_sigmoid, name='sig', arity=1, need_const=False)




_function_map = {'abs': abs1,
                 'add2': add2,
                 'div2': div2,
                 'inv': inv1,
                 'log': log,
                 'mul2': mul2,
                 'max2': max2,
                 'min2': min2,
                 'neg': neg1,
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
                 'ts_pred_delta': ts_pred_delta,
                 'ts_rank': ts_rank,
                 'ts_reg_alpha': ts_reg_alpha,
                 'ts_reg_beta': ts_reg_beta,
                 'ts_reg_residual': ts_reg_residual,
                 'ts_skew': ts_skew,
                 'ts_std': ts_std,
                 'ts_sum': ts_sum,
                 'sigmoid': sigmoid}

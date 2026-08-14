# coding: utf-8
# Author：fengchi863
# Date ：2020/7/27 10:14
"""Ordinary least-squares (OLS) regression.  Static and rolling cases."""

__author__ = "HANXU <hx5991@ruc.edu.cn>"
__all__ = ["OLS", "RollingOLS", "PandasRollingOLS"]


from functools import lru_cache

import numpy as np
from pandas import DataFrame, Series
import scipy.stats as scs
from statsmodels.tools import add_constant

def _rolling_windows(a, window):
    """Creates rolling-window 'blocks' of length `window` from `a`.
    Note that the orientation of rows/columns follows that of pandas.
    Example
    -------
    import numpy as np
    onedim = np.arange(20)
    twodim = onedim.reshape((5,4))
    print(twodim)
    [[ 0  1  2  3]
     [ 4  5  6  7]
     [ 8  9 10 11]
     [12 13 14 15]
     [16 17 18 19]]
    print(rwindows(onedim, 3)[:5])
    [[0 1 2]
     [1 2 3]
     [2 3 4]
     [3 4 5]
     [4 5 6]]
    print(rwindows(twodim, 3)[:5])
    [[[ 0  1  2  3]
      [ 4  5  6  7]
      [ 8  9 10 11]]
     [[ 4  5  6  7]
      [ 8  9 10 11]
      [12 13 14 15]]
     [[ 8  9 10 11]
      [12 13 14 15]
      [16 17 18 19]]]
    """

    if window > a.shape[0]:
        raise ValueError(
            "Specified `window` length of {0} exceeds length of"
            " `a`, {1}.".format(window, a.shape[0])
        )
    if isinstance(a, (Series, DataFrame)):
        a = a.values
    if a.ndim == 1:
        a = a.reshape(-1, 1)
    shape = (a.shape[0] - window + 1, window) + a.shape[1:]
    strides = (a.strides[0],) + a.strides
    windows = np.squeeze(
        np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    )
    # In cases where window == len(a), we actually want to "unsqueeze" to 2d.
    #     I.e., we still want a "windowed" structure with 1 window.
    if windows.ndim == 1:
        windows = np.atleast_2d(windows)
    return windows

def _rolling_lstsq(x, y):
    """Finds solution for the rolling case.  Matrix formulation."""
    if x.ndim == 2:
        # Treat everything as 3d and avoid AxisError on .swapaxes(1, 2) below
        # This means an original input of:
        #     array([0., 1., 2., 3., 4., 5., 6.])
        # becomes:
        # array([[[0.],
        #         [1.],
        #         [2.],
        #         [3.]],
        #
        #        [[1.],
        #         [2.],
        #         ...
        x = x[:, :, None]
    elif x.ndim <= 1:
        raise np.AxisError("x should have ndmi >= 2")
    return np.squeeze(
        np.matmul(
            np.linalg.inv(np.matmul(x.swapaxes(1, 2), x)),
            np.matmul(x.swapaxes(1, 2), np.atleast_3d(y)),
        )
    )

def _confirm_constant(a):
    """Confirm `a` has volumn vector of 1s."""
    a = np.asanyarray(a)
    return np.isclose(a, 1.0).all(axis=0).any()

def _check_constant_params(a, has_const=False, use_const=True, rtol=1e-05, atol=1e-08):
    """Helper func to interaction between has_const and use_const params.
    has_const   use_const   outcome
    ---------   ---------   -------
    True        True        Confirm that a has constant; return a
    False       False       Confirm that a doesn't have constant; return a
    False       True        Confirm that a doesn't have constant; add constant
    True        False       ValueError
    """

    if all((has_const, use_const)):
        if not _confirm_constant(a):
            raise ValueError(
                "Data does not contain a constant; specify" " has_const=False"
            )
        k = a.shape[-1] - 1
    elif not any((has_const, use_const)):
        if _confirm_constant(a):
            raise ValueError(
                "Data already contains a constant; specify" " has_const=True"
            )
        k = a.shape[-1]
    elif not has_const and use_const:
        # Also run a quick check to confirm that `a` is *not* ~N(0,1).
        #     In this case, constant should be zero. (exclude it entirely)
        c1 = np.allclose(a.mean(axis=0), b=0.0, rtol=rtol, atol=atol)
        c2 = np.allclose(a.std(axis=0), b=1.0, rtol=rtol, atol=atol)
        if c1 and c2:
            # TODO: maybe we want to just warn here?
            raise ValueError(
                "Data appears to be ~N(0,1).  Specify" " use_constant=False."
            )
        # `has_constant` does checking on its own and raises VE if True
        try:
            a = add_constant(a, has_constant="raise")
        except ValueError as e:
            raise ValueError(
                "X data already contains a constant; please specify"
                " has_const=True"
            ) from e
        k = a.shape[-1] - 1
    else:
        raise ValueError("`use_const` == False implies has_const is False.")

    return k, a

def _handle_ab(solution, use_const=True):
    b = solution[1:] if use_const else solution
    b = b.item() if b.size == 1 else b
    a = solution[0] if use_const else None
    return a, b

def _handle_rolling_ab(solution, use_const=True):
    b = solution[:, 1:] if use_const else solution
    b = np.squeeze(b) if b.shape[1] == 1 else b
    a = solution[:, 0] if use_const else None
    return a, b

def _clean_xy(y, x=None, thres=0, wgt=None, has_const=False, use_const=True):

    x = np.asanyarray(x.copy()) if x is not None else None
    wgt = np.squeeze(np.asanyarray(wgt.copy())) if wgt is not None else None
    y = np.asanyarray(y.copy())
    # If only `y` is given (and `x=None`), `y` is assumed to be the first
    # column of `y` and `x` the remaining [1:] columns
    if x is None:
        x = y[:, 1:]
        y = y[:, 0]

    k, x = _check_constant_params(x, has_const=has_const, use_const=use_const)
    y = np.squeeze(y)

    if x.ndim == 1:
        x = x[:, None]
    assert y.ndim == 1 and x.ndim > 1

    if wgt is not None:
        if (wgt.ndim == 1) & (wgt.shape[0] == y.shape[0]):
            wxy = np.c_[x, y, wgt]
        else:
            wxy = np.c_[x, y]
    else:
        wxy = np.c_[x, y]

    nonNanSample = (~ np.isnan(wxy)).all(axis=-1)
    nonNanNum = nonNanSample.sum()

    if (nonNanNum > k - 1) & (nonNanNum / nonNanSample.shape[0] >= thres):

        x = x[nonNanSample]
        y = y[nonNanSample]

        if wgt is not None:
            if wgt.ndim == 1:
                wgt = wgt[nonNanSample]
                x = (wgt * x.T).T
                y = wgt * y
            else:
                wgt = wgt[nonNanSample][:, nonNanSample]
                x = wgt.dot(x)
                y = wgt.dot(y)

    return x, y, k, nonNanSample

def _roll_clean_xy(window, y, x=None, thres=0, wgt=None, has_const=False, use_const=True):

    x = np.asanyarray(x.copy()) if x is not None else None
    wgt = np.squeeze(np.asanyarray(wgt.copy())) if wgt is not None else None
    y = np.asanyarray(y.copy())
    # If only `y` is given (and `x=None`), `y` is assumed to be the first
    # column of `y` and `x` the remaining [1:] columns
    if x is None:
        x = y[:, 1:]
        y = y[:, 0]

    k, x = _check_constant_params(x, has_const=has_const, use_const=use_const)
    y = np.squeeze(y)

    if x.ndim == 1:
        x = x[:, None]
    assert y.ndim == 1 and x.ndim > 1

    if wgt is not None:
        if (wgt.ndim == 1) & (wgt.shape[0] == y.shape[0]):
            wxy = np.c_[x, y, wgt]
        else:
            wxy = np.c_[x, y]
    else:
        wxy = np.c_[x, y]

    nonNanSample = (~np.isnan(wxy)).all(axis=-1)
    rnn = _rolling_windows(nonNanSample, window)
    n = rnn.sum(axis=-1).astype(float)
    exist = (n > k - 1) & (n / window >= thres)
    n[~exist] = np.nan

    x[~nonNanSample] = 0
    y[~nonNanSample] = 0

    wx = _rolling_windows(x, window) + 0
    wy = _rolling_windows(y, window) + 0

    wx[~exist] = np.nan
    wy[~exist] = np.nan

    if wgt is not None:
        if wgt.shape[0] == window:
            wx = (wx.swapaxes(1,-1) * wgt).swapaxes(1,-1)
            wy = wy * wgt
        elif wgt.shape[0] == nonNanSample.shape[0]:
            wgt[~nonNanSample] = 0
            wgt = _rolling_windows(wgt, window)
            wx = (wgt.swapaxes(0,-1) * wx.swapaxes(0,-1)).swapaxes(0,-1)
            wy = wy * wgt
        else:
            raise ValueError('wgt must be the same length with window or length of y')

    return wx, wy, wgt, k, n, rnn, exist

def _half_life_wgt(half_life, window):

    half_life_wgt = 2 ** (- (1 / half_life) * np.arange(window - 1, -1, -1))
    half_life_wgt /= half_life_wgt.sum()
    return half_life_wgt

class OLS(object):
    """Ordinary least-squares (OLS) regression.
    Implemented in NumPy.  Outputs are NumPy arrays or scalars.
    Attributes largely mimic statsmodels' OLS RegressionResultsWrapper.
    (see statsmodels.regression.linear_model.RegressionResults)
    The core of the model is calculated with the 'gelsd' LAPACK driver,
    witin numpy.linalg.lstsq, yielding the coefficients (parameters).  Most
    methods are then a derivation of these coefficients.
    Parameters
    ----------
    y : array-like
        The single y (dependent, response, endogenous) variable.
    x : array-like or None, default None
        The x (independent, explanatory, exogenous) variables.  If only `y`
        is given (and `x=None`), `y` is assumed to be the first column of
        `y` and `x` the remaining [1:] columns.
    has_const : bool, default False
        Specifies whether `x` includes a user-supplied constant (a column
        vector).  If False, it is added at instantiation.
    use_const ; bool, default True
        Whether to include an intercept term in the model output.  Note the
        difference between has_const and use_const.  The former specifies
        whether a column vector of 1s is included in the input; the latter
        specifies whether the model itself should include a constant
        (intercept) term.  Exogenous data that is ~N(0,1) would have a
        constant equal to zero; specify use_const=False in this situation.
    """

    def __init__(self, y, x=None, thres=0, wgt=None, has_const=False, use_const=True):

        self.wgt = _half_life_wgt(wgt, y.shape[0]) if type(wgt) == int else wgt
        self.x, self.y, self.k, self.nonNanSample = _clean_xy(y, x, thres, self.wgt, has_const, use_const)
        self.n = self.y.shape[0]

        # np.lstsq(a,b): Solves the equation a x = b by computing a vector x
        self.solution = np.linalg.lstsq(self.x, self.y, rcond=None)[0]

        self.has_const = has_const
        self.use_const = use_const

    @property
    def alpha(self):
        """The intercept term (alpha).
        Technically defined as the coefficient to a column vector of ones.
        """

        return _handle_ab(self.solution, self.use_const)[0]

    @property
    def beta(self):
        """The parameters (coefficients), excl. the intercept."""
        return _handle_ab(self.solution, self.use_const)[1]

    @property
    def condition_number(self):
        """Condition number of x; ratio of largest to smallest eigenvalue."""
        # Mimic x = np.matrix(self.x) (deprecated)
        x = np.atleast_2d(self.x)
        ev = np.linalg.eig(x.T @ x)[0]
        return np.sqrt(ev.max() / ev.min())

    @property
    def df_tot(self):
        """Total degrees of freedom, n - 1."""
        return self.n - 1

    @property
    def df_reg(self):
        """Model degrees of freedom. Equal to k."""
        return self.k

    @property
    def df_err(self):
        """Residual degrees of freedom. n - k - 1."""
        return self.n - self.k - 1

    @property
    def _predicted(self):
        """The predicted values of y (yhat)."""
        # don't transpose - shape should match that of self.y
        return self.x.dot(self.solution)

    @property
    def predicted(self):
        """The predicted values of y (yhat)."""
        # don't transpose - shape should match that of self.y
        predict = np.full(self.nonNanSample.shape, np.nan)
        predict[self.nonNanSample] = self._predicted
        return predict

    @property
    def _resids(self):
        """The residuals (errors)."""
        return self.y - self._predicted

    @property
    def resids(self):
        """The residuals (errors)."""
        res = np.full(self.nonNanSample.shape, np.nan)
        res[self.nonNanSample] = self._resids
        return res

    @property
    def ss_err(self):
        """Sum of squares of the residuals (error sum of squares)."""
        return np.sum(np.square(self._resids), axis=0)

    @property
    def durbin_watson(self):
        return np.sum(np.diff(self._resids) ** 2.0) / self.ss_err

    @property
    def ss_reg(self):
        """Sum of squares of the regression."""
        return np.sum(np.square(self._predicted - self.ybar), axis=0)

    @property
    def ms_reg(self):
        """Mean squared error the regression (model)."""
        return self.ss_reg / self.df_reg

    @property
    def ms_err(self):
        """Mean squared error the errors (residuals)."""
        return self.ss_err / self.df_err

    @property
    def fstat(self):
        """F-statistic of the fully specified model."""
        return self.ms_reg / self.ms_err

    @property
    def fstat_sig(self):
        """p-value of the F-statistic."""
        return 1.0 - scs.f.cdf(self.fstat, self.df_reg, self.df_err)

    @property
    def jarque_bera(self):
        return scs.jarque_bera(self._resids)[0]

    @property
    def _pvalues_all(self):
        """Two-tailed p values for t-stats of all parameters."""
        return 2.0 * (1.0 - scs.t.cdf(np.abs(self._tstat_all), self.df_err))

    @property
    def pvalue_alpha(self):
        """Two-tailed p values for t-stats of the intercept only."""
        return _handle_ab(self._pvalues_all, self.use_const)[0]

    @property
    def pvalue_beta(self):
        """Two-tailed p values for t-stats of parameters, excl. intercept."""
        return _handle_ab(self._pvalues_all, self.use_const)[1]

    @property
    def rsq(self):
        """The coefficent of determination, R-squared."""
        return self.ss_reg / self.ss_tot

    @property
    def rsq_adj(self):
        """Adjusted R-squared."""
        n = self.n
        k = self.k
        return 1.0 - ((1.0 - self.rsq) * (n - 1.0) / (n - k - 1.0))

    @property
    def _se_all(self):
        """Standard errors (SE) for all parameters, including the intercept."""
        x = np.atleast_2d(self.x)
        err = np.atleast_1d(self.ms_err)
        se = np.sqrt(np.diagonal(np.linalg.inv(x.T @ x)) * err[:, None])
        return np.squeeze(se)

    @property
    def se_alpha(self):
        """Standard errors (SE) of the intercept (alpha) only."""
        return _handle_ab(self._se_all, self.use_const)[0]

    @property
    def se_beta(self):
        """Standard errors (SE) of the parameters, excluding the intercept."""
        return _handle_ab(self._se_all, self.use_const)[1]

    @property
    def ybar(self):
        """The mean of y."""
        return self.y.mean(axis=0)

    @property
    def ss_tot(self):
        """Total sum of squares."""
        return np.sum(np.square(self.y - self.ybar), axis=0)

    @property
    def std_err(self):
        """Standard error of the estimate (SEE).  A scalar.
        For standard errors of parameters, see _se_all, se_alpha, and se_beta.
        """

        return np.sqrt(np.sum(np.square(self._resids), axis=0) / self.df_err)

    @property
    def _tstat_all(self):
        """The t-statistics of all parameters, incl. the intecept."""
        return self.solution.T / self._se_all

    @property
    def tstat_alpha(self):
        """The t-statistic of the intercept (alpha)."""
        return _handle_ab(self._tstat_all, self.use_const)[0]

    @property
    def tstat_beta(self):
        """The t-statistics of the parameters, excl. the intecept."""
        return _handle_ab(self._tstat_all, self.use_const)[1]

class RollingOLS(object):
    """Rolling ordinary least-squares regression.
    Uses matrix formulation with NumPy broadcasting.  Outputs are NumPy arrays
    or scalars.
    Attributes largely mimic statsmodels' OLS RegressionResultsWrapper.
    (see statsmodels.regression.linear_model.RegressionResults)
    The core of the model is calculated with the 'gelsd' LAPACK driver,
    witin numpy.linalg.lstsq, yielding the coefficients (parameters).  Most
    methods are then a derivation of these coefficients.
    Parameters
    ----------
    y : array-like
        The single y (dependent, response, endogenous) variable
    x : array-like or None, default None
        The x (independent, explanatory, exogenous) variables.  If only `y`
        is given (and `x=None`), `y` is assumed to be the first column of
        `y` and `x` the remaining [1:] columns
    window : int
        Length of each rolling window
    has_const : bool, default False
        Specifies whether `x` includes a user-supplied constant (a column
        vector).  If False, it is added at instantiation
    use_const : bool, default True
        Whether to include an intercept term in the model output.  Note the
        difference between has_const and use_const.  The former specifies
        whether a column vector of 1s is included in the input; the latter
        specifies whether the model itself should include a constant
        (intercept) term.  Exogenous data that is ~N(0,1) would have a
        constant equal to zero; specify use_const=False in this situation
    """

    def __init__(self, window, y, x=None, thres=0, wgt=None, has_const=False, use_const=True):

        self.wgt = _half_life_wgt(wgt, window) if type(wgt) == int else wgt
        self.wx, self.wy, self.wgt, self.k, self.n, self.rnn, self.exist =\
            _roll_clean_xy(window, y, x, thres, self.wgt, has_const, use_const)
        self.solution = _rolling_lstsq(self.wx, self.wy)
        self.window = window
        self.has_const = has_const
        self.use_const = use_const

    @property
    def _alpha(self):
        """The intercept term (alpha).
        Technically defined as the coefficient to a column vector of ones.
        """

        return _handle_rolling_ab(self.solution, self.use_const)[0]

    @property
    def _beta(self):
        """The parameters (coefficients), excl. the intercept."""
        return _handle_rolling_ab(self.solution, self.use_const)[1]

    @property
    def _df_tot(self):
        """Total degrees of freedom, n - 1."""
        return self.n - 1

    @property
    def _df_reg(self):
        """Model degrees of freedom. Equal to k."""
        return self.k

    @property
    def _df_err(self):
        """Residual degrees of freedom. n - k - 1."""
        return self.n - self.k - 1

    @property
    @lru_cache(maxsize=None)
    def _predicted(self):
        """The predicted values of y ('yhat')."""
        pred = np.squeeze(np.matmul(self.wx, np.expand_dims(self.solution, axis=-1)))
        pred[~self.rnn] = np.nan
        pred = pred / self.wgt if self.wgt is not None else pred
        return pred

    @property
    @lru_cache(maxsize=None)
    def _resids(self):
        res = self.wy / self.wgt - self._predicted if self.wgt is not None else self.wy - self._predicted
        return res

    @property
    def _std_err(self):
        """Standard error of the estimate (SEE).  A scalar.
        For standard errors of parameters, see _se_all, se_alpha, and se_beta.
        """
        return np.sqrt(np.sum(np.square(self._resids), axis=1) / self._df_err)

    @property
    def _jarque_bera(self):
        return np.apply_along_axis(scs.jarque_bera, 1, self._resids)[:, 0]

    @property
    @lru_cache(maxsize=None)
    def _ss_err(self):
        """Sum of squares of the residuals (error sum of squares)."""
        return np.sum(np.square(self._resids), axis=1)

    @property
    def _durbin_watson(self):
        return np.sum(
            np.square(np.diff(self._resids))
            / np.expand_dims(self._ss_err, axis=-1),
            axis=1,
        )

    @property
    @lru_cache(maxsize=None)
    def _ybar(self):
        """The mean of y."""
        return self.wy.mean(axis=1)

    @property
    @lru_cache(maxsize=None)
    def _ss_tot(self):
        """Total sum of squares."""
        return np.sum(
            np.square(self.wy - np.expand_dims(self._ybar, axis=-1)), axis=1
        )

    @property
    @lru_cache(maxsize=None)
    def _ss_reg(self):
        """Sum of squares of the regression."""
        return np.sum(
            np.square(self._predicted - np.expand_dims(self._ybar, axis=1)),
            axis=1,
        )

    @property
    def _ms_reg(self):
        """Mean squared error the regression (model)."""
        return self._ss_reg / self._df_reg

    @property
    def _rsq(self):
        """The coefficent of determination, R-squared."""
        return self._ss_reg / self._ss_tot

    @property
    def _rsq_adj(self):
        """Adjusted R-squared."""
        n = self.n
        k = self.k
        return 1.0 - ((1.0 - self._rsq) * (n - 1.0) / (n - k - 1.0))

    @property
    def _ms_err(self):
        """Mean squared error the errors (residuals)."""
        return self._ss_err / self._df_err

    @property
    def _fstat(self):
        """F-statistic of the fully specified model."""
        return self._ms_reg / self._ms_err

    @property
    def _fstat_sig(self):
        """p-value of the F-statistic."""
        return 1.0 - scs.f.cdf(self._fstat, self._df_reg, self._df_err)

    @property
    @lru_cache(maxsize=None)
    def _se_all(self):
        """Standard errors (SE) for all parameters, including the intercept."""
        err = np.expand_dims(self._ms_err, axis=1)
        t1 = np.diagonal(
            np.linalg.inv(np.matmul(self.wx.swapaxes(1, 2), self.wx)),
            axis1=1,
            axis2=2,
        )
        return np.squeeze(np.sqrt(t1 * err))

    @property
    def _se_alpha(self):
        """Standard errors (SE) of the intercept (alpha) only."""
        return _handle_rolling_ab(self._se_all, self.use_const)[0]

    @property
    def _se_beta(self):
        """Standard errors (SE) of the parameters, excluding the intercept."""
        return _handle_rolling_ab(self._se_all, self.use_const)[1]

    @property
    @lru_cache(maxsize=None)
    def _tstat_all(self):
        """The t-statistics of all parameters, incl. the intecept."""
        return self.solution / self._se_all

    @property
    def _tstat_alpha(self):
        """The t-statistic of the intercept (alpha)."""
        return _handle_rolling_ab(self._tstat_all, self.use_const)[0]

    @property
    def _tstat_beta(self):
        """The t-statistics of the parameters, excl. the intecept."""
        return _handle_rolling_ab(self._tstat_all, self.use_const)[1]

    @property
    @lru_cache(maxsize=None)
    def _pvalues_all(self):
        """Two-tailed p values for t-stats of all parameters."""
        return 2.0 * (1.0 - scs.t.cdf(np.abs(self._tstat_all).T, self._df_err).T)

    @property
    def _pvalue_alpha(self):
        """Two-tailed p values for t-stats of the intercept only."""
        return _handle_rolling_ab(self._pvalues_all, self.use_const)[0]

    @property
    def _pvalue_beta(self):
        """Two-tailed p values for t-stats of parameters, excl. intercept."""
        return _handle_rolling_ab(self._pvalues_all, self.use_const)[1]

    @property
    def _condition_number(self):
        """Condition number of x; ratio of largest to smallest eigenvalue."""
        nnwx = self.wx[self.exist]
        ev = np.linalg.eig(np.matmul(nnwx.swapaxes(1, 2), nnwx))[0]
        cn = np.sqrt(ev.max(axis=1) / ev.min(axis=1))
        cn[~self.exist] = np.nan
        return cn

    # -----------------------------------------------------------------
    # "Public" results

    @property
    def alpha(self):
        return self._alpha

    @property
    def beta(self):
        return self._beta

    @property
    def df_tot(self):
        """Total degrees of freedom, n - 1."""
        return self._df_tot

    @property
    def df_reg(self):
        """Model degrees of freedom. Equal to k."""
        return self._df_reg

    @property
    def df_err(self):
        """Residual degrees of freedom. n - k - 1."""
        return self._df_err

    @property
    def std_err(self):
        """Standard error of the estimate (SEE).  A scalar.
        For standard errors of parameters, see _se_all, se_alpha, and se_beta.
        """
        return self._std_err

    @property
    def predicted(self):
        """The predicted values of y ('yhat')."""
        return self._predicted

    @property
    def resids(self):
        return self._resids

    @property
    def jarque_bera(self):
        return self._jarque_bera

    @property
    def durbin_watson(self):
        return self._durbin_watson

    @property
    def ybar(self):
        """The mean of y."""
        return self._ybar

    @property
    def ss_tot(self):
        """Total sum of squares."""
        return self._ss_tot

    @property
    def ss_reg(self):
        """Sum of squares of the regression."""
        return self._ss_reg

    @property
    def ss_err(self):
        """Sum of squares of the residuals (error sum of squares)."""
        return self._ss_err

    @property
    def rsq(self):
        """The coefficent of determination, R-squared."""
        return self._rsq

    @property
    def rsq_adj(self):
        """Adjusted R-squared."""
        return self._rsq_adj

    @property
    def ms_err(self):
        """Mean squared error the errors (residuals)."""
        return self._ms_err

    @property
    def ms_reg(self):
        """Mean squared error the regression (model)."""
        return self._ms_reg

    @property
    def fstat(self):
        """F-statistic of the fully specified model."""
        return self._fstat

    @property
    def fstat_sig(self):
        """p-value of the F-statistic."""
        return self._fstat_sig

    @property
    def se_alpha(self):
        """Standard errors (SE) of the intercept (alpha) only."""
        return self._se_alpha

    @property
    def se_beta(self):
        """Standard errors (SE) of the parameters, excluding the intercept."""
        return self._se_beta

    @property
    def tstat_alpha(self):
        """The t-statistic of the intercept (alpha)."""
        return self._tstat_alpha

    @property
    def tstat_beta(self):
        """The t-statistics of the parameters, excl. the intecept."""
        return self._tstat_beta

    @property
    def pvalue_alpha(self):
        """Two-tailed p values for t-stats of the intercept only."""
        return self._pvalue_alpha

    @property
    def pvalue_beta(self):
        """Two-tailed p values for t-stats of parameters, excl. intercept."""
        return self._pvalue_beta

    @property
    def condition_number(self):
        """Condition number of x; ratio of largest to smallest eigenvalue."""
        return self._condition_number

# TODO: Instead of quasi-private and public attributes, probably should
#       just call super() directly.  I.e.:
#
#    @property
#    def beta(self):
#        return DataFrame(super(PandasRollingOLS, self).beta())

class PandasRollingOLS(RollingOLS):
    def __init__(self, window, y, x=None, thres=0, wgt=None, has_const=False, use_const=True, names=None):

        # A little redundant needing to establish k...
        if not names:
            if x is None:
                if hasattr(y, "columns"):
                    if has_const:
                        names = y.columns[1:-1]
                    else:
                        names = y.columns[1:]
                else:
                    if has_const:
                        k = y.shape[-1] - 2
                    else:
                        k = y.shape[-1] - 1
                    names = ["feature{}".format(i) for i in range(1, k + 1)]
            else:
                if hasattr(x, "columns"):
                    if has_const:
                        names = x.columns[:-1]
                    else:
                        names = x.columns
                else:
                    if has_const:
                        k = x.shape[-1] - 1
                    else:
                        if x.ndim == 1:
                            k = 1
                        else:
                            k = x.shape[-1]
                    names = ["feature{}".format(i) for i in range(1, k + 1)]
        self.names = names

        super(PandasRollingOLS, self).__init__(
            window=window, y=y, x=x, thres=thres, wgt=wgt, has_const=has_const, use_const=use_const
        )

        self.index = y.index
        # Index for the rolling result starts at (window - 1)
        self.ridx = y.index[window - 1 :]

    def _wrap_series(self, stat, name=None):
        if name is None:
            name = stat[1:]
        return Series(getattr(self, stat), index=self.ridx, name=name)

    def _wrap_dataframe(self, stat):
        return DataFrame(
            getattr(self, stat), index=self.ridx, columns=self.names
        )

    def _wrap_multidx(self, stat, name=None):
        if name is None:
            name = stat[1:]
        outer = np.repeat(self.ridx, self.window)
        inner = np.ravel(
            _rolling_windows(self.index.values, window=self.window)
        )
        return Series(
            getattr(self, stat).flatten(), index=[outer, inner], name=name
        ).rename_axis(["end", "subperiod"])

    @property
    def alpha(self):
        return self._wrap_series(stat="_alpha", name="intercept")

    @property
    def beta(self):
        return self._wrap_dataframe(stat="_beta")

    # df_tot, df_reg, df_err are scalars; no override.

    @property
    def std_err(self):
        """Standard error of the estimate (SEE).  A scalar.
        For standard errors of parameters, see _se_all, se_alpha, and se_beta.
        """
        return self._wrap_series(stat="_std_err")

    @property
    def predicted(self):
        """The predicted values of y ('yhat')."""
        return self._wrap_multidx("_predicted")

    @property
    def resids(self):
        return self._wrap_multidx("_resids")

    @property
    def jarque_bera(self):
        return self._wrap_series(stat="_jarque_bera")

    @property
    def durbin_watson(self):
        return self._wrap_series(stat="_durbin_watson")

    @property
    def ybar(self):
        """The mean of y."""
        return self._wrap_series(stat="_ybar")

    @property
    def ss_tot(self):
        """Total sum of squares."""
        return self._wrap_series(stat="_ss_tot")

    @property
    def ss_reg(self):
        """Sum of squares of the regression."""
        return self._wrap_series(stat="_ss_reg")

    @property
    def ss_err(self):
        """Sum of squares of the residuals (error sum of squares)."""
        return self._wrap_series(stat="_ss_err")

    @property
    def rsq(self):
        """The coefficent of determination, R-squared."""
        return self._wrap_series(stat="_rsq")

    @property
    def rsq_adj(self):
        """Adjusted R-squared."""
        return self._wrap_series(stat="_rsq_adj")

    @property
    def ms_err(self):
        """Mean squared error the errors (residuals)."""
        return self._wrap_series(stat="_ms_err")

    @property
    def ms_reg(self):
        """Mean squared error the regression (model)."""
        return self._wrap_series(stat="_ms_reg")

    @property
    def fstat(self):
        """F-statistic of the fully specified model."""
        return self._wrap_series(stat="_fstat")

    @property
    def fstat_sig(self):
        """p-value of the F-statistic."""
        return self._wrap_series(stat="_fstat_sig")

    @property
    def se_alpha(self):
        """Standard errors (SE) of the intercept (alpha) only."""
        return self._wrap_series(stat="_se_alpha")

    @property
    def se_beta(self):
        """Standard errors (SE) of the parameters, excluding the intercept."""
        return self._wrap_dataframe(stat="_se_beta")

    @property
    def tstat_alpha(self):
        """The t-statistic of the intercept (alpha)."""
        return self._wrap_series(stat="_tstat_alpha")

    @property
    def tstat_beta(self):
        """The t-statistics of the parameters, excl. the intecept."""
        return self._wrap_dataframe(stat="_tstat_beta")

    @property
    def pvalue_alpha(self):
        """Two-tailed p values for t-stats of the intercept only."""
        return self._wrap_series(stat="_pvalue_alpha")

    @property
    def pvalue_beta(self):
        """Two-tailed p values for t-stats of parameters, excl. intercept."""
        return self._wrap_dataframe(stat="_pvalue_beta")

    @property
    def condition_number(self):
        """Condition number of x; ratio of largest to smallest eigenvalue."""
        return self._wrap_series(stat="_condition_number")
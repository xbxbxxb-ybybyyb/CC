import numpy as np
import bottleneck
from FactorCalculator_ import bottleneck2


class ArrReshape(object):

    def to2d(self, arr):
        self.freq = arr.shape[1]
        return arr.reshape(arr.shape[0] * arr.shape[1], arr.shape[2])

    def to3d(self, arr):
        return arr.reshape(arr.shape[0] // self.freq, self.freq, arr.shape[1])


def _fill(arr, l, axis=0):
    if arr.ndim == 2:
        return np.pad(arr, ((l, 0), (0, 0)), mode='constant', constant_values=np.nan)

    elif arr.ndim == 3:
        if axis:
            return np.pad(arr, ((0, 0), (l, 0), (0, 0)), mode='constant', constant_values=np.nan)
        else:
            return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)

    else:
        raise ValueError


def abss(x):
    return np.abs(x)


def sqrt(x):
    return np.sqrt(np.abs(x)) * np.sign(x)


def square(x):
    return x ** 2


def cube(x):
    return x ** 3


def neg(x):
    return - x


def inv(x):
    return np.where(x != 0, 1 / x, np.nan)


def log(x):
    return np.where(x > -1, np.log(1 + x), np.nan)


def exp(x):
    return np.exp(x) - 1


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def add2(x, y, w):
    return w * x + (1 - w) * y


def shorten(x, w):
    return w * x


def reducen(x, w):
    return x - w


def relu(x):
    return np.where(x > 0, x, 0)


def max2(x, y):
    return np.fmax(x, y)


def min2(x, y):
    return np.fmin(x, y)


def deviation2(x, y):
    return np.where(x + y != 0, (x - y) / (x + y), 1)


def sign_mul2(x, y):
    return np.sign(x) * y


def mul2(x, y):
    return x * y


def sum2(x, y):
    return x + y


def div2(x, y):
    return np.where(y != 0, x / abss(y), np.nan)


def sub2(x, y):
    return x - y


def abs_sub2(x, y):
    return abss(sub2(x, y))


def percent2(x, y):
    return (x - y) / abss(y)


def pn_condition2(x, y):
    return np.where(x > 1e-6, y, np.where(x < -1e-6, -y, np.nan))


def zero_condition2(x, y):
    return np.where(x > 1e-6, y, np.nan)


def const_condition(x, y, w):
    return np.where(x > w, y, np.nan)


def filter2(x, y):
    return np.where(y > x, y, np.nan)


def true_div2(x, y):
    return np.where(y != 0, x / y, np.nan)


def time_condition(x, t):
    reference = {
        1: [True] * 120 + [False] * 120,
        2: [False] * 120 + [True] * 120,
        3: [True] * 60 + [False] * 180,
        4: [False] * 180 + [True] * 60,
        5: [True] * 60 + [False] * 120 + [True] * 60,
        6: [True] * 180 + [False] * 60,
        7: [False] * 60 + [True] * 180,
        8: [True] * 90 + [False] * 150,
        9: [True] * 150 + [False] * 90,
        10: [True] * 90 + [False] * 60 + [True] * 90,
        11: [False] * 60 + [True] * 60 + [False] * 120,
        12: [False] * 120 + [True] * 60 + [False] * 60,
        13: [False] * 60 + [True] * 120 + [False] * 60,
        14: [True] * 30 + [False] * 210,
        15: [False] * 210 + [True] * 30,
        16: [False] * 30 + [True] * 30 + [False] * 180,
        17: [False] * 180 + [True] * 30 + [False] * 30,
        18: [True] * 30 + [False] * 180 + [True] * 30,
        19: [False] * 30 + [True] * 30 + [False] * 120 + [True] * 30 + [False] * 30,
        20: [False] * 90 + [True] * 60 + [False] * 90,
        21: [False] * 30 + [True] * 180 + [False] * 30,

        22: [True] * 30 + [False] * 210,
        23: [False] * 210 + [True] * 30,
    }

    freq = x.shape[1]
    period = 1 if freq == 242 else 240 // freq
    condition = reference[t][::period]
    if freq == 242:
        condition = [condition[0]] + condition + [condition[-1]]
    condition = np.asanyarray(condition, dtype=bool)[None, :, None]
    return np.where(condition, x, np.nan)


def arr_condition2(x, y):
    return np.where(y > 0, x, np.nan)


def brr_condition2(x, y, w):
    return np.where(y > w, x, np.nan)


def sign(x):
    return np.sign(x)


def cs_rank(x):
    rank = bottleneck.nanrankdata(x, axis=2).astype('float32')
    return rank / np.nanmax(rank, axis=2)[..., None]


def dt_delay(x, m):
    ar = ArrReshape()
    return ar.to3d(_fill(ar.to2d(x)[:-m], m))


def ds_delay(x, d):
    return _fill(x[:-d], d)


def dt_delta(x, m):
    return x - dt_delay(x, m)


def ds_delta(x, d):
    return x - ds_delay(x, d)


def dt_pct(x, m):
    return np.where(x != 0, dt_delta(x, m) / abss(x), np.nan)


def ds_pct(x, d):
    return np.where(x != 0, ds_delta(x, d) / abss(x), np.nan)


def dt_mean(x, m2):
    x = x.copy()
    ar = ArrReshape()
    x = ar.to2d(x)
    xf = np.isfinite(x)
    bottleneck2.clip_array_2d(x)
    cx = bottleneck2.dt_sum(x, m2)
    cn = bottleneck.move_sum(xf.astype('float32'), m2, axis=0)
    return ar.to3d(cx / cn)


def ds_mean(x, d2):
    x = x.copy()
    xf = np.isfinite(x)
    bottleneck2.clip_array_3d(x)
    cx = bottleneck2.ds_sum(x, d2)
    cn = bottleneck.move_sum(xf.astype('float32'), d2, axis=0)
    return cx / cn


def dt_dwm2(x, y, m2):
    x = x.copy()

    ar = ArrReshape()
    x = ar.to2d(x)
    y = ar.to2d(y)
    n = np.isfinite(x) & np.isfinite(y)
    y = np.where(n, y, np.array([0], dtype='float32'))

    bottleneck2.clip_array_2d(x)
    bottleneck2.clip_array_2d(y)
    cy = bottleneck2.dt_sum(y, m2)
    cxy = bottleneck2.dt_sum(x * y, m2)
    return ar.to3d(np.where(cy != 0, cxy / cy, np.nan))


def ds_dwm2(x, y, d2):
    x = x.copy()
    y = y.copy()
    n = np.isfinite(x) & np.isfinite(y)
    bottleneck2.clip_array_3d(x)
    bottleneck2.clip_array_3d(y)
    y = np.where(n, y, np.array([0], dtype='float32'))

    cy = bottleneck2.ds_sum(y, d2)
    cxy = bottleneck2.ds_sum(x * y, d2)
    return np.where(cy != 0, cxy / cy, np.nan)


def dt_std(x, m3):
    x = x.copy()
    ar = ArrReshape()
    x = ar.to2d(x)
    n = np.isfinite(x)
    bottleneck2.clip_array_2d(x)
    cx = bottleneck2.dt_sum(x, m3)
    cx2 = bottleneck2.dt_sum(x ** 2, m3)
    cn = bottleneck.move_sum(n.astype('float32'), m3, axis=0)
    std = (((cx2 - cx ** 2 / cn) / (cn - 1)) ** 0.5)

    std = np.where(cn < 3, np.array([np.nan], dtype='float32'), std)
    return ar.to3d(std)


def ds_std(x, d3):
    x = x.copy()
    n = np.isfinite(x)
    bottleneck2.clip_array_3d(x)
    cx = bottleneck2.ds_sum(x, d3)
    cx2 = bottleneck2.ds_sum(x ** 2, d3)
    cn = bottleneck.move_sum(n.astype('float32'), d3, axis=0)
    std = (((cx2 - cx ** 2 / cn) / (cn - 1)) ** 0.5)

    std = np.where(cn < 3, np.array([np.nan], dtype='float32'), std)
    return std


def dt_sharpe(x, m3):
    x1 = x.copy()
    ar = ArrReshape()
    x1 = ar.to2d(x1)
    n = np.isfinite(x1)
    bottleneck2.clip_array_2d(x1)
    cx = bottleneck2.dt_sum(x1, m3)
    cx2 = bottleneck2.dt_sum(x1 ** 2, m3)
    cn = bottleneck.move_sum(n.astype('float32'), m3, axis=0)
    std = (((cx2 - cx ** 2 / cn) / (cn - 1)) ** 0.5)

    std = np.where((cn < 3) | (std <= 0), np.array([np.nan], dtype='float32'), std)
    sharpe = (ar.to2d(x) - cx / cn) / std
    return ar.to3d(sharpe)


def dt_cv(x, m3):
    x = x.copy()
    ar = ArrReshape()
    x = ar.to2d(x)
    n = np.isfinite(x)
    bottleneck2.clip_array_2d(x)
    cx = bottleneck2.dt_sum(x, m3)
    cx2 = bottleneck2.dt_sum(x ** 2, m3)
    cn = bottleneck.move_sum(n.astype('float32'), m3, axis=0)
    cv = ((cx2 * cn ** 2 / cx ** 2 - cn) / (cn - 1)) ** 0.5

    cv = np.where(cn < 3, np.array([np.nan], dtype='float32'), cv)
    return ar.to3d(cv)


def dt_skew(x, m3):
    x = x.copy()
    ar = ArrReshape()
    x = ar.to2d(x)
    n = np.isfinite(x)
    bottleneck2.clip_array_2d(x)
    cx = bottleneck2.dt_sum(x, m3)
    cx2 = bottleneck2.dt_sum(x ** 2, m3)
    cx3 = bottleneck2.dt_sum(x ** 3, m3)
    cn = bottleneck.move_sum(n.astype('float32'), m3, axis=0)
    const = (cn * (cn - 1)) ** 0.5 / (cn - 2)
    skew = const * (cn ** 2 * cx3 - 3 * cn * cx * cx2 + 2 * cx ** 3
                    ) / (cx2 - cn * cx ** 2) ** 1.5

    skew = np.where(cn < 3, np.array([np.nan], dtype='float32'), skew)
    return ar.to3d(skew)


def ds_skew(x, d3):
    x = x.copy()
    n = np.isfinite(x)
    bottleneck2.clip_array_3d(x)
    cx = bottleneck2.ds_sum(x, d3)
    cx2 = bottleneck2.ds_sum(x ** 2, d3)
    cx3 = bottleneck2.ds_sum(x ** 3, d3)
    cn = bottleneck.move_sum(n.astype('float32'), d3, axis=0)
    const = (cn * (cn - 1)) ** 0.5 / (cn - 2)
    skew = const * (cn ** 2 * cx3 - 3 * cn * cx * cx2 + 2 * cx ** 3
                    ) / (cx2 - cn * cx ** 2) ** 1.5

    skew = np.where(cn < 3, np.array([np.nan], dtype='float32'), skew)
    return skew


def dt_kurt(x, m4):
    x = x.copy()
    ar = ArrReshape()
    x = ar.to2d(x)
    n = np.isfinite(x)
    bottleneck2.clip_array_2d(x)
    cx = bottleneck2.dt_sum(x, m4)
    cx2 = bottleneck2.dt_sum(x ** 2, m4)
    cx3 = bottleneck2.dt_sum(x ** 3, m4)
    cx4 = bottleneck2.dt_sum(x ** 4, m4)
    cn = bottleneck.move_sum(n.astype('float32'), m4, axis=0)
    const = (cn - 1) / (cn - 2) / (cn - 3)
    kurt = const * ((cn + 1) * (cn ** 3 * cx4 - 4 * cn ** 2 * cx3 *
                                cx + 6 * cn * cx2 * cx ** 2 - 3 * cx ** 4) / (
                            cn ** 2 * cx2 ** 2 - 2 * cn * cx2 * cx ** 2 + cx ** 4) - 3 * (cn - 1))

    kurt = np.where(cn < 4, np.array([np.nan], dtype='float32'), kurt)
    return ar.to3d(kurt)


def ds_kurt(x, d4):
    x = x.copy()
    n = np.isfinite(x)
    bottleneck2.clip_array_3d(x)
    cx = bottleneck2.ds_sum(x, d4)
    cx2 = bottleneck2.ds_sum(x ** 2, d4)
    cx3 = bottleneck2.ds_sum(x ** 3, d4)
    cx4 = bottleneck2.ds_sum(x ** 4, d4)
    cn = bottleneck.move_sum(n.astype('float32'), d4, axis=0)
    const = (cn - 1) / (cn - 2) / (cn - 3)
    kurt = const * ((cn + 1) * (cn ** 3 * cx4 - 4 * cn ** 2 * cx3 *
                                cx + 6 * cn * cx2 * cx ** 2 - 3 * cx ** 4) / (
                            cn ** 2 * cx2 ** 2 - 2 * cn * cx2 * cx ** 2 + cx ** 4) - 3 * (cn - 1))

    kurt = np.where(cn < 4, np.array([np.nan], dtype='float32'), kurt)
    return kurt


def dt_corr2(x, y, m3):
    ar = ArrReshape()
    x = ar.to2d(x)
    y = ar.to2d(y)
    n = np.isfinite(x) & np.isfinite(y)

    x = np.where(n, x, np.array([0], dtype='float32'))
    y = np.where(n, y, np.array([0], dtype='float32'))
    bottleneck2.clip_array_2d(x)
    bottleneck2.clip_array_2d(y)
    cx = bottleneck2.dt_sum(x, m3)
    cx2 = bottleneck2.dt_sum(x ** 2, m3)
    cy = bottleneck2.dt_sum(y, m3)
    cy2 = bottleneck2.dt_sum(y ** 2, m3)
    cxy = bottleneck2.dt_sum(x * y, m3)
    cn = bottleneck.move_sum(n.astype('float32'), m3, axis=0)
    corr = (cn * cxy - cx * cy) / np.sqrt((cn * cx2 - cx ** 2) * (cn * cy2 - cy ** 2))

    corr = np.where(cn < 3, np.array([np.nan], dtype='float32'), corr)
    return ar.to3d(corr)


def ds_corr2(x, y, d3):
    n = np.isfinite(x) & np.isfinite(y)

    x = np.where(n, x, np.array([0], dtype='float32'))
    y = np.where(n, y, np.array([0], dtype='float32'))
    bottleneck2.clip_array_3d(x)
    bottleneck2.clip_array_3d(y)
    cx = bottleneck2.ds_sum(x, d3)
    cx2 = bottleneck2.ds_sum(x ** 2, d3)
    cy = bottleneck2.ds_sum(y, d3)
    cy2 = bottleneck2.ds_sum(y ** 2, d3)
    cxy = bottleneck2.ds_sum(x * y, d3)
    cn = bottleneck.move_sum(n.astype('float32'), d3, axis=0)
    corr = (cn * cxy - cx * cy) / np.sqrt((cn * cx2 - cx ** 2) * (cn * cy2 - cy ** 2))

    corr = np.where(cn < 3, np.array([np.nan], dtype='float32'), corr)
    return corr


def dt_beta2(x, y, m3):
    ar = ArrReshape()
    x = ar.to2d(x)
    y = ar.to2d(y)
    n = np.isfinite(x) & np.isfinite(y)

    x = np.where(n, x, np.array([0], dtype='float32'))
    y = np.where(n, y, np.array([0], dtype='float32'))
    bottleneck2.clip_array_2d(x)
    bottleneck2.clip_array_2d(y)
    cx = bottleneck2.dt_sum(x, m3)
    cx2 = bottleneck2.dt_sum(x ** 2, m3)
    cy = bottleneck2.dt_sum(y, m3)
    cxy = bottleneck2.dt_sum(x * y, m3)
    cn = bottleneck.move_sum(n.astype('float32'), m3, axis=0)
    beta = (cn * cxy - cx * cy) / (cn * cx2 - cx ** 2)

    beta = np.where(cn < 3, np.array([np.nan], dtype='float32'), beta)
    return ar.to3d(beta)


def ds_beta2(x, y, d3):
    n = np.isfinite(x) & np.isfinite(y)

    x = np.where(n, x, np.array([0], dtype='float32'))
    y = np.where(n, y, np.array([0], dtype='float32'))
    bottleneck2.clip_array_3d(x)
    bottleneck2.clip_array_3d(y)
    cx = bottleneck2.ds_sum(x, d3)
    cx2 = bottleneck2.ds_sum(x ** 2, d3)
    cy = bottleneck2.ds_sum(y, d3)
    cxy = bottleneck2.ds_sum(x * y, d3)
    cn = bottleneck.move_sum(n.astype('float32'), d3, axis=0)
    beta = (cn * cxy - cx * cy) / (cn * cx2 - cx ** 2)

    beta = np.where(cn < 3, np.array([np.nan], dtype='float32'), beta)
    return beta


def dt_intercept2(x, y, m3):
    ar = ArrReshape()
    x = ar.to2d(x)
    y = ar.to2d(y)
    n = np.isfinite(x) & np.isfinite(y)

    x = np.where(n, x, np.array([0], dtype='float32'))
    y = np.where(n, y, np.array([0], dtype='float32'))
    bottleneck2.clip_array_2d(x)
    bottleneck2.clip_array_2d(y)
    cx = bottleneck2.dt_sum(x, m3)
    cx2 = bottleneck2.dt_sum(x ** 2, m3)
    cy = bottleneck2.dt_sum(y, m3)
    cxy = bottleneck2.dt_sum(x * y, m3)
    cn = bottleneck.move_sum(n.astype('float32'), m3, axis=0)
    beta = (cn * cxy - cx * cy) / (cn * cx2 - cx ** 2)
    intercept = (cy - beta * cx) / cn

    intercept = np.where(cn < 3, np.array([np.nan], dtype='float32'), intercept)
    return ar.to3d(intercept)


def ds_intercept2(x, y, d3):
    n = np.isfinite(x) & np.isfinite(y)

    x = np.where(n, x, np.array([0], dtype='float32'))
    y = np.where(n, y, np.array([0], dtype='float32'))
    bottleneck2.clip_array_3d(x)
    bottleneck2.clip_array_3d(y)
    cx = bottleneck2.ds_sum(x, d3)
    cx2 = bottleneck2.ds_sum(x ** 2, d3)
    cy = bottleneck2.ds_sum(y, d3)
    cxy = bottleneck2.ds_sum(x * y, d3)
    cn = bottleneck.move_sum(n.astype('float32'), d3, axis=0)
    beta = (cn * cxy - cx * cy) / (cn * cx2 - cx ** 2)
    intercept = (cy - beta * cx) / cn

    intercept = np.where(cn < 3, np.array([np.nan], dtype='float32'), intercept)
    return intercept


def dt_alpha2(x, y, m3):
    return y - x * dt_beta2(x, y, m3)


def ds_alpha2(x, y, d3):
    return y - x * ds_beta2(x, y, d3)


def dt_resid2(x, y, m3):
    ar = ArrReshape()
    x = ar.to2d(x)
    y = ar.to2d(y)
    n = np.isfinite(x) & np.isfinite(y)

    x = np.where(n, x, np.array([0], dtype='float32'))
    y = np.where(n, y, np.array([0], dtype='float32'))
    bottleneck2.clip_array_2d(x)
    bottleneck2.clip_array_2d(y)
    cx = bottleneck2.dt_sum(x, m3)
    cx2 = bottleneck2.dt_sum(x ** 2, m3)
    cy = bottleneck2.dt_sum(y, m3)
    cxy = bottleneck2.dt_sum(x * y, m3)
    cn = bottleneck.move_sum(n.astype('float32'), m3, axis=0)
    beta = (cn * cxy - cx * cy) / (cn * cx2 - cx ** 2)

    beta = np.where(cn < 3, np.array([np.nan], dtype='float32'), beta)
    intercept = (cy - beta * cx) / cn
    return ar.to3d(y - intercept - x * beta)


def ds_resid2(x, y, d3):
    n = np.isfinite(x) & np.isfinite(y)

    x = np.where(n, x, np.array([0], dtype='float32'))
    y = np.where(n, y, np.array([0], dtype='float32'))
    bottleneck2.clip_array_3d(x)
    bottleneck2.clip_array_3d(y)
    cx = bottleneck2.ds_sum(x, d3)
    cx2 = bottleneck2.ds_sum(x ** 2, d3)
    cy = bottleneck2.ds_sum(y, d3)
    cxy = bottleneck2.ds_sum(x * y, d3)
    cn = bottleneck.move_sum(n.astype('float32'), d3, axis=0)
    beta = (cn * cxy - cx * cy) / (cn * cx2 - cx ** 2)

    beta = np.where(cn < 3, np.array([np.nan], dtype='float32'), beta)
    intercept = (cy - beta * cx) / cn
    return y - intercept - x * beta


def dt_nonlinear_alpha(x, m3):
    x = x.copy()
    ar = ArrReshape()
    x = ar.to2d(x)
    n = np.isfinite(x)
    bottleneck2.clip_array_2d(x)
    y = x ** 3
    cx = bottleneck2.dt_sum(x, m3)
    cx2 = bottleneck2.dt_sum(x ** 2, m3)
    cx3 = bottleneck2.dt_sum(y, m3)
    cx4 = bottleneck2.dt_sum(x ** 4, m3)
    cn = bottleneck.move_sum(n.astype('float32'), m3, axis=0)
    beta = (cn * cx4 - cx * cx3) / (cn * cx2 - cx ** 2)

    beta = np.where(cn < 3, np.array([np.nan], dtype='float32'), beta)

    x = np.where(n, x, np.array([np.nan], dtype='float32'))

    y = np.where(n, y, np.array([np.nan], dtype='float32'))
    return ar.to3d(y - x * beta)


def ts_cumsum(x):
    x = np.where(np.isfinite(x), x, np.array([np.nan], dtype='float32'))
    return np.nancumsum(x, axis=1)


def ts_cummean(x):
    cn = np.cumsum(np.isfinite(x).astype('float32'), axis=1)
    return ts_cumsum(x) / cn


def ts_cumstd(x):
    n = np.isfinite(x)

    x = np.where(n, x, np.array([0], dtype='float32'))
    cx = np.cumsum(x, axis=1)
    cx2 = np.cumsum(x ** 2, axis=1)
    cn = np.cumsum(n.astype('float32'), axis=1)
    std = np.sqrt((cx2 - cx ** 2 / cn) / (cn - 1))

    std = np.where(cn < 3, np.array([np.nan], dtype='float32'), std)
    return std


def ts_cumskew(x):
    n = np.isfinite(x)

    x = np.where(n, x, np.array([0], dtype='float32'))
    cx = np.cumsum(x, axis=1)
    cx2 = np.cumsum(x ** 2, axis=1)
    cx3 = np.cumsum(x ** 3, axis=1)
    cn = np.cumsum(n.astype('float32'), axis=1)
    const = (cn * (cn - 1)) ** 0.5 / (cn - 2)
    skew = const * (cn ** 2 * cx3 - 3 * cn * cx * cx2 + 2 * cx ** 3
                    ) / (cx2 - cn * cx ** 2) ** 1.5

    skew = np.where(cn < 3, np.array([np.nan], dtype='float32'), skew)
    return skew


def ts_cumkurt(x):
    n = np.isfinite(x)

    x = np.where(n, x, np.array([0], dtype='float32'))
    cx = np.cumsum(x, axis=1)
    cx2 = np.cumsum(x ** 2, axis=1)
    cx3 = np.cumsum(x ** 3, axis=1)
    cx4 = np.cumsum(x ** 4, axis=1)
    cn = np.cumsum(n.astype('float32'), axis=1)
    const = (cn - 1) / (cn - 2) / (cn - 3)
    kurt = const * ((cn + 1) * (cn ** 3 * cx4 - 4 * cn ** 2 * cx3 *
                                cx + 6 * cn * cx2 * cx ** 2 - 3 * cx ** 4) / (
                            cn ** 2 * cx2 ** 2 - 2 * cn * cx2 * cx ** 2 + cx ** 4) - 3 * (cn - 1))

    kurt = np.where(cn < 4, np.array([np.nan], dtype='float32'), kurt)
    return kurt


def ts_cumcorr2(x, y):
    n = np.isfinite(x) & np.isfinite(y)

    x = np.where(n, x, np.array([0], dtype='float32'))
    y = np.where(n, y, np.array([0], dtype='float32'))
    cx = np.cumsum(x, axis=1)
    cy = np.cumsum(y, axis=1)
    cx2 = np.cumsum(x ** 2, axis=1)
    cy2 = np.cumsum(y ** 2, axis=1)
    cxy = np.cumsum(x * y, axis=1)
    cn = np.cumsum(n.astype('float32'), axis=1)
    corr = (cn * cxy - cx * cy) / np.sqrt((cn * cx2 - cx ** 2) * (cn * cy2 - cy ** 2))
    corr = np.where(cn < 3, np.array([np.nan], dtype='float32'), corr)

    return corr


def ts_cumbeta2(x, y):
    n = np.isfinite(x) & np.isfinite(y)

    x = np.where(n, x, np.array([0], dtype='float32'))
    y = np.where(n, y, np.array([0], dtype='float32'))
    cx = np.cumsum(x, axis=1)
    cy = np.cumsum(y, axis=1)
    cx2 = np.cumsum(x ** 2, axis=1)
    cxy = np.cumsum(x * y, axis=1)
    cn = np.cumsum(n.astype('float32'), axis=1)
    beta = (cn * cxy - cx * cy) / (cn * cx2 - cx ** 2)

    beta = np.where(cn < 3, np.array([np.nan], dtype='float32'), beta)
    return beta


def ts_cumintercept2(x, y):
    n = np.isfinite(x) & np.isfinite(y)

    x = np.where(n, x, np.array([0], dtype='float32'))
    y = np.where(n, y, np.array([0], dtype='float32'))
    cx = np.cumsum(x, axis=1)
    cy = np.cumsum(y, axis=1)
    cx2 = np.cumsum(x ** 2, axis=1)
    cxy = np.cumsum(x * y, axis=1)
    cn = np.cumsum(n.astype('float32'), axis=1)
    beta = (cn * cxy - cx * cy) / (cn * cx2 - cx ** 2)

    beta = np.where(cn < 3, np.array([np.nan], dtype='float32'), beta)
    intercept = (cy - cx * beta) / cn
    return intercept


def ts_cumresid2(x, y):
    n = np.isfinite(x) & np.isfinite(y)

    x = np.where(n, x, np.array([0], dtype='float32'))
    y = np.where(n, y, np.array([0], dtype='float32'))
    cx = np.cumsum(x, axis=1)
    cy = np.cumsum(y, axis=1)
    cx2 = np.cumsum(x ** 2, axis=1)
    cxy = np.cumsum(x * y, axis=1)
    cn = np.cumsum(n.astype('float32'), axis=1)
    beta = (cn * cxy - cx * cy) / (cn * cx2 - cx ** 2)

    beta = np.where(cn < 3, np.array([np.nan], dtype='float32'), beta)
    intercept = (cy - cx * beta) / cn
    resid = y - intercept - x * beta

    resid = np.where(~ n, np.array([np.nan], dtype='float32'), resid)
    return resid


def ts_cumalpha2(x, y):
    n = np.isfinite(x) & np.isfinite(y)

    x = np.where(n, x, np.array([0], dtype='float32'))
    y = np.where(n, y, np.array([0], dtype='float32'))
    cx = np.cumsum(x, axis=1)
    cy = np.cumsum(y, axis=1)
    cx2 = np.cumsum(x ** 2, axis=1)
    cxy = np.cumsum(x * y, axis=1)
    cn = np.cumsum(n.astype('float32'), axis=1)
    beta = (cn * cxy - cx * cy) / (cn * cx2 - cx ** 2)

    beta = np.where(cn < 3, np.array([np.nan], dtype='float32'), beta)
    alpha = y - x * beta

    alpha = np.where(~ n, np.array([np.nan], dtype='float32'), alpha)
    return alpha


def ts_dwm2(x, y):
    n = np.isfinite(x) & np.isfinite(y)

    y = np.where(n, y, np.array([0], dtype='float32'))
    cxy = ts_cumsum(x * y)
    cy = ts_cumsum(y)
    return np.where(cy != 0, cxy / cy, np.nan)


def dt_ewm_new(x, m2):
    ar = ArrReshape()
    alpha = 0.5 ** (2 / m2)
    weight = alpha ** np.arange(m2).astype('float32')
    x = ar.to2d(x)
    ewa = bottleneck2.dt_ewa(x, weight)
    return ar.to3d(ewa)


def ds_ewm_new(x, d2):
    alpha = 0.5 ** (2 / d2)
    weight = alpha ** np.arange(d2).astype('float32')
    ewa = bottleneck2.ds_ewa(x, weight)
    return ewa


def dt_lwm_new(x, m2):
    ar = ArrReshape()
    weight = np.arange(m2)[::-1].astype('float32') + 1
    x = ar.to2d(x)
    ewa = bottleneck2.dt_ewa(x, weight)
    return ar.to3d(ewa)


def ds_lwm_new(x, d2):
    weight = np.arange(d2)[::-1].astype('float32') + 1
    ewa = bottleneck2.ds_sum(x, weight)
    return ewa


def dt_cwm_new(x, m2):
    x = x.copy()
    ar = ArrReshape()
    alpha = 0.5 ** (2 / m2)
    weight = alpha ** np.arange(m2).astype('float32')
    weight = weight[::-1].cumsum()[::-1]
    x = ar.to2d(x)
    ewa = bottleneck2.dt_ewa(x, weight)
    return ar.to3d(ewa)


def ds_cwm_new(x, d2):
    alpha = 0.5 ** (2 / d2)
    weight = alpha ** np.arange(d2).astype('float32')
    weight = weight[::-1].cumsum()[::-1]
    ewa = bottleneck2.ds_sum(x, weight)
    return ewa


def max_min_ewm_dev2(x, y, m2):
    x = np.where(np.isfinite(x), x, np.array([np.nan], dtype='float32'))
    y = np.where(np.isfinite(y), y, np.array([np.nan], dtype='float32'))
    x1 = dt_ewm(np.where(x > y, x, 0), m2)
    y1 = dt_ewm(np.where(y > x, y, 0), m2)
    return deviation2(x1, y1)


def ts_cummax(x):
    return bottleneck2.ts_cummax(x)


def ts_cummin(x):
    return bottleneck2.ts_cummin(x)


def ts_cumargmax(x):
    return bottleneck2.ts_cumargmax(x)


def ts_cumargmin(x):
    return bottleneck2.ts_cumargmin(x)


def dt_median(x, m3):
    ar = ArrReshape()
    x = ar.to2d(x)
    n = np.isfinite(x)
    cn = bottleneck.move_sum(n.astype('float32'), m3, axis=0)
    n2 = (~ n).astype('float32').cumsum(axis=0) % 2 == 0
    x = np.where(~n & n2, np.array([np.inf], dtype='float32'),
                 np.where(~n & ~n2, np.array([- np.inf], dtype='float32'), x))

    mx = bottleneck.move_median(x, m3, axis=0)
    x = np.where(~n, -x, x)

    mx_ = bottleneck.move_median(x, m3, axis=0)

    mx = (mx + mx_) / 2

    mx = np.where((cn < 3) | ~ np.isfinite(mx), np.array([np.nan], dtype='float32'), mx)
    return ar.to3d(mx)


def ds_median(x, d3):
    n = np.isfinite(x)
    cn = bottleneck.move_sum(n.astype('float32'), d3, axis=0)
    n2 = (~ n).astype('float32').cumsum(axis=0) % 2 == 0

    x = np.where(~n & n2, np.array([np.inf], dtype='float32'),
                 np.where(~n & ~n2, np.array([- np.inf], dtype='float32'), x))
    mx = bottleneck.move_median(x, d3, axis=0)
    x = np.where(~n, -x, x)

    mx_ = bottleneck.move_median(x, d3, axis=0)

    mx = (mx + mx_) / 2

    mx = np.where((cn < 3) | ~ np.isfinite(mx), np.array([np.nan], dtype='float32'), mx)
    return mx


def dt_min(x, m4):
    ar = ArrReshape()
    x = ar.to2d(x)

    x = np.where(~ np.isfinite(x), np.array([np.inf], dtype='float32'), x)
    x = bottleneck.move_min(x, m4, axis=0)

    x = np.where(~ np.isfinite(x), np.array([np.nan], dtype='float32'), x)
    return ar.to3d(x)


def ds_min(x, d4):
    x = np.where(~ np.isfinite(x), np.array([np.inf], dtype='float32'), x)
    x = bottleneck.move_min(x, d4, axis=0)

    x = np.where(~ np.isfinite(x), np.array([np.nan], dtype='float32'), x)
    return x


def dt_max(x, m4):
    ar = ArrReshape()
    x = ar.to2d(x)

    x = np.where(~ np.isfinite(x), np.array([- np.inf], dtype='float32'), x)
    x = bottleneck.move_max(x, m4, axis=0)

    x = np.where(~ np.isfinite(x), np.array([np.nan], dtype='float32'), x)
    return ar.to3d(x)


def ds_max(x, d4):
    x = np.where(~ np.isfinite(x), np.array([- np.inf], dtype='float32'), x)
    x = bottleneck.move_max(x, d4, axis=0)

    x = np.where(~ np.isfinite(x), np.array([np.nan], dtype='float32'), x)
    return x


def dt_argmax(x, m4):
    ar = ArrReshape()
    x = ar.to2d(x)

    x = np.where(~ np.isfinite(x), np.array([- np.inf], dtype='float32'), x)
    x = bottleneck.move_argmax(x, m4, axis=0) / (m4 - 1)

    x = np.where(~ np.isfinite(x), np.array([np.nan], dtype='float32'), x)
    return ar.to3d(x)


def ds_argmax(x, d4):
    x = np.where(~ np.isfinite(x), np.array([- np.inf], dtype='float32'), x)
    x = bottleneck.move_argmax(x, d4, axis=0) / (d4 - 1)

    x = np.where(~ np.isfinite(x), np.array([np.nan], dtype='float32'), x)
    return x


def dt_argmin(x, m4):
    ar = ArrReshape()
    x = ar.to2d(x)

    x = np.where(~ np.isfinite(x), np.array([np.inf], dtype='float32'), x)
    x = bottleneck.move_argmin(x, m4, axis=0) / (m4 - 1)

    x = np.where(~ np.isfinite(x), np.array([np.nan], dtype='float32'), x)
    return ar.to3d(x)


def ds_argmin(x, d4):
    x = np.where(~ np.isfinite(x), np.array([np.inf], dtype='float32'), x)
    x = bottleneck.move_argmin(x, d4, axis=0) / (d4 - 1)

    x = np.where(~ np.isfinite(x), np.array([np.nan], dtype='float32'), x)
    return x


def dt_rank(x, m4):
    ar = ArrReshape()
    x = ar.to2d(x)
    n = np.isfinite(x)
    cn = bottleneck.move_sum(n.astype('float32'), m4, axis=0)

    x = np.where(~ n, np.array([-np.inf], dtype='float32'), x)
    mx = bottleneck.move_rank(x, m4, axis=0)
    mx = ((mx + 1) * (m4 - 1) / 2 - m4 + cn) / (cn - 1)
    mx = np.where((cn < 4) | ~ n, np.array([np.nan], dtype='float32'), mx)

    return ar.to3d(mx)


def ds_rank(x, d4):
    n = np.isfinite(x)
    cn = bottleneck.move_sum(n.astype('float32'), d4, axis=0)

    x = np.where(~ n, np.array([-np.inf], dtype='float32'), x)
    mx = bottleneck.move_rank(x, d4, axis=0)
    mx = ((mx + 1) * (d4 - 1) / 2 - d4 + cn) / (cn - 1)
    mx = np.where((cn < 4) | ~ n, np.array([np.nan], dtype='float32'), mx)

    return mx


def dt_ewm(x, m2):
    ar = ArrReshape()
    alpha = 0.5 ** (2 / m2)
    weight = alpha ** np.arange(m2).astype('float32')
    x = ar.to2d(x)
    xf = np.isfinite(x)

    x = np.where(~ xf, np.array([0], dtype='float32'), x)
    cx = np.apply_along_axis(np.convolve, 0, x, weight, 'valid')
    cw = np.apply_along_axis(np.convolve, 0, xf, weight, 'valid')
    cn = bottleneck.move_sum(xf.astype('float32'), m2, axis=0)[m2 - 1:]
    cw = np.where(cn < m2 / 2, np.array([np.nan], dtype='float32'), cw)

    return ar.to3d(_fill(cx / cw, m2 - 1))


def dt_lwm(x, m2):
    ar = ArrReshape()
    weight = np.arange(m2)[::-1].astype('float32') + 1
    x = ar.to2d(x)
    xf = np.isfinite(x)

    x = np.where(~ xf, np.array([0], dtype='float32'), x)
    cx = np.apply_along_axis(np.convolve, 0, x, weight, 'valid')
    cw = np.apply_along_axis(np.convolve, 0, xf, weight, 'valid')
    cn = bottleneck.move_sum(xf.astype('float32'), m2, axis=0)[m2 - 1:]
    cw = np.where(cn < m2 / 2, np.array([np.nan], dtype='float32'), cw)

    return ar.to3d(_fill(cx / cw, m2 - 1))


def dt_cwm(x, m2):
    ar = ArrReshape()
    alpha = 0.5 ** (2 / m2)
    weight = alpha ** np.arange(m2).astype('float32')
    weight = weight[::-1].cumsum()[::-1]
    x = ar.to2d(x)
    xf = np.isfinite(x)

    x = np.where(~ xf, np.array([0], dtype='float32'), x)
    cx = np.apply_along_axis(np.convolve, 0, x, weight, 'valid')
    cw = np.apply_along_axis(np.convolve, 0, xf, weight, 'valid')
    cn = bottleneck.move_sum(xf.astype('float32'), m2, axis=0)[m2 - 1:]
    cw = np.where(cn < m2 / 2, np.array([np.nan], dtype='float32'), cw)

    return ar.to3d(_fill(cx / cw, m2 - 1))


def ds_ewm(x, d2):
    alpha = 0.5 ** (2 / d2)
    weight = alpha ** np.arange(d2).astype('float32')
    xf = np.isfinite(x)

    x = np.where(~ xf, np.array([0], dtype='float32'), x)
    cx = np.apply_along_axis(np.convolve, 0, x, weight, 'valid')
    cw = np.apply_along_axis(np.convolve, 0, xf, weight, 'valid')
    cn = bottleneck.move_sum(xf.astype('float32'), d2, axis=0)[d2 - 1:]
    cw = np.where(cn < d2 / 2, np.array([np.nan], dtype='float32'), cw)

    return _fill(cx / cw, d2 - 1)


def ds_lwm(x, d2):
    weight = np.arange(d2)[::-1].astype('float32') + 1
    xf = np.isfinite(x)

    x = np.where(~ xf, np.array([0], dtype='float32'), x)
    cx = np.apply_along_axis(np.convolve, 0, x, weight, 'valid')
    cw = np.apply_along_axis(np.convolve, 0, xf, weight, 'valid')
    cn = bottleneck.move_sum(xf.astype('float32'), d2, axis=0)[d2 - 1:]
    cw = np.where(cn < d2 / 2, np.array([np.nan], dtype='float32'), cw)

    return _fill(cx / cw, d2 - 1)


def ds_cwm(x, d2):
    alpha = 0.5 ** (2 / d2)
    weight = alpha ** np.arange(d2).astype('float32')
    weight = weight[::-1].cumsum()[::-1]
    xf = np.isfinite(x)

    x = np.where(~ xf, np.array([0], dtype='float32'), x)
    cx = np.apply_along_axis(np.convolve, 0, x, weight, 'valid')
    cw = np.apply_along_axis(np.convolve, 0, xf, weight, 'valid')
    cn = bottleneck.move_sum(xf.astype('float32'), d2, axis=0)[d2 - 1:]
    cw = np.where(cn < d2 / 2, np.array([np.nan], dtype='float32'), cw)

    return _fill(cx / cw, d2 - 1)


def ts_ols_rmse2(x, y, m3):
    ar = ArrReshape()
    x = ar.to2d(x)
    y = ar.to2d(y)
    n = np.isfinite(x) & np.isfinite(y)
    x = np.where(n, x, np.array([0], dtype='float32'))
    y = np.where(n, y, np.array([0], dtype='float32'))
    bottleneck2.clip_array_2d(x)
    bottleneck2.clip_array_2d(y)
    cx = bottleneck2.dt_sum(x, m3)
    cx2 = bottleneck2.dt_sum(x ** 2, m3)
    cy = bottleneck2.dt_sum(y, m3)
    cy2 = bottleneck2.dt_sum(y ** 2, m3)
    cxy = bottleneck2.dt_sum(x * y, m3)
    cn = bottleneck.move_sum(n.astype('float32'), m3, axis=0)
    beta = (cn * cxy - cx * cy) / (cn * cx2 - cx ** 2)
    alpha = (cy - beta * cx) / cn
    mse = (cy2 + beta ** 2 * cx2 + cn * alpha ** 2 - 2 * beta * cxy -
           2 * alpha * cy + 2 * alpha * beta * cx) / cn
    mse = np.where(cn < 3, np.array([np.nan], dtype='float32'), mse)
    rmse = mse ** 0.5
    return ar.to3d(rmse)

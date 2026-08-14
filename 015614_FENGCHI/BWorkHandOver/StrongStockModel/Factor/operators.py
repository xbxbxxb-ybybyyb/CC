from groupTrueSend.utils import ArrReshape, _fill, _ffill, _roll_fill
import numpy as np
import bottleneck


def abss(x):
    return np.abs(x)


def sign(x):
    return np.sign(x)


def sqrt(x):
    return np.sqrt(np.abs(x)) * np.sign(x)


def square(x):
    return x ** 2


def cube(x):
    return x ** 3


def neg(x):
    return - x


def inv(x):
    return _ffill(np.where(x != 0, 1 / x, np.nan))


def log(x):
    return _ffill(np.where(x > -1, np.log(1 + x), np.nan))


def exp(x):
    return np.exp(x) - 1


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def dt_cumsum(x):
    ar = ArrReshape()
    return ar.to3d(np.nancumsum(ar.to2d(x), axis=0))


def dt_delay(x, m):
    ar = ArrReshape()
    return ar.to3d(_fill(ar.to2d(x)[:-m], m))


def dt_delta(x, m):
    return x - dt_delay(x, m)


def dt_pct(x, m):
    return _ffill(np.where(x != 0, dt_delta(x, m) / abss(x), np.nan))


def dt_mean(x, m2):
    ar = ArrReshape()
    return ar.to3d(bottleneck.move_mean(ar.to2d(x), m2, axis=0))


def dt_ewm(x, m2):
    ar = ArrReshape()
    alpha = 0.5 ** (2 / m2)
    weight = alpha ** np.arange(m2).astype(float)
    weight /= weight.sum()
    return ar.to3d(_fill(np.apply_along_axis(np.convolve, 0, ar.to2d(x), weight, 'valid'), m2 - 1))


def dt_lwm(x, m2):
    ar = ArrReshape()
    weight = np.arange(m2)[::-1].astype(float) + 1
    weight /= weight.sum()
    return ar.to3d(_fill(np.apply_along_axis(np.convolve, 0, ar.to2d(x), weight, 'valid'), m2 - 1))


def dt_cwm(x, m2):
    ar = ArrReshape()
    alpha = 0.5 ** (2 / m2)
    weight = alpha ** np.arange(m2).astype(float)
    weight = weight[::-1].cumsum()[::-1]
    weight /= weight.sum()
    return ar.to3d(_fill(np.apply_along_axis(np.convolve, 0, ar.to2d(x), weight, 'valid'), m2 - 1))


def dt_median(x, m3):
    ar = ArrReshape()
    return ar.to3d(bottleneck.move_median(ar.to2d(x), m3, axis=0))


def dt_min(x, m4):
    ar = ArrReshape()
    return ar.to3d(bottleneck.move_min(ar.to2d(x), m4, axis=0))


def dt_max(x, m4):
    ar = ArrReshape()
    return ar.to3d(bottleneck.move_max(ar.to2d(x), m4, axis=0))


def dt_argmax(x, m4):
    ar = ArrReshape()
    return ar.to3d(bottleneck.move_argmax(ar.to2d(x), m4, axis=0)) / (m4 - 1)


def dt_argmin(x, m4):
    ar = ArrReshape()
    return ar.to3d(bottleneck.move_argmin(ar.to2d(x), m4, axis=0)) / (m4 - 1)


def dt_rank(x, m4):
    ar = ArrReshape()
    return (ar.to3d(bottleneck.move_rank(ar.to2d(x), m4, axis=0)) + 1) / 2


def dt_std(x, m3):
    ar = ArrReshape()
    return ar.to3d(bottleneck.move_std(ar.to2d(x), m3, axis=0))


def dt_skew(x, m3):
    m3 = 3 if m3 < 3 else m3
    ar = ArrReshape()
    x = ar.to2d(x)
    x = x - bottleneck.move_mean(x, m3, axis=0)
    const = (m3 - 1) ** (1 / 2) * m3 ** (1 / 6) / (m3 - 2)
    skew = const * bottleneck.move_sum(x ** 3, m3, axis=0) / (
        bottleneck.move_sum(x ** 2, m3, axis=0)) ** 1.5
    return ar.to3d(skew)


def dt_kurt(x, m4):
    m4 = 4 if m4 < 4 else m4
    ar = ArrReshape()
    x = ar.to2d(x)
    x = x - bottleneck.move_mean(x, m4, axis=0)
    const1 = (m4 + 1) * m4 * (m4 - 1) / (m4 - 2) / (m4 - 3)
    const2 = 3 * (m4 - 1) ** 2 / (m4 - 2) / (m4 - 3)
    kurt = const1 * bottleneck.move_sum(x ** 4, m4, axis=0) / (
        bottleneck.move_sum(x ** 2, m4, axis=0)) ** 2 - const2
    return ar.to3d(kurt)


def ds_cumsum(x):
    return np.nancumsum(x, axis=0)


def ds_delay(x, d):
    return _fill(x[:-d], d)


def ds_delta(x, d):
    return x - ds_delay(x, d)


def ds_pct(x, d):
    return _ffill(np.where(x != 0, ds_delta(x, d) / abss(x), np.nan))


def ds_mean(x, d2):
    return bottleneck.move_mean(x, d2, axis=0)


def ds_ewm(x, d2):
    alpha = 0.5 ** (2 / d2)
    weight = alpha ** np.arange(d2).astype(float)
    weight /= weight.sum()
    return _fill(np.apply_along_axis(np.convolve, 0, x, weight, 'valid'), d2 - 1)


def ds_lwm(x, d2):
    weight = np.arange(d2)[::-1].astype(float) + 1
    weight /= weight.sum()
    return _fill(np.apply_along_axis(np.convolve, 0, x, weight, 'valid'), d2 - 1)


def ds_median(x, d3):
    return bottleneck.move_median(x, d3, axis=0)


def ds_min(x, d4):
    return bottleneck.move_min(x, d4, axis=0)


def ds_max(x, d4):
    return bottleneck.move_max(x, d4, axis=0)


def ds_argmax(x, d4):
    return bottleneck.move_argmax(x, d4, axis=0) / (d4 - 1)


def ds_argmin(x, d4):
    return bottleneck.move_argmin(x, d4, axis=0) / (d4 - 1)


def ds_rank(x, d4):
    return (bottleneck.move_rank(x, d4, axis=0) + 1) / 2


def ds_std(x, d3):
    return bottleneck.move_std(x, d3, axis=0)


def ds_skew(x, d3):
    d3 = 3 if d3 < 3 else d3
    x = x - bottleneck.move_mean(x, d3, axis=0)
    const = (d3 - 1) ** (1 / 2) * d3 ** (1 / 6) / (d3 - 2)
    skew = const * bottleneck.move_sum(x ** 3, d3, axis=0) / (
        bottleneck.move_sum(x ** 2, d3, axis=0)) ** 1.5
    return skew


def ds_kurt(x, d4):
    d4 = 4 if d4 < 4 else d4
    x = x - bottleneck.move_mean(x, d4, axis=0)
    const1 = (d4 + 1) * d4 * (d4 - 1) / (d4 - 2) / (d4 - 3)
    const2 = 3 * (d4 - 1) ** 2 / (d4 - 2) / (d4 - 3)
    kurt = const1 * bottleneck.move_sum(x ** 4, d4, axis=0) / (
        bottleneck.move_sum(x ** 2, d4, axis=0)) ** 2 - const2
    return kurt


def ts_cumsum(x):
    return np.nancumsum(x, axis=1)


def ts_cummean(x):
    return ts_cumsum(x) / (np.arange(x.shape[1]) + 1)[None, :, None]


def ts_cumstd(x):
    cx = ts_cumsum(x)
    cx2 = ts_cumsum(x ** 2)
    std = np.sqrt((cx2 - cx ** 2 / (np.arange(x.shape[1]) + 1)[None, :, None])
                  / np.arange(x.shape[1])[None, :, None])
    std[:, :5] = 0
    return std


def ts_cummax(x):
    return np.maximum.accumulate(x, axis=1)


def ts_cummin(x):
    return np.minimum.accumulate(x, axis=1)


def ts_cumargmax(x):
    arg = np.arange(x.shape[1])[:, None].repeat(x.shape[0] * x.shape[2], axis=1).reshape(
        x.shape[1], x.shape[0], x.shape[2]).transpose(1, 0, 2)
    arg[np.maximum.accumulate(x, axis=1) != x] = 0
    return 1 - np.maximum.accumulate(arg, axis=1) / (np.arange(x.shape[1]) + 1)[None, :, None]


def ts_cumargmin(x):
    arg = np.arange(x.shape[1])[:, None].repeat(x.shape[0] * x.shape[2], axis=1).reshape(
        x.shape[1], x.shape[0], x.shape[2]).transpose(1, 0, 2)
    arg[np.minimum.accumulate(x, axis=1) != x] = 0
    return 1 - np.maximum.accumulate(arg, axis=1) / (np.arange(x.shape[1]) + 1)[None, :, None]


def ts_cumskew(x):
    x = x - ts_cummean(x)
    seq = (np.arange(x.shape[1]) + 1)[None, :, None]
    const = (seq - 1) ** (1 / 2) * seq ** (1 / 6) / (seq - 2)
    skew = const * ts_cumsum(x ** 3) / (ts_cumsum(x ** 2)) ** 1.5
    skew[:, :5] = np.nan
    skew = _roll_fill(skew)
    return skew


def ts_cumkurt(x):
    x = x - ts_cummean(x)
    seq = (np.arange(x.shape[1]) + 1)[None, :, None]
    const1 = (seq + 1) * seq * (seq - 1) / (seq - 2) / (seq - 3)
    const2 = 3 * (seq - 1) ** 2 / (seq - 2) / (seq - 3)
    kurt = const1 * ts_cumsum(x ** 4) / (ts_cumsum(x ** 2)) ** 2 - const2
    kurt[:, :5] = 0
    return kurt


def cs_rank(x):
    rank = bottleneck.nanrankdata(x, axis=2)
    return rank / np.nanmax(rank, axis=2)[..., None]


def add2(x, y, w):
    return w * x + (1 - w) * y


def shorten(x, w):
    return w * x


def dt_corr2(x, y, m3):
    ar = ArrReshape()
    x = ar.to2d(x)
    y = ar.to2d(y)
    cx = bottleneck.move_mean(x, m3, axis=0)
    cy = bottleneck.move_mean(y, m3, axis=0)
    cx2 = bottleneck.move_mean(x ** 2, m3, axis=0)
    cy2 = bottleneck.move_mean(y ** 2, m3, axis=0)
    cxy = bottleneck.move_mean(x * y, m3, axis=0)
    return ar.to3d((m3 * cxy - cx * cy) / np.sqrt((m3 * cx2 - cx ** 2) * (m3 * cy2 - cy ** 2)))


def dt_beta2(x, y, m3):
    ar = ArrReshape()
    x = ar.to2d(x)
    y = ar.to2d(y)
    cx = bottleneck.move_mean(x, m3, axis=0)
    cy = bottleneck.move_mean(y, m3, axis=0)
    cx2 = bottleneck.move_mean(x ** 2, m3, axis=0)
    cxy = bottleneck.move_mean(x * y, m3, axis=0)
    return ar.to3d((m3 * cxy - cx * cy) / (m3 * cx2 - cx ** 2))


def dt_intercept2(x, y, m3):
    return dt_mean(y, m3) - dt_mean(x, m3) * dt_beta2(x, y, m3)


def dt_alpha2(x, y, m3):
    return y - x * dt_beta2(x, y, m3)


def dt_resid2(x, y, m3):
    beta = dt_beta2(x, y, m3)
    alpha = dt_mean(y, m3) - dt_mean(x, m3) * beta
    return y - alpha - x * beta


def dt_nonlinear_alpha(x, m3):
    return dt_alpha2(x, cube(x), m3)


def ds_corr2(x, y, d3):
    cx = bottleneck.move_mean(x, d3, axis=0)
    cy = bottleneck.move_mean(y, d3, axis=0)
    cx2 = bottleneck.move_mean(x ** 2, d3, axis=0)
    cy2 = bottleneck.move_mean(y ** 2, d3, axis=0)
    cxy = bottleneck.move_mean(x * y, d3, axis=0)
    return (d3 * cxy - cx * cy) / np.sqrt((d3 * cx2 - cx ** 2) * (d3 * cy2 - cy ** 2))


def ds_beta2(x, y, d3):
    cx = bottleneck.move_mean(x, d3, axis=0)
    cy = bottleneck.move_mean(y, d3, axis=0)
    cx2 = bottleneck.move_mean(x ** 2, d3, axis=0)
    cxy = bottleneck.move_mean(x * y, d3, axis=0)
    return (d3 * cxy - cx * cy) / (d3 * cx2 - cx ** 2)


def ds_resid2(x, y, d3):
    beta = ds_beta2(x, y, d3)
    alpha = ds_mean(y, d3) - ds_mean(x, d3) * beta
    return y - alpha - x * beta


def ds_intercept2(x, y, d3):
    return ds_mean(y, d3) - ds_mean(x, d3) * ds_beta2(x, y, d3)


def ds_alpha2(x, y, d3):
    return y - x * ds_beta2(x, y, d3)


def ts_cumcorr2(x, y):
    cx = ts_cumsum(x)
    cy = ts_cumsum(y)
    cx2 = ts_cumsum(x ** 2)
    cy2 = ts_cumsum(y ** 2)
    cxy = ts_cumsum(x * y)
    cn = (np.arange(x.shape[1]) + 1)[None, :, None]
    corr = (cn * cxy - cx * cy) / np.sqrt((cn * cx2 - cx ** 2) * (cn * cy2 - cy ** 2))
    corr[:, :5] = 0
    return corr


def ts_cumbeta2(x, y):
    cx = ts_cumsum(x)
    cy = ts_cumsum(y)
    cx2 = ts_cumsum(x ** 2)
    cxy = ts_cumsum(x * y)
    cn = (np.arange(x.shape[1]) + 1)[None, :, None]
    beta = (cn * cxy - cx * cy) / (cn * cx2 - cx ** 2)
    beta[:, :5] = np.nan
    beta = _roll_fill(beta)
    return beta


def ts_cumresid2(x, y):
    beta = ts_cumbeta2(x, y)
    alpha = ts_cummean(y) - ts_cummean(x) * beta
    return y - alpha - x * beta


def ts_cumintercept2(x, y):
    return ts_cummean(y) - ts_cummean(x) * ts_cumbeta2(x, y)


def ts_cumalpha2(x, y):
    return y - x * ts_cumbeta2(x, y)


def relu(x):
    return np.where(x > 0, x, 0)


def max2(x, y):
    return np.fmax(x, y)


def min2(x, y):
    return np.fmin(x, y)


def deviation2(x, y):
    return np.where(x + y != 0, (x - y) / (x + y), 0)


def max_min_ewm_dev2(x, y, m2):
    x1 = dt_ewm(np.where(x > y, x, 0), m2)
    y1 = dt_ewm(np.where(y > x, y, 0), m2)
    return deviation2(x1, y1)


def dt_dwm2(x, y, m2):
    cxy = dt_mean(x * y, m2)
    cy = dt_mean(y, m2)
    return _ffill(np.where(cy != 0, cxy / cy, np.nan))


def ds_dwm2(x, y, d2):
    cxy = ds_mean(x * y, d2)
    cy = ds_mean(y, d2)
    return _ffill(np.where(cy != 0, cxy / cy, np.nan))


def ts_dwm2(x, y):
    cxy = ts_cumsum(x * y)
    cy = ts_cumsum(y)
    return _roll_fill(np.where(cy != 0, cxy / cy, np.nan))


def sign_mul2(x, y):
    return sign(x) * y


def mul2(x, y):
    return x * y


def sum2(x, y):
    return x + y


def div2(x, y):
    return _ffill(np.where(y != 0, x / abss(y), np.nan))


def sub2(x, y):
    return x - y


def abs_sub2(x, y):
    return abss(sub2(x, y))


def percent2(x, y):
    return (x - y) / abss(y)


def pn_condition2(x, y):
    return np.where(x > 0, y, -y)


def zero_condition2(x, y):
    return np.where(x > 0, y, 0)


def true_div2(x, y):
    return _ffill(np.where(y != 0, x / y, np.nan))


def dt_sharpe(x, m3):
    std = dt_std(x, m3)
    return _ffill(np.where(std > 0, (x - dt_mean(x, m3)) / std, np.nan))


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
    }

    freq = x.shape[1]
    period = 1 if freq == 242 else 240 // freq
    condition = reference[t][::period]
    if freq == 242:
        condition = [condition[0]] + condition + [condition[-1]]
    condition = np.asanyarray(condition, dtype=bool)[None, :, None]
    return np.where(condition, x, 0)


def arr_condition2(x, y):
    return np.where(y > 0, x, 0)

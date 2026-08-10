import numpy as np
from .operators_wsc import *
from .help_functions_wsc import replace_zero, type_convertor

"""
MA_Type: 0=SMA, 1=EMA, 2=WMA, 3=DEMA, 4=TEMA, 5=TRIMA, 6=KAMA, 7=MAMA, 8=T3 (Default=SMA)
"""


# __all__ = ['adx', 'adxr', 'aroon', 'atr', 'bbands', 'bop', 'cci', 'cmo', 'dema', 'di', 'dx', 'kama', 'macd', 'mavp',
#            'mfi', 'midpoint', 'midprice', 'mom', 'po', 'ppo', 'rsi', 'roc', 'rocr', 'trima', 'wma']


def bbands(price, time_period=5, a=2):
    """
    Bollinger Bands：过去一段时间的均价加上/减去过去一段时间价格的标准差
    :param price: array_like
        原始价格序列
    :param time_period: int
        回看长度
    :param a: int
        加减标准差的倍数
    :return: price_ma, price_up_track. price_down_track: array_like
        价格均线，价格上轨，价格下轨
    """
    price_ma = ts_mean(price, time_period)
    price_std = ts_std(price, time_period)
    price_up_track = price_ma + a * price_std
    price_down_track = price_ma - a * price_std
    return price_ma, price_up_track, price_down_track


def dema(price, time_period=30):
    """
    double exponential moving average: 双重指数移动平均
    :param price: array_like
        原始价格序列
    :param time_period: int
        回看长度
    :return: array_like
        dema of price
    """
    price_ema = ts_ema_span(price, time_period)
    price_dema = 2 * price_ema - ts_ema_span(price_ema, time_period)
    return price_dema


def kama(price, time_period=10, n1=2, n2=30):
    """
    Kaufman's Adaptative Moving Average: 考夫曼自适应移动平均
    When market volatility is low, Kaufman’s Adaptive Moving Average remains near the current market price, but when
    volatility increases, it will lag behind. What the KAMA indicator aims to do is filter out “market noise” –
    insignificant, temporary surges in price action. One of the primary weaknesses of traditional moving averages is
    that when used for trading signals, they tend to generate many false signals. The KAMA indicator seeks to lessen
    this tendency – generate fewer false signals – by not responding to short-term, insignificant price movements.
    :param price: array_like
        原始价格序列
    :param time_period: int
        回看长度
    :param n1: int
        快速移动平均周期
    :param n2: int
        慢速移动平均周期
    :return: array_like
        kama of price
    """
    change = abs(ts_delta(price, time_period))
    volatility = ts_sum(abs(ts_delta(price, 1)), time_period)
    er = change / volatility
    fast_sc = 2 / (n1 + 1)
    slow_sc = 2 / (n2 + 1)
    smooth_constant = er * (fast_sc - slow_sc) + slow_sc
    cof = smooth_constant ** 2
    price_kama = price.ema(alpha=cof, adjust=False).mean()
    return price_kama


@type_convertor
def mavp(price, va_time_period, min_period, max_period):
    """
    MAVP - Moving average with variable period.
    It gets an input price array, and a period array that are the same length.
    The output price array is the moving average at the point using the specified period at the point.
    So, if you have an array of [1, 5, 3, 8] and you specify period [2,3,3,2] then the output will be:
    [MA(2)[0], MA(3)[1], MA(3)[2], MA(2)[3]]
    With the exception that it puts maxperiod number of nan's at the front, for some reason so you'd need to call it like:

    example:
    price = np.array([1,5,7,8], dtype=float)
    va_time_period =np.array([2,3,3,2], dtype=float)
    mavp(price, period, maxperiod=3)
    array([nan, nan, 4.33333333, 7.5])

    ts_mean(price, 2)
    array([ nan, 3., 6., 7.5])

    ts_mean(price, 3)
    array([nan, nan, 4.33333333, 6.66666667])

    :param price: array_like
        原始价格序列
    :param va_time_period: array_like
        可变回看序列
    :param min_period: int
        最短回看长度
    :param max_period: int
        最长回看长度
    :return: array_like
        price of mavp
    """
    try:
        price = price.values
    except AttributeError:
        pass
    price_mavp = np.empty_like(price)
    va_time_period[va_time_period < min_period] = min_period
    va_time_period[va_time_period > max_period] = max_period
    va_time_period_unique = np.unique(va_time_period)
    average_array = np.empty(shape=(len(va_time_period_unique), len(price)))
    for i, i_num in enumerate(va_time_period_unique):
        average_array[i] = ts_mean(price, i_num)
    for j, j_num in va_time_period:
        index_va_time_period = np.argwhere(va_time_period_unique == j_num)
        price_mavp[j] = average_array[index_va_time_period, j]
    return price_mavp


def midpoint(price, time_period):
    """
    (highest value + lowest value)/2
    :param price: array_like
        原始价格序列
    :param time_period: int
        回看时间长度
    :return: array_like
        midpoint of price
    """
    highest_price = ts_max(price, time_period)
    lowest_price = ts_min(price, time_period)
    price_midpoint = (highest_price + lowest_price) / 2
    return price_midpoint


def midprice(price_high, price_low, time_period):
    """
    (highest high + lowest low) / 2
    :param price_high: array_like
        原始高价序列
    :param price_low: array_like
        原始低价序列
    :param time_period: int
        回看时间长度
    :return: array_like
        midprice of price
    """
    highest_price = ts_max(price_high, time_period)
    lowest_price = ts_min(price_low, time_period)
    price_midprice = (highest_price + lowest_price) / 2
    return price_midprice


def trima(price, time_period):
    if time_period % 2 == 0:
        price_trima = ts_mean(ts_mean(price, int(time_period / 2 + 1)), int(time_period / 2))
    else:
        price_trima = ts_mean(ts_mean(price, int((time_period + 1) / 2)), int((time_period + 1) / 2))
    return price_trima


def wma(price, time_period):
    # weighted_mean
    return ts_decay_linear(price, time_period)


def di(price_high, price_low, price_close, time_period=14):
    # 动量指标，但是看不懂在干嘛，而且不同版本的公式还不一样
    max_high = ts_delta(price_high, 1)
    max_high[max_high < 0] = 0
    max_low = -ts_delta(price_low, 1)
    max_low[max_low < 0] = 0
    xpdm = ts_delta(price_high, 1)
    xpdm[max_high <= max_low] = 0
    pdm = ts_mean(xpdm, time_period)
    xndm = -ts_delta(price_low, 1)
    xndm[max_low <= max_high] = 0
    ndm = ts_mean(xndm, time_period)
    price_atr = atr(price_high, price_low, price_close, time_period)
    di_plus = pdm / price_atr
    di_minus = ndm / price_atr
    return di_plus, di_minus


def dx(price_high, price_low, price_close, time_period=14):
    di_plus, di_minus = di(price_high, price_low, price_close, time_period)
    price_dx = abs(di_plus - di_minus) / abs(di_plus + di_minus)
    return price_dx


def adx(price_high, price_low, price_close, time_period=14):
    price_dx = dx(price_high, price_low, price_close, time_period)
    price_adx = ts_mean(price_dx, time_period)
    return price_adx


def adxr(price_high, price_low, price_close, time_period=14):
    price_adx = adx(price_high, price_low, price_close, time_period)
    price_adxr = (price_adx + ts_delay(price_adx, time_period)) / 2
    return price_adxr


def po(price, fast_time_period=12, slow_time_period=26):
    # PO(price oscillator), the difference between two moving averages.
    slow_ma = ts_mean(price, slow_time_period)
    fast_ma = ts_mean(price, fast_time_period)
    price_po = slow_ma - fast_ma
    return price_po


def aroon(price_high, price_low, time_period=14):
    """
    The word aroon is Sanskrit for "dawn's early night".
    The Aroon indicator attempts to show when is a new trend is dawning.
    The indicator consists of two lines(up and down) that measures how long it has been since the highest high/lowest
    low has occurred within a period range.
    """
    price_aroon_up = 1 + ts_argmax(price_high, time_period)
    price_aroon_down = 1 + ts_argmin(price_low, time_period)
    price_aroon = price_aroon_up - price_aroon_down
    return price_aroon_up, price_aroon_down, price_aroon


def bop(price_open, price_high, price_low, price_close, time_period=14):
    """
    BOP(balance of power)技术指标，用来衡量收盘价与开盘价的距离占最高价与最低价的距离的比例，反应市场的多空力量对比
    BOP越大，说明价格被往最高价的方向推动得越多，反之亦然
    """
    price_bop_raw = (price_close - price_open) / (price_high - price_low)
    price_bop = ts_mean(price_bop_raw, time_period)
    return price_bop


def cci(price_high, price_low, price_close, time_period=14):
    """
    CCI(commodity channel index)指标用来衡量典型价格与其一段时间的移动平均的偏离程度，可以用来反映市场的超买超卖状态；
    一般认为，CCI超过100则市场处于超买状态，低于-100则市场处于超卖状态。
    """
    typical_price = (price_high + price_low + price_close) / 3
    typical_price_ma = ts_mean(typical_price, time_period)
    typical_price_mean_deviation = ts_mean(abs(typical_price - typical_price_ma), time_period)
    price_cci = (typical_price - typical_price_ma) / (0.015 * typical_price_mean_deviation)
    return price_cci


def cmo(price_close, time_period=14):
    """
    CMO(Chande momentum oscillator)指标，用于衡量动量，分子表示总的动量（向上的动量-向下的动量），分母表示这段时间价格的
    移动距离。可以认为是RSI指标的变形。
    There are several ways to interpret the CMO. Values over 0.5 indicate overbought conditions, while values under -0.5
    indicate oversold conditions. High CMO values indicate strong trends. When the CMO crosses above a moving average of
    CMO, it is a buy signal, crossing down is a sell signal.
    """
    price_delta_up = ts_delta(price_close, 1)
    price_delta_up[price_delta_up < 0] = 0
    price_delta_down = -ts_delta(price_close, 1)
    price_delta_down[price_delta_down < 0] = 0
    price_delta_up_sum = ts_sum(price_delta_up, time_period)
    price_delta_down_sum = ts_sum(price_delta_down, time_period)
    price_cmo = (price_delta_up_sum - price_delta_down_sum) / replace_zero(price_delta_up_sum + price_delta_down_sum)
    return price_cmo


def macd(price_close, fast_period=12, slow_period=26, signal_period=9):
    """
    MACD(moving average convergence divergence)指标衡量快速均线与慢速均线的差值，是一个动量指标。
    上涨趋势中快速均线会比慢速均线涨得快，反之亦然，因此MACD上穿/下穿0可以用于构造交易信号，或是用其值衡量超买/超卖状态；
    另一种构造信号的方式是求MACD与其移动平均线的差得到MACD柱，并与MACD柱上穿/下穿0来构造交易信号。
    """
    price_macd = ts_mean(price_close, fast_period) - ts_mean(price_close, slow_period)
    price_macd_signal = ts_mean(price_macd, signal_period)
    price_macd_histogram = price_macd - price_macd_signal
    return price_macd, price_macd_signal, price_macd_histogram


def mfi(price_high, price_low, price_close, volume, time_period=14):
    """
    mfi(money flow index)指标衡量了上涨时刻的资金流入与总的资金流入的比值，是个动量指标
    """
    typical_price = (price_high + price_low + price_close) / 3
    money_flow_pos = typical_price * volume
    money_flow_pos[ts_delta(typical_price, 1) < 0] = 0
    money_flow_neg = typical_price * volume
    money_flow_neg[ts_delta(typical_price, 1) > 0] = 0
    money_flow_pos_sum = ts_sum(money_flow_pos, time_period)
    money_flow_neg_sum = ts_sum(money_flow_neg, time_period)
    price_mfi = money_flow_pos_sum / replace_zero(money_flow_pos_sum + money_flow_neg_sum)
    return price_mfi


def mom(price_close, time_period=10):
    # Momentum
    price_momentum = ts_delta(price_close, time_period)
    return price_momentum


def ppo(price_close, fast_period=12, slow_period=26):
    """
    PPO(Percentage Price Oscillator) shows the percentage difference between two moving averages.
    """
    slow_ma = ts_mean(price_close, slow_period)
    fast_ma = ts_mean(price_close, fast_period)
    price_ppo = (slow_ma - fast_ma) / fast_ma
    return price_ppo


def roc(price_close, time_period=10):
    """
    roc(rate of change)技术指标，计算价格涨跌幅
    """
    price_roc = ts_pct_change(price_close, time_period)
    return price_roc


def rocr(price_close, time_period=10):
    """
    rocr(rate fo change ratio)技术指标，当前价格与上一时段价格的比值
    """
    price_rocr = ts_pct_change(price_close, time_period) + 1
    return price_rocr


def rsi(price_close, time_period=14):
    """
    rsi(relative strength index) calculates a ratio of the recent upward price movements to the absolute price movement.
    """
    close_up = ts_delta(price_close, 1)
    close_up[close_up < 0] = 0
    close_down = -ts_delta(price_close, 1)
    close_down[close_down < 0] = 0
    close_up_ma = ts_mean(close_up, time_period)
    close_down_ma = ts_mean(close_down, time_period)
    price_rsi = close_up_ma / (close_up_ma + close_down_ma)
    return price_rsi


def stoch(price_high, price_low, price_close, fastk_period=5, fastd_period=3, slowk_period=3, slowd_period=3):
    highest_high = ts_max(price_high, fastk_period)
    lowest_low = ts_min(price_low, fastk_period)
    price_fastk = (price_close - lowest_low) / (highest_high - lowest_low)
    price_fastd = ts_mean(price_fastk, fastd_period)
    price_slowk = ts_mean(price_fastk, slowk_period)
    price_slowd = ts_mean(price_slowk, slowd_period)
    return price_fastk, price_fastd, price_slowk, price_slowd


def stoch_rsi(price_close, time_period=14, fastk_period=5, fastd_period=3):
    # stoch(rsi(price_close))
    price_rsi = rsi(price_close, time_period)
    price_fastk = (price_rsi - ts_min(price_rsi, fastk_period)) / (
            ts_max(price_rsi, fastk_period) - ts_min(price_rsi, fastk_period))
    price_fastd = ts_mean(price_fastk, fastd_period)
    return price_fastk, price_fastd


def trix(price_close, time_period=30):
    price_trix = ts_ema_span(ts_ema_span(ts_ema_span(ts_pct_change(price_close, 1), time_period), time_period),
                             time_period)
    return price_trix


def ultosc(price_high, price_low, price_close, time_period_1, time_period_2, time_period_3):
    # ultimate oscillator
    true_high = np.maximum(price_high, ts_delay(price_close, 1))
    true_low = np.minimum(price_low, ts_delay(price_close, 1))
    true_range = true_high - true_low
    price_a1 = ts_mean(price_close - true_low, time_period_1) * time_period_1
    price_a2 = ts_mean(price_close - true_low, time_period_2) * time_period_2
    price_a3 = ts_mean(price_close - true_low, time_period_3) * time_period_3
    price_b1 = ts_mean(true_range, time_period_1) * time_period_1
    price_b2 = ts_mean(true_range, time_period_2) * time_period_2
    price_b3 = ts_mean(true_range, time_period_3) * time_period_3
    price_ultosc = (4 * (price_a1 / price_b1) + 2 * (price_a2 / price_b2) + (price_a3 / price_b3)) / 7
    return price_ultosc


def willr(price_high, price_low, price_close, time_period=14):
    highest_high = ts_max(price_high, time_period)
    lowest_low = ts_min(price_low, time_period)
    price_willr = (highest_high - price_close) / (highest_high - lowest_low)
    return price_willr


def ad(price_high, price_low, price_close, price_volume):
    """
    accumulation/distribution line, 使用当前时刻的价格信息对volume进行修正，close越高则修正后的volume越大
    """
    clv = ((price_close - price_low) - (price_high - price_close)) / (price_high - price_low)
    price_ad = (clv * price_volume).cumsum()
    return price_ad


def adosc(price_high, price_low, price_close, price_volume, fast_period=3, slow_period=10):
    price_ad = ad(price_high, price_low, price_close, price_volume)
    return ts_mean(price_ad, fast_period) - ts_mean(price_ad, slow_period)


def obv(price_close, price_volume):
    price_sign = np.sign(ts_delta(price_close, 1))
    price_volume_adj = price_volume * price_sign
    return price_volume_adj.cumsum()


def tr(price_high, price_low, price_close):
    true_high = np.maximum(price_high, ts_delay(price_close, 1))
    true_low = np.minimum(price_low, ts_delay(price_close, 1))
    price_tr = true_high - true_low
    # price_tr = np.maximum(np.maximum(abs(price_high - price_low), abs(price_high - ts_delay(price_close, 1))),
    #                       abs(price_low - ts_delay(price_close, 1)))  # 两种算法等价
    return price_tr


def atr(price_high, price_low, price_close, time_period=14):
    # ATR(average true range)技术指标，用于衡量市场波动，波动越大则值越大
    price_tr = tr(price_high, price_low, price_close)
    price_atr = ts_mean(price_tr, time_period)
    return price_atr


def natr(price_high, price_low, price_close, time_period=14):
    # normalized atr
    price_atr = atr(price_high, price_low, price_close, time_period)
    price_natr = price_atr / price_close
    return price_natr


def avg_price(price_open, price_high, price_low, price_close):
    # average price
    return (price_open + price_high + price_low + price_close) / 4


def med_price(price_high, price_low):
    # median price
    return (price_high + price_low) / 2


def typ_price(price_high, price_low, price_close):
    # typical price
    return (price_high + price_low + price_close) / 3


def wcl_price(price_high, price_low, price_close):
    # weighted close price
    return (price_high + price_low + 2 * price_close) / 4


def two_crows(price_open, price_close):
    # 两只乌鸦技术指标
    con_1 = (price_open > ts_delay(price_close, 1))  # 今天早盘高开
    con_2 = (price_open > price_close)  # 今天收跌
    con_3 = (ts_delay(price_open, 1) > ts_delay(price_close, 1))  # 昨天收跌
    con_4 = (ts_delay(price_open, 1) > ts_delay(price_close, 2))  # 昨天早盘高开
    con_5 = (ts_delay(price_close, 2) > ts_delay(price_open, 2))  # 前天收涨
    con_6 = (ts_delay(price_close, 1) > ts_delay(price_close, 2))  # 昨天和前天的蜡烛图出现缺口
    con_all = con_1 * con_2 * con_3 * con_4 * con_5 * con_6
    return con_all


def long_in1(df, idx, lag):
    o = df['open']
    c = df['close']
    h = df['high']
    ma_d5 = df['ma_d5']
    ma_d10 = df['ma_d10']

    res = False
    if (lag >= 20) and (lag <= 210) and (h.iloc[idx] >= h.iloc[idx + 1 - (lag + 480):idx + 1].max()) and (
            o.iloc[idx - (lag - 1)] > c.iloc[idx - lag]) and (
            c.iloc[idx] > max(ma_d5.iloc[idx], ma_d10.iloc[idx])) and (
            (ma_d5.iloc[idx - (lag + 240)] > ma_d10.iloc[idx - (lag + 240)]) or (
            ma_d5.iloc[idx - lag] > ma_d10.iloc[idx - lag])):
        res = True
    return res

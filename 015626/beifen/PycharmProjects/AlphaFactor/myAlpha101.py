import numpy as np
import pandas as pd
from numpy import abs
from numpy import log
from numpy import sign
from scipy.stats import rankdata
from multifactor.IO import IO
import time

def rank(df):
    return df.rank(pct=True)


def delay(df, d=1):
    return df.shift(d)


def correlation(x, y, d=10):
    return x.rolling(d).corr(y)


def covariance(x, y, d=10):
    return x.rolling(d).cov(y)


def scale(df, a=1):
    return df.mul(a).div(np.abs(df).sum())

def delta(df, d=1):
    return df.diff(d)


def signedpower(x, a):
    return x ^ a


def decay_linear(df, period=10):
    # Clean data
    if df.isnull().values.any():
        df.fillna(method='ffill', inplace=True)
        df.fillna(method='bfill', inplace=True)
        df.fillna(value=0, inplace=True)
    na_lwma = np.zeros_like(df)
    na_lwma[:period, :] = df.iloc[:period, :]
    na_series = df.as_matrix()

    divisor = period * (period + 1) / 2
    y = (np.arange(period) + 1) * 1.0 / divisor

    for row in range(period - 1, df.shape[0]):
        x = na_series[row - period + 1: row + 1, :]
        na_lwma[row, :] = (np.dot(x.T, y))
    data = pd.DataFrame(na_lwma, index=df.index, columns=df.columns)

    return data


def ts_min(df, d=10):
    return df.rolling(d).min()


def ts_max(df, d=10):
    return df.rolling(d).max()


def ts_argmax(df, d=10):
    return df.rolling(d).apply(np.argmax) + 1


def ts_argmin(df, d=10):
    return df.rolling(d).apply(np.argmin) + 1


def ts_rank(df, d=10):
    def rolling_rank(x):
        return rankdata(x)[-1]

    return df.rolling(d).apply(rolling_rank)


def ts_sum(df, d=10):
    return df.rolling(d).sum()


def sma(df, d):
    return df.rolling(d).mean()


def product(df, d=10):
    def rolling_prod(x):
        return np.prod(x)

    return df.rolling(d).apply(rolling_prod)


def stddev(df, d=10):
    return df.rolling(d).std()


class my101Alphas(object):
    def __init__(self, df):
        self.open = df['open']
        self.high = df['high']
        self.low = df['low']
        self.close = df['close']
        self.volume = df['volume'] * 100
        self.returns = df['pct_chg']
        self.cap = df['mkt_cap_ard'] * 10000
        self.vwap = (df['amt'] * 1000) / (df['volume'] * 100 + 1)

    # def alpha051(self):
    #     inner = (((delay(self.close, 20) - delay(self.close, 10)) / 10) - (
    #             (delay(self.close, 10) - self.close) / 10))
    #     alpha = (-1 * delta(self.close))
    #     alpha[inner < -0.05] = 1
    #     return alpha
    #
    # def alpha052(self):
    #     return (((-1 * delta(ts_min(self.low, 5), 5)) *
    #              rank(((ts_sum(self.returns, 240) - ts_sum(self.returns, 20)) / 220))) * ts_rank(self.volume, 5))
    #
    # def alpha053(self):
    #     inner = (self.close - self.low).replace(0, 0.0001)
    #     return -1 * delta((((self.close - self.low) - (self.high - self.close)) / inner), 9)
    #
    # def alpha054(self):
    #     inner = (self.low - self.high).replace(0, -0.0001)
    #     return -1 * (self.low - self.close) * (self.open ** 5) / (inner * (self.close ** 5))
    #
    # def alpha055(self):
    #     divisor = (ts_max(self.high, 12) - ts_min(self.low, 12)).replace(0, 0.0001)
    #     inner = (self.close - ts_min(self.low, 12)) / (divisor)
    #     df = correlation(rank(inner), rank(self.volume), 6)
    #     return -1 * df.replace([-np.inf, np.inf], 0).fillna(value=0)
    #
    # def alpha056(self):
    #     return (0 - (1 * (rank((ts_sum(self.returns, 10) / ts_sum(ts_sum(self.returns, 2), 3))) * rank(
    #         (self.returns * self.cap)))))
    #
    # def alpha057(self):
    #     return (0 - (1 * (
    #             (self.close - self.vwap) / decay_linear(rank(ts_argmax(self.close, 30)), 2))))
    #
    # # def alpha060(self):
    # #     divisor = (self.high - self.low).replace(0, 0.0001)
    # #     inner = ((self.close - self.low) - (self.high - self.close)) * self.volume / divisor
    # #     return - ((2 * scale(rank(inner))) - scale(rank(ts_argmax(self.close, 10))))
    #
    # def alpha061(self):
    #     adv180 = sma(self.volume, 180)
    #     data = (rank((self.vwap - ts_min(self.vwap, 16))) < rank(correlation(self.vwap, adv180, 18)))
    #     for u in data.columns:
    #         if data[u].dtype == bool:
    #             data[u] = data[u].astype('int')
    #     return data
    #
    # def alpha062(self):
    #     adv20 = sma(self.volume, 20)
    #     return ((rank(correlation(self.vwap, sma(adv20, 22), 10)) < rank(
    #         ((rank(self.open) + rank(self.open)) < (rank(((self.high + self.low) / 2)) + rank(self.high))))) * -1)
    #
    # def alpha064(self):
    #     adv120 = sma(self.volume, 120)
    #     return ((rank(
    #         correlation(ts_sum(((self.open * 0.178404) + (self.low * (1 - 0.178404))), 13), ts_sum(adv120, 13),
    #                     17)) < rank(
    #         delta(((((self.high + self.low) / 2) * 0.178404) + (self.vwap * (1 - 0.178404))), 3.69741))) * -1)
    #
    # def alpha065(self):
    #     adv60 = sma(self.volume, 60)
    #     return ((rank(
    #         correlation(((self.open * 0.00817205) + (self.vwap * (1 - 0.00817205))), ts_sum(adv60, 9), 6)) < rank(
    #         (self.open - ts_min(self.open, 14)))) * -1)
    #
    # def alpha066(self):
    #     return ((rank(decay_linear(delta(self.vwap, 4), 7)) +
    #              ts_rank(decay_linear(((((self.low * 0.96633) + (self.low * (1 - 0.96633))) - self.vwap)
    #                                    / (self.open - ((self.high + self.low) / 2))), 11), 7)) * -1)
    #
    # def alpha068(self):
    #     adv15 = sma(self.volume, 15)
    #     return ((ts_rank(correlation(rank(self.high), rank(adv15), 9), 14) < rank(
    #         delta(((self.close * 0.518371) + (self.low * (1 - 0.518371))), 1.06157))) * -1)

    # def alpha071(self):
    #     adv180 = sma(self.volume, 180)
    #     p1 = ts_rank(decay_linear(correlation(ts_rank(self.close, 3), ts_rank(adv180, 12), 18), 4),
    #                  16)
    #     p2 = ts_rank(
    #         decay_linear((rank(((self.low + self.open) - (self.vwap + self.vwap))).pow(2)), 16), 4)
    #     df = pd.DataFrame({'p1': p1, 'p2': p2})
    #     df.at[df['p1'] >= df['p2'], 'max'] = df['p1']
    #     df.at[df['p2'] >= df['p1'], 'max'] = df['p2']
    #     return df['max']

    # def alpha072(self):
    #     adv40 = sma(self.volume, 40)
    #     return (rank(decay_linear(correlation(((self.high + self.low) / 2), adv40, 9), 10)) / rank(
    #         decay_linear(correlation(ts_rank(self.vwap, 4), ts_rank(self.volume, 19), 7), 3)))

    # def alpha073(self):
    #     p1 = rank(decay_linear(delta(self.vwap, 5), 3))
    #     p2 = ts_rank(decay_linear(((delta(((self.open * 0.147155) + (self.low * (1 - 0.147155))), 2) / (
    #             (self.open * 0.147155) + (self.low * (1 - 0.147155)))) * -1), 3), 17)
    #     df = pd.DataFrame({'p1': p1, 'p2': p2})
    #     df.at[df['p1'] >= df['p2'], 'max'] = df['p1']
    #     df.at[df['p2'] >= df['p1'], 'max'] = df['p2']
    #     return -1 * df['max']

    # def alpha074(self):
    #     adv30 = sma(self.volume, 30)
    #     return ((rank(correlation(self.close, ts_sum(adv30, 37), 15)) < rank(
    #         correlation(rank(((self.high * 0.0261661) + (self.vwap * (1 - 0.0261661)))), rank(self.volume),
    #                     11))) * -1)
    #
    # def alpha075(self):
    #     adv50 = sma(self.volume, 50)
    #     data = (rank(correlation(self.vwap, self.volume, 4)) < rank(correlation(rank(self.low), rank(adv50), 12)))
    #     for u in data.columns:
    #         if data[u].dtype == bool:
    #             data[u] = data[u].astype('int')
    #     return data

    # def alpha077(self):
    #     adv40 = sma(self.volume, 40)
    #     p1 = rank(decay_linear(((((self.high + self.low) / 2) + self.high) - (self.vwap + self.high)),
    #                            20))
    #     p2 = rank(decay_linear(correlation(((self.high + self.low) / 2), adv40, 3), 6))
    #     df = pd.DataFrame({'p1': p1, 'p2': p2})
    #     df.at[df['p1'] >= df['p2'], 'min'] = df['p2']
    #     df.at[df['p2'] >= df['p1'], 'min'] = df['p1']
    #     return df['min']

    # def alpha078(self):
    #     adv40 = sma(self.volume, 40)
    #     return (rank(
    #         correlation(ts_sum(((self.low * 0.352233) + (self.vwap * (1 - 0.352233))), 20), ts_sum(adv40, 20),
    #                     7)).pow(rank(correlation(rank(self.vwap), rank(self.volume), 6))))

    def alpha081(self):
        adv10 = sma(self.volume, 10)
        data = (rank(log(product(rank((rank(correlation(self.vwap, ts_sum(adv10, 50), 8)).pow(4))), 15))) < rank(
            correlation(rank(self.vwap), rank(self.volume), 5))) * -1
        for u in data.columns:
            if data[u].dtype == bool:
                data[u] = data[u].astype('int')
        return data

    def alpha083(self):
        return ((rank(delay(((self.high - self.low) / (ts_sum(self.close, 5) / 5)), 2)) * rank(
            rank(self.volume))) / (
                        ((self.high - self.low) / (ts_sum(self.close, 5) / 5)) / (self.vwap - self.close)))

    def alpha084(self):
        return pow(ts_rank((self.vwap - ts_max(self.vwap, 15)), 21), delta(self.close, 5))

    def alpha085(self):
        adv30 = sma(self.volume, 30)
        return (rank(correlation(((self.high * 0.876703) + (self.close * (1 - 0.876703))), adv30, 10)).pow(
            rank(correlation(ts_rank(((self.high + self.low) / 2), 4), ts_rank(self.volume, 10), 7))))

    def alpha086(self):
        adv20 = sma(self.volume, 20)
        return ((ts_rank(correlation(self.close, ts_sum(adv20, 15), 6), 20) < rank(
            ((self.open + self.close) - (self.vwap + self.open)))) * -1)

    # def alpha088(self):
    #     adv60 = sma(self.volume, 60)
    #     p1 = rank(
    #         decay_linear(((rank(self.open) + rank(self.low)) - (rank(self.high) + rank(self.close))),
    #                      8))
    #     p2 = ts_rank(decay_linear(correlation(ts_rank(self.close, 8), ts_rank(adv60, 21), 8), 7),
    #                  3)
    #     df = pd.DataFrame({'p1': p1, 'p2': p2})
    #     df.at[df['p1'] >= df['p2'], 'min'] = df['p2']
    #     df.at[df['p2'] >= df['p1'], 'min'] = df['p1']
    #     return df['min']

    # def alpha092(self):
    #     adv30 = sma(self.volume, 30)
    #     p1 = ts_rank(decay_linear(((((self.high + self.low) / 2) + self.close) < (self.low + self.open)),
    #                               15), 19)
    #     p2 = ts_rank(decay_linear(correlation(rank(self.low), rank(adv30), 8), 7), 7)
    #     df = pd.DataFrame({'p1': p1, 'p2': p2})
    #     df.at[df['p1'] >= df['p2'], 'min'] = df['p2']
    #     df.at[df['p2'] >= df['p1'], 'min'] = df['p1']
    #     return df['min']

    def alpha094(self):
        adv60 = sma(self.volume, 60)
        return ((rank((self.vwap - ts_min(self.vwap, 12))).pow(
            ts_rank(correlation(ts_rank(self.vwap, 20), ts_rank(adv60, 4), 18), 3)) * -1))

    def alpha095(self):
        adv40 = sma(self.volume, 40)
        return (rank((self.open - ts_min(self.open, 12))) < ts_rank(
            (rank(correlation(ts_sum(((self.high + self.low) / 2), 19), ts_sum(adv40, 19), 13)).pow(5)), 12))

    # def alpha096(self):
    #     adv60 = sma(self.volume, 60)
    #     p1 = ts_rank(decay_linear(correlation(rank(self.vwap), rank(self.volume), 4), 4), 8)
    #     p2 = ts_rank(decay_linear(ts_argmax(correlation(ts_rank(self.close, 7), ts_rank(adv60, 4), 4), 13),14), 13)
    #     df = pd.DataFrame({'p1': p1, 'p2': p2})
    #     df.at[df['p1'] >= df['p2'], 'max'] = df['p1']
    #     df.at[df['p2'] >= df['p1'], 'max'] = df['p2']
    #     return -1 * df['max']

    def alpha098(self):
        adv5 = sma(self.volume, 5)
        adv15 = sma(self.volume, 15)
        return (rank(decay_linear(correlation(self.vwap, ts_sum(adv5, 26), 5), 7))
                - rank(decay_linear(ts_rank(ts_argmin(correlation(rank(self.open), rank(adv15), 21), 9), 7),
                                    8)))

    def alpha099(self):
        adv60 = sma(self.volume, 60)
        return ((rank(correlation(ts_sum(((self.high + self.low) / 2), 20), ts_sum(adv60, 20), 9))
                 < rank(correlation(self.low, self.volume, 6))) * -1)

    def alpha101(self):
        return (self.close - self.open) / ((self.high - self.low) + 0.001)


print('read_data')
df = IO.read_data([20140101,20180630],columns = ['open','high','low','close','pct_chg','amt','volume','mkt_cap_ard'],alt = 'A:/zhangf/data/md/CHINA_STOCK/B8/WIND/MD_CHINA_STOCK_B8_WIND.h5')
print('calculate factor')
Alpha101 = my101Alphas(df.unstack())
alpha_name_list = (dir(my101Alphas))
for alpha_name in alpha_name_list:
    if 'alpha' in alpha_name:
        print(alpha_name)
        start_time = time.time()
        df[alpha_name] = getattr(Alpha101, alpha_name)().stack()

        print(time.time() - start_time)
        IO.pd_hdf5_writer(df[alpha_name].to_frame(), 'A:\\weiyc\\factor\\factor101\\' + alpha_name + '.h5', dataset=alpha_name)
# df = df.drop(['open','high','low','close','pct_chg','amt','volume','mkt_cap_ard'], axis=1)
# print('save factor')
# IO.pd_hdf5_writer(df, 'd:/015626/Desktop/factor101.h5', dataset='factor101')
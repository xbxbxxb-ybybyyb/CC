import pandas as pd
import numpy as np
import bottleneck as bn


def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table

class Operator(object):
    # def __init__(self, **kwargs):
    #     for k, w in kwargs.items():
    #         setattr(k, w)
    def __init__(self, params):
        self.d = params['d']  # 时间序列移动平均时往前追溯的参数
        self.min_periods = params['min_periods']  # df.rolling()中参数
        self.alpha = params['alpha']  # 移动加权平均中的参数α, α越大近期的权重越大
        self.a = params['a']  # 比较大小并截断的参数, a为数列, 具体用法见相应函数
        # self.condition = params['condition']  # 用于筛选df中符合条件的数
        # self.a = params['a']  # 幂系数

    def ts_mean(self, df1):
        # moving time-series average for the past d periods
        output = pd.DataFrame(bn.move_mean(df1, window=self.d, min_count=self.min_periods, axis=0),
                              index=df1.index, columns=df1.columns)
        return output

    def ts_median(self, df1):
        # moving time-series median for the past d periods
        output = pd.DataFrame(bn.move_median(df1, window=self.d, min_count=self.min_periods, axis=0),
                              index=df1.index, columns=df1.columns)
        return output

    def ts_std(self, df1):
        # moving time-series standard deviation over the past d periods
        output = pd.DataFrame(bn.move_std(df1, window=self.d, min_count=self.min_periods, axis=0, ddof=1),
                              index=df1.index, columns=df1.columns)
        return output

    def ts_skew(self, df1):
        # moving time-series skew over the past d periods
        output = df1.rolling(self.d, min_periods=self.min_periods).skew()
        output.iloc[:self.d - 1] = np.nan
        return output

    def ts_kurt(self, df1):
        # moving time-series kurt over the past d periods
        output = df1.rolling(self.d, min_periods=self.min_periods).kurt()
        output.iloc[:self.d - 1] = np.nan
        return output

    def ts_min(self, df1):
        # time-series min over the past d periods.
        output = pd.DataFrame(bn.move_min(df1, window=self.d, min_count=self.min_periods, axis=0),
                              index=df1.index, columns=df1.columns)
        return output

    def ts_max(self, df1):
        # time-series max over the past d periods.
        output = pd.DataFrame(bn.move_max(df1, window=self.d, min_count=self.min_periods, axis=0),
                              index=df1.index, columns=df1.columns)
        return output

    def ts_product(self, df1):
        # time-series product over the past d periods
        output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
        for i in df1.columns:
            temp_y = df1[i].values
            temp_y = rolling_window(temp_y, self.d)
            flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
            flag = np.where(flag <= self.d - self.min_periods, 1, np.nan)
            output[i].iloc[self.d - 1:] = temp_y.prod(axis=1) * flag
        return output

    def ts_argmax(self, df1):
        # which day ts_max(x, d) occurred on.
        # bn.move_argmin函数的序号是倒序, 与常规的理解相反
        output = pd.DataFrame(bn.move_argmin(df1, window=self.d, min_count=self.min_periods, axis=0),
                              index=df1.index, columns=df1.columns)
        return output

    def ts_argmin(self, df1):
        # which day ts_min(x, d) occurred on.
        # bn.move_argmax函数的序号是倒序, 与常规的理解相反
        output = pd.DataFrame(bn.move_argmax(df1, window=self.d, min_count=self.min_periods, axis=0),
                              index=df1.index, columns=df1.columns)
        return output

    def ts_rank(self, df1):
        # 时序rolling秩
        output = pd.DataFrame(bn.move_rank(df1, window=self.d, min_count=self.min_periods, axis=0),
                              index=df1.index, columns=df1.columns)
        return output

    def ts_bounded_zscore(self, df1):
        # 时序rolling_zscore, 为保证有界性分母做了改动
        # Y_i = (A_i-mean(A))/(max(A)-min(A))
        temp_df_mean = pd.DataFrame(bn.move_mean(df1, window=self.d, min_count=self.min_periods, axis=0),
                                    index=df1.index, columns=df1.columns)
        temp_df_max = pd.DataFrame(bn.move_max(df1, window=self.d, min_count=self.min_periods, axis=0),
                                   index=df1.index, columns=df1.columns)
        temp_df_min = pd.DataFrame(bn.move_min(df1, window=self.d, min_count=self.min_periods, axis=0),
                                   index=df1.index, columns=df1.columns)
        output = (df1 - temp_df_mean) / (temp_df_max - temp_df_min)
        return output

    def ts_sma(self, df1):
        # 移动平均 Y_0 = A_0, Y_i = alpha*A_i + (1-alpha)*Y_(i-1)
        output = df1.ewm(alpha=self.alpha, adjust=False).mean()
        return output

    def ts_decay_linear(self, df1):
        # weighted moving average over the past d periods
        # linearly decaying weights d, d – 1, …, 1 (rescaled to sum up to 1)
        output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
        weight = np.arange(self.d) + 1
        for i in df1.columns:
            temp_y = df1[i].values
            temp_y = rolling_window(temp_y, self.d)
            temp_x = np.tile(weight, (temp_y.shape[0], 1))
            flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
            flag = np.where(flag <= self.d - self.min_periods, 1, np.nan)
            output[i].iloc[self.d - 1:] = ((temp_y * temp_x).sum(axis=1) / temp_x.sum(axis=1)) * flag
        return output

    def ts_wma(self, df1):
        # weighted moving average over the past d periods
        # with linearly decaying weights 1, 0.9, …, 0.9^(d-1) (rescaled to sum up to 1)
        output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
        weight = [(1 - self.alpha) ** i for i in range(self.d - 1, -1, -1)]
        for i in df1.columns:
            temp_y = df1[i].values
            temp_y = rolling_window(temp_y, self.d)
            temp_x = np.tile(weight, (temp_y.shape[0], 1))
            flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
            flag = np.where(flag <= self.d - self.min_periods, 1, np.nan)
            output[i].iloc[self.d - 1:] = ((temp_y * temp_x).sum(axis=1) / temp_x.sum(axis=1)) * flag
        return output

    def ts_wma1(self, df1):
        # 移动平均 using weights (1-alpha)**(n-1), (1-alpha)**(n-2), …, 1-alpha, 1.
        output = df1.ewm(alpha=self.alpha, adjust=True).mean()
        return output

    # def filter(self, df1):
    #     # 对A筛选符合condition的样本
    #     output = df1[self.condition]
    #     return output

    # def ts_condition_count(self, df1):
    #     # 过去d期满足条件的样本个数
    #     temp_df = df1[self.condition]
    #     output = temp_df.rolling(self.d, min_periods=self.min_periods).count()
    #     output.iloc[:self.d - 1] = np.nan
    #     return output

    # def ts_sumif(self, df1):
    #     # 对A过去d期满足条件的元素求和
    #     temp_df = df1[self.condition]
    #     output = temp_df.rolling(self.d, min_periods=self.min_periods).sum()
    #     output.iloc[:self.d - 1] = np.nan
    #     return output

    # def signed_power(self, df1):
    #     # df^a
    #     return df1 ** self.a

    @staticmethod  # 静态函数不必实例化类就可以直接调用: Operator.sign(df1)
    def sign(df1):
        # sign(x) = 1 if x>0
        # sign(x) = 0 if x=0
        # sign(x) = -1 if x<0
        output = np.sign(df1.replace(np.nan, 0))[~df1.isnull()]  # np.sign不接受nan值作为输入, 所以先转为0, 再用[~df1.isnull()]改回nan值
        return output

    @staticmethod
    def log(df1):
        output = np.log(df1[df1 > 0])
        return output

    def delay(self, df1):
        # A_(i-n)
        output = df1.shift(periods=self.d)
        return output

    def delta(self, df1):
        # A_i - A_(i-d)
        output = df1.diff(periods=self.d)
        return output

    def reg_beta(self, df1):
        # 过去d期A对1:d回归的回归系数
        output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
        for i in df1.columns:
            temp_y = df1[i].values
            temp_y = rolling_window(temp_y, self.d)
            temp_x = np.tile(np.arange(self.d) + 1, (temp_y.shape[0], 1))
            y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
            x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
            flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
            flag = np.where(flag <= self.d - self.min_periods, 1, np.nan)
            output[i].iloc[self.d - 1:] = (y / x) * flag
        return output

    def max(self, df1):
        # 把df每列中小于该列给定分位数的数字变为对应分位数字
        output = np.maximum(df1, df1.quantile(self.a[0]))
        return output

    def min(self, df1):
        # 把df每列中大于该列给定分位数的数字变为对应分位数字
        output = np.minimum(df1, df1.quantile(self.a[1]))
        return output


import pandas as pd
import numpy as np


class Operator(object):
    # def __init__(self, **kwargs):
    #     for k, w in kwargs.items():
    #         setattr(k, w)
    def __init__(self, params):
        self.d = params['d']  # 时间序列移动平均时往前追溯的参数
        self.min_periods = params['min_periods']  # df.rolling()中参数
        self.alpha = params['alpha']  # 移动加权平均中的参数α, α越大近期的权重越大
        self.condition = params['condition']  # 用于筛选df中符合条件的数
        self.a = params['a']  # 幂系数

    def ts_corr(self, df1, df2):
        # df1, df2过去d条数据的时序相关系数
        output = df1.rolling(self.d, min_periods=self.min_periods).corr(df2.sort_index())
        output.iloc[:self.d - 1] = np.nan
        return output

    def ts_cov(self, df1, df2):
        # df1, df2过去d条数据的时序协方差
        output = df1.rolling(self.d, min_periods=self.min_periods).cov(df2.sort_index())
        output.iloc[:self.d - 1] = np.nan
        return output

    def min(self, A, B):
        # 返回A,B中对应位置最小值
        if isinstance(A, pd.DataFrame) & isinstance(B, pd.DataFrame):  # A、B都是df
            output = A.copy()
            output[A > B] = B
        elif isinstance(A, pd.DataFrame) & isinstance(B, (int, float)):  # A是df, B是数字
            output = A.copy()
            output[A > B] = B
        elif isinstance(A, (int, float)) & isinstance(B, pd.DataFrame):  # A是数字, B是df
            output = B.copy()
            output[B > A] = A
        else:
            output = A if A < B else B
        return output

    def max(self, A, B):
        # 返回A,B中对应位置最大值
        if isinstance(A, pd.DataFrame) & isinstance(B, pd.DataFrame):  # A、B都是df
            output = A.copy()
            output[A < B] = B
        elif isinstance(A, pd.DataFrame) & isinstance(B, (int, float)):  # A是df, B是数字
            output = A.copy()
            output[A < B] = B
        elif isinstance(A, (int, float)) & isinstance(B, pd.DataFrame):  # A是数字, B是df
            output = B.copy()
            output[B < A] = A
        else:
            output = A if A > B else B
        return output

    def reg_beta(self, A, B):
        # 过去d期A对B回归的回归系数
        output = pd.DataFrame(np.nan, index=A.index, columns=A.columns)
        if isinstance(B, pd.DataFrame):
            for i in range(len(output) - self.d + 1):
                j = i + self.d
                tA = A.iloc[i:j]
                tB = B.iloc[i:j]
                beta = ((tA - tA.mean()) * (tB - tB.mean())).sum() / ((tA - tA.mean()) ** 2).sum()
                output.iloc[j - 1] = np.where((tA.count() >= self.min_periods) &
                                              (tB.count() >= self.min_periods), beta, np.nan)
        else:  # A和1:d滚动回归
            tB = pd.DataFrame(np.tile(np.arange(self.d) + 1, (A.shape[1], 1)).T, columns=A.columns)
            for i in range(len(output) - self.d + 1):
                j = i + self.d
                tA = A.iloc[i:j]
                tB.index = tA.index
                beta = ((tA - tA.mean()) * (tB - tB.mean())).sum() / ((tA - tA.mean()) ** 2).sum()
                output.iloc[j - 1] = np.where(tA.count() >= self.min_periods, beta, np.nan)
        return output

import pandas as pd


class SingleFactorTest:
    def __init__(self, factor, return_raw):
        """
        类初始化
        :param factor: 因子值
        :param return_raw: 收益率序列
        """
        self.factor = factor
        self.return_raw = return_raw

    def calc_ic(self):
        return self.factor.corr(self.return_raw)

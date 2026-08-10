import numpy as np


class CurveFit:
    """
    曲线拟合的各种方法

    Parameters
    ----------
    x: array_like
        regressor
    y: array_like
        regressand
    """
    def __init__(self, x, y):
        assert type(x) == type(y)
        assert x.shape == y.shape
        self.x = x
        self.y = y

    def polynomial_fitting(self, deg):
        """
        多项式拟合
        :param deg: int
            多项式最高阶数
        :return: np.poly1d()
            拟合后多项式的参数
        """
        return np.poly1d(np.polyfit(self.x, self.y, deg=deg))

from sklearn.feature_selection import SelectKBest, mutual_info_classif
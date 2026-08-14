from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import time
from sklearn.neighbors import KNeighborsRegressor

class KNN30(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.pct_chg"]
    #依赖的个人因子库的因子，默认为空，可不设置
    depend_factors = []
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 99
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 5

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        ret = database.depend_data["FactorData.Basic_factor.pct_chg"].copy()
        stock_list = ret.columns
        train_x_list = []
        train_y_list = []
        for i in range(ret.shape[0]-11):
            train_x_list.append(np.array(ret.iloc[i:i+10, :]))
            train_y_list.append(np.array(ret.iloc[i+11, :].rank()))
        train_x = np.concatenate(train_x_list, axis=1).T
        train_y = np.concatenate(train_y_list)
        total = pd.DataFrame(train_x)
        total['label'] = train_y
        total = total.dropna(axis=0, how='any')
        train_x = np.array(total.iloc[:, :10])
        train_y = np.array(total['label'])
        del total
        knn = KNeighborsRegressor(n_neighbors=30, weights='uniform')
        knn.fit(train_x, train_y)
        test_x = ret.iloc[-10:, :].T
        test_x = test_x.dropna(axis=0, how='any')
        remain_index = test_x.index
        ans = knn.predict(test_x)
        ans = pd.Series(ans, index=remain_index)
        ans.reindex(stock_list)
        return ans

    def reform(self, temp_result):
        temp_result = temp_result.astype('float64')
        return temp_result.rolling(self.reform_window).mean()

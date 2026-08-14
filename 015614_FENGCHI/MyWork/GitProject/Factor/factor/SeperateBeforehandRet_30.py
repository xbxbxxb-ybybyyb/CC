from xfactor.BaseFactor import BaseFactor
import pandas as pd
import copy
import numpy as np

def get_SBR(ret: pd.DataFrame, last_turn: pd.DataFrame):
    # 上行
    ret_up = ret[ret > ret.median()]
    ret_up = ret_up * last_turn / last_turn
    codition = pd.isna(ret_up)
    last_turn_up = copy.deepcopy(last_turn)
    last_turn_up[codition == True] = np.nan
    # 下行
    ret_down = ret[ret <= ret.median()]
    ret_down = ret_down * last_turn / last_turn
    codition = pd.isna(ret_down)
    last_turn_down = copy.deepcopy(last_turn)
    last_turn_down[codition == True] = np.nan

    result = []
    for i in last_turn_up.columns:
        data_1: pd.Series = ret_up.loc[:, i].dropna()
        data_2: pd.Series = last_turn_up.loc[:, i].dropna()
        data_3: pd.Series = ret_down.loc[:, i].dropna()
        data_4: pd.Series = last_turn_down.loc[:, i].dropna()
        if data_1.__len__() < 10 or data_2.__len__() < 10 or data_3.__len__() < 10 or data_4.__len__() < 10:
            temp = np.nan
        else:
            temp = data_1.corr(data_2) - data_3.corr(data_4)
        result.append(temp)
    return result


def pre_process(data: pd.Series):
    if data.std() == 0:
        return data
    max_value = data.mean() + 3 * data.std()
    min_value = data.mean() - 3 * data.std()
    data[data > max_value] = max_value
    data[data < min_value] = min_value
    data = (data - data.mean()) / data.std()
    return data

class SeperateBeforehandRet_30(BaseFactor):
    #  定义因子参数
    n = 30
    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.turn", "FactorData.Basic_factor.close", "FactorData.Basic_factor.adjfactor"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 2 * n + 1
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 1

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        close = database.depend_data['FactorData.Basic_factor.close']
        adj = database.depend_data['FactorData.Basic_factor.adjfactor']
        close_adj = close * adj
        turn = database.depend_data['FactorData.Basic_factor.turn']

        ret: pd.DataFrame = (close_adj - close_adj.shift(1)) / close_adj.shift(1)
        last_turn = turn.shift(1)
        number = 2 * self.n
        factor_list = []
        index_list = []
        print('prcocess begin')
        for index in ret.index[2 * self.n:]:
            number = number + 1  # iloc取值左闭右开，当天的因子值需要包括当日行情，所以在开始用number+=1，使取到的行情可以包括今日
            print('{}/{}'.format(number, len(ret.index)))
            index_list.append(index)
            temp_ret = ret.iloc[number - 2 * self.n:number]
            temp_last_turn = last_turn.iloc[number - 2 * self.n:number]
            temp_reult = get_SBR(temp_ret, temp_last_turn)
            factor_list.append(temp_reult)
        factor_data = pd.DataFrame(factor_list, index=index_list, columns=last_turn.columns)
        factor_data = factor_data.iloc[-1,]
        return -factor_data

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean()


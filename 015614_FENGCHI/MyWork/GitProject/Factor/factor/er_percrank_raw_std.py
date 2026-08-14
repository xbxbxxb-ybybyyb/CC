from xfactor.Util import *
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform,min_forward_adj
import statsmodels.api as sm
import pandas as pd
from copy import deepcopy

class er_percrank_raw_std(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.limit_status_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 11
    reform_window = 35
    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        #分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        #处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation = ["drop1", "drop4"])
        limit_status = database.depend_data['FactorData.Basic_factor.limit_status_minute']

        close = data_filter(database.depend_data['FactorData.Basic_factor.close_minute'],limit_status,method='minute')
        min_close=min_forward_adj(close)
        min_close['min'] = [i.minute % 5 for i in min_close.index]
        min_close_5 = min_close[min_close['min']==0]
        min_ret_5 = np.log(min_close_5.iloc[:,:-1]/min_close_5.iloc[:,:-1].shift(1))
        min_ret_5['index'] = min_ret_5.index

        ## 去除包含开盘收益率的数据
        subret_open=min_ret_5.resample('1D').first();
        index_to_drop= subret_open['index'].dropna()
        min_ret_5.drop(index_to_drop.values,axis=0,inplace=True)
        min_ret_5.fillna(0, inplace=True)

        ## 计算MAD并选出高于1.96倍MAD的5分钟收益率作为极致收益率
        subret_np = min_ret_5.iloc[:, :-1].values
        subret_med = np.median(subret_np, axis=0)
        subret_dist = np.abs(subret_np - subret_med)
        MAD = np.median(subret_dist, axis=0)
        MAD_e = 1.483*MAD
        to_cmp = pd.DataFrame(subret_dist-1.96*MAD_e>0,index=min_ret_5.index,columns=min_ret_5.columns[:-1])
        subret_extreme = min_ret_5.iloc[:, :-1][to_cmp]
        subret_extreme['date'] =[i.date() for i in subret_extreme.index]

        ## 进行最后一天的五分钟收益率的求和合成日度的极致收益率(此处取47个五分钟收益率是因为之前计算五分钟的收益率的方法会让一天的五分钟收益率个数少一个)
        subret_extreme = subret_extreme.iloc[-47:,:-1].sum(axis=0)
        return subret_extreme

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    def reform(self, temp_result):
        # 因子计算的历史分位数函数
        def get_rollingperc(info):
            info_rollingmean = info.rolling(window=20, min_periods=1).mean().shift(1)
            info_rollingstd = info.rolling(window=20, min_periods=1).apply(lambda x:x.std()).shift(1)
            info_rollingstd[abs(info_rollingstd) <= 0.00001] = np.nan
            info_rollingperc = (info - info_rollingmean) / info_rollingstd
            return info_rollingperc
        raw_data = deepcopy(temp_result)
        raw_data = get_rollingperc(raw_data).rank(axis=1)
        last_window = 5  # 此处为最后统计量需要的窗口
        alpha = raw_data.rolling(window=last_window ,min_periods=last_window // 2).apply(lambda x:x.std())
        return alpha


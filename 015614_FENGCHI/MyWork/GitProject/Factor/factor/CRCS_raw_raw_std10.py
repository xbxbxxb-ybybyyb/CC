from xfactor.Util import *
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
import statsmodels.api as sm
from copy import deepcopy
from xfactor.FixUtil import minute_data_transform,min_forward_adj


class CRCS_raw_raw_std10(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.limit_status_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag=9
    reform_window=20
    batch_info={'is_adj':'raw','is_rank':'raw','single_chr':'std'}
    is_adj=batch_info['is_adj']
    is_rank=batch_info['is_rank']
    single_chr=batch_info['single_chr']

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        #分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        #处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation = ["drop1", "drop4"])
        limit_status = database.depend_data['FactorData.Basic_factor.limit_status_minute']


        # 播放的数据通过database.depend_data字典获取
        close_adj = data_filter(database.depend_data['FactorData.Basic_factor.close_minute'],limit_status,method='minute')
        close_adj = min_forward_adj(close_adj)
        subret = pd.DataFrame(close_adj.values / close_adj.values[0, :], index=close_adj.index,
                              columns=close_adj.columns)
        subret['date'] = [i.date() for i in subret.index]
        def getslope(is_adj, is_rank, subret):
            # 判断是否提取最后30分钟
            # 判断是否进行时序rank
            if is_rank == 'rank':
                subret = subret.rank()
            elif is_rank == 'raw':
                pass
            else:
                raise Exception
            tm_id = list(range(len(subret)))
            x = sm.add_constant(tm_id)
            res = sm.OLS(subret, x).fit()
            subslope = res.params.ix['x1', :]
            subslope = (subslope).astype(np.float64)
            subslope = subslope[~np.isinf(subslope)]
            subslope.index = subret.columns
            # 判断是否需要用可决系数对beta进行调整
            if is_adj == 'adj':
                proj = subret.values - res.resid.values
                proj_np = np.array(proj)
                subret_np = np.array(subret)
                inner_prd = ((proj_np - proj_np.mean(axis=0)) * (subret_np - subret_np.mean(axis=0))).sum(axis=0) / len(
                    proj_np)
                std_proj, std_sbrt = proj_np.std(axis=0), subret_np.std(axis=0)
                R_squared = np.power(inner_prd / (std_proj * std_sbrt), 2)
                adj_subslope = pd.Series(subslope.values * R_squared, index=subret.columns)
                return adj_subslope
            elif is_adj == 'raw':
                return subslope
            else:
                raise Exception

        sng_slope = subret.iloc[:, :-1].groupby(subret['date']).apply(
            lambda x: getslope(self.is_adj, self.is_rank, x))

        def get_rollingperc(info):
            info_rollingmean = info.iloc[:-1, :].mean()
            info_rollingstd = info.iloc[:-1, :].std()
            info_rollingstd[abs(info_rollingstd / info.iloc[-1, :]) <= 0.00001] = np.nan
            info_rollingperc = (info - info_rollingmean) / info_rollingstd
            return info_rollingperc

        # 判断统计量
        alpha_data = deepcopy(sng_slope)
        if self.single_chr in ['mean', 'std', 'skew', 'kurt']:
            alpha = eval("alpha_data." + str(self.single_chr) + "()")
        elif self.single_chr == 'ms':
            alpha_data_std = alpha_data.std()
            alpha_data_std[abs(alpha_data_std / alpha_data.iloc[-1, :]) <= 0.00001] = np.nan
            alpha = alpha_data.mean() / alpha_data_std
        elif self.single_chr == 'zscore':
            alpha = get_rollingperc(alpha_data)
        else:
            raise Exception
        return alpha

    def reform(self, temp_result):
        
        alpha = temp_result  # 传入这里的函数每天都会调用一次播放数据计算中间量
        return alpha



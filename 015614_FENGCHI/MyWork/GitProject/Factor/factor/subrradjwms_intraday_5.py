from xfactor.Util import *
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj


class subrradjwms_intraday_5(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.high_minute","FactorData.Basic_factor.low_minute","FactorData.Basic_factor.limit_status_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag=4
    reform_window=1

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        #分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        #处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        limit_status = database.depend_data['FactorData.Basic_factor.limit_status_minute']
        close = data_filter(database.depend_data['FactorData.Basic_factor.close_minute'],limit_status,method='minute')
        close_adj=min_forward_adj(close)
        ret=pd.DataFrame(close_adj.values / close_adj.shift(1).values - 1, index=close_adj.index,
                     columns=close_adj.columns)
        database.depend_data['FactorData.Basic_factor.ret_minute'] = ret
        minute_data_transform(database.depend_data, operation=["drop1", "drop4"])


        ret_adj = database.depend_data['FactorData.Basic_factor.ret_minute'].copy()

        # 播放的数据通过database.depend_data字典获取
        high_adj = data_filter(database.depend_data['FactorData.Basic_factor.high_minute'],limit_status,method='minute')
        high_adj = min_forward_adj(high_adj)
        low_adj = data_filter(database.depend_data['FactorData.Basic_factor.low_minute'],limit_status,method='minute')
        low_adj = min_forward_adj(low_adj)
        subhigh = high_adj.resample('5min').max().dropna(how='all')
        sublow = low_adj.resample('5min').min().dropna(how='all')
        subrange = pd.DataFrame(subhigh.values / sublow.values, index=subhigh.index, columns=subhigh.columns)
        subret = ret_adj.resample('5min').sum().dropna(how='all')
        subret = subret.reindex(subrange.index)
        date = pd.Series([i.date() for i in subhigh.index], index=subhigh.index)
        date_bf = date[date != date.values[-1]].index.tolist()
        date_crt = date[date == date.values[-1]].index.tolist()
        subret_bf = subret.loc[date_bf, :]
        subrange_bf = subrange.loc[date_bf, :]
        subret_crt = subret.loc[date_crt, :]
        subrange_crt = subrange.loc[date_crt, :]

        subrr_bf = pd.DataFrame((subret_bf.values) / subrange_bf.values, index=subrange_bf.index,
                                columns=subrange_bf.columns)
        subrr_crt = pd.DataFrame((subret_crt.values) / subrange_crt.values, index=subrange_crt.index,
                                 columns=subrange_crt.columns)
        alpha_bf = pd.Series(np.nanmean(subrr_bf.values, axis=0) / np.nanstd(subrr_bf.values, axis=0),
                             index=subrr_bf.columns)
        alpha_crt = pd.Series(np.nanmean(subrr_crt.values, axis=0) / np.nanstd(subrr_crt.values, axis=0),
                              index=subrr_crt.columns)
        alpha_crt_rank = alpha_crt.rank(pct=True)
        alpha_bf_rank = alpha_bf.rank(pct=True)
        alpha_bf[(alpha_crt_rank < 0.15) & (alpha_bf_rank < 0.5)] = alpha_bf.median()
        return alpha_bf

    def reform(self, temp_result):
        
        alpha = temp_result
        return alpha



# -*- coding: utf-8 -*-
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
class HighFreqTurnRetCorr(BaseFactor):
     # 因子频率，。默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.close_adj_minute","FactorData.Basic_factor.free_float_shares",
    "FactorData.Basic_factor.close"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    minute_lag = 5
    lag = 2
    # fix_times=["1300"]
    def calc_single(self, database):
        data_min = {"FactorData.Basic_factor.amt_minute":database.depend_data['FactorData.Basic_factor.amt_minute'],
                   "FactorData.Basic_factor.close_adj_minute":database.depend_data['FactorData.Basic_factor.close_adj_minute']}
        minute_data_transform(data_min, operation = ['drop', 'merge'])
        MinuteTurnover = data_min['FactorData.Basic_factor.amt_minute']  
        MinuteClose = data_min['FactorData.Basic_factor.close_adj_minute']
        close = database.depend_data['FactorData.Basic_factor.close']
        free_float_shares = database.depend_data['FactorData.Basic_factor.free_float_shares']
        free_float_cap = close*free_float_shares
        free_float_cap = pd.DataFrame(free_float_cap.values*10000,index=free_float_cap.index,columns=free_float_cap.columns)
        pv_corr = -self.minute_help( MinuteTurnover, MinuteClose, free_float_cap)
        return pv_corr


    def minute_help(self, MinuteTurnover, MinuteClose, free_float_cap):
        fmt = '%Y%m%d'
        date_list = sorted(np.unique(MinuteTurnover.index.strftime(fmt)))
        compute_date = date_list[-1]
        pre_date = date_list[-2]
        Close = MinuteClose.loc[compute_date]
        pre_Close = MinuteClose.loc[pre_date]
        amt_min = MinuteTurnover.loc[compute_date]

        turnover =pd.DataFrame(amt_min.values/free_float_cap.loc[pre_date].values,index=amt_min.index,columns=amt_min.columns)
        amt_min_pre =  MinuteTurnover.loc[pre_date]
        pre_turnover =pd.DataFrame(amt_min_pre.values/free_float_cap.loc[pre_date].values,index=amt_min_pre.index,columns=amt_min_pre.columns)
        # ret = Close.pct_change(1)
        # pre_ret = pre_Close.pct_change(1)
        turnover = turnover.append(pre_turnover)
        # ret = ret.append(pre_ret)
        Close_append = Close.append(pre_Close)
        ret1 = pd.DataFrame((Close_append.values - Close_append.iloc[0].values)/Close_append.iloc[0].values,index=Close_append.index,columns=Close_append.columns)
        t_ret_corr1 = Util.array_coef(turnover,ret1)

        return t_ret_corr1
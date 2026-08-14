from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class Min_RelativeDownReturn(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.open_minute","FactorData.Basic_factor.close_minute"]
    lag = 0
    reform_window = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteOpen = database.depend_data['FactorData.Basic_factor.open_minute']
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']

        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteOpen.index.strftime(fmt))
        # res = {}
        # for date in date_list:
        date = date_list[-1]
        dt = pd.Timestamp(date)
        Open = MinuteOpen.loc[date]
        Close = MinuteClose.loc[date]
        ret = pd.DataFrame(Close.values/Open.values-1,index=Close.index,columns=Close.columns)
        mean_ret = ret.rolling(window=10,min_periods=1).mean()
        std_ret = ret.rolling(window=10,min_periods=1).std()
        boll_down = mean_ret.values-2*std_ret.values
        down_range = boll_down-ret.values
        ratio = down_range/boll_down
        ratio[down_range<=0] = np.nan
        res = np.nansum(ratio,axis=0)

        # res = pd.DataFrame(res).T
        return -pd.Series(res,index=Close.columns)

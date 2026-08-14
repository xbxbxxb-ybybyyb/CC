from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform
import pandas as pd

class TurnoverHighRetSharpe(BaseFactor):

    factor_type = "FIX"
    depend_data = [ 
                 "FactorData.Basic_factor.open_minute",
                 "FactorData.Basic_factor.amt_minute",]

    lag = 1
    minute_lag = 1
    reform_window= 10
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        open_minute = database.depend_data['FactorData.Basic_factor.open_minute']
        amt_minute = database.depend_data['FactorData.Basic_factor.amt_minute']
        fmt = '%Y%m%d'
        date_list = sorted(np.unique(amt_minute.index.strftime(fmt)))
        compute_date = date_list[-1]
        pre_date = date_list[-2]
        open_today = open_minute.loc[compute_date]
        re_today = pd.DataFrame(open_today.values/open_today.shift(1).values-1, index=open_today.index,columns=open_today.columns)
        open_yesterday = open_minute.loc[pre_date]
        re_yesterday = pd.DataFrame(open_yesterday.values/open_yesterday.shift(1).values-1, index=open_yesterday.index,columns=open_yesterday.columns)

        zscore_today =pd.DataFrame((re_today.values - re_today.mean().values) / re_today.std().values, index = re_today.index,columns = re_today.columns)
        zscore_yesterday =pd.DataFrame((re_yesterday.values - re_yesterday.mean().values) / re_yesterday.std().values , index = re_yesterday.index,columns = re_yesterday.columns)
        thresh = 2
        cond1 =pd.DataFrame(zscore_today.values > thresh,index = zscore_today.index, columns=zscore_today.columns)
        cond2 = pd.DataFrame(zscore_yesterday.values > thresh,index = zscore_yesterday.index, columns=zscore_yesterday.columns)

        turnover = amt_minute.loc[compute_date][cond1]
        turnover_yesterday = amt_minute.loc[pre_date][cond2]
        result = turnover.sum() + turnover_yesterday.sum()

        return result
    
    def reform(self, temp_result):
        return temp_result.rolling(window=self.reform_window, min_periods=1).mean()/temp_result.rolling(window=self.reform_window, min_periods=1).std()


    
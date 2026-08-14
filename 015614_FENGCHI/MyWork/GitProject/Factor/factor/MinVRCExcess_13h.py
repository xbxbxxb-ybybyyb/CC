# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform,min_forward_adj
import time


class MinVRCExcess_13h(BaseFactor):
    factor_type = 'FIX'     
    # fix_times = ["1300"]
    depend_data = ['FactorData.Basic_factor.close_minute', 'FactorData.Basic_factor.citics_indcode1']   
    lag = 1

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        citics_indcode1 = database.depend_data['FactorData.Basic_factor.citics_indcode1'][MinuteClose.columns]

        fmt = '%Y%m%d'
        date_list = sorted(np.unique(MinuteClose.index.strftime(fmt)))
        date = date_list[-1]
        pre_date = date_list[-2]

        close = MinuteClose.loc[date]
        t = np.array([list(range(1,close.shape[0]+1))]*close.shape[1]).T
        industry = citics_indcode1.loc[pre_date]
        indus_unique = industry.unique()
        r = 1-close.values/close.iloc[-1].values
        for indus in indus_unique:
            ind = np.where(industry==indus)[0]
            r[:,ind] = r[:,ind]-np.nanmean(r[:,ind],axis=1).reshape(r.shape[0],1)
        w = t/np.nansum(t,axis=0)
        MinARC = np.sum(r*w,axis=0)
        MinVRC = np.nansum((w*(r-MinARC)**2),axis=0)

        return pd.Series(-np.sqrt(MinVRC),index=close.columns)
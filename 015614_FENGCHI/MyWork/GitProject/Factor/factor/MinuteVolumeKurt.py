from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class MinuteVolumeKurt(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.volume_minute"]
    lag = 0
    reform_window = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteVolume.index.strftime(fmt))

        date = date_list[-1]
        volume = MinuteVolume.loc[date]
        volume = volume.resample('5T').sum()
        kurt = volume.iloc[-30:].kurt()
        if np.sum(~np.isnan(kurt))==0:
            kurt = np.array([0.0]*volume.shape[1])

        return pd.Series(-kurt,index=volume.columns)

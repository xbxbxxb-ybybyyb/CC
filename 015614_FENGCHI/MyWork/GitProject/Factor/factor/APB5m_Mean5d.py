from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform


class APB5m_Mean5d(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.volume_adj_minute", 
                   "FactorData.Basic_factor.amt_minute", 
                "FactorData.Basic_factor.is_valid", ]
    
    lag = 0
    minute_lag = 0
    reform_window = 5
    
    def calc_single(self, database):
    
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        amt_minute = database.depend_data['FactorData.Basic_factor.amt_minute']
        volume_adj_minute = database.depend_data['FactorData.Basic_factor.volume_adj_minute']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']
        valid = pd.DataFrame(is_valid.values==1, index=is_valid.index, columns=is_valid.columns).iloc[-1]
        amt_minute.index = pd.to_datetime(amt_minute.index)

        volume_adj_minute.index = pd.to_datetime(volume_adj_minute.index)
        amt_minute = amt_minute.groupby(pd.Grouper(freq='5min')).sum()
        volume_adj_minute = volume_adj_minute.groupby(pd.Grouper(freq='5min')).sum()
        
        amt_minute = pd.concat([amt_minute.between_time(start_time='09:30:00',end_time='11:29:00'),
                                amt_minute.between_time(start_time='13:00:00',end_time='14:59:00')]).sort_index()
        volume_adj_minute = pd.concat([volume_adj_minute.between_time(start_time='09:30:00',end_time='11:29:00'),
                                volume_adj_minute.between_time(start_time='13:00:00',end_time='14:59:00')]).sort_index()        

        vwap_adj = (amt_minute/volume_adj_minute).fillna(method='ffill')
        volume = volume_adj_minute.fillna(0)
        
        vwap_adj_avg = vwap_adj.mean()
        vwap_adj_weightavg = (vwap_adj*volume).sum()/volume.sum()
                
        result = np.log(vwap_adj_avg/vwap_adj_weightavg)
        return result[valid]

    def reform(self,temp_result):
        factor = temp_result
        res =factor.rolling(5,1).mean()
        return res

        

    
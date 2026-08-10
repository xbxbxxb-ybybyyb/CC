import numpy as np
from future_factor import FutureFactor

class MinuteTotalValueTrade3Ratio(FutureFactor):
    '''
    Description: mean(TotalValueTrade_03 / (TotalValueTrade_00 + TotalValueTrade_01 + TotalValueTrade_02 + TotalValueTrade_03), 10)
    Class: All_Contract
    Author: jinpx, modified by jinpx
    '''   
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Other_Future_Instrument'] = {'00':['TotalValueTrade'], '01':['TotalValueTrade'], '02':['TotalValueTrade'], '03':['TotalValueTrade']}
    normalize_size = 10 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        totalvaluetrade_00 = data['TotalValueTrade_00'].values
        totalvaluetrade_01 = data['TotalValueTrade_01'].values
        totalvaluetrade_02 = data['TotalValueTrade_02'].values
        totalvaluetrade_03 = data['TotalValueTrade_03'].values
        
        N = 10
        totalvaluetrade_ratio = totalvaluetrade_03[-N:]/(totalvaluetrade_00[-N:]+totalvaluetrade_01[-N:]+totalvaluetrade_02[-N:]+totalvaluetrade_03[-N:])
        f = np.nanmean(totalvaluetrade_ratio)
        
        return f
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 11:10:35 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

def normalization(signal, holding_window = 1200): 
    max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
    min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
    a = (signal - min_s)/(max_s-min_s)
    a = 2*a-1
    aa = pd.DataFrame(a)
    aa.index = signal.index
    aa.columns = signal.columns
    return aa

class MDI_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['low_spot', 'high_spot', 'open_spot']

        super(MDI_ind_CC, self).__init__(
                                  required_columns=required_columns)

    def on_bar(self, data):
        idx = data.index
        data = data.loc[~(((idx.hour==9) & (idx.minute < 30)) | ((idx.hour==11) & (idx.minute == 30)))]
        data = data.sort_index()
        
        mdi_p = data['open_spot'].diff()>0
        mdi_n = data['open_spot'].diff()<0

        hmo = data['high_spot'] - data['open_spot']
        oml = data['open_spot'] - data['low_spot']
        od = data['open_spot'].diff()
        ps1 = hmo.where(hmo>od, other=od)
        MDI_up = ps1.where(od>=0,other=0)
        ps2 = oml.where(oml>od,other=od)
        MDI_down = ps2.where(od<=0,other=0)
        MDI_up = MDI_up.rolling(120,min_periods=30).mean()
        MDI_down = MDI_down.rolling(120,min_periods=30).mean()
        MDI_max = MDI_up.where(MDI_up>MDI_down,other=MDI_down)
        sig = ((MDI_up-MDI_down)/MDI_max)
        factor = sig.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = normalization(factor)
        
        factor[factor>=0] = np.nan
        return factor
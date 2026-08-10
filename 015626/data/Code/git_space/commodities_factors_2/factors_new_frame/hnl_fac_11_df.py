from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class hnl_fac_11_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(int(np.ceil(1200 / self.bars_dict[self.ticker])) * freq)
        self.required_columns = [ 'close', 'tday']
        self.instrument_type = 'main' #second_main
        self.normalize_size = int(int(self.bars_dict[self.ticker]) / int(self.freq) * 3)
        self.normalize_type = 'calc_zscore'
        self.factor_name = self.__class__.__name__
        self.chip_dis_short_list = []
        self.chip_dis_long_list = []
        self.fac_raw2_list = []
        self.fac_raw_list = []
    
    def calculate(self, data):

        unit = int(self.freq)
        hclose = data['close'][-555:]
        coef = int(int(self.bars_dict[self.ticker]) / int(self.freq))
        hdiff = hclose[1:] - hclose[:-1]
        
        chip_dis_short = rolling_norm_raw(hclose,  nanmin_np([int(10 / unit), 4]))
        self.chip_dis_short_list.append(chip_dis_short)
        chip_dis_long = rolling_norm_raw(hclose,  int(coef))
        self.chip_dis_long_list.append(chip_dis_long)
        fac_raw =   - chip_dis_long# - chip_dis_short.rolling(60, min_periods = 1).mean()
        self.fac_raw_list.append(fac_raw)
        vol = nanstd_np(hdiff[-int(coef / 10):])
        fuck = np.column_stack((self.chip_dis_short_list[-int(coef / 2):], self.chip_dis_long_list[-int(coef / 2):]))
        fuck = fuck[~np.isnan(fuck).any(axis = 1)]
        fac_raw2 = corrcoef_np(fuck[:, 0], fuck[:, 1])[0][1] * np.sign(chip_dis_short)
        fac_raw2 = fac_raw2 / r(vol) / r(vol)
        self.fac_raw2_list.append(fac_raw2)
        
        fac1 = -calc_zscore_raw(self.fac_raw2_list, int(coef / 2)) - calc_zscore_raw(self.fac_raw_list, int(coef / 2))
        return fac1
    def pre_calculate(self, data):
        self.chip_dis_short_list = []
        self.chip_dis_long_list = []
        self.fac_raw2_list = []
        self.fac_raw_list = []
        for i in range(1200, -1, -1):
            if i == 0:
                hclose = data['close'][-555 - i:]

            else:
                hclose = data['close'][-555 - i: -i]
 
            hdiff = hclose[1:] - hclose[:-1]
            unit = int(self.freq)
            coef = int(int(self.bars_dict[self.ticker]) / int(self.freq))
            
            chip_dis_short = rolling_norm_raw(hclose,  nanmin_np([int(10 / unit), 4]))
            self.chip_dis_short_list.append(chip_dis_short)
            chip_dis_long = rolling_norm_raw(hclose,  int(coef))
            self.chip_dis_long_list.append(chip_dis_long)
            fac_raw =   - chip_dis_long# - chip_dis_short.rolling(60, min_periods = 1).mean()
            self.fac_raw_list.append(fac_raw)
            vol = nanstd_np(hdiff[-int(coef / 10):])
            fuck = np.column_stack((self.chip_dis_short_list[-int(coef / 2):], self.chip_dis_long_list[-int(coef / 2):]))
            fuck = fuck[~np.isnan(fuck).any(axis = 1)]
            fac_raw2 = corrcoef_np(fuck[:, 0], fuck[:, 1])[0][1] * np.sign(chip_dis_short)
            fac_raw2 = fac_raw2 / r(vol) / r(vol)
            self.fac_raw2_list.append(fac_raw2)
            


        
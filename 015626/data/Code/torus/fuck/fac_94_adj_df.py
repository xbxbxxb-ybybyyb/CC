from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class fac_94_adj_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(int(np.ceil(1601 / self.bars_dict[self.ticker])) * freq)
        self.required_columns = [ 'high', 'close', 'BidAskSpreadMean', 'low', 'dt']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 2400
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.fac_list = []

    def calculate(self, data):
        hclose = data['close'][-31:]
        coef_temp = nanstd_np(hclose[1:] - hclose[:-1], ddof = 1) / r(nanmean_np(data['BidAskSpreadMean'][-30:]))
        dlow = data['low'][-1201:]
        dhigh = data['high'][-1201:]
        aaa = 400
        
        if coef_temp > 10:
            coef =0.3
        elif (coef_temp > 6) and (coef_temp <= 10):
            coef = 0.5
        elif (coef_temp > 4) and (coef_temp <= 6):
            coef = 1
        elif (coef_temp > 3) and (coef_temp <= 4):
            coef = 2
        elif (coef_temp <= 3):
            coef = 3
        else:
            coef = 6


        locallow = nanargmin_new(dlow[-int(nanmax_np([1, aaa * coef])):])
        
        fac_high = nanmax_np(dhigh[locallow:])
        fac_low = nanmin_np(dlow[locallow:])

        fac = (data['close'][-1] - fac_low) / r(fac_high - fac_low)
        self.fac_list.append(fac)
        #if data['dt'][-1] == np.datetime64(pd.to_datetime('201703032100')):
        #    print(self.fac_list[-40:])
        return irr_filter_raw(self.fac_list[-40:], 8)[-1]
    def pre_calculate(self, data):
        for i in range(41, -1, -1):
            if i == 0:
                hclose = data['close'][-31 - i:]
                ba = data['BidAskSpreadMean'][-30 - i:]
                dlow = data['low'][-1201 - i:]
                dhigh = data['high'][-1201 - i:]
    
            else:
                hclose = data['close'][-31 - i: -i]
                ba = data['BidAskSpreadMean'][-30 - i: -i]
                dlow = data['low'][-1201 - i: -i]
                dhigh = data['high'][-1201 - i: -i]
            if len(hclose) < 10:
                self.fac_list.append(np.nan)
                continue
            aaa = 400
            
            coef_temp = nanstd_np(hclose[1:] - hclose[:-1], ddof = 1) / r(nanmean_np(ba))
            if coef_temp > 10:
                coef =0.3
            elif (coef_temp > 6) and (coef_temp <= 10):
                coef = 0.5
            elif (coef_temp > 4) and (coef_temp <= 6):
                coef = 1
            elif (coef_temp > 3) and (coef_temp <= 4):
                coef = 2
            elif (coef_temp <= 3):
                coef = 3
            else:
                coef = 6
    
        
            locallow = nanargmin_new(dlow[-int(nanmax_np([1, aaa * coef])):])
            
            fac_high = nanmax_np(dhigh[locallow:])
            fac_low = nanmin_np(dlow[locallow:])
    
            fac = (hclose[-1] - fac_low) / r(fac_high - fac_low)
            self.fac_list.append(fac)

        
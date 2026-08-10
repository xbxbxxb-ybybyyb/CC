from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np




class fac_49_adj_df_5x_(FutureFactor):
    required_columns = ['close', 'BidAskSpreadMean', 'high', 'low']

    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(int(np.ceil(6000 / self.bars_dict[self.ticker])) * self.freq)
        self.required_columns = ['close', 'BidAskSpreadMean', 'high', 'low']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 1000
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.temp2_list = []
        self.temp4_list = []


        
    def calculate(self, data):
        hclose = data['close'][-31:]
        coef_temp = nanstd_np(hclose[1:] - hclose[:-1], ddof = 1) / r(nanmean_np(data['BidAskSpreadMean'][-30:]))

        
        if coef_temp > 10:
            coef =0.1
        elif (coef_temp > 6) and (coef_temp <= 10):
            coef = 0.3
        elif (coef_temp > 4) and (coef_temp <= 6):
            coef = 1
        elif (coef_temp > 3) and (coef_temp <= 4):
            coef = 2
        elif (coef_temp <= 3):
            coef = 5
        else:
            coef = 6
        
        
        aaa = 900
        b = 300
        c = 50
        d = 5
        

        dclose = data['close'][-aaa * 5 - 5 :]
        dhigh = data['high'][-aaa * 5 - 5 :]
        dlow = data['low'][-aaa * 5 - 5 :]
        
        low_n = nanmin_np(dlow[-int(coef * aaa):])
        high_n = nanmax_np(dhigh[-int(coef * aaa):])
        temp1 = high_n - low_n

        temp2 = (dclose[-1] - low_n) / r(temp1)
        self.temp2_list.append(temp2)

        
        b_low = nanmin_np(self.temp2_list[-b:])
        b_high = nanmax_np(self.temp2_list[-b:])

        temp3 = b_high - b_low
        temp4 = (temp2 - b_low) / r(temp3)
        self.temp4_list.append(temp4)


        sig = irr_filter4(self.temp4_list, coef, c) + temp4

        return sig

    def pre_calculate(self, data):
        self.temp2_list = []
        self.temp4_list = []
        aaa = 900
        b = 300
        c = 50
        d = 5
        
        for i in range(1200, -1, -1):
            
            if i == 0:
                hclose = data['close'][(-31 - i) : ]
                dclose = data['close'][-aaa * 5 - 5 :]
                dhigh = data['high'][-aaa * 5 - 5 :]
                dlow = data['low'][-aaa * 5 - 5 :]
                ba = data['BidAskSpreadMean'][(-30 - i) : ]

            else:
                hclose = data['close'][(-31 - i) : -i]
                dclose = data['close'][-aaa * 5 - 5 - i : -i]
                dhigh = data['high'][-aaa * 5 - 5 - i: -i]
                dlow = data['low'][-aaa * 5 - 5 - i: -i]
                ba = data['BidAskSpreadMean'][(-30 - i) : -i]


            coef_temp = nanstd_np(hclose[1:] - hclose[:-1], ddof = 1) / r(nanmean_np(ba))
    
            
            if coef_temp > 10:
                coef =0.1
            elif (coef_temp > 6) and (coef_temp <= 10):
                coef = 0.3
            elif (coef_temp > 4) and (coef_temp <= 6):
                coef = 1
            elif (coef_temp > 3) and (coef_temp <= 4):
                coef = 2
            elif (coef_temp <= 3):
                coef = 5
            else:
                coef = 6
            
            if len(dclose) == 0:
                temp2 = np.nan
            else:
                low_n = nanmin_np(dlow[-int(coef * aaa):])
                high_n = nanmax_np(dhigh[-int(coef * aaa):])
                temp1 = high_n - low_n
        
                temp2 = (dclose[-1] - low_n) / r(temp1)
            self.temp2_list.append(temp2)
            b_low = nanmin_np(self.temp2_list[-b:])
            b_high = nanmax_np(self.temp2_list[-b:])
            temp3 = b_high - b_low
            temp4 = (temp2 - b_low) / r(temp3)

                
            
            self.temp4_list.append(temp4)


        
        
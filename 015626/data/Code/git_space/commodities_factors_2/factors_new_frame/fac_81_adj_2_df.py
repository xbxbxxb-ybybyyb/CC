from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class fac_81_adj_2_df(FutureFactor):


    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(4 * self.freq)
        self.required_columns = ['buy_small_volume',  'sell_small_volume', 'low', 'BidAskSpreadMean', 'close']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 1200
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.fac1_list = []



        
    def calculate(self, data):
        hclose = data['close'][-31:]
        coef_temp = nanstd_np(hclose[1:] - hclose[:-1], ddof = 1) / r(nanmean_np(data['BidAskSpreadMean'][-30:]))
        
        aaa = 120
        
        if coef_temp > 10:
            coef =0.1
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

        locallow = nanargmin_new(data['low'][-int(nanmax_np([1, aaa * coef])):])
        
        fac = (data['buy_small_volume'][-400:]- data['sell_small_volume'][-400:])
        fac = nanmean_np(-fac[locallow:])

        if ('SC' in self.ticker) or ('AU' in self.ticker) or ('CU' in self.ticker) or ('SN' in self.ticker):
            fac = -fac
        self.fac1_list.append(fac)
        return irr_filter(self.fac1_list[-10:], 2)[-1]
        
    def pre_calculate(self, data):
        self.fac1_list = []
        
        aaa = 120
        
        for i in range(10, -1, -1):
            
            if i == 0:
                hclose = data['close'][(-31 - i) : ]
                dclose = data['close'][-aaa * 5 - 5 :]
                dlow = data['low'][-aaa * 5 - 5 :]
                ba = data['BidAskSpreadMean'][(-30 - i) : ]
                bsv = data['buy_small_volume'][(-400 - i) :]
                ssv = data['sell_small_volume'][(-400 - i) :]

            else:
                hclose = data['close'][(-31 - i) : -i]
                dclose = data['close'][-aaa * 5 - 5 - i : -i]
                dlow = data['low'][-aaa * 5 - 5 - i: -i]
                ba = data['BidAskSpreadMean'][(-30 - i) : -i]
                bsv = data['buy_small_volume'][(-400 - i) : -i]
                ssv = data['sell_small_volume'][(-400 - i) : -i]
                

            coef_temp = nanstd_np(hclose[1:] - hclose[:-1], ddof = 1) / r(nanmean_np(ba))
            

            
            if coef_temp > 10:
                coef =0.1
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
            
            fac = (bsv- ssv)
            fac = nanmean_np(-fac[locallow:])

            if ('SC' in self.ticker) or ('AU' in self.ticker) or ('CU' in self.ticker) or ('SN' in self.ticker):
                fac = -fac

            self.fac1_list.append(fac)
        
        
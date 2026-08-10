from future_factor import FutureFactor
import pandas as pd
import numpy as np
import numpy.ma as ma
import bottleneck as bk

# factor = div2(bun_to_bn_w2, sun_to_sn_w2) * -1
class search2_wyc(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['SellUniqueOrderNum', 'SellTradeNum','BuyUniqueOrderNum', 'BuyTradeNum','weight']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    
    def calculate(self, df):
        weight = df['weight'][-1:].values
        bun = df['BuyUniqueOrderNum'][-2:].sum(axis = 0)
        bn = df['BuyTradeNum'][-2:].sum(axis = 0).replace(0, np.nan)
        sun = df['SellUniqueOrderNum'][-2:].sum(axis = 0)
        sn = df['SellTradeNum'][-2:].sum(axis = 0).replace(0, np.nan)
        
        bun_to_bn_w2 = np.nansum((bun / bn).values * weight)
        sun_to_sn_w2 = np.nansum((sun / sn).values * weight)

        if sun_to_sn_w2 == 0:
            return np.nan
        else:
            return bun_to_bn_w2 / sun_to_sn_w2 * -1
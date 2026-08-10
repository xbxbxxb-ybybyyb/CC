from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import bottleneck as bk

def rank_data(data):
    n = len(data)
    if n < 1:
        return np.nan
    elif n == 1:
        return 0.0
    data = np.array(data)
    current_value = data[-1]
    less = np.sum(data < current_value)
    equal = np.sum(data == current_value)
    rank = less + (equal + 1) / 2
    return 2 * ((rank - 1) / (n - 1)) - 1

class fac_71_df(FutureFactor):    

    def __init__(self, ticker, freq = 1):
        super().__init__()
        self.factor_name = self.__class__.__name__
        self.required_columns = ['close','BidAskSpreadMean','twap']
        self.normalize_size = 400
        self.normalize_type = 'ts_rank'
        self.ticker = ticker
        self.freq = freq
        self.days_past = int(freq) * 3 # different product should be different
        self.rmax_list = []
        self.rmin_list = []        
        self.rshift_list = []
    
    def calculate(self, data):
        cls = data['close'][-31:]
        bidaskmean = data['BidAskSpreadMean'][-31:]
        hclose = data['twap'][-300:]
        cls_diff = cls[1:] - cls[:-1]
        cls_diff_std = nanstd_np(cls_diff[-30:],ddof = 1)
        bidaskmean_m = nanmean_np(bidaskmean[-30:])
        if abs(bidaskmean_m) < 1e-9:
            bidaskmean_m = np.nan
        coef_temp = cls_diff_std / bidaskmean_m
        if coef_temp > 10:
            coef = 0.1
        elif coef_temp > 6:
            coef = 0.3
        elif coef_temp > 4:
            coef = 1
        elif coef_temp > 3:
            coef = 2
        else:
            coef = 5        

        if len(hclose) >= int(50 * np.sqrt(coef)):
   
            rmax = nanmax_np(hclose[-int(50 * np.sqrt(coef)):])
            rshift = hclose[-int(50 * np.sqrt(coef))]
            rmin = nanmin_np(hclose[-int(50 * np.sqrt(coef)):])
        else:
            if len(hclose) > 0:
                rmax = nanmax_np(hclose)
                rshift = hclose[0]
                rmin = nanmin_np(hclose)
            else:
                rmax = np.nan
                rshift = np.nan
                rmin = np.nan

        self.rmax_list.append(rmax)
        self.rshift_list.append(rshift)
        self.rmin_list.append(rmin)

        if len(hclose[-300:]) < 150:
            return np.nan
        else:
            lth = len(hclose[-300:])
        dd = hclose[-lth:] - np.array(self.rmax_list[-lth:])
        #maxdd = rolling_min_adj(dd, np.sqrt(coef), win)
        temp = (hclose[-lth:] - np.array(self.rshift_list[-lth:])) / dd
        fac_rk = rank_data(temp[-lth:])
        #fac_rk = bk.rankdata(temp[-200:])/200
        fac1 = abs(fac_rk)-1
        
        roll_max = move_max_bk(hclose,window = 50,min_count=1)
        dd2 = hclose - roll_max
        temp2 = (hclose[50:] - hclose[:-50]) / dd2[50:]
        fac_rk2 = rank_data(temp2[-200:])
        #fac_rk2 = bk.rankdata(temp2[-200:])/200
        fac2 = abs(fac_rk2)-1
        factor = (fac1 + fac2) / 2       
        return factor

    def pre_calculate(self,data):
        self.rmax_list = []
        self.rmin_list = []        
        self.rshift_list = []
        # calc roll_max_adj
        for i in range(300, -1, -1):
            if i == 0:
                cls = data['close'][-31:]
                bidaskmean = data['BidAskSpreadMean'][-31:]
                hclose = data['twap'][-300:]
            else:
                cls = data['close'][-(31+i):-i]
                bidaskmean = data['BidAskSpreadMean'][-(31+i):-i]
                hclose = data['twap'][-(300+i):-i]
            cls_diff = cls[1:] - cls[:-1]
            cls_diff_std = nanstd_np(cls_diff[-30:],ddof = 1)
            bidaskmean_m = nanmean_np(bidaskmean[-30:])
            if abs(bidaskmean_m) < 1e-9:
                bidaskmean_m = np.nan
            coef_temp = cls_diff_std / bidaskmean_m
            if coef_temp > 10:
                coef = 0.1
            elif coef_temp > 6:
                coef = 0.3
            elif coef_temp > 4:
                coef = 1
            elif coef_temp > 3:
                coef = 2
            else:
                coef = 5
            if len(hclose) >= int(50 * np.sqrt(coef)):
   
                rmax = nanmax_np(hclose[-int(50 * np.sqrt(coef)):])
                rshift = hclose[-int(50 * np.sqrt(coef))]
                rmin = nanmin_np(hclose[-int(50 * np.sqrt(coef)):])
            else:
                if len(hclose) > 0:
                    rmax = nanmax_np(hclose)
                    rshift = hclose[0]
                    rmin = nanmin_np(hclose)
                else:
                    rmax = np.nan
                    rshift = np.nan
                    rmin = np.nan
                
            self.rmax_list.append(rmax)
            self.rshift_list.append(rshift)
            self.rmin_list.append(rmin)        

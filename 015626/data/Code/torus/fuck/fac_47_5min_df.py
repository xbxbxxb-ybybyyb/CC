from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np
import numpy as np
from numba import njit
from utils_zsj import SMA



class fac_47_5min_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(3 * int(self.freq))
        self.required_columns = [ 'close', 'volume', 'high', 'low', 'close_secmain', 'volume_secmain', 'high_secmain', 'low_secmain', 'BidAskSpreadMean']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 3000
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__

        self.index_close_list = []
        self.log_ret_weight_list = []
        self.log_ret_list = []
        self.factor_raw_list = []

    
    def calculate(self, data):
        aaa = 3
        bbb = 10
        ccc = 70
        ddd = 10
        hclose = data['close'][-31:]
        ba = data['BidAskSpreadMean'][-30:]
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
            
        norm_price1 = (data['close'][-2:] + data['high'][-2:] + data['low'][-2:]) / 3 
        norm_price2 = (data['close_secmain'][-2:] + data['high_secmain'][-2:] + data['low_secmain'][-2:]) / 3
        
        index_close1 = nanmean_np(norm_price1)
        index_close2 = nanmean_np(norm_price2)
        self.index_close_list.append([index_close1, index_close2])

        index_volume = nanmean_np(nansum_np([data['volume'][-2:], data['volume_secmain'][-2:]], axis = 1 ))
        
        log_ret = nanmean_np([self.index_close_list[-1][0] - self.index_close_list[-2][0], self.index_close_list[-1][1] - self.index_close_list[-2][1]])
        if np.isnan(log_ret):
            log_ret = self.log_ret_list[-1]
        self.log_ret_list.append(log_ret)
        ret_std = nanstd_np(self.log_ret_list[-aaa:], ddof = 1)
        log_ret_weight = log_ret / r(index_volume) * ret_std
        if np.isnan(log_ret_weight):
            log_ret_weight = self.log_ret_weight_list[-1]   
        self.log_ret_weight_list.append(log_ret_weight)
        factor_raw = irr_filter_raw(self.log_ret_weight_list[-bbb * 5:], bbb)[-1]
        if np.isnan(factor_raw):
            factor_raw = self.factor_raw_list[-1]
        self.factor_raw_list.append(factor_raw)
        #irr_filter_raw(np.array(self.factor_raw_list)[-ccc* 6:][-int(np.sqrt(coef) * ccc):], int(np.sqrt(coef) * ccc))[-1]
        factor_mean = irr_filter4(np.array(self.factor_raw_list), (np.sqrt(coef)), ccc) +  ema_1(self.factor_raw_list[-ccc*3:], ccc*3, 1/(ccc+1))

        return factor_mean


    
    def pre_calculate(self, data):
        aaa = 3
        bbb = 10
        ccc = 70
        ddd = 10
        

        
        for i in range(450, -1, -1):
            if i == 0:
                norm_price1 = (data['close'][-2:] + data['high'][-2:] + data['low'][-2:]) / 3 
                norm_price2 = (data['close_secmain'][-2:] + data['high_secmain'][-2:] + data['low_secmain'][-2:]) / 3
                index_volume = nanmean_np(nansum_np([data['volume'][-2:], data['volume_secmain'][-2:]], axis = 1))

            else:
                norm_price1 = (data['close'][-2 - i: -i] + data['high'][-2 - i: -i] + data['low'][-2 - i: -i]) / 3 
                norm_price2 = (data['close_secmain'][-2 - i: -i] + data['high_secmain'][-2 - i: -i] + data['low_secmain'][-2 - i: -i]) / 3
                index_volume = nanmean_np(nansum_np([data['volume'][-2 - i: -i], data['volume_secmain'][-2 - i: -i]], axis = 1))


            index_close1 = nanmean_np(norm_price1)
            index_close2 = nanmean_np(norm_price2)
            self.index_close_list.append([index_close1, index_close2])
            if len(self.index_close_list) > 1:
                log_ret = nanmean_np([self.index_close_list[-1][0] - self.index_close_list[-2][0], self.index_close_list[-1][1] - self.index_close_list[-2][1]])
                if np.isnan(log_ret):
                    try:
                        log_ret = self.log_ret_list[-1]
                    except:
                        pass
                self.log_ret_list.append(log_ret)
                ret_std = nanstd_np(self.log_ret_list[-aaa:], ddof = 1)
                log_ret_weight = log_ret / r(index_volume) * ret_std
                if np.isnan(log_ret_weight):
                    try:
                        log_ret_weight = self.log_ret_weight_list[-1]
                    except:
                        pass
                self.log_ret_weight_list.append(log_ret_weight)
                factor_raw = irr_filter_raw(self.log_ret_weight_list[-bbb * 5:], bbb)[-1]
                if np.isnan(factor_raw):
                    try:
                        factor_raw_list = self.factor_raw_list[-1]
                    except:
                        pass
                        
                self.factor_raw_list.append(factor_raw)


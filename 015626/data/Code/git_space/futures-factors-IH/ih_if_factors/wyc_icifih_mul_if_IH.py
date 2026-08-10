from future_factor import FutureFactor
import numpy as np
import bottleneck as bk

class wyc_icifih_mul_if_IH(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close'],'000300.SH':['close'],'000016.SH':['close']} 
    normalize_size = 5 * 242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = None 
    
    def calculate(self, df):
        factor = (df['close_000905.SH'] - 2 * df['close_000016.SH'] + df['close_000300.SH']).values[-200:]
        factor = factor[-1] - np.nanmean(factor)
        return factor


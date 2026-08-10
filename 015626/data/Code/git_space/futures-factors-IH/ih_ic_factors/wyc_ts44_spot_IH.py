from future_factor import FutureFactor
import numpy as np
import bottleneck as bk

# rolling norm前有fillna
class wyc_ts44_spot_IH(FutureFactor):
    data_type = 'Future' 
#     instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['close','volume']} 
    normalize_size = 5 * 242 
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 

    def calculate(self, df):
        
        v = df['volume_000016.SH'][-40:]
        temp1 = v
        c = df['close_000016.SH'][-40:]
        con2 = c < c.shift(1)
        temp1[con2] = -1 * temp1
        
        factor = bk.move_sum(temp1.values, window=20, min_count=int(20 / 2), axis=0)[-20:]
        factor = np.nanmean(factor)

        return factor

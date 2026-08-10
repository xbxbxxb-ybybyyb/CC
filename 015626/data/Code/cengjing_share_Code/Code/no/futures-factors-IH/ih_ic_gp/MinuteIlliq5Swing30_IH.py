import numpy as np
import bottleneck as bn
from future_factor import FutureFactor

class MinuteIlliq5Swing30_IH(FutureFactor):
    '''
    Description: max(abs(pct_chg(Index_ClosePx, 5)) / sum(Index_Volume, 5), 30) - min(abs(pct_chg(Index_ClosePx, 5)) / sum(Index_Volume, 5), 30)
    Class: Liquidity
    Author: liuz, modified by jinpx
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['close', 'volume']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        
        index_close = data['close_000016.SH'].values
        index_volume = data['volume_000016.SH'].values
        
        index_r_5 = (index_close[5:] - index_close[:-5]) / index_close[:-5]
        index_volume_sum_5 = bn.move_sum(index_volume, 5)
        
        N = 30
        illiquidity = np.abs(index_r_5[-N:]) / index_volume_sum_5[-N:]
        f = np.max(illiquidity) - np.min(illiquidity)
        
        return f
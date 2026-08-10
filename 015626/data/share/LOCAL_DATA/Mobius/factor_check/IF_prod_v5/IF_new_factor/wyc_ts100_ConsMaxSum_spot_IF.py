from future_factor import FutureFactor
import numpy as np

class wyc_ts100_ConsMaxSum_spot_IF(FutureFactor):
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close','amount']}
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        N = 30        
        index_close = data['close_000300.SH'][-N:].values
        index_amount = data['amount_000300.SH'][(1-N):].values
        
        narray = index_close[1:] / index_close[:-1] - 1
        
        maxsum,maxhere = narray[0],narray[0]
        AllMaxStart, AllMaxEnd, MaxStart, MaxEnd = 0,0,0,0
        
        for i in range(1, len(narray)):
            if maxhere <= 0:
                maxhere = narray[i]
                MaxStart = i
            else:
                maxhere += narray[i]
                MaxEnd = i
            if maxhere > maxsum:
                maxsum = maxhere
                AllMaxStart = MaxStart
                AllMaxEnd = MaxEnd

        maxamount = np.nansum(index_amount[AllMaxStart:AllMaxEnd+1])
        
        return maxamount

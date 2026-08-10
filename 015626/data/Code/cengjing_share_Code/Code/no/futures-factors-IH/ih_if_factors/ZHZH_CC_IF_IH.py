import bottleneck as bk
from future_factor import FutureFactor


class ZHZH_CC_IF_IH(FutureFactor):

    data_type = 'Future' 
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IH':['high']}
    normalize_size = 1200
    normalize_type = 'ts_rank' 

    
    def calculate(self, data):
        future_high = data['high_cont_IH'].values[-130:]
       
        temp = future_high >= bk.move_max(future_high, 10, 5)
        temp = bk.move_mean(temp, 120, 5)
        return temp[-1]
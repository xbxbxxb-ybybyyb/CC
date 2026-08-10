from future_factor import FutureFactor


class OFIR_if(FutureFactor):

    data_type = 'Future'  # 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Continuous_Data'] = {'IF':['OrderFlowImbalanceRatioLv1']} 
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None    

    def calculate(self, data):
        factor = data['OrderFlowImbalanceRatioLv1_cont_IF'].values[-1]

        return factor

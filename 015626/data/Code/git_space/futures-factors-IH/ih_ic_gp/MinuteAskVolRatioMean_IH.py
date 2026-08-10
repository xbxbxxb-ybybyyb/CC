from future_factor import FutureFactor
import numpy as np


class MinuteAskVolRatioMean_IH(FutureFactor):
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 7
    data_dict = {}
    data_dict['Continuous_Data'] = {'IH': ['AskVol']}
    normalize_size = 1 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 30
        ask = (data['AskVol_cont_IH']).values[-6 * 240:].reshape(-1, 240)
        ask_ratio = (ask[-1] / np.nanmean(ask[:-1], axis=0))[-lb:]
        f = np.nanmean(ask_ratio)
        return f

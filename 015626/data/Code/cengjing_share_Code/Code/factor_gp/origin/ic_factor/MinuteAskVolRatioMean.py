from future_factor import FutureFactor
import numpy as np


class MinuteAskVolRatioMean(FutureFactor):
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 6
    data_dict = {}
    data_dict['Future_Data'] = ['AskVol']
    normalize_size = 1 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 30
        ask = (data['AskVol']).values[-self.days_past * 240:].reshape(-1, 240)
        ask_ratio = (ask[-1] / np.nanmean(ask[:-1], axis=0))[-lb:]
        f = np.nanmean(ask_ratio)
        return f

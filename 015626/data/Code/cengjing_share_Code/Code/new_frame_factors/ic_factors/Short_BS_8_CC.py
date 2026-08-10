import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from future_factor import FutureFactor


def r(data, x=np.nan):

    data[abs(data) < 1e-8] = x
    return data

    
class Short_BS_8_CC(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeNum', 'SellUniqueOrderNum', 'SellTradeNum']
    normalize_size = 1800 
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        stk_BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-70:]
        stk_BuyTradeNum = data['BuyTradeNum'].values[-70:]
        stk_SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-70:]
        stk_SellTradeNum = data['SellTradeNum'].values[-70:]
        
        a = stk_BuyUniqueOrderNum / r(stk_BuyTradeNum)
        b = stk_SellUniqueOrderNum / r(stk_SellTradeNum)
        temp1 = (bk.move_max(a, 60, 15, axis=0) - a) / (bk.move_max(a, 60, 15, axis=0) - bk.move_min(a, 60, 15, axis=0))
        temp2 = (a - bk.move_min(a, 60, 15, axis=0)) / (bk.move_max(a, 60, 15, axis=0) - bk.move_min(a, 60, 15, axis=0))
        temp3 = (bk.move_max(b, 60, 15, axis=0) - b) / (bk.move_max(b, 60, 15, axis=0) - bk.move_min(b, 60, 15, axis=0))
        temp4 = (b - bk.move_min(b, 60, 15, axis=0)) / (bk.move_max(b, 60, 15, axis=0) - bk.move_min(b, 60, 15, axis=0))
        factor = temp2 - temp1 + temp3 - temp4
        factor = np.nanmean(factor, axis=1)
        factor = -bk.move_mean(factor, 10, 5)
        return factor[-1]
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from future_factor import FutureFactor


def r(data, x=np.nan):

    data[abs(data) < 1e-8] = x
    return data

    
class Short_BS_Main_CFG_CC(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['amount', 'weight', 'BuyUniqueOrderNum', 'BuyTradeNum', 'SellUniqueOrderNum', 'SellTradeNum']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-13:]
        stk_weight = data['weight'].values[-13:]
        stk_BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-13:]
        stk_BuyTradeNum = data['BuyTradeNum'].values[-13:]
        stk_SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-13:]
        stk_SellTradeNum = data['SellTradeNum'].values[-13:]

        df_s = bk.move_sum(stk_amount, 10, 5, axis=0)
        df_s[stk_weight<=0] = np.nan
        amount_mask = np.nanquantile(df_s, 0.9, axis=1)
        amount_mask = np.expand_dims(amount_mask, axis=-1)
        factor_raw = (stk_BuyUniqueOrderNum / r(stk_BuyTradeNum)) - (stk_SellUniqueOrderNum / r(stk_SellTradeNum))
        factor_raw_after_mask = ma.array(factor_raw, mask=(df_s<=amount_mask))
        factor_raw_after_mask = np.nanmean(factor_raw_after_mask, axis=1)
        factor_mean = -bk.move_mean(factor_raw_after_mask, 3, 1)
        return factor_mean[-1]
import numpy as np
from future_factor import FutureFactor

class MinuteIndexSellMoneyPerUniqueOrderGrowth(FutureFactor):
    '''
    Description: -1 * sum(mean(sell_growth, 240) / std(sell_growth, 240), w = index_weight) when num(sell_growth == 0) < 3 for index stock,
                where sell_growth = pct_chg(sell_money_30 / sell_order_30), sell_money_30 = pct_chg(cumsum(SellTradeMoney,240),30), sell_order_30 = pct_chg(cumsum(SellUniqueOrderNum,240),30)
    Class: Buy_Sell
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight','SellTradeMoney', 'SellUniqueOrderNum']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 240
        weight = data['weight'].values
        sell_money = data['SellTradeMoney'].values
        sell_order = data['SellUniqueOrderNum'].values
        
        sell_money_temp = np.nancumsum(sell_money[-lb:], axis=0)
        sell_money_30 = sell_money_temp[::-30][::-1]
        sell_money_30 = sell_money_30[1:] - sell_money_30[:-1]

        sell_order_temp = np.nancumsum(sell_order[-lb:], axis=0)
        sell_order_30 = sell_order_temp[::-30][::-1]
        sell_order_30 = sell_order_30[1:] - sell_order_30[:-1]

        sell_per_order = sell_money_30 / sell_order_30
        sell_growth = sell_per_order[1:] / sell_per_order[:-1] - 1

        sell_growth[sell_growth == 0] = np.nan
        nan_num = np.isnan(sell_growth).sum(axis=0)
        sell_growth = sell_growth[:, nan_num < 3]
        mean = np.nanmean(sell_growth, axis=0)
        std = np.nanstd(sell_growth, axis=0)
        std[std == 0] = np.nan

        f = -np.nansum(mean / std * weight[-1][nan_num < 3])
        
        if np.isnan(f) or np.isinf(f):
            return 0
        else:
            return f
import pandas as pd
import math
import numpy as np

def get_deal_ratio(minute_trade_detail_path, max_wait_tick_num = 4):
    tick_state_list = pd.read_csv(minute_trade_detail_path)['tick_state'].to_list()
    deal_num = 0
    order_num = 0
    for tick_state in tick_state_list:
        tick_state = eval(tick_state)
        deal_num += np.sum(tick_state)
        order_num += math.ceil(len(tick_state) / max_wait_tick_num)
    return deal_num / order_num

get_deal_ratio('/data/group/800466/warehouse/prod/tradingstats/Mobius/backtest/20230526_ic_ic_v7unifac/sig_ic_unifac_norm2/sig_ic_unifac_norm2_minute_trade_detail.csv')
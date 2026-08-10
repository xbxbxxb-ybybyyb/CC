import numpy as np
import pandas as pd

def order_planner_xdy(auction_amount, stock_price, tick_deal_ratio=0.2, 
                  target_amount=2.5E6, order_freq=100, min_order_size=100):
    # action_amount: 09:25 total amount in RMB
    # stock_price: auction end stock price
    # tick_deal_ratio: deal ratio per tick
    # target_amount: order amount per stock in RMB
    # order_freq: gap between split orders in ms
    # min_order_size: stock exchange minimum vol size per stock
    # return: list of order volumns as in [500, 300, 100, 100, 100, ...]
    # the sum of return list <= (target_amount / stock_price)
    # each element in return list rounded by min_order_size
    TICK_AUCTION_RATIO = {1: 0.5617,
                          2: 0.2053,
                          3: 0.1326,
                          4: 0.1178,
                          5: 0.0986,
                          6: 0.0778,
                          7: 0.0725,
                          8: 0.0729,
                          9: 0.0762,
                          10: 0.0772,
                          11: 0.078,
                          12: 0.0734,
                          13: 0.0719,
                          14: 0.0683,
                          15: 0.0634,
                          16: 0.0594,
                          17: 0.0598,
                          18: 0.0579,
                          19: 0.0575,
                          20: 0.0614}
    target_vol = target_amount // (stock_price * min_order_size)
    if target_vol == 0:
        return []
    order_num_per_tick = int(np.floor(3 * 1000 / order_freq))
    residual_vol = 0
    delt_vol = 0
    order_list = []
    for key in sorted(TICK_AUCTION_RATIO.keys()):
        amt_tick = auction_amount * TICK_AUCTION_RATIO[key] * tick_deal_ratio
        vol_per_order = amt_tick / order_num_per_tick / (stock_price * min_order_size)
        vol_per_order_list = [vol_per_order // 1] * order_num_per_tick
        residual_vol += vol_per_order * order_num_per_tick - sum(vol_per_order_list)
        if residual_vol > 1:
            residual_num = residual_vol // 1
            residual_vol = residual_vol % 1
            vol_per_order_list = [item + 1 if idx < residual_num else item \
                                           for idx, item in enumerate(vol_per_order_list)]
        for v in vol_per_order_list:
            if v > 0:
                deal_v = min(v, target_vol - delt_vol)
                order_list.append(int(deal_v * min_order_size))
                delt_vol += deal_v
                if delt_vol == target_vol:
                    return order_list
    if np.sum(order_list) / min_order_size > target_vol:
        raise AssertionError('Abnormal Deal Volume')
        return []
    return order_list
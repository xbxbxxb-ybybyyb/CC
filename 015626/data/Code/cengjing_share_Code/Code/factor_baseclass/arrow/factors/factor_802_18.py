from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime, math
import numpy as np
import bottleneck as bk
import pandas as pd
# 集合竞价order因子
class factor_802_18(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['tick', 'order']
        super(factor_802_18, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            tick = df['tick'][stk]
            order = df['order'][stk]

            order['OrderMoney'] = order.OrderPrice * order.OrderQty

            order1 = order[order['dt'].dt.time >= datetime.time(9, 24)]
            order2 = order[order['dt'].dt.time >= datetime.time(9, 20)]
            tick1 = tick[tick['dt'].dt.time >= datetime.time(9, 24)]
            if len(tick1) == 0 or len(order1) == 0 or len(order2) == 0:
                continue

            open_price = tick.iloc[-1]['LastPx']
            fac_order1_amount = order1.OrderMoney.sum()
            fac_order1_amount_ratio = fac_order1_amount / order2.OrderMoney.sum()

            flist = [fac_order1_amount, fac_order1_amount_ratio]

            for k in [1, 2]:
                order1_buy = order1[order1.OrderBSFlag == k]
                fac_order1_buy_amount = order1_buy.OrderMoney.sum()
                fac_order1_buy_amount_ratio = fac_order1_buy_amount / fac_order1_amount

                order1_buy_big = order1[order1.OrderMoney > 100000]
                fac_order1_buy_big_amount = order1_buy_big.OrderMoney.sum()
                fac_order1_buy_big_amount_ratio = fac_order1_buy_big_amount / fac_order1_amount

                order1_buy_radical = order1_buy[order1_buy.OrderPrice >= open_price]
                if k == 2:
                    order1_buy_radical = order1_buy[order1_buy.OrderPrice <= open_price]
                fac_order1_buy_radical_amount = order1_buy_radical.OrderMoney.sum()
                fac_order1_buy_radical_amount_ratio = fac_order1_buy_radical_amount / fac_order1_amount

                order1_buy_big_radical = order1_buy_radical[order1_buy_radical.OrderMoney > 100000]
                fac_order1_buy_big_radical_amount = order1_buy_big_radical.OrderMoney.sum()
                fac_order1_buy_big_radical_amount_ratio = fac_order1_buy_big_radical_amount / fac_order1_amount
                flist += [fac_order1_buy_amount, fac_order1_buy_amount_ratio, fac_order1_buy_big_amount, fac_order1_buy_big_amount_ratio, 
                          fac_order1_buy_radical_amount, fac_order1_buy_radical_amount_ratio, fac_order1_buy_big_radical_amount, fac_order1_buy_big_radical_amount_ratio]
            factor[stk] = flist         

        factor = pd.DataFrame(factor, index = [f'factor_802_{i}' for i in range(18)]).T

        return factor
# coding: utf-8
# Author：fengchi863
# Date ：2020/7/15 8:31

'''
此文件用于调试模拟撮合函数，待全部完成后，可以转移至测试基类中
20211230更新：更新了数据源的读取方式
'''

import datetime as dt
import time
import h5py

import numpy as np
import pandas as pd

from dataApi.tradeDate import trans_datetime2int
from dataApi.stockList import trans_int2windcode


class OrderMatchSystem:
    def __init__(self):
        pass

    @staticmethod
    def get_tick_data(code, date, address='/arch1/group/800442/800319/H5LimitTickData2/'):

        date = str(trans_datetime2int(date))
        code = trans_int2windcode(code)
        tick_data = {}
        items = {
            'RawMDTime': 'TimeStamp',
            'Buy1Price': 'BidPrice1',
            'Buy2Price': 'BidPrice2',
            'Buy3Price': 'BidPrice3',
            'Buy4Price': 'BidPrice4',
            'Buy5Price': 'BidPrice5',
            'Buy6Price': 'BidPrice6',
            'Buy7Price': 'BidPrice7',
            'Buy8Price': 'BidPrice8',
            'Buy9Price': 'BidPrice9',
            'Buy10Price': 'BidPrice10',
            'Sell1Price': 'AskPrice1',
            'Sell2Price': 'AskPrice2',
            'Sell3Price': 'AskPrice3',
            'Sell4Price': 'AskPrice4',
            'Sell5Price': 'AskPrice5',
            'Sell6Price': 'AskPrice6',
            'Sell7Price': 'AskPrice7',
            'Sell8Price': 'AskPrice8',
            'Sell9Price': 'AskPrice9',
            'Sell10Price': 'AskPrice10',
            'Buy1OrderQty': 'BidVolume1',
            'Buy2OrderQty': 'BidVolume2',
            'Buy3OrderQty': 'BidVolume3',
            'Buy4OrderQty': 'BidVolume4',
            'Buy5OrderQty': 'BidVolume5',
            'Buy6OrderQty': 'BidVolume6',
            'Buy7OrderQty': 'BidVolume7',
            'Buy8OrderQty': 'BidVolume8',
            'Buy9OrderQty': 'BidVolume9',
            'Buy10OrderQty': 'BidVolume10',
            'Sell1OrderQty': 'AskVolume1',
            'Sell2OrderQty': 'AskVolume2',
            'Sell3OrderQty': 'AskVolume3',
            'Sell4OrderQty': 'AskVolume4',
            'Sell5OrderQty': 'AskVolume5',
            'Sell6OrderQty': 'AskVolume6',
            'Sell7OrderQty': 'AskVolume7',
            'Sell8OrderQty': 'AskVolume8',
            'Sell9OrderQty': 'AskVolume9',
            'Sell10OrderQty': 'AskVolume10',
        }
        for item in items:
            with h5py.File(f'{address}/{item}/{date}.h5') as hf:
                tick_data[items[item]] = hf[f'{code}'][:]
        return tick_data

    @staticmethod
    def get_transaction_data(code, date, address='/arch1/group/800442/800319/H5LimitTradeData2/'):
        date = str(trans_datetime2int(date))
        code = trans_int2windcode(code)
        trade_data = {}
        items = {
            'MDTime': 'TimeStamp',
            'TradePrice': 'Price',
            'TradeQty': 'Volume',
            'TradeType': 'TradeType',
        }
        for item in items:
            with h5py.File(f'{address}/{item}/{date}.h5') as hf:
                trade_data[items[item]] = hf[f'{code}'][:]
        return trade_data

    @staticmethod
    def generate_order_dict(stk_id, price, vol, trade_direction, date_time, withdraw_seconds=None):
        order = dict()
        order['stk_id'] = stk_id
        order['price'] = np.float32(price)
        order['volume'] = vol
        order['direction'] = trade_direction
        order['start_time'] = date_time
        if withdraw_seconds is None:
            order['withdraw_time'] = dt.timedelta(seconds=15000)
        else:
            order['withdraw_time'] = dt.timedelta(seconds=withdraw_seconds)
        return order

    def order_transaction(self, order: dict, tick_data=None, transaction_data=None):
        '''
        calculate the mean_price and volume that can be truly done by making matches between your order and tick_data/transaction_data
        :param order: A dict which should has following keys: stk_id(int), price(float/int), volume(int), direction(str, 'B' or 'S'), start_time(datetime.datetime), withdraw_time(datetime.timedelta)
        :param tick_data: tick data on the day which should matches the start_time of order
        :param transaction_data: transaction data on the day which should matches the start_time of order
        :return: deal_price, deal_volume

        Examples:
        order = dict()
        order['stk_id'] = 600519
        order['price'] = 779.2
        order['volume'] = 50000
        order['direction'] = 'B'
        order['start_time'] = dt.datetime(2018, 1, 10, 9, 50, 0)
        order['withdraw_time'] = dt.timedelta(seconds=59)
        deal_price, deal_volume = order_transaction(order, tick_data, transaction_data)
        print(deal_price, deal_volume)
        code:
        779.1250151057401 3310.0
        '''

        pd.set_option('mode.chained_assignment', None)  # 关闭真香警告
        stk_id = order['stk_id']
        start_time = order['start_time']
        date = start_time.date()
        order_time = (start_time.hour * 10000 + start_time.minute * 100 + start_time.second) * 1000
        vol_left = order['volume']
        withdraw_time = start_time + order['withdraw_time']

        withdraw_time = (withdraw_time.hour * 10000 + withdraw_time.minute * 100 + withdraw_time.second) * 1000
        if order_time <= 11300000 and withdraw_time > 113000000:
            withdraw_time += 17000000
        if withdraw_time > 150000000:
            withdraw_time = 150000000

        if tick_data is None:
            tick_data = self.get_tick_data(stk_id, int(date.strftime('%Y%m%d')))
        if transaction_data is None:
            transaction_data = self.get_transaction_data(stk_id, int(date.strftime('%Y%m%d')))

        if len(tick_data) == 0:
            raise ValueError('tick_data is empty!')
        if len(transaction_data) == 0:
            raise ValueError('trans_data is empty!')

        ii_tick = 0  # tick数据计数器
        ii_trans = 0  # transaction数据计数器

        adsorbed_start_time = tick_data['TimeStamp'][ii_tick] * 1000
        # 定位到目标盘口处
        for i in range(ii_tick, len(tick_data["TimeStamp"])):
            if tick_data["TimeStamp"][i] * 1000 >= order_time:
                ii_tick = i
                adsorbed_start_time = tick_data['TimeStamp'][i] * 1000  # 吸附在最近的tick盘口上
                break
        for j in range(ii_trans, len(transaction_data["TimeStamp"])):
            if transaction_data['TimeStamp'][j] > adsorbed_start_time:
                ii_trans = j
                break

        # 盘口整理成list格式
        ask_price_list = [tick_data["AskPrice1"][ii_tick], tick_data["AskPrice2"][ii_tick],
                          tick_data["AskPrice3"][ii_tick], tick_data["AskPrice4"][ii_tick],
                          tick_data["AskPrice5"][ii_tick], tick_data["AskPrice6"][ii_tick],
                          tick_data["AskPrice7"][ii_tick], tick_data["AskPrice8"][ii_tick],
                          tick_data["AskPrice9"][ii_tick], tick_data["AskPrice10"][ii_tick]]
        ask_price_list = list(map(lambda x: round(x, 2), ask_price_list))
        ask_volume_list = [tick_data["AskVolume1"][ii_tick], tick_data["AskVolume2"][ii_tick],
                           tick_data["AskVolume3"][ii_tick], tick_data["AskVolume4"][ii_tick],
                           tick_data["AskVolume5"][ii_tick], tick_data["AskVolume6"][ii_tick],
                           tick_data["AskVolume7"][ii_tick], tick_data["AskVolume8"][ii_tick],
                           tick_data["AskVolume9"][ii_tick], tick_data["AskVolume10"][ii_tick]]
        bid_price_list = [tick_data["BidPrice1"][ii_tick], tick_data["BidPrice2"][ii_tick],
                          tick_data["BidPrice3"][ii_tick], tick_data["BidPrice4"][ii_tick],
                          tick_data["BidPrice5"][ii_tick], tick_data["BidPrice6"][ii_tick],
                          tick_data["BidPrice7"][ii_tick], tick_data["BidPrice8"][ii_tick],
                          tick_data["BidPrice9"][ii_tick], tick_data["BidPrice10"][ii_tick]]
        bid_price_list = list(map(lambda x: round(x, 2), bid_price_list))
        bid_volume_list = [tick_data["BidVolume1"][ii_tick], tick_data["BidVolume2"][ii_tick],
                           tick_data["BidVolume3"][ii_tick], tick_data["BidVolume4"][ii_tick],
                           tick_data["BidVolume5"][ii_tick], tick_data["BidVolume6"][ii_tick],
                           tick_data["BidVolume7"][ii_tick], tick_data["BidVolume8"][ii_tick],
                           tick_data["BidVolume9"][ii_tick], tick_data["BidVolume10"][ii_tick]]

        # 记录委托的成交情况
        transaction_list = []
        deal_price = 0
        deal_volume = 0
        deal_amount = 0

        # 买入情形
        if order['direction'] is 'B':
            # 先成交盘口上的对手价
            for k in range(len(ask_price_list)):
                if order['price'] >= ask_price_list[k] and vol_left <= ask_volume_list[k]:
                    transaction_list.append([ask_price_list[k], vol_left])
                    vol_left = 0
                    break
                elif order['price'] >= ask_price_list[k] and vol_left > ask_volume_list[k]:
                    transaction_list.append([ask_price_list[k], ask_volume_list[k]])
                    vol_left -= ask_volume_list[k]
                else:
                    break

            # 若仍有未成交的单子
            if vol_left > 0:
                order_queue = []
                for k in range(len(bid_price_list)):
                    if bid_price_list[k] >= order['price']:
                        order_queue.append([bid_price_list[k], bid_volume_list[k]])
                    else:
                        break
                for j in range(ii_trans, len(transaction_data['TimeStamp'])):
                    # 处理委托挂单之前市场上其他人的挂单，关注撤单
                    if transaction_data['TimeStamp'][j] <= withdraw_time:
                        while len(order_queue) > 0:
                            if transaction_data['TradeType'][j] != 0:
                                if transaction_data['Price'][j] in list(np.array(order_queue, dtype='object')[:, 0]):
                                    idx = order_queue[0].index(transaction_data['Price'][j])
                                    if transaction_data['Volume'][j] >= order_queue[idx][1]:
                                        order_queue.pop(idx)
                                        break
                                    else:
                                        order_queue[idx][1] -= transaction_data['Volume'][j]
                                        break
                                else:
                                    break
                            else:
                                if transaction_data['Price'][j] <= order_queue[0][0] and transaction_data['Volume'][j] < \
                                        order_queue[0][1]:
                                    order_queue[0][1] -= transaction_data['Volume'][j]
                                    transaction_data['Volume'][j] = 0
                                    break
                                elif transaction_data['Price'][j] <= order_queue[0][0] and transaction_data['Volume'][j] >= \
                                        order_queue[0][1]:
                                    transaction_data['Volume'][j] -= order_queue[0][1]
                                    order_queue.pop(0)
                                else:
                                    break
                        if transaction_data['TradeType'][j] == 0 and len(order_queue) == 0:
                            # 开始成交我们自己的委托单
                            if 0 < transaction_data['Volume'][j] < vol_left and transaction_data['Price'][j] <= order['price']:
                                transaction_list.append([transaction_data['Price'][j], transaction_data['Volume'][j]])
                                vol_left -= transaction_data['Volume'][j]
                            elif transaction_data['Volume'][j] >= vol_left and transaction_data['Price'][j] <= order['price']:
                                transaction_list.append([transaction_data['Price'][j], vol_left])
                                break
                    else:
                        continue

        elif order['direction'] is 'S':
            for k in range(len(bid_price_list)):
                if order['price'] <= bid_price_list[k] and vol_left <= bid_volume_list[k]:
                    transaction_list.append([bid_price_list[k], vol_left])
                    vol_left = 0
                    break
                elif order['price'] <= bid_price_list[k] and vol_left > bid_volume_list[k]:
                    transaction_list.append([bid_price_list[k], bid_volume_list[k]])
                    vol_left -= bid_volume_list[k]
                else:
                    break

            if vol_left > 0:
                order_queue = []
                for k in range(len(ask_price_list)):
                    if ask_price_list[k] <= order['price']:
                        order_queue.append([ask_price_list[k], ask_volume_list[k]])
                    else:
                        break
                for j in range(ii_trans, len(transaction_data['TimeStamp'])):
                    if transaction_data['TimeStamp'][j] <= withdraw_time:
                        while len(order_queue) > 0:
                            if transaction_data['TradeType'][j] != 0:
                                if transaction_data['Price'][j] in list(np.array(order_queue, dtype='object')[:, 0]):
                                    idx = order_queue[0].index(transaction_data['Price'][j])
                                    if transaction_data['Volume'][j] >= order_queue[idx][1]:
                                        order_queue.pop(idx)
                                        break
                                    else:
                                        order_queue[idx][1] -= transaction_data['Volume'][j]
                                        break
                                else:
                                    break
                            else:
                                if transaction_data['Price'][j] >= order_queue[0][0] and transaction_data['Volume'][j] < \
                                        order_queue[0][1]:
                                    order_queue[0][1] -= transaction_data['Volume'][j]
                                    transaction_data['Volume'][j] = 0
                                    break
                                elif transaction_data['Price'][j] >= order_queue[0][0] and transaction_data['Volume'][j] >= \
                                        order_queue[0][1]:
                                    transaction_data['Volume'][j] -= order_queue[0][1]
                                    order_queue.pop(0)
                                else:
                                    break
                        if transaction_data['TradeType'][j] == 0 and len(order_queue) == 0:
                            if 0 < transaction_data['Volume'][j] < vol_left and transaction_data['Price'][j] >= order['price']:
                                transaction_list.append([transaction_data['Price'][j], transaction_data['Volume'][j]])
                                vol_left -= transaction_data['Volume'][j]
                            elif transaction_data['Volume'][j] >= vol_left and transaction_data['Price'][j] >= order['price']:
                                transaction_list.append([transaction_data['Price'][j], vol_left])
                                break
                    else:
                        continue

        for transaction in transaction_list:
            deal_volume += transaction[1]
            deal_amount += transaction[0] * transaction[1]
        if deal_volume > 0:
            deal_price = deal_amount / deal_volume
        else:
            return np.nan, np.nan

        return round(deal_price, 2), deal_volume


if __name__ == '__main__':
    oms = OrderMatchSystem()
    # 对比两种情况
    # order = generate_order_dict(2717, 24.1, 600, 'S', dt.datetime(2018, 1, 22, 11, 25, 0))
    order = oms.generate_order_dict(32, 19.69, 100000, 'B', dt.datetime(2021, 1, 4, 13, 41, 4))
    # tick_data = oms.get_tick_data(order['stk_id'], int(order['start_time'].strftime('%Y%m%d')))
    # transaction_data = oms.get_transaction_data(order['stk_id'], int(order['start_time'].strftime('%Y%m%d')))
    e1 = time.time()
    deal_price, deal_volume = oms.order_transaction(order)
    print(deal_price, deal_volume)
    print(time.time() - e1)

    # e1 = time.time()
    # # 创建一个订单
    # order1 = Order(stock_code=trans_int2windcode(order['stk_id']), order_time=order['start_time'],
    #                order_price=order['price'],
    #                order_volume=order['volume'], bs_flag=order['direction'])
    # # 实例化一个ExchangeHouse，撮合模式为TICK
    # exchange_house1 = ExchangeHouse(mode='TICK')
    # # 模拟下单
    # order_number1 = exchange_house1.send(orders=order1)
    # # 模拟挂单
    # exchange_house1.drive(order_number=order_number1, hold_time=59)
    # # 模拟撤单
    # exchange_house1.back(order_number=order_number1, back_date_time=59)
    # # 获取交易订单的成交信息
    # print(order1.get_record())
    # print(time.time() - e1)

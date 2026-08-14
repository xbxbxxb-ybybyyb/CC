import Position
import pandas as pd
from dataApi.getData import *
root_path = '/data/group/800319/junkData/'
import copy
import time
import numpy as np
class Record:
    """
    用于记录某一次回测过程中的：
    持仓信息
    报单信息
    成交信息
    持仓过程中分红等情况

    """
    def __init__(self):
        self.holding = [] #每个bar结束时各个标的持仓数量
        self.frozen_holding = []
        self.tradable_holding = []
        self.position_values = []#每个bar结束时各个持仓标的市值
        self.order_info = []#(date_time,stk_id,stk_num,price,flag)下单信息
        self.deal_info = []#(date_time,stk_id,stk_num,price,flag)#成交信息
        self.adj_info = []#('XXXX0930',stk_id,detail) 拆股、分红、付息等事件导致的股价变化记录
        self.cash = []
        ##############################
        self.holding_df = pd.DataFrame()
        self.frozen_holding_df = pd.DataFrame()
        self.tradable_holding_df = pd.DataFrame()
        self.cash_df = pd.DataFrame()
        self.account_info = pd.DataFrame()
        self.signal_records_evaluation = pd.DataFrame()
        # self.date_list = date_list
    def add_log_position_df(self,position:Position,date_time:int):
        """
        记录某一bar结束时的持仓状况
        :param position: 当前持仓情况
        :param date_time: 时间戳(分钟末)
        :return: None
        """
        temp_position_df = pd.DataFrame(position.holding,index = [date_time])
        temp_frozen_holding = pd.DataFrame(position.frozen_holding,index=[date_time])
        temp_tradable_holding = pd.DataFrame(position.tradable_holding, index=[date_time])
        if temp_position_df.shape[0]>0:
            self.holding.append(temp_position_df)
        if temp_frozen_holding.shape[0]>0:
            self.frozen_holding.append(temp_frozen_holding)
        if temp_tradable_holding.shape[0]>0:
            self.tradable_holding.append(temp_tradable_holding)
        self.cash.append([date_time,position.cash])
        pass
    def add_log_position(self,position:Position,date_time:int):
        """
        记录某一bar结束时的持仓状况
        :param position: 当前持仓情况
        :param date_time: 时间戳(分钟末)
        :return: None
        """
        if len(position.holding)>0:
            self.holding.append([date_time,copy.deepcopy(position.holding)])
            # print(date_time, len(self.holding[0][1]))
        if len(position.tradable_holding)>0:
            self.tradable_holding.append([date_time,copy.deepcopy(position.tradable_holding)])
        if len(position.frozen_holding)>0:
            self.frozen_holding.append([date_time,copy.deepcopy(position.frozen_holding)])
        self.cash.append([date_time,position.cash])

        pass
    def add_log_order_info(self,order_list,deal_info):
        """
        记录前一个bar结束(close)到当前bar结束(close)之间的下单和成交情况
        :param order_list:
        :param deal_info:
        :return:
        """
        if len(order_list)>0 or len(deal_info)>0:
            self.order_info.extend(order_list)
            self.deal_info.extend(deal_info)
        pass
    def get_net_value(self):
        """
        返回记录期间的账户
        :return:
        """
        return
    def processing(self,benchmark):
        e1 = time.time()
        self.holding_df = pd.DataFrame({x[0]:x[1] for x in self.holding}).T
        self.frozen_holding_df = pd.DataFrame({x[0]:x[1] for x in self.frozen_holding}).T
        self.tradable_holding_df = pd.DataFrame({x[0]:x[1] for x in self.tradable_holding}).T
        self.cash_df = pd.DataFrame(self.cash, columns=['datetime', 'cash']).set_index('datetime')
        print('df processing:',time.time()-e1)
        h5 = pd.HDFStore('%s/minuteByFactor/close.h5'%root_path)
        close = h5['/close']
        h5.close()
        print('read data',time.time()-e1)
        close.index = list(map(lambda x: x[0] * 10000 + x[1], close.index.tolist()))
        self.position_values = self.holding_df * close.loc[self.holding_df.index,self.holding_df.columns]
        self.account_info = pd.concat([self.position_values,self.cash_df],axis=1)
        self.net_value = pd.DataFrame(self.account_info.sum(axis=1))
        self.deal_info.sort()

        record_dict = {}
        temp_dict = {}
        temp_vol_dict = {}
        for deal_order in self.deal_info:
            date_time, stk_id, vol, _, flag = deal_order
            adj_price = close.loc[date_time,stk_id]
            if vol==0:
                continue
            if flag=='B':
                vol = -1 * vol
            cash_flow = vol * adj_price
            pitch = [date_time,cash_flow,benchmark[date_time]]
            if stk_id not in temp_dict:
                temp_dict[stk_id] = [pitch]
                temp_vol_dict[stk_id] = vol
            else:
                temp_dict[stk_id].append(pitch)
                temp_vol_dict[stk_id] += vol
            if temp_vol_dict[stk_id] == 0:
                if stk_id not in record_dict:
                    record_dict[stk_id] = [temp_dict.pop(stk_id)]
                else:
                    record_dict[stk_id].append(temp_dict.pop(stk_id))

        result = []
        for stk_id in record_dict:
            result.extend(list(map(lambda x : [stk_id] + get_one_pitch_result(x),record_dict[stk_id])))
        result = pd.DataFrame(result, columns=['stk_id', 'start', 'end', 'profit', 'excess profit'])
        self.signal_records_evaluation = result

def get_one_pitch_result(pitch):
    sell_amt_stock = np.array([x[1] if x[1] > 0 else 0 for x in pitch])
    sell_percent = sell_amt_stock / sell_amt_stock.sum()
    buy_vol_bench = np.array([-1. / x[-1] if x[1] < 0 else 0 for x in pitch])
    sell_vol_bench = abs(buy_vol_bench.sum()) * sell_percent
    bench_vol_list = buy_vol_bench + sell_vol_bench
    if bench_vol_list.sum() != 0:
        raise Exception('Benchmark not close position')
    stock_profit = sum([x[1] for x in pitch]) / sum([-x[1] if x[1] < 0 else 0 for x in pitch])
    bench_price = np.array([x[2] for x in pitch])
    bench_cash_flow = bench_price * bench_vol_list
    bench_profit = bench_cash_flow.sum() / sum([-x if x < 0 else 0 for x in bench_cash_flow])

    return [pitch[0][0], pitch[-1][0], stock_profit, stock_profit - bench_profit]
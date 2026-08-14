# @Time : 2021/5/2 9:55
# @Author : Zhichen Lu
# @File : Application930.py

import pandas as pd
from online_conf import realtime_path  # , local_config_path, sub_output_path
from ExtraTools import get_path_conf
import os, datetime, traceback
import time as tm
import numpy as np
from ExtraTools import get_path_conf

market_data_path = realtime_path + 'market_data/'
path_conf = get_path_conf('/data/group/800319/strategy_local_path3/')
local_config_path, sub_output_path = [path_conf[x] for x in ['local_config_path', 'sub_output_path']]
sub_local_config_path = f'{local_config_path}/FolderFor930/'


# sub_output_path = f'{daily_out_path}out_930/'


class Application930:

    def __init__(self, date, log=print):
        # date = 20201106
        # in_path = f'{sub_local_config_path}{date}/StrategyIn/'
        self.log = log
        out_path = f'{sub_local_config_path}{date}/StrategyOut/'
        strategy_config = pd.read_pickle(f'{sub_local_config_path}{date}/StrategyIn/init{date}.pkl')
        self.log(f'930:{strategy_config}')
        date, pre_date, barly_max_buy, stk_min_amt = map(int, [strategy_config[x] for x in
                                                               ['date', 'pre_date', 'barly_max_buy', 'stk_min_amt']])
        order_ratio = float(strategy_config['order_ratio'])
        per_amt = float(strategy_config['per_amt'])
        portfolio_id = eval(strategy_config['portfolio_id'])
        # 初始化输出路径
        if not os.path.exists(f'{out_path}/{str(date)}'):
            os.mkdir(f'{out_path}/{str(date)}')
        if not os.path.exists(f'{sub_local_config_path}{pre_date}/StrategyOut/holding{pre_date}.pkl'):
            raise Exception('No available holding info file')
        holding_info = pd.read_pickle(f'{sub_local_config_path}{pre_date}/StrategyOut/holding{pre_date}.pkl')
        # 加载持仓股票的买入时间信息
        if not os.path.exists(f'{sub_local_config_path}{pre_date}/StrategyOut/buy_time_info{pre_date}.pkl'):
            raise Exception('No available buy time info file')
        buy_time_info = pd.read_pickle(f'{sub_local_config_path}{pre_date}/StrategyOut/buy_time_info{pre_date}.pkl')

        vol_info = pd.read_pickle(f'{sub_local_config_path}{date}/StrategyIn/vol_info{date}.pkl')
        # 加载复权因子
        if portfolio_id is None:
            portfolio_id = -1
        unavailable_pool = pd.read_pickle(f'{local_config_path}restrict_list.pkl')

        signal = pd.read_pickle(f'{local_config_path}morning_model/val_sign/{date}.pkl')
        code_list = signal.index.tolist()
        close = pd.read_pickle(f'{market_data_path}{pre_date}/close.pkl')

        self.log = log
        self.portfolio_id = portfolio_id
        self.date = date
        self.pre_date = pre_date
        self.per_amt = per_amt
        self.barly_max_buy = barly_max_buy
        self.stk_min_amt = stk_min_amt
        self.order_ratio = order_ratio
        self.stk_list = sorted(list(set(code_list) - unavailable_pool))
        self.pre_close = close.iloc[-1]#.loc[str(pre_date)]

        self.buy_time_info = buy_time_info
        self.cash = holding_info.pop('cash')
        self.holding = holding_info
        self.available = holding_info.copy()
        self.pool_with_over_night_stk = sorted(list(set(self.stk_list).union(self.holding.keys())))
        self.vol_info = vol_info[self.pool_with_over_night_stk]
        self.pred_ret = signal
        self.signal = signal
        self.time = 930
        self.pre_time = None
        self.buy_order_record = {}
        self.sell_order_record = {}
        self.total_buy_amt = 0
        self.total_sell_amt = 0
        # 截止至某个bar,近半小时买、卖的成交额
        self.barly_buy_amt, self.barly_sell_amt = {}, {}
        self.holding_info = {}
        self.holding_change = {}

    def holding_another_round(self, stk):
        if stk not in self.buy_time_info or stk not in self.available or stk not in self.holding:
            self.log('Existing information of stock %s are not complete' % stk)
            return
        buy_date, buy_time = self.buy_time_info[stk][:2]
        if buy_date == self.pre_date and buy_time == self.time:
            self.buy_time_info[stk] = (self.date, self.time)

    def bar_handler(self, holding_info, signal=None):
        self.log(f'{self.time} bar_handler in')
        self.holding_info_update(holding_info)
        date = self.date
        bar_close = self.pre_close.reindex(self.pool_with_over_night_stk)
        available_instance = holding_info['Symbol'].tolist()
        # 剔除盘中涨跌停

        if signal is None:
            signal = self.signal
        trigger_stk = set(signal.keys())
        # 当日可卖出股票 = 持仓股票剔除 盘中涨跌停
        avaliable_stk = set(self.available.keys())  # - set(limit_status[limit_status.isin([1, -1])].index)
        avaliable_trigger_stk = avaliable_stk.intersection(trigger_stk)
        sell_stk = list(avaliable_stk - trigger_stk)
        # 截止当前持有超过240分钟的股票
        ######################
        # stk_hold_over_240 = set()
        # for stk in avaliable_stk:
        #     buy_date, buy_time = self.buy_time_info[stk][:2]
        #     if buy_date == self.pre_date and buy_time == self.time:
        #         stk_hold_over_240.add(stk)
        #
        # sell_stk = list(stk_hold_over_240 - trigger_stk)
        # avaliable_trigger_stk = set(stk_hold_over_240).intersection(trigger_stk)
        ##########################
        # 可买入股票 = 触发股票 剔除 不在股票池的股票 以及 有持仓个股
        trigger_stk = trigger_stk.intersection(set(self.stk_list))
        trigger_stk = trigger_stk - set(self.holding.keys())
        if trigger_stk - set(available_instance):
            self.log(f'Buy stock contain unavailable instance {trigger_stk - set(available_instance)}')
        trigger_stk = trigger_stk.intersection(set(available_instance))
        historical_future_vol = round(self.vol_info * self.order_ratio, -2)
        for stk in avaliable_trigger_stk:
            self.holding_another_round(stk)
        close = bar_close

        # if sell_stk:
        #     limit_down_judge = limit_status.eq(-1).loc[sell_stk]
        #     sell_stk = limit_down_judge[~limit_down_judge].index.tolist()

        sell_vol = {}
        if self.cash < self.per_amt:
            # 如果当前现金不足买入一支股票，仅卖出
            target_vol = pd.Series()
        elif trigger_stk:
            # 处理买入股票
            # limit_up_judge = limit_status.eq(1).loc[trigger_stk]  # pd.Series(limit_up_judge, index=trigger_stk)
            # trigger_stk = limit_up_judge[~limit_up_judge].index.tolist()
            target_close = close.loc[trigger_stk]
            target_vol = round(self.per_amt / target_close, -2)
            target_vol = pd.concat([target_vol, historical_future_vol[list(trigger_stk)]], axis=1).min(axis=1)
            target_vol = target_vol // 100 * 100
            target_amt = target_vol * target_close
            target_amt = target_amt.loc[signal[trigger_stk].sort_values(ascending=False).index.tolist()]
            target_amt = target_amt[target_amt >= self.stk_min_amt]
            target_amt = target_amt[target_amt.cumsum() < self.cash]
            trigger_stk = target_amt.index.tolist()
            trigger_num = min(len(trigger_stk), int(self.cash // self.per_amt), self.barly_max_buy)
            trigger_stk = trigger_stk[:trigger_num]
            target_vol, target_amt = target_vol[trigger_stk], target_amt[trigger_stk]
        else:
            target_vol = pd.Series()
        # self.holding.rename({x:int(x[:-3]) for x in self.holding.index}).to_frame().astype(int).reset_index().values.tolist()
        if set(sell_stk) - set(available_instance):
            self.log(f'Sell stock contain stock not in available instance pool {set(sell_stk) - set(available_instance)}')
        sell_stk = list(set(sell_stk).intersection(set(available_instance)))
        for stk in sell_stk:
            buy_date, buy_time = self.buy_time_info[stk]
            if buy_date < self.pre_date or (buy_date == self.pre_date and buy_time <= self.time):
                try:
                    sell_vol[stk] = min(historical_future_vol[stk] // 100 * 100, self.holding[stk])
                except:
                    print(1)
        sell_vol = pd.Series(sell_vol)
        self.sell_order_record[self.time] = sell_vol.copy()
        self.buy_order_record[self.time] = target_vol.copy()
        e = tm.time()
        sell_vol = self.get_formated_order(sell_vol, 'S')
        target_vol = self.get_formated_order(target_vol, 'B')
        self.log(f'Timetable generation time in {self.time}: {tm.time() - e}')
        order_content = sell_vol + target_vol
        if not os.path.exists(sub_output_path):
            os.mkdir(sub_output_path)
        if not os.path.exists(f'{sub_output_path}/{str(self.date)}/'):
            os.mkdir(f'{sub_output_path}/{str(self.date)}/')
        pd.to_pickle({
            'sell_vol': self.sell_order_record[self.time],
            'buy_vol': self.buy_order_record[self.time],
            'order_content': order_content
        }, f'{sub_output_path}/{str(self.date)}/order_info_930.pkl')
        self.barly_output()
        return order_content

    def get_formated_order(self, target_vol, flag):
        if flag == 'S':
            target_vol = -1 * target_vol
        elif flag == 'B':
            pass
        else:
            raise Exception('Wrong Flag')
        content = []
        for stk in target_vol.index:
            # if stk in self.intraDistr:
            #     distr = self.intraDistr[stk]
            # else:
            #     self.log(f'---------------------intrDistr of {stk} does not exist------------------------')
            #     distr = {str(self.time).zfill(4): np.arange(1, 4)}
            # timetable = generateTimetableAndTargetQtyIntervalEqully(distr, target_vol[stk], self.date, 20,
            #                                                   str(self.time).zfill(4))
            start_time = datetime.datetime(self.date // 10000, self.date % 10000 // 100, self.date % 100, self.time // 100, self.time % 100)
            end_time = start_time + datetime.timedelta(0, 1800)
            target_form = {"StartTime": start_time.strftime('%H:%M:%S'), "EndTime": end_time.strftime('%H:%M:%S'), "TargetQty": str(target_vol[stk])}
            item = {
                'portfolio': str(self.portfolio_id),
                'symbol': stk,
                'target': target_form
            }
            content.append(item)
        return content  # {'command': 'TARGET', 'content': content}

    def holding_info_update(self, holding):
        self.holding_info[self.time] = holding
        holding_df = holding.set_index('Symbol')
        holding_df['NetPosition'] = holding_df['NetPosition'].astype(float)
        holding_df = holding_df[holding_df['NetPosition'] > 0]

        unioin_stk_list = list(set(holding_df.index).union(set(self.holding.keys())))
        current_holding = holding_df['NetPosition'].reindex(unioin_stk_list).fillna(0)
        pre_holding = pd.Series(self.holding).reindex(unioin_stk_list).fillna(0)
        holding_change = current_holding - pre_holding
        for each in holding_change.index:
            if holding_change[each] > 0 and each not in self.buy_time_info:
                self.buy_time_info[each] = (self.date, self.pre_time)
            if holding_change[each] < 0 and current_holding[each] == 0 and each in self.buy_time_info:
                self.buy_time_info.pop(each)
        # 在T-1个bar执行导致T个bar完成的仓位变化
        if not os.path.exists(f'{sub_output_path}{self.date}/'):
            os.mkdir(f'{sub_output_path}{self.date}/')

        pd.to_pickle(holding_change, f'{sub_output_path}{self.date}/holding_change_{self.time}.pkl')
        self.holding = holding_df['NetPosition']
        if set(self.holding.keys()) != set(self.buy_time_info.keys()).intersection(set(self.holding.keys())):
            self.log('Holding keys and buy time info are not match')
            raise Exception('Holding keys and buy time info are not match')
        self.available = holding_df['SellAvailable'][holding_df['SellAvailable'] > 0]
        total_buy_amt, total_sell_amt = holding[['TotalBuyAmount', 'TotalSellAmount']].sum().tolist()
        self.barly_buy_amt[self.time], self.barly_sell_amt[
            self.time] = total_buy_amt - self.total_buy_amt, total_sell_amt - self.total_sell_amt
        self.total_buy_amt, self.total_sell_amt = total_buy_amt, total_sell_amt
        self.cash += self.barly_sell_amt[self.time] - self.barly_buy_amt[self.time]
        return True

    def output_daily_summary(self):
        buy_time_info = {}
        for each in self.buy_time_info:
            date, time = self.buy_time_info[each][:2]
            if each in self.holding or date == self.date:
                buy_time_info[each] = self.buy_time_info[each]
        # pd.to_pickle(buy_time_info,buy_time_info_path+'%d.pkl'%self.date)
        res = {
            'stk_list': self.stk_list,
            'stk_list_with_over_night': self.pool_with_over_night_stk,
            'barly_holding_info': self.holding_info,
            'barly_sell_amt': self.barly_sell_amt,
            'barly_buy_amt': self.barly_buy_amt,
            'sell_order_record': self.sell_order_record,
            'buy_order_record': self.buy_order_record,
            'pred_ret': self.pred_ret,
            'signal': self.signal,
            'buy_time_info': buy_time_info,
            'last_bar_initial_cash': self.cash,
        }
        pd.to_pickle(res, sub_output_path + '%d.pkl' % self.date)

    def barly_output(self):
        res = {
            'stk_list': self.stk_list,
            'stk_list_with_over_night': self.pool_with_over_night_stk,
            'barly_holding_info': self.holding_info[self.time],
            'barly_sell_amt': self.barly_sell_amt[self.time],
            'barly_buy_amt': self.barly_buy_amt[self.time],
            'sell_order_record': self.sell_order_record[self.time],
            'buy_order_record': self.buy_order_record[self.time],
            'pred_ret': self.pred_ret,
            'signal': self.signal,
            'buy_time_info': self.buy_time_info,
            'bar_inital_cash': self.cash,
        }
        if not os.path.exists(f'{sub_output_path}{self.date}/'):
            os.mkdir(f'{sub_output_path}{self.date}/')
        pd.to_pickle(res, f'{sub_output_path}{self.date}/{str(self.time)}_summary.pkl')

import matplotlib
matplotlib.use('Agg')

import pandas as pd
import numpy as np
import datetime
from multifactor.IO import IO
from tqdm import tqdm
import os
import matplotlib.pyplot as plt
import itertools
import multifactor.utility.dt as udt
import warnings
warnings.filterwarnings('ignore')


class TS_BACK_TEST:

    def __init__(self, signal_df, ticker='IC.CFE', price_kind='vwap', pos_dict = {},
                 min_holding_period=5, stop_profit=100, tick_price_kind = 'tickslippage',
                 stop_loss=-100, capital_use_rate = 3,  open_num_permin=10, close_num_permin=10, deal_volume_ratio = 0.1,
                 initial_cash=50000000, c_rate=2.5 / 100000, slippage=0.6, tickslippage = 1.2, vol_pertick = 1, 
                 delay_tick_num = 0,max_wait_tick_num = 0, hour_t=14, minute_t=30, save_path='/data/user/', name_prefix=''):
        """
        :param signal_df: 信号dataframe，index为分钟，如果只有一列，则认为此列为信号值，读取行情数据进行测试。
                            如果多列，则第一列需为信号值，在函数内读取行情数据
                            测试时不对信号值做任何处理，使用原始值。
        :param ticker: 交易品种，
        :param price_kind: 使用下一分钟的哪个字段作为买入卖出价格，默认vwap
        :param long_in: 开多进场阈值
        :param long_out: 开多出场阈值
        :param short_in: 开空进场阈值，默认设的极小表示不开空
        :param short_out: 开空出场阈值
        :param signal_down_t: 信号值从当前持仓周期内最大回撤阈值
        :param profit_down_t: 收益从当前持仓周期内最大回撤阈值
        :param signal_inout_diff: 刚开仓在min_holding_period内允许信号波动的幅度，如0.5进场，理论出场阈值为0.5，
                                  但可在min_holding_period内出场阈值设为0.4
        :param min_holding_period: 最小持仓周期，但触发止损除外
        :param stop_profit: 止盈
        :param stop_loss: 止损
        
        :param initial_cash: 初始资金
        :param c_rate: 交易费用
        :param slippage: 交易价格滑点
        :param hour_t: 表示几点
        :param minute_t: 几分后不开仓，默认是14:30后不开仓，只平仓
        :param save_path: 结果保存路径
        :param name_prefix: 结果csv命名前缀
        :back_test function return: 一个字典：'results': 策略评价指标,
                'pnl',每分钟累积收益，equity_curve字段表示资金曲线
                'trade_detail': 每笔交易细节，equity_curve字段表示资金曲线,
                'daily_return',每日收益,
                'monthly_return': 月度收益
        """

        self.signal_df = signal_df
        self.ticker = ticker
        self.price_kind = price_kind
        self.para_pos_dict = pos_dict
#         self.para_pos_dict = self.get_target_pos_dict(entry_para, exit_para)
        self.min_holding_period = min_holding_period
        self.stop_profit = stop_profit
        self.stop_loss = stop_loss * initial_cash
        self.open_num_permin = open_num_permin
        self.close_num_permin = close_num_permin
        self.deal_volume_ratio = deal_volume_ratio
        self.initial_cash = initial_cash
        self.c_rate = c_rate
        self.slippage = slippage
        self.hour_t = hour_t
        self.minute_t = minute_t
        face_value_dict = {'IC.CFE': 200,
                           'IF.CFE': 300,
                           'IH.CFE': 300}
        self.face_value = face_value_dict[self.ticker]
        self.save_path = save_path
        self.name_prefix = name_prefix
        self.max_open_value = capital_use_rate * self.initial_cash
        self.capital_use_rate = capital_use_rate
        
        self.tickslippage = tickslippage
        self.vol_pertick = vol_pertick
        self.max_wait_tick_num = max_wait_tick_num
        self.delay_tick_num = delay_tick_num
        self.tick_price_kind = tick_price_kind

    def back_test(self):
        df = self.prepare_data()

        raw = df.iloc[0]['raw']
        deal_count = 0  # 第几笔交易 每分钟开仓算一笔交易
        now_hold_dealcount = []  # 当前未平仓的开仓序号
        pre_target_pos = (0,0)
        pre_target_pos_state = 0
        profit_intraday = 0
        now_hold_num = 0
        pre_hold_num = 0 #记录上一时刻仓位,计算多少笔交易时使用
        totaldeal_count = 0 #从空仓到持仓再到空仓算一笔交易
        totaltrade_dict = {}
        profit_intradeal = 0 # 计算本次交易收益
        maxposition_intradeal = (0,0)
        trade_dict = {}
        pnl_dict = {}  # 记录每分钟的资金曲线
        open_value_intraday = 0  # 今日开仓了多少钱 累计
        pre_date = datetime.date(1998, 1, 1)  # 初始前一天日期
        length = len(df) - 1
        
        stop_loss_flag = False # 是否触发了止损
        stop_loss_timelist = []
        tick_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/TICK/STOCK_INDEX_FUTURE/'

        for i in tqdm(range(1, length)):
            nowtime = df.iloc[i]['dt']

            now_date = nowtime.date()
            if now_date != pre_date:
                tickdf = pd.read_csv(os.path.join(tick_path, df.iloc[i]['contract_00'][:6], str(now_date).replace('-','') + '.csv'))[['dt','Buy1Price','Sell1Price','TotalVolumeTrade']]
                tickdf['TotalVolumeTrade'] = tickdf.TotalVolumeTrade.diff()
                tickdf['dt'] = pd.to_datetime(tickdf['dt'])
                tickdf = tickdf.set_index('dt')
                tickdf = tickdf.round({'Buy1Price':1,'Sell1Price':1})
                idx_tickdf = tickdf.index
                buy1px_idx = tickdf.columns.tolist().index('Buy1Price')
                sell1px_idx = tickdf.columns.tolist().index('Sell1Price')
                volume_idx = tickdf.columns.tolist().index('TotalVolumeTrade')
                
                open_value_intraday = 0
                profit_intraday = 0
                stop_loss_flag = False
                if now_hold_num != 0:
                    print(nowtime, now_hold_num, '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                    assert now_hold_num == 0
            
            valid_px = df.iloc[0]['close'] if i < 5 else df.iloc[i-5]['close']
            
            close = df.iloc[i]['close']
            last_close = df.iloc[i - 1]['close']  # 上一分钟收盘价
            twap_px = df.iloc[i]['twap']
                
            pre_raw = raw
            raw = df.iloc[i]['raw']
            
            # 当每分钟最大成交数量占此分钟成交量的百分比大于0时，更新每分钟最大平仓数量
            if self.deal_volume_ratio > 0:
                self.open_num_permin = min(max(np.floor(df.iloc[i]['volume'] * self.deal_volume_ratio), 1), 30)
                self.close_num_permin = self.open_num_permin

            now_hold_num_state = np.sign(now_hold_num)
            now_hold_num_abs = abs(now_hold_num)

            if (nowtime.hour >= self.hour_t) and (nowtime.minute >= self.minute_t):
                target_pos = (0, 0)
            else:
                target_pos = self.get_target_pos_from_signal(raw)
            target_pos_state = np.sign(raw)
            
            pre_tickdf = tickdf.loc[idx_tickdf.time < nowtime.time()].iloc[-1*(self.delay_tick_num + 1):].values
            if pre_target_pos_state >= 0:
                open_price = pre_tickdf[0][buy1px_idx] + self.tickslippage if self.tick_price_kind == 'tickslippage' else pre_tickdf[0][sell1px_idx]
            else:
                open_price = pre_tickdf[0][sell1px_idx] - self.tickslippage if self.tick_price_kind == 'tickslippage' else pre_tickdf[0][buy1px_idx]
      
            target_open_num_max = np.floor(self.initial_cash * max(pre_target_pos)  / (self.face_value * open_price))
            target_open_num_min = np.floor(self.initial_cash * min(pre_target_pos)  / (self.face_value * open_price))
            if min(pre_target_pos) > min(maxposition_intradeal):
                maxposition_intradeal = pre_target_pos

            #如果当前持仓方向与上一分钟开仓信号方向不一致，先平仓。或者当前持仓大于目标持仓上限，需平仓
            if (stop_loss_flag and (now_hold_num!=0)) or (((nowtime.hour == 14) and (nowtime.minute == 57)) and (now_hold_num != 0)) or \
             (now_hold_num_state * pre_target_pos_state == -1) or (now_hold_num_abs > target_open_num_max):
                
                if ((nowtime.hour == 14) and (nowtime.minute == 57)) and (now_hold_num != 0):
                    close_contract_num = now_hold_num_abs
                elif stop_loss_flag and (now_hold_num!=0):
                    close_contract_num = min(now_hold_num_abs, self.close_num_permin)
                elif now_hold_num_state * pre_target_pos_state == -1:
                 
                    close_contract_num = min(now_hold_num_abs, self.close_num_permin)
                elif now_hold_num_abs > target_open_num_max:
                    close_contract_num = min(now_hold_num_abs - target_open_num_max, self.close_num_permin)
                
                
                if now_hold_num_state == 1:
                    close_price = pre_tickdf[0][sell1px_idx] - self.tickslippage if self.tick_price_kind == 'tickslippage' else pre_tickdf[0][buy1px_idx]
                elif now_hold_num_state == -1:
                    close_price = pre_tickdf[0][buy1px_idx] + self.tickslippage if self.tick_price_kind == 'tickslippage' else pre_tickdf[0][sell1px_idx]
                
                
                # 开始平仓
                close_dict = {}
                totalclose_fee = 0
                totalclose_value = 0
                dealtickcount = 0
                usetickcount = 0
                dealtotal_vol = 0  #此分钟平仓了多少手
                order_px_para = tickdf.loc[(idx_tickdf.hour == nowtime.hour) & (idx_tickdf.minute == nowtime.minute)].values
                wait_tick_num = 0
                putorder_num = 1 # 此分钟发单次数
                makedealflag = False
                tick_state = []
                for j in range(len(order_px_para)):
                    if abs(close_price / valid_px - 1) >= 0.05:
                        if now_hold_num_state == 1:
                            close_price = order_px_para[j][sell1px_idx] - self.tickslippage if self.tick_price_kind == 'tickslippage' else order_px_para[j][buy1px_idx]
                        elif now_hold_num_state == -1:
                            close_price = order_px_para[j][buy1px_idx] + self.tickslippage if self.tick_price_kind == 'tickslippage' else order_px_para[j][sell1px_idx]
                        if (j != (len(order_px_para) - 1)) and (close_contract_num != 0) and (now_hold_num != 0):
                            putorder_num += 1
                        tick_state.append(0)
                        continue
                    tickvolume = order_px_para[j][volume_idx]
                    if now_hold_num_state == 1:
                        deal_price = order_px_para[j][buy1px_idx]
                        if (round(close_price,1) <= deal_price) and (tickvolume > 0) and not makedealflag:
                            deal_vol = min(self.vol_pertick, close_contract_num)
                            close_dict[deal_price] = close_dict[deal_price] + deal_vol if deal_price in close_dict.keys() else deal_vol
                            close_contract_num -= deal_vol
                            
                            close_value = deal_price * self.face_value * deal_vol
                            close_fee = close_value * self.c_rate
                            totalclose_value += close_value
                            totalclose_fee += close_fee
                            now_hold_num -= deal_vol * now_hold_num_state
                            dealtickcount += 1
                            dealtotal_vol += deal_vol
                            
                            tick_state.append(1)
                            makedealflag = True
                            
                        else:
                            tick_state.append(0)
                            
                        wait_tick_num += 1
                        if wait_tick_num >= self.max_wait_tick_num:
                            if j - self.delay_tick_num < 0:
                                close_price = pre_tickdf[j+1][sell1px_idx] - self.tickslippage if self.tick_price_kind == 'tickslippage' else pre_tickdf[j+1][buy1px_idx]
                            else:
                                close_price = order_px_para[j-self.delay_tick_num][sell1px_idx] - self.tickslippage if self.tick_price_kind == 'tickslippage' else order_px_para[j-self.delay_tick_num][buy1px_idx] 
                            if (j != (len(order_px_para) - 1)) and (close_contract_num != 0) and (now_hold_num !=0):
                                putorder_num += 1
                            wait_tick_num = 0
                            makedealflag = False
                        
                    elif now_hold_num_state == -1:
                        deal_price = order_px_para[j][sell1px_idx]
                        if (round(close_price,1) >= deal_price) and (tickvolume > 0) and not makedealflag:
                            deal_vol = min(self.vol_pertick, close_contract_num)
                            close_dict[deal_price] = close_dict[deal_price] + deal_vol if deal_price in close_dict.keys() else deal_vol
                            close_contract_num -= deal_vol
                            
                            close_value = deal_price * self.face_value * deal_vol
                            close_fee = close_value * self.c_rate
                            totalclose_fee += close_fee
                            totalclose_value += close_value
                            now_hold_num -= deal_vol * now_hold_num_state
                            dealtickcount += 1
                            dealtotal_vol += deal_vol
                            
                            tick_state.append(1)
                            makedealflag = True
                        else:
                            tick_state.append(0)
                            
                        wait_tick_num += 1
                        if wait_tick_num >= self.max_wait_tick_num:
                            if j - self.delay_tick_num < 0:
                                close_price = pre_tickdf[j+1][buy1px_idx] + self.tickslippage if self.tick_price_kind == 'tickslippage' else pre_tickdf[j+1][sell1px_idx]
                            else:
                                close_price = order_px_para[j-self.delay_tick_num][buy1px_idx] + self.tickslippage if self.tick_price_kind == 'tickslippage' else order_px_para[j-self.delay_tick_num][sell1px_idx]
                            if (j != (len(order_px_para) - 1)) and (close_contract_num != 0) and (now_hold_num !=0):
                                putorder_num += 1
                            wait_tick_num = 0
                            makedealflag = False
                            
                        
                   
                    # 处理最后一刻没平完的情况
                    if (nowtime.hour == 14) & (nowtime.minute == 57) & (j == (len(order_px_para) - 1)) & (now_hold_num != 0):
                        print('*****     %s      *****' % ('最后一刻强行平完'), now_hold_num, self.initial_cash, nowtime, self.tickslippage, self.max_wait_tick_num, self.delay_tick_num)
                        with open(os.path.join(self.save_path, 'pingcang.txt'), 'a') as file:
                            file.write(str(nowtime) + ' ' + str(now_hold_num) + ' ' + str(self.initial_cash) + ' ' + str(self.tickslippage) + ' ' + str(self.max_wait_tick_num) + ' ' + str(self.delay_tick_num) + '\r\n')
                        
                        if now_hold_num_state == 1:
                            deal_price = order_px_para[j][buy1px_idx]
                        elif now_hold_num_state == -1:
                            deal_price = order_px_para[j][sell1px_idx]
                        deal_vol = abs(now_hold_num)
                        close_dict[deal_price] = close_dict[deal_price] + deal_vol if deal_price in close_dict.keys() else deal_vol
                        
                        close_value = deal_price * self.face_value * deal_vol
                        close_fee = close_value * self.c_rate
                        totalclose_value += close_value
                        totalclose_fee += close_fee
                        now_hold_num -= deal_vol * now_hold_num_state
                        dealtickcount += 1
                        dealtotal_vol += deal_vol
                    
                    usetickcount += 1
                    if (close_contract_num == 0) or (now_hold_num == 0):
                        break
                
#                 now_hold_dealcount.append(deal_count)
                weighted_close_px = 0
                this_deal_nowprofit = 0
                if len(close_dict) > 0:
                    this_deal_nowprofit= sum([self.face_value * v * (k - last_close) * now_hold_num_state for k,v in close_dict.items()])
                    weighted_close_px = sum([k*v for k,v in close_dict.items()]) / sum([v for k,v in close_dict.items()])
                dealflag = 'Sc' if now_hold_num_state == 1 else 'Bc'
                # 记录下来本次开仓记录
                trade_dict[deal_count] = {'deal_count': deal_count, 'pos': pre_target_pos_state, 'dealflag':dealflag, 'deal_time': nowtime,
                                          'deal_weighted_price': weighted_close_px,'twap':twap_px,'deal_dict': str(close_dict),
                                          'deal_contract_num': dealtotal_vol, 'now_hold_num': now_hold_num,
                                          'target_pos_max': pre_target_pos_state * target_open_num_max,
                                          'target_pos_min': pre_target_pos_state * target_open_num_min,
                                          'target_pos': pre_target_pos,
                                          'signal': pre_raw,
                                          'deal_value': totalclose_value, 'deal_fee': totalclose_fee,'open_value_intraday':np.nan,
                                          'putorder_num':putorder_num,
                                          'dealtickcount': dealtickcount,'usetickcount': usetickcount, 'tick_state':str(tick_state)}

                deal_count += 1
                
                
                if now_hold_num != 0:
                    now_hold_num_profit = self.face_value * now_hold_num * (close - last_close)  # 此分钟收益
                else:
                    now_hold_num_profit = 0
                    
                profit_thismin = this_deal_nowprofit - totalclose_fee + now_hold_num_profit
                pnl_dict[nowtime] = profit_thismin # 此分钟盈亏应为此分钟收益减去手续费
                profit_intraday += profit_thismin
                profit_intradeal += profit_thismin
                
                if (pre_hold_num != 0) and (now_hold_num == 0):
                    totaltrade_dict[totaldeal_count].update({'pos_close':np.sign(pre_hold_num),'close_time':nowtime,'profit_intradeal':profit_intradeal,'max_position':maxposition_intradeal})
                    profit_intradeal = 0
                    maxposition_intradeal = (0,0)
                    totaldeal_count += 1


            elif (now_hold_num_abs >= target_open_num_min) and (now_hold_num_abs <= target_open_num_max):
                # 之前持仓的本分钟收益
                if now_hold_num != 0:
                    now_hold_num_profit = self.face_value * now_hold_num * (close - last_close)  # 此分钟收益
                else:
                    now_hold_num_profit = 0
                pnl_dict[nowtime] = now_hold_num_profit
                profit_intraday += now_hold_num_profit
                profit_intradeal += now_hold_num_profit
                
                
            elif now_hold_num_abs < target_open_num_min: # 开仓
                # 之前持仓的本分钟收益
                if now_hold_num != 0:
                    now_hold_num_profit = self.face_value * now_hold_num * (close - last_close)  # 此分钟收益
                else:
                    now_hold_num_profit = 0
                    
                open_contract_num = min(target_open_num_min - now_hold_num_abs, self.open_num_permin, np.floor((self.max_open_value-open_value_intraday)/(1+self.c_rate)/open_price / self.face_value))
                # 两点半后 止损 当日开仓金额达到上限不开仓
                if ((open_contract_num <=0 ) or (nowtime.hour == self.hour_t) and (nowtime.minute >= self.minute_t)) or stop_loss_flag or (open_value_intraday > self.max_open_value):
                    pnl_dict[nowtime] = now_hold_num_profit
                    profit_intraday += now_hold_num_profit
                    profit_intradeal += now_hold_num_profit
                    
                    pre_date = now_date
                    pre_target_pos = target_pos
                    pre_target_pos_state = target_pos_state
                    pre_hold_num = now_hold_num
                    continue
                
                # 开始开仓
                open_dict = {}
                order_px_para = tickdf.loc[(idx_tickdf.hour == nowtime.hour) & (idx_tickdf.minute == nowtime.minute)].values
                dealtickcount = 0
                usetickcount = 0
                dealtotal_vol = 0
                totalopen_value = 0
                totalopen_fee = 0
                wait_tick_num = 0
                putorder_num = 1
                makedealflag = False
                tick_state = []
                for z in range(len(order_px_para)):
                    if abs(open_price / valid_px - 1) >= 0.05:
                        if pre_target_pos_state == 1:
                            open_price = order_px_para[z][buy1px_idx] + self.tickslippage if self.tick_price_kind == 'tickslippage' else order_px_para[z][sell1px_idx]
                        elif pre_target_pos_state == -1:
                            open_price = order_px_para[z][sell1px_idx] - self.tickslippage if self.tick_price_kind == 'tickslippage' else order_px_para[z][buy1px_idx]
                        if (z != (len(order_px_para) - 1)) and (open_contract_num != 0):
                            putorder_num += 1
                        tick_state.append(0)
                        continue
                    tickvolume = order_px_para[z][volume_idx]
                    if pre_target_pos_state == 1:
                        deal_price = order_px_para[z][sell1px_idx]
                        if (round(open_price,1) >= deal_price) and (tickvolume > 0) and not makedealflag:
                            deal_vol = min(self.vol_pertick, open_contract_num)
                            open_dict[deal_price] = open_dict[deal_price] + deal_vol if deal_price in open_dict.keys() else deal_vol
                            open_contract_num -= deal_vol
                            
                            open_value = deal_price * self.face_value * deal_vol
                            open_fee = open_value * self.c_rate
                            open_value_intraday += (open_value + open_fee)
                            totalopen_value += open_value
                            totalopen_fee += open_fee
                            now_hold_num += deal_vol * pre_target_pos_state
                            dealtickcount += 1
                            dealtotal_vol += deal_vol
                            
                            tick_state.append(1)
                            makedealflag = True
                            
                        else:# 没成交
                            tick_state.append(0)
                            
                        wait_tick_num += 1    
                        if wait_tick_num >= self.max_wait_tick_num:
                            if z - self.delay_tick_num < 0:
                                open_price = pre_tickdf[z+1][buy1px_idx] + self.tickslippage if self.tick_price_kind == 'tickslippage' else pre_tickdf[z+1][sell1px_idx]
                            else:
                                open_price = order_px_para[z-self.delay_tick_num][buy1px_idx] + self.tickslippage if self.tick_price_kind == 'tickslippage' else order_px_para[z-self.delay_tick_num][sell1px_idx]
                            if (z != (len(order_px_para) - 1)) and (open_contract_num != 0):
                                putorder_num += 1
                            wait_tick_num = 0
                            makedealflag = False
                        
                    elif pre_target_pos_state == -1:
                        deal_price = order_px_para[z][buy1px_idx]
                        if (round(open_price,1) <= deal_price) and (tickvolume > 0) and not makedealflag:
                            deal_vol = min(self.vol_pertick, open_contract_num)
                            open_dict[deal_price] = open_dict[deal_price] + deal_vol if deal_price in open_dict.keys() else deal_vol
                            open_contract_num -= deal_vol
                            
                            open_value = deal_price * self.face_value * deal_vol
                            open_fee = open_value * self.c_rate
                            open_value_intraday += (open_value + open_fee)
                            totalopen_value += open_value
                            totalopen_fee += open_fee
                            now_hold_num += deal_vol * pre_target_pos_state
                            dealtickcount += 1
                            dealtotal_vol += deal_vol
                            
                            tick_state.append(1)
                            makedealflag = True
                        else:# 没成交
                            tick_state.append(0)
                        
                        wait_tick_num += 1
                        if wait_tick_num >= self.max_wait_tick_num:
                            if z - self.delay_tick_num < 0:
                                open_price = pre_tickdf[z+1][sell1px_idx] - self.tickslippage if self.tick_price_kind == 'tickslippage' else pre_tickdf[z+1][buy1px_idx]
                            else:
                                open_price = order_px_para[z-self.delay_tick_num][sell1px_idx] - self.tickslippage if self.tick_price_kind == 'tickslippage' else order_px_para[z-self.delay_tick_num][buy1px_idx]
                            if (z != (len(order_px_para) - 1)) and (open_contract_num != 0):
                                putorder_num += 1
                            wait_tick_num = 0
                            makedealflag = False
                  
                    usetickcount += 1    
                    if open_contract_num == 0:
                        break
                

                now_hold_dealcount.append(deal_count)
                
                weighted_open_px = 0
                this_deal_nowprofit = 0
                if len(open_dict) > 0:
                    this_deal_nowprofit= sum([self.face_value * v * (close - k) * pre_target_pos_state for k,v in open_dict.items()])
                    weighted_open_px = sum([k*v for k,v in open_dict.items()]) / sum([v for k,v in open_dict.items()])
                
                dealflag = 'Bo' if pre_target_pos_state == 1 else 'So'
                # 记录下来本次开仓记录
                trade_dict[deal_count] = {'deal_count': deal_count, 'pos': pre_target_pos_state, 'dealflag':dealflag, 'deal_time': nowtime,
                                          'deal_weighted_price': weighted_open_px,'twap':twap_px,'deal_dict': str(open_dict),
                                          'deal_contract_num': dealtotal_vol, 'now_hold_num': now_hold_num,
                                          'target_pos_max': pre_target_pos_state * target_open_num_max,
                                          'target_pos_min': pre_target_pos_state * target_open_num_min,
                                          'target_pos': pre_target_pos,
                                          'signal': pre_raw,
                                          'deal_value': totalopen_value, 'deal_fee': totalopen_fee,'open_value_intraday':open_value_intraday,
                                          'putorder_num':putorder_num,
                                          'dealtickcount': dealtickcount,'usetickcount': usetickcount,'tick_state':str(tick_state)}

                deal_count += 1
               
                profit_thismin = this_deal_nowprofit - totalopen_fee + now_hold_num_profit
                pnl_dict[nowtime] = profit_thismin # 此分钟盈亏应为此分钟收益减去手续费
                profit_intraday += profit_thismin
                profit_intradeal += profit_thismin
                
                if (pre_hold_num == 0) and (now_hold_num != 0):
                    totaltrade_dict[totaldeal_count] = {'totaltrade_count':totaldeal_count,'pos':np.sign(now_hold_num),'open_time':nowtime}
                
            pre_date = now_date
            pre_target_pos = target_pos
            pre_target_pos_state = target_pos_state
            pre_hold_num = now_hold_num
            
            if profit_intraday < self.stop_loss:
                stop_loss_timelist.append(nowtime)
                stop_loss_flag = True
           
        trade_df = pd.DataFrame(trade_dict).T
        
        totaltrade_df = pd.DataFrame(totaltrade_dict).T
        totaltrade_df = totaltrade_df.sort_values('open_time')
        totaltrade_df['change'] = totaltrade_df.profit_intradeal / self.initial_cash
        totaltrade_df['equity_curve'] = totaltrade_df.change.cumsum()
        totaltrade_df['holding_time'] = totaltrade_df.apply(lambda x: self.get_timediff_minutes(x.open_time, x.close_time), axis=1)
        
        pnl_df = pd.DataFrame(pnl_dict, index=['profit']).T
        pnl_df = pnl_df.reset_index()
        pnl_df.columns = ['dt', 'profit']
        pnl_df['change'] = pnl_df['profit'] / self.initial_cash
        pnl_df['equity_curve'] = (pnl_df['profit'].cumsum() + self.initial_cash) / self.initial_cash

        results, daily_return, daily_openvalue = self.strategy_evaluate(pnl_df.copy(), totaltrade_df.copy(), trade_df.copy())
        
        
        stop_loss_timelist.sort()
        stoplossdf = pd.DataFrame({'stop_loss_time':stop_loss_timelist})
        stoplossdf['date'] = stoplossdf.stop_loss_time.apply(lambda x:x.date())
        stoplossdf = stoplossdf.groupby('date').agg({'stop_loss_time':lambda x:x.head(1)})
        
        results.loc['止损次数'] = len(stoplossdf)
        daily_return.columns = ['daily_return','daily_equty_curve']

        pnl_df = pnl_df.set_index('dt')
        pnl = pnl_df[['equity_curve']] - 1
        pnl.columns = ['profit']

        trade_df = trade_df[['deal_count', 'pos', 'dealflag', 'deal_time','twap','deal_weighted_price','deal_dict','deal_contract_num', 
                             'now_hold_num','target_pos_max', 'target_pos_min','target_pos','signal','deal_value', 'deal_fee',
                             'open_value_intraday','putorder_num', 'dealtickcount','usetickcount', 'tick_state']]
        
        totaltrade_df = totaltrade_df[['totaltrade_count', 'pos',  'open_time', 'close_time', 'pos_close', 'profit_intradeal', 'change',
                                      'equity_curve', 'holding_time','max_position']]

        
        
        if self.save_path != None:
            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)
            daily_openvalue.to_csv(os.path.join(self.save_path, self.name_prefix + 'daily_openvalue.csv'), index=False)
            totaltrade_df.to_csv(os.path.join(self.save_path, self.name_prefix + 'total_trade_detail.csv'), index=False)
            trade_df.to_csv(os.path.join(self.save_path, self.name_prefix + 'minute_trade_detail.csv'), index=False)
            pnl.to_csv(os.path.join(self.save_path, self.name_prefix + 'pnl.csv'))
            daily_return.to_csv(os.path.join(self.save_path, self.name_prefix + 'daily_return.csv'))
            results.to_csv(os.path.join(self.save_path, self.name_prefix + 'results.csv'), encoding='gbk')
            stoplossdf.to_csv(os.path.join(self.save_path, self.name_prefix + 'stop_loss_time.csv'), index=False)
            pnl.plot(figsize=(20, 10))
            plt.title('profit', fontsize='large')
            plt.savefig(os.path.join(self.save_path, self.name_prefix + 'profit.png'))
        return pnl, results, trade_df, totaltrade_dict

    def prepare_data(self):
        if isinstance(self.signal_df, pd.Series):
            self.signal_df = self.signal_df.to_frame()

        # 获取信号开始结束时间，获取行情数据
        start_time = int(str(self.signal_df.ix[[0]].index.values[0]).split('T')[0].replace('-', ''))
        end_time = str(self.signal_df.ix[[-1]].index.values[0]).split('T')[0]
        end_time = int(
            str((datetime.datetime.strptime(end_time, '%Y-%m-%d') + datetime.timedelta(1)).date()).replace('-', ''))
        if len(self.signal_df.columns.tolist()) == 1:
            self.signal_df.columns = ['raw']
            md = IO.read_data([start_time, end_time], columns=['contract_00', 'open', 'high', 'low', 'close', 'vwap','volume','twap'],
                              alt='/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_SIF_TICK_TO_MINUTE_RECENT_MONTH.h5')
            md = md.xs(self.ticker, level=1)
            df = self.signal_df.join(md, how='inner')

        else:
            clist = ['raw'] + self.signal_df.columns.tolist()[1:]
            self.signal_df.columns = clist
            df = self.signal_df.copy()
            
        t_days_list = udt.get_trading_date_range(str(df.index[0].date()).replace('-', ''), str(df.index[-1].date()).replace('-', ''))
        t_days_list = [str(i)[:10] for i in t_days_list]
        t_mins_list = pd.date_range('09:30:00', '11:29:00', freq='min').to_list() + pd.date_range('13:00:00', '14:57:00', freq='min').to_list()
        t_mins_list = [str(i)[-8:] for i in t_mins_list]
        index_list = []
        for d in t_days_list:
            for m in t_mins_list:
                index_list.append(d + ' ' + m)
        index_min = pd.DataFrame({'dt': index_list})
        index_min['dt'] = pd.to_datetime(index_min['dt'])
        index_min = index_min.set_index('dt').sort_index()
        
        df = df.join(index_min,how = 'outer').sort_index()
        df['raw'] = df['raw'].fillna(0)

        # 每天只交易9:35-14:55时间段
        idx = df.index
        t1 = df.loc[(idx.hour == 9) & (idx.minute >= 34)]
        t2 = df.loc[(idx.hour == 10) | (idx.hour == 13)]
        t3 = df.loc[(idx.hour == 11) & (idx.minute < 30)]
        t4 = df.loc[(idx.hour == 14) & (idx.minute <= 57)]
        t = t1.append(t2).append(t3).append(t4)
#         t = t.sort_index()
#         t = t.reset_index()
#         t['date'] = t['dt'].apply(lambda x: x.date())
#         # 将每天数据的第一条以及后两条设置为0,确保不持隔夜仓
#         alist = t.groupby('date').apply(lambda x: x.dt.iloc[0]).tolist()
#         blist = t.groupby('date').apply(lambda x: x.dt.iloc[-27:]).tolist()
#         t.loc[t.dt.isin(alist), 'raw'] = 0
#         t.loc[t.dt.isin(blist), 'raw'] = 0
#         t.drop(['date'], axis=1, inplace=True)
#         t = t.set_index('dt')

        df = t.sort_index().reset_index()
        df['raw'] = round(df['raw'],4)
        return df

    def get_target_pos_from_signal(self, signal):
        if signal != signal:
            signal = 0
        for k in self.para_pos_dict.keys():
            if (abs(signal) >= k[0]) and (abs(signal) < k[1]):
                return self.para_pos_dict[k]
    
#         return self.para_pos_dict[float(str(abs(signal))[:3])]
    
    # 计算策略评价指标
    def strategy_evaluate(self, pnl, trade, trade_minute):
        """
        :param trade: 每笔交易的df
        :return:
        """

        # ===新建一个dataframe保存回测指标
        results = pd.DataFrame()

        # ===计算累积净值
        results.loc[0, '累积净值'] = round(pnl['equity_curve'].iloc[-1], 3)

        # 计算夏普比率
        pnl['date'] = pnl['dt'].apply(lambda x: x.date())
        sharpedailyreturn = pnl.groupby('date')['change'].sum().to_frame()
        tradedays = len(sharpedailyreturn)
        sharpe_ratio = round(sharpedailyreturn['change'].mean() / sharpedailyreturn['change'].std() * np.sqrt(252), 3)
        results.loc[0, '夏普比率'] = sharpe_ratio

        # ===计算年化收益
        annual_return = (pnl['equity_curve'].iloc[-1] / pnl['equity_curve'].iloc[0] - 1) * (
                '365 days 00:00:00' / (pnl['dt'].iloc[-1] - pnl['dt'].iloc[0]))

        results.loc[0, '年化收益'] = format(round(annual_return, 3), '.2%')


        
        sharpedailyreturn['equity_curve'] = sharpedailyreturn['change'].cumsum()
        sharpedailyreturn = sharpedailyreturn.reset_index()
        # ===计算最大回撤
        # 计算当日之前的资金曲线的最高点
        sharpedailyreturn['max2here'] = sharpedailyreturn['equity_curve'].expanding().max()
        # 计算到历史最高值到当日的跌幅，drowdwon
        sharpedailyreturn['dd2here'] = sharpedailyreturn['equity_curve'] - sharpedailyreturn['max2here']
        # 计算最大回撤，以及最大回撤结束时间
        end_date, max_draw_down = tuple(sharpedailyreturn.sort_values(by=['dd2here']).iloc[0][['date', 'dd2here']])
        # 计算最大回撤开始时间
        start_date = sharpedailyreturn[sharpedailyreturn['date'] <= end_date].sort_values(by='equity_curve', ascending=False).iloc[0][
            'date']
        # 将无关的变量删除
        sharpedailyreturn.drop(['max2here', 'dd2here'], axis=1, inplace=True)
        sharpedailyreturn = sharpedailyreturn.set_index('date')
        results.loc[0, '最大回撤'] = format(max_draw_down, '.2%')
        results.loc[0, '最大回撤开始时间'] = str(start_date)
        results.loc[0, '最大回撤结束时间'] = str(end_date)
        

        # ===年化收益/回撤比
        results.loc[0, '年化收益/回撤比'] = round(abs(annual_return / max_draw_down), 2)
        
        # ===统计每笔交易
        results.loc[0, '总交易笔数'] = len(trade)  # 交易笔数
        results.loc[0, '平均每天交易笔数'] = round(len(trade) / tradedays, 2)  # 盈利笔数
        results.loc[0, '亏损笔数'] = len(trade.loc[trade['change'] <= 0])  # 亏损笔数
        results.loc[0, '盈利笔数'] = len(trade.loc[trade['change'] > 0])  # 盈利笔数
        results.loc[0, '胜率'] = format(results.loc[0, '盈利笔数'] / len(trade), '.2%')  # 胜率
        
        longtrade = trade[trade['pos'] == 1]
        shorttrade = trade[trade['pos'] == -1]
        results.loc[0, '做多笔数'] = len(longtrade)  
        results.loc[0, '做多胜率'] = format(len(longtrade[longtrade.change > 0]) / len(longtrade), '.2%')  # 胜率
        results.loc[0, '做空笔数'] = len(shorttrade)  
        results.loc[0, '做空胜率'] = format(len(shorttrade[shorttrade.change > 0]) / len(shorttrade), '.2%')  # 胜率
        

        results.loc[0, '每笔交易平均盈亏'] = format(trade['change'].mean(), '.4%')  # 每笔交易平均盈亏
        results.loc[0, '盈亏收益比'] = round(trade.loc[trade['change'] > 0]['change'].mean() / \
                                        trade.loc[trade['change'] < 0][
                                            'change'].mean() * (-1), 2)  # 盈亏比

        results.loc[0, '单笔最大盈利'] = format(trade['change'].max(), '.2%')  # 单笔最大盈利
        results.loc[0, '单笔最大亏损'] = format(trade['change'].min(), '.2%')  # 单笔最大亏损

        # ===统计持仓时间
        trade['持仓时间'] = trade['holding_time']
        max_minutes = trade['持仓时间'].max()
        results.loc[0, '单笔最长持有时间'] = str(int(max_minutes)) + ' 分钟'  # 单笔最长持有时间

        min_minutes = trade['持仓时间'].min()
        results.loc[0, '单笔最短持有时间'] = str(int(min_minutes)) + ' 分钟'  # 单笔最短持有时间

        mean_minutes = trade['持仓时间'].mean()
        results.loc[0, '平均持仓周期'] = str(round(mean_minutes, 1)) + ' 分钟'  # 平均持仓周期

        # ===连续盈利亏算
        results.loc[0, '最大连续盈利笔数'] = max(
            [len(list(v)) for k, v in itertools.groupby(np.where(trade['change'] > 0, 1, np.nan))])  # 最大连续盈利笔数
        results.loc[0, '最大连续亏损笔数'] = max(
            [len(list(v)) for k, v in itertools.groupby(np.where(trade['change'] < 0, 1, np.nan))])  # 最大连续亏损笔数
        
        trade_minute['date'] = trade_minute['deal_time'].apply(lambda x:x.date())
        trade_minute['open_value_intraday'] = trade_minute['open_value_intraday'].fillna(method = 'ffill')
        daily_openvalue = trade_minute.groupby('date').agg({'open_value_intraday':lambda x:x.tail(1)})
        results.loc[0, '平均每日杠杆'] = round(daily_openvalue.open_value_intraday.sum()/ len(sharpedailyreturn) / self.initial_cash, 2)

        results = results.T
        results.columns = ['num']
        return results, sharpedailyreturn, daily_openvalue
    
    def get_timediff_minutes(self, a, b):
        m = (b - a).total_seconds() / 60
        if (a.hour <= 11) & (b.hour >= 13):
            return m - 90 + 1
        else:
            return m + 1
            
# normalize 
def rolling_normalize_quantile(x, p = 1200, winsorize = True):
    up = x.rolling(p,min_periods = int(p/2)).quantile(0.99)
    down = x.rolling(p,min_periods=int(p/2)).quantile(0.01)
    xnorm = ((x-down)/(up-down))*2-1
    if winsorize:
        xnorm[xnorm>1] = 1
        xnorm[xnorm<-1] = -1
    return xnorm

# amt adj
def get_open_amt(ticker = '000906'):
    data = pd.read_pickle('/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/index/indexMinute_'+ticker+'.pkl',compression='gzip')
    amt = data.xs(int(ticker),level=1)[['minute','amt']]
    amt_df = amt.reset_index().set_index(['dt','minute'])['amt'].unstack()
    amt_df = amt_df/1e8
    amt_sum = amt_df.cumsum(axis=1)
    mnew = amt_sum[925]
    mnew = mnew.reset_index()
    mnew['dt'] = mnew['dt'].apply(lambda x:pd.Timestamp(str(x)))
    mnew = mnew.set_index('dt')
    return mnew

def get_amt_adj(start_date,end_date,ticker ='IC.CFE'):
    if ticker == 'IC.CFE':
        open_amt = get_open_amt('000905')
    elif ticker == 'IF.CFE':
        open_amt = get_open_amt('000300')
    else:
        raise ValueError('Wrong ticker!')
    start_date = IO.str_date_parser(start_date)
    end_date = udt.get_trading_day_offset(end_date,1)[0]
    open_amt = get_open_amt('000905').loc[start_date:end_date]  # for IC, we use zz500
    amt_adj = rolling_normalize_quantile(open_amt,120,winsorize=True)*0.5+1
    amt_adj.columns=['amt_adj']
    return amt_adj

# ret_std adj
def get_ret_std_adj(start_date,end_date,ticker = 'IC.CFE'):
    start_date = IO.str_date_parser(start_date)
    end_date = udt.get_trading_day_offset(end_date,1)[0]
    minute_data = IO.read_data([start_date,end_date],alt = 
                                '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_STOCK_INDEX_SPOT_MINUTE.h5')
    minute_data = minute_data.xs(ticker,level=1)
    minute_data['ret'] = minute_data['close_spot']/minute_data['close_spot'].shift(1)-1
    rt = minute_data['ret']
    rt[(rt.index.hour==9)&(rt.index.minute==30)]=np.nan
    rt_std = rt.rolling(240*2,min_periods=240).std()
    rt_std_adj = rolling_normalize_quantile(rt_std,240*120,winsorize=True)*0.5+1
    rt_std_adj.name='rt_std_adj'
    rt_std_adj = rt_std_adj.to_frame()
    return rt_std_adj
# equal weight of the two

def get_sig_adj(start_date, end_date, ticker='IC.CFE'):
    amt_adj = get_amt_adj(start_date,end_date,ticker=ticker)
    rt_std_adj = get_ret_std_adj(start_date,end_date,ticker=ticker)
    sig_adj = pd.concat([amt_adj,rt_std_adj],axis=1).sort_index()
    sig_adj['amt_adj']=sig_adj['amt_adj'].fillna(method='pad')
    sig_adj= sig_adj[sig_adj.index.hour!=0]
    adjcom = sig_adj.mean(axis=1)
    adjcom.name = 'sig_adj'
    return adjcom

# final result adjustment
def change_sig(path, sdate = 20150101, edate = 20201204, change_ticker = 'IC.CFE'):
    sigorg = pd.read_hdf(path)*2-1
    sigorg.index.name='dt'
    adjcom = get_sig_adj(sdate, edate, ticker=change_ticker)
    sig_res = sigorg*adjcom
    sig_res.name = 'sig_res'
    sig_res = sig_res.to_frame()
    return sig_res
    
def get_tickresult(para):
    tickslippage = para[0]
    max_wait_tick_num = para[1]
    delaynum = para[2]
    cash = para[3]
    cashdict = {50000000:'_0.5e8',100000000:'_1e8', 500000000:'_5e8', 300000000:'_3e8'}
    
    factor = change_sig('/data/user/012315/share/ts/strategy/minute/res_20201211/ic/base_prod_nd/pred_comb_norm_nd_mod.h5' )
#     factor = pd.read_hdf('/data/user/012315/share/ts/strategy/minute/res_20201211/ic/base_prod_nd/pred_comb_norm_nd_mod.h5') * 2 - 1
    
    save_root_path = '/data/user/015626/data/share/factor/back_test/IC_ts/20201218_orderprice_v2/'
    sigtype = 'base_prod_nd'
    adj = 0.5
    h5 = 'pred_comb_norm_nd_mod.h5'
    pos_dict = {(0, 0.4): (0.0, 0.0),
                     (0.4, 0.5): (0.0, 0.2/3),
                     (0.5, 0.6): (0.2/3, 0.4/3),
                     (0.6, 0.7): (0.4/3, 0.6/3),
                     (0.7, 0.8): (0.6/3, 0.8/3),
                     (0.8, 0.9): (0.8/3, 1.0/3),
                     (0.9, 2.1): (1.0/3, 1.0/3)}
        
    name_prefix = '20190501_20200401' + cashdict[cash]
    save_path = os.path.join(save_root_path, sigtype + '_' + str(adj), name_prefix, h5[:-3] + '_%s_%s_%s' % (str(tickslippage), str(max_wait_tick_num), str(delaynum)))
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    a,b,c,d = TS_BACK_TEST(factor.loc['20190501':'20200401'],price_kind='twap',ticker='IC.CFE', slippage=0.6, initial_cash=cash, save_path = save_path, name_prefix = name_prefix,
              pos_dict=pos_dict, capital_use_rate = 1,stop_loss = -0.005,deal_volume_ratio = 1, 
              tick_price_kind = 'orderprice',
              tickslippage = tickslippage, max_wait_tick_num = max_wait_tick_num, delay_tick_num=delaynum).back_test() 
            
tslippagelist = [0.4,0.6,0.8,1.0,1.2,1.4,1.6,1.8,2.0]
waitlist = [4, 10]
delaylist = [1,2,3]
cashlist = [500000000]
paralist = []
for x in tslippagelist:
    for y in waitlist:
        for z in delaylist:
            for k in cashlist:
                paralist.append([x, y, z, k])
                
from multiprocessing import Pool
with Pool(processes = 24) as pool:
    pool.map(get_tickresult, paralist)                
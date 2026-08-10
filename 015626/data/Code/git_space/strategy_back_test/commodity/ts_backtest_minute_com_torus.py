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
import matplotlib
# 全局设置 figure 面板颜色
matplotlib.rcParams['figure.facecolor'] = 'white'
# 全局设置 axes 面板颜色
matplotlib.rcParams['axes.facecolor'] = 'white'
import shutil


class TS_BACK_TEST:

    def __init__(self, signal_df, ticker='IC.CFE', price_kind='vwap', pos_dict = {(0,   0.1): (0.0, 0.0),
                                                                                 (0.1, 0.2): (0,   0.5),
                                                                                 (0.2, 0.8): (0,   1),
                                                                                 (0.8, 0.9): (0.5, 1),
                                                                                 (0.9, 100): (1,   1)},
                 stop_loss=-100, open_num_permin=30, close_num_permin=30, deal_volume_ratio = 0,
                 initial_cash=1000000, leverge = 1, c_rate=0.0004, slippage=0, 
                 std_filter_threshold = -100, minute_after_stop_loss = 1, max_hold_time = None, filter_series = None, 
                 start_date = None, end_date = None, trading_range = None,
                 save_path='/data/user/', name_prefix='', show_image = True, save_csv = False, save_image = True, roll_over = True,
                 data_freq = 1, data_root_path = '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/MD/', univ = None):
        """ ！！！！！！！！！！！！！！ 默认参数的信号值在[-1,1]之间 ！！！！！！！！！！！
        :param signal_df: 信号 只能有一列， 测试时不对信号值做任何处理，使用原始值。
        :param ticker: 交易品种，
        :param price_kind: 使用下一分钟的哪个字段作为买入卖出价格，默认twap，如果改为'buy_sell'则用对价-slippage进行撮合
        :param pos_dict: 信号对应的仓位，信号一定要围绕0左右对称

        :param stop_loss: 止损
        :param minute_after_stop_loss: 止损后多久不交易，设置为30就是止损后30个bar内不再开仓

        :param open_num_permin: 开仓时每分钟可以撮合几张
        :param close_num_permin: 平仓时每分钟可以撮合几张
        :param deal_volume_ratio: 每分钟撮合张数占当分钟成交量的比例，当不为0时上面两个参数失去作用，设置为0.3，表示最多撮合30%的成交量

        :param initial_cash: 初始资金
        :param leverge: 杠杆，几倍杠杆
        :param c_rate: 交易费率（！！！ 此参数不起作用），商品撮合时自动从csv中读取费率，如果读取不到，则使用0.0001作为备选费率
        :param slippage: 交易价格滑点
        :param std_filter_threshold: 没有作用，不用管

        :param max_hold_time: 单笔最长持有时间,到时间后进行平仓
        :param filter_series: 1 0 -1，不是1,0！！！ 只对开仓有效
        :param start_date end_date: 回测日期区间
        :param trading_range: 每日的可以发单交易区间，[datetime.time(9,0), datetime.time(15,0)]，只接受datetime.time格式，设置为这样就是夜盘不交易
        
        :param save_path: 结果保存路径
        :param name_prefix: 结果命名前缀
        :param show_image: 是否展示图片
        :param save_csv: 是否保存各个结果
        :param save_image: 是否保存图片
        :param roll_over: 移仓
        :param data_freq: 读取什么频率的数据作为撮合价
        :param univ: 日频数据，每天交易哪个合约


        :back_test return: 一个字典：{分钟收益  'pnl':pnl , 评价指标 'results':results, 发单细节 'trade_df':trade_df, 
        成交笔数细节记录'totaltrade_df':totaltrade_df, 
        日频收益 'daily_return':daily_return}
        """

        if start_date is None:
            start_date = int(signal_df.index[0].date().strftime('%Y%m%d'))
        if end_date is None:
            end_date = int(signal_df.index[-1].date().strftime('%Y%m%d'))
        if trading_range is not None:
            assert isinstance(trading_range[0], datetime.time) and isinstance(trading_range[1], datetime.time), 'trading_range type must be datetime.time'
        self.trading_range = trading_range
        self.signal_df = signal_df.copy()
        if isinstance(self.signal_df, pd.Series):
            self.signal_df = self.signal_df.to_frame(name = 'raw')
        else:
            self.signal_df.columns = ['raw']

        data = IO.read_data([start_date, f'{end_date}235959'], columns = ['close', 'twap', 'Buy1Price_mean', 'Sell1Price_mean', 'BidAskSpreadMean', 'tday', 'volume'], 
            alt = f'{data_root_path}/{data_freq}MIN/PER_TICKER/{ticker}.h5')
        data = data.rename(columns = {'volume':'volume_deal','Buy1Price_mean':'Buy1Price', 'Sell1Price_mean':'Sell1Price', 'BidAskSpreadMean':'spread'})
        self.data_origin = data.copy()

        if isinstance(univ, pd.Series):
            univ = univ.to_frame(name = 'univ')
        else:
            univ.columns = ['univ']
        univ.index.name = 'tday'
        univ = univ.reset_index()
        univ['tday'] = univ['tday'].apply(lambda x:int(x.strftime('%Y%m%d')))

        data = data.reset_index().merge(univ, left_on = 'tday', right_on = 'tday', how = 'left')
        data['univ'] = data['univ'].fillna(method = 'ffill').fillna(method = 'bfill')
        select_data = data[data['Ticker'] == data['univ']]
        select_data = select_data.set_index('dt').rename(columns = {'Ticker':'contract'})
        self.signal_df = self.signal_df.join(select_data, how = 'left')
        self.signal_df['contract'] = self.signal_df['contract'].fillna(method = 'ffill')


        ccp = pd.read_csv('/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/INFO/WIND_CFuturesContPro.csv')
        ccp = ccp[['S_INFO_CEMULTIPLIER','S_INFO_DMEAN',  'S_INFO_PUNIT',  'S_INFO_WINDCODE']]
        ccp = ccp.rename(columns = {'S_INFO_WINDCODE':'Ticker'})
        ccp['multiplier'] = ccp['S_INFO_CEMULTIPLIER'].fillna(ccp['S_INFO_PUNIT'])
        ccp = ccp.set_index('Ticker')
        multiplier_dict = ccp['multiplier'].to_dict()

        self.signal_df['multiplier'] = self.signal_df['contract'].apply(lambda x:multiplier_dict[x]).fillna(method = 'ffill')

        self.signal_df = self.signal_df.loc[str(start_date):str(end_date)].sort_index()


        self.ticker = ticker
        self.price_kind = price_kind
        self.para_pos_dict = pos_dict
        self.stop_loss = stop_loss * initial_cash
        self.minute_after_stop_loss = minute_after_stop_loss
        self.max_hold_time = max_hold_time
        self.open_num_permin = open_num_permin
        self.close_num_permin = close_num_permin
        self.deal_volume_ratio = deal_volume_ratio
        self.initial_cash = initial_cash
        self.leverge = leverge
        fee_dict = pd.read_csv('/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/INFO/fee.csv', index_col=0)['fee'].to_dict()
        if c_rate is None:
            c_rate = fee_dict.get(ticker, 0.0001)
        if c_rate > 0.5:
            self.c_value = c_rate
            self.c_rate = 0
        else:
            self.c_rate = c_rate
            self.c_value = 0
        
        self.slippage = slippage

        self.std_filter_threshold = std_filter_threshold

        self.save_path = save_path
        self.name_prefix = name_prefix
        self.show_image = show_image
        self.save_csv = save_csv
        self.save_image = save_image
        self.roll_over = roll_over

        self.filter_series = filter_series
        if self.filter_series is None:
            self.signal_df['filter_score'] = np.nan
        else:
            if isinstance(self.filter_series, pd.Series):
                self.filter_series = self.filter_series.to_frame(name = 'filter_score')
            else:
                self.filter_series.columns = ['filter_score']
            self.signal_df = self.signal_df.join(self.filter_series, how = 'left')
            # self.signal_df.loc[(self.signal_df['raw'] < 0) & (self.signal_df['filter_score'] == 1), 'filter_score'] = -1

        columns_list = self.signal_df.reset_index().columns.tolist()
        global dt_idx, raw_idx, std_signal_idx, open_idx, close_idx ,low_idx ,vwap_idx ,twap_idx ,volume_idx ,amount_idx ,price_kind_idx, buy_vwap_idx, sell_vwap_idx, filter_socre_idx, HTSCSecurityID_idx, atr_idx, multiplier_idx, tday_idx, spread_idx
        dt_idx = columns_list.index('dt')
        raw_idx = columns_list.index('raw')
        # std_signal_idx = columns_list.index('std_signal')
        # open_idx = columns_list.index('open')
        close_idx = columns_list.index('close')
        # high_idx = columns_list.index('high')
        # low_idx = columns_list.index('low')
        # vwap_idx = columns_list.index('vwap')
        twap_idx = columns_list.index('twap')
        volume_idx = columns_list.index('volume_deal')
        # amount_idx = columns_list.index('amount')
        price_kind_idx = columns_list.index(price_kind)
        HTSCSecurityID_idx = columns_list.index('contract')
        filter_socre_idx = columns_list.index('filter_score')
        # atr_idx = columns_list.index('ATR')
        multiplier_idx = columns_list.index('multiplier')
        buy_vwap_idx = columns_list.index('Buy1Price')
        sell_vwap_idx = columns_list.index('Sell1Price')
        tday_idx = columns_list.index('tday')
        spread_idx = columns_list.index('spread')

    def back_test(self):
        df = self.signal_df.reset_index().values

        raw = df[0][raw_idx]
        deal_count = 0  # 第几笔交易 每分钟开仓算一笔交易
        now_hold_dealcount = []  # 当前未平仓的开仓序号
        pre_target_pos = (0,0)
        pre_target_pos_state = 0
        now_hold_num = 0
        pre_hold_num = 0 #记录上一时刻仓位,计算多少笔交易时使用
        totaldeal_count = 0 #从空仓到持仓再到空仓算一笔交易
        totaltrade_dict = {}
        profit_intradeal = 0 # 计算本次交易收益
        maxposition_intradeal = (0,0) # 记录下来本次交易过程中的最大仓位
        trade_dict = {}
        pnl_dict = {}  # 记录每分钟的资金曲线
        length = len(df) - 1
    
        stop_loss_flag = False # 是否触发了止损
        stop_loss_timelist = []
        stop_loss_minute = 0
        now_hold_time = 0
        max_hold_time_flag = 0

        pos_price = np.nan # 用于计算仓位的价格

        yicang_flag = False
        trading_flag = True

        for i in tqdm(range(1, length)):
            nowtime = df[i][dt_idx]
            if self.trading_range is not None and (nowtime.time() < self.trading_range[0] or nowtime.time() > self.trading_range[1]):
                trading_flag = False
            else:
                trading_flag = True

            close = df[i][close_idx]
            last_close = df[i-1][close_idx]  # 上一分钟收盘价
            twap = df[i][twap_idx]

            pre_raw = raw
            raw = df[i][raw_idx]

            pre_filter_socre = df[i-1][filter_socre_idx] 
            # std_filter_socre = df[i][std_signal_idx]
            open_flag = True #if std_filter_socre >= self.std_filter_threshold else False

            HTSCSecurityID = df[i][HTSCSecurityID_idx]

            if HTSCSecurityID != df[i-1][HTSCSecurityID_idx] and now_hold_num != 0 and self.roll_over:
                yicang_flag = True
                cont_old = df[i-1][HTSCSecurityID_idx]
                cont_old_pre_close = self.data_origin.loc[(df[i-1][dt_idx], cont_old)]['close']
                cont_old_twap = self.data_origin.loc[(df[i][dt_idx], cont_old)]['twap']
            else:
                yicang_flag = False
            
            face_value = df[i][multiplier_idx] #self.multiplier_dict[HTSCSecurityID.replace('.ZCE', '.CZC')]

            if now_hold_num != 0:
                now_hold_time += 1
            else:
                now_hold_time = 0

            if self.max_hold_time is not None and now_hold_time > self.max_hold_time:
                # stop_loss_flag = True
                if now_hold_num > 0:
                    max_hold_time_flag = 1
                else:
                    max_hold_time_flag = -1
            
            if stop_loss_flag:
                stop_loss_minute += 1

            # 当每分钟最大成交数量占此分钟成交量的百分比大于0时，更新每分钟最大平仓数量
            if self.deal_volume_ratio > 0:
                self.open_num_permin = max(np.floor(df[i][volume_idx] * self.deal_volume_ratio), 1)
                self.close_num_permin = self.open_num_permin

            now_hold_num_state = np.sign(now_hold_num)
            now_hold_num_abs = abs(now_hold_num)

            target_pos = self.get_target_pos_from_signal(raw)
            target_pos_state = np.sign(raw)
            if self.price_kind == 'buy_sell':
                if pre_target_pos_state == 1:
                    open_price = df[i][sell_vwap_idx] + self.slippage
                else:
                    open_price = df[i][buy_vwap_idx] - self.slippage
            else:
                open_price = df[i][price_kind_idx] + df[i][spread_idx] / 2 * pre_target_pos_state
            if now_hold_num == 0:
                pos_price = open_price
                if stop_loss_minute >= self.minute_after_stop_loss:
                    stop_loss_flag = False
                    stop_loss_minute = 0

            target_open_num_max = np.floor(self.initial_cash * self.leverge * max(pre_target_pos)  / (face_value * pos_price))
            target_open_num_min = np.floor(self.initial_cash * self.leverge * min(pre_target_pos)  / (face_value * pos_price))

            if min(pre_target_pos) > min(maxposition_intradeal):
                maxposition_intradeal = pre_target_pos

            if pre_hold_num == 0 and max_hold_time_flag == 1 and (pre_target_pos_state == -1 or target_open_num_max == 0):
                max_hold_time_flag = 0
            elif now_hold_num == 0 and max_hold_time_flag == -1 and (pre_target_pos_state == 1 or target_open_num_max == 0):
                max_hold_time_flag = 0

            #如果当前持仓方向与上一分钟开仓信号方向不一致，先平仓。或者当前持仓大于目标持仓上限，需平仓,或者该合约到期了。
            if trading_flag and now_hold_num != 0 and ((stop_loss_flag) or \
                         (now_hold_num_state * pre_target_pos_state == -1) or (now_hold_num_abs > target_open_num_max) or \
                         (max_hold_time_flag != 0) or (HTSCSecurityID != df[i-1][HTSCSecurityID_idx] and not self.roll_over)):
                
                if HTSCSecurityID != df[i-1][HTSCSecurityID_idx]:
                    close_contract_num = now_hold_num_abs # close all
                elif stop_loss_flag and (now_hold_num!=0):
                    close_contract_num = min(now_hold_num_abs, self.close_num_permin)
                elif now_hold_num_state * pre_target_pos_state == -1:
                    close_contract_num = min(now_hold_num_abs, self.close_num_permin)
                elif now_hold_num_abs > target_open_num_max:
                    close_contract_num = min(now_hold_num_abs - target_open_num_max, self.close_num_permin)
                elif max_hold_time_flag != 0:
                    close_contract_num = min(now_hold_num_abs, self.close_num_permin)
                
                
                if HTSCSecurityID == df[i-1][HTSCSecurityID_idx]:
                    if self.price_kind == 'buy_sell':
                        if now_hold_num_state == 1:
                            close_price = df[i][buy_vwap_idx] - self.slippage
                        else:
                            close_price = df[i][sell_vwap_idx] + self.slippage
                    else:
                        close_price = df[i][price_kind_idx] - df[i][spread_idx] / 2 * now_hold_num_state
                    
                    now_deal_pos_state = 1 if now_hold_num > 0 else -1
                    close_value = close_price * face_value * close_contract_num
                    close_fee = close_value * self.c_rate + self.c_value * close_contract_num
                    close_profit_this_min = face_value * close_contract_num * (close_price - last_close) * now_deal_pos_state - close_fee
                    
                    now_hold_num -= (close_contract_num * now_deal_pos_state)

                    dealflag = 'S' if now_hold_num_state == 1 else 'B'
                    trade_dict[deal_count] = {'deal_count': deal_count, 'pos': np.sign(now_hold_num), 'dealflag':dealflag, 'deal_time': nowtime,
                                          'deal_price':close_price,
                                          'deal_contract_num': close_contract_num,'now_hold_num': now_hold_num,
                                          'target_pos_max': pre_target_pos_state * target_open_num_max,
                                          'target_pos_min': pre_target_pos_state * target_open_num_min,
                                          'target_pos': pre_target_pos,'pre_signal': pre_raw,
                                          'deal_value': close_value, 'deal_fee': close_fee,'deal_contract':HTSCSecurityID, 'deal_type':''}
                else:
                    cont_old = df[i-1][HTSCSecurityID_idx]
                    cont_old_pre_close = self.data_origin.loc[(df[i-1][dt_idx], cont_old)]['close']
                    cont_old_twap = self.data_origin.loc[(df[i][dt_idx], cont_old)]['twap']

                    if self.price_kind == 'buy_sell':
                        if now_hold_num_state == 1:
                            close_price = self.data_origin.loc[(df[i][dt_idx], cont_old)]['Buy1Price'] - self.slippage
                        else:
                            close_price = self.data_origin.loc[(df[i][dt_idx], cont_old)]['Sell1Price'] + self.slippage
                    else:
                        close_price = cont_old_twap - self.data_origin.loc[(df[i][dt_idx], cont_old)]['spread'] / 2 * now_hold_num_state
                    
                    now_deal_pos_state = 1 if now_hold_num > 0 else -1
                    close_value = close_price * face_value * close_contract_num
                    close_fee = close_value * self.c_rate + self.c_value * close_contract_num
                    close_profit_this_min = face_value * close_contract_num * (close_price - cont_old_pre_close) * now_deal_pos_state - close_fee
                    
                    now_hold_num -= (close_contract_num * now_deal_pos_state)

                    dealflag = 'S' if now_hold_num_state == 1 else 'B'
                    trade_dict[deal_count] = {'deal_count': deal_count, 'pos': np.sign(now_hold_num), 'dealflag':dealflag, 'deal_time': nowtime,
                                          'deal_price':close_price,
                                          'deal_contract_num': close_contract_num,'now_hold_num': now_hold_num,
                                          'target_pos_max': pre_target_pos_state * target_open_num_max,
                                          'target_pos_min': pre_target_pos_state * target_open_num_min,
                                          'target_pos': pre_target_pos,'pre_signal': pre_raw,
                                          'deal_value': close_value, 'deal_fee': close_fee,'deal_contract':cont_old,'deal_type':'close old contract'}

                deal_count += 1    

                if now_hold_num != 0:
                    now_hold_num_profit = face_value * now_hold_num * (close - last_close)  # 此分钟收益
                else:
                    now_hold_num_profit = 0
                
                profit_thismin = close_profit_this_min + now_hold_num_profit
                pnl_dict[nowtime] = profit_thismin
                profit_intradeal += profit_thismin
                
                if (pre_hold_num != 0) and (now_hold_num == 0):
                    totaltrade_dict[totaldeal_count].update({'pos_close':np.sign(pre_hold_num),'close_time':nowtime,'profit_intradeal':profit_intradeal,'max_position':maxposition_intradeal, 'holding_time':now_hold_time, 'close_contract':HTSCSecurityID, 'blocked_money':self.initial_cash * min(maxposition_intradeal)})
                    profit_intradeal = 0
                    maxposition_intradeal = (0,0)
                    totaldeal_count += 1
                

            elif not trading_flag or (stop_loss_flag and (now_hold_num==0)) or ((now_hold_num_abs >= target_open_num_min) and (now_hold_num_abs <= target_open_num_max)) or not open_flag or (max_hold_time_flag != 0):
                # 之前持仓的本分钟收益
                if now_hold_num != 0:
                    if yicang_flag:
                        if self.price_kind == 'buy_sell':
                            if now_hold_num_state == 1:
                                _close_price = self.data_origin.loc[(df[i][dt_idx], cont_old)]['Buy1Price'] - self.slippage
                            else:
                                _close_price = self.data_origin.loc[(df[i][dt_idx], cont_old)]['Sell1Price'] + self.slippage
                        else:
                            _close_price = cont_old_twap - self.data_origin.loc[(df[i][dt_idx], cont_old)]['spread'] / 2 * now_hold_num_state
                        
                        now_deal_pos_state = 1 if now_hold_num > 0 else -1
                        close_value = _close_price * face_value * abs(now_hold_num)
                        close_fee = close_value * self.c_rate + self.c_value * abs(now_hold_num)
                        close_profit_this_min = face_value * abs(now_hold_num) * (cont_old_twap - cont_old_pre_close) * now_deal_pos_state - close_fee
                        
                        dealflag = 'S' if now_hold_num_state == 1 else 'B'
                        trade_dict[deal_count] = {'deal_count': deal_count, 'pos': np.sign(now_hold_num), 'dealflag':dealflag, 'deal_time': nowtime,
                                              'deal_price':_close_price,
                                              'deal_contract_num': abs(now_hold_num),'now_hold_num': now_hold_num,
                                              'target_pos_max': pre_target_pos_state * target_open_num_max,
                                              'target_pos_min': pre_target_pos_state * target_open_num_min,
                                              'target_pos': pre_target_pos,'pre_signal': pre_raw,
                                              'deal_value': close_value, 'deal_fee': close_fee,'deal_contract':cont_old,'deal_type':'yicang old contract'}
                        deal_count += 1


                        if self.price_kind == 'buy_sell':
                            if now_hold_num_state == 1:
                                _open_price = df[i][sell_vwap_idx] + self.slippage
                            else:
                                _open_price = df[i][buy_vwap_idx] - self.slippage
                        else:
                            _open_price = df[i][price_kind_idx] + df[i][spread_idx] / 2 * now_hold_num_state
                        
                        now_deal_pos_state = 1 if now_hold_num > 0 else -1
                        _open_value = _open_price * face_value * abs(now_hold_num)
                        _open_fee = _open_value * self.c_rate + self.c_value * abs(now_hold_num)
                        close_profit_this_min += face_value * abs(now_hold_num) * (close - _open_price) * now_deal_pos_state - _open_fee
                        

                        dealflag = 'S' if now_hold_num_state == 1 else 'B'
                        trade_dict[deal_count] = {'deal_count': deal_count, 'pos': np.sign(now_hold_num), 'dealflag':dealflag, 'deal_time': nowtime,
                                              'deal_price':_open_price,
                                              'deal_contract_num': abs(now_hold_num),'now_hold_num': now_hold_num,
                                              'target_pos_max': pre_target_pos_state * target_open_num_max,
                                              'target_pos_min': pre_target_pos_state * target_open_num_min,
                                              'target_pos': pre_target_pos,'pre_signal': pre_raw,
                                              'deal_value': _open_value, 'deal_fee': _open_fee,'deal_contract':HTSCSecurityID, 'deal_type':'yicang new contract'}
                        deal_count += 1


                        now_hold_num_profit = close_profit_this_min
                        _fee = close_fee + _open_fee
                        now_hold_num_profit -= _fee
                    else:
                        now_hold_num_profit = face_value * now_hold_num * (close - last_close)  # 此分钟收益
                else:
                    now_hold_num_profit = 0
                pnl_dict[nowtime] = now_hold_num_profit
                profit_intradeal += now_hold_num_profit
                
                
            elif trading_flag and (now_hold_num_abs < target_open_num_min) and open_flag and max_hold_time_flag == 0: # 开仓
                # 之前持仓的本分钟收益
                if now_hold_num != 0:
                    if yicang_flag:
                        if self.price_kind == 'buy_sell':
                            if now_hold_num_state == 1:
                                _close_price = self.data_origin.loc[(df[i][dt_idx], cont_old)]['Buy1Price'] - self.slippage
                            else:
                                _close_price = self.data_origin.loc[(df[i][dt_idx], cont_old)]['Sell1Price'] + self.slippage
                        else:
                            _close_price = cont_old_twap - self.data_origin.loc[(df[i][dt_idx], cont_old)]['spread'] / 2 * now_hold_num_state
                        
                        now_deal_pos_state = 1 if now_hold_num > 0 else -1
                        close_value = _close_price * face_value * abs(now_hold_num)
                        close_fee = close_value * self.c_rate + self.c_value * abs(now_hold_num)
                        close_profit_this_min = face_value * abs(now_hold_num) * (cont_old_twap - cont_old_pre_close) * now_deal_pos_state - close_fee
                        
                        dealflag = 'S' if now_hold_num_state == 1 else 'B'
                        trade_dict[deal_count] = {'deal_count': deal_count, 'pos': np.sign(now_hold_num), 'dealflag':dealflag, 'deal_time': nowtime,
                                              'deal_price':_close_price,
                                              'deal_contract_num': abs(now_hold_num),'now_hold_num': now_hold_num,
                                              'target_pos_max': pre_target_pos_state * target_open_num_max,
                                              'target_pos_min': pre_target_pos_state * target_open_num_min,
                                              'target_pos': pre_target_pos,'pre_signal': pre_raw,
                                              'deal_value': close_value, 'deal_fee': close_fee,'deal_contract':cont_old,'deal_type':'yicang old contract'}
                        deal_count += 1


                        if self.price_kind == 'buy_sell':
                            if now_hold_num_state == 1:
                                _open_price = df[i][sell_vwap_idx] + self.slippage
                            else:
                                _open_price = df[i][buy_vwap_idx] - self.slippage
                        else:
                            _open_price = df[i][price_kind_idx] + df[i][spread_idx] / 2 * now_hold_num_state
                        
                        now_deal_pos_state = 1 if now_hold_num > 0 else -1
                        _open_value = _open_price * face_value * abs(now_hold_num)
                        _open_fee = _open_value * self.c_rate + self.c_value * abs(now_hold_num)
                        close_profit_this_min += face_value * abs(now_hold_num) * (close - _open_price) * now_deal_pos_state - _open_fee
                        

                        dealflag = 'S' if now_hold_num_state == 1 else 'B'
                        trade_dict[deal_count] = {'deal_count': deal_count, 'pos': np.sign(now_hold_num), 'dealflag':dealflag, 'deal_time': nowtime,
                                              'deal_price':_open_price,
                                              'deal_contract_num': abs(now_hold_num),'now_hold_num': now_hold_num,
                                              'target_pos_max': pre_target_pos_state * target_open_num_max,
                                              'target_pos_min': pre_target_pos_state * target_open_num_min,
                                              'target_pos': pre_target_pos,'pre_signal': pre_raw,
                                              'deal_value': _open_value, 'deal_fee': _open_fee,'deal_contract':HTSCSecurityID, 'deal_type':'yicang new contract'}
                        deal_count += 1


                        now_hold_num_profit = close_profit_this_min
                        _fee = close_fee + _open_fee
                        now_hold_num_profit -= _fee
                    else:
                        now_hold_num_profit = face_value * now_hold_num * (close - last_close)  # 此分钟收益
                else:
                    now_hold_num_profit = 0
                    
                open_contract_num = min(target_open_num_min - now_hold_num_abs, self.open_num_permin)
                
                if self.filter_series is not None and open_contract_num > 0 and open_contract_num * now_hold_num >= 0:
                    if pre_target_pos_state != pre_filter_socre:
                        open_contract_num = 0
                        # print(open_contract_num, pre_target_pos_state, pre_filter_socre, nowtime, '!!!!!!!!!!!')
                    # if pre_target_pos_state == -1 and pre_filter_socre != -1:
                    #     open_contract_num = 0

                if open_contract_num == 0:
                    pnl_dict[nowtime] = now_hold_num_profit
                    profit_intradeal += now_hold_num_profit
                else:
                    open_value = open_price * face_value * open_contract_num
                    open_fee = open_value * self.c_rate + self.c_value * open_contract_num

                    now_hold_num += open_contract_num * pre_target_pos_state

                    now_hold_dealcount.append(deal_count)
                    # 记录下来本次开仓记录
   
                    dealflag = 'B' if pre_target_pos_state == 1 else 'S'
                    trade_dict[deal_count] = {'deal_count': deal_count, 'pos': np.sign(now_hold_num), 'dealflag':dealflag, 'deal_time': nowtime,
                                          'deal_price':open_price,
                                          'deal_contract_num': open_contract_num,'now_hold_num': now_hold_num,
                                          'target_pos_max': pre_target_pos_state * target_open_num_max,
                                          'target_pos_min': pre_target_pos_state * target_open_num_min,
                                          'target_pos': pre_target_pos,'pre_signal': pre_raw,
                                          'deal_value': open_value, 'deal_fee': open_fee,'deal_contract':HTSCSecurityID}
                

                    deal_count += 1
                    this_deal_nowprofit = face_value * open_contract_num * (close - open_price) * pre_target_pos_state
                    profit_thismin = this_deal_nowprofit - open_fee + now_hold_num_profit
                    pnl_dict[nowtime] = profit_thismin # 此分钟盈亏应为此分钟收益减去手续费
                    profit_intradeal += profit_thismin
                    
                    if (pre_hold_num == 0) and (now_hold_num != 0):
                        totaltrade_dict[totaldeal_count] = {'totaltrade_count':totaldeal_count,'pos':np.sign(now_hold_num),'open_time':nowtime, 'open_contract':HTSCSecurityID}
                
            pre_target_pos = target_pos
            pre_target_pos_state = target_pos_state
            pre_hold_num = now_hold_num
            if profit_intradeal < self.stop_loss:
                stop_loss_timelist.append(nowtime)
                stop_loss_flag = True
        
        if len(trade_dict) == 0:
            print('no trade')
            return

        trade_df = pd.DataFrame(trade_dict).T
        
        totaltrade_df = pd.DataFrame(totaltrade_dict).T

        totaltrade_df = totaltrade_df.sort_values('open_time')
        if totaltrade_df.iloc[-1]['close_time'] != totaltrade_df.iloc[-1]['close_time']:
            totaltrade_df = totaltrade_df[:-1]
        totaltrade_df['change'] = totaltrade_df.profit_intradeal / self.initial_cash
        totaltrade_df['equity_curve'] = totaltrade_df.change.cumsum()
        # totaltrade_df['holding_time'] = totaltrade_df.apply(lambda x: self.get_timediff_minutes(x.open_time, x.close_time), axis=1)
        
        pnl_df = pd.DataFrame(pnl_dict, index=['profit']).T
        pnl_df = pnl_df.reset_index()
        pnl_df.columns = ['dt', 'profit']
        pnl_df['change'] = pnl_df['profit'] / self.initial_cash
        pnl_df['equity_curve'] = (pnl_df['profit'].cumsum() + self.initial_cash) / self.initial_cash


        results, daily_return = self.strategy_evaluate(pnl_df.copy(), totaltrade_df.copy(), trade_df.copy())
        
        stop_loss_timelist.sort()
        stoplossdf = pd.DataFrame({'stop_loss_time':stop_loss_timelist})
        stoplossdf['date'] = stoplossdf.stop_loss_time.apply(lambda x:x.date())
        stoplossdf = stoplossdf.groupby('date').agg({'stop_loss_time':lambda x:x.head(1)})
        
        results.loc['止损次数'] = len(stoplossdf)
        daily_return.columns = ['daily_return', 'profit', 'daily_equty_curve', 'long_change', 'long_profit', 'short_change', 'short_profit']

        ic_lenth_list = [1,5,10,20,30,45,60,90,120,180,240,360,480]
        for p in ic_lenth_list:
            results.loc[f'IC_{p}'] = self.signal_df['raw'].corr(self.signal_df['close'].pct_change(p).shift(-(p+1)))
        results.loc['autocorr_60'] = self.signal_df['raw'].corr(self.signal_df['raw'].shift(60))

        pnl_df = pnl_df.set_index('dt')
        pnl = pnl_df[['equity_curve']] - 1
        pnl.columns = ['profit']

        trade_df = trade_df[['deal_count', 'pos', 'dealflag', 'deal_time', 'deal_price', 'deal_contract_num','now_hold_num',
                             'target_pos_max', 'target_pos_min', 'target_pos','pre_signal', 'deal_value', 'deal_fee','deal_contract', 'deal_type']]
        
        totaltrade_df = totaltrade_df[['totaltrade_count', 'pos',  'open_time', 'close_time', 'pos_close', 'profit_intradeal', 'change',
                                      'equity_curve', 'holding_time', 'open_contract', 'close_contract', 'max_position', 'blocked_money']]

        if self.save_path != None:
            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)
            if self.save_csv:
                totaltrade_df.to_csv(os.path.join(self.save_path, self.name_prefix + '_total_trade_detail.csv'), index=False)
                trade_df.to_csv(os.path.join(self.save_path, self.name_prefix + '_minute_trade_detail.csv'), index=False)
                pnl.to_csv(os.path.join(self.save_path, self.name_prefix + '_pnl.csv'))
                daily_return.to_csv(os.path.join(self.save_path, self.name_prefix + '_daily_return.csv'))
                results.to_csv(os.path.join(self.save_path, self.name_prefix + '_results.csv'), encoding='gbk')
                stoplossdf.to_csv(os.path.join(self.save_path, self.name_prefix + '_stop_loss_time.csv'), index=False)
            # daily_return['daily_equty_curve'].plot(figsize=(10, 5))
            # plt.title('profit', fontsize='large')
            # plt.savefig(os.path.join(self.save_path, self.name_prefix + 'profit.png'))
            draw_picture(daily_return, results['num'], pnl, self.save_path, self.name_prefix, self.initial_cash, self.show_image, self.save_image)

            
        return {'pnl':pnl, 'results':results, 'trade_df':trade_df, 'totaltrade_df':totaltrade_df, 'daily_return':daily_return}

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
        sharpedailyreturn = pnl.groupby('date')[['change', 'profit']].sum()#.to_frame()
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

        long_change = longtrade.groupby(longtrade['open_time'].dt.date)[['change', 'profit_intradeal']].sum()#.to_frame(name = 'long_change')
        long_change.columns = ['long_change', 'long_profit']
        long_change.index.name = 'date'
        short_change = shorttrade.groupby(shorttrade['open_time'].dt.date)[['change', 'profit_intradeal']].sum()#.to_frame(name = 'short_change')
        short_change.columns = ['short_change', 'short_profit']
        short_change.index.name = 'date'

        results.loc[0, '做多笔数'] = len(longtrade) 
        if len(longtrade) > 0: 
            results.loc[0, '做多胜率'] = format(len(longtrade[longtrade.change > 0]) / len(longtrade), '.2%')  # 胜率
        results.loc[0, '做空笔数'] = len(shorttrade)  
        if len(shorttrade) > 0:
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
        results.loc[0, '单笔最长持有时间'] = str(int(max_minutes)) #+ ' 分钟'  # 单笔最长持有时间

        min_minutes = trade['持仓时间'].min()
        results.loc[0, '单笔最短持有时间'] = str(int(min_minutes)) #+ ' 分钟'  # 单笔最短持有时间

        mean_minutes = trade['持仓时间'].mean()
        results.loc[0, '平均持仓周期'] = str(round(mean_minutes, 1))# + ' 分钟'  # 平均持仓周期

        # ===连续盈利亏算
        results.loc[0, '最大连续盈利笔数'] = max(
            [len(list(v)) for k, v in itertools.groupby(np.where(trade['change'] > 0, 1, np.nan))])  # 最大连续盈利笔数
        results.loc[0, '最大连续亏损笔数'] = max(
            [len(list(v)) for k, v in itertools.groupby(np.where(trade['change'] < 0, 1, np.nan))])  # 最大连续亏损笔数
        
        # trade_minute['date'] = trade_minute['open_time'].apply(lambda x:x.date())
        # daily_openvalue = trade_minute.groupby('date').agg({'open_value_intraday':lambda x:x.tail(1)})
        # results.loc[0, '平均每日杠杆'] = round(daily_openvalue.open_value_intraday.sum()/ len(sharpedailyreturn) / self.initial_cash, 2)
        # results.loc[0, '平均每日交易分钟数'] = round(trade_minute.groupby('date')['open_value_intraday'].count().mean(),1)

        if len(longtrade) > 0:
            results.loc[0, '做多收益'] = format(longtrade.change.sum(), '.4%')
            results.loc[0, '做多盈亏比'] = round(longtrade.loc[longtrade['change'] > 0]['change'].mean() / longtrade.loc[longtrade['change'] < 0]['change'].mean() * (-1), 2)  
        else:
            results.loc[0, '做多收益'] = np.nan
            results.loc[0, '做多盈亏比'] = np.nan
        if len(shorttrade) > 0:
            results.loc[0, '做空收益'] = format(shorttrade.change.sum(), '.4%')
            results.loc[0, '做空盈亏比'] = round(shorttrade.loc[shorttrade['change'] > 0]['change'].mean() / shorttrade.loc[shorttrade['change'] < 0]['change'].mean() * (-1), 2)  
        else:
            results.loc[0, '做空收益'] = np.nan
            results.loc[0, '做空盈亏比'] = np.nan
        results = results.T
        results.columns = ['num']
        return results, pd.concat([sharpedailyreturn, long_change, short_change], axis = 1).fillna(0)
    
    def get_timediff_minutes(self, a, b):
        m = (b - a).total_seconds() / 60
        return m

def draw_picture(daily_return, _result, _pnl, save_path, name, initial_cash, show_image, save_image):
    required_columns = ['daily_return', 'long_change', 'short_change']
    for col in required_columns:
        if col not in daily_return.columns:
            raise ValueError(f"Missing required column: {col}")

    daily_df = daily_return[required_columns].fillna(0).cumsum()
    daily_df.columns = ['Total', 'Long', 'Short']

    fig = plt.figure(figsize=(10, 10))

    ax1 = fig.add_subplot(2, 1, 1)
    ax1.spines['top'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)

    plt.text(0, 1.0, '%s report'%name, fontsize=22)

    text_fontsize = 16

    plt.text(0, 0.9, 'net value:  ' + str(_result.loc['累积净值']), fontsize=text_fontsize)
    plt.text(0, 0.8, 'sharpe:  '+ str(_result.loc['夏普比率']), fontsize=text_fontsize)
    plt.text(0, 0.7, 'annual ret:  '+ str(_result.loc['年化收益']), fontsize=text_fontsize)
    plt.text(0, 0.6, 'MDD:  '+ str(_result.loc['最大回撤']), fontsize=text_fontsize)
    plt.text(0, 0.5, 'MDD sdate: ' + str(_result.loc['最大回撤开始时间']), fontsize=text_fontsize)
    plt.text(0, 0.4, 'MDD edate: ' + str(_result.loc['最大回撤结束时间']), fontsize=text_fontsize)
    plt.text(0, 0.3, 'annual ret/mdd:  ' + str(_result.loc['年化收益/回撤比']), fontsize=text_fontsize)
    plt.text(0, 0.2, 'trade counts perday:  ' + str(_result.loc['平均每天交易笔数']), fontsize=text_fontsize)
    plt.text(0, 0.1, 'hold time per trade:  ' + str(_result.loc['平均持仓周期']).split(' ')[0], fontsize=text_fontsize)
    plt.text(0, 0, 'win ratio:  ' + str(_result.loc['胜率']), fontsize=text_fontsize)
    plt.text(0, -0.1, 'long ret:  ' + str(_result.loc['做多收益']), fontsize=text_fontsize)
    plt.text(0, -0.2, 'short ret:  ' + str(_result.loc['做空收益']), fontsize=text_fontsize)
    
    plt.text(0.5, 0.9, 'ret per trade:  ' + str(_result.loc['每笔交易平均盈亏']), fontsize=text_fontsize)
    plt.text(0.5, 0.8, 'profit win/loss: ' + str(_result.loc['盈亏收益比']), fontsize=text_fontsize)
    plt.text(0.5, 0.7, 'max profit one trade:  ' + str(_result.loc['单笔最大盈利']), fontsize=text_fontsize)
    plt.text(0.5, 0.6, 'max loss one trade:  ' + str(_result.loc['单笔最大亏损']), fontsize=text_fontsize)
    # plt.text(0.5, 0.5, 'average leverage:  ' + str(_result.loc['平均每日杠杆']), fontsize=text_fontsize)
    # plt.text(0.5, 0.4, 'average open value:  ' + '%.3e'%daily_df.open_value_intraday.mean(), fontsize=text_fontsize)
    # plt.text(0.5, 0.4, 'max open value:  ' + str(round(_result.loc['单日最大开仓金额'] / 1e8, 3))+'e8', fontsize=text_fontsize)
    # plt.text(0.5, 0.3, 'average trade minutes:  ' + str(_result.loc['平均每日交易分钟数']), fontsize=text_fontsize)
    plt.text(0.5, 0.5, 'initial cash:  ' + str(initial_cash / 1e8) + 'e8', fontsize=text_fontsize)
    # plt.text(0.5, 0.1, 'net ret per trade:  ' + str(_result.loc['平均每笔市值收益']), fontsize=text_fontsize)
    # plt.text(0.5, 0, 'net ret per day:  ' + str(_result.loc['平均每日市值收益']), fontsize=text_fontsize)
    plt.text(0.5, 0.4, 'long profit win/loss:  ' + str(_result.loc['做多盈亏比']), fontsize=text_fontsize)
    plt.text(0.5, 0.3, 'short profit win/loss:  ' + str(_result.loc['做空盈亏比']), fontsize=text_fontsize)
    # plt.text(0.5, -0.2, 'max trade counts perday:  ' + str(_result.loc['最大每天交易笔数']), fontsize=text_fontsize)


    plt.xticks([])  # 去掉x轴
    plt.yticks([])  # 去掉y轴

    plt.subplots_adjust(top=0.95, hspace=0)

    ax1 = fig.add_subplot(2, 1, 2)
    if len(daily_return) > 1:
        # 图：分组收益
        xlist = [x.strftime('%Y%m%d') for x in daily_df.index.tolist()]
        ylist = daily_df.values  # 获取所有三列的数据

        # 定义颜色列表
        colors = ['red', 'dodgerblue', 'green']
        labels = ['Total', 'Long', 'Short']

        for col, color, label in zip(['Total', 'Long', 'Short'], colors, labels):
            ax1.plot(np.arange(len(xlist)), daily_df[col], color=color, label=label)

        # 设置 x 轴刻度和标签
        step = max(len(xlist) // 8, 1)
        ax1.set_xticks(np.arange(0, len(xlist), step))
        ax1.set_xticklabels([xlist[i] for i in np.arange(0, len(xlist), step)], rotation=30)

        plt.ylabel('Return', fontsize='medium')
        plt.title('Daily Results', fontsize='large')
        plt.legend(loc='upper left', fontsize='medium')  # 添加图例

    else:
        _pnl.plot(ax = ax1)
        plt.title('profit', fontsize='large')

    plt.subplots_adjust(top=0.95, hspace=0.3)
    if save_image:
        plt.savefig(os.path.join(save_path, name + '.png'))
    if show_image:
        plt.show()
    plt.close()

def merge_evaluate(total_trade, total_daily_return, daily_return):
    trade = total_trade.sort_values(by = ['open_time'])
    ticker_num = len(total_trade.Ticker.unique())
    total_trade['date'] = total_trade['open_time'].apply(lambda x:x.date())
    daily_ticker_blocked_money = total_trade.groupby(['date', 'Ticker'])[['blocked_money']].max()
    daily_blocked_money = daily_ticker_blocked_money.groupby(['date'])['blocked_money'].sum()
    
    # ===新建一个dataframe保存回测指标
    results = pd.DataFrame()
    
    # ===计算累积净值
    results.loc[0, '累积净值'] = int(total_daily_return.sum())
    
    # 计算夏普比率
    sharpedailyreturn = total_daily_return.to_frame(name = 'change')
    sharpedailyreturn.index.name = 'date'
    sharpedailyreturn = sharpedailyreturn.reset_index()
    
    tradedays = len(sharpedailyreturn)
    sharpe_ratio = round(sharpedailyreturn['change'].mean() / sharpedailyreturn['change'].std() * np.sqrt(252), 3)
    results.loc[0, '夏普比率'] = sharpe_ratio
    
    # ===计算年化收益
    annual_return = (total_daily_return.sum()) * (
            '365 days 00:00:00' / (sharpedailyreturn['date'].iloc[-1] - sharpedailyreturn['date'].iloc[0]))
    
    results.loc[0, '年化收益'] = int(annual_return)
    
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
    results.loc[0, '最大回撤'] = round(max_draw_down, 0)
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
    results.loc[0, '平均每日持仓数量'] = round(daily_return['profit'].unstack().replace(0, np.nan).count(axis = 1).mean(), 1)
    results.loc[0, '交易品种数量'] = ticker_num
    results.loc[0, '最大日占资'] = int(daily_blocked_money.max())
    results.loc[0, '平均日占资'] = int(daily_blocked_money.mean())
    
    longtrade = trade[trade['pos'] == 1]
    shorttrade = trade[trade['pos'] == -1]
    results.loc[0, '做多笔数'] = len(longtrade) 
    if len(longtrade) > 0: 
        results.loc[0, '做多胜率'] = format(len(longtrade[longtrade.change > 0]) / len(longtrade), '.2%')  # 胜率
    results.loc[0, '做空笔数'] = len(shorttrade)  
    if len(shorttrade) > 0:
        results.loc[0, '做空胜率'] = format(len(shorttrade[shorttrade.change > 0]) / len(shorttrade), '.2%')  # 胜率
    
    
    results.loc[0, '每笔交易平均盈亏'] = int(trade['profit_intradeal'].mean())  # 每笔交易平均盈亏
    results.loc[0, '盈亏收益比'] = round(trade.loc[trade['change'] > 0]['profit_intradeal'].mean() / \
                                    trade.loc[trade['change'] < 0][
                                        'profit_intradeal'].mean() * (-1), 2)  # 盈亏比
    
    results.loc[0, '单笔最大盈利'] = int(trade['profit_intradeal'].max())  # 单笔最大盈利
    results.loc[0, '单笔最大亏损'] = int(trade['profit_intradeal'].min())  # 单笔最大亏损
    
    # ===统计持仓时间
    trade['持仓时间'] = trade['holding_time']
    max_minutes = trade['持仓时间'].max()
    results.loc[0, '单笔最长持有时间'] = str(int(max_minutes)) #+ ' 分钟'  # 单笔最长持有时间
    
    min_minutes = trade['持仓时间'].min()
    results.loc[0, '单笔最短持有时间'] = str(int(min_minutes)) #+ ' 分钟'  # 单笔最短持有时间
    
    mean_minutes = trade['持仓时间'].mean()
    results.loc[0, '平均持仓周期'] = str(round(mean_minutes, 1))# + ' 分钟'  # 平均持仓周期
    
    # ===连续盈利亏算
    results.loc[0, '最大连续盈利笔数'] = max(
        [len(list(v)) for k, v in itertools.groupby(np.where(trade['change'] > 0, 1, np.nan))])  # 最大连续盈利笔数
    results.loc[0, '最大连续亏损笔数'] = max(
        [len(list(v)) for k, v in itertools.groupby(np.where(trade['change'] < 0, 1, np.nan))])  # 最大连续亏损笔数
    
    if len(longtrade) > 0:
        results.loc[0, '做多收益'] = round(longtrade.profit_intradeal.sum(), 0)
        results.loc[0, '做多盈亏比'] = round(longtrade.loc[longtrade['change'] > 0]['profit_intradeal'].mean() / longtrade.loc[longtrade['change'] < 0]['profit_intradeal'].mean() * (-1), 2)  
    else:
        results.loc[0, '做多收益'] = np.nan
        results.loc[0, '做多盈亏比'] = np.nan
    if len(shorttrade) > 0:
        results.loc[0, '做空收益'] = round(shorttrade.profit_intradeal.sum(), 0)
        results.loc[0, '做空盈亏比'] = round(shorttrade.loc[shorttrade['change'] > 0]['profit_intradeal'].mean() / shorttrade.loc[shorttrade['change'] < 0]['profit_intradeal'].mean() * (-1), 2)  
    else:
        results.loc[0, '做空收益'] = np.nan
        results.loc[0, '做空盈亏比'] = np.nan
    results = results.T
    results.columns = ['num']
    return results

def merge_draw_picture(daily_return, _result, save_path, name, show_image, save_image):
    daily_df = daily_return.fillna(0).cumsum()
    
    fig = plt.figure(figsize=(10, 10))

    ax1 = fig.add_subplot(2, 1, 1)
    ax1.spines['top'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)

    plt.text(0, 1.0, '%s report'%name, fontsize=22)

    text_fontsize = 16

    plt.text(0, 0.9, 'net value:  ' + str(int(_result.loc['累积净值'])), fontsize=text_fontsize)
    plt.text(0, 0.8, 'sharpe:  '+ str(_result.loc['夏普比率']), fontsize=text_fontsize)
    plt.text(0, 0.7, 'annual ret:  '+ str(int(_result.loc['年化收益'])), fontsize=text_fontsize)
    plt.text(0, 0.6, 'MDD:  '+ str(_result.loc['最大回撤']), fontsize=text_fontsize)
    plt.text(0, 0.5, 'MDD sdate: ' + str(_result.loc['最大回撤开始时间'][:10]), fontsize=text_fontsize)
    plt.text(0, 0.4, 'MDD edate: ' + str(_result.loc['最大回撤结束时间'][:10]), fontsize=text_fontsize)
    plt.text(0, 0.3, 'annual ret/mdd:  ' + str(_result.loc['年化收益/回撤比']), fontsize=text_fontsize)
    plt.text(0, 0.2, 'trade counts perday:  ' + str(_result.loc['平均每天交易笔数']), fontsize=text_fontsize)
    plt.text(0, 0.1, 'hold time per trade:  ' + str(_result.loc['平均持仓周期']).split(' ')[0], fontsize=text_fontsize)
    plt.text(0, 0, 'win ratio:  ' + str(_result.loc['胜率']), fontsize=text_fontsize)
    plt.text(0, -0.1, 'long ret:  ' + str(int(_result.loc['做多收益'])), fontsize=text_fontsize)
    plt.text(0, -0.2, 'short ret:  ' + str(int(_result.loc['做空收益'])), fontsize=text_fontsize)
    
    plt.text(0.5, 0.9, 'ret per trade:  ' + str(_result.loc['每笔交易平均盈亏']), fontsize=text_fontsize)
    plt.text(0.5, 0.8, 'profit win/loss: ' + str(_result.loc['盈亏收益比']), fontsize=text_fontsize)
    plt.text(0.5, 0.7, 'max profit one trade:  ' + str(int(_result.loc['单笔最大盈利'])), fontsize=text_fontsize)
    plt.text(0.5, 0.6, 'max loss one trade:  ' + str(int(_result.loc['单笔最大亏损'])), fontsize=text_fontsize)
    plt.text(0.5, 0.5, 'max hold time:  ' + str(_result.loc['单笔最长持有时间']), fontsize=text_fontsize)
    plt.text(0.5, 0.4, 'long profit win/loss:  ' + str(_result.loc['做多盈亏比']), fontsize=text_fontsize)
    plt.text(0.5, 0.3, 'short profit win/loss:  ' + str(_result.loc['做空盈亏比']), fontsize=text_fontsize)
    plt.text(0.5, 0.2, 'max blocked money:  ' + str(int(_result.loc['最大日占资'])), fontsize=text_fontsize)
    plt.text(0.5, 0.1, 'mean blocked money:  ' + str(int(_result.loc['平均日占资'])), fontsize=text_fontsize)
    plt.text(0.5, 0.0, 'daily hold ticker num:  ' + str(_result.loc['平均每日持仓数量']), fontsize=text_fontsize)
    plt.text(0.5, -0.1, 'trade ticker num:  ' + str(int(_result.loc['交易品种数量'])), fontsize=text_fontsize)

    plt.xticks([])  # 去掉x轴
    plt.yticks([])  # 去掉y轴

    plt.subplots_adjust(top=0.95, hspace=0)

    ax1 = fig.add_subplot(2, 1, 2)

        # 图：分组收益
    xlist = [x.strftime('%Y%m%d') for x in daily_df.index.tolist()]
    ylist = daily_df.values  # 获取所有三列的数据

    # 定义颜色列表
    colors = ['red', 'dodgerblue', 'green']
    labels = ['Total', 'Long', 'Short']

    for col, color, label in zip(['Total', 'Long', 'Short'], colors, labels):
        ax1.plot(np.arange(len(xlist)), daily_df[col], color=color, label=label)

    # 设置 x 轴刻度和标签
    step = max(len(xlist) // 8, 1)
    ax1.set_xticks(np.arange(0, len(xlist), step))
    ax1.set_xticklabels([xlist[i] for i in np.arange(0, len(xlist), step)], rotation=30)

    plt.ylabel('Profit', fontsize='medium')
    plt.title('Daily Results', fontsize='large')
    plt.legend(loc='upper left', fontsize='medium')  # 添加图例

    plt.subplots_adjust(top=0.95, hspace=0.3)
    if save_image:
        os.makedirs(save_path, exist_ok=True)
        plt.savefig(os.path.join(save_path, name + '.png'))
    if show_image:
        plt.show()
    plt.close()

import pickle
def save_pickle(save_dict,save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
    return 

def merge_results(pkl_path, save_path, name, show_image, save_image, save_results):
    pkl_results = pd.read_pickle(pkl_path)
    total_daily_return_list = []
    total_results_list = []
    total_trade_list = []
    for ticker in pkl_results.keys():
        reskey = pkl_results[ticker]
        if reskey is None:
            continue
        daily_return = reskey['daily_return']['daily_return'].to_frame(name = ticker)
        total_daily_return_list.append(daily_return)
    
        total_trade_list.append(reskey['totaltrade_df'])   
        total_results_list.append(reskey['results']['num'].to_frame(name = ticker))
    
    total_results = pd.concat(total_results_list, axis = 1)
    total_trade = pd.concat(total_trade_list, axis = 0)
    
    total_daily_return = pd.concat(total_daily_return_list, axis = 1).fillna(0)
    total_daily_return.index = pd.to_datetime(total_daily_return.index)
    total_daily_return = total_daily_return.sort_index().mean(axis = 1)
    
    ticker_num = len(total_daily_return_list)
    
    _result = merge_evaluate(total_trade, total_daily_return, ticker_num)
    
    daily_return = total_daily_return.to_frame(name = 'change')
    daily_return['daily_equty_curve'] = daily_return['change'].cumsum()
    
    merge_draw_picture(daily_return, _result['num'], save_path, name, show_image, save_image)
    results = {'daily_return':daily_return, 'results':_result, 'total_results':total_results}
    if save_results:
        os.makedirs(save_path, exist_ok=True)
        save_pickle(results, os.path.join(save_path, f'{name}_result.pkl'))
    return results

def merge_all(base_path, save_path, ticker_list = None, name = 'A.A.A Merge', show_image = True, save = True):
    if save:
        os.makedirs(save_path, exist_ok=True)
    if ticker_list is None:
        ticker_list = os.listdir(base_path)

    daily_ret_list = []
    total_trade_list = []
    for ticker in ticker_list:
        if ticker.split('.')[-1] not in ['SHF', 'ZCE', 'INE', 'GFE', 'CFE', 'DCE', 'CZC']:
            continue
        daily_ret_ticker = pd.read_csv(os.path.join(base_path, ticker, f'{ticker}_daily_return.csv'), index_col=0, parse_dates=True)
        daily_ret_ticker.index.name = 'dt'
        daily_ret_ticker['Ticker'] = ticker
        daily_ret_ticker = daily_ret_ticker.set_index('Ticker', append = True)
        total_trade_ticker = pd.read_csv(os.path.join(base_path, ticker, f'{ticker}_total_trade_detail.csv'), parse_dates=['open_time', 'close_time'])
        total_trade_ticker['Ticker'] = ticker
        total_trade_ticker = total_trade_ticker.set_index(['Ticker', 'open_time'])
        daily_ret_list.append(daily_ret_ticker)
        total_trade_list.append(total_trade_ticker)
        if save:
            shutil.copy2(os.path.join(base_path, ticker, f'{ticker}.png'), os.path.join(save_path, f'{ticker}.png'))

    daily_df2 = pd.concat(daily_ret_list).sort_index()
    trade_df2 = pd.concat(total_trade_list)

    total_trade = trade_df2.reset_index()

    total_daily_return = daily_df2['profit'].unstack().sum(axis = 1)
    total_daily_long_return = daily_df2['long_profit'].unstack().sum(axis = 1)
    total_daily_short_return = daily_df2['short_profit'].unstack().sum(axis = 1)

    daily_return = pd.concat([total_daily_return, total_daily_long_return, total_daily_short_return], axis = 1)
    daily_return.columns = ['Total', 'Long', 'Short']

    ticker_num = len(total_trade.Ticker.unique())

    results = merge_evaluate(total_trade, total_daily_return, daily_df2)
    if save:
        results.to_csv(os.path.join(save_path, f'{name}_results.csv'))
        daily_return.to_csv(os.path.join(save_path, f'{name}_daily_return.csv'))
        daily_df2.to_csv(os.path.join(save_path, f'{name}_daily_df.csv'))
        trade_df2.to_csv(os.path.join(save_path, f'{name}_trade_df.csv'))
    merge_draw_picture(daily_return, results['num'], save_path, name, show_image, save)

    return {'results':results, 'daily_return':daily_return, 'daily_df':daily_df2, 'trade_df': trade_df2}

# trade_df = pd.read_hdf('/dfs/group/800466/warehouse/test/alpha/CHINA_COMMODITIES/1MIN/trade_df.h5')
# daily_df = pd.read_hdf('/dfs/group/800466/warehouse/test/alpha/CHINA_COMMODITIES/1MIN/daily_df.h5')

# total_daily_return = daily_df['dailyret'].unstack().mean(axis = 1)#.cumsum().plot()
# ticker_num = len(daily_df.index.get_level_values(1).unique().tolist())
# ticker_num = trade_df.perret.sum() / total_daily_return.sum()

# total_trade = trade_df.reset_index().rename(columns = {'intime':'open_time', 'perret':'change', 'hds':'holding_time'})

# daily_return = total_daily_return.to_frame(name = 'daily_ret')
# daily_return['daily_equty_curve'] = daily_return['daily_ret'].cumsum()

# results = merge_evaluate(total_trade, total_daily_return, ticker_num)
# merge_draw_picture(daily_return, results['num'], None, 'daily result', True, False)


# 如下为最初调试框架做数据的样例，框架定稿后可以删除


# data = IO.read_data(columns = ['close', 'twap', 'Buy1Price_mean', 'Sell1Price_mean', 'tday'], alt = f'/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/MD/{data_freq}MIN/PER_TICKER/{ticker}.h5')

# minute_tay = data.groupby('dt')[['tday']].first(1)
# minute_tay['tday'] = minute_tay['tday'].astype('int')

# ref_all = pd.read_pickle('/data/user/016700/Data/Factors/TEMP/commodities/minute_backtest_reference_15min.pkl')
# ref = ref_all[ticker]
# ref['contract'] = ref['contract'].astype(str).str.replace('.CZC', '.ZCE').replace('CZC', 'ZCE')

# ref = ref.join(minute_tay, how = 'left')
# univ = pd.read_hdf('/data/user/020529/share/commodity_research/temp/universe/universe_amt3000w.h5')
# univ = univ[ticker].to_frame(name = 'filter').reset_index()
# df = ref.reset_index().merge(univ, left_on='tday', right_on='tday', how='left').set_index('dt')
# df['close'] = df['twap']
# df = sig.to_frame(name = 'raw').fillna(0).join(df, how = 'left')

# ccp = pd.read_csv('/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/INFO/WIND_CFuturesContPro.csv')
# ccp = ccp[['S_INFO_CEMULTIPLIER','S_INFO_DMEAN',  'S_INFO_PUNIT',  'S_INFO_WINDCODE']]
# ccp = ccp.rename(columns = {'S_INFO_WINDCODE':'Ticker'})
# ccp['multiplier'] = ccp['S_INFO_CEMULTIPLIER'].fillna(ccp['S_INFO_PUNIT'])
# ccp = ccp.set_index('Ticker')
# multiplier_dict = ccp['multiplier'].to_dict()

# df['multiplier'] = df['contract'].apply(lambda x:multiplier_dict[x]).fillna(method = 'ffill')
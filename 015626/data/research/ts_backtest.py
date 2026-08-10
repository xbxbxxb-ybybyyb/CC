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

    def __init__(self, signal_df, ticker='IC.CFE', price_kind='vwap', pos_dict = {(0, 0.4): (0.0, 0.0),
                                                                                 (0.4, 0.5): (0.0, 0.2/3),
                                                                                 (0.5, 0.6): (0.2/3, 0.4/3),
                                                                                 (0.6, 0.7): (0.4/3, 0.6/3),
                                                                                 (0.7, 0.8): (0.6/3, 0.8/3),
                                                                                 (0.8, 0.9): (0.8/3, 1.0/3),
                                                                                 (0.9, 1.01): (1.0/3, 1.0/3)},
                 stop_profit=100,
                 stop_loss=-100, open_num_permin=30, close_num_permin=30, deal_volume_ratio = 0,
                 initial_cash=1000000, leverge = 1, c_rate=0.0004, slippage=0.006, minimum_trading_unit = 0.001,
                 std_filter_threshold = -100,
                 save_path='/data/user/', name_prefix=''):
        """ ！！！！！！！！！！！！！！ 默认参数的信号值在[-1,1]之间 ！！！！！！！！！！！
        :param signal_df: 信号dataframe，index为分钟，如果只有一列，则认为此列为信号值，读取行情数据进行测试。
                            如果多列，则第一列需为信号值，在函数内读取行情数据
                            测试时不对信号值做任何处理，使用原始值。
        :param ticker: 交易品种，
        :param price_kind: 使用下一分钟的哪个字段作为买入卖出价格，默认vwap
        :param pos_dict: 信号对应的仓位，信号一定要围绕0左右对称
        :param data_kind: 测试用数据类型 期货数据future还是指数数据spot还是etf
        :param signal_down_t: 信号值从当前持仓周期内最大回撤阈值
        :param profit_down_t: 收益从当前持仓周期内最大回撤阈值
        :param signal_inout_diff: 刚开仓在min_holding_period内允许信号波动的幅度，如0.5进场，理论出场阈值为0.5，
                                  但可在min_holding_period内出场阈值设为0.4
        :param stop_profit: 止盈
        :param stop_loss: 止损
        
        :param initial_cash: 初始资金
        :param c_rate: 交易费用
        :param slippage: 交易价格滑点
        :param hour_t: 表示几点
        :param minute_t: 几分后不开仓，默认是14:30后不开仓，只平仓
        :param save_path: 结果保存路径
        :param name_prefix: 结果csv命名前缀
        :param minimum_trading_unit: 最小交易单位
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
        self.stop_profit = stop_profit
        self.stop_loss = stop_loss * initial_cash
        self.open_num_permin = open_num_permin
        self.close_num_permin = close_num_permin
        self.deal_volume_ratio = deal_volume_ratio
        self.initial_cash = initial_cash
        self.leverge = leverge
        self.c_rate = c_rate
        self.slippage = slippage
        self.minimum_trading_unit_num = 1 / minimum_trading_unit

        self.std_filter_threshold = std_filter_threshold

        self.face_value = 1
        self.save_path = save_path
        self.name_prefix = name_prefix


        columns_list = self.signal_df.reset_index().columns.tolist()
        global dt_idx, raw_idx, std_signal_idx, open_idx, close_idx ,low_idx ,vwap_idx ,twap_idx ,volume_idx ,amount_idx ,price_kind_idx 
        dt_idx = columns_list.index('dt')
        raw_idx = columns_list.index('raw')
        std_signal_idx = columns_list.index('std_signal')
        # open_idx = columns_list.index('open')
        close_idx = columns_list.index('close')
        # high_idx = columns_list.index('high')
        # low_idx = columns_list.index('low')
        # vwap_idx = columns_list.index('vwap')
        # twap_idx = columns_list.index('twap')
        volume_idx = columns_list.index('volume_deal')
        # amount_idx = columns_list.index('amount')
        price_kind_idx = columns_list.index(price_kind)

    def back_test(self):
        df = self.signal_df.reset_index().values

        raw = df[0][raw_idx]
        filter_socre = df[0][std_signal_idx]
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

        pos_price = np.nan # 用于计算仓位的价格

        for i in tqdm(range(1, length)):
            nowtime = df[i][dt_idx]

            close = df[i][close_idx]
            last_close = df[i-1][close_idx]  # 上一分钟收盘价

            pre_raw = raw
            raw = df[i][raw_idx]

            pre_filter_socre = filter_socre
            filter_socre = df[i][std_signal_idx]
            open_flag = True if filter_socre >= self.std_filter_threshold else False

            # 当每分钟最大成交数量占此分钟成交量的百分比大于0时，更新每分钟最大平仓数量
            if self.deal_volume_ratio > 0:
                self.open_num_permin = max(round(np.floor(df[i][volume_idx] * 1 / self.minimum_trading_unit * self.deal_volume_ratio) / (1 / self.minimum_trading_unit), len(str(self.minimum_trading_unit)) - 2), self.minimum_trading_unit)
                self.close_num_permin = self.open_num_permin

            now_hold_num_state = np.sign(now_hold_num)
            now_hold_num_abs = abs(now_hold_num)

            target_pos = self.get_target_pos_from_signal(raw)
            target_pos_state = np.sign(raw)
            open_price = df[i][price_kind_idx] + self.slippage * pre_target_pos_state
            if now_hold_num == 0:
                pos_price = open_price
                stop_loss_flag = False

            target_open_num_max = np.floor(self.initial_cash * self.leverge * max(pre_target_pos)  / (self.face_value * pos_price) * self.minimum_trading_unit_num) / self.minimum_trading_unit_num
            target_open_num_min = np.floor(self.initial_cash * self.leverge * min(pre_target_pos)  / (self.face_value * pos_price) * self.minimum_trading_unit_num) / self.minimum_trading_unit_num
            if min(pre_target_pos) > min(maxposition_intradeal):
                maxposition_intradeal = pre_target_pos

            #如果当前持仓方向与上一分钟开仓信号方向不一致，先平仓。或者当前持仓大于目标持仓上限，需平仓
            if (stop_loss_flag and (now_hold_num!=0)) or \
             (now_hold_num_state * pre_target_pos_state == -1) or (now_hold_num_abs > target_open_num_max):
                
                if stop_loss_flag and (now_hold_num!=0):
                    close_contract_num = min(now_hold_num_abs, self.close_num_permin)
                elif now_hold_num_state * pre_target_pos_state == -1:
                    close_contract_num = min(now_hold_num_abs, self.close_num_permin)
                elif now_hold_num_abs > target_open_num_max:
                    close_contract_num = min(now_hold_num_abs - target_open_num_max, self.close_num_permin)
                
                close_price = df[i][price_kind_idx] - self.slippage * now_hold_num_state
                close_profit_this_min = 0

                while (close_contract_num > 0):
                    if len(now_hold_dealcount) == 0:
                        break
                    wait_close_dealcount = now_hold_dealcount[-1]
                    nowdeal_wait_close_info = trade_dict[wait_close_dealcount]
                    now_deal_pos_state = nowdeal_wait_close_info['pos']
                    now_deal_already_close_num = nowdeal_wait_close_info['close_contract_num']
                    nowdeal_wait_close_num = nowdeal_wait_close_info['open_contract_num'] - now_deal_already_close_num
                    this_deal_close_num = min(nowdeal_wait_close_num, close_contract_num)

                    close_value = close_price * self.face_value * this_deal_close_num
                    close_fee = close_value * self.c_rate
                    thisdeal_thismin_profit = self.face_value * this_deal_close_num * (close_price - last_close) * now_deal_pos_state - close_fee
                    close_profit_this_min += thisdeal_thismin_profit

                    trade_dict[wait_close_dealcount].update({'close_time': nowtime, 'close_price': close_price,
                                                             'close_contract_num': this_deal_close_num + now_deal_already_close_num})
                    now_hold_num -= (this_deal_close_num * now_deal_pos_state)

                    if nowdeal_wait_close_num > close_contract_num:
                        break
                    if nowdeal_wait_close_num == close_contract_num:
                        now_hold_dealcount.remove(wait_close_dealcount)
                        break
                    if nowdeal_wait_close_num < close_contract_num:
                        now_hold_dealcount.remove(wait_close_dealcount)
                        close_contract_num -= nowdeal_wait_close_num

                if now_hold_num != 0:
                    now_hold_num_profit = self.face_value * now_hold_num * (close - last_close)  # 此分钟收益
                else:
                    now_hold_num_profit = 0
                
                profit_thismin = close_profit_this_min + now_hold_num_profit
                pnl_dict[nowtime] = profit_thismin
                profit_intradeal += profit_thismin
                
                if (pre_hold_num != 0) and (now_hold_num == 0):
                    totaltrade_dict[totaldeal_count].update({'pos_close':np.sign(pre_hold_num),'close_time':nowtime,'profit_intradeal':profit_intradeal,'max_position':maxposition_intradeal})
                    profit_intradeal = 0
                    maxposition_intradeal = (0,0)
                    totaldeal_count += 1
                

            elif (now_hold_num_abs >= target_open_num_min) and (now_hold_num_abs <= target_open_num_max) or not open_flag:
                # 之前持仓的本分钟收益
                if now_hold_num != 0:
                    now_hold_num_profit = self.face_value * now_hold_num * (close - last_close)  # 此分钟收益
                else:
                    now_hold_num_profit = 0
                pnl_dict[nowtime] = now_hold_num_profit
                profit_intradeal += now_hold_num_profit
                
                
            elif (now_hold_num_abs < target_open_num_min) and open_flag: # 开仓
                # 之前持仓的本分钟收益
                if now_hold_num != 0:
                    now_hold_num_profit = self.face_value * now_hold_num * (close - last_close)  # 此分钟收益
                else:
                    now_hold_num_profit = 0
                    
                open_contract_num = min(target_open_num_min - now_hold_num_abs, self.open_num_permin)

                open_value = open_price * self.face_value * open_contract_num
                open_fee = open_value * self.c_rate

                now_hold_num += open_contract_num * pre_target_pos_state

                now_hold_dealcount.append(deal_count)
                # 记录下来本次开仓记录
                trade_dict[deal_count] = {'deal_count': deal_count, 'pos': pre_target_pos_state, 'open_time': nowtime,
                                          'open_price': open_price,
                                          'open_contract_num': open_contract_num, 'now_hold_num': now_hold_num,
                                          'target_pos_max': pre_target_pos_state * target_open_num_max,
                                          'target_pos_min': pre_target_pos_state * target_open_num_min,
                                          'target_pos': pre_target_pos,
                                          'open_signal': pre_raw,
                                          'open_value': open_value, 'open_fee': open_fee,
                                          'now_hold_dealcount': str(now_hold_dealcount),
                                          'close_time': None, 'close_price': None,
                                          'close_contract_num': 0, 'net_value': None, 'out_threshold': None,
                                          'max_signal': None, 'pre_signal': None, 'now_signal': None}

                deal_count += 1
                this_deal_nowprofit = self.face_value * open_contract_num * (close - open_price) * pre_target_pos_state
                profit_thismin = this_deal_nowprofit - open_fee + now_hold_num_profit
                pnl_dict[nowtime] = profit_thismin # 此分钟盈亏应为此分钟收益减去手续费
                profit_intradeal += profit_thismin
                
                if (pre_hold_num == 0) and (now_hold_num != 0):
                    totaltrade_dict[totaldeal_count] = {'totaltrade_count':totaldeal_count,'pos':np.sign(now_hold_num),'open_time':nowtime}
                
            pre_target_pos = target_pos
            pre_target_pos_state = target_pos_state
            pre_hold_num = now_hold_num
            
            if profit_intradeal < self.stop_loss:
                stop_loss_timelist.append(nowtime)
                stop_loss_flag = True
           
        trade_df = pd.DataFrame(trade_dict).T
        
        totaltrade_df = pd.DataFrame(totaltrade_dict).T

        totaltrade_df = totaltrade_df.sort_values('open_time')
        if totaltrade_df.iloc[-1]['close_time'] != totaltrade_df.iloc[-1]['close_time']:
            totaltrade_df = totaltrade_df[:-1]
        totaltrade_df['change'] = totaltrade_df.profit_intradeal / self.initial_cash
        totaltrade_df['equity_curve'] = totaltrade_df.change.cumsum()
        totaltrade_df['holding_time'] = totaltrade_df.apply(lambda x: self.get_timediff_minutes(x.open_time, x.close_time), axis=1)
        
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
        daily_return.columns = ['daily_return','daily_equty_curve']

        pnl_df = pnl_df.set_index('dt')
        pnl = pnl_df[['equity_curve']] - 1
        pnl.columns = ['profit']

        trade_df = trade_df[
            ['deal_count', 'pos', 'open_time', 'open_price', 'open_contract_num', 'now_hold_num', 
             'target_pos_max','target_pos_min','target_pos',
             'open_signal', 'now_hold_dealcount', 'close_time', 'close_price',
             'close_contract_num', 'net_value', 'out_threshold', 'max_signal', 'pre_signal', 'now_signal']]
        
        totaltrade_df = totaltrade_df[['totaltrade_count', 'pos',  'open_time', 'close_time', 'pos_close', 'profit_intradeal', 'change',
                                      'equity_curve', 'holding_time','max_position']]

        
        
        if self.save_path != None:
            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)
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
            if self.data_kind == 'future':
                md = IO.read_data([start_time, end_time], columns=['open', 'high', 'low', 'close', 'vwap','volume','twap'],
                                  alt='/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_SIF_TICK_TO_MINUTE_RECENT_MONTH.h5')
                md = md.xs(self.ticker, level=1)
                df = self.signal_df.join(md, how='inner')
            elif self.data_kind == 'spot':
                md = IO.read_data([start_time, end_time], columns=['open_spot', 'high_spot', 'low_spot', 'close_spot','volume_spot'],
                                  alt='/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_STOCK_INDEX_SPOT_MINUTE.h5')
                md.columns = ['open', 'high', 'low', 'close','volume']
                spot_twap = pd.read_hdf('/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/TWAP_SPOT.h5')
                spot_twap.columns = ['twap']
                md = md.join(spot_twap, how = 'left')
                md = md.xs(self.ticker, level=1)
                if self.ticker == 'IM.CFE':
                    twap_fake = pd.read_hdf('/data/user/017024/share/vars/for_cf/future_twap_im_interpolation.h5').to_frame()
                    twap_fake.columns = ['twap_fake']
                    md = md.join(twap_fake, how = 'left')
                df = self.signal_df.join(md, how='inner')
            elif self.data_kind == 'etf':
                md = IO.read_data([start_time, end_time], columns=['open', 'high', 'low', 'close','volume','amount'],
                                  alt='/data/user/015626/data/share/MD/CHINA_FUND/MINUTE/MD_CHINA_ETF_MINUTE.h5')
                md = md.xs(self.ticker, level=1)
                md['vwap'] = (md['amount'] / md['volume']).replace([np.inf, -np.inf, 0], np.nan).fillna(method = 'ffill')
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
        t = t.sort_index()
        t = t.reset_index()
        t['date'] = t['dt'].apply(lambda x: x.date())
        # 将每天数据的第一条以及后两条设置为0,确保不持隔夜仓
        alist = t.groupby('date').apply(lambda x: x.dt.iloc[0]).tolist()
        blist = t.groupby('date').apply(lambda x: x.dt.iloc[-8:]).tolist()
        t.loc[t.dt.isin(alist), 'raw'] = 0
        t.loc[t.dt.isin(blist), 'raw'] = 0
        t.drop(['date'], axis=1, inplace=True)
        t = t.set_index('dt')

        df = t.sort_index()
        df = df.reset_index()
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

#         # ===计算最大回撤
#         # 计算当日之前的资金曲线的最高点
#         pnl['max2here'] = pnl['equity_curve'].expanding().max()
#         # 计算到历史最高值到当日的跌幅，drowdwon
#         #     pnl['dd2here'] = pnl['equity_curve'] / pnl['max2here'] - 1
#         pnl['dd2here'] = pnl['equity_curve'] - pnl['max2here']
#         # 计算最大回撤，以及最大回撤结束时间
#         end_date, max_draw_down = tuple(pnl.sort_values(by=['dd2here']).iloc[0][['dt', 'dd2here']])
#         # 计算最大回撤开始时间
#         start_date = pnl[pnl['dt'] <= end_date].sort_values(by='equity_curve', ascending=False).iloc[0][
#             'dt']
#         # 将无关的变量删除
#         pnl.drop(['max2here', 'dd2here'], axis=1, inplace=True)
#         results.loc[0, '最大回撤'] = format(max_draw_down, '.2%')
#         results.loc[0, '最大回撤开始时间'] = str(start_date)
#         results.loc[0, '最大回撤结束时间'] = str(end_date)
        
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
        return results, sharpedailyreturn
    
    def get_timediff_minutes(self, a, b):
        m = (b - a).total_seconds() / 60
        return m


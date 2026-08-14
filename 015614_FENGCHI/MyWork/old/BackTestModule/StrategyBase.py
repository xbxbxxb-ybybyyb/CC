from Position import Position
from Record import Record
from abc import abstractmethod
from Broker import Broker
from dataApi.dividend import *
from Evaluation_helper import *
from config import *
import datetime
import copy
from xquant.strategy.backtest.Performance import *
import time
from xquant.factordata import FactorData
import os
import pandas as pd
import tqdm
s = FactorData()

def get_intraday_bar_list(date):
    # date = 20160104

    intraday_bar_list = [date*10000+925]
    for H in [9,10,11,13,14]:
        for m in range(60):
            if H ==9 and m<30:
                continue
            if H==11 and m>29:
                continue
            temp_bar = H*100 + m
            intraday_bar_list.append(date*10000+temp_bar)
    intraday_bar_list.append(date*10000+1500)
    return intraday_bar_list
class StrategyBase:
    """
    策略基类
    通过继承基类并重定义bar_handle()函数和daily_update函数来定义一个新的策略
    """
    def __init__(self,start:int,end:int,initial_cash:float,universe:list, benchmark = 'ZZ500',cost_rate = 0.0012, slippage=0.001):
        self.start = start #策略起始时间
        self.end = end #策略结束时间
        self.universe = universe #股票池
        self.available_stk = []
        self.benchmark = benchmark
        self.date_list = s.tradingday(str(start)[:8],str(end)[:8], \
                               frequency='DAY', dayType=None, dateType='TRADINGDAYS') #交易bar列表
        self.date_list = list(map(int,self.date_list))
        self.cost_rate = cost_rate #交易成本
        self.record = Record() #回测记录 Record对象
        self.position = Position(initial_cash) #实时仓位记录
        # self.position.holding = {stk:0 for stk in self.universe}
        self.slippage = slippage #滑点成本
        self.broker = Broker(int(self.date_list[0]),self.universe)#交易所
        self.evaluation_result = pd.DataFrame(index=[0])
        self.benchmark_net = load_minutes_data(self.benchmark, self.date_list, 'index')
        self.benchmark_net = self.benchmark_net[['close']].rename(columns={'close':self.benchmark})
        self.running_time = {}

    # @abstractmethod
    # def bar_handle(self,date_time,position):
    #     """
    #     策略逻辑函数
    #     :param date_time:bar的时间戳
    #     :return: 买卖信号的 order_list
    #     """
    # @abstractmethod
    def daily_update(self,date):
        """
        每天(月)更新股票池和对象中的数据
        更新broker数据
        :return:
        """
        self.broker.dataflow.update_date(date)
        self.position.new_day()
        available_stk = s.stock_filter(self.universe, str(date), 'SSO')  # 开盘涨跌停、停牌、STSP剔除
        if len(available_stk) == 0:
            self.available_stk = []
        else:
            self.available_stk = available_stk['stock'].apply(lambda x: int(x[:-3])).tolist()
        """
        权息信息待处理
        """
        stk_list = [x for x in self.position.holding]
        dividend_info = EXRightDividend[EXRightDividend['date']==date]
        dividend_info = dividend_info[dividend_info['code'].isin(self.position.holding)]
        if len(dividend_info)!=0:
            print(date,'dividend')
            dividend_info = dividend_info.set_index('code')
            self.position.deal_with_dividend(dividend_info)

    def run_strategy(self,bar_handle):
        """
        执行策略
        :return: 策略执行后的记录
        """
        e0 = e = time.time()
        self.record = Record()
        bar = tqdm.tqdm(self.date_list)
        for date in bar:
            bar.set_description('BackTesting %s'%str(date))
            # print(date, time.time() - e)
            self.daily_update(date)
            intraday_bar_list = get_intraday_bar_list(date)
            for date_time in intraday_bar_list:
                self.record.add_log_position(self.position, date_time)
                order_list = bar_handle(date_time, self.position)
                deal_info = self.broker.deal_with_order(order_list, self.position)
                self.record.add_log_order_info(order_list, deal_info)
                ################
        self.running_time['Backtest Time'] = time.time() - e0
        print('Backtest Time(s):',self.running_time['Backtest Time'] )
        e0 = time.time()
        self.record.processing(self.benchmark_net[self.benchmark_net.columns[0]])
        self.running_time['Record Processing Time'] = time.time()-e0
        print('processing(s):', self.running_time['Record Processing Time'])
        e0 = time.time()
        self.evaluation()
        self.running_time['Evaluation Time'] = time.time() - e0
        print('evaluation:',self.running_time['Evaluation Time'])
        self.running_time['Total Strategy'] = time.time() - e
        return self.record,self.evaluation_result

    def evaluation(self):
        benchmark_net = self.benchmark_net.rename(
            index={x: datetime.datetime.strptime(str(x), '%Y%m%d%H%M%S') for x in self.benchmark_net.index})
        benchmark_net = benchmark_net.resample('1d').last().dropna()
        benchmark_net = benchmark_net.rename(index={x: int(x.strftime('%Y%m%d')) for x in benchmark_net.index})
        net_value = self.record.net_value.rename(
            index={x: datetime.datetime.strptime(str(x), '%Y%m%d%H%M%S') for x in self.record.net_value.index})
        net_value = net_value.resample('1d').last().dropna()
        net_value = net_value.rename(index={x: int(x.strftime('%Y%m%d')) for x in net_value.index})
        self.evaluation_result = get_net_value_evaluation(net_value, benchmark_net)
        if len(self.record.signal_records_evaluation)>0:
            self.evaluation_result = self.evaluation_result.T
            self.evaluation_result['mean profit each holding'] = self.record.signal_records_evaluation['profit'].mean()
            self.evaluation_result['mean excess profit each holding'] = self.record.signal_records_evaluation['excess profit'].mean()
            self.evaluation_result = self.evaluation_result.T
        return self.evaluation_result

    def output_result(self,path,file_name):
        self.evaluation_result.to_excel(path+file_name+'.xlsx')
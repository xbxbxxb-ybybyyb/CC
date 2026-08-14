import datetime
import json
import os
import sys
import traceback
import warnings
from abc import abstractmethod

import pandas as pd
from PythonStrategy import PythonStrategy
from StrategyState import StrategyState

sys.path.append(os.path.abspath(os.path.abspath(__file__) + "/.."))

from TimeEventHandler import TimeEventHandler
from MessageManager import MessageManager
import Config

warnings.filterwarnings("ignore")

FACTOR_TIME_EVENT_KEY = 'key-FTEK'
COMMUNICATION_READY_EVENT_KEY = 'key-CREK'


class BaseStrategy(PythonStrategy):
    def __init__(self):
        super().__init__()
        self.__factor_time_event_key = FACTOR_TIME_EVENT_KEY

        self.__factor_save_path = Config.get_factor_save_path()
        self.__timetable = Config.get_timetable_list()
        self.__time_event_handler = None
        self.__message_manager = None

        self.date = Config.get_today_date()
        self.market_data_path = os.path.join(Config.get_realtime_data_path(), self.date)
        self.order_allow_time = datetime.datetime.strptime(self.date + '0930', '%Y%m%d%H%M')

        self.strategy_name = 'Base'
        self.strategy_version = 'v1.0'
        self.subscribe_strategy_name = 'DemoStrategy'
        self.subscribe_key = 'key-Demo-SK'
        self.publish_key = 'key-Demo-PK'

    def subscribe(self):
        pass

    def on_market_data(self, market_data):
        pass

    def on_state_updated(self, pre_state):
        try:
            if pre_state == StrategyState.Initializing and self.state == StrategyState.Running:
                self.both_ends_log_info(f'开始启动策略')
                self.init_params()
                self.on_strategy_started()
                self.both_ends_log_info(
                    f'{self.strategy_name} {self.strategy_version} 策略启动成功, 日期={self.date}, 参数={self.strategy_params}')
        except Exception as e:
            self.both_ends_log_error(f'策略启动失败: 原因={traceback.format_exc()}')
            self.trade_service.pause_strategy()

    def on_time_event(self, key):
        try:
            if self.state != StrategyState.Running:
                return
            if key == self.__factor_time_event_key:
                if self.__message_manager.is_stock_count_test_pass():
                    res_list = self.__time_event_handler.process_factors_time_event()
                    if res_list:
                        time_spot, factor_path = res_list
                        self.both_ends_log_info(f'{time_spot} 因子数据计算完成')
                        if self.on_factor_calculated(time_spot, factor_path):
                            if datetime.datetime.strptime(self.date + time_spot, '%Y%m%d%H%M') >= self.order_allow_time:
                                self.__message_manager.send_cancel_order_command()
                            else:
                                self.both_ends_log_info(
                                    f'预测成功，但指令不允许发送！！ 指令允许发送最早时点={self.order_allow_time}, 当前时间点={time_spot}')
                        else:
                            self.both_ends_log_info(f'预测失败！！ 当前时间点={time_spot}')
                self.subscribe_service.subscribe_timer_event(1000, self.__factor_time_event_key)
            elif key == COMMUNICATION_READY_EVENT_KEY:
                if self.__message_manager.is_stock_count_test_pass():
                    self.both_ends_log_info(f'通信测试完成: {self.__message_manager.comm_progress_log()}')
                else:
                    self.both_ends_log_error(f'通信测试检查不通过: {self.__message_manager.comm_progress_log()}')
                    self.subscribe_service.subscribe_timer_event(300000, COMMUNICATION_READY_EVENT_KEY)

        except Exception as e:
            self.both_ends_log_error(f'框架事件处理失败: key={key}, 原因={traceback.format_exc()}')
            self.trade_service.pause_strategy()

    def on_customized_message(self, message, strategyName, strategyInstanceId, key):
        try:
            self.logger.info(
                f'MassageReceived: message={message}, strategyName={strategyName}, strategyInstanceId={strategyInstanceId}, key={key}')
            if key != self.subscribe_key or self.state != StrategyState.Running:
                return
            if self.__message_manager.parse_received_command(message):
                self.both_ends_log_info(f'收集到所有持仓信息: 组合大小={self.__message_manager.get_stock_list_size()}')
                portfolio_df = self.__message_manager.get_portfolio_dataframe()
                msg = self.on_portfolio_collected(portfolio_df)
                if msg:
                    self.__message_manager.send_new_target_command(msg)
        except Exception as e:
            self.both_ends_log_error(f'调仓指令生成失败: 原因={traceback.format_exc()}')
            self.trade_service.pause_strategy()

    @abstractmethod
    def on_factor_calculated(self, time_point: str, factor_file_path: str) -> bool:
        pass

    @abstractmethod
    def on_portfolio_collected(self, portfolio_dataframe: pd.DataFrame) -> str:
        pass

    @abstractmethod
    def on_strategy_started(self) -> None:
        pass

    def init_params(self):
        try:
            params = json.loads(self.strategy_params)
            if '日期' in params and params['日期'] and datetime.datetime.strptime(params['日期'], "%Y%m%d"):
                self.date = params['日期']
                self.market_data_path = os.path.join(Config.get_realtime_data_path(), self.date)
                self.order_allow_time = datetime.datetime.strptime(self.date + '0930', '%Y%m%d%H%M')
            if '对应调仓策略名称' in params and params['对应调仓策略名称']:
                self.subscribe_strategy_name = params['对应调仓策略名称']
            if '指令允许发送最早时点' in params and params['指令允许发送最早时点']:
                self.order_allow_time = datetime.datetime.strptime(self.date + params['指令允许发送最早时点'], '%Y%m%d%H%M')
            self.__factor_save_path = os.path.join(self.__factor_save_path, self.date)
            self.__time_event_handler = TimeEventHandler(self.__factor_save_path, self.__timetable,
                                                         log_info=self.both_ends_log_info,
                                                         log_error=self.both_ends_log_error)
        except Exception as e:
            self.both_ends_log_error(f'前台参数错误: 原因={traceback.format_exc()}')
            self.trade_service.pause_strategy()

    def init_modules(self, stock_set):
        self.__message_manager = MessageManager(stock_set=stock_set,
                                                publish_customized_message_func=self.trade_service.publish_customized_message,
                                                trade_service=self.trade_service,
                                                publish_key=self.publish_key,
                                                log_info=self.both_ends_log_info,
                                                log_error=self.both_ends_log_error)
        # check_init_data_dir
        flag_path = os.path.join(self.__factor_save_path, 'flag')
        if not os.path.isdir(flag_path):
            self.both_ends_log_error(f'{flag_path} 因子标记目录不存在，请确认！')
        for time_spot in self.__timetable:
            time_spot_path = os.path.join(self.__factor_save_path, time_spot)
            if not os.path.isdir(time_spot_path):
                self.both_ends_log_error(f'{time_spot_path} 因子数据目录不存在，请确认！')
        self.subscribe_service.subscribe_timer_event(1000, self.__factor_time_event_key)
        self.subscribe_service.subscribe_timer_event(300000, COMMUNICATION_READY_EVENT_KEY)
        self.subscribe_service.subscribe_customized_message(self.subscribe_strategy_name, self.subscribe_key)
        self.__message_manager.send_test_order_command()

    def subscribe_factors(self, time_factor_dic):
        try:
            for key in time_factor_dic:
                if key not in self.__timetable:
                    raise RuntimeError("时间点不存在")
            self.__time_event_handler.set_subscribed_factors(time_factor_dic)
        except Exception as e:
            self.both_ends_log_error(f'因子订阅失败: 原因={traceback.format_exc()}')
            self.trade_service.pause_strategy()

    def send_new_target_command(self, msg):
        self.__message_manager.send_new_target_command(msg)

    def get_new_target_command(self, content, flag):
        stock_set = self.__message_manager.get_stock_set()
        for stock in content:
            if stock["symbol"] not in stock_set:
                self.both_ends_log_error(f'收到非股票池内调仓计划: {stock["symbol"]}, 请核对调仓计划！！')
                return None
        return '{"command": "TARGET", "content": ' + str(content).replace("\'", '"') + ', "shouldPause":' + str(
            flag) + '}'

    def get_portfolio_msg_dict(self):
        if self.__message_manager:
            return self.__message_manager.lastest_portfolio_msg_dict
        else:
            return dict()

    def both_ends_log_info(self, msg):
        self.logger.info(msg)
        self.trade_service.send_strategy_log(msg)

    def both_ends_log_error(self, msg):
        self.logger.error(msg)
        self.trade_service.send_strategy_log(msg)

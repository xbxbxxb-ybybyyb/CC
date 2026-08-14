import datetime
import json
import traceback
import warnings
import os, sys
import pandas as pd
from abc import abstractmethod

from PythonStrategy import PythonStrategy
from StrategyState import StrategyState

sys.path.append(os.path.abspath(os.path.abspath(__file__) + "/.."))

from TimeEventHandler import TimeEventHandler
from MessageManager import MessageManager
import Config

warnings.filterwarnings("ignore")

FACTOR_TIME_EVENT_KEY = 'key-FTEK'


class BaseStrategy(PythonStrategy):
    def __init__(self):
        super().__init__()
        self.__factor_time_event_key = FACTOR_TIME_EVENT_KEY

        self.__factor_save_path = Config.get_factor_save_path()
        self.__timetable = Config.get_timetable_list()
        self.__time_event_handler = None
        self.message_manager = None

        self.date = Config.get_today_date()
        self.market_data_path = os.path.join(Config.get_realtime_data_path(), self.date)
        self.strategy_name = 'Base'
        self.subscribe_strategy_name = 'DemoStrategy'
        self.subscribe_key = 'key-Demo-SK'
        self.publish_key = 'key-Demo-PK'

        self.order_allow_time = datetime.datetime.strptime(self.date + '0930', '%Y%m%d%H%M')

    def subscribe_factors(self, time_factor_dic):
        try:
            for key in time_factor_dic:
                if key not in self.__timetable:
                    raise RuntimeError("时间点不存在")
            self.__time_event_handler.set_subscribed_factors(time_factor_dic)
        except Exception as e:
            self.both_ends_log_error(f'因子订阅失败: 原因={traceback.format_exc()}')
            self.trade_service.pause_strategy()

    def subscribe(self):
        pass

    def on_market_data(self, market_data):
        pass

    def on_state_updated(self, pre_state):
        try:
            if pre_state == StrategyState.Initializing and self.state == StrategyState.Running:
                self.on_strategy_started()
        except Exception as e:
            self.both_ends_log_error(f'策略启动失败: 原因={traceback.format_exc()}')
            self.trade_service.pause_strategy()

    def on_time_event(self, key):
        if self.state != StrategyState.Running:
            return
        try:
            if key == self.__factor_time_event_key:
                res_list = self.__time_event_handler.process_factors_time_event()
                if res_list:
                    time_spot, factor_path = res_list
                    self.both_ends_log_info(f'{time_spot} 因子数据计算完成')
                    if self.on_factor_calculated(time_spot, factor_path):
                        self.message_manager.send_cancel_order_command()
                self.subscribe_service.subscribe_timer_event(1000, self.__factor_time_event_key)
        except Exception as e:
            self.both_ends_log_error(f'TimeEvent处理失败: key={key}, 原因={traceback.format_exc()}')
            self.trade_service.pause_strategy()

    def on_customized_message(self, message, strategyName, strategyInstanceId, key):
        if self.state != StrategyState.Running:
            return
        try:
            self.logger.info(
                f'MassageReceived: message={message}, strategyName={strategyName}, strategyInstanceId={strategyInstanceId}, key={key}')
            if key != self.subscribe_key:
                return
            flag = self.message_manager.parse_received_command(message)
            if flag and str(self.state) == "StrategyState.Running":
                self.both_ends_log_info(f'收集到所有持仓信息: 组合大小={self.message_manager.get_stock_list_size()}')
                portfolio_df = self.message_manager.get_portfolio_dataframe()
                msg = self.on_portfolio_collected(portfolio_df)
                self.message_manager.send_new_target_command(msg)
        except Exception as e:
            self.both_ends_log_error(f'调仓指令生成失败: 原因={traceback.format_exc()}')
            self.trade_service.pause_strategy()

    def get_portfolio_msg_dict(self):
        if self.message_manager:
            return self.message_manager.lastest_portfolio_msg_dict
        else:
            return dict()

    def both_ends_log_info(self, msg):
        self.logger.info(msg)
        self.trade_service.send_strategy_log(msg)

    def both_ends_log_error(self, msg):
        self.logger.error(msg)
        self.trade_service.send_strategy_log(msg)

    '''please implement in subclass'''
    '''return True/False'''

    @abstractmethod
    def on_factor_calculated(self, time_point: str, factor_file_path: str) -> bool:
        pass

    '''please implement in subclass'''
    '''return msg'''

    @abstractmethod
    def on_portfolio_collected(self, portfolio_dataframe: pd.DataFrame) -> str:
        pass

    def on_strategy_started(self) -> None:
        try:
            params = json.loads(self.strategy_params)
            if params['日期'] and datetime.datetime.strptime(params['日期'], "%Y%m%d"):
                self.date = params['日期']
                self.market_data_path = os.path.join(Config.get_realtime_data_path(), self.date)
            if params['对应调仓策略名称']:
                self.subscribe_strategy_name = params['对应调仓策略名称']
            # 限制指令发出时间
            if params['指令允许发送最早时点']:
                self.order_allow_time = datetime.datetime.strptime(self.date + params['指令允许发送最早时点'], '%Y%m%d%H%M')
        except Exception as e:
            self.both_ends_log_error(f'前台参数错误: 原因={traceback.format_exc()}')
            self.trade_service.pause_strategy()
        self.__factor_save_path = os.path.join(self.__factor_save_path, self.date)
        self.__time_event_handler = TimeEventHandler(self.__factor_save_path, self.__timetable,
                                                     log_info=self.both_ends_log_info,
                                                     log_error=self.both_ends_log_error)
        self.message_manager = MessageManager(self.trade_service.publish_customized_message,
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
        self.message_manager.send_test_order_command()
        self.subscribe_service.subscribe_timer_event(1000, self.__factor_time_event_key)
        self.subscribe_service.subscribe_customized_message(self.subscribe_strategy_name, self.subscribe_key)

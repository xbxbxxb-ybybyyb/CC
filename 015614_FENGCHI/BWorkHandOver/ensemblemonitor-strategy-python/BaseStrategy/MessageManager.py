import pandas as pd
from loguru import logger

import traceback


class MessageManager:
    def __init__(self, stock_set, publish_customized_message_func, trade_service, publish_key='key-PK', log_info=print,
                 log_error=print):
        self.__stocks = set()
        self.__stock_set = stock_set
        self.__trade_service = trade_service
        self.__portfolio_msg_dict = dict()
        self.lastest_portfolio_msg_dict = dict()

        self.__publish_customized_message_func = publish_customized_message_func
        self.__log_info = log_info
        self.__log_error = log_error
        self.__test_command = '{"command": "TEST", "content": [] , "shouldPause": 1}'
        self.__cancel_command = '{"command": "CANCEL", "content": [] , "shouldPause": 1}'
        self.__publish_key = publish_key

    def send_test_order_command(self):
        self.__publish_customized_message_func(self.__test_command, self.__publish_key)
        self.__log_info(f'发送指令: 测试指令,内容={self.__test_command}')

    def send_cancel_order_command(self):
        self.__publish_customized_message_func(self.__cancel_command, self.__publish_key)
        self.__log_info(f'发送指令: 撤单指令,内容={self.__cancel_command}')

    def send_new_target_command(self, msg):
        self.__publish_customized_message_func(msg, self.__publish_key)
        self.__log_info(f'发送指令: 调仓指令,内容={msg}')

    def parse_received_command(self, msg):
        try:
            arr = msg.split(',')
            if len(arr) != 7:
                self.__log_error(f'收到异常交互信息,已忽略: msg={msg}')
                return False

            portfolio = arr[1]
            symbol = arr[2]
            net_position = float(arr[3])
            sell_available = float(arr[4])
            total_buy_amount = float(arr[5])
            total_sell_amount = float(arr[6])

            if arr[0] == 'Test':
                if symbol in self.__stocks:
                    self.__log_error(f'收到重复股票:{symbol}，请核对调仓策略实例！！')
                elif symbol in self.__stock_set:
                    self.__stocks.add(symbol)
                    subscribe_stocks_size = len(self.__stock_set)
                    received_stocks_size = len(self.__stocks)
                    logger.info(
                        f'PortfolioInfoManager: Test for {symbol}, length={self.comm_progress_log()}')
                    if received_stocks_size == subscribe_stocks_size:
                        self.__log_info(f'通信测试完成: {self.comm_progress_log()}')
                    elif received_stocks_size % 500 == 0 or (
                            received_stocks_size > subscribe_stocks_size * 0.8 and received_stocks_size % 100 == 0):
                        self.__log_info(f'通信测试进度: {self.comm_progress_log()}')
                else:
                    self.__log_error(f'收到非股票池内的股票:{symbol}，请核对调仓策略实例！！')
            elif arr[0] == 'Update' and symbol in self.__stock_set:
                self.__portfolio_msg_dict[symbol] = [portfolio, symbol, net_position, sell_available, total_buy_amount,
                                                     total_sell_amount]
                return len(self.__portfolio_msg_dict) == len(self.__stock_set)
            return False
        except Exception as e:
            self.__log_error(f'PortfolioInfoManager: Parse Command Fail {traceback.format_exc()}')
            return False

    def get_stock_list_size(self):
        return len(self.__stocks)

    def get_portfolio_dataframe(self):
        df = pd.DataFrame(list(self.__portfolio_msg_dict.values()),
                          columns=["PortfolioNO", "Symbol", "NetPosition", "SellAvailable", "TotalBuyAmount",
                                   "TotalSellAmount"]
                          )
        self.lastest_portfolio_msg_dict = self.__portfolio_msg_dict
        self.__portfolio_msg_dict = dict()
        return df

    def comm_progress_log(self):
        return f'{len(self.__stocks)}/{len(self.__stock_set)}'

    def get_stock_set(self):
        return self.__stock_set

    def is_stock_count_test_pass(self):
        if len(self.__stocks) == len(self.__stock_set):
            return True
        else:
            return False

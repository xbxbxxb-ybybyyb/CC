import pandas as pd
from loguru import logger

import traceback


class MessageManager:
    def __init__(self, publish_customized_message_func, publish_key='key-PK', log_info=print,
                 log_error=print):
        self.__stocks = set()
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
                    self.__log_error(f'收到重复股票（{symbol}）测试信息，请核对调仓策略实例！！')
                else:
                    self.__stocks.add(symbol)
                    logger.info("PortfolioInfoManager: Test for {}", symbol)
            elif arr[0] == 'Update' and symbol in self.__stocks:
                self.__portfolio_msg_dict[symbol] = [portfolio, symbol, net_position, sell_available, total_buy_amount,
                                                     total_sell_amount]
                return len(self.__portfolio_msg_dict) == len(self.__stocks)
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

import time

from xdb.hfd_type import DataType
from xdb.file_loader import FileLoader
import os
import os.path
import pandas as pd
from loguru import logger
import datetime
# from FactorProvider.conf.DubboConf import get_xquantConfig


class StockData:
    def __init__(self):
        self.root = r"/dfs/group/900001/XDB/00_MarketData/00_StockData"
        self.loader_mgr = {}
        self.partition_loader_map = {}
        self.all_market_num_cache = {}
        self.all_market_channel_cache = {}
        # self.__user = get_xquantConfig().get("userAccount")
        # self.__filename = time.strftime('%Y%m%d_%H%M%S', time.localtime()) + "_" + self.__user

    def get_trade(self, date: str, symbol: str):
        res = self._fetch(date, symbol, DataType.TRADE)
        # self.__action_counter(symbol, "trade", res.shape[0])
        return res

    def get_order(self, date: str, symbol: str):
        res = self._fetch(date, symbol, DataType.ORDER)
        # self.__action_counter(symbol, "order", res.shape[0])
        return res

    def get_cancel(self, date: str, symbol: str):
        res = self._fetch(date, symbol, DataType.CANCEL)
        # self.__action_counter(symbol, "cancel", res.shape[0])
        return res

    def get_tick1s(self, date: str, symbol: str):
        res = self._fetch(date, symbol, DataType.TICK1S)
        # self.__action_counter(symbol, "tick1s", res.shape[0])
        return res

    def get_status(self, date: str, symbol: str):
        res = self._fetch(date, symbol, DataType.STATUS)
        # self.__action_counter(symbol, "tick1s", res.shape[0])
        return res

    def get_kline1m(self, date: str, symbol: str):
        res = self._fetch(date, symbol, DataType.KLINE1MIN)
        # self.__action_counter(symbol, "kline1min", res.shape[0])
        return res

    def get_enhancedtrade(self, date: str, symbol: str):
        res = self._fetch(date, symbol, DataType.ENHANCEDTRADE)
        # self.__action_counter(symbol, "enhancedtrade", res.shape[0])
        return res

    def get_dailydata(self, date: str, symbol: str):
        res = self._fetch_daily_data(date, symbol, DataType.DAILYDATA)
        # self.__action_counter(symbol, "daily", res.shape[0])
        return res

    def get_tickfull(self, date: str, symbol: str):
        res = self._fetch(date, symbol, DataType.TICKFULL)
        # self.__action_counter(symbol, "tickfull", res.shape[0])
        return res

    def get_tickex(self, date: str, symbol: str):
        res = self._fetch(date, symbol, DataType.TICKEX)
        # self.__action_counter(symbol, "tickex", res.shape[0])
        return res

    def get_staticinfo(self, date: str, symbol: str):
        res = self._fetch(date, symbol, DataType.STATICINFO)
        return res

    def get_trade_num(self, date: str, market: str, symbol=None):
        if symbol is None:
            symbol = []
        return self._get_num(date, market, DataType.TRADE, symbol)

    def get_order_num(self, date: str, market: str, symbol=None):
        if symbol is None:
            symbol = []
        return self._get_num(date, market, DataType.ORDER, symbol)

    def get_cancel_num(self, date: str, market: str, symbol=None):
        if symbol is None:
            symbol = []
        return self._get_num(date, market, DataType.CANCEL, symbol)

    def get_tick1s_num(self, date: str, market: str, symbol=None):
        if symbol is None:
            symbol = []
        return self._get_num(date, market, DataType.TICK1S, symbol)

    def get_channel_info(self, date: str, market: str, symbol=None):
        if symbol is None:
            symbol = []
        return self._get_channel(date, market, DataType.ORDER, symbol)

    def get_tickfull_num(self, date: str, market: str, symbol=None):
        if symbol is None:
            symbol = []
        return self._get_num(date, market, DataType.TICKFULL, symbol)

    def _get_num(self, date, market, market_data_type, symbol):

        if len(market) != 2:
            logger.error("参数错误: 市场格式不匹配, 请使用正确格式, 如 SH。当前输入={}".format(market))
            #raise Exception(s"check_params - market format error, please check input. input={} Example: SH".format(market))

        result = {}
        all_market_flag = False
        if isinstance(symbol, list):
            if len(symbol) == 0 or (len(symbol) == 1 and symbol[0] == ""):
                symbol = [""]
                all_market_flag = True

        elif isinstance(symbol, str):
            if symbol == "":
                all_market_flag = True
            symbol = [symbol]

        if all_market_flag:
            if date + "_" + market.upper() in self.all_market_num_cache:
                return self.all_market_num_cache[date + "_" + market.upper()]

        for i in symbol:
            if i != "":
                ret = self._check_params(date, i, market_data_type)
                if not ret:
                    return result

            path = self._get_file_path(date, market, market_data_type)
            if path in self.loader_mgr:
                result.update(self.loader_mgr[path]._load_info(market_data_type, i, market))
            else:
                loader = FileLoader(market_data_type, path, market)
                self.loader_mgr[path] = loader
                result.update(loader._load_info(market_data_type, i, market))
        if all_market_flag:
            self.all_market_num_cache[date + "_" + market.upper()] = result

        return result

    def _get_channel(self, date, market, market_data_type, symbol):

        if len(market) != 2 or (market.upper() != "SZ" and market.upper() != "SH" and market.upper() != "BJ"):
            logger.error("参数错误: 市场格式不匹配, 请使用正确格式, 如 SH。当前输入={}".format(market))
            #raise Exception("check_params - market format error, please check input. input={} Example: SH".format(market))

        result = {}
        all_market_flag = False
        if isinstance(symbol, list):
            if len(symbol) == 0 or (len(symbol) == 1 and symbol[0] == ""):
                symbol = [""]
                all_market_flag = True

        elif isinstance(symbol, str):
            if symbol == "":
                all_market_flag = True
            symbol = [symbol]

        if all_market_flag:
            if date + "_" + market.upper() in self.all_market_channel_cache:
                return self.all_market_channel_cache[date + "_" + market.upper()]

        for i in symbol:
            if i != "":
                ret = self._check_params(date, i, market_data_type)
                if not ret:
                    return result

            path = self._get_file_path(date, market, market_data_type)
            if path not in self.loader_mgr:
                loader = FileLoader(market_data_type, path, market)
                self.loader_mgr[path] = loader

            result.update(self.loader_mgr[path]._load_channel(i))

        if all_market_flag:
            self.all_market_channel_cache[date + "_" + market.upper()] = result

        return result

    def _check_params(self, date, symbol, market_data_type):
        if len(symbol) != 9:
            logger.error("参数错误: 标的长度有误, 请使用正确格式, 如 000001.SZ。当前输入={}".format(symbol))
            # return False
            raise Exception("check_params - Symbol error, please check input. input={} Example: 000001.SZ".format(symbol))
        elif not (symbol.endswith(".SZ") or symbol.endswith(".SH") or symbol.endswith(".BJ")):
            logger.error("参数错误: 标的后缀交易所不明确, 请使用正确格式, 如 000001.SZ。当前输入={}".format(symbol))
            # return False
            raise Exception("check_params - Symbol suffix error, please check input. input={} Example: 000001.SZ".format(symbol))
        try:
            datetime.datetime.strptime(date, '%Y%m%d')
        except ValueError:
            logger.error("参数错误: date参数时间格式不匹配, 请使用正确格式, 如 20230422。当前输入={}".format(date))
            # return False
            raise Exception("check_params - datetime format error, please check input. input={} Example: 20230422".format(date))

        if market_data_type == DataType.STATUS and not symbol.endswith(".SH"):
            logger.error("参数错误: 仅上海标的存在Status。当前输入={}".format(symbol))
            # return False
            raise Exception(
                "check_params - Status is only available in SH market. input={}".format(symbol))

        return True

    def _fetch(self, date, symbol, market_data_type):
        ret = self._check_params(date, symbol, market_data_type)
        if not ret:
            return pd.DataFrame()
        market = symbol.split(".")[-1].upper()
        path = self._get_file_path(date, market, market_data_type)
        if path in self.loader_mgr:
            return self.loader_mgr[path].load_symbol(date, symbol, market_data_type)
        else:
            try:
                loader = FileLoader(market_data_type, path, market, cached=False)
            except Exception as e:
                return pd.DataFrame()
            self.loader_mgr[path] = loader
            return loader.load_symbol(date, symbol, market_data_type)

    def _fetch_daily_data(self, date, symbol, market_data_type):
        ret = self._check_params(date, symbol, market_data_type)
        if not ret:
            return pd.DataFrame()
        market = symbol.split(".")[-1].upper()
        path = self._get_file_path(date, market, market_data_type)
        if path not in self.loader_mgr:
            self.loader_mgr[path] = FileLoader(market_data_type, path, market, cached=False)

        return self.loader_mgr[path].load_dailydata(date, symbol)

    def _get_file_path(self, date, market, market_data_type):
        if market.upper() == 'SZ':
            market_dir = "00_SZ"
        elif market.upper() == 'SH':
            market_dir = "01_SH"
        else:
            market_dir = "02_BJ"

        if market_data_type is DataType.STATUS:
            return os.path.join(self.root, "02_UHFData", market_dir, "09_Status", date,
                                f"Stock_{market.upper()}_Status_{date}")
        elif market_data_type is DataType.ORDER:
            return os.path.join(self.root, "02_UHFData", market_dir, "02_Order", date,
                                f"Stock_{market.upper()}_Order_{date}")
        elif market_data_type is DataType.TRADE:
            return os.path.join(self.root, "02_UHFData", market_dir, "01_Trade", date,
                                f"Stock_{market.upper()}_Trade_{date}")
        elif market_data_type is DataType.CANCEL:
            return os.path.join(self.root, "02_UHFData", market_dir, "03_Cancel", date,
                                f"Stock_{market.upper()}_Cancel_{date}")
        elif market_data_type is DataType.TICK1S:
            return os.path.join(self.root, "02_UHFData", market_dir, "04_Tick1s", date,
                                f"Stock_{market.upper()}_Tick1s_{date}")
        elif market_data_type is DataType.TICKFULL:
            return os.path.join(self.root, "02_UHFData", market_dir, "05_TickFull", date,
                                f"Stock_{market.upper()}_TickFull_{date}")
        elif market_data_type is DataType.TICKEX:
            return os.path.join(self.root, "02_UHFData", market_dir, "00_TickEx", date,
                                f"Stock_{market.upper()}_TickEx_{date}")
        elif market_data_type is DataType.KLINE1MIN:
            return os.path.join(self.root, "02_UHFData", market_dir, "06_KLine1Min", date,
                                f"Stock_{market.upper()}_KLine1Min_{date}")
        elif market_data_type is DataType.ENHANCEDTRADE:
            return os.path.join(self.root, "02_UHFData", market_dir, "07_EnhancedTrade", date,
                                f"Stock_{market.upper()}_EnhancedTrade_{date}")
        elif market_data_type is DataType.DAILYDATA:
            return os.path.join(self.root, "02_UHFData", market_dir, "08_DailyData", date,
                                f"Stock_{market.upper()}_DailyData_{date}")
        elif market_data_type is DataType.STATICINFO:
            return os.path.join(self.root, "04_StaticInfo", market_dir, date,
                                f"Stock_{market.upper()}_StaticInfo_{date}")

    # def _get_file_dir(self, date, market_data_type, isSH):
    #     market = "SH" if isSH else "SZ"
    #     if market_data_type is DataType.ORDER:
    #         return os.path.join(self.root, "02_UHFData", market, "Order", date)
    #     elif market_data_type is DataType.TRADE:
    #         return os.path.join(self.root, "02_UHFData", market, "Trade", date)
    #     elif market_data_type is DataType.CANCEL:
    #         return os.path.join(self.root, "02_UHFData", market, "Cancel", date)
    #     elif market_data_type is DataType.TICK1S:
    #         return os.path.join(self.root, "02_UHFData", market, "Tick1s", date)
    #     elif market_data_type is DataType.TICKFULL:
    #         return os.path.join(self.root, "02_UHFData", market, "TickFull", date)
    #     elif market_data_type is DataType.TICKEX:
    #         return os.path.join(self.root, "02_UHFData", market, "TickEx", date)

    def __action_counter(self, symbol, data_type, row):
        return
        # if not os.path.exists("/data/user/019073/cost_analysis/logs/"):
        #     return
        # with open("/data/user/019073/cost_analysis/logs/" + self.__filename, 'a') as file:
        #     act = time.strftime('%Y%m%d_%H%M%S', time.localtime()) + ", " + symbol + ", " + data_type + "," + str(row) + "\n"
        #     file.write(act)

from toolkit.xdb_reader.xdb.hfd_type import DataType
from toolkit.xdb_reader.xdb.file_loader import FileLoader
import os
import os.path
import pandas as pd
from loguru import logger
import datetime


class BondData:
    def __init__(self):
        self.root = r"/dfs/group/900001/XDB/00_MarketData/01_BondData/02_UHFData/"
        self.loader_mgr = {}
        self.partition_loader_map = {}

    def get_trade(self, date: str, symbol: str):
        return self._fetch(date, symbol, DataType.TRADE)

    def get_order(self, date: str, symbol: str):
        return self._fetch(date, symbol, DataType.ORDER)

    def get_cancel(self, date: str, symbol: str):
        return self._fetch(date, symbol, DataType.CANCEL)

    def get_tick1s(self, date: str, symbol: str):
        return self._fetch(date, symbol, DataType.TICK1S)

    def get_kline1m(self, date: str, symbol: str):
        return self._fetch(date, symbol, DataType.KLINE1MIN)

    def get_dailydata(self, date: str, symbol: str):
        return self._fetch_daily_data(date, symbol, DataType.DAILYDATA)

    def get_tickfull(self, date: str, symbol: str):
        return self._fetch(date, symbol, DataType.TICKFULL)

    def get_tickex(self, date: str, symbol: str):
        return self._fetch(date, symbol, DataType.TICKEX)

    def get_trade_num(self, date: str, market: str, symbol=""):
        return self._get_num(date, market, DataType.TRADE, symbol)

    def get_order_num(self, date: str, market: str, symbol=""):
        return self._get_num(date, market, DataType.ORDER, symbol)

    def get_cancel_num(self, date: str, market: str, symbol=""):
        return self._get_num(date, market, DataType.CANCEL, symbol)

    def get_tick1s_num(self, date: str, market: str, symbol=""):
        return self._get_num(date, market, DataType.TICK1S, symbol)

    # def get_tickfull_num(self, date: str, market: str, symbol=""):
    #     return self._get_num(date, market, DataType.TICKFULL, symbol)

    def _get_num(self, date, market, market_data_type, symbol):

        if len(market) != 2:
            logger.error("参数错误: 市场格式不匹配, 请使用正确格式, 如 SH。当前输入={}".format(market))
            # raise Exception("check_params - market format error, please check input. input={} Example: SH".format(market))

        if symbol != "":
            ret = self._check_params(date, symbol, market_data_type)
            if not ret:
                return {}
        market = 'SH' if ".SH" in symbol else 'SZ'
        path = self._get_file_path(date, market, market_data_type)
        if path in self.loader_mgr:
            return self.loader_mgr[path]._load_info(market_data_type, symbol, market)
        else:
            loader = FileLoader(market_data_type, path, market)
            self.loader_mgr[path] = loader
            return loader._load_info(market_data_type, symbol, market)

    def _check_params(self, date, symbol, market_data_type):
        if len(symbol) != 9:
            logger.error("参数错误: 标的长度有误, 请使用正确格式, 如 000001.SZ。当前输入={}".format(symbol))
            return False
            # raise Exception("check_params - Symbol error, please check input. input={} Example: 000001.SZ".format(symbol))
        elif not (symbol.endswith(".SZ") or symbol.endswith(".SH")):
            logger.error("参数错误: 标的后缀交易所不明确, 请使用正确格式, 如 000001.SZ。当前输入={}".format(symbol))
            return False
            # raise Exception("check_params - Symbol suffix error, please check input. input={} Example: 000001.SZ".format(symbol))
        try:
            datetime.datetime.strptime(date, '%Y%m%d')
        except ValueError:
            logger.error("参数错误: date参数时间格式不匹配, 请使用正确格式, 如 20230422。当前输入={}".format(date))
            return False
            # raise Exception("check_params - datetime format error, please check input. input={} Example: 20230422".format(date))

        return True

    def _fetch(self, date, symbol, market_data_type):
        ret = self._check_params(date, symbol, market_data_type)
        if not ret:
            return pd.DataFrame()
        is_sh = ".SH" in symbol
        market = 'SZ'
        if is_sh:
            market = 'SH'
        path = self._get_file_path(date, market, market_data_type)
        if path in self.loader_mgr:
            return self.loader_mgr[path].load_symbol(date, symbol, market_data_type)
        else:
            loader = FileLoader(market_data_type, path, market, cached=False)
            self.loader_mgr[path] = loader
            return loader.load_symbol(date, symbol, market_data_type)

    def _fetch_daily_data(self, date, symbol, market_data_type):
        ret = self._check_params(date, symbol, market_data_type)
        if not ret:
            return pd.DataFrame()
        market = 'SH' if ".SH" in symbol else 'SZ'
        path = self._get_file_path(date, market, market_data_type)
        if path not in self.loader_mgr:
            self.loader_mgr[path] = FileLoader(market_data_type, path, market, cached=False)

        return self.loader_mgr[path].load_dailydata(date, symbol)

    # def fetch_partition(self, date, symbol, market_data_type):
    #
    #     if symbol in self.loader_mgr:
    #         return self.loader_mgr[symbol].load_symbol(symbol)
    #
    #     else:
    #         if market_data_type in self.partition_loader_map:
    #             for loader in self.partition_loader_map[market_data_type].values():
    #                 if loader.check_symbol_exist(symbol):
    #                     self.loader_mgr[symbol] = loader
    #                     return loader.load_symbol(symbol)
    #         else:
    #             self.partition_loader_map[market_data_type] = {}
    #
    #         if symbol.endswith(".SZ") or symbol.endswith(".sz"):
    #             isSH = False
    #         elif symbol.endswith(".SH") or symbol.endswith(".sh"):
    #             isSH = True
    #         else:
    #             logger.error("获取数据错误: 标的后缀交易所不明确！")
    #             #raise Exception(
    #                 "fetch_partition - Symbol suffix error, please check input. input={} Example: 000001.SZ".format(symbol))
    #             return
    #         dir_path = self._get_file_dir(date, market_data_type, isSH)
    #
    #         file_list = os.listdir(dir_path)
    #         for p in file_list:
    #             tmp_path = os.path.join(dir_path, p)
    #             if tmp_path not in self.partition_loader_map[market_data_type]:
    #                 tmp_loader = FileLoader(market_data_type, tmp_path, cached=False)
    #                 self.partition_loader_map[market_data_type][tmp_path] = tmp_loader
    #             else:
    #                 tmp_loader = self.partition_loader_map[market_data_type][tmp_path]
    #
    #             if tmp_loader.check_symbol_exist(symbol):
    #                 self.loader_mgr[symbol] = tmp_loader
    #                 return tmp_loader.load_symbol(symbol)
    #
    #         logger.warning("获取数据失败: 标的在当前交易日无相关存储信息！标的={}, 日期={}".format(symbol, date))
    #         return
    #
    # def _fetch_all_data(self, date, market_data_type):
    #     # path = self._get_file_path(date, market_data_type)
    #     # loader = FileLoader(market_data_type, path, cached=False)
    #     # return loader.load_all_symbol()
    #     return

    def _get_file_path(self, date, market, market_data_type):
        stockex = ""
        if market.upper() == "SZ":
            stockex = "00_SZ"
        elif market.upper() == "SH":
            stockex = "01_SH"
        else:
            logger.error("市场输入异常！输入 sz 或 sh！")
            return

        if market_data_type is DataType.ORDER:
            return os.path.join(self.root, stockex, "02_Order", date, f"Bond_{market.upper()}_Order_{date}")
        elif market_data_type is DataType.TRADE:
            return os.path.join(self.root, stockex, "01_Trade", date, f"Bond_{market.upper()}_Trade_{date}")
        elif market_data_type is DataType.CANCEL:
            return os.path.join(self.root, stockex, "03_Cancel", date, f"Bond_{market.upper()}_Cancel_{date}")
        elif market_data_type is DataType.TICK1S:
            return os.path.join(self.root, stockex, "04_Tick1s", date, f"Bond_{market.upper()}_Tick1s_{date}")
        elif market_data_type is DataType.TICKFULL:
            return os.path.join(self.root, stockex, "05_TickFull", date, f"Bond_{market.upper()}_TickFull_{date}")
        elif market_data_type is DataType.TICKEX:
            return os.path.join(self.root, stockex, "00_TickEx", date, f"Bond_{market.upper()}_TickEx_{date}")
        elif market_data_type is DataType.KLINE1MIN:
            return os.path.join(self.root, stockex, "06_KLine1Min", date, f"Bond_{market.upper()}_KLine1Min_{date}")
        elif market_data_type is DataType.DAILYDATA:
            return os.path.join(self.root, stockex, "08_DailyData", date, f"Bond_{market.upper()}_DailyData_{date}")

    def _get_file_dir(self, date, market_data_type, isSH):
        market = "SH" if isSH else "SZ"
        if market_data_type is DataType.ORDER:
            return os.path.join(self.root, market, "Order", date)
        elif market_data_type is DataType.TRADE:
            return os.path.join(self.root, market, "Trade", date)
        elif market_data_type is DataType.CANCEL:
            return os.path.join(self.root, market, "Cancel", date)
        elif market_data_type is DataType.TICK1S:
            return os.path.join(self.root, market, "Tick1s", date)
        elif market_data_type is DataType.TICKFULL:
            return os.path.join(self.root, market, "TickFull", date)
        elif market_data_type is DataType.TICKEX:
            return os.path.join(self.root, market, "TickEx", date)

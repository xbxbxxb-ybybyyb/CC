import time

from xdb.hfd_type import DataType
from xdb.file_loader import FileLoader
import os
import os.path
import pandas as pd
from loguru import logger
import datetime
from FactorProvider.conf.DubboConf import get_xquantConfig

class FundData:
    def __init__(self):
        self.root = r"/dfs/group/900001/XDB/00_MarketData/04_FundData"
        self.loader_mgr = {}
        self.partition_loader_map = {}

    def get_trade(self, date: str, symbol: str):
        res = self._fetch(date, symbol, DataType.TRADE)
        # self.__action_counter(symbol, "trade", res.shape[0])
        return res

    def get_tickex(self, date: str, symbol: str):
        res = self._fetch(date, symbol, DataType.TICKEX)
        # self.__action_counter(symbol, "tickex", res.shape[0])
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

    # def get_kline1m(self, date: str, symbol: str):
    #     res = self._fetch(date, symbol, DataType.KLINE1MIN)
    #     # self.__action_counter(symbol, "kline1min", res.shape[0])
    #     return res

    # def get_dailydata(self, date: str, symbol: str):
    #     res = self._fetch_daily_data(date, symbol, DataType.DAILYDATA)
    #     # self.__action_counter(symbol, "daily", res.shape[0])
    #     return res

    def get_staticinfo(self, date: str, symbol: str):
        res = self._fetch(date, symbol, DataType.STATICINFO)
        # self.__action_counter(symbol, "daily", res.shape[0])
        return res

    def get_tickfull(self, date: str, symbol: str):
        res = self._fetch(date, symbol, DataType.TICKFULL)
        # self.__action_counter(symbol, "tickfull", res.shape[0])
        return res

    def get_etfcreationredemptioninfo(self, date: str, symbol: str):
        res1, res2 = self._fetch(date, symbol, DataType.ETFCREATIONREDEMPTIONINFO)
        return res1, res2

    def _check_params(self, date, symbol, market_data_type):
        if len(symbol) != 9:
            logger.error("参数错误: 标的长度有误, 请使用正确格式, 如 000001.SZ。当前输入={}".format(symbol))
            # return
            raise Exception("check_params - Symbol error, please check input. input={} Example: 000001.SZ".format(symbol))
        elif not (symbol.endswith(".SZ") or symbol.endswith(".SH")):
            logger.error("参数错误: 标的后缀交易所不明确, 请使用正确格式, 如 000001.SZ。当前输入={}".format(symbol))
            # return
            raise Exception("check_params - Symbol suffix error, please check input. input={} Example: 000001.SZ".format(symbol))
        try:
            datetime.datetime.strptime(date, '%Y%m%d')
        except ValueError:
            logger.error("参数错误: date参数时间格式不匹配, 请使用正确格式, 如 20230422。当前输入={}".format(date))
            # return
            raise Exception("check_params - datetime format error, please check input. input={} Example: 20230422".format(date))

        return True

    def _fetch(self, date, symbol, market_data_type):
        self._check_params(date, symbol, market_data_type)
        market = 'SH' if ".SH" in symbol else 'SZ'

        path = self._get_file_path(date, market, market_data_type)
        if path in self.loader_mgr:
            if market_data_type == DataType.ETFCREATIONREDEMPTIONINFO:
                return self.loader_mgr[path].load_ETF_symbol(date, symbol)
            else:
                return self.loader_mgr[path].load_symbol(date, symbol, market_data_type)
        else:
            loader = FileLoader(market_data_type, path, market, cached=False)
            self.loader_mgr[path] = loader
            if market_data_type == DataType.ETFCREATIONREDEMPTIONINFO:
                return loader.load_ETF_symbol(date, symbol)
            else:
                return loader.load_symbol(date, symbol, market_data_type)


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
            return os.path.join(self.root, "02_UHFData", stockex, "02_Order", date,
                                f"Fund_{market.upper()}_Order_{date}")
        elif market_data_type is DataType.TRADE:
            return os.path.join(self.root, "02_UHFData", stockex, "01_Trade", date,
                                f"Fund_{market.upper()}_Trade_{date}")
        elif market_data_type is DataType.CANCEL:
            return os.path.join(self.root, "02_UHFData", stockex, "03_Cancel", date,
                                f"Fund_{market.upper()}_Cancel_{date}")
        elif market_data_type is DataType.TICK1S:
            return os.path.join(self.root, "02_UHFData", stockex, "04_Tick1s", date,
                                f"Fund_{market.upper()}_Tick1s_{date}")
        elif market_data_type is DataType.TICKFULL:
            return os.path.join(self.root, "02_UHFData", stockex, "05_TickFull", date,
                                f"Fund_{market.upper()}_TickFull_{date}")
        elif market_data_type is DataType.TICKEX:
            return os.path.join(self.root, "02_UHFData", stockex, "00_TickEx", date,
                                f"Fund_{market.upper()}_TickEx_{date}")

        # elif market_data_type is DataType.KLINE1MIN:
        #     return os.path.join(self.root, "02_UHFData", stockex, "06_KLine1Min", date,
        #                         f"Fund_{market.upper()}_KLine1Min_{date}")
        elif market_data_type is DataType.DAILYDATA:
            return os.path.join(self.root, "02_UHFData", stockex, "08_DailyData", date,
                                f"Fund_{market.upper()}_DailyData_{date}")
        elif market_data_type is DataType.STATICINFO:
            return os.path.join(self.root, "04_StaticInfo", stockex, date,
                                f"Fund_{market.upper()}_StaticInfo_{date}")
        elif market_data_type is DataType.ETFCREATIONREDEMPTIONINFO:
            return os.path.join(self.root, "05_ETFPurchaseRedemptionInfo", stockex, date,
                                f"Fund_{market.upper()}_ETFPurchaseRedemptionInfo_{date}")
        else:
            logger.error("DataType not match, only indextickex supported")

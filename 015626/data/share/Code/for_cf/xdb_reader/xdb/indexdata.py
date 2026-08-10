import time

from xdb.hfd_type import DataType
from xdb.file_loader import FileLoader
import os
import os.path
import pandas as pd
from loguru import logger
import datetime
from FactorProvider.conf.DubboConf import get_xquantConfig

class IndexData:
    def __init__(self):
        self.root = r"/dfs/group/900001/XDB/00_MarketData/03_IndexData"
        self.loader_mgr = {}
        self.partition_loader_map = {}

    def get_tickex(self, date: str, symbol: str):
        res = self._fetch(date, symbol, DataType.INDEXTICKEX)
        return res

    def get_staticinfo(self, date: str, symbol: str):
        res = self._fetch(date, symbol, DataType.STATICINFO)
        return res

    def _check_params(self, date, symbol, market_data_type):
        if len(symbol) != 9:
            logger.error("参数错误: 标的长度有误, 请使用正确格式, 如 000001.SZ。当前输入={}".format(symbol))
            return
            #raise Exception("check_params - Symbol error, please check input. input={} Example: 000001.SZ".format(symbol))
        elif not (symbol.endswith(".SZ") or symbol.endswith(".SH")):
            logger.error("参数错误: 标的后缀交易所不明确, 请使用正确格式, 如 000001.SZ。当前输入={}".format(symbol))
            return
            #raise Exception("check_params - Symbol suffix error, please check input. input={} Example: 000001.SZ".format(symbol))
        try:
            datetime.datetime.strptime(date, '%Y%m%d')
        except ValueError:
            logger.error("参数错误: date参数时间格式不匹配, 请使用正确格式, 如 20230422。当前输入={}".format(date))
            return
            #raise Exception("check_params - datetime format error, please check input. input={} Example: 20230422".format(date))

        return True

    def _fetch(self, date, symbol, market_data_type):
        self._check_params(date, symbol, market_data_type)
        market = 'SH' if ".SH" in symbol else 'SZ'
        path = self._get_file_path(date, market, market_data_type)
        if path in self.loader_mgr:
            return self.loader_mgr[path].load_symbol(date, symbol, market_data_type)
        else:
            loader = FileLoader(market_data_type, path, market, cached=False)
            self.loader_mgr[path] = loader
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

        if market_data_type is DataType.INDEXTICKEX:
            return os.path.join(self.root, "02_UHFData", stockex, "00_TickEx", date, f"Index_{market.upper()}_TickEx_{date}")
        elif market_data_type is DataType.STATICINFO:
            return os.path.join(self.root, "04_StaticInfo", stockex, date,
                                f"Index_{market.upper()}_StaticInfo_{date}")
        else:
            logger.error("DataType not match, only indextickex supported")

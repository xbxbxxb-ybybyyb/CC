import time

from toolkit.xdb_reader.xdb.hfd_type import DataType
from toolkit.xdb_reader.xdb.file_loader import FileLoader
import os
import os.path
import pandas as pd
from loguru import logger
import datetime
from FactorProvider.conf.DubboConf import get_xquantConfig

class FutureData:
    def __init__(self):
        self.root = r"/dfs/group/900001/XDB/00_MarketData/02_FutureData"
        self.loader_mgr = {}
        self.partition_loader_map = {}


    def get_tickex(self, date: str, symbol: str):
        res = self._fetch(date, symbol, DataType.FUTURETICKEX)
        return res

    def get_staticinfo(self, date: str, symbol: str):
        res = self._fetch(date, symbol, DataType.STATICINFO)
        return res

    def _check_params(self, date, symbol, market_data_type):

        try:
            datetime.datetime.strptime(date, '%Y%m%d')
        except ValueError:
            logger.error("参数错误: date参数时间格式不匹配, 请使用正确格式, 如 20230422。当前输入={}".format(date))
            return False
            #raise Exception("check_params - datetime format error, please check input. input={} Example: 20230422".format(date))

        return True

    def _fetch(self, date, symbol, market_data_type):
        ret = self._check_params(date, symbol, market_data_type)
        if not ret:
            return pd.DataFrame()
        market = 'CCFX'
        path = self._get_file_path(date, market, market_data_type)
        if path in self.loader_mgr:
            return self.loader_mgr[path].load_symbol(date, symbol, market_data_type)
        else:
            loader = FileLoader(market_data_type, path, market, cached=False)
            self.loader_mgr[path] = loader
            return loader.load_symbol(date, symbol, market_data_type)


    def _get_file_path(self, date, market, market_data_type):

        if market_data_type is DataType.FUTURETICKEX:
            return os.path.join(self.root, "02_UHFData", "03_CCFX", "00_TickEx", date, f"Future_CCFX_TickEx_{date}")
        elif market_data_type is DataType.STATICINFO:
            return os.path.join(self.root, "04_StaticInfo", "03_CCFX", date, f"Future_CCFX_StaticInfo_{date}")
        else:
            logger.error("DataType not match, only futuretickex supported")
            #raise RuntimeError("DataType not match")



    # def _get_file_dir(self, date, market_data_type, isSH):
    #     market = "SH" if isSH else "SZ"
    #
    #     if market_data_type is DataType.TICKEX:
    #         return os.path.join(self.root, "02_UHFData", market, "TickEx", date)


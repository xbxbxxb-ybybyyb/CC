import os
import pandas as pd
from loguru import logger
from xdb.hfd_type import DataType
from xdb.file_loader import FileLoader
import datetime
import struct
import zstd
import numpy as np


class FactorData:
    def __init__(self):
        self.root = r"/dfs/group/900001/XDB/01_FactorData/"
        self.loader_mgr = {}
        self.partition_loader_map = {}

    # def get_factor(self, date: str, symbol: str, strategy: str):
    #     return self._fetch(date, symbol, DataType.FACTOR, strategy)

    def get_factor_from_path(self, date: str, symbol: str, path: str):
        return self._fetch_from_path(date, symbol, DataType.FACTOR, path)

    def _check_params(self, date, symbol, strategy):
        # if len(symbol) != 9:
        #     logger.error("参数错误: 标的长度有误, 请使用正确格式, 如 000001.SZ。当前输入={}".format(symbol))
        #     return False
            #raise Exception("check_params - Symbol error, please check input. input={} Example: 000001.SZ".format(symbol))
        # elif not (symbol.endswith(".SZ") or symbol.endswith(".SH") or symbol.endswith(".CF")):
        #     logger.error("参数错误: 标的后缀交易所不明确, 请使用正确格式, 如 000001.SZ。当前输入={}".format(symbol))
        #     return False
            #raise Exception("check_params - Symbol suffix error, please check input. input={} Example: 000001.SZ".format(symbol))
        try:
            datetime.datetime.strptime(date, '%Y%m%d')
        except ValueError:
            logger.error("参数错误: date参数时间格式不匹配, 请使用正确格式, 如 20230422。当前输入={}".format(date))
            return False
            #raise Exception("check_params - datetime format error, please check input. input={} Example: 20230422".format(date))

        return True

    def _fetch_from_path(self, date, symbol, data_type, path):
        ret = self._check_params(date, symbol, "")

        if not ret:
            return pd.DataFrame()

        # path = os.path.join(path, date, symbol)
        market = symbol.split(".")[-1].upper()
        if path in self.loader_mgr:
            return self.loader_mgr[path].load_factor(symbol, data_type)
        else:
            loader = FileLoader(data_type, path, market, cached=False)
            self.loader_mgr[path] = loader
            return loader.load_factor(symbol, data_type)

    def _fetch(self, date, symbol, data_type, strategy):
        ret = self._check_params(date, symbol, strategy)
        if not ret:
            return pd.DataFrame()
        market = symbol.split(".")[-1].upper()
        path = self._get_file_path(symbol, date, strategy)

        if path in self.loader_mgr:
            return self.loader_mgr[path].load_factor(symbol, data_type)
        else:
            loader = FileLoader(data_type, path, market, cached=False)
            self.loader_mgr[path] = loader
            return loader.load_factor(symbol, data_type)


    def _get_file_path(self, symbol, date, strategy):
        return os.path.join(self.root, strategy, date, symbol)

    def _load_factor_data(self, path):
        return





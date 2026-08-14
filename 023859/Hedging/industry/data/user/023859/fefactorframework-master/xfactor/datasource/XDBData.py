import os
import time
import numpy as np
import settings
import struct
from loguru import logger
from xfactor import FactorDataPrepareUtil
import pandas as pd
import zstd

def get_xdb_data(data_name, strategy, date):
    file_path = settings.xdb_path[strategy] + "/" + data_name + "/" + date + ".pkl"
    if not os.path.exists(file_path):
        logger.warning(
            "name={}, date={}, strategy={} xdb file not exists! return empty dataframe".format(data_name, date,
                                                                                               strategy))
        return pd.DataFrame()
    df = pd.read_pickle(file_path, compression='gzip')
    return df


def parse_header(file_stream):

    location_map = {}
    magic_data = file_stream.read(8)

    _header_size = file_stream.read(8)
    _header_size = struct.unpack('q', _header_size)[0]
    _header_count = _header_size // 26
    if _header_count != _header_size / 26:
        logger.error("解析头文件出错：头文件大小不合规。请检查数据文件是否完整。")
        return

    for i in range(_header_count):
        cur_symbol = file_stream.read(26)
        name, mkt, start, end = struct.unpack('<8s2sqq', cur_symbol)

        name = (name[:6]).decode()
        mkt = (mkt).decode()
        if len(name) > 6:
            name = name[:6]
        name = name + '.' + mkt
        location_map[name] = {"symbol": name,
                              "start": start,
                              "end": end
                              }

    return location_map

def get_xdb_data_test(data_name, strategy, date):
    file_path = settings.xdb_path_new[strategy] + "/{}/{}.pkl".format(data_name, date)
    data_format = np.dtype([
        ("MDDate", "<S8"), ("MDTime", '<i8'), ("NumTrades", '<i8'),
        ("TotalVolumeTrade", '<i8'),
        ("VolumeTrade", '<i8'), ("pattern", '<i8'),

        ("TotalBidQty", '<i8'), ("TotalOfferQty", '<i8'),
        ("Buy1OrderQty", "<i8"),
        ("Buy2OrderQty", "<i8"), ("Buy3OrderQty", "<i8"),
        ("Buy4OrderQty", "<i8"), ("Buy5OrderQty", "<i8"),
        ("Buy6OrderQty", "<i8"), ("Buy7OrderQty", "<i8"),
        ("Buy8OrderQty", "<i8"), ("Buy9OrderQty", "<i8"),
        ("Buy10OrderQty", "<i8"),

        ("Buy1NumOrders", "<i8"),
        ("Buy2NumOrders", "<i8"), ("Buy3NumOrders", "<i8"),
        ("Buy4NumOrders", "<i8"), ("Buy5NumOrders", "<i8"),
        ("Buy6NumOrders", "<i8"), ("Buy7NumOrders", "<i8"),
        ("Buy8NumOrders", "<i8"), ("Buy9NumOrders", "<i8"),
        ("Buy10NumOrders", "<i8"),

        ("Sell1OrderQty", "<i8"),
        ("Sell2OrderQty", "<i8"), ("Sell3OrderQty", "<i8"),
        ("Sell4OrderQty", "<i8"), ("Sell5OrderQty", "<i8"),
        ("Sell6OrderQty", "<i8"), ("Sell7OrderQty", "<i8"),
        ("Sell8OrderQty", "<i8"), ("Sell9OrderQty", "<i8"),
        ("Sell10OrderQty", "<i8"),

        ("Sell1NumOrders", "<i8"),
        ("Sell2NumOrders", "<i8"), ("Sell3NumOrders", "<i8"),
        ("Sell4NumOrders", "<i8"), ("Sell5NumOrders", "<i8"),
        ("Sell6NumOrders", "<i8"), ("Sell7NumOrders", "<i8"),
        ("Sell8NumOrders", "<i8"), ("Sell9NumOrders", "<i8"),
        ("Sell10NumOrders", "<i8"),

        ("TotalValueTrade", '<f8'), ("LastPx", '<f8'), ("ff_shares", '<f8'), ("industry", '<f8'),
        ("after_not_ul_len", '<f8'), ("OpenPx", '<f8'),
        ("WeightedAvgBidPx", '<f8'), ("WeightedAvgOfferPx", '<f8'),
        ("Buy1Price", "<f8"),
        ("Buy2Price", "<f8"), ("Buy3Price", "<f8"),
        ("Buy4Price", "<f8"), ("Buy5Price", "<f8"),
        ("Buy6Price", "<f8"), ("Buy7Price", "<f8"),
        ("Buy8Price", "<f8"), ("Buy9Price", "<f8"),
        ("Buy10Price", "<f8"),
        ("Sell1Price", "<f8"),
        ("Sell2Price", "<f8"), ("Sell3Price", "<f8"),
        ("Sell4Price", "<f8"), ("Sell5Price", "<f8"),
        ("Sell6Price", "<f8"), ("Sell7Price", "<f8"),
        ("Sell8Price", "<f8"), ("Sell9Price", "<f8"),
        ("Sell10Price", "<f8"), ])
    if not os.path.exists(file_path):
        logger.warning(
            "name={}, date={}, strategy={} xdb file not exists! return empty dataframe".format(data_name, date,
                                                                                               strategy))
        return {}

    file_stream = open(file_path, 'rb')
    location_map = parse_header(file_stream)
    result = {}
    for k,v in location_map.items():

        loc = location_map[k]
        start = loc["start"]
        end = loc["end"]
        if len(loc["symbol"]) == 0:
             return pd.DataFrame()
        if end <= start or end < 0 or start < 0:
            return pd.DataFrame()

        file_stream.seek(start, 0)
        _data = file_stream.read(end - start)

        uncompress = zstd.ZSTD_uncompress(_data)

        df = pd.DataFrame(np.frombuffer(uncompress, data_format))
        df["MDDate"] = df["MDDate"].apply(lambda x: x.decode())
        df['dt'] = date
        df["Ticker"] = k
        df.set_index(['dt', 'Ticker'], drop=True, inplace=True)
        result[k] = df

    return result

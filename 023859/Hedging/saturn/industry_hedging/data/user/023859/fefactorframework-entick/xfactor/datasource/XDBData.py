from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from threading import RLock
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
    if data_name in ['xdb_order', 'xdb_trade', 'xdb_cancel', 'xdb_tickex']:
        file_path = settings.xdb_path_xdbformat[strategy] + "/" + data_name + "/" + date + ".pkl"
        if not os.path.exists(file_path):
            logger.warning(
                "name={}, date={}, strategy={} xdb file not exists! return empty dataframe".format(data_name, date,
                                                                                                   strategy))
            return pd.DataFrame()
        df = pd.read_pickle(file_path)
        return df
    elif data_name in ['xdb_tick1s', 'xdb_tickfull', 'xdb_tickfulladdorder']:
        return get_xdb_data_from_xdb_format(data_name, strategy, date)

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


def fetch_parallel(file_stream, start, end, lock, data_format, date, symbol):
    lock.acquire()
    file_stream.seek(start, 0)
    _data = file_stream.read(end - start)
    lock.release()

    uncompress = zstd.ZSTD_uncompress(_data)

    df = pd.DataFrame(np.frombuffer(uncompress, data_format))
    df["MDDate"] = df["MDDate"].apply(lambda x: x.decode())
    if "OrderType" in df.columns:
        df["OrderType"] = df["OrderType"].apply(lambda x: x.decode())
    df['dt'] = pd.Timestamp(str(date))
    df["Ticker"] = symbol
    df.set_index(['dt', 'Ticker'], drop=True, inplace=True)
    return df


def get_xdb_data_from_xdb_format(data_name, strategy, date):
    file_path = settings.xdb_path_xdbformat[strategy] + "/{}/{}".format(data_name, date)
    if not os.path.exists(file_path):
        logger.warning(
            "name={}, date={}, strategy={} xdb file not exists! return empty dataframe".format(data_name, date,
                                                                                               strategy))
        return {}
    if data_name in ["xdb_tick1s", "xdb_tickfull"]:
        data_format = np.dtype([
            ("MDDate", "<S8"), ("MDTime", '<i8'), ("appl_seq_num", "<i8"), ("NumTrades", '<i8'),
            ("TotalVolumeTrade", '<i8'), ("pattern", '<i8'),
            ("TotalBidQty", '<i8'), ("TotalOfferQty", '<i8'),

            ("Buy1OrderQty", "<i8"),
            ("Buy2OrderQty", "<i8"), ("Buy3OrderQty", "<i8"),
            ("Buy4OrderQty", "<i8"), ("Buy5OrderQty", "<i8"),
            ("Buy6OrderQty", "<i8"), ("Buy7OrderQty", "<i8"),
            ("Buy8OrderQty", "<i8"), ("Buy9OrderQty", "<i8"),
            ("Buy10OrderQty", "<i8"),

            ("Sell1OrderQty", "<i8"),
            ("Sell2OrderQty", "<i8"), ("Sell3OrderQty", "<i8"),
            ("Sell4OrderQty", "<i8"), ("Sell5OrderQty", "<i8"),
            ("Sell6OrderQty", "<i8"), ("Sell7OrderQty", "<i8"),
            ("Sell8OrderQty", "<i8"), ("Sell9OrderQty", "<i8"),
            ("Sell10OrderQty", "<i8"),

            ("TotalValueTrade", '<f8'), ("VolumeTrade", '<f8'), ("LastPx", '<f8'),
            ("ff_shares", '<f8'), ("industry", '<f8'), ("after_not_ul_len", '<f8'), ("pre_close", '<f8'),
            ("OpenPx", '<f8'), ("HighPx", '<f8'), ("LowPx", '<f8'), ("WeightedAvgBidPx", '<f8'),
            ("WeightedAvgOfferPx", '<f8'),

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
            ("Sell10Price", "<f8"),
        ])
    elif data_name in ["xdb_tickfulladdorder"]:
        data_format = np.dtype([
            ("MDDate", "<S8"), ("OrderType", "<S2"), ("MDTime", '<i8'), ("appl_seq_num", "<i8"), ("NumTrades", '<i8'),
            ("TotalVolumeTrade", '<i8'), ("pattern", '<i8'),
            ("TotalBidQty", '<i8'), ("TotalOfferQty", '<i8'),

            ("Buy1OrderQty", "<i8"),
            ("Buy2OrderQty", "<i8"), ("Buy3OrderQty", "<i8"),
            ("Buy4OrderQty", "<i8"), ("Buy5OrderQty", "<i8"),
            ("Buy6OrderQty", "<i8"), ("Buy7OrderQty", "<i8"),
            ("Buy8OrderQty", "<i8"), ("Buy9OrderQty", "<i8"),
            ("Buy10OrderQty", "<i8"),

            ("Sell1OrderQty", "<i8"),
            ("Sell2OrderQty", "<i8"), ("Sell3OrderQty", "<i8"),
            ("Sell4OrderQty", "<i8"), ("Sell5OrderQty", "<i8"),
            ("Sell6OrderQty", "<i8"), ("Sell7OrderQty", "<i8"),
            ("Sell8OrderQty", "<i8"), ("Sell9OrderQty", "<i8"),
            ("Sell10OrderQty", "<i8"),

            ("TotalValueTrade", '<f8'), ("VolumeTrade", '<f8'), ("LastPx", '<f8'),
            ("ff_shares", '<f8'), ("industry", '<f8'), ("after_not_ul_len", '<f8'), ("pre_close", '<f8'),
            ("OpenPx", '<f8'), ("HighPx", '<f8'), ("LowPx", '<f8'), ("WeightedAvgBidPx", '<f8'),
            ("WeightedAvgOfferPx", '<f8'),

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
            ("Sell10Price", "<f8"), ("OrderPrice", "<f8"), ("OrderQty", "<f8"),
        ])

    else:
        logger.error(
            "xdb data name not exist! Only tick1s tickfull support xdb format! dataname={}, strategy={}".format(
                data_name, strategy))
        raise Exception("xdb data name not exist!")

    try:
        file_stream = open(file_path, 'rb')
        location_map = parse_header(file_stream)
        result = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:

            rlock = RLock()

            for k, v in location_map.items():
                start = v["start"]
                end = v["end"]
                if len(v["symbol"]) == 0:
                    result[k] = pd.DataFrame()
                    continue
                if end <= start or end < 0 or start < 0:
                    result[k] = pd.DataFrame()
                    continue

                result[k] = executor.submit(fetch_parallel, file_stream, start, end, rlock, data_format, date, k)

            for i in result.keys():
                try:
                    df = result[i].result()
                    if data_name in ["xdb_tickfulladdorder"]:
                        df["OrderPrice"].replace(-1, np.nan, inplace=True)
                        df["OrderQty"].replace(-1, np.nan, inplace=True)
                    result[i] = df
                except Exception as exc:
                    raise Exception('Get xdb value exception: %s' % (exc))

    except Exception as e:
        logger.error("xdb data prep error! dataname={}, strategy={}".format(data_name, strategy))
        raise Exception("xdb data prep error!")

    result["lag_info"] = 3
    return result

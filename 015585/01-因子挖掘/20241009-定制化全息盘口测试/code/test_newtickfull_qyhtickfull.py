import pandas as pd
import os
import numpy as np
from loguru import logger
import math
import copy
from multiprocessing import Pool
from xquant.factordata import FactorData
import IO
import struct
import zstd
os.system("pip uninstall xdbJG -y")
os.system("pip install /data/user/019073/marketdata/installer_and_demo/xdbJG-2.0.0-cp36-cp36m-linux_x86_64.whl")
from xdbJG.stockdata import StockData

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

data_name = 'xdb_tickfulladdorder'
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

def get_xdb_data_test(path, date):
    file_path = path + date

    if not os.path.exists(file_path):
        logger.warning(
            "xdb file not exists! return empty dataframe")
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
        df['MDDate'] = df['MDDate'].apply(lambda x: x.decode())
        df['OrderType'] = df['OrderType'].apply(lambda x: x.decode())
        result[k] = df

    return result
a = StockData()



df1 = get_xdb_data_test('/dfs/group/800463/data/xdb_data_lag3_test/europa_jupiter/xdb_tickfulladdorder/', '20180102')
tmp = df1['000672.SZ']
# 比对T日因子值结果
df1 = pd.read_hdf('/data/user/015585/20240116_frame/factor_value/europa/qyh_europa_20240905_1_test.h5')
df2 = pd.read_hdf('/data/user/015585/20240116_frame/factor_value/europa/qyh_europa_20240905_1.h5')
df2['new_value'] = df1['qyh_europa_20240905_1_test']
tmp = df2['qyh_europa_20240905_1'] - df2['new_value']
#
df_ori1 = pd.read_pickle('/dfs/group/800463/data/project1_prod/tickfull_europa_add_order/20170112.pkl')
df_ori2 = pd.read_pickle('/dfs/group/800463/data/xdb_data_lag3_test/T_europa_jupiter_test/20170112.pkl')
df_ori1 = df_ori1.query('Ticker == "002300.SZ"')
df_ori1 = df_ori1[df_ori1['MDTime'] >= 93000000]
df_ori2 = df_ori2.query('Ticker == "002300.SZ"')
df_ori2 = df_ori2[df_ori2['MDTime'] >= 93000000]
for col in ['OrderType' ,'OrderQty', 'OrderPrice']:
    df_ori1[col + '_new'] = df_ori2[col]
df_ori1['check1'] = df_ori1['OrderPrice'] - df_ori1['OrderPrice_new']
df_ori1[abs(df_ori1['check1']) >= 1e-10]
import decimal
def round_(x, n=0):
    x = x + 1e-10
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                     rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res
def func_factor(tick_df):
    tick_df['LastPx_100'] = tick_df['LastPx'].rolling(100, 1).mean().apply(lambda x : round_(x,5))
    tick_df = tick_df[tick_df['LastPx'] > tick_df['LastPx_100']]
    tick_df = tick_df[tick_df['OrderPrice'].apply(lambda x: round_(x, 2)) >= (tick_df['pre_close'] * 1.09).apply(lambda x: round_(x, 2))]
    tick_df['factor'] = (tick_df['OrderPrice'] - tick_df['LastPx']) / tick_df['pre_close']
    res = tick_df['factor'].std()
    return res
func_factor(df_ori1)
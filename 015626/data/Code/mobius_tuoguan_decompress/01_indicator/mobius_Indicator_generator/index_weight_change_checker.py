## Step 0
########### detect index weight change ###########

import numpy as np
import pandas as pd
import struct
import zstd
import os
from loguru import logger

import time
import datetime as dt
import sys
from xquant.factordata import FactorData
factorData = FactorData()
import settings

def get_pre_trading_date(date):
    return factorData.tradingday(date, -2)[0]


def get_next_trading_date(date):
    return factorData.tradingday(date, 2)[-1]

def get_trading_date_list(start, end):
    return factorData.tradingday(start, end)


read_format = {"IndexWeights": [
    ('Ticker', 'S64'),
    ('weight', '<d'),
    ('dt', 'S64')
],
    "IndexDF": [
        ('dt', 'S64'),
        ('Ticker', 'S64'),
        ('contract_00', 'S64'),
        ('contract_main', 'S64')
    ],
    "DailyDF": [
        ('dt', 'S64'),
        ('Ticker', 'S64'),
        ('open', '<d'),
        ('close', '<d'),
        ('high', '<d'),
        ('low', '<d'),
        ('volume', '<d'),
        ('amount', '<d'),
        ('position', '<d'),
        ('settle', '<d'),
        ('prod_id', 'S64'),
        ('expiration_days', '<d')
    ]
}


def parse_header(file_stream):
    location_map = {}
    magic_data = file_stream.read(8)

    _header_size = file_stream.read(8)
    _header_size = struct.unpack('q', _header_size)[0]
    _header_count = _header_size // 34
    if _header_count != _header_size / 34:
        logger.error("解析头文件出错：头文件大小不合规。请检查数据文件是否完整。")
        return

    for i in range(_header_count):
        cur_symbol = file_stream.read(34)
        name, mkt, start, end = struct.unpack('<16s2sqq', cur_symbol)

        name = name.decode()
        name = name.rstrip('\x00')
        location_map[name] = {"name": name,
                              "start": start,
                              "end": end
                              }

    return location_map


def get_index_data(file_path, data_format, key_list):
    if not os.path.exists(file_path):
        logger.warning(
            "xdb file not exists! return empty dataframe")
        return {}

    file_stream = open(file_path, 'rb')
    location_map = parse_header(file_stream)
    res = pd.DataFrame()
    for k in key_list:

        loc = location_map[k]
        start = loc["start"]
        end = loc["end"]
        if len(loc["name"]) == 0:
            return pd.DataFrame()
        if end <= start or end < 0 or start < 0:
            return pd.DataFrame()

        file_stream.seek(start, 0)
        _data = file_stream.read(end - start)

        uncompress = zstd.ZSTD_uncompress(_data)

        df = pd.DataFrame(np.frombuffer(uncompress, data_format))

        for fmt in read_format.get("IndexWeights"):
            if fmt[1].startswith("S"):
                df[fmt[0]] = df[fmt[0]].apply(lambda x: x.decode())

        df["index"] = k
        res = pd.concat([res, df])
    return res

def check_index_weight_file(date):
    flag_file = f"{settings.OfficialIndexWeightFlagFolder}/{date}_inx_ixcsiwgtnd.success"
    # if os.path.exists(flag_file):
    #     index_file_path_today = f"{settings.OfficialIndexWeightFolder}/{date}/inx_ixcsiwgtnd"
    #     index_weight_df_today = get_index_data(index_file_path_today, np.dtype(read_format.get("IndexWeights")), settings.IndexList)
    #     if len(index_weight_df_today) != 1850:
    #         logger.warning(f"成分股权重文件错误，数量={len(index_weight_df_today)}")
    #     return True
    # else:
    #     return False
    while True:
        if not os.path.exists(flag_file):
            logger.warning(f"成分股权重文件未生成，等待5分钟，flag_path={flag_file}")
            time.sleep(60 * 5)
        else:
            break
    index_file_path_today = f"{settings.OfficialIndexWeightFolder}/{date}/inx_ixcsiwgtnd"
    index_weight_df_today = get_index_data(index_file_path_today, np.dtype(read_format.get("IndexWeights")), settings.IndexList)
    if len(index_weight_df_today) != 1850:
        logger.warning(f"成分股权重文件错误，数量={len(index_weight_df_today)}")
        return False
    else:
        return True

def get_index_stock_change_dict(index_weight_folder, index_list, today):
    index_stock_change_dict = dict()
    pre_trade_day = get_pre_trading_date(today)
    logger.info(f"compare estimated index weight between today={today}, pre_trade_day={pre_trade_day}")

    index_file_path_today = f"{index_weight_folder}/{today}/inx_ixcsiwgtnd"
    index_weight_df_today = get_index_data(index_file_path_today, np.dtype(read_format.get("IndexWeights")), index_list)
    index_file_path_pre = f"{index_weight_folder}/{pre_trade_day}/inx_ixcsiwgtnd"
    index_weight_df_pre = get_index_data(index_file_path_pre, np.dtype(read_format.get("IndexWeights")), index_list)

    for index_name in index_list:
        tmp_df_today = index_weight_df_today[index_weight_df_today["index"] == index_name]
        ticker_list_today = tmp_df_today["Ticker"].to_list()
        tmp_df_pre = index_weight_df_pre[index_weight_df_pre["index"] == index_name]
        ticker_list_pre = tmp_df_pre["Ticker"].to_list()

        stock_change_dict = dict()

        if ticker_list_today != ticker_list_pre:
            new_stock_set = set(ticker_list_today) - set(ticker_list_pre)
            removed_stock_set = set(ticker_list_pre) - set(ticker_list_today)
            if len(new_stock_set) != len(removed_stock_set):
                logger.error(
                    f"len(new_stock_set)={len(new_stock_set)} != len(removed_stock_set)={len(removed_stock_set)}")
                sys.exit(1)

            stock_change_dict["new_stocks"] = new_stock_set
            stock_change_dict["removed_stocks"] = removed_stock_set

            index_stock_change_dict[index_name] = stock_change_dict
    return index_stock_change_dict


## Step 1
########### re-generate previous 27 index weight file ###########
writer_format = {"IndexWeights": [
    ('Ticker', '64s'),
    ('weight', '<d'),
    ('dt', '64s')
]
}


def retriver(cdate_list, index_list):
    for date in cdate_list:
        next_trading_date = get_next_trading_date(date)
        date = str(date)
        index_df_dict = {}
        for index in index_list:
            while True:
                df = factorData.hset('INDEX', next_trading_date, index, weightType=1)
                if len(df) != 0:
                    break
                else:
                    print(index, next_trading_date, 'no data, retrying in 3 minutes...')
                    time.sleep(180)  # 等待3分钟
            df = df.reset_index()[['stock', 'weight']]
            df = df.rename(columns={'stock': 'Ticker'})
            df['dt'] = next_trading_date
            df['weight'] = df['weight'] / 100
            # Check if the sum of weights is within the acceptable range
            sum_weights = df['weight'].sum()
            if abs(sum_weights - 1) >= 0.001:
                print(f"Warning: {index} on {date} has sum {sum_weights:.4f}, difference {abs(sum_weights - 1):.4f}")

            index_df_dict[index] = df
            # print(index, ' ', date, '  retriver done')

        return index_df_dict


def get_stock_list(date):
    df = factorData.get_factor_value('WIND_AShareDescription',
                                     factors=['S_INFO_WINDCODE', 'S_INFO_LISTDATE', 'S_INFO_DELISTDATE'])
    df = df.rename(columns={'S_INFO_WINDCODE': 'Ticker'}).set_index('Ticker').sort_index().fillna(20990101).astype(
        'int')
    tmp_df = df[df['S_INFO_DELISTDATE'] > date]
    tmp_df = tmp_df[tmp_df['S_INFO_LISTDATE'] <= date]
    tmp_df['alla'] = True
    tmp_df = tmp_df[['alla']]
    return tmp_df


def update_constituent_stocks(index_weight_dict, index_name, removed_stocks, new_stocks):
    if len(removed_stocks) != len(new_stocks):
        print(f"size of removed_stocks({len(removed_stocks)}) != new_stocks({len(new_stocks)})")
        return None
    index_weight_df_origin = index_weight_dict[index_name]

    removed_stocks_condition = index_weight_df_origin["Ticker"].isin(removed_stocks)
    index_weight_df_new = index_weight_df_origin[~removed_stocks_condition]
    date = index_weight_df_origin["dt"][0]
    for new_stock in new_stocks:
        new_row = pd.Series([new_stock, np.nan, date], index=index_weight_df_new.columns)
        index_weight_df_new = index_weight_df_new.append(new_row, ignore_index=True)
    if index_weight_df_origin.shape[0] != index_weight_df_new.shape[0]:
        print(
            f"size of index_weight_df_origin({index_weight_df_origin.shape[0]}) != index_weight_df_new({index_weight_df_new.shape[0]})")
        return None

    index_weight_df_new = index_weight_df_new.sort_values(by='Ticker')
    index_weight_df_new = index_weight_df_new.reset_index(drop=True)

    index_weight_dict[index_name] = index_weight_df_new
    return index_weight_dict


def write_index_weights(arg):
    path, header_item_size, source, date, index_df_dict = arg
    formats = writer_format.get("IndexWeights")

    # 检查每个 DataFrame 是否包含所有必要的字段
    for index_name, df in index_df_dict.items():
        required_columns = [fmt[0] for fmt in formats]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing columns in {index_name}: {missing_columns}")

    # 处理数据，将其转换为字节流
    byte_arr = []

    for index_name, df in index_df_dict.items():
        for fmt in formats:
            df[fmt[0]] = df[fmt[0]].apply(
                lambda x: struct.pack(fmt[1], x if fmt[1][-1] != 's' else str.encode(str(x))))
        byte_arr.append((index_name, b"".join(np.ravel(df.values))))

    # 创建文件夹
    file_path = os.path.join(path, str(date))
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    # 写入二进制文件
    with open(file_path + "/inx_ixcsiwgtnd", "wb") as f:
        magic = '12342800'
        f.write(struct.pack('8s', str.encode(magic)))
        header_size = len(byte_arr) * header_item_size
        f.write(struct.pack('<q', header_size))
        start = 8 + 8 + header_size

        for i in range(len(byte_arr)):
            f.seek(start)
            key, byte_data = byte_arr[i]
            compressed = zstd.ZSTD_compress(byte_data)
            f.write(compressed)

            f.seek(8 + 8 + header_item_size * i)
            f.write(struct.pack('16s', str.encode(key)))
            f.write(struct.pack('2s', str.encode(source)))
            f.write(struct.pack('<q', start))
            f.write(struct.pack('<q', start + len(compressed)))
            start += len(compressed)

    # print(f"{date} 指数权重文件写入完毕")


def generate_single_index_weight_file_for_constituent_stocks_change(contract_path, trading_date,
                                                                    index_stock_change_dict):
    cdate_list = [trading_date]
    factor_list = ['HS300', 'ZZ500', 'SH50', 'ZZ1000']
    index_weight_dict = retriver(cdate_list, factor_list)
    for k, v in index_stock_change_dict.items():
        #         logger.info(f"k={k}, v={v}")
        index_name = k
        removed_stocks = v["removed_stocks"]
        new_stocks = v["new_stocks"]
        #         logger.info(f"index_name={index_name}, removed_stocks={removed_stocks}, new_stocks={new_stocks}")
        index_weight_dict = update_constituent_stocks(index_weight_dict, index_name, removed_stocks, new_stocks)
    arg = (contract_path, 34, "ZZ", trading_date, index_weight_dict)
    write_index_weights(arg)


def generate_index_weight_file_for_constituent_stocks_change(contract_path, trading_date_list, index_stock_change_dict):
    logger.info(f"Generate new index weight file for dates={trading_date_list}")
    for date in trading_date_list:
        generate_single_index_weight_file_for_constituent_stocks_change(contract_path, date, index_stock_change_dict)



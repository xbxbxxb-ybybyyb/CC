# 下载xdb数据至公共文件夹使用
'''
'''
import pandas as pd
import os
import numpy as np
from loguru import logger
import math
import copy
from multiprocessing import Pool
from xquant.factordata import FactorData
from h5data.IO import IO
import struct
import zstd

os.system("pip uninstall xdbJG -y")
os.system("pip install /data/user/019073/marketdata/installer_and_demo/xdbJG-2.0.0-cp36-cp36m-linux_x86_64.whl")
from xdbJG.stockdata import StockData
import decimal
'''
1、after_not_ul_len含义为list_len
'''

def convert_tick(df, date, output_path):  # tick1s, tickfull转为二进制文件
    print(date, '进行二进制转换')
    # paths = base_path + "/" + date + ".pkl"
    # df = pd.read_pickle(paths, compression='gzip')
    symbol_list = list(df.index.get_level_values(1).unique())
    total_header_size = len(symbol_list) * 26
    idx = pd.IndexSlice

    with open(output_path + "/" + date, 'wb') as file:
        file.write(b'12345600')
        file.write(struct.pack('<q', total_header_size))

        headerCurrentIndex = 8 + 8
        start = 8 + 8 + total_header_size
        end = 0
        for symbol in symbol_list:
            cur_df = df.loc[idx[:, [symbol]],]
            if cur_df.empty:
                continue
            md_date_nparr = np.array(cur_df["MDDate"].apply(lambda x: str.encode(x)))
            int_selected = cur_df[[
                "MDTime", "appl_seq_num", "NumTrades", "TotalVolumeTrade",
                'pattern', "TotalBidQty", "TotalOfferQty",
                "Buy1OrderQty", "Buy2OrderQty", "Buy3OrderQty", "Buy4OrderQty", "Buy5OrderQty",
                "Buy6OrderQty", "Buy7OrderQty", "Buy8OrderQty", "Buy9OrderQty", "Buy10OrderQty",
                "Sell1OrderQty", "Sell2OrderQty", "Sell3OrderQty", "Sell4OrderQty", "Sell5OrderQty",
                "Sell6OrderQty", "Sell7OrderQty", "Sell8OrderQty", "Sell9OrderQty", "Sell10OrderQty", ]]
            double_selected = cur_df[[
                "TotalValueTrade", "VolumeTrade", "LastPx",
                'ff_shares', 'industry', 'after_not_ul_len', 'pre_close', "OpenPx", "HighPx", "LowPx",
                "WeightedAvgBidPx", "WeightedAvgOfferPx", "Buy1Price", "Buy2Price",
                "Buy3Price", "Buy4Price", "Buy5Price", "Buy6Price", "Buy7Price", "Buy8Price", "Buy9Price",
                "Buy10Price",
                "Sell1Price", "Sell2Price", "Sell3Price", "Sell4Price", "Sell5Price", "Sell6Price", "Sell7Price",
                "Sell8Price", "Sell9Price", "Sell10Price"]]
            int_selected_nparr = np.apply_along_axis(lambda x: np.array(x.tobytes(), dtype=np.void),
                                                     arr=int_selected.values, axis=1)
            double_selected_nparr = np.apply_along_axis(lambda x: np.array(x.tobytes(), dtype=np.void),
                                                        arr=double_selected.values, axis=1)

            df_nparr = md_date_nparr + int_selected_nparr + double_selected_nparr
            final_nparr = bytes.join(b"", df_nparr)

            compressed = zstd.ZSTD_compress(final_nparr)

            file.write(str.encode(symbol[:6] + '\0' + '\0'))
            file.write(str.encode(symbol[-2:]))
            file.write(struct.pack('<q', start))
            file.write(struct.pack('<q', start + len(compressed)))
            headerCurrentIndex += 26

            file.seek(start, 0)
            file.write(compressed)

            end = start + len(compressed)
            start = end

            file.seek(headerCurrentIndex, 0)  # # t
def convert_tickaddorder(df, date, output_path):
    print(date, '进行二进制转换')
    # paths = base_path + "/" + date + ".pkl"
    # df = pd.read_pickle(paths, compression='gzip')
    symbol_list = list(df.index.get_level_values(1).unique())
    total_header_size = len(symbol_list) * 26
    idx = pd.IndexSlice

    def encode_order_type(x):
        if x == "":
            return str.encode("\0\0")
        return str.encode(x)

    with open(output_path + "/" + date, 'wb') as file:
        file.write(b'12345600')
        file.write(struct.pack('<q', total_header_size))

        headerCurrentIndex = 8 + 8
        start = 8 + 8 + total_header_size
        end = 0
        for symbol in symbol_list:
            cur_df = df.loc[idx[:, [symbol]],]
            if cur_df.empty:
                continue
            md_date_nparr = np.array(cur_df["MDDate"].apply(lambda x: str.encode(x)))
            order_type_arr = np.array(cur_df["OrderType"].apply(lambda x: encode_order_type(x)))
            int_selected = cur_df[[
                "MDTime", "appl_seq_num", "NumTrades", "TotalVolumeTrade",
                'pattern', "TotalBidQty", "TotalOfferQty",
                "Buy1OrderQty", "Buy2OrderQty", "Buy3OrderQty", "Buy4OrderQty", "Buy5OrderQty",
                "Buy6OrderQty", "Buy7OrderQty", "Buy8OrderQty", "Buy9OrderQty", "Buy10OrderQty",
                "Sell1OrderQty", "Sell2OrderQty", "Sell3OrderQty", "Sell4OrderQty", "Sell5OrderQty",
                "Sell6OrderQty", "Sell7OrderQty", "Sell8OrderQty", "Sell9OrderQty", "Sell10OrderQty", ]]
            double_selected = cur_df[[
                "TotalValueTrade", "VolumeTrade", "LastPx",
                'ff_shares', 'industry', 'after_not_ul_len', 'pre_close', "OpenPx", "HighPx", "LowPx",
                "WeightedAvgBidPx", "WeightedAvgOfferPx", "Buy1Price", "Buy2Price",
                "Buy3Price", "Buy4Price", "Buy5Price", "Buy6Price", "Buy7Price", "Buy8Price", "Buy9Price",
                "Buy10Price",
                "Sell1Price", "Sell2Price", "Sell3Price", "Sell4Price", "Sell5Price", "Sell6Price", "Sell7Price",
                "Sell8Price", "Sell9Price", "Sell10Price", "OrderPrice", "OrderQty"]]
            int_selected_nparr = np.apply_along_axis(lambda x: np.array(x.tobytes(), dtype=np.void),
                                                     arr=int_selected.values, axis=1)
            double_selected_nparr = np.apply_along_axis(lambda x: np.array(x.tobytes(), dtype=np.void),
                                                        arr=double_selected.values, axis=1)

            df_nparr = md_date_nparr + order_type_arr + int_selected_nparr + double_selected_nparr
            final_nparr = bytes.join(b"", df_nparr)

            compressed = zstd.ZSTD_compress(final_nparr)

            file.write(str.encode(symbol[:6] + '\0' + '\0'))
            file.write(str.encode(symbol[-2:]))
            file.write(struct.pack('<q', start))
            file.write(struct.pack('<q', start + len(compressed)))
            headerCurrentIndex += 26

            file.seek(start, 0)
            file.write(compressed)

            end = start + len(compressed)
            start = end

            file.seek(headerCurrentIndex, 0)  # # t
def find_repeat_tick(tick_data, repeat_filter_cols):
    tick_data['inf_str'] = tick_data[repeat_filter_cols].apply(lambda x: str(x.values), axis=1)
    tick_data['last_inf_str'] = tick_data['inf_str'].shift(1)
    return tick_data['inf_str'] == tick_data['last_inf_str']
def round_(x, n=0):
    x = x + 1e-10
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                     rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res
def prepare_order_data_new(df, base_date):
    try:
        # st = time.time()
        df.columns = ['symbol', 'appl_seq_num', 'OrderIndex', 'OrderPrice', 'OrderQty', "MDTime", "order_index",
                      'local_index', "OrderBSFlag", "OrderType", "MDDate", "timestamp",
                      'ff_shares', 'pre_close', 'industry',
                      'after_not_ul_len', 'HTSCSecurityID', 'Ticker', 'pattern', 'dt']
        df["dt"] = pd.to_datetime(df["dt"])
        df['OrderBSFlag'] = df['OrderBSFlag'].apply(lambda x: int(x))
        df['OrderType'].replace('U', '3', inplace=True)  # xdb接口用U表示本方最优，转换为int类型的3，从而和xquant一致
        df['OrderType'] = df['OrderType'].apply(lambda x: int(x))
        df.set_index(["dt", "Ticker"], inplace=True)

        df['zcz'] = (((df.reset_index()['Ticker'].apply(lambda x: x[0] == '3')) & (
                    df.reset_index()['dt'] >= '2020-08-24')) | (
                         df.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
        df['ul_price'] = np.floor(df['pre_close'] * 100 * 1.1 + 0.5 + 1e-8) / 100
        df['ul_price'][df['zcz']] = np.floor(df['pre_close'] * 100 * 1.2 + 0.5 + 1e-8) / 100
        df['dl_price'] = np.floor(df['pre_close'] * 100 * 0.9 + 0.5 + 1e-8) / 100
        df['dl_price'][df['zcz']] = np.floor(df['pre_close'] * 100 * 0.8 + 0.5 + 1e-8) / 100
        df.loc[(df['OrderType'].isin([1, 3])) & (df['OrderBSFlag'] == 1), 'OrderPrice'] = df.loc[
            (df['OrderType'].isin([1, 3])) & (df['OrderBSFlag'] == 1), 'ul_price']
        df.loc[(df['OrderType'].isin([1, 3])) & (df['OrderBSFlag'] == 2), 'OrderPrice'] = df.loc[
            (df['OrderType'].isin([1, 3])) & (df['OrderBSFlag'] == 2), 'dl_price']
        df = df[['MDDate', 'MDTime', 'appl_seq_num', 'OrderIndex', 'OrderPrice', 'OrderQty', 'OrderBSFlag', "OrderType",
                 'ff_shares', 'pattern', 'industry', 'after_not_ul_len', 'pre_close', 'ul_price', 'dl_price']]
        for col in ['OrderPrice', 'pre_close', 'ul_price', 'dl_price']:
            df[col] = df[col].apply(lambda x: round_(x, 2))
        for col in ['ff_shares']:
            df[col] = df[col].apply(lambda x: round_(x, 4))
        for col in ['pattern']:
            df[col] = df[col].apply(lambda x: int(round_(x, 0)))
    except Exception as e:
        logger.error(
            "Order数据准备错误！base_date={}, error={}, trace={}".format(base_date, e.__cause__,
                                                                 e.__traceback__))
    return df
def prepare_trade_data_new(df, base_date):
    try:
        # st = time.time()
        df.columns = ['symbol', 'appl_seq_num', 'TradeBuyNo', 'TradeSellNo', 'TradePrice', "TradeQty", "MDTime", "TradeIndex",
                      'local_index', "TradeBSFlag", "MDDate", "timestamp",
                     'ff_shares', 'pre_close', 'industry', 'after_not_ul_len', 'HTSCSecurityID', 'Ticker', 'pattern', 'dt']
        # ed = time.time()
        # logger.info("rename cost={}".format(ed - st))
        # st = time.time()
        df["TradeMoney"] = (df["TradeQty"] * df["TradePrice"]).apply(lambda x : round_(x,2))
        df["TradeType"] = 0
        df['TradeBSFlag'] = df['TradeBSFlag'].apply(lambda x: int(x))
        df["dt"] = pd.to_datetime(df["dt"])
        df.set_index(["dt", "Ticker"], inplace=True)
        df = df[['MDDate', 'MDTime', 'appl_seq_num',
                 'TradeIndex', 'TradeBuyNo', 'TradeSellNo', 'TradeType', 'TradeBSFlag', 'TradePrice', 'TradeQty',
                 'TradeMoney', 'ff_shares', 'pattern', 'industry', 'after_not_ul_len', 'pre_close']]
        for col in ['TradePrice','pre_close']:
            df[col] = df[col].apply(lambda x : round_(x,2))
        for col in ['ff_shares']:
            df[col] = df[col].apply(lambda x : round_(x,4))
        # for col in ['industry','after_not_ul_len']:
        #     df[col] = df[col].apply(lambda x : round_(x,1))
        for col in ['pattern']:
            df[col] = df[col].apply(lambda x : int(round_(x,0)))

    except Exception as e:
        logger.error(
            "Trade数据准备错误！base_date={}, error={}, trace={}".format(base_date, e.__cause__,
                                                                 e.__traceback__))
    return df
def prepare_tick_data_new(df, base_date, tick_type):
    try:
        # st = time.time()
        df.columns = ['symbol', "MDDate", "MDTime", "timestamp", "appl_seq_num",
                      "OpenPx", "LastPx", "HighPx", "LowPx", "TotalOfferQty", "TotalBidQty",
                      "WeightedAvgOfferPx", "WeightedAvgBidPx", "TotalVolumeTrade", 'TotalValueTrade', 'VolumeTrade',
                      "NumTrades", 'TradingPhaseCode', 'last_local_index',
                      "Sell1Price", "Sell2Price", "Sell3Price", "Sell4Price", "Sell5Price",
                      "Sell6Price", "Sell7Price", "Sell8Price", "Sell9Price", "Sell10Price",
                      "Sell1OrderQty", "Sell2OrderQty", "Sell3OrderQty", "Sell4OrderQty", "Sell5OrderQty",
                      "Sell6OrderQty", "Sell7OrderQty", "Sell8OrderQty", "Sell9OrderQty", "Sell10OrderQty",
                      "Sell1NumOrders", "Sell2NumOrders", "Sell3NumOrders", "Sell4NumOrders", "Sell5NumOrders",
                      "Sell6NumOrders", "Sell7NumOrders", "Sell8NumOrders", "Sell9NumOrders", "Sell10NumOrders",

                      "Buy1Price", "Buy2Price", "Buy3Price", "Buy4Price", "Buy5Price",
                      "Buy6Price", "Buy7Price", "Buy8Price", "Buy9Price", "Buy10Price",
                      "Buy1OrderQty", "Buy2OrderQty", "Buy3OrderQty", "Buy4OrderQty", "Buy5OrderQty",
                     "Buy6OrderQty", "Buy7OrderQty", "Buy8OrderQty", "Buy9OrderQty", "Buy10OrderQty",
                     "Buy1NumOrders", "Buy2NumOrders", "Buy3NumOrders", "Buy4NumOrders", "Buy5NumOrders",
                     "Buy6NumOrders", "Buy7NumOrders", "Buy8NumOrders", "Buy9NumOrders", "Buy10NumOrders",
                     'ff_shares', 'pre_close', 'industry',
                     'after_not_ul_len', 'HTSCSecurityID', 'Ticker', 'pattern', 'dt']

        df["dt"] = pd.to_datetime(df["dt"])
        if tick_type == 'xdb_tickex': # 对tickex执行去重，915筛选
            repeat_filter_cols = ['dt','Ticker','NumTrades', 'TotalVolumeTrade', 'TotalValueTrade', 'LastPx', 'TotalBidQty',
                                  'TotalOfferQty',
                                  'WeightedAvgBidPx', 'WeightedAvgOfferPx', 'TradingPhaseCode'] + \
                                 ['Buy%dPrice' % (i) for i in range(1, 11)] + ['Sell%dPrice' % (i) for i in
                                                                               range(1, 11)] + \
                                 ['Buy%dOrderQty' % (i) for i in range(1, 11)] + ['Sell%dOrderQty' % (i) for i
                                                                                  in
                                                                                  range(1, 11)]
            df['repeat_filter'] = find_repeat_tick(df.copy(), repeat_filter_cols)
            df = df[~df['repeat_filter']]
            df = df[df['MDTime'] >= 91500000]
        df.set_index(["dt", "Ticker"], inplace=True)
        df['VolumeTrade'] = df.groupby(["dt", "Ticker"])['TotalVolumeTrade'].diff().fillna(df['TotalVolumeTrade'])

        df = df[[
            "MDDate", "MDTime", 'appl_seq_num', "NumTrades", "TotalVolumeTrade", "TotalValueTrade", "VolumeTrade",
            "LastPx",
            'ff_shares', 'pattern', 'industry', 'after_not_ul_len', 'pre_close', "OpenPx", "HighPx", "LowPx",
            "TotalBidQty",
            "TotalOfferQty", "WeightedAvgBidPx", "WeightedAvgOfferPx", "Buy1Price", "Buy2Price",
            "Buy3Price", "Buy4Price", "Buy5Price", "Buy6Price", "Buy7Price", "Buy8Price", "Buy9Price",
            "Buy10Price", "Buy1OrderQty", "Buy2OrderQty", "Buy3OrderQty", "Buy4OrderQty", "Buy5OrderQty",
            "Buy6OrderQty", "Buy7OrderQty", "Buy8OrderQty", "Buy9OrderQty", "Buy10OrderQty",
            "Sell1Price", "Sell2Price", "Sell3Price", "Sell4Price", "Sell5Price", "Sell6Price", "Sell7Price",
            "Sell8Price", "Sell9Price", "Sell10Price", "Sell1OrderQty",
            "Sell2OrderQty", "Sell3OrderQty", "Sell4OrderQty", "Sell5OrderQty",
            "Sell6OrderQty", "Sell7OrderQty", "Sell8OrderQty", "Sell9OrderQty",
            "Sell10OrderQty"]]
        for col in ['pre_close', 'VolumeTrade']:
            df[col] = df[col].apply(lambda x: round_(x, 2))
        for col in ['WeightedAvgBidPx', 'WeightedAvgOfferPx']:
            df[col] = df[col].apply(lambda x: round_(x, 3))
        for col in ['ff_shares']:
            df[col] = df[col].apply(lambda x: round_(x, 4))
        # for col in ['industry','after_not_ul_len']:
        #     df[col] = df[col].apply(lambda x : round_(x,1))
        for col in ['pattern']:
            df[col] = df[col].apply(lambda x: int(round_(x, 0)))

    except Exception as e:
        logger.error(
            "Tick数据准备错误！base_date={}, error={}, trace={}".format(base_date, e.__cause__,
                                                                 e.__traceback__))
    return df
def prepare_tickaddorder_data_new(df, base_date):
    try:
        # st = time.time()
        df.columns = ['symbol', "MDDate", "MDTime", "timestamp", "appl_seq_num",
                      "OpenPx", "LastPx", "HighPx", "LowPx", "TotalOfferQty", "TotalBidQty",
                      "WeightedAvgOfferPx", "WeightedAvgBidPx", "TotalVolumeTrade", 'TotalValueTrade', 'VolumeTrade',
                      "NumTrades", 'TradingPhaseCode', 'last_local_index',
                      "Sell1Price", "Sell2Price", "Sell3Price", "Sell4Price", "Sell5Price",
                      "Sell6Price", "Sell7Price", "Sell8Price", "Sell9Price", "Sell10Price",
                      "Sell1OrderQty", "Sell2OrderQty", "Sell3OrderQty", "Sell4OrderQty", "Sell5OrderQty",
                      "Sell6OrderQty", "Sell7OrderQty", "Sell8OrderQty", "Sell9OrderQty", "Sell10OrderQty",
                      "Sell1NumOrders", "Sell2NumOrders", "Sell3NumOrders", "Sell4NumOrders", "Sell5NumOrders",
                      "Sell6NumOrders", "Sell7NumOrders", "Sell8NumOrders", "Sell9NumOrders", "Sell10NumOrders",

                      "Buy1Price", "Buy2Price", "Buy3Price", "Buy4Price", "Buy5Price",
                      "Buy6Price", "Buy7Price", "Buy8Price", "Buy9Price", "Buy10Price",
                      "Buy1OrderQty", "Buy2OrderQty", "Buy3OrderQty", "Buy4OrderQty", "Buy5OrderQty",
                      "Buy6OrderQty", "Buy7OrderQty", "Buy8OrderQty", "Buy9OrderQty", "Buy10OrderQty",
                      "Buy1NumOrders", "Buy2NumOrders", "Buy3NumOrders", "Buy4NumOrders", "Buy5NumOrders",
                      "Buy6NumOrders", "Buy7NumOrders", "Buy8NumOrders", "Buy9NumOrders", "Buy10NumOrders",
                      'OrderType', 'OrderPrice', 'OrderQty',
                      'ff_shares', 'pre_close', 'industry',
                      'after_not_ul_len', 'HTSCSecurityID', 'Ticker', 'pattern', 'dt']

        df["dt"] = pd.to_datetime(df["dt"])
        df.set_index(["dt", "Ticker"], inplace=True)
        df["OrderPrice"].fillna(-1.0, inplace=True)
        df["OrderQty"].fillna(-1.0, inplace=True)
        df['VolumeTrade'] = df.groupby(["dt", "Ticker"])['TotalVolumeTrade'].diff().fillna(df['TotalVolumeTrade'])

        df = df[[
            "MDDate", "MDTime", "NumTrades", "TotalVolumeTrade", "TotalValueTrade", "VolumeTrade", "LastPx",
            'ff_shares', 'pattern', 'industry', 'after_not_ul_len', 'pre_close', "OpenPx", "HighPx", "LowPx",
            "TotalBidQty",
            "TotalOfferQty", "WeightedAvgBidPx", "WeightedAvgOfferPx", "Buy1Price", "Buy2Price",
            "Buy3Price", "Buy4Price", "Buy5Price", "Buy6Price", "Buy7Price", "Buy8Price", "Buy9Price",
            "Buy10Price", "Buy1OrderQty", "Buy2OrderQty", "Buy3OrderQty", "Buy4OrderQty", "Buy5OrderQty",
            "Buy6OrderQty", "Buy7OrderQty", "Buy8OrderQty", "Buy9OrderQty", "Buy10OrderQty",
            "Sell1Price", "Sell2Price", "Sell3Price", "Sell4Price", "Sell5Price", "Sell6Price", "Sell7Price",
            "Sell8Price", "Sell9Price", "Sell10Price", "Sell1OrderQty",
            "Sell2OrderQty", "Sell3OrderQty", "Sell4OrderQty", "Sell5OrderQty",
            "Sell6OrderQty", "Sell7OrderQty", "Sell8OrderQty", "Sell9OrderQty",
            "Sell10OrderQty",
            'appl_seq_num', 'OrderType', 'OrderPrice', 'OrderQty']]
        for col in ['pre_close', 'VolumeTrade']:
            df[col] = df[col].apply(lambda x: round_(x, 2))
        for col in ['WeightedAvgBidPx', 'WeightedAvgOfferPx']:
            df[col] = df[col].apply(lambda x: round_(x, 3))
        for col in ['ff_shares']:
            df[col] = df[col].apply(lambda x: round_(x, 4))
        # for col in ['industry','after_not_ul_len']:
        #     df[col] = df[col].apply(lambda x : round_(x,1))
        for col in ['pattern']:
            df[col] = df[col].apply(lambda x: int(round_(x, 0)))

    except Exception as e:
        logger.error(
            "Tick数据准备错误！base_date={}, error={}, trace={}".format(base_date, e.__cause__,
                                                                 e.__traceback__))
    return df
def prepare_cancel_data_new(df, base_date):
    try:
        df.columns = ['symbol', 'appl_seq_num', 'OrderIndex', 'OrderPrice', 'OrderQty', "MDTime", "order_index",
                      'local_index', "OrderBSFlag", "MDDate", "timestamp",
                      'ff_shares', 'pre_close', 'industry',
                      'after_not_ul_len', 'HTSCSecurityID', 'Ticker', 'pattern', 'dt']
        df["dt"] = pd.to_datetime(df["dt"])
        df['OrderBSFlag'] = df['OrderBSFlag'].apply(lambda x: int(x))
        df.set_index(["dt", "Ticker"], inplace=True)
        df['zcz'] = (((df.reset_index()['Ticker'].apply(lambda x: x[0] == '3')) & (
                    df.reset_index()['dt'] >= '2020-08-24')) | (
                         df.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
        df['ul_price'] = np.floor(df['pre_close'] * 100 * 1.1 + 0.5 + 1e-8) / 100
        df['ul_price'][df['zcz']] = np.floor(df['pre_close'] * 100 * 1.2 + 0.5 + 1e-8) / 100
        df['dl_price'] = np.floor(df['pre_close'] * 100 * 0.9 + 0.5 + 1e-8) / 100
        df['dl_price'][df['zcz']] = np.floor(df['pre_close'] * 100 * 0.8 + 0.5 + 1e-8) / 100
        df = df[['MDDate', 'MDTime', 'appl_seq_num', 'OrderIndex', 'OrderPrice', 'OrderQty', 'OrderBSFlag',
                 'ff_shares', 'pattern', 'industry', 'after_not_ul_len', 'pre_close', 'ul_price', 'dl_price']]
        for col in ['OrderPrice', 'pre_close', 'ul_price', 'dl_price']:
            df[col] = df[col].apply(lambda x: round_(x, 2))
        for col in ['ff_shares']:
            df[col] = df[col].apply(lambda x: round_(x, 4))
        for col in ['pattern']:
            df[col] = df[col].apply(lambda x: int(round_(x, 0)))
    except Exception as e:
        logger.error(
            "Order数据准备错误！base_date={}, error={}, trace={}".format(base_date, e.__cause__,
                                                                  e.__traceback__))
    return df
def prepare_order1m_data_new(df, base_date):
    try:
        df = df.rename(columns = {
            'md_date':'MDDate',
            'md_time':'MDTime',
        })
        used_columns = ['MDDate','MDTime','appl_seq_num_min','appl_seq_num_max',
                        'OrderPrice_buy_type1_mean','OrderPrice_buy_type2_mean','OrderPrice_buy_type3_mean',
                        'OrderPrice_sell_type1_mean','OrderPrice_sell_type2_mean','OrderPrice_sell_type3_mean',
                        'OrderPrice_buy_mean','OrderPrice_sell_mean',
                        'OrderAmt_buy_type1','OrderAmt_buy_type2','OrderAmt_buy_type3',
                        'OrderAmt_sell_type1','OrderAmt_sell_type2','OrderAmt_sell_type3',
                        'OrderAmt_buy','OrderAmt_sell',
                        'OrderQty_buy_type1','OrderQty_buy_type2','OrderQty_buy_type3',
                        'OrderQty_sell_type1','OrderQty_sell_type2','OrderQty_sell_type3',
                        'OrderQty_buy','OrderQty_sell',
                        'OrderNum_buy_type1','OrderNum_buy_type2','OrderNum_buy_type3',
                        'OrderNum_sell_type1','OrderNum_sell_type2','OrderNum_sell_type3',
                        'OrderNum_buy','OrderNum_sell',
                        'ff_shares','pattern','industry','after_not_ul_len','pre_close','ul_price','dl_price']
        df["dt"] = pd.to_datetime(df["dt"])
        df.set_index(["dt", "Ticker"], inplace=True)
        df['zcz'] = (((df.reset_index()['Ticker'].apply(lambda x: x[0] == '3')) & (
                    df.reset_index()['dt'] >= '2020-08-24')) | (
                         df.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
        df['ul_price'] = np.floor(df['pre_close'] * 100 * 1.1 + 0.5 + 1e-8) / 100
        df['ul_price'][df['zcz']] = np.floor(df['pre_close'] * 100 * 1.2 + 0.5 + 1e-8) / 100
        df['dl_price'] = np.floor(df['pre_close'] * 100 * 0.9 + 0.5 + 1e-8) / 100
        df['dl_price'][df['zcz']] = np.floor(df['pre_close'] * 100 * 0.8 + 0.5 + 1e-8) / 100
        df = df[used_columns]
        for col in ['pre_close', 'ul_price', 'dl_price']:
            df[col] = df[col].apply(lambda x: round_(x, 2))
        for col in ['OrderPrice_buy_type1_mean','OrderPrice_buy_type2_mean','OrderPrice_buy_type3_mean',
                    'OrderPrice_sell_type1_mean','OrderPrice_sell_type2_mean','OrderPrice_sell_type3_mean',
                    'OrderPrice_buy_mean','OrderPrice_sell_mean',]:
            df[col] = df[col].apply(lambda x: round_(x, 5))
        for col in ['OrderAmt_buy_type1','OrderAmt_buy_type2','OrderAmt_buy_type3',
                    'OrderAmt_sell_type1','OrderAmt_sell_type2','OrderAmt_sell_type3',
                    'OrderAmt_buy','OrderAmt_sell',]:
            df[col] = df[col].apply(lambda x: round_(x, 2))
        for col in ['OrderQty_buy_type1','OrderQty_buy_type2','OrderQty_buy_type3',
                    'OrderQty_sell_type1','OrderQty_sell_type2','OrderQty_sell_type3',
                    'OrderQty_buy','OrderQty_sell',
                    'OrderNum_buy_type1','OrderNum_buy_type2','OrderNum_buy_type3',
                    'OrderNum_sell_type1','OrderNum_sell_type2','OrderNum_sell_type3',
                    'OrderNum_buy','OrderNum_sell',]:
            df[col] = df[col].apply(lambda x: int(round_(x, 0)) if not np.isnan(x) else x)
        for col in ['ff_shares']:
            df[col] = df[col].apply(lambda x: round_(x, 4))
        for col in ['pattern']:
            df[col] = df[col].apply(lambda x: int(round_(x, 0)))
    except Exception as e:
        logger.error(
            "Order1m数据准备错误！base_date={}, error={}, trace={}".format(base_date, e.__cause__,
                                                                  e.__traceback__))
    return df
def prepare_tick1m_data_new(df, base_date):
    try:
        df = df.rename(columns = {
            'md_date':'MDDate',
            'md_time':'MDTime',
            'num_trades':'NumTrades',
            'total_volume':'TotalVolumeTrade',
            'total_amount':'TotalValueTrade',
            'volume':'VolumeTrade',
            'last_px':'LastPx',
            'last_px_mean':'LastPx_mean',
            'open_px':'OpenPx',
            'open_1m':'OpenPx_1m',
            'high_px':'HighPx',
            'high_1m':'HighPx_1m',
            'low_px':'LowPx',
            'low_1m':'LowPx_1m',
            'bid_order_qty':'TotalBidQty',
            'bid_order_qty_mean':'TotalBidQty_mean',
            'ask_order_qty':'TotalOfferQty',
            'ask_order_qty_mean':'TotalOfferQty_mean',
            'bid_avg_px':'WeightedAvgBidPx',
            'bid_avg_price_mean':'WeightedAvgBidPx_mean',
            'ask_avg_px':'WeightedAvgOfferPx',
            'ask_avg_price_mean':'WeightedAvgOfferPx_mean',
        })
        rename_dict_1_10 = {}
        for i in range(1,11):
            rename_dict_1_10[f'bid_price{i}'] = f'Buy{i}Price'
            rename_dict_1_10[f'ask_price{i}'] = f'Sell{i}Price'
            rename_dict_1_10[f'bid_qty{i}'] = f'Buy{i}OrderQty'
            rename_dict_1_10[f'ask_qty{i}'] = f'Sell{i}OrderQty'
        df = df.rename(columns=rename_dict_1_10)
        used_columns = ['MDDate','MDTime','appl_seq_num_min','appl_seq_num_max','NumTrades',
                        'TotalVolumeTrade','TotalValueTrade','VolumeTrade',
                        'LastPx','LastPx_mean','OpenPx','OpenPx_1m','HighPx','HighPx_1m','LowPx','LowPx_1m',
                        'TotalBidQty','TotalBidQty_mean','TotalOfferQty','TotalOfferQty_mean',
                        'WeightedAvgBidPx','WeightedAvgBidPx_mean','WeightedAvgOfferPx','WeightedAvgOfferPx_mean',
                        'ff_shares','pattern','industry','after_not_ul_len','pre_close','ul_price','dl_price'] \
                        + ['Buy%dPrice' % (i) for i in range(1, 11)] + ['Sell%dPrice' % (i) for i in range(1, 11)] \
                        + ['Buy%dOrderQty' % (i) for i in range(1, 11)] + ['Sell%dOrderQty' % (i) for i in range(1, 11)]

        df["dt"] = pd.to_datetime(df["dt"])
        df.set_index(["dt", "Ticker"], inplace=True)
        df['zcz'] = (((df.reset_index()['Ticker'].apply(lambda x: x[0] == '3')) & (
                    df.reset_index()['dt'] >= '2020-08-24')) | (
                         df.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
        df['ul_price'] = np.floor(df['pre_close'] * 100 * 1.1 + 0.5 + 1e-8) / 100
        df['ul_price'][df['zcz']] = np.floor(df['pre_close'] * 100 * 1.2 + 0.5 + 1e-8) / 100
        df['dl_price'] = np.floor(df['pre_close'] * 100 * 0.9 + 0.5 + 1e-8) / 100
        df['dl_price'][df['zcz']] = np.floor(df['pre_close'] * 100 * 0.8 + 0.5 + 1e-8) / 100
        df = df[used_columns]
        for col in ['pre_close', 'ul_price', 'dl_price', 'OpenPx', 'LastPx', 'HighPx', 'LowPx',
                    'OpenPx_1m', 'HighPx_1m', 'LowPx_1m']:
            df[col] = df[col].apply(lambda x: round_(x, 2))
        for col in ['LastPx_mean', 'TotalBidQty_mean', 'TotalOfferQty_mean',
                    'WeightedAvgBidPx_mean', 'WeightedAvgOfferPx_mean', 'WeightedAvgBidPx', 'WeightedAvgOfferPx']:
            df[col] = df[col].apply(lambda x: round_(x, 5))
        for col in ['ff_shares']:
            df[col] = df[col].apply(lambda x: round_(x, 4))
        for col in ['pattern']:
            df[col] = df[col].apply(lambda x: int(round_(x, 0)))
    except Exception as e:
        logger.error(
            "Tick1m数据准备错误！base_date={}, error={}, trace={}".format(base_date, e.__cause__,
                                                                  e.__traceback__))
    return df

def get_data(base_path, data_name, dates, xdb_datasource, basic_dict):
    industry = basic_dict["industry"]
    md_df = basic_dict["md_df"]
    idx = pd.IndexSlice
    result = {}
    for k, v in basic_dict.items():
        if (k == "industry") | (k == 'md_df'):
            continue

        basic = v
        symbols = [i[1] for i in basic.loc[dates[-1]].index.values]
        strategy = k
        backup_index = 0
        if data_name == "xdb_order":
            for symbol in symbols:
                if symbol in result:
                    continue
                df_list = []

                date_li = dates[::-1][1:]
                cnt = 0
                for date in date_li:
                    try:
                        if md_df.loc[(pd.Timestamp(date), symbol),'amt'] <= 0:
                            continue
                        else:
                            pass
                    except:
                        pass
                    if symbol == "001914.SZ" and dates[-1] >= str(20191216) and date < str(20191216):
                        order_df = xdb_datasource.get_order(date, "000043.SZ")
                    elif symbol == "001872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        order_df = xdb_datasource.get_order(date, "000022.SZ")
                    elif symbol == "201872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        order_df = xdb_datasource.get_order(date, "200022.SZ")
                    elif symbol == "601360.SH" and dates[-1] >= str(20180228) and date < str(20180228):
                        order_df = xdb_datasource.get_order(date, "601313.SH")
                    else:
                        order_df = xdb_datasource.get_order(date, symbol)
                    if (md_df.loc[idx[date:date, symbol:symbol], :]['amt'].empty) or (
                    not md_df.loc[idx[date:date, symbol:symbol], :]['amt'].values[0] > 0):  # 强制把停牌日的置为空tick_df
                        order_df = pd.DataFrame()
                    if order_df.empty:
                        logger.warning("Empty dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                        continue
                    if symbol == "000043.SZ" and date < str(20191216):
                        daily_df = xdb_datasource.get_dailydata(date, "001914.SZ")
                    elif symbol == "000022.SZ" and date < str(20181226):
                        daily_df = xdb_datasource.get_dailydata(date, "001872.SZ")
                    elif symbol == "200022.SZ" and date < str(20181226):
                        daily_df = xdb_datasource.get_dailydata(date, "201872.SZ")
                    elif symbol == "601313.SH" and date < str(20180228):
                        daily_df = xdb_datasource.get_dailydata(date, "601360.SH")
                    else:
                        daily_df = xdb_datasource.get_dailydata(date, symbol)
                    if daily_df.empty:
                        logger.error("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                        raise RuntimeError("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                    order_df["ff_shares"] = daily_df["float_a_shr_today"].values[0]
                    order_df["pre_close"] = daily_df["pre_close"].values[0]
                    df_list.insert(0, order_df)
                    cnt += 1
                    if cnt == lag:
                        break
                if df_list:
                    tmp_df = pd.concat(df_list)
                else:
                    tmp_df = pd.DataFrame()
                    result[symbol] = tmp_df
                    continue
                try:
                    tmp_df["industry"] = industry.loc[dates[-2], symbol].values[0]
                except Exception as e:
                    logger.warning("Industry label not found! date={}, symbol={}".format(dates[-1], symbol))
                    tmp_df["industry"] = np.nan
                tmp_df["after_not_ul_len"] = basic.loc[dates[-1], symbol]["after_not_ul_len"]
                tmp_df["HTSCSecurityID"] = symbol
                tmp_df["Ticker"] = symbol
                if strategy == "saturn" or strategy == "sell":
                    tmp_df["pattern"] = basic.loc[dates[-1], symbol]["lzt_label_pattern"]
                else:
                    tmp_df["pattern"] = -1

                tmp_df["dt"] = dates[-1]
                tmp_df = prepare_order_data_new(tmp_df, dates[-1])

                result[symbol] = tmp_df

        elif data_name == "xdb_trade":
            for symbol in symbols:
                if symbol in result:
                    continue
                df_list = []
                date_li = dates[::-1][1:]
                cnt = 0
                for date in date_li:
                    try:
                        if md_df.loc[(pd.Timestamp(date), symbol),'amt'] <= 0:
                            continue
                        else:
                            pass
                    except:
                        pass
                    if symbol == "001914.SZ" and dates[-1] >= str(20191216) and date < str(20191216):
                        trade_df = xdb_datasource.get_trade(date, "000043.SZ")
                    elif symbol == "001872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        trade_df = xdb_datasource.get_trade(date, "000022.SZ")
                    elif symbol == "201872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        trade_df = xdb_datasource.get_trade(date, "200022.SZ")
                    elif symbol == "601360.SH" and dates[-1] >= str(20180228) and date < str(20180228):
                        trade_df = xdb_datasource.get_trade(date, "601313.SH")
                    else:
                        trade_df = xdb_datasource.get_trade(date, symbol)
                    if (md_df.loc[idx[date:date, symbol:symbol], :]['amt'].empty) or (
                    not md_df.loc[idx[date:date, symbol:symbol], :]['amt'].values[0] > 0):  # 强制把停牌日的置为空tick_df
                        trade_df = pd.DataFrame()
                    if trade_df.empty:
                        logger.warning("Empty dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                        continue

                    if symbol == "000043.SZ" and date < str(20191216):
                        daily_df = xdb_datasource.get_dailydata(date, "001914.SZ")
                    elif symbol == "000022.SZ" and date < str(20181226):
                        daily_df = xdb_datasource.get_dailydata(date, "001872.SZ")
                    elif symbol == "200022.SZ" and date < str(20181226):
                        daily_df = xdb_datasource.get_dailydata(date, "201872.SZ")
                    elif symbol == "601313.SH" and date < str(20180228):
                        daily_df = xdb_datasource.get_dailydata(date, "601360.SH")
                    else:
                        daily_df = xdb_datasource.get_dailydata(date, symbol)

                    if daily_df.empty:
                        logger.error("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                        raise RuntimeError("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                    trade_df["ff_shares"] = daily_df["float_a_shr_today"].values[0]
                    trade_df["pre_close"] = daily_df["pre_close"].values[0]
                    df_list.insert(0, trade_df)
                    cnt += 1
                    if cnt == lag:
                        break

                if df_list:
                    tmp_df = pd.concat(df_list)
                else:
                    tmp_df = pd.DataFrame()
                    result[symbol] = tmp_df
                    continue

                try:
                    tmp_df["industry"] = industry.loc[dates[-2], symbol].values[0]
                except Exception as e:
                    logger.warning("Industry label not found! date={}, symbol={}".format(dates[-1], symbol))
                    tmp_df["industry"] = np.nan
                tmp_df["after_not_ul_len"] = basic.loc[dates[-1], symbol]["after_not_ul_len"]
                tmp_df["HTSCSecurityID"] = symbol
                tmp_df["Ticker"] = symbol
                if strategy == "saturn" or strategy == "sell":
                    tmp_df["pattern"] = basic.loc[dates[-1], symbol]["lzt_label_pattern"]
                else:
                    tmp_df["pattern"] = -1

                tmp_df["dt"] = dates[-1]
                tmp_df = prepare_trade_data_new(tmp_df, dates[-1])
                result[symbol] = tmp_df

        elif data_name == "xdb_cancel":
            # logger.warning("xdb_cancel not supported at this time.")
            for symbol in symbols:
                if symbol in result:
                    continue
                df_list = []
                date_li = dates[::-1][1:]
                cnt = 0
                for date in date_li:
                    try:
                        if md_df.loc[(pd.Timestamp(date), symbol),'amt'] <= 0:
                            continue
                        else:
                            pass
                    except:
                        pass
                    if symbol == "001914.SZ" and dates[-1] >= str(20191216) and date < str(20191216):
                        order_df = xdb_datasource.get_cancel(date, "000043.SZ")
                    elif symbol == "001872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        order_df = xdb_datasource.get_cancel(date, "000022.SZ")
                    elif symbol == "201872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        order_df = xdb_datasource.get_cancel(date, "200022.SZ")
                    elif symbol == "601360.SH" and dates[-1] >= str(20180228) and date < str(20180228):
                        order_df = xdb_datasource.get_cancel(date, "601313.SH")
                    else:
                        order_df = xdb_datasource.get_cancel(date, symbol)
                    if (md_df.loc[idx[date:date, symbol:symbol], :]['amt'].empty) or (
                            not md_df.loc[idx[date:date, symbol:symbol], :]['amt'].values[0] > 0):  # 强制把停牌日的置为空tick_df
                        order_df = pd.DataFrame()
                    if order_df.empty:
                        logger.warning("Empty dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                        continue
                    if symbol == "000043.SZ" and date < str(20191216):
                        daily_df = xdb_datasource.get_dailydata(date, "001914.SZ")
                    elif symbol == "000022.SZ" and date < str(20181226):
                        daily_df = xdb_datasource.get_dailydata(date, "001872.SZ")
                    elif symbol == "200022.SZ" and date < str(20181226):
                        daily_df = xdb_datasource.get_dailydata(date, "201872.SZ")
                    elif symbol == "601313.SH" and date < str(20180228):
                        daily_df = xdb_datasource.get_dailydata(date, "601360.SH")
                    else:
                        daily_df = xdb_datasource.get_dailydata(date, symbol)
                    if daily_df.empty:
                        logger.error(
                            "Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                        raise RuntimeError(
                            "Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                    order_df["ff_shares"] = daily_df["float_a_shr_today"].values[0]
                    order_df["pre_close"] = daily_df["pre_close"].values[0]
                    df_list.insert(0, order_df)
                    cnt += 1
                    if cnt == lag:
                        break
                if df_list:
                    tmp_df = pd.concat(df_list)
                else:
                    tmp_df = pd.DataFrame()
                    result[symbol] = tmp_df
                    continue
                try:
                    tmp_df["industry"] = industry.loc[dates[-2], symbol].values[0]
                except Exception as e:
                    logger.warning("Industry label not found! date={}, symbol={}".format(dates[-1], symbol))
                    tmp_df["industry"] = np.nan
                tmp_df["after_not_ul_len"] = basic.loc[dates[-1], symbol]["after_not_ul_len"]
                tmp_df["HTSCSecurityID"] = symbol
                tmp_df["Ticker"] = symbol
                if strategy == "saturn" or strategy == "sell":
                    tmp_df["pattern"] = basic.loc[dates[-1], symbol]["lzt_label_pattern"]
                else:
                    tmp_df["pattern"] = -1

                tmp_df["dt"] = dates[-1]
                tmp_df = prepare_cancel_data_new(tmp_df, dates[-1])

                result[symbol] = tmp_df

        elif data_name == "xdb_tick1s":
            for symbol in symbols:
                if symbol in result:
                    continue
                df_list = []
                date_li = dates[::-1][1:]
                cnt = 0
                for date in date_li:
                    try:
                        if md_df.loc[(pd.Timestamp(date), symbol),'amt'] <= 0:
                            continue
                        else:
                            pass
                    except:
                        pass
                    if symbol == "001914.SZ" and dates[-1] >= str(20191216) and date < str(20191216):
                        tick1s_df = xdb_datasource.get_tick1s(date, "000043.SZ")
                    elif symbol == "001872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        tick1s_df = xdb_datasource.get_tick1s(date, "000022.SZ")
                    elif symbol == "201872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        tick1s_df = xdb_datasource.get_tick1s(date, "200022.SZ")
                    elif symbol == "601360.SH" and dates[-1] >= str(20180228) and date < str(20180228):
                        tick1s_df = xdb_datasource.get_tick1s(date, "601313.SH")
                    else:
                        tick1s_df = xdb_datasource.get_tick1s(date, symbol)
                    if (md_df.loc[idx[date:date, symbol:symbol], :]['amt'].empty) or (
                    not md_df.loc[idx[date:date, symbol:symbol], :]['amt'].values[0] > 0):  # 强制把停牌日的置为空tick_df
                        tick1s_df = pd.DataFrame()
                    if tick1s_df.empty:
                        logger.warning("Empty dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                        continue

                    if symbol == "000043.SZ" and date < str(20191216):
                        daily_df = xdb_datasource.get_dailydata(date, "001914.SZ")
                    elif symbol == "000022.SZ" and date < str(20181226):
                        daily_df = xdb_datasource.get_dailydata(date, "001872.SZ")
                    elif symbol == "200022.SZ" and date < str(20181226):
                        daily_df = xdb_datasource.get_dailydata(date, "201872.SZ")
                    elif symbol == "601313.SH" and date < str(20180228):
                        daily_df = xdb_datasource.get_dailydata(date, "601360.SH")
                    else:
                        daily_df = xdb_datasource.get_dailydata(date, symbol)

                    if daily_df.empty:
                        logger.error("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                        raise RuntimeError("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))

                    tick1s_df["ff_shares"] = daily_df["float_a_shr_today"].values[0]
                    tick1s_df["pre_close"] = daily_df["pre_close"].values[0]

                    df_list.insert(0, tick1s_df)
                    cnt += 1
                    if cnt == lag:
                        break
                if df_list:
                    tmp_df = pd.concat(df_list)
                else:
                    tmp_df = pd.DataFrame()
                    result[symbol] = tmp_df
                    continue
                try:
                    tmp_df["industry"] = industry.loc[dates[-2], symbol].values[0]
                except Exception as e:
                    logger.warning("Industry label not found! date={}, symbol={}".format(dates[-1], symbol))
                    tmp_df["industry"] = np.nan
                tmp_df["after_not_ul_len"] = basic.loc[dates[-1], symbol]["after_not_ul_len"]
                tmp_df["HTSCSecurityID"] = symbol
                tmp_df["Ticker"] = symbol
                if strategy == "saturn" or strategy == "sell":
                    tmp_df["pattern"] = basic.loc[dates[-1], symbol]["lzt_label_pattern"]
                else:
                    tmp_df["pattern"] = -1

                tmp_df["dt"] = dates[-1]
                tmp_df = prepare_tick_data_new(tmp_df, dates[-1], data_name)
                result[symbol] = tmp_df

        elif data_name == "xdb_tickfull":
            for symbol in symbols:
                if symbol in result:
                    continue
                df_list = []
                date_li = dates[::-1][1:]
                cnt = 0
                for date in date_li:
                    try:
                        if md_df.loc[(pd.Timestamp(date), symbol),'amt'] <= 0:
                            continue
                        else:
                            pass
                    except:
                        pass
                    if symbol == "001914.SZ" and dates[-1] >= str(20191216) and date < str(20191216):
                        tickfull_df = xdb_datasource.get_tickfull(date, "000043.SZ")
                    elif symbol == "001872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        tickfull_df = xdb_datasource.get_tickfull(date, "000022.SZ")
                    elif symbol == "201872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        tickfull_df = xdb_datasource.get_tickfull(date, "200022.SZ")
                    elif symbol == "601360.SH" and dates[-1] >= str(20180228) and date < str(20180228):
                        tickfull_df = xdb_datasource.get_tickfull(date, "601313.SH")
                    else:
                        tickfull_df = xdb_datasource.get_tickfull(date, symbol)
                    if (md_df.loc[idx[date:date, symbol:symbol], :]['amt'].empty) or (
                    not md_df.loc[idx[date:date, symbol:symbol], :]['amt'].values[0] > 0):  # 强制把停牌日的置为空tick_df
                        tickfull_df = pd.DataFrame()
                    if tickfull_df.empty:
                        logger.warning("Empty dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                        continue

                    if symbol == "000043.SZ" and date < str(20191216):
                        daily_df = xdb_datasource.get_dailydata(date, "001914.SZ")
                    elif symbol == "000022.SZ" and date < str(20181226):
                        daily_df = xdb_datasource.get_dailydata(date, "001872.SZ")
                    elif symbol == "200022.SZ" and date < str(20181226):
                        daily_df = xdb_datasource.get_dailydata(date, "201872.SZ")
                    elif symbol == "601313.SH" and date < str(20180228):
                        daily_df = xdb_datasource.get_dailydata(date, "601360.SH")
                    else:
                        daily_df = xdb_datasource.get_dailydata(date, symbol)
                    if daily_df.empty:
                        logger.error("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                        raise RuntimeError("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                    tickfull_df["ff_shares"] = daily_df["float_a_shr_today"].values[0]
                    tickfull_df["pre_close"] = daily_df["pre_close"].values[0]

                    df_list.insert(0, tickfull_df)
                    cnt += 1
                    if cnt == lag:
                        break
                if df_list:
                    tmp_df = pd.concat(df_list)
                else:
                    tmp_df = pd.DataFrame()
                    result[symbol] = tmp_df
                    continue
                try:
                    tmp_df["industry"] = industry.loc[dates[-2], symbol].values[0]
                except Exception as e:
                    logger.warning("Industry label not found! date={}, symbol={}".format(dates[-1], symbol))
                    tmp_df["industry"] = np.nan
                tmp_df["after_not_ul_len"] = basic.loc[dates[-1], symbol]["after_not_ul_len"]
                tmp_df["HTSCSecurityID"] = symbol
                tmp_df["Ticker"] = symbol
                if strategy == "saturn" or strategy == "sell":
                    tmp_df["pattern"] = basic.loc[dates[-1], symbol]["lzt_label_pattern"]
                else:
                    tmp_df["pattern"] = -1

                tmp_df["dt"] = dates[-1]
                tmp_df = prepare_tick_data_new(tmp_df, dates[-1], data_name)
                result[symbol] = tmp_df
        elif data_name == 'xdb_tickfulladdorder':
            for symbol in symbols:
                if symbol in result:
                    continue
                df_list = []
                date_li = dates[::-1][1:]
                cnt = 0
                for date in date_li:
                    try:
                        if md_df.loc[(pd.Timestamp(date), symbol),'amt'] <= 0:
                            continue
                        else:
                            pass
                    except:
                        pass
                    if symbol == "001914.SZ" and dates[-1] >= str(20191216) and date < str(20191216):
                        tickfull_df = xdb_datasource.get_entickfull(date, "000043.SZ")
                    elif symbol == "001872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        tickfull_df = xdb_datasource.get_entickfull(date, "000022.SZ")
                    elif symbol == "201872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        tickfull_df = xdb_datasource.get_entickfull(date, "200022.SZ")
                    elif symbol == "601360.SH" and dates[-1] >= str(20180228) and date < str(20180228):
                        tickfull_df = xdb_datasource.get_entickfull(date, "601313.SH")
                    else:
                        tickfull_df = xdb_datasource.get_entickfull(date, symbol)
                    if (md_df.loc[idx[date:date, symbol:symbol], :]['amt'].empty) or (
                    not md_df.loc[idx[date:date, symbol:symbol], :]['amt'].values[0] > 0):  # 强制把停牌日的置为空tick_df
                        tickfull_df = pd.DataFrame()
                    if tickfull_df.empty:
                        logger.warning("Empty dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                        continue

                    if symbol == "000043.SZ" and date < str(20191216):
                        daily_df = xdb_datasource.get_dailydata(date, "001914.SZ")
                    elif symbol == "000022.SZ" and date < str(20181226):
                        daily_df = xdb_datasource.get_dailydata(date, "001872.SZ")
                    elif symbol == "200022.SZ" and date < str(20181226):
                        daily_df = xdb_datasource.get_dailydata(date, "201872.SZ")
                    elif symbol == "601313.SH" and date < str(20180228):
                        daily_df = xdb_datasource.get_dailydata(date, "601360.SH")
                    else:
                        daily_df = xdb_datasource.get_dailydata(date, symbol)
                    if daily_df.empty:
                        logger.error(
                            "Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                        raise RuntimeError(
                            "Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                    tickfull_df["ff_shares"] = daily_df["float_a_shr_today"].values[0]
                    tickfull_df["pre_close"] = daily_df["pre_close"].values[0]

                    df_list.insert(0, tickfull_df)
                    cnt += 1
                    if cnt == lag:
                        break
                if df_list:
                    tmp_df = pd.concat(df_list)
                else:
                    tmp_df = pd.DataFrame()
                    result[symbol] = tmp_df
                    continue
                try:
                    tmp_df["industry"] = industry.loc[dates[-2], symbol].values[0]
                except Exception as e:
                    logger.warning("Industry label not found! date={}, symbol={}".format(dates[-1], symbol))
                    tmp_df["industry"] = np.nan
                tmp_df["after_not_ul_len"] = basic.loc[dates[-1], symbol]["after_not_ul_len"]
                tmp_df["HTSCSecurityID"] = symbol
                tmp_df["Ticker"] = symbol
                if strategy == "saturn" or strategy == "sell":
                    tmp_df["pattern"] = basic.loc[dates[-1], symbol]["lzt_label_pattern"]
                else:
                    tmp_df["pattern"] = -1

                tmp_df["dt"] = dates[-1]
                tmp_df = prepare_tickaddorder_data_new(tmp_df, dates[-1])
                result[symbol] = tmp_df
        elif data_name == "xdb_tickex":
            for symbol in symbols:
                if symbol in result:
                    continue
                df_list = []
                date_li = dates[::-1][1:]
                cnt = 0
                for date in date_li:
                    try:
                        if md_df.loc[(pd.Timestamp(date), symbol),'amt'] <= 0:
                            continue
                        else:
                            pass
                    except:
                        pass
                    if symbol == "001914.SZ" and dates[-1] >= str(20191216) and date < str(20191216):
                        tickex_df = xdb_datasource.get_tickex(date, "000043.SZ")
                    elif symbol == "001872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        tickex_df = xdb_datasource.get_tickex(date, "000022.SZ")
                    elif symbol == "201872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        tickex_df = xdb_datasource.get_tickex(date, "200022.SZ")
                    elif symbol == "601360.SH" and dates[-1] >= str(20180228) and date < str(20180228):
                        tickex_df = xdb_datasource.get_tickex(date, "601313.SH")
                    else:
                        tickex_df = xdb_datasource.get_tickex(date, symbol)
                    if (md_df.loc[idx[date:date, symbol:symbol], :]['amt'].empty) or (
                    not md_df.loc[idx[date:date, symbol:symbol], :]['amt'].values[0] > 0):  # 强制把停牌日的置为空tick_df
                        tickex_df = pd.DataFrame()
                    if tickex_df.empty:
                        logger.warning("Empty dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                        continue

                    if symbol == "000043.SZ" and date < str(20191216):
                        daily_df = xdb_datasource.get_dailydata(date, "001914.SZ")
                    elif symbol == "000022.SZ" and date < str(20181226):
                        daily_df = xdb_datasource.get_dailydata(date, "001872.SZ")
                    elif symbol == "200022.SZ" and date < str(20181226):
                        daily_df = xdb_datasource.get_dailydata(date, "201872.SZ")
                    elif symbol == "601313.SH" and date < str(20180228):
                        daily_df = xdb_datasource.get_dailydata(date, "601360.SH")
                    else:
                        daily_df = xdb_datasource.get_dailydata(date, symbol)

                    if daily_df.empty:
                        logger.error(
                            "Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                        raise RuntimeError(
                            "Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))

                    tickex_df["ff_shares"] = daily_df["float_a_shr_today"].values[0]
                    tickex_df["pre_close"] = daily_df["pre_close"].values[0]

                    df_list.insert(0, tickex_df)
                    cnt += 1
                    if cnt == lag:
                        break
                if df_list:
                    tmp_df = pd.concat(df_list)
                else:
                    tmp_df = pd.DataFrame()
                    result[symbol] = tmp_df
                    continue
                try:
                    tmp_df["industry"] = industry.loc[dates[-2], symbol].values[0]
                except Exception as e:
                    logger.warning("Industry label not found! date={}, symbol={}".format(dates[-1], symbol))
                    tmp_df["industry"] = np.nan
                tmp_df["after_not_ul_len"] = basic.loc[dates[-1], symbol]["after_not_ul_len"]
                tmp_df["HTSCSecurityID"] = symbol
                tmp_df["Ticker"] = symbol
                if strategy == "saturn" or strategy == "sell":
                    tmp_df["pattern"] = basic.loc[dates[-1], symbol]["lzt_label_pattern"]
                else:
                    tmp_df["pattern"] = -1

                tmp_df["dt"] = dates[-1]
                tmp_df = prepare_tick_data_new(tmp_df, dates[-1],data_name)
                result[symbol] = tmp_df
        elif data_name == "xdb_order1m":
            for symbol in symbols:
                if symbol in result:
                    continue
                df_list = []

                date_li = dates[::-1][1:]
                cnt = 0
                for date in date_li:
                    print('xdb_order1m',date,symbol)
                    try:
                        if md_df.loc[(pd.Timestamp(date), symbol),'amt'] <= 0:
                            continue
                        else:
                            pass
                    except:
                        pass
                    if symbol == "001914.SZ" and dates[-1] >= str(20191216) and date < str(20191216):
                        order_df = xdb_datasource.get_order_1min(date, "000043.SZ")
                    elif symbol == "001872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        order_df = xdb_datasource.get_order_1min(date, "000022.SZ")
                    elif symbol == "201872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        order_df = xdb_datasource.get_order_1min(date, "200022.SZ")
                    elif symbol == "601360.SH" and dates[-1] >= str(20180228) and date < str(20180228):
                        order_df = xdb_datasource.get_order_1min(date, "601313.SH")
                    else:
                        order_df = xdb_datasource.get_order_1min(date, symbol)
                    if (md_df.loc[idx[date:date, symbol:symbol], :]['amt'].empty) or (
                    not md_df.loc[idx[date:date, symbol:symbol], :]['amt'].values[0] > 0):  # 强制把停牌日的置为空tick_df
                        order_df = pd.DataFrame()
                    if order_df.empty:
                        logger.warning("Empty dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                        continue
                    if symbol == "000043.SZ" and date < str(20191216):
                        daily_df = xdb_datasource.get_dailydata(date, "001914.SZ")
                    elif symbol == "000022.SZ" and date < str(20181226):
                        daily_df = xdb_datasource.get_dailydata(date, "001872.SZ")
                    elif symbol == "200022.SZ" and date < str(20181226):
                        daily_df = xdb_datasource.get_dailydata(date, "201872.SZ")
                    elif symbol == "601313.SH" and date < str(20180228):
                        daily_df = xdb_datasource.get_dailydata(date, "601360.SH")
                    else:
                        daily_df = xdb_datasource.get_dailydata(date, symbol)
                    if daily_df.empty:
                        logger.error("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                        raise RuntimeError("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                    order_df["ff_shares"] = daily_df["float_a_shr_today"].values[0]
                    order_df["pre_close"] = daily_df["pre_close"].values[0]
                    df_list.insert(0, order_df)
                    cnt += 1
                    if cnt == lag:
                        break
                if df_list:
                    tmp_df = pd.concat(df_list)
                else:
                    tmp_df = pd.DataFrame()
                    result[symbol] = tmp_df
                    continue
                try:
                    tmp_df["industry"] = industry.loc[dates[-2], symbol].values[0]
                except Exception as e:
                    logger.warning("Industry label not found! date={}, symbol={}".format(dates[-1], symbol))
                    tmp_df["industry"] = np.nan
                tmp_df["after_not_ul_len"] = basic.loc[dates[-1], symbol]["after_not_ul_len"]
                tmp_df["HTSCSecurityID"] = symbol
                tmp_df["Ticker"] = symbol
                if strategy == "saturn" or strategy == "sell":
                    tmp_df["pattern"] = basic.loc[dates[-1], symbol]["lzt_label_pattern"]
                else:
                    tmp_df["pattern"] = -1

                tmp_df["dt"] = dates[-1]
                tmp_df = prepare_order1m_data_new(tmp_df, dates[-1])

                result[symbol] = tmp_df
        elif data_name == "xdb_tick1m":
            for symbol in symbols:
                if symbol in result:
                    continue
                df_list = []

                date_li = dates[::-1][1:]
                cnt = 0
                for date in date_li:
                    print('xdb_tick1m',date,symbol)
                    try:
                        if md_df.loc[(pd.Timestamp(date), symbol),'amt'] <= 0:
                            continue
                        else:
                            pass
                    except:
                        pass
                    if symbol == "001914.SZ" and dates[-1] >= str(20191216) and date < str(20191216):
                        order_df = xdb_datasource.get_tick_1min(date, "000043.SZ")
                    elif symbol == "001872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        order_df = xdb_datasource.get_tick_1min(date, "000022.SZ")
                    elif symbol == "201872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        order_df = xdb_datasource.get_tick_1min(date, "200022.SZ")
                    elif symbol == "601360.SH" and dates[-1] >= str(20180228) and date < str(20180228):
                        order_df = xdb_datasource.get_tick_1min(date, "601313.SH")
                    else:
                        order_df = xdb_datasource.get_tick_1min(date, symbol)
                    if (md_df.loc[idx[date:date, symbol:symbol], :]['amt'].empty) or (
                    not md_df.loc[idx[date:date, symbol:symbol], :]['amt'].values[0] > 0):  # 强制把停牌日的置为空tick_df
                        order_df = pd.DataFrame()
                    if order_df.empty:
                        logger.warning("Empty dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                        continue
                    if symbol == "000043.SZ" and date < str(20191216):
                        daily_df = xdb_datasource.get_dailydata(date, "001914.SZ")
                    elif symbol == "000022.SZ" and date < str(20181226):
                        daily_df = xdb_datasource.get_dailydata(date, "001872.SZ")
                    elif symbol == "200022.SZ" and date < str(20181226):
                        daily_df = xdb_datasource.get_dailydata(date, "201872.SZ")
                    elif symbol == "601313.SH" and date < str(20180228):
                        daily_df = xdb_datasource.get_dailydata(date, "601360.SH")
                    else:
                        daily_df = xdb_datasource.get_dailydata(date, symbol)
                    if daily_df.empty:
                        logger.error("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                        raise RuntimeError("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                    order_df["ff_shares"] = daily_df["float_a_shr_today"].values[0]
                    order_df["pre_close"] = daily_df["pre_close"].values[0]
                    df_list.insert(0, order_df)
                    cnt += 1
                    if cnt == lag:
                        break
                if df_list:
                    tmp_df = pd.concat(df_list)
                else:
                    tmp_df = pd.DataFrame()
                    result[symbol] = tmp_df
                    continue
                try:
                    tmp_df["industry"] = industry.loc[dates[-2], symbol].values[0]
                except Exception as e:
                    logger.warning("Industry label not found! date={}, symbol={}".format(dates[-1], symbol))
                    tmp_df["industry"] = np.nan
                tmp_df["after_not_ul_len"] = basic.loc[dates[-1], symbol]["after_not_ul_len"]
                tmp_df["HTSCSecurityID"] = symbol
                tmp_df["Ticker"] = symbol
                if strategy == "saturn" or strategy == "sell":
                    tmp_df["pattern"] = basic.loc[dates[-1], symbol]["lzt_label_pattern"]
                else:
                    tmp_df["pattern"] = -1

                tmp_df["dt"] = dates[-1]
                tmp_df = prepare_tick1m_data_new(tmp_df, dates[-1])

                result[symbol] = tmp_df

        else:
            logger.error("xdb type not correct! input_type={}".format(data_name))
            raise RuntimeError("XDBData - xdb type not correct!")

    tables = result.values()
    res = pd.concat(tables)
    out_dir = base_path + "/" + data_name + "/"
    if not os.path.exists(out_dir):
        os.system("mkdir -p " + out_dir)
    if data_name in ['xdb_tick1s', 'xdb_tickfull']:
        convert_tick(res, str(dates[-1]), out_dir)
    elif data_name in ['xdb_tickfulladdorder']:
        convert_tickaddorder(res, str(dates[-1]), out_dir)
    else:
        target_path = out_dir + str(dates[-1]) + ".pkl"
        res.to_pickle(target_path)
    return

def split_task(task_arr, num_threads):
    if num_threads == 1:
        return [task_arr]
    if num_threads > len(task_arr):
        return [[i] for i in task_arr]
    remainder = len(task_arr) % num_threads
    quotient = math.floor(len(task_arr) / num_threads)
    cur = 0
    res = []
    for i in range(num_threads):
        if remainder > 0:
            res.append(task_arr[cur: cur + quotient + 1])
            cur += quotient + 1
        else:
            res.append(task_arr[cur: cur + quotient])
            cur += quotient
    return res

def __execute(tasks, basic_dict, xdb_datasource, base_path):
    for i in tasks:
        try:
        # i = ('xdb_trade', ['20170309', '20170310', '20170313', '20170314', '20170315', '20170316', '20170317', '20170320', '20170321', '20170322', '20170323', '20170324', '20170327', '20170328', '20170329', '20170330', '20170331', '20170405', '20170406', '20170407', '20170410', '20170411', '20170412'], 3)
            get_data(base_path, i[0], i[1], xdb_datasource, basic_dict)
        except Exception as e:
            logger.error("find error")
            print(i[1][-1])
            print(e)


def prepare_data(trading_days, data_types, base_path, cpus=16, lag=10, back_up_lag=20, strategy=''):
    if strategy not in ['neptune']:
        logger.error("策略名称不在枚举中")
    if cpus == 1:
        logger.error("cpu=1太慢了！多设一点")
        # return
    logger.info("start prepareing data!")
    neptune_basic = pd.read_pickle('/dfs/user/023859/Neptune/basic_file_neptune_20160101_20201231.pkl')
    neptune_basic = neptune_basic.rename(columns = {'list_len':'after_not_ul_len'})

    industry = IO.read_data([trading_days[0], trading_days[-1]], columns=['Industry'],
                            alt='/data/group/800080/warehouseJG/prod/RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5')
    md_df = IO.read_data([trading_days[0], trading_days[-1]], columns=['pre_close', 'amt'],
                         alt='/data/group/800080/warehouseJG/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    logger.info("basic and industry loaded!")
    basic_dict_all = {
        "neptune": neptune_basic,
        "industry": industry,
        "md_df": md_df
    }
    if strategy == 'neptune':
        basic_dict = {key: basic_dict_all[key] for key in ['neptune', 'industry', 'md_df']}
    else:
        raise TypeError
    tasks = []
    for i in data_types:
        idx = lag + back_up_lag
        while idx < len(trading_days):
            dates = trading_days[idx - lag - back_up_lag:idx + 1]
            tasks.append((i, dates, lag))
            idx += 1
    process_tasks = split_task(tasks, cpus)

    logger.info("start executing tasks")

    if cpus == 1:
        xdb_datasource = StockData()
        __execute(process_tasks[0], basic_dict, xdb_datasource, base_path)
    else:
        num_threads = min(cpus, len(process_tasks))
        pool = Pool(num_threads)
        for i in range(num_threads):
            xdb_datasource = StockData()
            pool.apply_async(__execute, (
                process_tasks[i], basic_dict, xdb_datasource, base_path,
            ))
        pool.close()
        pool.join()

    logger.info("execution finished")

#
if __name__ == "__main__":
    base_path_dict = {
        'neptune': "/dfs/group/800463/data/xdb_data_lag3_new/neptune/"
                      }
    # start_date = "20170110"
    # end_date = "20170131" # 1224
    start_date = "20170901"
    end_date = "20171031" # 1224
    cpus = 30
    lag = 3
    # data_types = ["xdb_order", 'xdb_trade', "xdb_tick1s", "xdb_tickfull", 'xdb_tickfulladdorder',
    #               'xdb_cancel','xdb_tickex','xdb_order1m','xdb_tick1m']
    data_types = ['xdb_order1m','xdb_tick1m']
    strategy_list = ['neptune']
    for strategy in strategy_list:
        base_path = base_path_dict[strategy]
        print(start_date, end_date)
        print(strategy)
        print(base_path)
        xquant_factor_data = FactorData()
        start_date = xquant_factor_data.tradingday(start_date, 1)[0]
        real_start_date = xquant_factor_data.tradingday(start_date, -(lag + 20 + 1))[0]
        trading_days = xquant_factor_data.tradingday(real_start_date, end_date)

        prepare_data(trading_days, data_types, base_path, cpus, lag, strategy=strategy)

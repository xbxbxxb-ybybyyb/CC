from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from threading import RLock
import os
import struct
import time
import numpy as np
import zstd
import settings
from xfactor.datasource.TDayData import get_full_basic_df
from multiprocessing import pool
from settings import xdb_path_xdbformat
from loguru import logger
from xfactor import FactorDataPrepareUtil
import pandas as pd
from multiprocessing import Pool

try:
    from xdb.stockdata import StockData
except Exception as e:
    os.system("pip install /data/user/019073/marketdata/installer_and_demo/xdb-2.0.0-cp36-cp36m-linux_x86_64.whl")
    from xdb.stockdata import StockData

xdb_datasource = StockData()


def get_xdb_data(data_name, strategy, date):
    if data_name in ['xdb_order', 'xdb_trade', 'xdb_cancel', 'xdb_tickex',
                     'xdb_order1m', 'xdb_tick1m',
                     'xdb_balancesheet_cs', 'xdb_cashflow_cs', 'xdb_income_cs',
                     'xdb_order_cs', 'xdb_trade_cs', 'xdb_cancel_cs', 'xdb_tickex_cs',
                     'xdb_order1m_cs', 'xdb_tick1m_cs',
                     'xdb_balancesheet', 'xdb_cashflow', 'xdb_income',
                     'xdb_researchreport', 'xdb_reportratingadj', 'xdb_reporttargetpriceadj', 'xdb_researchreportadj',
                     'xdb_researchreport_cs', 'xdb_reportratingadj_cs', 'xdb_reporttargetpriceadj_cs', 'xdb_researchreportadj_cs',
                     ]:
        if data_name in ['xdb_order_cs', 'xdb_trade_cs', 'xdb_cancel_cs', 'xdb_tickex_cs',
                         'xdb_balancesheet_cs', 'xdb_cashflow_cs', 'xdb_income_cs',
                         'xdb_order1m_cs', 'xdb_tick1m_cs',
                         'xdb_researchreport_cs', 'xdb_reportratingadj_cs', 'xdb_reporttargetpriceadj_cs', 'xdb_researchreportadj_cs',
                        ]:
            data_name = data_name[:-3]
        file_path = settings.xdb_path_xdbformat[strategy] + "/" + data_name + "/" + date + ".pkl"
        if not os.path.exists(file_path):
            logger.warning(
                "name={}, date={}, strategy={} xdb file not exists! return empty dataframe".format(data_name, date,
                                                                                                   strategy))
            return pd.DataFrame()
        df = pd.read_pickle(file_path)
        # df = FactorDataPrepareUtil.data_filter_dict[data_filter](df, strategy, basic_file)
        return df
    elif data_name in ['xdb_tick1s', 'xdb_tickfull', 'xdb_tickfulladdorder', 'xdb_tick1s_cs', 'xdb_tickfull_cs',
                       'xdb_tickfulladdorder_cs']:
        tmp = data_name
        if tmp in ['xdb_tick1s_cs', 'xdb_tickfull_cs', 'xdb_tickfulladdorder_cs']:
            tmp = tmp[:-3]
        df = get_xdb_data_from_xdb_format(tmp, strategy, date)
        if data_name in ['xdb_tick1s_cs', 'xdb_tickfull_cs', 'xdb_tickfulladdorder_cs']:
            df_arr = []
            for k, v in df.items():
                if k == "lag_info":
                    continue
                df_arr.append(v)
            df = pd.concat(df_arr, sort=True)
        # df = FactorDataPrepareUtil.data_filter_dict[data_filter](df, strategy, basic_file)
        return df


# TODO may need modify for data creation
#  for daily runner only
def get_all_xdb_data(data_name, dates, symbols, lag, basic_dict, industry, strategy, num_threads):
    pool = Pool(num_threads)
    task_ids = []
    result = {}
    for symbol in symbols:
        task_ids.append(pool.apply_async(get_data, (
            data_name, dates, symbol, lag, basic_dict, industry, strategy,
        )))
    pool.close()
    pool.join()
    task_results = [task_id.get() for task_id in task_ids]
    pool.terminate()
    for sub_result in task_results:
        if not sub_result:
            logger.error("empty xdb result! something went wrong!")
        symbol = list(sub_result.keys())[0]
        if sub_result[symbol].empty:
            logger.warning("no xdb data loaded! symbol={}, base_date={}, lag={}".format(symbol, dates[-1], lag))
        result[data_name][symbol] = sub_result[symbol]
    return result

# for daily runner only
def get_data(data_name, dates, symbol, lag, basic_dict, industry, strategy):
    result = {}
    if data_name == "xdb_order":
        base_date = dates[-1]
        df_list = []

        cnt = 0
        for date in dates[::-1][1:]:
            order_df = xdb_datasource.get_order(date, symbol)
            if order_df.empty:
                logger.warning("Empty dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                continue

            daily_df = xdb_datasource.get_dailydata(date, symbol)
            if daily_df.empty:
                logger.error("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                raise RuntimeError("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))

            order_df["ff_shares"] = daily_df["float_a_shr_today"].values[0]
            order_df["pre_close"] = daily_df["pre_close"].values[0]
            df_list.append(order_df)
            cnt += 1
            if cnt == lag:
                break

        if df_list:
            tmp_df = pd.concat(df_list[::-1])

            try:
                tmp_df["industry"] = industry.loc[base_date, symbol].values[0]
            except Exception as e:
                logger.warning("Industry label not found! date={}, symbol={}".format(base_date, symbol))
                tmp_df["industry"] = np.nan
            tmp_df["after_not_ul_len"] = basic_dict[base_date].loc[base_date, symbol]["after_not_ul_len"]
            tmp_df["HTSCSecurityID"] = symbol
            tmp_df["Ticker"] = symbol
            if strategy == "saturn" or strategy == "sell":
                tmp_df["pattern"] = basic_dict[base_date].loc[dates[-1], symbol]["lzt_label_pattern"]
            else:
                tmp_df["pattern"] = -1

            tmp_df["dt"] = base_date
            tmp_df = FactorDataPrepareUtil.prepare_order_data_new(tmp_df, base_date)

            result[symbol] = tmp_df
        else:
            result[symbol] = pd.DataFrame()

    elif data_name == "xdb_trade":

        base_date = dates[-1]
        df_list = []

        cnt = 0
        for date in dates[::-1][1:]:
            trade_df = xdb_datasource.get_trade(date, symbol)
            if trade_df.empty:
                logger.warning("Empty dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                continue

            daily_df = xdb_datasource.get_dailydata(date, symbol)
            if daily_df.empty:
                logger.error("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                raise RuntimeError("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))

            trade_df["ff_shares"] = daily_df["float_a_shr_today"].values[0]
            trade_df["pre_close"] = daily_df["pre_close"].values[0]
            df_list.append(trade_df)
            cnt += 1
            if cnt == lag:
                break

        if df_list:
            tmp_df = pd.concat(df_list[::-1])
            try:
                tmp_df["industry"] = industry.loc[base_date, symbol].values[0]
            except Exception as e:
                logger.warning("Industry label not found! date={}, symbol={}".format(base_date, symbol))
                tmp_df["industry"] = np.nan
            tmp_df["after_not_ul_len"] = basic_dict[base_date].loc[base_date, symbol]["after_not_ul_len"]
            tmp_df["HTSCSecurityID"] = symbol
            tmp_df["Ticker"] = symbol
            if strategy == "saturn" or strategy == "sell":
                tmp_df["pattern"] = basic_dict[base_date].loc[dates[-1], symbol]["lzt_label_pattern"]
            else:
                tmp_df["pattern"] = -1

            tmp_df["dt"] = base_date
            tmp_df = FactorDataPrepareUtil.prepare_trade_data_new(tmp_df, base_date)

            result[symbol] = tmp_df
        else:
            result[symbol] = pd.DataFrame()

    elif data_name == "xdb_cancel":
        logger.warning("xdb_cancel not supported at this time.")

    elif data_name == "xdb_tick1s":

        base_date = dates[-1]
        df_list = []

        cnt = 0
        for date in dates[::-1][1:]:
            tick1s_df = xdb_datasource.get_tick1s(date, symbol)
            if tick1s_df.empty:
                logger.warning("Empty dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                continue

            daily_df = xdb_datasource.get_dailydata(date, symbol)
            if daily_df.empty:
                logger.error("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                raise RuntimeError("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))

            tick1s_df["ff_shares"] = daily_df["float_a_shr_today"].values[0]
            tick1s_df["pre_close"] = daily_df["pre_close"].values[0]
            df_list.append(tick1s_df)
            cnt += 1
            if cnt == lag:
                break

        if df_list:
            tmp_df = pd.comcat(df_list[::-1])
            try:
                tmp_df["industry"] = industry.loc[base_date, symbol].values[0]
            except Exception as e:
                logger.warning("Industry label not found! date={}, symbol={}".format(base_date, symbol))
                tmp_df["industry"] = np.nan
            tmp_df["after_not_ul_len"] = basic_dict[base_date].loc[base_date, symbol]["after_not_ul_len"]
            tmp_df["HTSCSecurityID"] = symbol
            tmp_df["Ticker"] = symbol
            if strategy == "saturn" or strategy == "sell":
                tmp_df["pattern"] = basic_dict[base_date].loc[dates[-1], symbol]["lzt_label_pattern"]
            else:
                tmp_df["pattern"] = -1

            tmp_df["dt"] = base_date
            tmp_df = FactorDataPrepareUtil.prepare_tick_data_new(tmp_df, base_date, "xdb_tick1s")

            result[symbol] = tmp_df
        else:
            result[symbol] = pd.DataFrame()

    elif data_name == "xdb_tickfull":

        base_date = dates[-1]
        df_list = []

        cnt = 0
        for date in dates[::-1][1:]:

            tickfull_df = xdb_datasource.get_tickfull(date, symbol)
            if tickfull_df.empty:
                logger.warning("Empty dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                continue

            daily_df = xdb_datasource.get_dailydata(date, symbol)
            if daily_df.empty:
                logger.error("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                raise RuntimeError("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))

            tickfull_df["ff_shares"] = daily_df["float_a_shr_today"].values[0]
            tickfull_df["pre_close"] = daily_df["pre_close"].values[0]
            df_list.append(tickfull_df)
            cnt += 1
            if cnt == lag:
                break

        if df_list:
            tmp_df = pd.concat(df_list[::-1])
            # aa = time.time()
            try:
                tmp_df["industry"] = industry.loc[base_date, symbol].values[0]
            except Exception as e:
                logger.warning("Industry label not found! date={}, symbol={}".format(base_date, symbol))
                tmp_df["industry"] = np.nan
            tmp_df["after_not_ul_len"] = basic_dict[base_date].loc[base_date, symbol]["after_not_ul_len"]
            tmp_df["HTSCSecurityID"] = symbol
            tmp_df["Ticker"] = symbol
            if strategy == "saturn" or strategy == "sell":
                tmp_df["pattern"] = basic_dict[base_date].loc[dates[-1], symbol]["lzt_label_pattern"]
            else:
                tmp_df["pattern"] = -1

            tmp_df["dt"] = base_date
            tmp_df = FactorDataPrepareUtil.prepare_tick_data_new(tmp_df, base_date, "xdb_tickfull")

            result[symbol] = tmp_df
        else:
            result[symbol] = pd.DataFrame()

    elif data_name == "xdb_tickfulladdorder":

        base_date = dates[-1]
        df_list = []

        cnt = 0
        for date in dates[::-1][1:]:

            entickfull_df = xdb_datasource.get_entickfull(date, symbol)
            if entickfull_df.empty:
                logger.warning("Empty dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                continue

            daily_df = xdb_datasource.get_dailydata(date, symbol)
            if daily_df.empty:
                logger.error("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                raise RuntimeError("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))

            entickfull_df["ff_shares"] = daily_df["float_a_shr_today"].values[0]
            entickfull_df["pre_close"] = daily_df["pre_close"].values[0]
            df_list.append(entickfull_df)
            cnt += 1
            if cnt == lag:
                break

        if df_list:
            tmp_df = pd.concat(df_list[::-1])
            # aa = time.time()
            try:
                tmp_df["industry"] = industry.loc[base_date, symbol].values[0]
            except Exception as e:
                logger.warning("Industry label not found! date={}, symbol={}".format(base_date, symbol))
                tmp_df["industry"] = np.nan
            tmp_df["after_not_ul_len"] = basic_dict[base_date].loc[base_date, symbol]["after_not_ul_len"]
            tmp_df["HTSCSecurityID"] = symbol
            tmp_df["Ticker"] = symbol
            if strategy == "saturn" or strategy == "sell":
                tmp_df["pattern"] = basic_dict[base_date].loc[dates[-1], symbol]["lzt_label_pattern"]
            else:
                tmp_df["pattern"] = -1

            tmp_df["dt"] = base_date
            tmp_df = FactorDataPrepareUtil.prepare_tickaddorder_data_new(tmp_df, base_date)

            result[symbol] = tmp_df
        else:
            result[symbol] = pd.DataFrame()

    elif data_name == "xdb_tickex":

        base_date = dates[-1]
        df_list = []

        cnt = 0
        for date in dates[::-1][1:]:

            tickex_df = xdb_datasource.get_tickex(date, symbol)
            if tickex_df.empty:
                logger.warning("Empty dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                continue

            daily_df = xdb_datasource.get_dailydata(date, symbol)
            if daily_df.empty:
                logger.error("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                raise RuntimeError("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))

            tickex_df["ff_shares"] = daily_df["float_a_shr_today"].values[0]
            tickex_df["pre_close"] = daily_df["pre_close"].values[0]
            df_list.append(tickex_df)
            cnt += 1
            if cnt == lag:
                break

        if df_list:
            tmp_df = pd.concat(df_list[::-1])
            try:
                tmp_df["industry"] = industry.loc[base_date, symbol].values[0]
            except Exception as e:
                logger.warning("Industry label not found! date={}, symbol={}".format(base_date, symbol))
                tmp_df["industry"] = np.nan
            tmp_df["after_not_ul_len"] = basic_dict[base_date].loc[base_date, symbol]["after_not_ul_len"]
            tmp_df["HTSCSecurityID"] = symbol
            tmp_df["Ticker"] = symbol
            if strategy == "saturn" or strategy == "sell":
                tmp_df["pattern"] = basic_dict[base_date].loc[dates[-1], symbol]["lzt_label_pattern"]
            else:
                tmp_df["pattern"] = -1

            tmp_df["dt"] = base_date
            tmp_df = FactorDataPrepareUtil.prepare_tick_data_new(tmp_df, base_date, "xdb_tickex")

            result[symbol] = tmp_df
        else:
            result[symbol] = pd.DataFrame()

    else:
        logger.error("xdb type not correct! input_type={}".format(data_name))
        raise RuntimeError("XDBData - xdb type not correct!")

    return result


##################### xdb_format with mutlthreading
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
                              "end": end }
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
            ("MDDate", "<S8"), ("MDTime", '<i8'), ("appl_seq_num", '<i8'), ("NumTrades", '<i8'),
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
            ("OpenPx", '<f8'), ("HighPx", '<f8'), ("LowPx", '<f8'),("WeightedAvgBidPx", '<f8'), ("WeightedAvgOfferPx", '<f8'),

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
                    result[i] = df
                except Exception as exc:
                    raise Exception('Get xdb value exception: %s' % (exc))

    except Exception as e:
        logger.error("xdb data prep error! dataname={}, strategy={}, path={}".format(data_name, strategy, file_path))
        raise Exception("xdb data prep error!")

    result["lag_info"] = 3
    return result


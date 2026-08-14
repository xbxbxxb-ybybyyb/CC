# 下载xdb数据至公共文件夹使用
import pandas as pd
import os
import numpy as np
from loguru import logger
import math
import copy
from multiprocessing import Pool
from xquant.factordata import FactorData
from h5data.IO import IO

os.system("pip uninstall xdb -y")
os.system("pip install /data/user/019073/marketdata/installer_and_demo/xdb-2.0.0-cp36-cp36m-linux_x86_64.whl")
from xdb.stockdata import StockData
import decimal

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
        df['OrderType'].replace('U','3',inplace = True) # xdb接口用U表示本方最优，转换为int类型的3，从而和xquant一致
        df['OrderType'] = df['OrderType'].apply(lambda x : int(x))
        df.set_index(["dt", "Ticker"], inplace=True)
        df = df[['MDDate', 'MDTime', 'OrderIndex', 'OrderPrice', 'OrderQty', 'OrderBSFlag', "OrderType",
                 'ff_shares', 'pattern', 'industry', 'after_not_ul_len', 'pre_close']]
        for col in ['OrderPrice','pre_close']:
            df[col] = df[col].apply(lambda x : round_(x,2))
        for col in ['ff_shares']:
            df[col] = df[col].apply(lambda x : round_(x,4))
        for col in ['pattern']:
            df[col] = df[col].apply(lambda x : int(round_(x,0)))
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
        df = df[['MDDate', 'MDTime',
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
        df.columns = ['symbol', "MDDate", "MDTime", "timestamp",
                     "OpenPx", "LastPx", "high_px", "low_px", "TotalOfferQty", "TotalBidQty",
                     "WeightedAvgOfferPx", "WeightedAvgBidPx", "TotalVolumeTrade", 'TotalValueTrade', 'VolumeTrade',
                     "NumTrades", 'TradingPhaseCode',
                     "Sell1Price", "Sell2Price", "Sell3Price", "Sell4Price", "Sell5Price",
                     "Sell6Price", "Sell7Price", "Sell8Price", "Sell9Price", "Sell10Price",
                     "Sell1OrderQty","Sell2OrderQty","Sell3OrderQty", "Sell4OrderQty", "Sell5OrderQty",
                     "Sell6OrderQty", "Sell7OrderQty", "Sell8OrderQty", "Sell9OrderQty", "Sell10OrderQty",
                     "Sell1NumOrders", "Sell2NumOrders", "Sell3NumOrders", "Sell4NumOrders", "Sell5NumOrders",
                     "Sell6NumOrders", "Sell7NumOrders", "Sell8NumOrders", "Sell9NumOrders", "Sell10NumOrders",

                     "Buy1Price", "Buy2Price","Buy3Price", "Buy4Price", "Buy5Price",
                     "Buy6Price", "Buy7Price", "Buy8Price", "Buy9Price", "Buy10Price",
                     "Buy1OrderQty", "Buy2OrderQty", "Buy3OrderQty", "Buy4OrderQty","Buy5OrderQty",
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

        df = df[[
            "MDDate", "MDTime", "NumTrades", "TotalVolumeTrade", "TotalValueTrade", "VolumeTrade", "LastPx",
            'ff_shares', 'pattern', 'industry', 'after_not_ul_len', 'pre_close', "OpenPx",
            "TotalBidQty",
            "TotalOfferQty", "WeightedAvgBidPx", "WeightedAvgOfferPx", "Buy1Price", "Buy2Price",
            "Buy3Price", "Buy4Price", "Buy5Price", "Buy6Price", "Buy7Price", "Buy8Price", "Buy9Price",
            "Buy10Price", "Buy1OrderQty", "Buy2OrderQty", "Buy3OrderQty", "Buy4OrderQty","Buy5OrderQty",
            "Buy6OrderQty", "Buy7OrderQty", "Buy8OrderQty", "Buy9OrderQty", "Buy10OrderQty",
            "Sell1Price", "Sell2Price", "Sell3Price", "Sell4Price", "Sell5Price", "Sell6Price", "Sell7Price",
            "Sell8Price", "Sell9Price", "Sell10Price", "Sell1OrderQty",
            "Sell2OrderQty", "Sell3OrderQty", "Sell4OrderQty", "Sell5OrderQty",
            "Sell6OrderQty", "Sell7OrderQty", "Sell8OrderQty", "Sell9OrderQty",
            "Sell10OrderQty"]]
        for col in ['WeightedAvgBidPx','WeightedAvgOfferPx','pre_close']:
            df[col] = df[col].apply(lambda x : round_(x,2))
        for col in ['ff_shares']:
            df[col] = df[col].apply(lambda x : round_(x,4))
        # for col in ['industry','after_not_ul_len']:
        #     df[col] = df[col].apply(lambda x : round_(x,1))
        for col in ['pattern']:
            df[col] = df[col].apply(lambda x : int(round_(x,0)))

    except Exception as e:
        logger.error(
            "Tick数据准备错误！base_date={}, error={}, trace={}".format(base_date, e.__cause__,
                                                                 e.__traceback__))
    return df


def get_data(base_path, data_name, dates, xdb_datasource, basic_dict):
    industry = basic_dict["industry"]
    md_df = basic_dict["md_df"]
    idx = pd.IndexSlice
    result = {}
    for k,v in basic_dict.items():
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
                    if not md_df.loc[idx[date:date, symbol:symbol], :]['amt'].values[0] > 0:# 强制把停牌日的置为空tick_df
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
                    if not md_df.loc[idx[date:date, symbol:symbol], :]['amt'].values[0] > 0:# 强制把停牌日的置为空tick_df
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
            logger.warning("xdb_cancel not supported at this time.")
            # for symbol in symbols:
            #     if symbol in result:
            #         continue
            #     df_list = []
            #     date_li = dates[::-1][1:]
            #     cnt = 0
            #     for date in date_li:
            #         cancel_df = xdb_datasource.get_cancel(date, symbol)
            #         if cancel_df.empty:
            #             logger.warning("Empty dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
            #             continue
            #         daily_df = xdb_datasource.get_dailydata(date, symbol)
            #         cancel_df["ff_shares"] = daily_df["float_a_shr_today"].values[0]
            #         cancel_df["pre_close"] = daily_df["pre_close"].values[0]
            #         df_list.insert(0, cancel_df)
            #         cnt += 1
            #         if cnt == lag:
            #             break
            #
            #     if df_list:
            #         tmp_df = pd.concat(df_list)
            #     else:
            #         tmp_df = pd.DataFrame()
            #         result[symbol] = tmp_df
            #         return
            #     try:
            #         tmp_df["industry"] = industry.loc[dates[-2], symbol].values[0]
            #     except Exception as e:
            #         logger.warning("Industry label not found! date={}, symbol={}".format(dates[-1], symbol))
            #         tmp_df["industry"] = np.nan
            #     tmp_df["after_not_ul_len"] = basic.loc[dates[-1], symbol]["after_not_ul_len"]
            #     tmp_df["HTSCSecurityID"] = symbol
            #     tmp_df["Ticker"] = symbol
            #     if strategy == "saturn" or strategy == "sell":
            #         tmp_df["pattern"] = basic.loc[dates[-1], symbol]["lzt_label_pattern"]
            #     else:
            #         tmp_df["pattern"] = -1
            #
            #     tmp_df["dt"] = dates[-1]
            #     tmp_df = prepare_trade_data_new(tmp_df, dates[-1])
            #     result[symbol] = tmp_df

        elif data_name == "xdb_tick1s":
            for symbol in symbols:
                if symbol in result:
                    continue
                df_list = []
                date_li = dates[::-1][1:]
                cnt = 0
                for date in date_li:
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
                    if not md_df.loc[idx[date:date, symbol:symbol], :]['amt'].values[0] > 0:# 强制把停牌日的置为空tick_df
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
                    if not md_df.loc[idx[date:date, symbol:symbol], :]['amt'].values[0] > 0:# 强制把停牌日的置为空tick_df
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
                tmp_df = prepare_tick_data_new(tmp_df, dates[-1],data_name)
                result[symbol] = tmp_df

        elif data_name == "xdb_tickex":
            for symbol in symbols:
                if symbol in result:
                    continue
                df_list = []
                date_li = dates[::-1][1:]
                cnt = 0
                for date in date_li:
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
                    if not md_df.loc[idx[date:date, symbol:symbol], :]['amt'].values[0] > 0:# 强制把停牌日的置为空tick_df
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


        else:
            logger.error("xdb type not correct! input_type={}".format(data_name))
            raise RuntimeError("XDBData - xdb type not correct!")

    tables = result.values()
    res = pd.concat(tables)
    out_dir = base_path + "/" + data_name + "/"
    if not os.path.exists(out_dir):
        os.system("mkdir -p " + out_dir)
    target_path = out_dir + str(dates[-1]) + ".pkl"
    res.to_pickle(target_path, compression='gzip')
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

def prepare_data(trading_days, data_types, base_path, cpus=16, lag=10, back_up_lag=20):
    if cpus == 1:
        logger.error("cpu=1太慢了！多设一点")
        # return
    logger.info("start prepareing data!")
    jupiter_basic = pd.read_hdf('/data/group/800463/data/project1_public/factor_lib_v2/Basic_zt_20150901_20191231.h5')
    saturn_basic = pd.read_hdf(
        '/data/group/800463/data/project2_public/factor_lib/Basic_closed_hf_finish_20160101_20191231.h5')
    sell_basic = pd.read_hdf(
        '/data/group/800463/data/projectS_public/factor_lib/Basic_closed_hf_finish_20160101_20191231.h5')
    europa_basic = pd.read_hdf(
        '/data/group/800463/data/project1_public/factor_lib_v3/Basic_zt_001_20150901_20191231.h5')
    metis_basic = pd.read_hdf(
        '/dfs/group/800463/data/project1_public/factor_lib_metis/Basic_metis_20160101_20191231.h5')
    mimas_basic = pd.read_hdf(
        '/data/group/800463/data/project2_public/next_factor_lib/Basic_next_hf_finish_20160101_20191231.h5',)
    industry = IO.read_data([trading_days[0], trading_days[-1]], columns=['Industry'],
                           alt='/data/group/800080/warehouse/prod/RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5')
    md_df = IO.read_data([trading_days[0], trading_days[-1]], columns=['pre_close','amt'],
                         alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    logger.info("basic and industry loaded!")
    basic_dict = {
        # "jupiter": jupiter_basic,
        "saturn": saturn_basic,
        "sell": sell_basic,
        # "europa": europa_basic,
        # "metis": metis_basic,
        # "mimas": mimas_basic,
        "industry": industry,
        "md_df": md_df
    }

    tasks = []
    for i in data_types:
        idx = lag + back_up_lag
        while idx <= len(trading_days):
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

if __name__ == "__main__":
    start_date = "20170401"
    end_date = "20170410"
    cpus = 20
    lag = 3
    # data_types = ["xdb_order",'xdb_trade',"xdb_tick1s", "xdb_tickfull",'xdb_tickex']
    data_types = ['xdb_trade',"xdb_tick1s", "xdb_tickfull",'xdb_tickex']
    base_path = "/dfs/group/800463/data/xdb_data_lag3/saturn_sell/"
    print(start_date,end_date)
    print(base_path)
    xquant_factor_data = FactorData()
    real_start_date = xquant_factor_data.tradingday(start_date, -(lag + 20))[0]
    trading_days = xquant_factor_data.tradingday(real_start_date, end_date)

    prepare_data(trading_days, data_types, base_path, cpus, lag)

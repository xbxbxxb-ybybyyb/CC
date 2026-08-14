# 下载xquant数据至公共文件夹作为xdb数据的补充
import pandas as pd
import os
import numpy as np
from loguru import logger
import math
import copy
from multiprocessing import Pool
from xquant.factordata import FactorData
from h5data.IO import IO
from xquant.marketdata import MarketData
mdp = MarketData()
import decimal
def round_(x, n=0):
    x = x + 1e-10
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                     rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res
def find_repeat_tick(tick_data, repeat_filter_cols):
    tick_data['inf_str'] = tick_data[repeat_filter_cols].apply(lambda x: str(x.values), axis=1)
    tick_data['last_inf_str'] = tick_data['inf_str'].shift(1)
    return tick_data['inf_str'] == tick_data['last_inf_str']
def prepare_order_data_new_xquant(df, base_date):
    try:
        df["dt"] = pd.to_datetime(df["dt"])
        df.set_index(["dt", "Ticker"], inplace=True)
        df['MDTime'] = df['MDTime'].astype(int)
        df['OrderBSFlag'] = df['OrderBSFlag'].apply(lambda x: int(x))
        df['pattern'] = df['pattern'].apply(lambda x : int(round_(x,0)))
        df['OrderQty'] = df['OrderQty'].apply(lambda x : int(round_(x,0)))
        df['OrderQty'] = df['OrderQty'].astype('int64')
        df = df.rename(columns={'OrderNo': 'OrderIndex'})

        df['zcz'] = (((df.reset_index()['Ticker'].apply(lambda x: x[0] == '3'))& (df.reset_index()['dt'] >= '2020-08-24')) | (
                         df.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
        df['ul_price'] = np.floor(df['pre_close'] * 100 * 1.1 + 0.5 + 1e-8) / 100
        df['ul_price'][df['zcz']] = np.floor(df['pre_close'] * 100 * 1.2 + 0.5 + 1e-8) / 100
        df['dl_price'] = np.floor(df['pre_close'] * 100 * 0.9 + 0.5 + 1e-8) / 100
        df['dl_price'][df['zcz']] = np.floor(df['pre_close'] * 100 * 0.8 + 0.5 + 1e-8) / 100
        df.loc[(df['OrderType'].isin([1, 3])) & (df['OrderBSFlag'] == 1), 'OrderPrice'] = df.loc[(df['OrderType'].isin([1, 3])) & (df['OrderBSFlag'] == 1), 'ul_price']
        df.loc[(df['OrderType'].isin([1, 3])) & (df['OrderBSFlag'] == 2), 'OrderPrice'] = df.loc[(df['OrderType'].isin([1, 3])) & (df['OrderBSFlag'] == 2), 'dl_price']
        df = df[['MDDate', 'MDTime', 'OrderIndex', 'OrderPrice', 'OrderQty', 'OrderBSFlag', "OrderType",
                 'ff_shares', 'pattern', 'industry', 'after_not_ul_len', 'pre_close','ul_price','dl_price']]
    except Exception as e:
        logger.error(
            "Order数据准备错误！base_date={}, error={}, trace={}".format(base_date, e.__cause__,
                                                                 e.__traceback__))
    return df
def prepare_trade_data_new_xquant(df, base_date):
    try:
        df["dt"] = pd.to_datetime(df["dt"])
        df.set_index(["dt", "Ticker"], inplace=True)
        df['MDTime'] = df['MDTime'].astype(int)
        # 注意，buysell赋值1，2的逻辑需要前置，这里是多天数据不可以使用
        # 清洗集合竞价期间BSFlag
        df.loc[df['MDTime'] < 92900000, 'TradeBSFlag'] = 0
        df['TradeBSFlag'] = df['TradeBSFlag'].apply(lambda x: int(x))
        df['pattern'] = df['pattern'].apply(lambda x : int(round_(x,0)))
        df['TradeType'] = df['TradeType'].astype('int64')
        df['TradeQty'] = df['TradeQty'].apply(lambda x : int(round_(x,0)))
        df['TradeQty'] = df['TradeQty'].astype('int64')
        #
        df['TradeMoney'] = (df['TradePrice'] * df['TradeQty']).apply(lambda x : round_(x,2))
        df = df[(df['TradePrice'] > 0) & (df['TradeMoney'] > 0)]  # 去除撤单
        df = df[['MDDate', 'MDTime',
                 'TradeIndex', 'TradeBuyNo', 'TradeSellNo', 'TradeType', 'TradeBSFlag', 'TradePrice', 'TradeQty',
                 'TradeMoney', 'ff_shares', 'pattern', 'industry', 'after_not_ul_len', 'pre_close']]
    except Exception as e:
        logger.error(
            "Trade数据准备错误！base_date={}, error={}, trace={}".format(base_date, e.__cause__,
                                                                 e.__traceback__))
    return df
def prepare_tickex_data_new_xquant(df, base_date):
    try:
        # st = time.time()
        df['MDTime'] = df['MDTime'].astype(int)
        df['pattern'] = df['pattern'].apply(lambda x : int(round_(x,0)))
        # 915之后时间筛选
        df = df[df['MDTime']>=91500000]
        df=df[~((df['MDTime']>113003000) & (df['MDTime']<130000000))]
        df=df[df['MDTime']<=150003000]
        df["dt"] = pd.to_datetime(df["dt"])
        df.set_index(["dt", "Ticker"], inplace=True)
        for col in (['Buy%dOrderQty' % (i) for i in range(1, 11)] + ['Sell%dOrderQty' % (i) for i in range(1, 11)]):
            df[col] = df[col].apply(lambda x: int(round_(x, 0)))
            df[col] = df[col].astype('int64')
        used_cols = ['MDDate','MDTime', 'NumTrades', 'TotalVolumeTrade', 'TotalValueTrade','VolumeTrade', 'LastPx',
                     'ff_shares','pattern','industry','after_not_ul_len','pre_close','OpenPx', "HighPx", "LowPx",
                     'TotalBidQty',
                     'TotalOfferQty','WeightedAvgBidPx', 'WeightedAvgOfferPx'] + \
                    ['Buy%dPrice' % (i) for i in range(1, 11)] + ['Buy%dOrderQty' % (i) for i in range(1, 11)] +\
                    ['Sell%dPrice' % (i) for i in range(1, 11)] + ['Sell%dOrderQty' % (i) for i in range(1, 11)]
        df = df[used_cols]
    except Exception as e:
        logger.error(
            "Tick数据准备错误！base_date={}, error={}, trace={}".format(base_date, e.__cause__,
                                                                 e.__traceback__))
    return df

def get_data(base_path, data_name, dates, mdp, basic_dict):
    industry = basic_dict["industry"]
    float_a_share_df = basic_dict["float_a_share_df"]
    md_df = basic_dict["md_df"]
    idx = pd.IndexSlice
    result = {}
    for k,v in basic_dict.items():
        if (k == "industry") | (k=='md_df') | (k == 'float_a_share_df'):
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
                    from data_sh_order_merge import get_sh_order
                    
                    if symbol == "001914.SZ" and dates[-1] >= str(20191216) and date < str(20191216):
                        order_df = mdp.get_data_by_date('Order', "000043.SZ", date)
                    elif symbol == "001872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        order_df = mdp.get_data_by_date('Order', "000022.SZ", date)
                    elif symbol == "201872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        order_df = mdp.get_data_by_date('Order', "200022.SZ", date)
                    elif symbol == "601360.SH" and dates[-1] >= str(20180228) and date < str(20180228):
                        #order_df = mdp.get_data_by_date('Order', "601313.SH", date)
                        order_df = get_sh_order(date,"601313.SH")
                    else:
                        if  symbol[-2:] == 'SH':
                            order_df = get_sh_order(date,symbol)
                            order_df['OrderType'] = 2
                        else:
                            order_df = mdp.get_data_by_date('Order', symbol, date)
                    if (md_df.loc[idx[date:date, symbol:symbol], :]['amt'].empty) or (not md_df.loc[idx[date:date, symbol:symbol], :]['amt'].values[0] > 0):# 强制把停牌日的置为空tick_df
                        order_df = pd.DataFrame()
                    if order_df.empty:
                        logger.warning("Empty dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                        continue

                    if symbol == "001914.SZ" and dates[-1] >= str(20191216) and date < str(20191216):
                        daily_float_a_share_df = float_a_share_df.loc[idx[date:date,"000043.SZ":"000043.SZ"],:]
                        daily_md_df = md_df.loc[idx[date:date,"000043.SZ":"000043.SZ"],:]
                    elif symbol == "000022.SZ" and date < str(20181226):
                        daily_float_a_share_df = float_a_share_df.loc[idx[date:date,"001872.SZ":"001872.SZ"],:]
                        daily_md_df = md_df.loc[idx[date:date, "000022.SZ":"000022.SZ"], :]
                    elif symbol == "001872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        daily_float_a_share_df = float_a_share_df.loc[idx[date:date, "001872.SZ":"001872.SZ"], :]
                        daily_md_df = md_df.loc[idx[date:date, "000022.SZ":"000022.SZ"], :]
                    elif symbol == "601313.SH" and date < str(20180228):
                        daily_float_a_share_df = float_a_share_df.loc[idx[date:date,"601360.SH":"601360.SH"],:]
                        daily_md_df = md_df.loc[idx[date:date,"601360.SH":"601360.SH"],:]
                    else:
                        daily_float_a_share_df = float_a_share_df.loc[idx[date:date, symbol:symbol], :]
                        daily_md_df = md_df.loc[idx[date:date, symbol:symbol], :]
                    if (daily_float_a_share_df.empty) | (daily_md_df.empty):
                        logger.error("Empty md or float_a_share dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                        raise RuntimeError("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                    order_df["ff_shares"] = daily_float_a_share_df["FLOAT_A_SHR_TODAY"].values[0]
                    order_df["pre_close"] = daily_md_df["pre_close"].values[0]
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
                tmp_df = prepare_order_data_new_xquant(tmp_df, dates[-1])
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
                        trade_df = mdp.get_data_by_date('Transaction', "000043.SZ", date)
                    elif symbol == "001872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        trade_df = mdp.get_data_by_date('Transaction', "000022.SZ", date)
                    elif symbol == "201872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        trade_df = mdp.get_data_by_date('Transaction', "200022.SZ", date)
                    elif symbol == "601360.SH" and dates[-1] >= str(20180228) and date < str(20180228):
                        trade_df = mdp.get_data_by_date('Transaction', "601313.SH", date)
                    else:
                        trade_df = mdp.get_data_by_date('Transaction', symbol, date)
                    if (md_df.loc[idx[date:date, symbol:symbol], :]['amt'].empty) or (not md_df.loc[idx[date:date, symbol:symbol], :]['amt'].values[0] > 0):# 强制把停牌日的置为空tick_df
                        trade_df = pd.DataFrame()
                    if trade_df.empty:
                        logger.warning("Empty dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                        continue
                    if symbol == "001914.SZ" and dates[-1] >= str(20191216) and date < str(20191216):
                        daily_float_a_share_df = float_a_share_df.loc[idx[date:date,"000043.SZ":"000043.SZ"],:]
                        daily_md_df = md_df.loc[idx[date:date,"000043.SZ":"000043.SZ"],:]
                    elif symbol == "000022.SZ" and date < str(20181226):
                        daily_float_a_share_df = float_a_share_df.loc[idx[date:date,"001872.SZ":"001872.SZ"],:]
                        daily_md_df = md_df.loc[idx[date:date, "000022.SZ":"000022.SZ"], :]
                    elif symbol == "001872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        daily_float_a_share_df = float_a_share_df.loc[idx[date:date, "001872.SZ":"001872.SZ"], :]
                        daily_md_df = md_df.loc[idx[date:date, "000022.SZ":"000022.SZ"], :]
                    elif symbol == "601313.SH" and date < str(20180228):
                        daily_float_a_share_df = float_a_share_df.loc[idx[date:date,"601360.SH":"601360.SH"],:]
                        daily_md_df = md_df.loc[idx[date:date,"601360.SH":"601360.SH"],:]
                    else:
                        daily_float_a_share_df = float_a_share_df.loc[idx[date:date,symbol:symbol],:]
                        daily_md_df = md_df.loc[idx[date:date,symbol:symbol],:]

                    if (daily_float_a_share_df.empty) | (daily_md_df.empty):
                        logger.error("Empty md or float_a_share dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                        raise RuntimeError("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                    trade_df["ff_shares"] = daily_float_a_share_df["FLOAT_A_SHR_TODAY"].values[0]
                    trade_df["pre_close"] = daily_md_df["pre_close"].values[0]
                    # 处理'TradeBSFlag'全是0的情况
                    if trade_df['TradeBSFlag'].sum() == 0:
                        temp_BSFlag = trade_df['TradeBSFlag'].copy()
                        temp_BSFlag[trade_df['TradeBuyNo'] < trade_df['TradeSellNo']] = 2.0
                        temp_BSFlag[trade_df['TradeBuyNo'] > trade_df['TradeSellNo']] = 1.0
                        trade_df['TradeBSFlag'] = temp_BSFlag
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
                tmp_df = prepare_trade_data_new_xquant(tmp_df, dates[-1])
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
                        tick_df = mdp.get_data_by_date('stock', "000043.SZ", date)
                    elif symbol == "001872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        tick_df = mdp.get_data_by_date('stock', "000022.SZ", date)
                    elif symbol == "201872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        tick_df = mdp.get_data_by_date('stock', "200022.SZ", date)
                    elif symbol == "601360.SH" and dates[-1] >= str(20180228) and date < str(20180228):
                        tick_df = mdp.get_data_by_date('stock', "601313.SH", date)
                    else:
                        tick_df = mdp.get_data_by_date('stock', symbol, date)
                    if (md_df.loc[idx[date:date, symbol:symbol], :]['amt'].empty) or (not md_df.loc[idx[date:date, symbol:symbol], :]['amt'].values[0] > 0):# 强制把停牌日的置为空tick_df
                        tick_df = pd.DataFrame()
                    if tick_df.empty:
                        logger.warning("Empty dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                        continue
                    if symbol == "001914.SZ" and dates[-1] >= str(20191216) and date < str(20191216):
                        daily_float_a_share_df = float_a_share_df.loc[idx[date:date,"000043.SZ":"000043.SZ"],:]
                        daily_md_df = md_df.loc[idx[date:date,"000043.SZ":"000043.SZ"],:]
                    elif symbol == "000022.SZ" and date < str(20181226):
                        daily_float_a_share_df = float_a_share_df.loc[idx[date:date,"001872.SZ":"001872.SZ"],:]
                        daily_md_df = md_df.loc[idx[date:date, "000022.SZ":"000022.SZ"], :]
                    elif symbol == "001872.SZ" and dates[-1] >= str(20181226) and date < str(20181226):
                        daily_float_a_share_df = float_a_share_df.loc[idx[date:date, "001872.SZ":"001872.SZ"], :]
                        daily_md_df = md_df.loc[idx[date:date, "000022.SZ":"000022.SZ"], :]
                    elif symbol == "601313.SH" and date < str(20180228):
                        daily_float_a_share_df = float_a_share_df.loc[idx[date:date,"601360.SH":"601360.SH"],:]
                        daily_md_df = md_df.loc[idx[date:date,"601360.SH":"601360.SH"],:]
                    else:
                        daily_float_a_share_df = float_a_share_df.loc[idx[date:date, symbol:symbol], :]
                        daily_md_df = md_df.loc[idx[date:date, symbol:symbol], :]
                    if (daily_float_a_share_df.empty) | (daily_md_df.empty):
                        logger.error("Empty md or float_a_share dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                        raise RuntimeError("Empty daily dataframe! date={}, symbol={}, type={}".format(date, symbol, data_name))
                    tick_df["ff_shares"] = daily_float_a_share_df["FLOAT_A_SHR_TODAY"].values[0]
                    tick_df["pre_close"] = daily_md_df["pre_close"].values[0]
                    # bef_len = len(tick_df)
                    repeat_filter_cols = ['NumTrades', 'TotalVolumeTrade', 'TotalValueTrade', 'LastPx', 'TotalBidQty',
                                          'TotalOfferQty',
                                          'WeightedAvgBidPx', 'WeightedAvgOfferPx', 'TradingPhaseCode'] + \
                                         ['Buy%dPrice' % (i) for i in range(1, 11)] + ['Sell%dPrice' % (i) for i in
                                                                                       range(1, 11)] + \
                                         ['Buy%dOrderQty' % (i) for i in range(1, 11)] + ['Sell%dOrderQty' % (i) for i
                                                                                          in
                                                                                          range(1, 11)]
                    tick_df['repeat_filter'] = find_repeat_tick(tick_df.copy(), repeat_filter_cols)
                    tick_df = tick_df[~tick_df['repeat_filter']]
                    # aft_len = len(tick_df)
                    # if (bef_len != aft_len): print('repeat tick num:%d' % (bef_len - aft_len))
                    tick_df['VolumeTrade'] = (tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)).apply(
                        lambda x: round_(x, 2))
                    df_list.insert(0, tick_df)
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
                tmp_df = prepare_tickex_data_new_xquant(tmp_df, dates[-1])
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

def __execute(tasks, basic_dict, mdp, base_path):
    for i in tasks:
        try:
        # i = ('xdb_trade', ['20170309', '20170310', '20170313', '20170314', '20170315', '20170316', '20170317', '20170320', '20170321', '20170322', '20170323', '20170324', '20170327', '20170328', '20170329', '20170330', '20170331', '20170405', '20170406', '20170407', '20170410', '20170411', '20170412'], 3)
            get_data(base_path, i[0], i[1], mdp, basic_dict)
        except Exception as e:
            logger.error("find error")
            print(e)

def prepare_data(trading_days, data_types, base_path, cpus=16, lag=10, back_up_lag=20, strategy = ''):
    if strategy not in ['neptune']:
        logger.error("策略名称不在枚举中")
    if cpus == 1:
        logger.error("cpu=1太慢了！多设一点")
        # return
    logger.info("start prepareing data!")
    neptune_basic = pd.read_pickle('/dfs/user/023859/share_file/for_qyh/basic_file_neptune_20160101_20191231.pkl')
    neptune_basic = neptune_basic.rename(columns = {'list_len':'after_not_ul_len'})

    industry = IO.read_data([trading_days[0], trading_days[-1]], columns=['Industry'],
                            alt='/data/group/800080/warehouseJG/prod/RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5')
    float_a_share_df = IO.read_data([trading_days[0], trading_days[-1]], columns=['FLOAT_A_SHR_TODAY'],
                                    alt='/data/group/800080/warehouse_event/prod/DATABASE/WIND/AShareEODDerivativeIndicator/AShareEODDerivativeIndicator.h5')
    md_df = IO.read_data([trading_days[0], trading_days[-1]], columns=['pre_close','amt'],
                         alt='/data/group/800080/warehouseJG/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    logger.info("basic and industry loaded!")
    basic_dict_all = {
        "neptune": neptune_basic,
        "industry": industry,
        "float_a_share_df": float_a_share_df,
        "md_df":md_df
    }
    if strategy == 'neptune':
        basic_dict = {key: basic_dict_all[key] for key in ['neptune', 'industry', 'float_a_share_df', 'md_df']}
    else:
        raise TypeError
    tasks = []
    for i in data_types:
        idx = lag + back_up_lag
        while idx < len(trading_days):
            dates = trading_days[idx-lag-back_up_lag:idx+1]
            tasks.append((i, dates, lag))
            idx += 1
    process_tasks = split_task(tasks, cpus)

    logger.info("start executing tasks")

    if cpus == 1:
        __execute(process_tasks[0], basic_dict, mdp, base_path)
    else:
        num_threads = min(cpus, len(process_tasks))
        pool = Pool(num_threads)
        for i in range(num_threads):
            pool.apply_async(__execute, (
                process_tasks[i], basic_dict, mdp, base_path,
            ))
        pool.close()
        pool.join()

    logger.info("execution finished")

if __name__ == "__main__":
    base_path_dict = {
        'neptune': "/dfs/group/800463/data/xdb_data_lag3_new/neptune/"
    }
    for tradingday_tmp in ['20190102', '20190103', '20191024', '20191025']:
        start_date = tradingday_tmp
        end_date = tradingday_tmp
        cpus = 1
        lag = 1
        # data_types = ["xdb_order",'xdb_trade','xdb_tickex']
        data_types = ['xdb_tickex']
        strategy_list = ['neptune']
        for strategy in strategy_list:
            base_path = base_path_dict[strategy]
            print(start_date,end_date)
            print(strategy)
            print(base_path)
            xquant_factor_data = FactorData()
            start_date = xquant_factor_data.tradingday(start_date, 1)[0]
            real_start_date = xquant_factor_data.tradingday(start_date, -(lag + 20+ 1))[0]
            trading_days = xquant_factor_data.tradingday(real_start_date, end_date)
            prepare_data(trading_days, data_types, base_path, cpus, lag, strategy = strategy)

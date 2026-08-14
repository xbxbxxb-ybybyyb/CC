import os

import numpy as np
import pandas as pd
import datetime as dt

import settings
from xfactor import FactorUtil
from xfactor.datasource import TDayData, XDBData, T_1FactorData
from xfactor.FactorUtil import FactorType
from settings import path_dict, RunMode
from xfactor.FactorDataPrepareUtil import fun_get_time
from xquant.factordata import FactorData
from loguru import logger
import copy

f = FactorData()

# load t-1 factor data for combined factors
def pre_load_data(task):
    if task["task_data_info"]["t_1_factor_data_info"]:
        data_info = list(task["task_data_info"]["t_1_factor_data_info"].values())[0]

        if "path" in data_info:
            data_path = data_info["path"]
        else:
            data_path = T_1FactorData.get_t_1_factor_path(data_info["name"])

        df = T_1FactorData.get_data(data_path, data_info["start_date"], data_info["end_date"], data_info["column"])
        return {data_info["name"]: df}
    elif task["task_data_info"]["other_t_day_data_info"]:
        data_info = list(task["task_data_info"]["other_t_day_data_info"].values())[0]
        path = data_info["path"]

        df = TDayData.get_data(path)
        return {data_info["name"]: df}

# 对加载的行业数据进行处理
def prepare_industry_dataframe(preload_database):
    if "industry" in preload_database and "industry_tmp" in preload_database:
        preload_database["industry"]['Industry'] = preload_database["industry_tmp"]['Industry'].unstack().shift(1).stack()
    return preload_database

# 用于precheck，因子一致性检测时加载数据
def load_data_for_same_check(task):
    database = {}

    if task["task_data_info"]["t_1_factor_data_info"]:
        for data_dict in task["task_data_info"]["t_1_factor_data_info"].values():
            data_path = data_dict["path"]
            df = T_1FactorData.get_data(data_path, data_dict["start_date"], data_dict["end_date"], data_dict["column"])
            database[data_dict["name"]] = df

    return database

# 获取策略对应的basic文件
def get_basic_data(strategy, start_date, end_date):
    if strategy in settings.valid_strategy_names:
        basic_df = T_1FactorData.get_data(settings.path_dict[strategy]["Basic"], start_date, end_date, [])
        return basic_df
    else:
        logger.error("Strategy name not correct! input={}".format(strategy))
        raise RuntimeError("Strategy name not correct")

#    获取指定batch依赖的数据集(全量)
def __load_data(task, preload_database, mode, cache=None):
    database = {}
    for k, v in preload_database.items():
        database[k] = v
    # database = copy.deepcopy(preload_database)
    # database["basic_file"] = preload_database["basic_file"].loc[pd.Timestamp(str(task["calc_end_date"])):pd.Timestamp(str(task["calc_end_date"]))].copy()
    database["basic_file"] = get_basic_data(task["strategy"], task["calc_start_date"], task["calc_end_date"])

    if task["factor_type"] == FactorType.T_1_FACTOR:
        return database
    else:
        strategy_name = task["strategy"]
        calc_date = task["calc_end_date"]

        if task["task_data_info"]["t_day_data_info"]:
            for data_name in task["task_data_info"]["t_day_data_info"]:
                if ('Tickfull' in data_name or 'Tick1s' in data_name or 'Cancel' in data_name) and (
                        calc_date < "20170101"):
                    database[data_name] = pd.DataFrame()
                    # database[data_name] = {}
                else:
                    path = TDayData.get_t_data_path(strategy_name, data_name, calc_date)
                    database[data_name] = TDayData.get_data(path)


        if task["task_data_info"]["xdb_data_info"]:
            for data_dict in task["task_data_info"]["xdb_data_info"].values():
                if (data_dict["name"] in ["xdb_tickfull", "xdb_tick1s", 'xdb_tickfulladdorder', "xdb_tickfull_cs",
                                          "xdb_tick1s_cs", 'xdb_tickfulladdorder_cs']) and (calc_date < "20170110"):
                    # database[data_dict["name"]] = pd.DataFrame()
                    database[data_dict["name"]] = {}
                elif data_dict["name"] in ['xdb_cancel', 'xdb_cancel_cs', 'xdb_tick1m', 'xdb_order1m', 'xdb_tick1m_cs', 'xdb_order1m_cs'] and (calc_date < "20170110"):
                    database[data_dict["name"]] = pd.DataFrame()
                else:
                    database[data_dict["name"]] = XDBData.get_xdb_data(data_dict["name"], strategy_name, calc_date)
                # TODO test
                # database[data_dict["name"]] = XDBData.get_xdb_data_test(data_dict["name"], strategy_name, calc_date)

        for data_dict in task["task_data_info"]["other_t_day_data_info"].values():
            database[data_dict["name"]] = TDayData.get_data(data_dict["path"])

        return database

# 当因子【不】依赖xdb数据的时候调用，返回值为dict
def get_database_T_N_without_xdb(task, factor, task_database):
    start_date = task["calc_start_date"]
    end_date = task["calc_end_date"]

    factor_database = {'skip': False}
    factor_database["basic_file"] = task_database["basic_file"]
    if task["factor_type"] == FactorType.T_1_FACTOR:
        for data_dict in factor.t_1_factor_data:
            break_flag = True
            counter = 0
            trading_days = []
            while break_flag:
                if counter > 5:
                    raise RuntimeError("tradingday接口调用失败超过5次！")

                try:
                    trading_days = f.tradingday(start_date, -int(data_dict["lag"]))
                    break_flag = False
                except Exception as e:
                    logger.warning("tradingday接口调用失败！重试...")
                    counter += 1

            factor_database[data_dict["name"]] = task_database[data_dict["name"]].loc[trading_days[0]:end_date].copy()
    else:
        for data_dict in factor.t_1_factor_data:
            break_flag = True
            counter = 0
            trading_days = []
            while break_flag:
                if counter > 5:
                    raise RuntimeError("tradingday接口调用失败超过5次！")

                try:
                    trading_days = f.tradingday(start_date, -int(data_dict["lag"]))
                    break_flag = False
                except Exception as e:
                    logger.warning("tradingday接口调用失败！重试...")
                    counter += 1

            factor_database[data_dict["name"]] = task_database[data_dict["name"]].loc[trading_days[0]:trading_days[-2]].copy()

    return factor_database


# 当因子为截面因子的时候调用，返回值为dict
def get_database_with_xdb_cs(task, factor, task_database):
    start_date = task["calc_start_date"]
    end_date = task["calc_end_date"]

    factor_database = {'skip': False}
    factor_database["basic_file"] = task_database["basic_file"]

    for data_dict in factor.t_1_factor_data:
        break_flag = True
        counter = 0
        trading_days = []
        while break_flag:
            if counter > 5:
                raise RuntimeError("tradingday接口调用失败超过5次！")

            try:
                trading_days = f.tradingday(start_date, -int(data_dict["lag"]))
                break_flag = False
            except Exception as e:
                logger.warning("tradingday接口调用失败！重试...")
                counter += 1
        factor_database[data_dict["name"]] = task_database[data_dict["name"]].loc[
                                             trading_days[0]:trading_days[-2]].copy()

    for data_dict in factor.xdb_data:
        symbol_df = task_database[data_dict["name"]]
        symbol_df["rank"] = symbol_df.groupby('Ticker')["MDDate"].apply(
            lambda x: x.rank(method="dense", ascending=False))
        symbol_df["rank"] = symbol_df["rank"].astype('int')
        df = symbol_df[symbol_df["rank"] <= int(data_dict["lag"])]
        factor_database[data_dict["name"]] = df

    return factor_database


def get_symbol_t_1_factor_datadict(factor_name, symbol, cur_df, calc_date, strategy, data_dict, result):
    if not "skip" in result:
        result["skip"] = False
    cur_dict = result

    if cur_df.empty:
        cur_dict["skip"] = True
        logger.warning(
            "因子数据准备异常：存在empty dataframe！factor={}, date={}, strategy={}, symbol={}, empty_data_name={}".format(
                factor_name, calc_date, strategy, symbol, data_dict["name"]))

    cur_dict[data_dict["name"]] =cur_df.copy()
    return cur_dict


def reload_xdb_data(data_name, strategy, start_date):
    return XDBData.get_xdb_data_from_xdb_format(data_name, strategy, start_date)


# 当因子依赖xdb数据的是调用，返回值为一个以[dt, ticker]为index的dataframe
def get_database_T_N_with_xdb(task, factor, task_database):
    start_date = task["calc_start_date"]
    end_date = task["calc_end_date"]

    basic = task_database["basic_file"]

    groupby = basic.loc[task["calc_start_date"]].groupby(level=[0, 1])
    symbol_data_df = pd.DataFrame()

    for data_dict in factor.xdb_data:
        cur_dic = task_database[data_dict["name"]]
        if data_dict["name"] == "xdb_tick1s" and cur_dic["lag_info"] < data_dict["lag"]:
            cur_dic = reload_xdb_data(data_dict["name"], task["strategy"], start_date)

        valid_df = FactorUtil.valid_dates
        if symbol_data_df.empty:
            symbol_data_df = groupby.apply(lambda x: get_symbol_xdb_datadict(
                factor.factor_name, x.name[1], cur_dic, valid_df, start_date, task["strategy"], data_dict, {}))
        else:
            symbol_data_df = groupby.apply(lambda x: get_symbol_xdb_datadict(
                factor.factor_name, x.name[1], cur_dic, valid_df, start_date, task["strategy"], data_dict,
                symbol_data_df.loc[task["calc_start_date"], x.name[1]]))

    for data_dict in factor.t_1_factor_data:
        break_flag = True
        counter = 0
        trading_days = []
        while break_flag:
            if counter > 5:
                raise RuntimeError("tradingday接口调用失败超过5次！")

            try:
                trading_days = f.tradingday(start_date, -int(data_dict["lag"]))
                break_flag = False
            except Exception as e:
                logger.warning("tradingday接口调用失败！重试...")
                counter += 1

        cur_df = task_database[data_dict["name"]].loc[trading_days[0]:trading_days[-2]]

        if symbol_data_df.empty:
            symbol_data_df = groupby.apply(lambda x: get_symbol_t_1_factor_datadict(
                factor.factor_name, x.name[1], cur_df, start_date, task["strategy"], data_dict, {}))
        else:
            symbol_data_df = groupby.apply(lambda x: get_symbol_t_1_factor_datadict(
                factor.factor_name, x.name[1], cur_df, start_date, task["strategy"], data_dict,
                symbol_data_df.loc[task["calc_start_date"], x.name[1]]))

    return symbol_data_df, groupby

def get_symbol_tday_datadict(factor_name, symbol, calc_date, strategy, data_name, task_database, result):
    if not "skip" in result:
        result["skip"] = False
    if not "Ticker" in result:
        result["Ticker"] = symbol
    cur_dict = result
    if data_name == "MarketIndTTick":
        zt_time = task_database["basic_file"].loc[calc_date, symbol]["ZT_Time"]
        zt_time = max(fun_get_time(int(zt_time), -3), 93000000)
        try:
            ind = task_database["industry"].loc[calc_date, symbol]["Industry"]
        except Exception as e:
            ind = np.nan
        if np.isnan(ind):
            df = pd.DataFrame()
        else:
            df = task_database[data_name]

        if df.empty:
            cur_dict["skip"] = True
            logger.warning(
                "因子数据准备异常：存在empty dataframe！factor={}, date={}, strategy={}, symbol={}, empty_data_name={}".format(
                    factor_name, calc_date, strategy, symbol, data_name))
        else:
            df = df[(df["Industry"] == ind) & (df['MDTime'] < zt_time)]
            df = df.groupby(['dt', 'Ticker']).nth([0, -1])
        cur_dict[data_name] = df.copy()

    elif data_name in ['LastTouchTTick', 'MarketTTick', 'Market1TTick','MarketTTick_ALL']:
        zt_time = task_database["basic_file"].loc[calc_date, symbol]["ZT_Time"]
        zt_time = max(fun_get_time(int(zt_time), -3), 93000000)
        df = task_database[data_name]
        if df.empty:
            cur_dict["skip"] = True
            logger.warning(
                "因子数据准备异常：存在empty dataframe！factor={}, date={}, strategy={}, symbol={}, empty_data_name={}".format(
                    factor_name, calc_date, strategy, symbol, data_name))
            cur_dict[data_name] = pd.DataFrame()

        else:
            df = df[df['MDTime'] < zt_time]

            if data_name == 'Market1TTick':
                if '.SH' in symbol:
                    df = df[df['is_SH']]
                else:
                    df = df[~df['is_SH']]
            if data_name in ['MarketTTick', 'Market1TTick']:
                df = df.groupby(['dt', 'Ticker']).nth([0, -1])
                cur_dict[data_name] = df.copy()
            else:
                cur_dict[data_name] = df
    elif data_name in [ 'MarketTTick_Ceres']:
        df = task_database[data_name]
        if df.empty:
            cur_dict["skip"] = True
            logger.warning(
                "因子数据准备异常：存在empty dataframe！factor={}, date={}, strategy={}, symbol={}, empty_data_name={}".format(
                    factor_name, calc_date, strategy, symbol, data_name))
            cur_dict[data_name] = pd.DataFrame()

        else:
            df = df.groupby(['dt', 'Ticker']).nth([0, -1])
            cur_dict[data_name] = df.copy()
    elif "_cs" in data_name:
        df = task_database[data_name]
        if strategy in ['saturn', 'sell']:  # saturn/sell要进行策略样本筛选
            df = df[df['lzt_label_pattern'].isin([3, 4])]
            df = df[df['after_not_ul_len'] > 10]
        cur_dict[data_name] = df
    else:
        try:
            df = task_database[data_name].xs(symbol, level=1, drop_level=False)
        except Exception as e:
            cur_dict["skip"] = True
            df = pd.DataFrame()
            logger.warning(
                "因子数据准备异常：存在empty dataframe！factor={}, date={}, strategy={}, symbol={}, empty_data_name={}".format(
                    factor_name, calc_date, strategy, symbol, data_name))
        cur_dict[data_name] = df.copy()
    return cur_dict


def get_symbol_xdb_datadict(factor_name, symbol, cur_df, valid_df, calc_date, strategy, data_dict, result):
    if not "skip" in result:
        result["skip"] = False
    if not "Ticker" in result:
        result["Ticker"] = symbol

    cur_dict = result
    if data_dict["name"] in ["xdb_tick1s", "xdb_tickfull", "xdb_tickfulladdorder"]:

        if not cur_df:
            cur_dict["skip"] = True
            logger.warning(
                "因子数据准备异常：存在empty dataframe！factor={}, date={}, strategy={}, symbol={}, empty_data_name={}".format(
                    factor_name, calc_date, strategy, symbol, data_dict["name"]))
            cur_dict[data_dict["name"]] = pd.DataFrame()
            return cur_dict

        try:
            symbol_df = cur_df[symbol]
        except Exception as e:
            cur_dict["skip"] = True
            cur_dict[data_dict["name"]] = pd.DataFrame()
            logger.warning(
                "因子数据准备异常：存在empty dataframe！factor={}, date={}, strategy={}, symbol={}, empty_data_name={}".format(
                    factor_name, calc_date, strategy, symbol, data_dict["name"]))
            return cur_dict

        if not symbol_df.empty:
            cur_df["lag_info"] = int(data_dict["lag"])
            if calc_date <= settings.xdb_check_range[0] or calc_date >= settings.xdb_check_range[1]:
                days = sorted(symbol_df["MDDate"].unique())
                tmp_df = symbol_df[(symbol_df["MDDate"] >= days[-min(int(data_dict["lag"]), len(days))])
                                   & (symbol_df["MDDate"] <= days[-1])]
                if tmp_df.empty:
                    cur_dict["skip"] = True
                    logger.warning(
                        "因子数据准备异常：存在empty dataframe！factor={}, date={}, strategy={}, symbol={}, empty_data_name={}".format(
                            factor_name, calc_date, strategy, symbol, data_dict["name"]))
                else:
                    cur_df[symbol] = tmp_df

            else:
                dates_li = list(valid_df.loc[calc_date, symbol].values)[:int(data_dict["lag"])]
                if not dates_li or set(dates_li) & settings.xdb_bad_dates_set:
                    cur_dict["skip"] = True
                    logger.warning(
                        "因子数据准备异常：涉及异常xdb日期，跳过！factor={}, date={}, strategy={}, symbol={}, empty_data_name={}".format(
                            factor_name, calc_date, strategy, symbol, data_dict["name"]))
                else:
                    days = sorted(symbol_df["MDDate"].unique())
                    cur_df[symbol] = symbol_df[(symbol_df["MDDate"] >= days[-min(int(data_dict["lag"]), len(days))])
                                               & (symbol_df["MDDate"] <= days[-1])]
                    if cur_df[symbol].empty:
                        cur_dict["skip"] = True
                        logger.warning(
                            "因子数据准备异常：存在empty dataframe！factor={}, date={}, strategy={}, symbol={}, empty_data_name={}".format(
                                factor_name, calc_date, strategy, symbol, data_dict["name"]))

        cur_dict[data_dict["name"]] = cur_df[symbol]
    elif "_cs" in data_dict["name"]:
        if cur_df.empty:
            cur_dict["skip"] = True
            # logger.warning(
            #     "因子数据准备异常：存在empty dataframe！factor={}, date={}, strategy={}, symbol={}, empty_data_name={}".format(
            #         factor_name, calc_date, strategy, symbol, data_dict["name"]))
            cur_dict[data_dict["name"]] = pd.DataFrame()
            return cur_dict

        symbol_df = cur_df

        df = pd.DataFrame()
        if not symbol_df.empty:
            if calc_date <= settings.xdb_check_range[0] or calc_date >= settings.xdb_check_range[1]:
                days = sorted(symbol_df["MDDate"].unique())
                df = symbol_df[(symbol_df["MDDate"] >= days[-min(int(data_dict["lag"]), len(days))])
                               & (symbol_df["MDDate"] <= days[-1])].copy()
                if df.empty:
                    cur_dict["skip"] = True
                    # logger.warning(
                    #     "因子数据准备异常：存在empty dataframe！factor={}, date={}, strategy={}, symbol={}, empty_data_name={}".format(
                    #         factor_name, calc_date, strategy, symbol, data_dict["name"]))
                else:
                    if strategy in ['saturn', 'sell']:  # saturn/sell要进行策略样本筛选
                        df = df[df['pattern'].isin([3, 4])]
                        df = df[df['after_not_ul_len'] > 10]

            else:
                dates_li = list(valid_df.loc[calc_date, symbol].values)[:int(data_dict["lag"])]
                if (not dates_li or set(dates_li) & settings.xdb_bad_dates_set) and (
                        data_dict["name"] in ['xdb_order_cs',
                                              'xdb_trade_cs',
                                              'xdb_order1m_cs',
                                              'xdb_tick1m_cs',
                                              'xdb_cancel_cs',
                                              "xdb_tick1s_cs",
                                              "xdb_tickfull_cs",
                                              'xdb_tickfulladdorder_cs',
                                              ]):
                    cur_dict["skip"] = True
                    # logger.warning(
                    #     "因子数据准备异常：涉及异常xdb日期，跳过！factor={}, date={}, strategy={}, symbol={}, empty_data_name={}".format(
                    #         factor_name, calc_date, strategy, symbol, data_dict["name"]))
                else:
                    days = sorted(symbol_df["MDDate"].unique())
                    df = symbol_df[(symbol_df["MDDate"] >= days[-min(int(data_dict["lag"]), len(days))])
                                   & (symbol_df["MDDate"] <= days[-1])].copy()
                    if df.empty:
                        cur_dict["skip"] = True
                        # logger.warning(
                        #     "因子数据准备异常：存在empty dataframe！factor={}, date={}, strategy={}, symbol={}, empty_data_name={}".format(
                        #         factor_name, calc_date, strategy, symbol, data_dict["name"]))
                    else:
                        if strategy in ['saturn', 'sell']:  # saturn/sell要进行策略样本筛选
                            df = df[df['lzt_label_pattern'].isin([3, 4])]
                            df = df[df['after_not_ul_len'] > 10]

        else:
            cur_dict["skip"] = True
            # logger.warning(
            #     "因子数据准备异常：存在empty dataframe！factor={}, date={}, strategy={}, symbol={}, empty_data_name={}".format(
            #         factor_name, calc_date, strategy, symbol, data_dict["name"]))

        cur_dict[data_dict["name"]] = df
    else:
        if cur_df.empty:
            cur_dict["skip"] = True
            logger.warning(
                "因子数据准备异常：存在empty dataframe！factor={}, date={}, strategy={}, symbol={}, empty_data_name={}".format(
                    factor_name, calc_date, strategy, symbol, data_dict["name"]))
            cur_dict[data_dict["name"]] = pd.DataFrame()
            return cur_dict

        try:
            symbol_df = cur_df.xs(symbol, level=1, drop_level=False)
        except Exception as e:
            cur_dict["skip"] = True
            symbol_df = pd.DataFrame()
            logger.warning(
                "因子数据准备异常：存在empty dataframe！factor={}, date={}, strategy={}, symbol={}, empty_data_name={}".format(
                    factor_name, calc_date, strategy, symbol, data_dict["name"]))

        df = pd.DataFrame()
        if not symbol_df.empty:
            if calc_date <= settings.xdb_check_range[0] or calc_date >= settings.xdb_check_range[1]:
                days = sorted(symbol_df["MDDate"].unique())
                df = symbol_df[(symbol_df["MDDate"] >= days[-min(int(data_dict["lag"]), len(days))])
                               & (symbol_df["MDDate"] <= days[-1])].copy()
                if df.empty:
                    cur_dict["skip"] = True
                    logger.warning(
                        "因子数据准备异常：存在empty dataframe！factor={}, date={}, strategy={}, symbol={}, empty_data_name={}".format(
                            factor_name, calc_date, strategy, symbol, data_dict["name"]))
            else:
                dates_li = list(valid_df.loc[calc_date, symbol].values)[:int(data_dict["lag"])]
                if (not dates_li or set(dates_li) & settings.xdb_bad_dates_set) and (data_dict["name"] in ['xdb_order',
                                                                                                           'xdb_trade',
                                                                                                           'xdb_order1m',
                                                                                                           'xdb_tick1m',
                                                                                                           'xdb_cancel']):
                    cur_dict["skip"] = True
                    logger.warning(
                        "因子数据准备异常：涉及异常xdb日期，跳过！factor={}, date={}, strategy={}, symbol={}, empty_data_name={}".format(
                            factor_name, calc_date, strategy, symbol, data_dict["name"]))
                else:
                    days = sorted(symbol_df["MDDate"].unique())
                    df = symbol_df[(symbol_df["MDDate"] >= days[-min(int(data_dict["lag"]), len(days))])
                                   & (symbol_df["MDDate"] <= days[-1])].copy()
                    if df.empty:
                        cur_dict["skip"] = True
                        logger.warning(
                            "因子数据准备异常：存在empty dataframe！factor={}, date={}, strategy={}, symbol={}, empty_data_name={}".format(
                                factor_name, calc_date, strategy, symbol, data_dict["name"]))
        else:
            cur_dict["skip"] = True
            logger.warning(
                "因子数据准备异常：存在empty dataframe！factor={}, date={}, strategy={}, symbol={}, empty_data_name={}".format(
                    factor_name, calc_date, strategy, symbol, data_dict["name"]))

        cur_dict[data_dict["name"]] = df
    return cur_dict

def update_pre_T_N(task, factor, symbol, date, pre_T_N, result):
    if not "skip" in result:
        result["skip"] = False
    if not "Ticker" in result:
        result["Ticker"] = symbol

    if factor.xdb_data:
        result["pre_T_N"] = pre_T_N.loc[(date, symbol), :].copy()
    else:
        result["pre_T_N"] = pre_T_N.copy()

    if result["pre_T_N"].empty:
        result["skip"] = True
        logger.warning(
            "因子数据准备异常：存在empty dataframe！factor={}, date={}, strategy={}, symbol={}, empty_data_name={}".format(
                factor.factor_name, task["calc_start_date"], task["strategy"], symbol, "pre_T_N"))

    return result


def get_database_T_Day(task, factor, task_database, precalc_database, symbol_data_df):
    start_date = task["calc_start_date"]
    end_date = task["calc_end_date"]

    basic = task_database["basic_file"]

    groupby = basic.loc[task["calc_start_date"]].groupby(level=[0, 1])

    if "pre_T_N" in precalc_database:
        if symbol_data_df.empty:
            symbol_data_df = groupby.apply(lambda x:  update_pre_T_N(task, factor, x.name[1], start_date, precalc_database["pre_T_N"], {}))
        else:
            symbol_data_df = groupby.apply(lambda x: update_pre_T_N(
                task, factor, x.name[1], start_date, precalc_database["pre_T_N"], symbol_data_df.loc[task["calc_start_date"], x.name[1]]))

    for data in factor.t_day_data:
        if symbol_data_df.empty:
            symbol_data_df = groupby.apply(lambda x:  get_symbol_tday_datadict(
                factor.factor_name, x.name[1], start_date, task["strategy"], data, task_database, {}))
        else:
            symbol_data_df = groupby.apply(lambda x: get_symbol_tday_datadict(
                factor.factor_name, x.name[1], start_date, task["strategy"], data, task_database,
                symbol_data_df.loc[task["calc_start_date"], x.name[1]]))

    for data in factor.other_t_day_data:
        if symbol_data_df.empty:
            symbol_data_df = groupby.apply(lambda x: get_symbol_tday_datadict(
                factor.factor_name, x.name[1], start_date, task["strategy"], data, task_database, {}))
        else:
            symbol_data_df = groupby.apply(lambda x: get_symbol_tday_datadict(
                factor.factor_name, x.name[1], start_date, task["strategy"], data, task_database,
                symbol_data_df.loc[task["calc_start_date"], x.name[1]]))

    return symbol_data_df, groupby

# 适用于纯cs的场景
def get_database_T_Day_pure_cs(task, factor, task_database, precalc_database):
    for data in factor.t_day_data:
        df = task_database[data]
        if task["strategy"] in ['saturn', 'sell']:  # saturn/sell要进行策略样本筛选
            df = df[df['lzt_label_pattern'].isin([3, 4])]
            df = df[df['after_not_ul_len'] > 10]
        precalc_database[data] = df

    for data in factor.other_t_day_data:
        df = task_database[data]
        if task["strategy"] in ['saturn', 'sell']:  # saturn/sell要进行策略样本筛选
            df = df[df['lzt_label_pattern'].isin([3, 4])]
            df = df[df['after_not_ul_len'] > 10]
        precalc_database[data] = df

    return precalc_database

def filter_and_check_pre_T_N(factor_name, symbol_database, symbol):
    if symbol_database["skip"] == True:
        return pd.Series({factor_name: np.nan})
    pre_T_N_df = symbol_database["pre_T_N"]
    if pre_T_N_df.shape[0] != 1:
        logger.error("PrecalcT-N异常！返回df行数不为1！factpr_name={}, symbol={}, pre_T_N_df_row_number={}".format(
            factor_name, symbol, pre_T_N_df.shape[0]
        ))
        raise RuntimeError("PrecalcT-N异常")

    return pre_T_N_df.iloc[0]

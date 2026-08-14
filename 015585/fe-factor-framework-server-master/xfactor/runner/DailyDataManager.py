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


# 获取数据
def __load_data(depend_data_type_list, stock_list, start_date, end_date, minute_start_date, financial_start_date,
                input_factor_lib, run_type, realtime_minute_data_path=None, cache=None, *args):
    return False


# # 只有盘前数据准备才会调用这个，获取全部的xdb股票数据
# def pre_load_xdb_data(xdb_tasks, calc_date):
#     dates = f.tradingday(calc_date, -(3 + 1))
#     basic_dict = {}
#     industry_dict = {}
#     for date in dates:
#         basic_df_path = settings.full_basic_path.format(date)
#
#     for task in xdb_tasks:
#         for data_dict in task["task_data_info"]["xdb_data_info"].values():
#             dates = f.tradingday(calc_date, -int(data_dict["lag"] + 1 + 20))
#             XDBData.get_data()
#     data_info = list(task["task_data_info"]["xdb_data_info"].values())[0]
#     XDBData.get_data(data_info["name"], data_info["calc_start_date"])
#     # return {data_info["name"]: df}


def pre_load_data_daily(task):
    if task["task_data_info"]["t_day_data_info"]:
        data_name = task["task_data_info"]["t_day_data_info"][0]
        path = TDayData.get_t_data_path(task["strategy"], data_name, task["calc_start_date"])
        df = TDayData.get_data(path)
        return {data_name: df}

    elif task["task_data_info"]["t_1_factor_data_info"]:
        data_info = list(task["task_data_info"]["t_1_factor_data_info"].values())[0]
        if "path" in data_info:
            data_path = data_info["path"]
        else:
            data_path = T_1FactorData.get_t_1_factor_path(data_info["name"])
        df = T_1FactorData.get_data(data_path, data_info["start_date"], data_info["end_date"], data_info["column"])
        return {data_info["name"]: df}

    elif task["task_data_info"]["xdb_data_info"]:
        data_info = list(task["task_data_info"]["xdb_data_info"].values())[0]
        df = XDBData.get_xdb_data(data_info["name"], data_info["strategy"], task["calc_start_date"])
        return {data_info["name"]: df}

    elif task["task_data_info"]["other_t_day_data_info"]:
        data_info = list(task["task_data_info"]["other_t_day_data_info"].values())[0]
        if "path" in data_info:
            path = data_info["path"]
        else:
            path = TDayData.get_t_data_path(data_info["strategy"], data_info["name"], task["calc_start_date"])
        df = TDayData.get_data(path)
        return {data_info["name"]: df}

# 对加载的行业数据进行处理
def prepare_industry_dataframe(preload_database):
    if "industry" in preload_database and "industry_tmp" in preload_database:
        preload_database["industry"]['Industry'] = preload_database["industry_tmp"]['Industry'].unstack().shift(
            1).stack()
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

# 每日因子更新使用
def get_daily_update_basic_data(strategy, date):
    if strategy in settings.valid_strategy_names:
        return pd.read_hdf(settings.path_dict[strategy]["DailyUpdateBasic"].format(date, date, date))
    else:
        logger.error("Strategy name not correct! input={}".format(strategy))
        raise RuntimeError("Strategy name not correct")

# 盘前数据准备使用
def get_prod_prepare_basic_data(strategy, date):
    if strategy in settings.valid_strategy_names:
        path = settings.path_dict[strategy]["ProdPrepBasic"].format(date, date, date)
        return pd.read_hdf(path)
    else:
        logger.error("Strategy name not correct! input={}".format(strategy))
        raise RuntimeError("Strategy name not correct")

def get_database_T_N_without_xdb(task, factor, task_database, mode):
    start_date = str(task["calc_start_date"])
    end_date = str(task["calc_end_date"])

    factor_database = {
        'skip': False,
        'basic_file': task_database["basic_file"].copy()
    }

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

            factor_database[data_dict["name"]] = task_database[data_dict["name"]].loc[
                                                 trading_days[0]:trading_days[-2]].copy()

    return factor_database

# 当因子为截面因子的时候调用，返回值为dict
def get_database_with_xdb_cs(task, factor, task_database):
    start_date = task["calc_start_date"]
    end_date = task["calc_end_date"]

    factor_database = {'skip': False}

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

def get_database_T_N_with_xdb(task, factor, task_database, mode):
    start_date = str(task["calc_start_date"])
    end_date = str(task["calc_end_date"])
    symbol_data_df = pd.DataFrame()

    basic = task_database["basic_file"]

    if mode == RunMode.prod_prepare:
        groupby = basic.loc[start_date].groupby(level=[0, 1])
        for data_dict in factor.xdb_data:
            cur_df = task_database[data_dict["name"]]

            if symbol_data_df.empty:
                symbol_data_df = groupby.apply(lambda x: get_symbol_xdb_datadict(
                    factor.factor_name, x.name[1], cur_df[x.name[1]], start_date, task["strategy"], data_dict, {}))
            else:
                symbol_data_df = groupby.apply(lambda x: get_symbol_xdb_datadict(
                    factor.factor_name, x.name[1], cur_df[x.name[1]], start_date, task["strategy"], data_dict,
                    symbol_data_df.loc[start_date, x.name[1]]))
    else:
        groupby = basic.loc[start_date].groupby(level=[0, 1])
        for data_dict in factor.xdb_data:
            cur_df = task_database[data_dict["name"]]

            if symbol_data_df.empty:
                symbol_data_df = groupby.apply(lambda x: get_symbol_xdb_datadict(
                    factor.factor_name, x.name[1], cur_df, start_date, task["strategy"], data_dict, {}))
            else:
                symbol_data_df = groupby.apply(lambda x: get_symbol_xdb_datadict(
                    factor.factor_name, x.name[1], cur_df, start_date, task["strategy"], data_dict,
                    symbol_data_df.loc[start_date, x.name[1]]))

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
                symbol_data_df.loc[start_date, x.name[1]]))

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

    elif data_name in ['LastTouchTTick', 'MarketTTick', 'Market1TTick']:
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


def get_symbol_xdb_datadict(factor_name, symbol, cur_df, calc_date, strategy, data_dict, result):
    if not "skip" in result:
        result["skip"] = False
    if not "Ticker" in result:
        result["Ticker"] = symbol
    cur_dict = result
    symbol_df = cur_df

    if symbol_df.empty:
        cur_dict["skip"] = True
        df = pd.DataFrame()
        logger.warning(
            "因子数据准备异常：存在empty dataframe！factor={}, date={}, strategy={}, symbol={}, empty_data_name={}".format(
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
    start_date = str(task["calc_start_date"])
    end_date = str(task["calc_end_date"])

    basic = task_database["basic_file"]

    groupby = basic.loc[start_date].groupby(level=[0, 1])

    if "pre_T_N" in precalc_database:
        if symbol_data_df.empty:
            symbol_data_df = groupby.apply(lambda x:  update_pre_T_N(task, factor, x.name[1], start_date, precalc_database["pre_T_N"], {}))
        else:
            symbol_data_df = groupby.apply(lambda x: update_pre_T_N(
                task, factor, x.name[1], start_date, precalc_database["pre_T_N"], symbol_data_df.loc[start_date, x.name[1]]))

    for data in factor.t_day_data:
        if symbol_data_df.empty:
            symbol_data_df = groupby.apply(lambda x: get_symbol_tday_datadict(
                factor.factor_name, x.name[1], start_date, task["strategy"], data, task_database, {}))
        else:
            symbol_data_df = groupby.apply(lambda x: get_symbol_tday_datadict(
                factor.factor_name, x.name[1], start_date, task["strategy"], data, task_database,
                symbol_data_df.loc[start_date, x.name[1]]))

    for data in factor.other_t_day_data:
        if symbol_data_df.empty:
            symbol_data_df = groupby.apply(lambda x: get_symbol_tday_datadict(
                factor.factor_name, x.name[1], start_date, task["strategy"], data, task_database, {}))
        else:
            symbol_data_df = groupby.apply(lambda x: get_symbol_tday_datadict(
                factor.factor_name, x.name[1], start_date, task["strategy"], data, task_database,
                symbol_data_df.loc[start_date, x.name[1]]))

    return symbol_data_df, groupby


def load_xdb_data(xdb_tasks, preload_database, num_threads):
    # preload_database["industry"]
    basic_dict = {}
    symbols = []

    for task in xdb_tasks:
        data_dict = list(task["task_data_info"]["xdb_data_info"].values())[0]
        break_flag = True
        counter = 0
        full_date_range = []
        while break_flag:
            if counter > 5:
                raise RuntimeError("tradingday接口调用失败超过5次！")

            try:
                full_date_range = f.tradingday(task["calc_start_date"], -int(data_dict["lag"] + 1 + 20))
                break_flag = False
            except Exception as e:
                logger.warning("tradingday接口调用失败！重试...")
                counter += 1

        for date in full_date_range[-7:]:
            if date in basic_dict:
                continue
            basic_dict[date] = TDayData.get_full_basic_df(date)  # TODO
        if not symbols:
            symbols = list(basic_dict[full_date_range[-2]].index.get_level_values(1))
        XDBData.get_all_xdb_data(data_dict["name"], full_date_range, symbols, data_dict["lag"], basic_dict,
                             preload_database['industry'], task["strategy"], num_threads)

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

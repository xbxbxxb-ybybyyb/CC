## Step 2
######### copy indicator of index {"000016", "000300", "000852", "000905"}

import os
import subprocess
from loguru import logger
from xquant.factordata import FactorData
factorData = FactorData()

from xdb.stockdata import StockData
a = StockData()

index_symbols = {"000016.SH", "000300.SH", "000852.SH", "000905.SH"}

def copy_index_indicator_from_offical_to_working_dir(offical_indicator_folder, work_indicator_folder,
                                                     change_date):
    trading_date_list = factorData.tradingday(change_date, -28)[:-1]
    logger.info(f"copy index indicator for dates={trading_date_list}")
    for date in trading_date_list:
        source_dir = f"{offical_indicator_folder}/{date}/offset_0/01_Indicator"
        target_dir = f"{work_indicator_folder}/{date}/offset_0/01_Indicator/"
        if not os.path.exists(f"{target_dir}"):
            os.makedirs(f"{target_dir}")

        for index_sym in index_symbols:
            source_file = f"{source_dir}/{index_sym}"
            cp_cmd = f"cp {source_file} {target_dir}"
            # print(cp_cmd)
            subprocess.run(cp_cmd, shell=True)

def get_channel_set(date, stock_list):
    channel_set = set()

    for stock in stock_list:
        market = stock.split(".")[-1]
        channel_info_map = a.get_channel_info(date, market, stock)
        for channel in channel_info_map.values():
            channel_str = f"stock_{market.lower()}_{channel}"
            channel_set.add(channel_str)
    return channel_set


import os
import datetime
import time
from xquant.factordata import FactorData
from loguru import logger
import multiprocessing
import subprocess

# lm = notice.LinkMessage()
s = FactorData()
trade_dates = s.tradingday(20210101, 20210631)


# trade_dates = ['20231113', '20231108', '20231114', '20231207', '20231212', '20231107', '20231109', '20231110']
# trade_dates = ["20221214"]
# cmd_prefix = "/dfs/user/666466/02_data_runner/01_indicator/indicator_generator"
# cmd_prefix_shipan_backtest = "/dfs/user/666466/02_data_runner/01_indicator/indicator_generator"

def run(cmd):
    result = subprocess.run(cmd, shell=True)


def generate_indicator_for_channels(cmd_prefix, testcase_root_folder, trade_date, channel_list, log_folder):
    # testcase_root_folder = f"/data/user/019906/018728/cpp_projects/csi_calculator/testcase_v6_history_data/{trade_date}"
    if not os.path.exists(f"{log_folder}"):
        os.makedirs(f"{log_folder}")

    cmd_list = []

    for channel in channel_list:
        cmd = f"{cmd_prefix} {testcase_root_folder}/{channel} > {log_folder}/{trade_date}_{channel}.log"
        cmd_list.append(cmd)
    logger.info(f"cmd_list={cmd_list}")
    pool = multiprocessing.Pool(processes=len(cmd_list))
    for cmd in cmd_list:
        pool.apply_async(run, (cmd,))
    pool.close()
    pool.join()

def generate_indicator_per_day(cmd_prefix, testcase_root_folder, date, log_folder):
    logger.info(f"{date} generate indicator start, {testcase_root_folder}")
    time_start = time.time()

    channel_list = [
        "stock_sh_1", "stock_sh_2",
        "stock_sh_3", "stock_sh_4", "stock_sh_5", "stock_sh_6", "future", "index"]
    generate_indicator_for_channels(cmd_prefix, testcase_root_folder, date, channel_list, log_folder)

    channel_list = ["stock_sz_2011", "stock_sz_2012", "stock_sz_2013", "stock_sz_2014", "stock_sz_2015"]
    generate_indicator_for_channels(cmd_prefix,testcase_root_folder, date, channel_list, log_folder)

    time_end = time.time()
    logger.info(f"{date} generate indicator end, time_cost={(time_end - time_start) / 60} min")

def generate_indicator_for_index_stock_change(cmd_prefix, trade_date, stock_list, testcase_root_folder, log_root_folder=".", minute_shift=0):
    channel_set = get_channel_set(trade_date, stock_list)
    logger.info(f"trade_date={trade_date}, stock_list={stock_list}, channel_set={channel_set}")

    test_case_base_folder_index_stock_change = os.path.join(testcase_root_folder, trade_date,
                                                            f"offset_{minute_shift}/01_Indicator/index_stock_change")
    log_base_folder_index_stock_change = f"{log_root_folder}/{trade_date}/offset_{minute_shift}/01_Indicator/index_stock_change"
    if not os.path.exists(log_base_folder_index_stock_change):
        os.makedirs(log_base_folder_index_stock_change)

    cmd_list = []

    for channel in channel_set:
        cmd = f"{cmd_prefix} {test_case_base_folder_index_stock_change}/{channel} > {log_base_folder_index_stock_change}/{trade_date}_{channel}.log"
        cmd_list.append(cmd)
    logger.info(f"date={trade_date}, cmd_list={cmd_list}")

    # 500G内存可支持约8个任务并行
    # pool = multiprocessing.Pool(processes=len(cmd_list))
    pool = multiprocessing.Pool(processes=6)
    for cmd in cmd_list:
        pool.apply_async(run, (cmd,))
    pool.close()
    pool.join()

def generate_indicator_for_index_stock_change_sequential(cmd_prefix, trade_date_list, batch_run_stock_list, testcase_root_folder, log_root_folder=".", minute_shift=0):
    for date in trade_date_list:
        logger.info(f"{date} offset_{minute_shift} stock_list({batch_run_stock_list}) generate indicator start")
        time_start = time.time()

        generate_indicator_for_index_stock_change(cmd_prefix, date, batch_run_stock_list, testcase_root_folder, log_root_folder, minute_shift=minute_shift)

        time_end = time.time()
        logger.info(f"{date} offset_{minute_shift} stock_list({batch_run_stock_list}) generate indicator, time_cost={round((time_end - time_start) / 60, 2)} min")

def generate_indicator_for_index_stock_change_parallel(cmd_prefix, trade_date_list, stock_list, testcase_root_folder, log_root_folder=".", minute_shift=0):
    logger.info(f"{trade_date_list} offset_{minute_shift } generate indicator start")
    time_start = time.time()
    cmd_list = []
    for trade_date in trade_date_list:
        channel_set = get_channel_set(trade_date, stock_list)
        logger.info(f"trade_date={trade_date}, offset={minute_shift}, stock_list={stock_list}, channel_set={channel_set}")

        # v = "/data/user/019906/devtree/csical-bundle/cmake-build-release/single"

        test_case_base_folder_index_stock_change = os.path.join(testcase_root_folder, trade_date,
                                                                f"offset_{minute_shift}/01_Indicator/index_stock_change")
        log_base_folder_index_stock_change = f"{log_root_folder}/{trade_date}/offset_{minute_shift}/01_Indicator/index_stock_change"
        if not os.path.exists(log_base_folder_index_stock_change):
            os.makedirs(log_base_folder_index_stock_change)

        for channel in channel_set:
            cmd = f"{cmd_prefix} {test_case_base_folder_index_stock_change}/{channel} > {log_base_folder_index_stock_change}/{trade_date}_{channel}.log"
            cmd_list.append(cmd)

    logger.info(f"cmd_list={cmd_list}")

    # 500G内存可支持约8个任务并行
    # pool = multiprocessing.Pool(processes=len(cmd_list))
    pool = multiprocessing.Pool(processes=6)
    for cmd in cmd_list:
        pool.apply_async(run, (cmd,))
    pool.close()
    pool.join()

    time_end = time.time()
    logger.info(f"{trade_date_list} generate indicator end, time_cost={int((time_end - time_start) / 60)} min")

def copy_generated_indicator_to_official_folder(trading_date_list, stock_list, offical_indicator_folder, work_indicator_folder):
    # offical_indicator_folder = "/dfs/user/019906/03_mobius/02_FactorData"
    # work_indicator_folder = "/dfs/user/019906/03_mobius/02_FactorData_index_stock_change"

    for date in trading_date_list:
        source_dir = f"{work_indicator_folder}/{date}/offset_0/01_Indicator"
        target_dir = f"{offical_indicator_folder}/{date}/offset_0/01_Indicator/"

        for stock in stock_list:
            source_file = f"{source_dir}/{stock}"
            cp_cmd = f"cp {source_file} {target_dir}"
            # print(cp_cmd)
            subprocess.run(cp_cmd, shell=True)

def run_shipan_backtest(cmd_prefix, testcase_root_folder, date, log_file):
    logger.info(f"{date} run shipan backtest start, {testcase_root_folder}")
    time_start = time.time()

    cmd = f"{cmd_prefix} {testcase_root_folder} > {log_file}"
    logger.info(f"shipan_backtest_cmd={cmd}")
    subprocess.run(cmd, shell=True)

    time_end = time.time()
    logger.info(f"{date} run shipan backtest end, time_cost={(time_end - time_start) / 60} min")

    ## check backtest log
    # 1）检查是否存在error；2）检查是否finish replay data
def check_shipan_backtest_log(log_file):
    check_success = True
    finish_replay_date = False

    with open(log_file, 'r', encoding='utf8') as f:
        for line in f:
            if "error" in line or "Error" in line or "ERROR" in line:
                if "position" in line and "> size" in line:
                    continue
                elif "open file failed errorno = %s, path = %s" in line:
                    continue
                else:
                    logger.error(f"ErrorInLine:{line}")
                    check_success = False
                    # break
            elif "finish replaying" in line:
                finish_replay_date = True
    if not finish_replay_date:
        logger.error(f"Not finish replay market data")
        check_success = False
    return check_success

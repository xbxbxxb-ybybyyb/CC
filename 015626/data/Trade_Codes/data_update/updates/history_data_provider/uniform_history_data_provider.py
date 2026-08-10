import math
import multiprocessing
import numpy as np
import os
import pandas as pd
import re
import signal
import struct
import time
import zstd
from loguru import logger
from xquant.factordata import FactorData

from consts import *

real_trading = True

test_base_input_dir = r"/data/user/015626/data/share/LOCAL_DATA/Mobius/data_sample_for_dolphindb/2023年6月"

base_input_dir = r"/data/group/800466/warehouse/prod/MD/MarketData/MD/"

base_exec_dir = r"/data/user/018728/cpp_projects/csi_calculator/history_data"

base_store_dir = r"/data/user/018728/cpp_projects/csi_calculator/history_data"

base_flags_dir = r"/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS"

def check_flag_files(base_flag_files_dir: str, dt: str):
    flags_dir = os.path.join(base_flag_files_dir, dt)
    cfg_file = os.path.join(flags_dir, dt + "_CFG.success")
    concat_file = os.path.join(flags_dir, dt + "_tick_concat.success")
    index_file = os.path.join(flags_dir, dt + "_INDEX.success")
    if os.path.exists(cfg_file) and os.path.exists(concat_file) and os.path.exists(index_file):
        return True
    return False

class UniformHistoryDataProvider:
    def __init__(self, exec_date):
        fd_service = FactorData()
        self.exec_date = exec_date
        self.all_dates = fd_service.tradingday(exec_date, -6)
        self.base_trading_day = fd_service.tradingday(exec_date, 2)[1]
        self.ih_arr = fd_service.hset_index('000016.SH', exec_date)['stock'].values
        self.im_arr = fd_service.hset_index('000852.SH', exec_date)['stock'].values
        self.if_arr = fd_service.hset_index('000300.SH', exec_date)['stock'].values
        self.ic_arr = fd_service.hset_index('000905.SH', exec_date)['stock'].values

    # target_date: history data to generate
    # base_date: base date used to generate constituen stocks
    def gen_uniform_files(self, target_date, last_his_trading_day, numthreads):
        logger.info("Generate uniform data, target_date={}, last_history_trading_date={}", target_date, last_his_trading_day)
        total_symbols = list(
            set(list(self.ih_arr + ".h5") + list(self.im_arr + ".h5") + list(self.if_arr + ".h5") + list(
                self.ic_arr + ".h5")))
        total_symbols = sorted(total_symbols)
        tasks = self.split_task(total_symbols, numthreads)
        pool = multiprocessing.Pool(processes=numthreads)
        s = FactorData()
        trade_status_df = s.get_factor_value('Basic_factor', stock=[], mddate=[target_date],
                                             factor_names=["trade_status"])

        stock_data_input_path = os.path.join(base_input_dir, "CHINA_STOCK/MINUTE")
        for i in range(len(tasks)):
            # merge_stock_file(i, stock_path, tasks[i], target_date, base_date, i)
            pool.apply_async(self.merge_stock_file, (
                i, stock_data_input_path, tasks[i], target_date, last_his_trading_day, trade_status_df, self.ih_arr, self.im_arr,
                self.if_arr, self.ic_arr), error_callback=self.throw_error)
        pool.close()
        pool.join()
        logger.info("stock file generated, target_date={}, exec_base_date={}", target_date, last_his_trading_day)
        self.check_stock_directory(stock_data_input_path, target_date, last_his_trading_day)
        logger.info("file check finished")
        # merge the generated file
        os.system(base_exec_dir + "/indicator_merge " + base_exec_dir + "/stock/base_" + self.base_trading_day + "/" + target_date + " 0")

        future_data_input_path = os.path.join(base_input_dir, "CHINA_FUTURES/MINUTE/backup")
        self.merge_future_file(future_data_input_path, os.listdir(future_data_input_path), target_date, 1)
        logger.info("future file generated")
        os.system(base_exec_dir + "/indicator_merge " + base_exec_dir + "/future/" + target_date + " 1")

        index_data_input_path = os.path.join(base_input_dir, "CHINA_INDEX/MINUTE")
        self.merge_index_file(index_data_input_path, os.listdir(index_data_input_path), target_date, 1)
        logger.info("index file generated")
        os.system(base_exec_dir + "/indicator_merge " + base_exec_dir + "/index/" + target_date + " 2")

    def throw_error(self, e):
        logger.info("error caught, error={}\n", e)
        logger.info(e.__cause__)
        os.killpg(os.getpgid(os.getpid()), signal.SIGKILL)

    def split_task(self, task_arr, num_threads):
        if num_threads == 1:
            return [task_arr]
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

    def check_stock_directory(self, path, check_date, exec_base_date):
        for i in self.ih_arr:
            if not os.path.exists(os.path.join(path, i + ".h5")):
                logger.error(
                    "ERROR!  File: " + i + ".h5 not found, 生成日期 = " + check_date + " , 成分股日期= " + exec_base_date + " IH")
        for i in self.im_arr:
            if not os.path.exists(os.path.join(path, i + ".h5")):
                logger.error(
                    "ERROR!  File: " + i + ".h5 not found, 生成日期 = " + check_date + " , 成分股日期= " + exec_base_date + " IM")
        for i in self.if_arr:
            if not os.path.exists(os.path.join(path, i + ".h5")):
                logger.error(
                    "ERROR!  File: " + i + ".h5 not found, 生成日期 = " + check_date + " , 成分股日期= " + exec_base_date + " IF")
        for i in self.ic_arr:
            if not os.path.exists(os.path.join(path, i + ".h5")):
                logger.error(
                    "ERROR!  File: " + i + ".h5 not found, 生成日期 = " + check_date + " , 成分股日期= " + exec_base_date + " IC")

    def merge_stock_file(self, proc_no, base_input_path, files, target_date, exec_base_date, trade_status_df, ih_arr, im_arr,
                         if_arr, ic_arr):
        intermediate_output_dir = base_exec_dir + "/stock/base_" + self.base_trading_day + "/" + target_date
        if not os.path.exists(intermediate_output_dir):
            os.system("mkdir -p {}".format(intermediate_output_dir))
        headerItemSize = 8 + 2 + 8 + 8
        totalHeaderSize = headerItemSize * len(files)
        logger.info("Processor: {} start, target_date={}, exec_base_date={}", proc_no, target_date, exec_base_date)
        try:
            with open(os.path.join(intermediate_output_dir, "stock_indicator_" + target_date + "_part_" + str(proc_no)),
                      "wb") as file:
                file.write(b'12345600')
                file.write(struct.pack('<q', totalHeaderSize))
                headerCurrentIndex = 8 + 8
                start = 8 + 8 + totalHeaderSize
                end = 0
                for filename in files:
                    # logger.info("Processor: {}, start, filename={}, target_date={}, base_date={}", proc_no, filename, target_date, base_date)
                    df = pd.read_hdf(os.path.join(base_input_path, filename))
                    if real_trading:
                        df = df[-1450:]
                    df.reset_index(inplace=True)
                    sym = df["Ticker"][0].strip()
                    symbol_str = sym.ljust(16, '\0')
                    if sym in ic_arr:
                        df["group"] = "IC\0\0\0\0\0\0"
                    elif sym in if_arr:
                        df["group"] = "IF\0\0\0\0\0\0"
                    elif sym in im_arr:
                        df["group"] = "IM\0\0\0\0\0\0"
                    elif sym in ih_arr:
                        df["group"] = "IH\0\0\0\0\0\0"
                    else:
                        file.write(str.encode(sym[:6] + '\0' + '\0'))
                        # file exists, but not belong to constituent stock of the base date
                        file.write(str.encode("02"))
                        file.write(struct.pack('<q', start))
                        file.write(struct.pack('<q', start))
                        headerCurrentIndex += headerItemSize
                        continue
                    df["timestamp"] = np.apply_along_axis(lambda x: np.int64(re.sub("\D", "", str(x))[:14]),
                                                          arr=df[["dt"]].values, axis=1)
                    # filter the target date
                    df = df[(df["timestamp"] > (int(target_date) * 1000000)) & (
                            df["timestamp"] < (int(target_date) * 1000000 + 235959))].reset_index(drop=True)
                    if df.empty:
                        file.write(str.encode(sym[:6] + '\0' + '\0'))
                        file.write(str.encode("01"))
                        file.write(struct.pack('<q', start))
                        file.write(struct.pack('<q', start))
                        headerCurrentIndex += headerItemSize
                        logger.warning("ticker of target date not exists in h5, ticker={}, target_date={}", sym,
                                       target_date)
                        continue
                    df["close_pre_adj"] = np.nan
                    df["open_pre_adj"] = np.nan
                    df["high_pre_adj"] = np.nan
                    df["low_pre_adj"] = np.nan
                    df["volume_pre_adj"] = np.nan
                    df["amended"] = False
                    status_result = trade_status_df.loc[(target_date, sym), 'trade_status']
                    if status_result == "停牌":
                        df["suspended"] = True
                    else:
                        df["suspended"] = False
                    df["symbol"] = symbol_str
                    selected1 = df[stock_part1_indicators]
                    selected2 = df[stock_part2_indicators]
                    # logger.info("Processor={}, generating {} bytes str, target_date={}, exec_base_date={}", proc_no, filename, target_date, exec_base_date)
                    group_nparr = np.array(df["group"].apply(lambda x: str.encode(x)))
                    symbol_nparr = np.array(df["symbol"].apply(lambda x: str.encode(x)))
                    timestamp_nparr = np.array(df["timestamp"].apply(lambda x: struct.pack('<q', x)))
                    amend_nparr = np.array(df["amended"].apply(lambda x: struct.pack('<?', x)))
                    selected1_nparr = np.apply_along_axis(lambda x: np.array(x.tobytes(), dtype=np.void),
                                                          arr=selected1.values, axis=1)
                    suspend_nparr = np.array(df["suspended"].apply(lambda x: struct.pack('<?', x)))
                    selected2_nparr = np.apply_along_axis(lambda x: np.array(x.tobytes(), dtype=np.void),
                                                          arr=selected2.values, axis=1)

                    df_nparr = group_nparr + symbol_nparr + timestamp_nparr + amend_nparr + selected1_nparr + suspend_nparr + selected2_nparr
                    final_nparr = np.add.reduce(df_nparr)

                    compressed = zstd.ZSTD_compress(final_nparr)
                    if sym[-2:] == "\0\0":
                        logger.info("part file is empty! file=" + filename)
                    if sym[:6] + '\0' + '\0' == "\0\0\0\0\0\0\0\0":
                        logger.info("symbol is empty! file=" + filename)
                    file.write(str.encode(sym[:6] + '\0' + '\0'))
                    file.write(str.encode(sym[-2:]))
                    file.write(struct.pack('<q', start))
                    file.write(struct.pack('<q', start + len(compressed)))
                    headerCurrentIndex += headerItemSize
                    file.seek(start, 0)
                    file.write(compressed)
                    end = start + len(compressed)
                    start = end
                    file.seek(headerCurrentIndex, 0)
        # logger.info("Processor={}, finish processing {}, target_date={}, exec_base_date={}", proc_no, filename, target_date, exec_base_date)
        except Exception as e:
            logger.error("exception caught! process_id=" + proc_no + ", file=" + filename + ", exception=" + str(
                e.__cause__) + ", trace=" + str(e.__traceback__))

    def merge_future_file(self, base_input_path, files, target_date, pid):
        intermediate_output_dir = base_exec_dir + "/future/" + target_date
        if not os.path.exists(intermediate_output_dir):
            os.system("mkdir -p {}".format(intermediate_output_dir))
        file_counter = 0
        for i in files:
            if i == 'T_MINUTE.h5':
                continue
            counter = 0
            zero_counter = 0
            zero_list = []
            df = pd.read_hdf(os.path.join(base_input_path, i))
            if real_trading:
                df = df[-1450 * 4:]
            df.reset_index(inplace=True)
            df["timestamp"] = np.apply_along_axis(lambda x: np.int64(re.sub("\D", "", str(x))[:14]),
                                                  arr=df[["dt"]].values, axis=1)
            df = df[(df["timestamp"] > (int(target_date) * 1000000)) & (
                    df["timestamp"] < (int(target_date) * 1000000 + 235959))].reset_index(drop=True)
            if df.empty:
                counter += 1
                zero_counter += 1
                zero_list.append(i)
                continue
            sym_arr = df["Ticker"].unique()
            headerItemSize = 8 + 2 + 8 + 8
            totalHeaderSize = headerItemSize * len(sym_arr)
            with open(os.path.join(intermediate_output_dir, "future_indicator_" + target_date + "_part_" + str(file_counter)),
                      "wb") as file:
                file.write(b'12345600')
                file.write(struct.pack('<q', totalHeaderSize))
                headerCurrentIndex = 8 + 8
                start = 8 + 8 + totalHeaderSize
                end = 0
                for i in sym_arr:
                    cur_df = df[df["Ticker"] == i].reset_index(drop=True)
                    sym = cur_df["Ticker"][0]
                    symbol_str = sym.ljust(16, '\0')

                    cur_df["amended"] = False
                    cur_df["suspended"] = False
                    cur_df["symbol"] = symbol_str

                    selected1 = cur_df[future_indicators]
                    symbol_nparr = np.array(cur_df["symbol"].apply(lambda x: str.encode(x)))
                    timestamp_nparr = np.array(cur_df["timestamp"].apply(lambda x: struct.pack('<q', x)))
                    amend_nparr = np.array(cur_df["amended"].apply(lambda x: struct.pack('<?', x)))
                    selected1_nparr = np.apply_along_axis(lambda x: np.array(x.tobytes(), dtype=np.void),
                                                          arr=selected1.values, axis=1)
                    suspend_nparr = np.array(cur_df["suspended"].apply(lambda x: struct.pack('<?', x)))
                    final_nparr = np.add.reduce(
                        symbol_nparr + timestamp_nparr + amend_nparr + selected1_nparr + suspend_nparr)
                    compressed = zstd.ZSTD_compress(final_nparr)
                    if (len(compressed) == 0):
                        logger.info("1")
                    file.write(str.encode(sym[:6] + '\0' + '\0'))
                    file.write(str.encode('\0' + '\0'))
                    file.write(struct.pack('<q', start))
                    file.write(struct.pack('<q', start + len(compressed)))
                    headerCurrentIndex += headerItemSize
                    file.seek(start, 0)
                    file.write(compressed)
                    end = start + len(compressed)
                    start = end
                    file.seek(headerCurrentIndex, 0)
            file_counter += 1

    def merge_index_file(self, base_input_path, files, date, pid):
        intermediate_output_dir = base_exec_dir + "/index/" + date
        if not os.path.exists(intermediate_output_dir):
            os.system("mkdir -p {}".format(intermediate_output_dir))
        file_counter = 0
        for i in files:
            counter = 0
            zero_counter = 0
            zero_list = []

            df = pd.read_hdf(os.path.join(base_input_path, i))
            if real_trading:
                df = df[-1450:]
            df.reset_index(inplace=True)
            df["timestamp"] = np.apply_along_axis(lambda x: np.int64(re.sub("\D", "", str(x))[:14]),
                                                  arr=df[["dt"]].values, axis=1)
            df = df[(df["timestamp"] > (int(date) * 1000000)) & (
                    df["timestamp"] < (int(date) * 1000000 + 235959))].reset_index(drop=True)

            if df.empty:
                counter += 1
                zero_counter += 1
                zero_list.append(i)
                continue

            sym_arr = df["Ticker"].unique()
            headerItemSize = 8 + 2 + 8 + 8
            totalHeaderSize = headerItemSize * len(sym_arr)
            with open(os.path.join(intermediate_output_dir, "index_indicator_" + date + "_part_" + str(file_counter)),
                      "wb") as file:
                file.write(b'12345600')
                file.write(struct.pack('<q', totalHeaderSize))
                headerCurrentIndex = 8 + 8
                start = 8 + 8 + totalHeaderSize
                end = 0
                for i in sym_arr:
                    cur_df = df[df["Ticker"] == i].reset_index(drop=True)
                    sym = cur_df["Ticker"][0]
                    symbol_str = sym.ljust(16, '\0')

                    cur_df["amended"] = False
                    cur_df["suspended"] = False
                    cur_df["symbol"] = symbol_str

                    selected1 = cur_df[['open', 'close', 'high', 'low', 'volume', 'amount']]

                    symbol_nparr = np.array(cur_df["symbol"].apply(lambda x: str.encode(x)))
                    timestamp_nparr = np.array(cur_df["timestamp"].apply(lambda x: struct.pack('<q', x)))
                    amend_nparr = np.array(cur_df["amended"].apply(lambda x: struct.pack('<?', x)))
                    selected1_nparr = np.apply_along_axis(lambda x: np.array(x.tobytes(), dtype=np.void),
                                                          arr=selected1.values, axis=1)
                    suspend_nparr = np.array(cur_df["suspended"].apply(lambda x: struct.pack('<?', x)))
                    final_nparr = np.add.reduce(
                        symbol_nparr + timestamp_nparr + amend_nparr + selected1_nparr + suspend_nparr)
                    compressed = zstd.ZSTD_compress(final_nparr)
                    file.write(str.encode(sym[:6] + '\0' + '\0'))
                    file.write(str.encode('\0' + '\0'))
                    file.write(struct.pack('<q', start))
                    file.write(struct.pack('<q', start + len(compressed)))
                    headerCurrentIndex += headerItemSize
                    file.seek(start, 0)
                    file.write(compressed)
                    end = start + len(compressed)
                    start = end
                    file.seek(headerCurrentIndex, 0)
            file_counter += 1

    def gen_base_date_all_data(self):
        if real_trading and not check_flag_files(base_flags_dir, self.all_dates[-1]):
            logger.warning("real trading flag files check not succeed")
            return
        for dt in self.all_dates:
            self.gen_uniform_files(dt, self.exec_date, 50)
        # self.gen_uniform_files(self.all_dates[-1], self.exec_date, 42)

if __name__ == "__main__":
    # execute this script before trading day, this will get 6 history dates
    last_his_trading_day = "20231008"  # get the next trading day's dependent history trading day data
    history_data_provider = UniformHistoryDataProvider(last_his_trading_day)
    history_data_provider.gen_base_date_all_data()

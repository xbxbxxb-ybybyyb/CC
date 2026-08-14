import os
import datetime as dt
from multiprocessing import Pool
from loguru import logger
from h5data.IO import IO
import settings
import xfactor.runner.DailyDataManager as DailyDataManager
from xfactor.runner.DailyTaskManager import DailyTaskManager
import xfactor.FactorUtil as FactorUtil
from settings import RunMode
import pandas as pd

'''
update daily/prepare prod data

'''


def run(factor_name_list, start_date, end_date, strategy, output_dir, mode, options=None):
    calc_num_cpus = 1
    if mode != RunMode.prod_prepare and mode != RunMode.daily_update:
        logger.error("DailyRunner 仅支持mode = RunMode.prod_prepare 或 mode = RunMode.daily_update")
        return
    if options is not None:
        if "calc.num_cpus" in options:
            calc_num_cpus = int(options["calc.num_cpus"])

    # daily runner每次只支持单个策略执行
    if strategy.lower() not in settings.valid_strategy_names:
        logger.error("运行策略名称不正确！输入策略名为={}".format(strategy))
        return

    # if strategy not in output_dir:
    #     logger.error("strategy={} not in output_path={}!".format(strategy, output_dir))
    #     raise RuntimeError("path not correct")

    if mode == RunMode.prod_prepare:

        # days = FactorUtil.factor_data.tradingday(start_date, -2)
        settings.prod_prep_date = str(start_date)
        # start_date = days[0]
        # end_date = days[0]
        if not os.path.exists(output_dir):
            logger.error("path not exists! path_name={}, path={}".format("prod_prepare_path", output_dir))
            raise RuntimeError("path not exists")
        settings.prod_data_dir = output_dir
    else:
        if not os.path.exists(output_dir):
            logger.error("path not exists! path_name={}, path={}".format("daily_update_path", output_dir))
            raise RuntimeError("path not exists")
        settings.daily_update_dir = output_dir

    __calc_factor(strategy, factor_name_list, str(start_date), str(end_date), mode, calc_num_cpus, output_dir)

    return


def __calc_factor(strategy, factor_name_list, start_date, end_date, mode, calc_num_cpus, output_dir):
    result = {}
    cost_result = {}
    task_manager = DailyTaskManager(factor_name_list, start_date, end_date, strategy)

    preload_database = {}

    task_dict = task_manager.generate_task(mode)

    if mode != RunMode.prod_prepare:
        # 计算每日因子值时，直接读取预先生成好的xdb文件，因此与其他数据准备工作同时进行
        task_dict["data_prepare_tasks"] = task_dict["h5_prepare_tasks"] + task_dict["xdb_prepare_tasks"] + task_dict["t_day_prepare_tasks"]
    else:
        task_dict["data_prepare_tasks"] = task_dict["h5_prepare_tasks"]

    if task_dict["data_prepare_tasks"]:
        logger.info(
            "计算开始：当前任务种类=data_prepare, 任务数量={}, 进程数={}".format(len(task_dict["data_prepare_tasks"]), calc_num_cpus))

        if calc_num_cpus == 1:

            prepare_results = [__preload_data(task) for task in task_dict["data_prepare_tasks"]]
            preload_database = __generate_preload_database(preload_database, prepare_results)

        else:

            prepare_ids = []
            pool = Pool(min(calc_num_cpus, len(task_dict["data_prepare_tasks"])))
            for task in task_dict["data_prepare_tasks"]:
                prepare_ids.append(pool.apply_async(__preload_data,
                                                    (task,)
                                                    ))
            pool.close()
            pool.join()
            prepare_results = [prepare_id.get() for prepare_id in prepare_ids]
            pool.terminate()
            preload_database = __generate_preload_database(preload_database, prepare_results)

    preload_database = DailyDataManager.prepare_industry_dataframe(preload_database)

    if mode == RunMode.prod_prepare:
        preload_database["basic_file"] = DailyDataManager.get_prod_prepare_basic_data(strategy, start_date)
        # 盘前数据准备需要单独准备xdb数据，
        if task_dict["xdb_prepare_tasks"]:
            preload_database = DailyDataManager.load_xdb_data(task_dict["xdb_prepare_tasks"], preload_database,
                                                              calc_num_cpus)
            # preload_database["full_basic_file"] = DailyDataManager.TDayData.get_full_basic_df(start_date)
    else:
        preload_database["basic_file"] = DailyDataManager.get_daily_update_basic_data(strategy, start_date)

    logger.info(
        "计算开始：当前任务种类=factor_calculate, 任务数量={}, 进程数={}".format(len(task_dict["calc_tasks"]), calc_num_cpus))
    if calc_num_cpus == 1:
        task_results = [__execute_task(task, preload_database, mode) for task in task_dict["calc_tasks"]]

    else:
        task_ids = []
        pool = Pool(min(calc_num_cpus, len(task_dict["calc_tasks"])))
        for task in task_dict["calc_tasks"]:
            task_ids.append(pool.apply_async(__execute_task, (
                task, preload_database, mode,
            )))
        pool.close()
        pool.join()
        task_results = [task_id.get() for task_id in task_ids]
        pool.terminate()

    error_factors = {}

    for sub_result in task_results:
        result, cost_result, error_factors = __merge_factor_values(result, cost_result, error_factors, sub_result, mode)
    logger.info("全部计算完成")

    if error_factors:
        for i in error_factors:
            for j in i:
                logger.error("factor calc error! factor_name=" + j)

    __save_factors(result, start_date, mode)

    return


def __save_factors(result, start_date, mode):
    ## TODO 更新每日更新路径
    if mode == RunMode.daily_update:
        # saved_factor_dirs = []
        for name, data_dict in result.items():
            strategy = name.split("_")[-1]
            factor_name = data_dict["factor_name"]
            update_path = os.path.join(settings.daily_update_dir, strategy, str(start_date), "factor")
            if not os.path.exists(update_path):
                os.system("mkdir -p " + update_path)
            factor_path = update_path + "/" + data_dict["factor_name"] + "_{}_{}.h5".format(
                start_date, start_date)
            # saved_factor_dirs.append({
            #     'strategy': strategy,
            #     'name': factor_name,
            #     'path': factor_path
            # })
            if os.path.exists(factor_path):
                IO.pd_hdf5_writer(data_dict["factor_value"], factor_path, dataset=factor_name, append=True)
            else:
                IO.pd_hdf5_writer(data_dict["factor_value"], factor_path, dataset=factor_name)
        logger.info("factor value saved!")
    else:
        for dic in result.values():
            prepare_dest = os.path.join(settings.prod_data_dir, dic["strategy"], str(start_date), "factor_prod_prepare")
            if not os.path.exists(prepare_dest):
                os.system("mkdir -p " + prepare_dest)
            file_path = prepare_dest + "/" + dic["factor_name"] + "_{}_{}.h5".format(
                start_date, start_date)
            if os.path.exists(file_path):
                IO.pd_hdf5_writer(dic["factor_value"], file_path, dataset=dic["factor_name"], override=True)
            else:
                IO.pd_hdf5_writer(dic["factor_value"], file_path, dataset=dic["factor_name"])

    return


# 运行指定task
def __execute_task(task, preload_database, mode):
    result = {}

    if task["factor_type"] == FactorUtil.FactorType.T_1_FACTOR:
        try:
            factor_class = task["factor_class_list"][0]
            factor_instance = FactorUtil.create_factor_instance(factor_class)
            time1 = dt.datetime.now()
            factor_database = DailyDataManager.get_database_T_N_without_xdb(task, factor_class, preload_database, mode)
            factor_database["skip"] = False  # 纯T-1_FACTOR因子默认h5文件不会为空，置为False

            time2 = dt.datetime.now()
            # precalculate
            if factor_class.need_pre_calculate_T_N:
                factor_database = factor_instance.pre_calculate_T_N_data(factor_database)

                factor_database["pre_T_N"] = FactorUtil.fun_append_next_tradingday(factor_database["pre_T_N"])
                result_df = pd.DataFrame(index=factor_database["basic_file"].index)
                for col in factor_database["pre_T_N"].columns:
                        result_df[col] = factor_database["pre_T_N"][col].unstack().shift(1).stack()
                factor_database["pre_T_N"] = result_df


            # get result and filter and shift
            time3 = dt.datetime.now()
            val_df = factor_instance.calculate(factor_database)
            time4 = dt.datetime.now()

            # val_df.fillna(factor_class.fill_na_value, inplace=True)
            val_df = FactorUtil.fill_factor_na_values(val_df, factor_class, factor_database["basic_file"])

            result[factor_class.factor_name + "_" + task["strategy"]] = {
                "error": False,
                "factor_name": factor_class.factor_name,
                "factor_type": FactorUtil.FactorType.T_1_FACTOR,
                "factor_value": val_df,
                "calc_start_date": task["calc_start_date"],
                "calc_end_date": task["calc_end_date"],
                "calc_cost": time4 - time3
            }
            logger.info(
                "子任务完成：strategy={}, factor={}, calc_start_date={}, calc_end_date={}, prep_h5_database_cost={}, pre_calc_T-N_cost={}, prepare_t_day_database_cost=n/a, prepareT_cost=n/a, calc_cost={}".format(
                    task["strategy"], factor_class.factor_name, task["calc_start_date"], task["calc_end_date"],
                    time2 - time1, time3 - time2, time4 - time3))
            return result
        except Exception as e:
            logger.error(
                "exception caught! strategy={}, factors={}, calc_start_date={},calc_end_date={}, error={}, trace={}".format(
                    task["strategy"], factor_class.factor_name, task["calc_start_date"], task["calc_end_date"],
                    e.__cause__, e.__traceback__))
            result[factor_class.factor_name + "_" + task["strategy"]] = {
                "error": True,
                "factor_name": factor_class.factor_name,
                "factor_type": FactorUtil.FactorType.T_1_FACTOR,
                "factor_value": pd.DataFrame(),
                "calc_start_date": task["calc_start_date"],
                "calc_end_date": task["calc_end_date"],
                "calc_cost": -1
            }
            return result
    else:
        try:
            factor_class = task["factor_class_list"][0]

            if "TOrder" in factor_class.t_day_data and task["strategy"] == 'jupiter':
                return

            if (FactorUtil.check_xdb_tick_1s_full(factor_class)) and (str(task["calc_start_date"]) < "20170110"):
                return

            factor_instance = FactorUtil.create_factor_instance(factor_class)
            if FactorUtil.check_pure_cs_factor(factor_class):
                # get factor database
                time1 = dt.datetime.now()
                factor_h5_database = DailyDataManager.get_database_with_xdb_cs(task, factor_class, preload_database)
                time2 = dt.datetime.now()

                # precalculate
                if factor_class.need_pre_calculate_T_N:
                    # precalculate t-1 factor 也是dt,Ticker, 所有提前准备的数据都存放到 "pre_T_N"里
                    factor_h5_database = factor_instance.pre_calculate_T_N_data(factor_h5_database)

                    if mode == RunMode.prod_prepare and (
                            len(factor_class.other_t_day_data) != 0 or len(factor_class.t_day_data) != 0):
                        time3 = dt.datetime.now()

                        result[factor_class.factor_name + "_" + task["strategy"]] = {
                            "error": False,
                            "factor_name": factor_class.factor_name,
                            "factor_type": FactorUtil.FactorType.T_DAY_FACTOR,
                            "factor_value": factor_h5_database["pre_T_N"],
                            "calc_start_date": task["calc_start_date"],
                            "calc_end_date": task["calc_end_date"],
                            "calc_cost": time3 - time2
                        }

                        logger.info(
                            "子任务完成：strategy={}, factor={}, calc_start_date={}, calc_end_date={}, prep_h5_database_cost={}, pre_calc_T-N_cost={}, prepare_t_day_database_cost=n/a, prepareT_cost=n/a, calc_cost={}".format(
                                task["strategy"], factor_class.factor_name, task["calc_start_date"],
                                task["calc_end_date"],
                                time2 - time1, time3 - time2, "n/a"))
                        return result

                time3 = dt.datetime.now()

                factor_h5_database = DailyDataManager.get_database_T_Day_pure_cs(task, factor_class, preload_database,
                                                                            factor_h5_database)
                factor_h5_database = factor_instance.prepare_T_data(factor_h5_database)

                time4 = dt.datetime.now()

                val_df = factor_instance.calculate(factor_h5_database)

                time5 = dt.datetime.now()

                # 入库时不进行basicfile的区分
                result_df = pd.DataFrame(index=preload_database["basic_file"].index)
                for col in val_df.columns:
                    result_df[col] = val_df[col]

                # result_df.fillna(factor_class.fill_na_value, inplace=True)
                result_df = FactorUtil.fill_factor_na_values(result_df, factor_class, preload_database["basic_file"])

                result[factor_class.factor_name + "_" + task["strategy"]] = {
                    "error": False,
                    "factor_name": factor_class.factor_name,
                    "factor_type": FactorUtil.FactorType.T_DAY_FACTOR,
                    "factor_value": result_df,
                    "factor_value_full": pd.DataFrame(),
                    "calc_date": "",
                    "calc_cost": time5 - time4
                }

            else:
                if factor_class.xdb_data:
                    pre_T_N_dict = {}
                    time1 = dt.datetime.now()
                    symbol_data_dict, groupby = DailyDataManager.get_database_T_N_with_xdb(task, factor_class,
                                                                                                  preload_database, mode)
                    time2 = dt.datetime.now()

                    # precalculate
                    if factor_class.need_pre_calculate_T_N:
                        symbol_data_dict = groupby.apply(lambda x: factor_instance.pre_calculate_T_N_data(
                            symbol_data_dict.loc[task["calc_start_date"], x.name[1]]))

                        prepare_df = groupby.apply(
                            lambda x: DailyDataManager.filter_and_check_pre_T_N(factor_class.factor_name, symbol_data_dict.loc[task["calc_start_date"], x.name[1]], x.name[1]))
                        # prepare_df = FactorUtil.fun_append_next_tradingday(prepare_df)
                        # result_df = pd.DataFrame(index=preload_database["basic_file"].index)
                        # for col in prepare_df.columns:
                        #         result_df[col] = prepare_df[col].unstack().shift(1).stack()
                        pre_T_N_dict["pre_T_N"] = prepare_df

                        if mode == RunMode.prod_prepare and (len(factor_class.other_t_day_data) != 0 or len(factor_class.t_day_data) != 0):
                            time3 = dt.datetime.now()

                            result[factor_class.factor_name + "_" + task["strategy"]] = {
                                "error": False,
                                "factor_name": factor_class.factor_name,
                                "factor_type": FactorUtil.FactorType.T_DAY_FACTOR,
                                "factor_value": prepare_df,
                                "calc_start_date": task["calc_start_date"],
                                "calc_end_date": task["calc_end_date"],
                                "calc_cost": time3 - time2
                            }

                            logger.info(
                                "子任务完成：strategy={}, factor={}, calc_start_date={}, calc_end_date={}, prep_h5_database_cost={}, pre_calc_T-N_cost={}, prepare_t_day_database_cost=n/a, prepareT_cost=n/a, calc_cost={}".format(
                                    task["strategy"], factor_class.factor_name, task["calc_start_date"],
                                    task["calc_end_date"],
                                    time2 - time1, time3 - time2, "n/a"))
                            return result

                    time3 = dt.datetime.now()
                    symbol_data_dict, groupby = DailyDataManager.get_database_T_Day(task, factor_class, preload_database,
                                                                                    pre_T_N_dict, symbol_data_dict)
                    time4 = dt.datetime.now()

                    # get sub result
                    symbol_data_dict = groupby.apply(lambda x: factor_instance.prepare_T_data(
                        symbol_data_dict.loc[task["calc_start_date"], x.name[1]]))

                    time5 = dt.datetime.now()

                    result_df = groupby.apply(lambda x: factor_instance.calculate(
                        symbol_data_dict.loc[task["calc_start_date"], x.name[1]]))

                    # result_df.fillna(factor_class.fill_na_value, inplace=True)
                    result_df = FactorUtil.fill_factor_na_values(result_df, factor_class,
                                                                 preload_database["basic_file"])
                    end_time = dt.datetime.now()
                    result[factor_class.factor_name + "_" + task["strategy"]] = {
                        "error": False,
                        "factor_name": factor_class.factor_name,
                        "factor_type": FactorUtil.FactorType.T_DAY_FACTOR,
                        "factor_value": result_df,
                        "calc_start_date": task["calc_start_date"],
                        "calc_end_date": task["calc_end_date"],
                        "calc_cost": end_time - time5
                    }
                    #
                    logger.info(
                        "子任务完成：strategy={}, factor={}, calc_start_date={}, calc_end_date={}, prep_h5_database_cost={}, pre_calc_T-N_cost={}, prepare_t_day_database_cost={}, prepareT_cost={}, calc_cost={}".format(
                            task["strategy"], factor_class.factor_name, task["calc_start_date"], task["calc_end_date"],
                            time2 - time1, time3 - time2, time4 - time3, time5 - time4, end_time - time5))

                else: # 没有XDB数据又不是纯T-1 Factor，说明一定有日频数据，不要需要算完

                    time1 = dt.datetime.now()
                    factor_h5_database = DailyDataManager.get_database_T_N_without_xdb(task, factor_class, preload_database, mode)
                    time2 = dt.datetime.now()

                    # precalculate
                    if factor_class.need_pre_calculate_T_N:
                        factor_h5_database = factor_instance.pre_calculate_T_N_data(factor_h5_database)

                        time3 = dt.datetime.now()

                        # 实盘准备和最新数据计算只能使用这种方式，因为取不到最新一天数据
                        factor_h5_database["pre_T_N"] = FactorUtil.fun_append_next_tradingday(
                            factor_h5_database["pre_T_N"])
                        result_df = pd.DataFrame(index=factor_h5_database["basic_file"].index)
                        for col in factor_h5_database["pre_T_N"].columns:
                                result_df[col] = factor_h5_database["pre_T_N"][col].unstack().shift(1).stack()

                        factor_h5_database["pre_T_N"] = result_df

                        if mode == RunMode.prod_prepare:
                            result[factor_class.factor_name + "_" + task["strategy"]] = {
                                "error": False,
                                "factor_name": factor_class.factor_name,
                                "factor_type": FactorUtil.FactorType.T_DAY_FACTOR,
                                "factor_value": result_df,
                                "calc_start_date": task["calc_start_date"],
                                "calc_end_date": task["calc_end_date"],
                                "calc_cost": time3 - time2
                            }

                            logger.info(
                                "子任务完成：strategy={}, factor={}, calc_start_date={}, calc_end_date={}, prep_h5_database_cost={}, pre_calc_T-N_cost={}, prepare_t_day_database_cost=n/a, prepareT_cost=n/a, calc_cost={}".format(
                                    task["strategy"], factor_class.factor_name, task["calc_start_date"],
                                    task["calc_end_date"],
                                    time2 - time1, time3 - time2, "n/a"))
                            return result

                    time3 = dt.datetime.now()
                    # prepare factor database
                    symbol_data_dict, groupby = DailyDataManager.get_database_T_Day(task, factor_class, preload_database,
                                                                                    factor_h5_database, pd.DataFrame())
                    time4 = dt.datetime.now()

                    # get sub result
                    symbol_data_dict = groupby.apply(lambda x: factor_instance.prepare_T_data(
                        symbol_data_dict.loc[task["calc_start_date"], x.name[1]]))

                    time5 = dt.datetime.now()

                    result_df = groupby.apply(lambda x: factor_instance.calculate(
                        symbol_data_dict.loc[task["calc_start_date"], x.name[1]]))

                    # result_df.fillna(factor_class.fill_na_value, inplace=True)
                    result_df = FactorUtil.fill_factor_na_values(result_df, factor_class, preload_database["basic_file"])
                    end_time = dt.datetime.now()
                    result[factor_class.factor_name + "_" + task["strategy"]] = {
                        "error": False,
                        "factor_name": factor_class.factor_name,
                        "factor_type": FactorUtil.FactorType.T_DAY_FACTOR,
                        "factor_value": result_df,
                        "calc_start_date": task["calc_start_date"],
                        "calc_end_date": task["calc_end_date"],
                        "calc_cost": end_time - time5
                    }
                    #
                    logger.info(
                        "子任务完成：strategy={}, factor={}, calc_start_date={}, calc_end_date={}, prep_h5_database_cost={}, pre_calc_T-N_cost={}, prepare_t_day_database_cost={}, prepareT_cost={}, calc_cost={}".format(
                            task["strategy"], factor_class.factor_name, task["calc_start_date"], task["calc_end_date"],
                            time2 - time1, time3 - time2, time4 - time3, time5 - time4, end_time - time5))

        except Exception as e:
            logger.error(
                "exception caught! strategy={}, factors={}, calc_date={}, error={}, trace={}".format(task["strategy"],
                                                                                                     factor_class.factor_name,
                                                                                                     task[
                                                                                                         "calc_start_date"],
                                                                                                     e.__cause__,
                                                                                                     e.__traceback__))
            result[factor_class.factor_name + "_" + task["strategy"]] = {
                "error": True,
                "factor_name": factor_class.factor_name,
                "factor_type": FactorUtil.FactorType.T_DAY_FACTOR,
                "factor_value": pd.DataFrame(),
                "calc_start_date": task["calc_start_date"],
                "calc_end_date": task["calc_end_date"],
                "calc_cost": -1
            }
        return result


# 提前加载数据
def __preload_data(task):
    database = DailyDataManager.pre_load_data_daily(task)
    return database


def __generate_preload_database(result, preload_result):
    for data_dict in preload_result:
        result.update(data_dict)
    return result


def __merge_factor_values(result, cost_result, error_factors, calc_result, mode):
    for factor_name in calc_result:
        strategy = factor_name.split("_")[-1]
        real_name = calc_result[factor_name]["factor_name"]

        if calc_result[factor_name]["error"]:

            if strategy not in error_factors:
                error_factors[strategy] = set()
            error_factors[strategy].add(real_name)
        else:
            if strategy in error_factors and calc_result[factor_name]["factor_name"] in error_factors[strategy]:
                if factor_name in result:
                    del result[factor_name]
                continue
            if factor_name in result:
                if mode == RunMode.prod_prepare:
                    logger.error("发现重复因子名！name={}".format(factor_name))
                    continue
                result[factor_name]["factor_value"] = result[factor_name]["factor_value"].append(
                        calc_result[factor_name]["factor_value"])
                cost_result[factor_name].append(calc_result[factor_name]["calc_cost"].total_seconds())
            else:
                result[factor_name] = {
                    "factor_name": calc_result[factor_name]["factor_name"],
                    "strategy": strategy,
                    "factor_value": calc_result[factor_name]["factor_value"]
                }
                cost_result[factor_name] = [calc_result[factor_name]["calc_cost"].total_seconds()]
    return result, cost_result, error_factors

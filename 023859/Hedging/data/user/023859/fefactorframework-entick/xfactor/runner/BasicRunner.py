import copy
import os
import datetime as dt
import time
import traceback
import multiprocessing as mp
from loguru import logger
import settings
import xfactor.runner.DataManager as DataManager
from xfactor.runner.BasicTaskManager import BasicTaskManager as TaskManager
import xfactor.FactorUtil as FactorUtil
from settings import RunMode
import pandas as pd
from xfactor.factor_precheck import precheck as prechecker
from xfactor.factor_test import test as tester
from xfactor.Util import view_bar

'''
用作批量计算因子，时间跨度和因子个数均不限制
每日盘中或盘后计算，只计算一天，建议使用DailyRunner（为因子存储特殊优化）
run()会返回因子计算结果

options中的calc.num_cpus不设置或者设置为1时，将不采用并行化方式运行，该状态下可用来调试
'''


def run(factor_name_list, start_date, end_date, strategy, output_dir, options=None):
    calc_num_cpus = 1
    mode = RunMode.research
    precheck = False
    report = False
    run_factor_test = False

    local_evaluator = ""
    if options is not None:
        if "calc.num_cpus" in options:
            calc_num_cpus = int(options["calc.num_cpus"])
        if "local_evaluator" in options:
            local_evaluator = options["local_evaluator"]
        if "precheck" in options:
            precheck = options["precheck"]
        if "factor_test" in options:
            run_factor_test = options["factor_test"]
        if "report" in options:
            report = options["report"]

    if strategy.lower() not in settings.valid_strategy_names:
        logger.error("运行策略名称不正确！输入策略名为={}".format(strategy))
        raise RuntimeError("Incorrect Strategy Name!")
    if local_evaluator != "" and not local_evaluator.endswith(".py"):
        logger.error("外部因子评估框架路径错误！仅支持单个py文件，需要输入以.py结尾的绝对路径。输入路径为={}".format(local_evaluator))
        raise RuntimeError("Incorrect Local_evaluator Name!")
    if not os.path.exists(output_dir):
        raise RuntimeError("Output path not exists! path={}".format(output_dir))

    result, check_result = __calc_factor(strategy, factor_name_list, start_date, end_date, mode, calc_num_cpus,
                                         precheck, run_factor_test, report, output_dir, local_evaluator)

    return result, check_result


def __calc_factor(strategy, factor_name_list, start_date, end_date, mode, calc_num_cpus, precheck, run_factor_test,
                  report, output_dir, local_evaluator):
    result = {}
    cost_result = {}
    checker_result = {}
    task_manager = TaskManager(factor_name_list, start_date, end_date, strategy)

    if precheck:
        prechecker.pre_calc_check(task_manager.get_factor_class_list())

    preload_database = {}
    # shared_preload_database = mp.Manager().dict()

    task_dict = task_manager.generate_task()
    if task_dict["data_prepare_tasks"]:
        preload_num_cpu = min(calc_num_cpus, len(task_dict["data_prepare_tasks"]))

        logger.info(
            "计算开始：当前任务种类=data_prepare, 任务数量={}, 进程数={}".format(len(task_dict["data_prepare_tasks"]), preload_num_cpu))

        if preload_num_cpu == 1:
            cnt = 0
            for task in task_dict["data_prepare_tasks"]:
                preload_database.update(__preload_data(task, cnt, len(task_dict["data_prepare_tasks"])))
                cnt += 1

            preload_database = DataManager.prepare_industry_dataframe(preload_database)

        else:
            prepare_ids = []
            pool = mp.Pool(preload_num_cpu)
            cnt = 0
            for task in task_dict["data_prepare_tasks"]:
                prepare_ids.append(
                    pool.apply_async(
                        __preload_data, (task, cnt, len(task_dict["data_prepare_tasks"]),)
                    )
                )
                cnt += 1
            pool.close()
            pool.join()
            prepare_results = [prepare_id.get() for prepare_id in prepare_ids]
            pool.terminate()
            preload_database = __generate_preload_database(preload_database, prepare_results)
            preload_database = DataManager.prepare_industry_dataframe(preload_database)

    logger.info(
        "计算开始：当前任务种类=factor_calculate, 任务数量={}, 进程数={}".format(len(task_dict["calc_tasks"]), calc_num_cpus))
    if calc_num_cpus == 1:
        task_results = []
        cnt = 0
        for task in task_dict["calc_tasks"]:
            task_results.append(__execute_task(task, preload_database, mode, cnt, len(task_dict["calc_tasks"])))
            cnt += 1

    else:
        task_ids = []
        cnt = 0
        pool = mp.Pool(min(calc_num_cpus, len(task_dict["calc_tasks"])))
        for task in task_dict["calc_tasks"]:
            task_ids.append(pool.apply_async(__execute_task, (
                task, preload_database, mode, cnt, len(task_dict["calc_tasks"]),
            )))
            cnt += 1
        pool.close()
        pool.join()
        task_results = [task_id.get() for task_id in task_ids]
        pool.terminate()

    error_factors = {}

    for sub_result in task_results:
        result, cost_result, error_factors = __merge_factor_values(result, cost_result, error_factors, sub_result)
    logger.info("全部计算完成")

    saved_factor_dirs = __save_factors(result, output_dir, start_date, end_date)
    if error_factors:
        strategies = strategy.split("/")
        for stra in strategies:
            for factor_name in error_factors[stra]:
                logger.error("FactorCalculateError! factor_name={}, strategy={}, skip.".format(factor_name, stra))

    factor_class_map = {}
    for factor_class in task_manager.factor_class_list:
        factor_class_map[factor_class.factor_name] = factor_class

    if precheck:
        __pre_check(strategy, start_date, end_date, task_manager.factor_class_list, error_factors, result, output_dir,
                    calc_num_cpus)

    if run_factor_test:
        checker_result = __factor_check(strategy, start_date, end_date, saved_factor_dirs, factor_class_map,
                                        cost_result, output_dir, calc_num_cpus, report, local_evaluator)
    return result, checker_result


def __save_factors(result, output_dir, start_date, end_date):
    saved_factor_dirs = []
    for name, data_dict in result.items():
        strategy = name.split("_")[-1]
        factor_name = data_dict["factor_name"]
        factor_path = os.path.join(output_dir, "factor_value", strategy)
        saved_factor_dirs.append({
            'strategy': strategy,
            'name': factor_name,
            'path': factor_path + "/" + factor_name + ".h5"
        })

        if not os.path.exists(factor_path):
            os.system("mkdir -p " + factor_path)
        data_dict["factor_value"].to_hdf(factor_path + "/" + factor_name + ".h5", "data")

        if start_date != settings.precheck_path_dict[strategy]["long_interval"][0] or end_date != \
                settings.precheck_path_dict[strategy]["long_interval"][1]:
            continue

        if data_dict["factor_type"] == FactorUtil.FactorType.T_1_FACTOR:
            if not "factor_value_full" in data_dict or data_dict["factor_value_full"].empty:
                logger.error("T-1 Factor 因子值字典内不存在未筛选的因子值！factor_name={}".format(factor_name))
                continue

            same_test_dir = output_dir + '/precheck/' + strategy + '/same_test/'
            if not os.path.exists(same_test_dir):
                os.system("mkdir -p " + same_test_dir)

            same_test_factor_path = same_test_dir + "/" + data_dict["factor_name"] + "_{}_{}.pkl".format(
                start_date, end_date)
            data_dict["factor_value_full"].to_pickle(same_test_factor_path)

    logger.info("factor value saved!")
    return saved_factor_dirs


def __preload_data(task, idx, total):
    data = DataManager.pre_load_data(task)

    view_bar(idx, total, "prepare")
    return data

def __factor_check(strategy, start_date, end_date, saved_factor_dirs, factor_class_map, cost_result, output_dir,
                   calc_num_cpus, report, local_evaluator_path):
    checker_result = {}
    test_output_dir = output_dir + "/factor_test/"
    if not os.path.exists(test_output_dir):
        os.system("mkdir -p " + test_output_dir)

    if calc_num_cpus == 1:
        for path_dict in saved_factor_dirs:
            factor_df0 = pd.read_hdf(path_dict["path"])
            cost_list = cost_result[path_dict["name"] + "_" + path_dict["strategy"]]["cost"]

            checker = tester.get_tester(strategy, factor_class_map[path_dict["name"]], start_date, end_date,
                                        local_evaluator_path)

            checker_result[path_dict["name"] + "_" + path_dict["strategy"]] = checker.factor_test(factor_df0, cost_list,
                                                                                                  test_output_dir, True,
                                                                                                  report)
    else:
        task_ids = {}
        pool = mp.Pool(min(calc_num_cpus, len(saved_factor_dirs)))
        for path_dict in saved_factor_dirs:
            checker = tester.get_tester(strategy, factor_class_map[path_dict["name"]], start_date, end_date,
                                        local_evaluator_path)

            factor_df0 = pd.read_hdf(path_dict["path"])
            cost_list = cost_result[path_dict["name"] + "_" + path_dict["strategy"]]["cost"]

            task_ids[path_dict["name"] + "_" + path_dict["strategy"]] = pool.apply_async(checker.factor_test, (
                factor_df0, cost_list, test_output_dir, True, report,
            ))
        pool.close()
        pool.join()

        for k, v in task_ids.items():
            checker_result[k] = v.get()
        pool.terminate()
    logger.info("Factor test finished!")
    return checker_result


def __pre_check(strategy, start_date, end_date, factor_class_list, error_factors, result, output_dir, calc_num_cpus):
    strategies = strategy.split("/")
    factor_groups = FactorUtil.split_calc_factor_into_group(strategy, factor_class_list)

    if calc_num_cpus == 1:

        for k, v in factor_groups.items():
            if k == "t_day_factor":
                factor_type = FactorUtil.FactorType.T_DAY_FACTOR
            elif k == "pure_t_1_factor":
                factor_type = FactorUtil.FactorType.T_1_FACTOR
            elif k == 'combined_t_1_factor':
                factor_type = FactorUtil.FactorType.COMBINED_FACTOR
            else:
                continue

            for kls in factor_groups[k]:
                factor_name = kls.factor_name
                for stra in strategies:
                    name = factor_name + "_" + stra
                    start_date_new = str(start_date)
                    if (FactorUtil.check_tday_tick1s_full(kls)) & (start_date_new < "20170101"):
                        start_date_new = "20170101"
                    if (FactorUtil.check_xdb_tick_1s_full(kls)) & (start_date_new < "20170110"):
                        start_date_new = "20170110"

                    res = result[name]["factor_value"] if name in result else pd.DataFrame()
                    prechecker.run_precheck(stra, error_factors, kls, start_date_new, end_date, res, factor_type,
                                            output_dir)

    else:
        task_ids = []
        pool = mp.Pool(calc_num_cpus)
        for k, v in factor_groups.items():
            if k == "t_day_factor":
                factor_type = FactorUtil.FactorType.T_DAY_FACTOR
            elif k == "pure_t_1_factor":
                factor_type = FactorUtil.FactorType.T_1_FACTOR
            elif k == 'combined_t_1_factor':
                factor_type = FactorUtil.FactorType.COMBINED_FACTOR
            else:
                continue

            for kls in factor_groups[k]:
                factor_name = kls.factor_name
                for stra in strategies:
                    name = factor_name + "_" + stra
                    start_date_new = str(start_date)
                    if (FactorUtil.check_tday_tick1s_full(kls)) & (start_date_new < "20170101"):
                        start_date_new = "20170101"
                    if (FactorUtil.check_xdb_tick_1s_full(kls)) & (start_date_new < "20170110"):
                        start_date_new = "20170110"
                    res = result[name]["factor_value"] if name in result else pd.DataFrame()
                    task_ids.append(pool.apply_async(prechecker.run_precheck, (
                        stra, error_factors, kls, start_date_new, end_date, res, factor_type, output_dir,
                    )))
        pool.close()
        pool.join()
        pool.terminate()

    return


# 运行指定task
def __execute_task(task, preload_database, mode, idx, tot):
    result = {}
    database = DataManager.__load_data(task, preload_database, mode)

    if task["factor_type"] == FactorUtil.FactorType.T_1_FACTOR:
        try:
            factor_class = task["factor_class_list"][0]
            factor_instance = FactorUtil.create_factor_instance(factor_class)
            time1 = dt.datetime.now()
            factor_database = DataManager.get_database_T_N_without_xdb(task, factor_class, database)
            factor_database["skip"] = False  # 纯T-1_FACTOR因子默认h5文件不会为空，置为False

            time2 = dt.datetime.now()
            # precalculate
            if factor_class.need_pre_calculate_T_N:
                factor_database = factor_instance.pre_calculate_T_N_data(factor_database)

            # get result and filter and shift
            time3 = dt.datetime.now()
            val_df = factor_instance.calculate(factor_database)
            time4 = dt.datetime.now()
            val_df = FactorUtil.fun_append_next_tradingday(val_df)

            # 入库时不进行basicfile的区分
            result_df_full = pd.DataFrame()
            result_df = pd.DataFrame(index=database["basic_file"].index)
            vals = val_df[val_df.columns[0]].unstack().shift(1).stack()

            result_df[val_df.columns[0]] = vals
            result_df_full[val_df.columns[0]] = vals

            result_df.fillna(factor_class.fill_na_value, inplace=True)
            result[factor_class.factor_name + "_" + task["strategy"]] = {
                "error": False,
                "factor_name": factor_class.factor_name,
                "factor_type": FactorUtil.FactorType.T_1_FACTOR,
                "factor_value": result_df,
                "factor_value_full": result_df_full,
                "calc_date": "",
                "calc_cost": time4 - time3
            }
            # logger.info(
            #     "子任务完成：strategy={}, factor={}, calc_start_date={}, calc_end_date={}, prep_h5_database_cost={}, pre_calc_T-N_cost={}, prepare_t_day_database_cost=n/a, prepareT_cost=n/a, calc_cost={}".format(
            #         task["strategy"], factor_class.factor_name, task["calc_start_date"], task["calc_end_date"],
            #         time2 - time1, time3 - time2, time4 - time3))

        except Exception as e:
            logger.error(
                "exception caught! strategy={}, factors={}, calc_start_date={},calc_end_date={}, error={}, trace={}".format(
                    task["strategy"], factor_class.factor_name, task["calc_start_date"], task["calc_end_date"],
                    e.__cause__, traceback.print_exc()))
            result[factor_class.factor_name + "_" + task["strategy"]] = {
                "error": True,
                "factor_name": factor_class.factor_name,
                "factor_type": FactorUtil.FactorType.T_1_FACTOR,
                "factor_value": pd.DataFrame(),
                "factor_value_full": pd.DataFrame(),
                "calc_date": "",
                "calc_cost": -1
            }
        view_bar(idx, tot, task["calc_start_date"])

        return result

    else:
        for factor_class in task["factor_class_list"]:
            try:

                if "TOrder" in factor_class.t_day_data and task["strategy"] == 'jupiter':
                    continue

                if (FactorUtil.check_xdb_tick_1s_full(factor_class)) and (task["calc_start_date"] < "20170110"):
                    continue
                if (FactorUtil.check_tday_tick1s_full(factor_class)) and (task["calc_start_date"] < "20170101"):
                    continue
                factor_instance = FactorUtil.create_factor_instance(factor_class)

                if factor_class.xdb_data:
                    pre_T_N_dict = {}
                    time1 = dt.datetime.now()
                    symbol_data_dict, groupby = DataManager.get_database_T_N_with_xdb(task, factor_class, database)
                    time2 = dt.datetime.now()

                    # precalculate
                    if factor_class.need_pre_calculate_T_N:
                        symbol_data_dict = groupby.apply(lambda x: factor_instance.pre_calculate_T_N_data(
                            symbol_data_dict.loc[task["calc_start_date"], x.name[1]]))
                        prepare_df = groupby.apply(
                            lambda x: DataManager.filter_and_check_pre_T_N(factor_class.factor_name,
                                                                           symbol_data_dict.loc[
                                                                               task["calc_start_date"], x.name[1]],
                                                                           x.name[1]))
                        # prepare_df = FactorUtil.fun_append_next_tradingday(prepare_df)
                        # result_df = pd.DataFrame(index=database["basic_file"].index)
                        # for col in prepare_df.columns:
                        #     result_df[col] = prepare_df[col].unstack().shift(1).stack()

                        pre_T_N_dict["pre_T_N"] = prepare_df

                    time3 = dt.datetime.now()

                    # prepare factor database
                    symbol_data_dict, groupby = DataManager.get_database_T_Day(task, factor_class, database,
                                                                               pre_T_N_dict, symbol_data_dict)

                else:
                    # get factor database
                    time1 = dt.datetime.now()
                    factor_h5_database = DataManager.get_database_T_N_without_xdb(task, factor_class, database)
                    time2 = dt.datetime.now()

                    # precalculate
                    if factor_class.need_pre_calculate_T_N:
                        # precalculate t-1 factor 也是dt,Ticker, 所有提前准备的数据都存放到 "pre_T_N"里
                        factor_h5_database = factor_instance.pre_calculate_T_N_data(factor_h5_database)

                        factor_h5_database["pre_T_N"] = FactorUtil.fun_append_next_tradingday(
                            factor_h5_database["pre_T_N"])
                        result_df = pd.DataFrame(index=factor_h5_database["basic_file"].index)

                        for col in factor_h5_database["pre_T_N"].columns:
                            result_df[col] = factor_h5_database["pre_T_N"][col].unstack().shift(1).stack()

                        factor_h5_database["pre_T_N"] = result_df

                    time3 = dt.datetime.now()
                    # prepare factor database
                    symbol_data_dict, groupby = DataManager.get_database_T_Day(task, factor_class, database,
                                                                               factor_h5_database, pd.DataFrame())

                time4 = dt.datetime.now()

                symbol_data_dict = groupby.apply(lambda x: factor_instance.prepare_T_data(
                    symbol_data_dict.loc[task["calc_start_date"], x.name[1]]))

                time5 = dt.datetime.now()

                # get sub result
                result_df = groupby.apply(lambda x: factor_instance.calculate(
                    symbol_data_dict.loc[task["calc_start_date"], x.name[1]]))

                result_df.fillna(factor_class.fill_na_value, inplace=True)
                end_time = dt.datetime.now()
                result[factor_class.factor_name + "_" + task["strategy"]] = {
                    "error": False,
                    "factor_name": factor_class.factor_name,
                    "factor_type": FactorUtil.FactorType.T_DAY_FACTOR,
                    "factor_value": result_df,
                    "factor_value_full": pd.DataFrame(),
                    "calc_date": task["calc_start_date"],
                    "calc_cost": end_time - time5
                }

                # logger.info(
                #     "子任务完成：strategy={}, factor={}, calc_start_date={}, calc_end_date={}, prep_h5_database_cost={}, pre_calc_T-N_cost={}, prepare_t_day_database_cost={}, prepareT_cost={}, calc_cost={}".format(
                #         task["strategy"], factor_class.factor_name, task["calc_start_date"], task["calc_end_date"],
                #         time2 - time1, time3 - time2, time4 - time3, time5 - time4, end_time - time5))
            except Exception as e:
                logger.error("exception caught! strategy={}, factor={}, calc_date={}, error={}, trace={}".format(
                    task["strategy"],
                    factor_class.factor_name, task["calc_start_date"], e.__cause__, traceback.print_exc()))
                result[factor_class.factor_name + "_" + task["strategy"]] = {
                    "error": True,
                    "factor_name": factor_class.factor_name,
                    "factor_type": FactorUtil.FactorType.T_DAY_FACTOR,
                    "factor_value": pd.DataFrame(),
                    "factor_value_full": pd.DataFrame(),
                    "calc_date": task["calc_start_date"],
                    "calc_cost": -1
                }
        # logger.info(
        #     "子任务完成：strategy={}, factors={}, calc_start_date={}, calc_end_date={}".format(
        #         task["strategy"],
        #         list(result.keys()), task["calc_start_date"], task["calc_end_date"]))

        view_bar(idx, tot, task["calc_start_date"])

        return result


# 提前加载数据
def __preload_data_single(task):
    database = DataManager.pre_load_data(task)
    return database


def __generate_preload_database(result, preload_result):
    for data_dict in preload_result:
        result.update(data_dict)
    return result


def __merge_factor_values(result, cost_result, error_factors, calc_result):
    for factor_name in calc_result:
        real_name = calc_result[factor_name]["factor_name"]
        strategy = factor_name.split("_")[-1]
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
                result[factor_name]["factor_value"] = result[factor_name]["factor_value"].append(
                    calc_result[factor_name]["factor_value"])
                cost_result[factor_name]["cost"].append(calc_result[factor_name]["calc_cost"].total_seconds())
                cost_result[factor_name]["calc_date"].append(calc_result[factor_name]["calc_date"])

            else:
                result[factor_name] = {
                    "factor_name": calc_result[factor_name]["factor_name"],
                    "factor_type": calc_result[factor_name]["factor_type"],
                    "factor_value": calc_result[factor_name]["factor_value"]
                }
                # 如果是入库，还需要单独把未经过筛选的全市场因子值拿出来
                if "factor_value_full" in calc_result[factor_name]:
                    result[factor_name]["factor_value_full"] = calc_result[factor_name]["factor_value_full"]

                cost_result[factor_name] = {
                    "factor_name": calc_result[factor_name]["factor_name"],
                    "factor_type": calc_result[factor_name]["factor_type"],
                    "calc_date": [calc_result[factor_name]["calc_date"]],
                    "cost": [calc_result[factor_name]["calc_cost"].total_seconds()]
                }
    return result, cost_result, error_factors

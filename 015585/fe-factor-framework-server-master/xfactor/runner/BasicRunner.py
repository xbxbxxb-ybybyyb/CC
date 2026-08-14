import copy
import os
import datetime as dt
import traceback
from multiprocessing import Pool, Manager
from loguru import logger
from h5data.IO import IO
import settings
import xfactor.runner.BasicDataManager as DataManager
from xfactor.runner.BasicTaskManager import BasicTaskManager as TaskManager
import xfactor.FactorUtil as FactorUtil
from settings import RunMode
import pandas as pd
from xfactor.factor_precheck import precheck as prechecker
from xfactor.factor_test import test as tester
from xfactor.factor_warehouse.europa_warehouse import europa_warehouse
from xfactor.factor_warehouse.sell_warehouse import sell_warehouse
from xfactor.factor_warehouse.saturn_warehouse import saturn_warehouse
from xfactor.factor_warehouse.metis_warehouse import metis_warehouse
from xfactor.factor_warehouse.mimas_warehouse import mimas_warehouse
from xfactor.factor_warehouse.neptune_warehouse import neptune_warehouse
from xfactor.factor_warehouse.neptunelong_warehouse import neptunelong_warehouse

from xfactor.Util import view_bar
'''
用作因子入库

options中的calc.num_cpus不设置或者设置为1时，将不采用并行化方式运行，该状态下可用来调试
'''


def run(factor_name_list, start_date, end_date, strategy, upload_date, mode, options=None):
    calc_num_cpus = 1
    precheck = False
    report = False
    run_factor_test = False
    override = False
    warehouse = False

    if not factor_name_list:
        logger.error("传入因子列表为空！")
        raise RuntimeError("传入因子列表为空！")

    base_path = os.getcwd()
    for factor_dict in factor_name_list:
        factor_path = os.path.join(base_path, factor_dict["module_path"]) + "/" + factor_dict["factor_name"] + ".py"

        if not os.path.exists(factor_path):
            logger.error("无法访问因子文件! path=" + factor_path)
            raise RuntimeError("无法访问因子文件! path=" + factor_path)

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
        if "override" in options:
            override = options["override"]
        if "warehouse" in options:
            warehouse = options["warehouse"]

    if mode == RunMode.research:
        if "factor_value_path" not in options or "factor_cost_path" not in options or "factor_precheck_path" not in options or "factor_test_path" not in options:
            logger.error("Option中路径参数不完整！需求参数：factor_value_path, factor_cost_path, factor_precheck_path, factor_test_path")
            raise RuntimeError("path param missing!")
        if not os.path.exists(options["factor_value_path"]):
            logger.error("无法访问factor_value_path! path=" + options["factor_value_path"])
            raise RuntimeError("无法访问factor_value_path!")
        if not os.path.exists(options["factor_cost_path"]):
            logger.error("无法访问factor_cost_path! path=" + options["factor_cost_path"])
            raise RuntimeError("无法访问factor_cost_path!")
        if not os.path.exists(options["factor_precheck_path"]):
            logger.error("无法访问factor_precheck_path! path=" + options["factor_precheck_path"])
            raise RuntimeError("无法访问factor_precheck_path!")
        if not os.path.exists(options["factor_test_path"]):
            logger.error("无法访问factor_test_path! path=" + options["factor_test_path"])
            raise RuntimeError("无法访问factor_test_path!")


    if strategy.lower() not in settings.valid_strategy_names:
        logger.error("运行策略名称不正确！输入策略名为={}".format(strategy))
        raise RuntimeError("Incorrect Strategy Name!")
    if local_evaluator != "" and not local_evaluator.endswith(".py"):
        logger.error("外部因子评估框架路径错误！仅支持单个py文件，需要输入以.py结尾的绝对路径。输入路径为={}".format(local_evaluator))
        raise RuntimeError("Incorrect Local_evaluator Name!")


    __check_paths(strategy, warehouse)
    __calc_factor(strategy, factor_name_list, start_date, end_date, upload_date, options, mode, calc_num_cpus,
                                           precheck, run_factor_test, report, local_evaluator, override, warehouse)

    return


def __check_paths(strategy, warehouse):
    path_dict_items = ["factor_value_path", "factor_precheck_path", "factor_test_path"]
    warehouse_items = ["res_path", "res_public_path"]
    for i in path_dict_items:
        if not os.path.exists(settings.path_dict[strategy][i]):
            logger.error("path not exists! path_name={}, path={}".format(i, settings.path_dict[strategy][i]))
            raise RuntimeError("path not exists! path_name={}, path={}".format(i, settings.path_dict[strategy][i]))

    if warehouse:
        if strategy != "jupiter":
            for i in warehouse_items:
                if not os.path.exists(settings.warehouse_settings_dict[strategy][i]):
                    logger.error("path not exists! path_name={}, path={}".format(i, settings.path_dict[strategy][i]))
                    raise RuntimeError("path not exists! path_name={}, path={}".format(i, settings.path_dict[strategy][i]))


#  根据因子输出路径筛选出已经计算过的因子
#  @return
#   res: 未计算过的因子
#   res_dir: 存储位置（根路径）
def __filter_factors(strategy, factor_kls_list, start_date, end_date, factor_value_path, factor_cost_path, factor_precheck_path):
    res = []
    for factor_dict in factor_kls_list:
        factor = factor_dict["factor_class"]
        xdb_tick_1s_full = FactorUtil.check_xdb_tick_1s_full(factor)
        xdb_tday_tick_1s_full = FactorUtil.check_tday_tick1s_full(factor)

        start_date_new = start_date
        if xdb_tday_tick_1s_full and str(start_date) < "20170101":
            start_date_new = "20170101"
        if xdb_tick_1s_full and str(start_date) < "20170110":
            start_date_new = "20170110"

        val_path = os.path.join(factor_value_path, factor.factor_name, factor.factor_name + ".h5")
        cost_path = os.path.join(factor_cost_path, factor.factor_name, factor.factor_name + "_{}_{}.pkl".format(start_date_new, end_date))  # TODos
        full_val_path = os.path.join(factor_precheck_path, "same_test", factor.factor_name + "_{}_{}.pkl".format(
            start_date_new, end_date))

        if not factor.t_day_data and not factor.xdb_data and not factor.other_t_day_data and factor.t_1_factor_data and not os.path.exists(full_val_path):
            res.append(factor_dict)
            continue
        if not os.path.exists(val_path) or not os.path.exists(cost_path):
            res.append(factor_dict)
        else:
            logger.info(
                "factor={}, strategy={}: factor value files exists at {}! Skip for calculating".format(factor, strategy,
                                                                                                       val_path))
    return res


def __calc_factor(strategy, factor_name_list, start_date, end_date, upload_date, options, mode, calc_num_cpus, precheck, run_factor_test,
                  report, local_evaluator, override, warehouse):
    result = {}
    cost_result = {}
    error_factors = {}

    task_manager = TaskManager(factor_name_list, start_date, end_date, strategy)
    kls_list = task_manager.get_full_class_list()

    factor_class_map = {}
    for factor_dict in kls_list:
        factor_class_map[factor_dict["factor_class"].factor_name] = factor_dict["factor_class"]

    if not override:
        factor_value_path = settings.path_dict[strategy]["factor_value_path"] if mode == RunMode.factor_warehouse else \
        options["factor_value_path"]
        factor_cost_path = settings.path_dict[strategy]["factor_cost_path"] if mode == RunMode.factor_warehouse else \
        options["factor_cost_path"]
        factor_precheck_path = settings.path_dict[strategy]["factor_precheck_path"] if mode == RunMode.factor_warehouse else \
        options["factor_precheck_path"]

        kls_list = __filter_factors(strategy, kls_list, start_date, end_date, factor_value_path, factor_cost_path, factor_precheck_path)

    pre_calc_check_res = {}
    if precheck:
        prev_factor_list = __get_all_factor_names(strategy, upload_date)
        pre_calc_check_res = prechecker.pre_calc_check(task_manager.get_full_class_list(), prev_factor_list)

    preload_database = {}
    # all_prepare_tasks = task_manager.generate_task(task_manager.get_full_class_list())
    task_dict = task_manager.generate_task(kls_list)

    if task_dict["data_prepare_tasks"]:
        preload_num_cpu = min(calc_num_cpus, len(task_dict["data_prepare_tasks"]))

        logger.info(
            "计算开始：当前任务种类=data_prepare, 任务数量={}, 进程数={}".format(len(task_dict["data_prepare_tasks"]), preload_num_cpu))

        if preload_num_cpu == 1:
            cnt = 0
            for task in task_dict["data_prepare_tasks"]:
                preload_database.update(__preload_data(task, cnt, len(task_dict["data_prepare_tasks"])))
                cnt +=1
            preload_database = DataManager.prepare_industry_dataframe(preload_database)

        else:

            prepare_ids = []
            pool = Pool(preload_num_cpu)
            cnt = 0
            for task in task_dict["data_prepare_tasks"]:
                prepare_ids.append(pool.apply_async(__preload_data, (task, cnt, len(task_dict["data_prepare_tasks"]), )))
                cnt += 1
            pool.close()
            pool.join()
            prepare_results = [prepare_id.get() for prepare_id in prepare_ids]
            pool.terminate()
            preload_database = __generate_preload_database(preload_database, prepare_results)
            preload_database = DataManager.prepare_industry_dataframe(preload_database)

    if task_dict["calc_tasks"]:
        logger.info(
            "计算开始：当前任务种类=factor_calculate, 任务数量={}, 进程数={}".format(len(task_dict["calc_tasks"]), calc_num_cpus))
        if calc_num_cpus == 1:
            cnt = 0
            task_results = []
            for task in task_dict["calc_tasks"]:
                task_results.append(__execute_task(task, preload_database, mode, cnt, len(task_dict["calc_tasks"])))
                cnt += 1

        else:
            task_ids = []
            pool = Pool(min(calc_num_cpus, len(task_dict["calc_tasks"])))
            cnt = 0
            for task in task_dict["calc_tasks"]:
                task_ids.append(pool.apply_async(__execute_task, (
                    task, preload_database, mode, cnt, len(task_dict["calc_tasks"]),
                )))
                cnt += 1
            pool.close()
            pool.join()
            task_results = [task_id.get() for task_id in task_ids]
            pool.terminate()



        for sub_result in task_results:
            result, cost_result, error_factors = __merge_factor_values(result, cost_result, error_factors, factor_class_map, sub_result)
        logger.info("全部计算完成")

        if error_factors:
            for stra in error_factors:
                for factor_name in error_factors[stra]:
                    logger.error("FactorCalculateError! factor_name={}, strategy={}, skip.".format(factor_name, stra))

        if mode == RunMode.factor_warehouse:
            __save_factor_value(result, settings.path_dict[strategy]["factor_value_path"], start_date, end_date, mode)
        else:
            __save_factor_value(result, options["factor_value_path"], start_date, end_date, mode)

        if mode == RunMode.factor_warehouse:
            __save_factor_cost(cost_result, start_date, end_date, settings.path_dict[strategy]["factor_cost_path"])
        else:
            __save_factor_cost(cost_result, start_date, end_date, options["factor_cost_path"])


    if precheck:
        if not pre_calc_check_res:
            logger.error("pre_calc_check结果为空！")
            raise RuntimeError("pre_calc_check结果为空！")
        precheck_path = settings.path_dict[strategy]["factor_precheck_path"] if mode == RunMode.factor_warehouse else options["factor_precheck_path"]
        __pre_check(strategy, start_date, end_date, task_manager.full_class_list, error_factors, precheck_path
                    , calc_num_cpus, pre_calc_check_res, preload_database)

    if run_factor_test:
        factor_value_path = settings.path_dict[strategy]["factor_value_path"] if mode == RunMode.factor_warehouse else options["factor_value_path"]
        factor_cost_path = settings.path_dict[strategy]["factor_cost_path"] if mode == RunMode.factor_warehouse else options["factor_cost_path"]
        factor_test_path = settings.path_dict[strategy]["factor_test_path"] if mode == RunMode.factor_warehouse else options["factor_test_path"]
        # in interval check
        if mode == RunMode.factor_warehouse:
            in_interval = settings.warehouse_settings_dict[strategy]['in_interval']
            out_interval = settings.warehouse_settings_dict[strategy]['out_interval']
            checker_result_in = __factor_check(strategy, in_interval[0], in_interval[1], start_date, end_date,
                                               task_manager.full_class_list,factor_value_path,factor_cost_path, factor_test_path, calc_num_cpus, report, local_evaluator)
            checker_result_out = __factor_check(strategy, out_interval[0], out_interval[1], start_date, end_date,
                                                task_manager.full_class_list,factor_value_path,factor_cost_path, factor_test_path, calc_num_cpus, report, local_evaluator)
        else:
            checker_result_in = __factor_check(strategy, start_date, end_date, start_date, end_date,
                                               task_manager.full_class_list, factor_value_path, factor_cost_path,
                                               factor_test_path, calc_num_cpus, report, local_evaluator)

    if warehouse:
        __warehouse(strategy)

    return


def __save_factor_value(result, output_dir, start_date, end_date, mode):
    for name, data_dict in result.items():
        strategy = name.split("_")[-1]
        factor_name = data_dict["factor_name"]
        all_factor_dir = os.path.join(output_dir, factor_name)

        # 先存一份在/all_cost/目录下
        if not os.path.exists(all_factor_dir):
            os.system("mkdir -p " + all_factor_dir)

        all_factor_factor_path = all_factor_dir + "/" + data_dict["factor_name"] + ".h5"

        if os.path.exists(all_factor_factor_path):
            IO.pd_hdf5_writer(data_dict["factor_value"], all_factor_factor_path, dataset=factor_name, append=True)
        else:
            IO.pd_hdf5_writer(data_dict["factor_value"], all_factor_factor_path, dataset=factor_name)

        # 对于需要调用precheck的入库模式，需要把未经过筛选的也存一份
        if mode == RunMode.factor_warehouse and data_dict["factor_type"] == FactorUtil.FactorType.T_1_FACTOR:
            if str(start_date) == "20160101" and str(end_date) == "20211231":
                if not "factor_value_full" in data_dict:
                    logger.error("T-1 Factor 因子值字典内不存在未筛选的因子值！factor_name={}".format(factor_name))
                    continue

                same_test_dir = settings.path_dict[strategy]["factor_precheck_path"] + "/same_test/"
                if not os.path.exists(same_test_dir):
                    os.system("mkdir -p " + same_test_dir)

                same_test_factor_path = same_test_dir + "/" + data_dict["factor_name"] + "_{}_{}.pkl".format(
                    start_date, end_date)
                data_dict["factor_value_full"].to_pickle(same_test_factor_path)

                # full_dir = settings.path_dict[strategy]["factor_precheck_path"] + '/same_test/'
                # if not os.path.exists(full_dir):
                #     os.system("mkdir -p " + full_dir)
                # full_path = os.path.join(full_dir, factor_name + "_{}_{}.pkl".format(start_date, end_date) )
                # data_dict["factor_value_full"].to_pickle(full_path)

    logger.info("factor value saved!")

    return

def __save_factor_cost(cost_result, start_date, end_date, output_dir):

    for name, data_dict in cost_result.items():
        strategy = name.split("_")[-1]
        factor_name = data_dict["factor_name"]
        kls = data_dict["factor_class"]
        factor_path = os.path.join(output_dir, factor_name)

        if not os.path.exists(factor_path):
            os.system("mkdir -p " + factor_path)
        df = pd.Series(data_dict["cost"], index=data_dict["calc_date"])
        df.index = pd.to_datetime(df.index)
        xdb_tick_1s_full = FactorUtil.check_xdb_tick_1s_full(kls)
        xdb_tday_tick_1s_full = FactorUtil.check_tday_tick1s_full(kls)

        start_date_new = start_date
        if xdb_tday_tick_1s_full and str(start_date) < "20170101":
            start_date_new = "20170101"

        if xdb_tick_1s_full and str(start_date) < "20170110":
            start_date_new = "20170110"

        df.to_pickle(factor_path + "/" + factor_name + "_{}_{}.pkl".format(start_date_new, end_date))
    logger.info("factor cost saved!")

    return

def __get_all_factor_names(strategy, upload_date):
    if strategy == "jupiter" or strategy == 'europa':
        # jupiter europa 共用文件
        df1 = pd.read_excel(settings.warehouse_settings_dict["europa"]["all_factors_list"], sheet_name="right_factor")
        df2 = pd.read_excel(settings.warehouse_settings_dict["europa"]["all_factors_list"], sheet_name="left_factor")
        df3 = pd.read_excel(settings.warehouse_settings_dict["europa"]["all_factors_list"], sheet_name="emotion_factor")
        df4 = pd.read_excel(settings.warehouse_settings_dict["europa"]["all_factors_list"], sheet_name="t_emotion_factor")
        df1 = df1[df1["factor_date"] < int(upload_date)]

        factor_name_list = df1['factor_name'].to_list() + df2['factor_name'].to_list() + df3['factor_name'].to_list() + df4['factor_name'].to_list()
    else:
        df = pd.read_excel(settings.warehouse_settings_dict[strategy]["all_factors_list"])
        if strategy == 'metis':
            df = df[df["factor_date"] < int(upload_date)]
        else:
            df = df[df["提交时间"] < int(upload_date)]
        factor_name_list = df['factor_name'].to_list()

    return factor_name_list

def __factor_check(strategy, check_start_date, check_end_date, calc_start_date, calc_end_date, factor_name_list,
                   factor_value_path,factor_cost_path, output_dir, calc_num_cpus, report, local_evaluator_path):

    checker_result = {}
    skip_factors = []
    if calc_num_cpus == 1:
        logger.info("计算开始：当前任务种类=factor_test, 任务数量={}, 进程数={}".format(len(factor_name_list), 1))
        for factor_dict in factor_name_list:
            factor_kls = factor_dict['factor_class']
            factor_val_path = os.path.join(factor_value_path, factor_kls.factor_name,
                                           factor_kls.factor_name + ".h5")
            if not os.path.exists(factor_val_path):
                logger.error(
                    "Factor value file not exists! Skip factor test! strategy={}, factor={}, expected_value_path={}".format(
                        strategy, factor_kls.factor_name, factor_val_path))
                skip_factors.append(factor_kls.factor_name)
                continue

            xdb_tick_1s_full = FactorUtil.check_xdb_tick_1s_full(factor_kls)
            xdb_tick_1s_full_tday = FactorUtil.check_tday_tick1s_full(factor_kls)

            check_start_date_new = str(check_start_date)
            if xdb_tick_1s_full_tday and check_start_date_new < "20170101":
                check_start_date_new = "20170101"
            if xdb_tick_1s_full and check_start_date_new < "20170110":
                check_start_date_new = "20170110"

            factor_df0 = pd.read_hdf(factor_val_path).loc[pd.to_datetime(str(check_start_date_new)):pd.to_datetime(str(check_end_date))]

            checker = tester.get_tester(strategy, factor_kls, check_start_date_new, check_end_date,
                                        local_evaluator_path)

            calc_start_date_new = str(calc_start_date)
            if xdb_tick_1s_full_tday and calc_start_date_new < "20170101":
                calc_start_date_new = "20170101"
            if xdb_tick_1s_full and calc_start_date_new < "20170110":
                calc_start_date_new = "20170110"

            cost_path = os.path.join(factor_cost_path, factor_kls.factor_name,
                                     factor_kls.factor_name + "_{}_{}.pkl".format(calc_start_date_new, calc_end_date))
            if not os.path.exists(cost_path):
                logger.error(
                    "Factor cost file not exists! Skip factor test! strategy={}, factor={}, expected_cost_path={}".format(
                        strategy, factor_kls.factor_name, cost_path))
                skip_factors.append(factor_kls.factor_name)
                continue
            cost_list = list(pd.read_pickle(cost_path).loc[pd.to_datetime(str(check_start_date_new)):pd.to_datetime(str(check_end_date))])

            res_path = output_dir + "/{}_{}/".format(check_start_date_new, check_end_date)
            if not os.path.exists(res_path):
                os.makedirs(res_path)
            checker.factor_test(factor_df0, cost_list,
                                             result_path=res_path,
                                             factor_corr_test=True, generate_pdf=report)
            checker_result[factor_kls.factor_name + "_" + strategy] = checker.result_dic
    else:
        task_ids = {}
        numcpu = min(calc_num_cpus, len(factor_name_list))
        pool = Pool(numcpu)
        logger.info("计算开始：当前任务种类=factor_test, 任务数量={}, 进程数={}".format(len(factor_name_list), numcpu))
        for factor_dict in factor_name_list:
            factor_kls = factor_dict['factor_class']
            xdb_tick_1s_full = FactorUtil.check_xdb_tick_1s_full(factor_kls)
            xdb_tick_1s_full_tday = FactorUtil.check_tday_tick1s_full(factor_kls)
            check_start_date_new = str(check_start_date)
            if xdb_tick_1s_full_tday and check_start_date_new < "20170101":
                check_start_date_new = "20170101"
            if xdb_tick_1s_full and check_start_date_new < "20170110":
                check_start_date_new = "20170110"

            checker = tester.get_tester(strategy, factor_kls, check_start_date_new, check_end_date,
                                        local_evaluator_path)
            calc_start_date_new = str(calc_start_date)
            if xdb_tick_1s_full_tday and calc_start_date_new < "20170101":
                calc_start_date_new = "20170101"
            if xdb_tick_1s_full and calc_start_date_new < "20170110":
                calc_start_date_new = "20170110"
            factor_val_path = os.path.join(factor_value_path, factor_kls.factor_name,
                                           factor_kls.factor_name + ".h5")
            if not os.path.exists(factor_val_path):
                logger.error(
                    "Factor value file not exists! Skip factor test! strategy={}, factor={}, expected_value_path={}".format(
                        strategy, factor_kls.factor_name, factor_val_path))
                skip_factors.append(factor_kls.factor_name)
                continue
            factor_df0 = pd.read_hdf(factor_val_path).loc[pd.to_datetime(str(check_start_date_new)):pd.to_datetime(str(check_end_date))]

            cost_path = os.path.join(factor_cost_path, factor_kls.factor_name,
                                     factor_kls.factor_name + "_{}_{}.pkl".format(calc_start_date_new, calc_end_date))
            if not os.path.exists(cost_path):
                logger.error(
                    "Factor cost file not exists! Skip factor test! strategy={}, factor={}, expected_cost_path={}".format(
                        strategy, factor_kls.factor_name, cost_path))
                skip_factors.append(factor_kls.factor_name)
                continue
            cost_list = list(pd.read_pickle(cost_path).loc[pd.to_datetime(str(check_start_date_new)):pd.to_datetime(str(check_end_date))])

            res_path = output_dir + "/{}_{}/".format(check_start_date_new, check_end_date)
            if not os.path.exists(res_path):
                os.system("mkdir -p " + res_path)
            task_ids[factor_kls.factor_name + "_" + strategy] = pool.apply_async(checker.factor_test, (
                factor_df0, cost_list, res_path, True, report,
            ))
        pool.close()
        pool.join()

        for k, v in task_ids.items():
            checker_result[k] = v.get()
        pool.terminate()
    logger.info("Factor test finished!")
    return checker_result


def __pre_check(strategy, start_date, end_date, factor_class_list, error_factors, output_dir, calc_num_cpus, pre_calc_check_res, preload_database):
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
                for stra in strategies:
                    start_date_new = str(start_date)
                    if (FactorUtil.check_tday_tick1s_full(kls)) and (start_date_new < "20170101"):
                        start_date_new = "20170101"
                    if (FactorUtil.check_xdb_tick_1s_full(kls)) and (start_date_new < "20170110"):
                        start_date_new = "20170110"
                    prechecker.run_precheck(stra, pre_calc_check_res, error_factors, kls, start_date_new, end_date, factor_type, output_dir, preload_database)

    else:
        task_ids = []
        pool = Pool(calc_num_cpus)
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
                for stra in strategies:
                    start_date_new = str(start_date)
                    if (FactorUtil.check_tday_tick1s_full(kls)) and (start_date_new < "20170101"):
                        start_date_new = "20170101"
                    if (FactorUtil.check_xdb_tick_1s_full(kls)) and (start_date_new < "20170110"):
                        start_date_new = "20170110"
                    task_ids.append(pool.apply_async(prechecker.run_precheck, (
                        stra, pre_calc_check_res, error_factors, kls, start_date_new, end_date, factor_type, output_dir, preload_database,
                    )))
        pool.close()
        pool.join()
        pool.terminate()
    return


# 运行指定task
def __execute_task(task, preload_database, mode, index, tot):
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

            # 入库模式需要保留全部标的的因子值做长短区间计算
            if mode == RunMode.factor_warehouse:
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

                # result_df.fillna(factor_class.fill_na_value, inplace=True)
                result_df = FactorUtil.fill_factor_na_values(result_df, factor_class, database["basic_file"])

                result[factor_class.factor_name + "_" + task["strategy"]] = {
                    "error": False,
                    "factor_name": factor_class.factor_name,
                    "factor_type": FactorUtil.FactorType.T_1_FACTOR,
                    "factor_value": result_df,
                    "factor_value_full": result_df_full,
                    "calc_start_date": task["calc_start_date"],
                    "calc_end_date": task["calc_end_date"],
                    "calc_cost": time4 - time3
                }
                # logger.info(
                #     "子任务完成：strategy={}, factor={}, calc_start_date={}, calc_end_date={}, prep_h5_database_cost={}, pre_calc_T-N_cost={}, prepare_t_day_database_cost=n/a, prepareT_cost=n/a, calc_cost={}".format(
                #         task["strategy"], factor_class.factor_name, task["calc_start_date"], task["calc_end_date"],
                #         time2 - time1, time3 - time2, time4 - time3))
                view_bar(index, tot, task["calc_start_date"])
                return result

            # 其他模式都优先进行df的操作
            else:
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
                val_df = FactorUtil.fill_factor_na_values(val_df, factor_class, database["basic_file"])

                result[factor_class.factor_name + "_" + task["strategy"]] = {
                    "error": False,
                    "factor_name": factor_class.factor_name,
                    "factor_type": FactorUtil.FactorType.T_1_FACTOR,
                    "factor_value": val_df,
                    "calc_start_date": task["calc_start_date"],
                    "calc_end_date": task["calc_end_date"],
                    "calc_cost": time4 - time3
                }
                # logger.info(
                #     "子任务完成：strategy={}, factor={}, calc_start_date={}, calc_end_date={}, prep_h5_database_cost={}, pre_calc_T-N_cost={}, prepare_t_day_database_cost=n/a, prepareT_cost=n/a, calc_cost={}".format(
                #         task["strategy"], factor_class.factor_name, task["calc_start_date"], task["calc_end_date"],
                #         time2 - time1, time3 - time2, time4 - time3))
                view_bar(index, tot, task["calc_start_date"])
                return result
        except Exception as e:
            logger.error(
                "exception caught! strategy={}, factors={}, calc_start_date={},calc_end_date={}, error={}".format(
                    task["strategy"], factor_class.factor_name, task["calc_start_date"], task["calc_end_date"],e))
            result[factor_class.factor_name + "_" + task["strategy"]] = {
                "error": True,
                "factor_name": factor_class.factor_name,
                "factor_type": FactorUtil.FactorType.T_1_FACTOR,
                "factor_value": pd.DataFrame(),
                "calc_start_date": task["calc_start_date"],
                "calc_end_date": task["calc_end_date"],
                "calc_cost": -1
            }
            view_bar(index, tot, task["calc_start_date"])
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

                if FactorUtil.check_pure_cs_factor(factor_class):
                    # get factor database
                    time1 = dt.datetime.now()
                    factor_h5_database = DataManager.get_database_with_xdb_cs(task, factor_class, database)
                    time2 = dt.datetime.now()

                    # precalculate
                    if factor_class.need_pre_calculate_T_N:
                        # precalculate t-1 factor 也是dt,Ticker, 所有提前准备的数据都存放到 "pre_T_N"里
                        factor_h5_database = factor_instance.pre_calculate_T_N_data(factor_h5_database)

                    time3 = dt.datetime.now()

                    factor_h5_database = DataManager.get_database_T_Day_pure_cs(task, factor_class, database,
                                                                                factor_h5_database)
                    factor_h5_database = factor_instance.prepare_T_data(factor_h5_database)

                    time4 = dt.datetime.now()

                    val_df = factor_instance.calculate(factor_h5_database)

                    time5 = dt.datetime.now()

                    # 入库时不进行basicfile的区分
                    result_df = pd.DataFrame(index=database["basic_file"].index)
                    for col in val_df.columns:
                        result_df[col] = val_df[col]

                    # result_df.fillna(factor_class.fill_na_value, inplace=True)
                    result_df = FactorUtil.fill_factor_na_values(result_df, factor_class, database["basic_file"])

                    result[factor_class.factor_name + "_" + task["strategy"]] = {
                        "error": False,
                        "factor_name": factor_class.factor_name,
                        "factor_type": FactorUtil.FactorType.T_DAY_FACTOR,
                        "factor_value": result_df,
                        "factor_value_full": pd.DataFrame(),
                        "calc_start_date": task["calc_start_date"],
                        "calc_end_date": task["calc_end_date"],
                        "calc_cost": time5 - time4
                    }

                else:

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
                                                                                        task["calc_start_date"], x.name[1]], x.name[1]))
                            # prepare_df = FactorUtil.fun_append_next_tradingday(prepare_df)
                            # result_df = pd.DataFrame(index=preload_database["basic_file"].index)
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
                        symbol_data_dict, groupby = DataManager.get_database_T_Day(task, factor_class, database, factor_h5_database, pd.DataFrame())

                    time4 = dt.datetime.now()

                    symbol_data_dict = groupby.apply(lambda x: factor_instance.prepare_T_data(
                        symbol_data_dict.loc[task["calc_start_date"], x.name[1]]))

                    time5 = dt.datetime.now()

                    # get sub result
                    result_df = groupby.apply(lambda x: factor_instance.calculate(
                        symbol_data_dict.loc[task["calc_start_date"], x.name[1]]))

                    # result_df.fillna(factor_class.fill_na_value, inplace=True)
                    result_df = FactorUtil.fill_factor_na_values(result_df, factor_class, database["basic_file"])

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

                # logger.info(
                #     "子任务完成：strategy={}, factor={}, calc_start_date={}, calc_end_date={}, prep_h5_database_cost={}, pre_calc_T-N_cost={}, prepare_t_day_database_cost={}, prepareT_cost={}, calc_cost={}".format(
                #         task["strategy"], factor_class.factor_name, task["calc_start_date"], task["calc_end_date"],
                #         time2 - time1, time3 - time2, time4 - time3, time5 - time4, end_time - time5))

            except Exception as e:
                logger.error("exception caught! strategy={}, factor={}, calc_date={}, error={}".format(
                    task["strategy"],factor_class.factor_name, task["calc_start_date"], e))
                result[factor_class.factor_name + "_" + task["strategy"]] = {
                    "error": True,
                    "factor_name": factor_class.factor_name,
                    "factor_type": FactorUtil.FactorType.T_DAY_FACTOR,
                    "factor_value": pd.DataFrame(),
                    "calc_start_date": task["calc_start_date"],
                    "calc_end_date": task["calc_end_date"],
                    "calc_cost": -1
                }
        view_bar(index, tot, task["calc_start_date"])
        return result

        # 提前加载数据


def __preload_data(task, index, tot):
    database = DataManager.pre_load_data(task)
    # for k in database.keys():
    #     v = database[k]
    #     new_dic = {}
    #     if v.shape[1] > 48:
    #         start = 0
    #         end = 25
    #         idx = 1
    #         while(start < v.shape[1]):
    #             new_dic[k+"_{}".format(str(idx))] = v.iloc[:, start:end]
    #             start = end
    #             end = end + 25 if end + 25 < v.shape[1] else v.shape[1]
    #             idx += 1
    #         database[k] = new_dic
    view_bar(index, tot, "prepare")
    return database


def __generate_preload_database(result, preload_result):
    for data_dict in preload_result:
        result.update(data_dict)
    return result


def __merge_factor_values(result, cost_result, error_factors, factor_class_map, calc_result):
    for factor_name in calc_result:
        real_name = calc_result[factor_name]["factor_name"]
        kls = factor_class_map[real_name]
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
                # TODO 耗时排序
                cost_result[factor_name]["cost"].append(calc_result[factor_name]["calc_cost"].total_seconds())
                cost_result[factor_name]["calc_date"].append(calc_result[factor_name]["calc_start_date"])

            else:
                result[factor_name] = {
                    "factor_name": calc_result[factor_name]["factor_name"],
                    "factor_class": kls,
                    "factor_type": calc_result[factor_name]["factor_type"],
                    "factor_value": calc_result[factor_name]["factor_value"]
                }
                # 如果是入库，还需要单独把未经过筛选的全市场因子值拿出来
                if "factor_value_full" in calc_result[factor_name]:
                    result[factor_name]["factor_value_full"] = calc_result[factor_name]["factor_value_full"]

                # TODO 耗时排序
                if calc_result[factor_name]["factor_type"] == FactorUtil.FactorType.T_1_FACTOR:
                    days = FactorUtil.factor_data.tradingday(calc_result[factor_name]["calc_start_date"], calc_result[factor_name]["calc_end_date"])
                    cost_result[factor_name] = {
                        "factor_name": calc_result[factor_name]["factor_name"],
                        "factor_class": kls,
                        "factor_type": calc_result[factor_name]["factor_type"],
                        "calc_date": days,
                        "cost": [calc_result[factor_name]["calc_cost"].total_seconds()] * len(days)
                    }
                else:
                    cost_result[factor_name] = {
                        "factor_name": calc_result[factor_name]["factor_name"],
                        "factor_class": kls,
                        "factor_type": calc_result[factor_name]["factor_type"],
                        "calc_date": [calc_result[factor_name]["calc_start_date"]],
                        "cost": [calc_result[factor_name]["calc_cost"].total_seconds()]
                    }
    return result, cost_result, error_factors


def __warehouse(strategy):
    if strategy == 'jupiter':
        logger.warning("Jupiter暂不支持入库！")
        return

    check_dict = {
        "europa": europa_warehouse,
        "saturn": saturn_warehouse,
        "sell": sell_warehouse,
        "metis": metis_warehouse,
        "mimas": mimas_warehouse,
        "neptune": neptune_warehouse,
        "neptunelong": neptunelong_warehouse
    }
    checker_result = {}
    check_dict[strategy]()

    logger.info("Factor warehouse finished!")
    return checker_result

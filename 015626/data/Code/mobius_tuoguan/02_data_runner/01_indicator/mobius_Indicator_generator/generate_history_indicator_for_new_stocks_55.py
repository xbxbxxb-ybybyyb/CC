import sys

from index_weight_change_checker import *
from indicator_generator import *
from param_generator.history_params_provider import *
import settings
import shutil
from daily_indicator_generator import check_base_data_pre_run



def write_index_stock_check_flag(date, minute_shift):
    flag_folder = f"{settings.FlagRootFolder}/{date}/offset_{minute_shift}/01_Indicator"
    if not os.path.exists(flag_folder):
        os.makedirs(flag_folder)
    flag_file = f"{flag_folder}/index_comp_check.success"
    with open(flag_file, "w") as f:
        f.write('')
        f.close()

def check_and_generate_indicator_for_index_stock_change(today, minute_shift):
    ## Step -1: check flag
    flag_file = f"{settings.FlagRootFolder}/{today}/offset_{minute_shift}/01_Indicator/index_comp_check.success"
    if os.path.exists(flag_folder):
        logger.info(f"flag已存在，不再校验指数成分股变化，{flag_file}")
        return

    ## Step 0: check base data
    check_base_data_pre_run(today, minute_shift)

    ## Step 1 : detect index weight change
    change_date = get_next_trading_date(today)
    index_stock_change_dict = get_index_stock_change_dict(settings.OfficialIndexWeightFolder, settings.IndexList, today)
    logger.info(
        f"[Mobius截面] 校验成分股变更, today={today}, change_date={change_date}, index_stock_change_dict={index_stock_change_dict}")
    if len(index_stock_change_dict) == 0:
        write_index_stock_check_flag(today, minute_shift)
        return

    ## Step 2: re-generate previous 27 index weight file
    if len(index_stock_change_dict) > 0:
        trading_date_list = factorData.tradingday(change_date, -29)[:-2]
        generate_index_weight_file_for_constituent_stocks_change(settings.IndexStockChangeWorkFolder, trading_date_list,
                                                                 index_stock_change_dict)

    ## Step 3: generate params for the new stocks
    batch_run_stock_list = set()
    for k, v in index_stock_change_dict.items():
        batch_run_stock_list = batch_run_stock_list | set(v["new_stocks"])
    logger.info(
        f"prepare history param for index stock change, change_date={change_date}, offset={minute_shift}, batch_run_stock_list={batch_run_stock_list}")
    history_dates = factorData.tradingday(change_date, -28)[:-1]
    prepare_param_for_history_dates(history_dates, settings.TestCaseRootFolder, batch_run_stock_list,
                                    settings.OfficalIndicatorFolder,
                                    minute_shift=minute_shift, work_index_weight_folder=settings.IndexStockChangeWorkFolder)
    ## Step 4: generate indicator for the new stocks
    ### Step 4-1: 生成前6天的冗余指标，为后续任务提供历史数据，不需要加载历史数据，可以并发执行
    dates_without_load_his_data = history_dates[:6]
    generate_indicator_for_index_stock_change_parallel(settings.CmdPrefixDailyGenerator, dates_without_load_his_data, batch_run_stock_list,
                                                       settings.TestCaseRootFolder, settings.LogRootFolder, minute_shift)
    ### Step 4-2: 生成后21天的有效指标，需要加载历史数据，需要顺序执行
    dates_with_load_his_data = history_dates[6:]
    generate_indicator_for_index_stock_change_sequential(settings.CmdPrefixDailyGenerator, dates_with_load_his_data, batch_run_stock_list,
                                                         settings.TestCaseRootFolder, settings.LogRootFolder, minute_shift)
    ## Step 5: 删除前6天的冗余指标
    delete_indicator_file(dates_without_load_his_data, batch_run_stock_list, settings.OfficalIndicatorFolder,
                          minute_shift)
    ## Step 6: 校验21天的有效指标
    check_success = check_indicator_file_exist(dates_with_load_his_data, batch_run_stock_list, settings.OfficalIndicatorFolder,
                          minute_shift)
    if check_success:
        write_index_stock_check_flag(today, minute_shift)
    else:
        logger.error(
            f"change_date={change_date}, today={today}, index_stock_change_dict={index_stock_change_dict}, 历史指标生成失败")

    ## Step 7: remove tmp 27 index weight file
    shutil.rmtree(settings.IndexStockChangeWorkFolder)

## 用于提前生成新成分股的历史指标，例如变更日=20250317，today=20250312
def ahead_generate_indicator_for_index_stock_change(today, change_date, minute_shift, index_stock_change_dict, first_generate):
    if first_generate:
        # 第一次生成历史指标，需要将前面的补齐
        full_history_dates = factorData.tradingday(change_date, -28)[:-1]
        history_dates = [date for date in full_history_dates if date <= today]
        if len(history_dates) < 7:
            logger.info(f"change_date={change_date}, today={today}, filtered_history_dates={filtered_history_dates}, 未到需要生成历史指标的日期")
            return

        ## Step 2: re-generate previous index weight file
        if len(index_stock_change_dict) > 0:
            date_list_for_index_weight = factorData.tradingday(change_date, -29)[:-2]
            filtered_date_list_for_index_weight = [date for date in date_list_for_index_weight if date < today]
            generate_index_weight_file_for_constituent_stocks_change(settings.IndexStockChangeWorkFolder,
                                                                     filtered_date_list_for_index_weight, index_stock_change_dict)

        ## Step 3: generate params for the new stocks
        batch_run_stock_list = set()
        for k, v in index_stock_change_dict.items():
            batch_run_stock_list = batch_run_stock_list | set(v["new_stocks"])
        logger.info(
            f"prepare history param for index stock change, change_date={change_date}, offset={minute_shift}, batch_run_stock_list={batch_run_stock_list}")

        prepare_param_for_history_dates(history_dates, settings.TestCaseRootFolder, batch_run_stock_list,
                                        settings.OfficalIndicatorFolder,
                                        minute_shift=minute_shift, work_index_weight_folder=settings.IndexStockChangeWorkFolder)
        ## Step 4: generate indicator for the new stocks
        ### Step 4-1: 生成前6天的冗余指标，为后续任务提供历史数据，不需要加载历史数据，可以并发执行
        dates_without_load_his_data = history_dates[:6]
        generate_indicator_for_index_stock_change_parallel(settings.CmdPrefixDailyGenerator, dates_without_load_his_data, batch_run_stock_list,
                                                           settings.TestCaseRootFolder, settings.LogRootFolder, minute_shift)
        ### Step 4-2: 生成后21天的有效指标，需要加载历史数据，需要顺序执行
        dates_with_load_his_data = history_dates[6:]
        generate_indicator_for_index_stock_change_sequential(settings.CmdPrefixDailyGenerator, dates_with_load_his_data, batch_run_stock_list,
                                                             settings.TestCaseRootFolder, settings.LogRootFolder, minute_shift)
        ## Step 5: 删除前6天的冗余指标
        delete_indicator_file(dates_without_load_his_data, batch_run_stock_list, settings.OfficalIndicatorFolder,
                              minute_shift)
        ## Step 6: 校验有效指标
        check_success = check_indicator_file_exist(dates_with_load_his_data, batch_run_stock_list, settings.OfficalIndicatorFolder,
                              minute_shift)
        if check_success:
            logger.info(
                f"change_date={change_date}, today={today}, index_stock_change_dict={index_stock_change_dict}, 历史指标生成成功")
        else:
            logger.error(f"change_date={change_date}, today={today}, index_stock_change_dict={index_stock_change_dict}, 历史指标生成失败!!!")

        # ## Step 7: remove tmp 27 index weight file
        # shutil.rmtree(settings.IndexStockChangeWorkFolder)
    else:
        #检查前6日指标是否存在
        check_dates = factorData.tradingday(today, -7)[:-1]
        batch_run_stock_list = set()
        for k, v in index_stock_change_dict.items():
            batch_run_stock_list = batch_run_stock_list | set(v["new_stocks"])
        check_success = check_indicator_file_exist(check_dates, batch_run_stock_list, settings.OfficalIndicatorFolder, minute_shift)
        if not check_success:
            logger.error(f"change_date={change_date}, today={today}, index_stock_change_dict={index_stock_change_dict}, 历史指标不存在")
            return

        #生成今日指标
        ##生成T-1日成分股文件
        generate_index_weight_file_for_constituent_stocks_change(settings.IndexStockChangeWorkFolder,
                                                                 [get_pre_trading_date(today)],
                                                                 index_stock_change_dict)
        ##生成参数
        test_case_base_folder_index_stock_change = os.path.join(settings.TestCaseRootFolder, today,
                                                                f"offset_{minute_shift}/01_Indicator/index_stock_change")
        prepare_trading_day(test_case_base_folder_index_stock_change, today, batch_run_stock_list=batch_run_stock_list,
                            load_his_data=None,
                            work_indicator_folder=settings.OfficalIndicatorFolder, minute_shift=minute_shift,
                            work_index_weight_folder=settings.IndexStockChangeWorkFolder)
        ##生成指标
        generate_indicator_for_index_stock_change_sequential(settings.CmdPrefixDailyGenerator, [today], batch_run_stock_list,
                                                             settings.TestCaseRootFolder, settings.LogRootFolder, minute_shift)
        ## 校验有效指标
        check_success = check_indicator_file_exist([today], batch_run_stock_list, settings.OfficalIndicatorFolder,
                                                   minute_shift)
        if check_success:
            logger.info(
                f"change_date={change_date}, today={today}, index_stock_change_dict={index_stock_change_dict}, 历史指标生成成功")
        else:
            logger.error(
                f"change_date={change_date}, today={today}, index_stock_change_dict={index_stock_change_dict}, 历史指标生成失败！！！")

        # ## Step 7: remove tmp index weight file
        # shutil.rmtree(settings.IndexStockChangeWorkFolder)

if __name__ == '__main__':
    today = "20250509"
    change_date = get_next_trading_date(today)
    minute_shift_list = [55]

    for minute_shift in minute_shift_list:
        # check_and_generate_indicator_for_index_stock_change(today, minute_shift)

        index_stock_change_dict={'ZZ1000': {'new_stocks': {'000589.SZ','301215.SZ','301377.SZ','601089.SH','603227.SH'},
                                            'removed_stocks': {'000736.SZ','001270.SZ','002214.SZ','300379.SZ','603398.SH'}}}
        # ahead_generate_indicator_for_index_stock_change("20250508", "20250512", minute_shift, index_stock_change_dict,
        #                                                 first_generate=True)
        ahead_generate_indicator_for_index_stock_change("20250509", "20250512", minute_shift, index_stock_change_dict,
                                                        first_generate=False)

        full_history_dates = factorData.tradingday(change_date, -22)[:-1]
        batch_run_stock_list = set()
        for k, v in index_stock_change_dict.items():
            batch_run_stock_list = batch_run_stock_list | set(v["new_stocks"])
        check_success = check_indicator_file_exist(full_history_dates, batch_run_stock_list, settings.OfficalIndicatorFolder,
                                                   minute_shift)
        if check_success:
            logger.info(f"Successfully generate history indicators for {batch_run_stock_list}, write flag")
            write_index_stock_check_flag(today, minute_shift)
            ## remove tmp index weight file
            #shutil.rmtree(settings.IndexStockChangeWorkFolder)
        else:
            logger.error(f"Failed to generate history indicators for {batch_run_stock_list}")





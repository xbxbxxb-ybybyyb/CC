import os
import sys

import settings
from index_weight_change_checker import *
from indicator_generator import *
from param_generator.history_params_provider import prepare_daily_param
from common.notice import *
lm = LinkMessage()
def LogAndSendMessageInfo(msg):
    logger.info(msg)
    lm.sendMessage(msg)
def LogAndSendMessageError(msg):
    logger.error(msg)
    lm.sendMessage(msg)


def check_market_data_flags(today):
    flag_list = [
        f"{settings.XdbFlagRootFolder}/stock/RHFData/HFData/{today}.success",
        f"{settings.XdbFlagRootFolder}/stock/UHFData/TickEx/{today}_sz.success",
        f"{settings.XdbFlagRootFolder}/stock/UHFData/TickEx/{today}_sh.success",
        f"{settings.XdbFlagRootFolder}/future/UHFData/TickEx/{today}.success",
        f"{settings.XdbFlagRootFolder}/index/UHFData/TickEx/{today}.success"
    ]
    unexist_flag_list = []
    for flag in flag_list:
        if not os.path.exists(flag):
            unexist_flag_list.append(flag)
    if len(unexist_flag_list) > 0:
        logger.warning(f"行情文件未生成，等待5分钟，missed_files={unexist_flag_list}")
        LogAndSendMessageError(
            f"[Mobius截面] 行情文件未生成，等待5分钟，missed_files={unexist_flag_list}")
        return False
    else:
        return True

def write_daily_indicator_flag(date, minute_shift):
    flag_base_folder_daily_indicator = f"{settings.FlagRootFolder}/{date}/offset_{minute_shift}/01_Indicator"
    if not os.path.exists(flag_base_folder_daily_indicator):
        os.makedirs(flag_base_folder_daily_indicator)
    flag_file = f"{flag_base_folder_daily_indicator}/daily_indicator.success"
    with open(flag_file, "w") as f:
        f.write('')
        f.close()

def write_pre_run_flag(date, minute_shift):
    flag_base_folder_daily_indicator = f"{settings.FlagRootFolder}/{date}/offset_{minute_shift}/01_Indicator"
    if not os.path.exists(flag_base_folder_daily_indicator):
        os.makedirs(flag_base_folder_daily_indicator)
    flag_file = f"{flag_base_folder_daily_indicator}/pre_run.success"
    with open(flag_file, "w") as f:
        f.write('')
        f.close()

def check_base_data(today):
    pre_trade_day = get_pre_trading_date(today)
    ## Step 0 : check index weight file | pre_trade_day
    check_index_weight_file_success = check_index_weight_file(pre_trade_day)
    if not check_index_weight_file_success:
        LogAndSendMessageError(f"[Mobius截面] 成分股文件校验失败, today={today}, pre_trade_day={pre_trade_day}")
        return False

    # wind ashare | pre_trade_day
    wind_file_flag_path = f"{settings.OfficialWindAshareFlagFolder}/{pre_trade_day}.success"
    while True:
        if not os.path.exists(wind_file_flag_path):
            logger.warning(f"WindAShare文件未生成，等待5分钟，flag_path={wind_file_flag_path}")
            LogAndSendMessageError(f"[Mobius截面] WindAShare文件未生成，等待5分钟，flag_path={wind_file_flag_path}")
            time.sleep(60 * 5)
        else:
            break

    # future contract | pre_trade_day
    future_contract_flag_path = f"{settings.OfficialFutureContractFlagFolder}/{pre_trade_day}_contract_univ.success"
    while True:
        if not os.path.exists(future_contract_flag_path):
            logger.warning(f"Future Contract文件未生成，等待5分钟，flag_path={future_contract_flag_path}")
            LogAndSendMessageError(f"[Mobius截面] Future Contract文件未生成，等待5分钟，flag_path={future_contract_flag_path}")
            time.sleep(60 * 5)
        else:
            break

    # daily data | today + pre_trade_day
    stock_daily_data_flag_path_pre = f"{settings.OfficialStockDailyDataFlagFolder}/{pre_trade_day}.success"
    while True:
        if not os.path.exists(stock_daily_data_flag_path_pre):
            logger.warning(f"StockDailyData前一日文件未生成，等待5分钟，flag_path={stock_daily_data_flag_path_pre}")
            LogAndSendMessageError(
                f"[Mobius截面] StockDailyData前一日文件未生成，等待5分钟，flag_path={stock_daily_data_flag_path_pre}")
            time.sleep(60 * 5)
        else:
            break
    stock_daily_data_flag_path_today = f"{settings.OfficialStockDailyDataFlagFolder}/{today}.success"
    while True:
        if not os.path.exists(stock_daily_data_flag_path_today):
            logger.warning(f"StockDailyData当日文件未生成，等待5分钟，flag_path={stock_daily_data_flag_path_today}")
            LogAndSendMessageError(
                f"[Mobius截面] StockDailyData当日文件未生成，等待5分钟，flag_path={stock_daily_data_flag_path_today}")
            time.sleep(60 * 5)
        else:
            break

    ## market data files | today
    while True:
        if not check_market_data_flags(today):
            time.sleep(60 * 5)
        else:
            break

def generate_daily_indicator(today, minute_shift):
    # LogAndSendMessageInfo(f"[Mobius截面] {today} offset_{minute_shift} 指标开始生成")
    # time_start = time.time()

    # pre_trade_day = get_pre_trading_date(today)
    # ## Step 0 : check index weight file/future contract/daily data/wind
    # check_index_weight_file_success = check_index_weight_file(pre_trade_day)
    # if not check_index_weight_file_success:
    #     LogAndSendMessageError(f"[Mobius截面] 成分股文件校验失败, today={today}, pre_trade_day={pre_trade_day}")
    #     return
    #
    # # wind_file_path = f"{settings.OfficialWindAshareFolder}/{pre_trade_day}/Stock_AShareCapitalization_{pre_trade_day}"
    # wind_file_flag_path = f"{settings.OfficialWindAshareFlagFolder}/{pre_trade_day}.success"
    # while True:
    #     if not os.path.exists(wind_file_flag_path):
    #         logger.warning(f"WindAShare文件未生成，等待5分钟，flag_path={wind_file_flag_path}")
    #         time.sleep(60 * 5)
    #     else:
    #         break
    #
    # ## Step 1 : check market data files
    # while True:
    #     if not check_market_data_flags(today):
    #         time.sleep(60 * 5)
    #     else:
    #         break

    ## Step 1 :
    check_base_data(today)

    # Step 2: generate params for generating daily indicator
    logger.info(f"prepare param, today={today}, minute_shift={minute_shift}")
    test_case_base_folder_daily_indicator = os.path.join(settings.TestCaseRootFolder, today,
                                                         f"offset_{minute_shift}/01_Indicator/daily_indicator")
    if not os.path.exists(test_case_base_folder_daily_indicator):
        os.makedirs(test_case_base_folder_daily_indicator)
    prepare_daily_param(today, test_case_base_folder_daily_indicator, settings.OfficalIndicatorFolder, minute_shift)

    ## Step 3: generate daily indicator
    log_base_folder_daily_indicator = f"{settings.LogRootFolder}/{today}/offset_{minute_shift}/01_Indicator/daily_indicator"
    if not os.path.exists(log_base_folder_daily_indicator):
        os.makedirs(log_base_folder_daily_indicator)

    generate_indicator_per_day(settings.CmdPrefixDailyGenerator, test_case_base_folder_daily_indicator, today,
                               log_base_folder_daily_indicator)

    ## Step 4: check daily indicator
    generate_folder = f"{settings.OfficalIndicatorFolder}/{today}/offset_{minute_shift}/01_Indicator/"
    indicator_file_list = os.listdir(generate_folder)
    if len(indicator_file_list) < 1808:
        LogAndSendMessageError(
            f"[Mobius截面] {today} offset_{minute_shift} generate indicator failed, count={len(indicator_file_list)}")
        sys.exit(1)
    else:
        # logger.info(f"{today} offset_{minute_shift} generate indicator success, count={len(indicator_file_list)}")
        write_daily_indicator_flag(today, minute_shift)

        # time_end = time.time()
        # LogAndSendMessageInfo(
        #     f"[Mobius截面] {today} offset_{minute_shift} generate indicator success, time_cost={round((time_end - time_start) / 60, 1)} min")

def check_base_data_pre_run(today, minute_shift):
    ## Step 0 : check index weight file | today
    check_index_weight_file_success = check_index_weight_file(today)
    if not check_index_weight_file_success:
        LogAndSendMessageError(f"[Mobius截面] 成分股文件校验失败, today={today}")
        return False

    # wind ashare | today
    wind_file_flag_path = f"{settings.OfficialWindAshareFlagFolder}/{today}.success"
    while True:
        if not os.path.exists(wind_file_flag_path):
            logger.warning(f"WindAShare文件未生成，等待5分钟，flag_path={wind_file_flag_path}")
            LogAndSendMessageError(f"[Mobius截面] WindAShare文件未生成，等待5分钟，flag_path={wind_file_flag_path}")
            time.sleep(60 * 5)
        else:
            break

    # future contract | today
    future_contract_flag_path = f"{settings.OfficialFutureContractFlagFolder}/{today}_contract_univ.success"
    while True:
        if not os.path.exists(future_contract_flag_path):
            logger.warning(f"Future Contract文件未生成，等待5分钟，flag_path={future_contract_flag_path}")
            LogAndSendMessageError(f"[Mobius截面] Future Contract文件未生成，等待5分钟，flag_path={future_contract_flag_path}")
            time.sleep(60 * 5)
        else:
            break

    # indicator | today
    flag_base_folder_daily_indicator = f"{settings.FlagRootFolder}/{today}/offset_{minute_shift}/01_Indicator/daily_indicator.success"
    while True:
        if not os.path.exists(flag_base_folder_daily_indicator):
            logger.warning(f"{today} offset_{minute_shift} 指标文件未生成，等待5分钟，flag_path={flag_base_folder_daily_indicator}")
            LogAndSendMessageError(
                f"[Mobius截面] {today} offset_{minute_shift} 指标文件未生成，等待5分钟，flag_path={flag_base_folder_daily_indicator}")
            time.sleep(60 * 5)
        else:
            break

def check_index_stock_change_flag_for_pre_run(date, minute_shift):
    flag_file = f"{settings.FlagRootFolder}/{date}/offset_{minute_shift}/01_Indicator/index_comp_check.success"
    if not os.path.exists(flag_file):
        LogAndSendMessageError(f"[Mobius截面] PreRun index_comp_check校验失败, flag_file={flag_file}")
        return False
    else:
        return True

def pre_run(today, minute_shift):
    ## Step 0: check base data
    #check_base_data_pre_run(today, minute_shift)

    ## Step 1: check index_stock_change_flag
    check_ret = check_index_stock_change_flag_for_pre_run(today, minute_shift)
    if not check_ret:
        return

    time_start = time.time()
    ## Step 5: 生成T+1日的实盘参数文件，回放T日的数据进行预跑
    logger.info(f"生成T+1日的实盘参数文件，回放T日的数据进行预跑")
    next_trade_date = get_next_trading_date(today)
    logger.info(f"prepare shipan param for next trade day={next_trade_date}, minute_shift={minute_shift}")
    test_case_base_folder_shipan_backtest = os.path.join(settings.TestCaseRootFolder, f"{today}_check",
                                                         f"offset_{minute_shift}/01_Indicator/shipan_backtest")
    if not os.path.exists(test_case_base_folder_shipan_backtest):
        os.makedirs(test_case_base_folder_shipan_backtest)
    prepare_daily_param(next_trade_date, test_case_base_folder_shipan_backtest, settings.OfficalIndicatorFolder,
                        minute_shift, replay_data_date=today,
                        real_env=False, mode='prd')
    log_base_folder_shipan_backtest = f"{settings.LogRootFolder}/{today}_check/offset_{minute_shift}/01_Indicator/shipan_backtest"
    if not os.path.exists(log_base_folder_shipan_backtest):
        os.makedirs(log_base_folder_shipan_backtest)
    log_file_shipan_backtest = f"{log_base_folder_shipan_backtest}/{next_trade_date}_shiban_backtest.log"
    run_shipan_backtest(settings.CmdPrefixShipanBacktest, test_case_base_folder_shipan_backtest, next_trade_date,
                        log_file_shipan_backtest)

    ## Step 6: check the log of shipan backtest
    back_test_log_check_success = check_shipan_backtest_log(log_file_shipan_backtest)
    if back_test_log_check_success:
        write_pre_run_flag(today, minute_shift)
        time_end = time.time()
        LogAndSendMessageInfo(
            f"[Mobius截面] PreRun successfully for next trade day={next_trade_date}, minute_shift={minute_shift}, total_time_cost={round((time_end - time_start) / 60, 1)} min")
    else:
        LogAndSendMessageError(
            f"[Mobius截面] PreRun run failed for next trade day={next_trade_date}, minute_shift={minute_shift} !!!!!!")

if __name__ == '__main__':
    # date_list = get_trading_date_list("20250318", "20250331")
    date_list = ["20250317"]
    for today in date_list:
        minute_shift_list = [0]
        # minute_shift_list = [10,20,30,40,55]
        for minute_shift in minute_shift_list:
            LogAndSendMessageInfo(f"[Mobius截面] {today} offset_{minute_shift} 指标开始生成")

            time_start = time.time()
            pre_trade_day = get_pre_trading_date(today)

            ## Step 0 : check index weight file
            check_index_weight_file_success = check_index_weight_file(settings.OfficialIndexWeightFolder, settings.IndexList,
                                                                      pre_trade_day)
            if not check_index_weight_file_success:
                LogAndSendMessageError(f"[Mobius截面] 成分股文件校验失败, today={today}, pre_trade_day={pre_trade_day}")
                sys.exit(1)

            wind_file_path = f"{settings.OfficialWindAshareFolder}/{pre_trade_day}/Stock_AShareCapitalization_{pre_trade_day}"
            while True:
                if not os.path.exists(wind_file_path):
                    logger.warning(f"WindAShare文件未生成，等待5分钟，path={wind_file_path}")
                    time.sleep(60 * 5)
                else:
                    break

            ## Step 1 : check market data files
            while True:
                if not check_market_data_flags(today):
                    time.sleep(60 * 5)
                else:
                    break

            # Step 2: generate params for generating daily indicator
            logger.info(f"prepare param, today={today}, minute_shift={minute_shift}")
            test_case_base_folder_daily_indicator = os.path.join(settings.TestCaseRootFolder, today,
                                                                 f"offset_{minute_shift}/01_Indicator/daily_indicator")
            if not os.path.exists(test_case_base_folder_daily_indicator):
                os.makedirs(test_case_base_folder_daily_indicator)
            prepare_daily_param(today, test_case_base_folder_daily_indicator, settings.OfficalIndicatorFolder, minute_shift)

            ## Step 3: generate daily indicator
            log_base_folder_daily_indicator = f"{LogRootFolder}/{today}/offset_{minute_shift}/01_Indicator/daily_indicator"
            if not os.path.exists(log_base_folder_daily_indicator):
                os.makedirs(log_base_folder_daily_indicator)

            generate_indicator_per_day(settings.CmdPrefixDailyGenerator, test_case_base_folder_daily_indicator, today, log_base_folder_daily_indicator)

            ## Step 4: check daily indicator
            generate_folder = f"{settings.OfficalIndicatorFolder}/{today}/offset_{minute_shift}/01_Indicator/"
            indicator_file_list = os.listdir(generate_folder)
            if len(indicator_file_list) != 1808:
                LogAndSendMessageError(f"[Mobius截面] {today} offset_{minute_shift} generate indicator failed, count={len(indicator_file_list)}")
                sys.exit(1)
            else:
                # logger.info(f"{today} offset_{minute_shift} generate indicator success, count={len(indicator_file_list)}")
                write_daily_indicator_flag(today, minute_shift)

                time_end = time.time()
                LogAndSendMessageInfo(
                    f"[Mobius截面] {today} offset_{minute_shift} generate indicator success, time_cost={round((time_end - time_start) / 60, 1)} min")

            # time_end = time.time()
            # LogAndSendMessageInfo(f"[Mobius截面] {today} offset_{minute_shift} generate indicator finished, time_cost={round((time_end - time_start) / 60, 1)} min")

            ## Step 5: 生成T+1日的实盘参数文件，回放T日的数据进行预跑
            logger.info(f"生成T+1日的实盘参数文件，回放T日的数据进行预跑")
            next_trade_date = get_next_trading_date(today)
            logger.info(f"prepare shipan param for next trade day={next_trade_date}, minute_shift={minute_shift}")
            test_case_base_folder_shipan_backtest = os.path.join(settings.TestCaseRootFolder, f"{next_trade_date}_check",
                                                                 f"offset_{minute_shift}/01_Indicator/shipan_backtest")
            if not os.path.exists(test_case_base_folder_shipan_backtest):
                os.makedirs(test_case_base_folder_shipan_backtest)
            prepare_daily_param(next_trade_date, test_case_base_folder_shipan_backtest, settings.OfficalIndicatorFolder, minute_shift, replay_data_date=today,
                                real_env=True, mode='prd')
            log_base_folder_shipan_backtest = f"{LogRootFolder}/{next_trade_date}_check/offset_{minute_shift}/01_Indicator/shipan_backtest"
            if not os.path.exists(log_base_folder_shipan_backtest):
                os.makedirs(log_base_folder_shipan_backtest)
            log_file_shipan_backtest = f"{log_base_folder_shipan_backtest}/{next_trade_date}_shiban_backtest.log"
            run_shipan_backtest(settings.CmdPrefixShipanBacktest, test_case_base_folder_shipan_backtest, next_trade_date, log_file_shipan_backtest)

            ## Step 6: check the log of shipan backtest
            back_test_log_check_success = check_shipan_backtest_log(log_file_shipan_backtest)
            if back_test_log_check_success:
                time_end = time.time()
                LogAndSendMessageInfo(f"[Mobius截面] Backtest run successfully for next trade day={next_trade_date}, minute_shift={minute_shift}, total_time_cost={round((time_end - time_start) / 60, 1)} min")
            else:
                LogAndSendMessageError(f"[Mobius截面] Backtest run failed for next trade day={next_trade_date}, minute_shift={minute_shift} !!!!!!")




import os
from loguru import logger
from datetime import date
from xquant.factordata import FactorData
from copy_file_for_prod import copy_entry_50

s = FactorData()


def indicator_entry(trading_day, offset):
    os.system(
        f'python3 /dfs/user/666466/02_data_runner/01_indicator/mobius_Indicator_generator/indicator_pre_run_entry.py {trading_day} {offset}')
    return None


def factor_entry(trading_day, offset):
    flag_file = f'/dfs/user/666466/04_flags/{trading_day}/offset_{offset}/factor/MobiusFactor.success'
    if os.path.exists(flag_file):
        os.system(
            f'python3 /dfs/user/666466/02_data_runner/factor/pre_gen_mobius_factor_params.py {trading_day} {offset}')
        os.system(f'python3 /dfs/user/666466/02_data_runner/factor/pre_run_mobius_factor.py {trading_day} {offset}')
    else:
        logger.error('pre run indicator flag not exist: {}', flag_file)
    return None


def get_next_trading_day(today):
    cdate_list = s.tradingday(today, 2)
    return cdate_list[-1]


def run_check():    
    offset = '50'
    today = date.today()
    today = today.strftime("%Y%m%d")
    #today = "20250418"
    cdate_list = [today]
    for today in cdate_list:
        trading_list = s.tradingday(today, -2)
        next_trading_day = get_next_trading_day(today)
        if today != trading_list[-1]:
            logger.warning("Today {} not trading day, exit", today)
        else:
            logger.info("Data delegate will run, today={}, offset={}", today, offset)
            indicator_entry(today, offset)
            factor_entry(today, offset)
            logger.info("Data Copy Entry today={}, next_trading_day = {}", today, next_trading_day)
            copy_entry_50(today, next_trading_day)

if __name__ == '__main__':
     run_check()

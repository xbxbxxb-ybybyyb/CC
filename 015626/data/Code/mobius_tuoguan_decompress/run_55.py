import os
from loguru import logger
from datetime import date
from xquant.factordata import FactorData


def indicator_entry(trading_day, offset):
    os.system(f'python3 /dfs/user/666466/02_data_runner/01_indicator/mobius_Indicator_generator/indicator_entry.py {trading_day} {offset}')
    return None


def factor_entry(trading_day, offset):
    flag_file = f'/dfs/user/666466/04_flags/{trading_day}/offset_{offset}/01_Indicator/daily_indicator.success'
    if os.path.exists(flag_file):
        os.system(f'python3 /dfs/user/666466/02_data_runner/factor/gen_mobius_factor_params.py {trading_day} {offset}')
        os.system(f'python3 /dfs/user/666466/02_data_runner/factor/run_mobius_factor.py {trading_day} {offset}')
    else:
        logger.error('indicator flag not exist: {}', flag_file)
    return None


def model_entry(today, offset):
    flag = os.path.join('/dfs/user/666466/04_flags/', today, 'offset_' + offset, 'factor', 'MobiusFactor.success')
    if os.path.exists(flag):
        if offset == '0':
            os.system("cd /dfs/user/666466/02_data_runner/model; python3 model_entry_0.py {}".format(today))
        elif offset == '50':
            os.system("cd /dfs/user/666466/02_data_runner/model; python3 model_entry_50.py {}".format(today))
        elif offset == '55':
            os.system("cd /dfs/user/666466/02_data_runner/model; python3 model_entry_55.py {}".format(today))
        else:
            logger.warn("invalid offset, offset={}", offset)
    else:
        logger.info('flag={} not exist, exit', flag)
    return None

def run_main():
    offset = '55'
    today = date.today()
    today = today.strftime("%Y%m%d")
    #today = "20250317"
    s = FactorData()
    cdate_list = [today]
    #cdate_list = s.tradingday("20250414", "20250417")
    for today in cdate_list:
    	trading_list = s.tradingday(today, -2)

    	if today != trading_list[-1]:
            logger.warning("Today {} not trading day, exit", today)
    	else:
            logger.info("Data delegate will run, today={}, offset={}", today, offset)
            indicator_entry(today, offset)
            factor_entry(today, offset)
            model_entry(today, offset)

if __name__ == '__main__':
    run_main()

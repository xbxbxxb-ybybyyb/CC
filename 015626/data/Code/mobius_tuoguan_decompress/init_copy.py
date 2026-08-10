# factor 61
# signal 61

import os
from loguru import logger
from xquant.factordata import FactorData
import shutil

def copy_factor(day_list, offset_list):
    for day in day_list:
        for offset in offset_list:
            logger.info("copy factor raw files, day={}, offset={}", day, offset)
            dest = f'/dfs/user/666466/06_prod_data/02_FactorData/{day}/offset_{offset}/02_Factor/raw'
            os.makedirs(dest, exist_ok=True)
            source = f'/dfs/user/666466/03_mobius/02_FactorData/{day}/offset_{offset}/02_Factor/raw/{day}'
            dest = f'/dfs/user/666466/06_prod_data/02_FactorData/{day}/offset_{offset}/02_Factor/raw/{day}'
            shutil.copy2(source, dest)

            if day == day_list[-1]:
                logger.info("copy factor norm files, day={}, offset={}", day, offset)
                dest = f'/dfs/user/666466/06_prod_data/02_FactorData/{day}/offset_{offset}/02_Factor/norm'
                os.makedirs(dest, exist_ok=True)
                source = f'/dfs/user/666466/03_mobius/02_FactorData/{day}/offset_{offset}/02_Factor/norm/{day}'
                dest = f'/dfs/user/666466/06_prod_data/02_FactorData/{day}/offset_{offset}/02_Factor/norm/{day}'
                shutil.copy2(source, dest)


def copy_signal(trading_list, signal_list, offset_list):
    for day in trading_list:
        for signal in signal_list:
            for offset in offset_list:
                logger.info("copy signal raw files, day={}, offset={}", day, offset)
                dest = f'/dfs/user/666466/06_prod_data/02_FactorData/{day}/offset_{offset}/03_signal/{signal}/raw'
                os.makedirs(dest, exist_ok=True)

                # copy norm
                source = f'/dfs/user/666466/03_mobius/02_FactorData/{day}/offset_{offset}/03_signal/{signal}/raw/{day}'
                dest = f'/dfs/user/666466/06_prod_data/02_FactorData/{day}/offset_{offset}/03_signal/{signal}/raw/{day}'
                shutil.copy2(source, dest)


def copy_indicator(trading_list, offset_list):
    for day in trading_list:
        for offset in offset_list:
            logger.info("copy indicator day={}, offset={}", day, offset)
            source = f'/dfs/user/666466/03_mobius/02_FactorData/{day}/offset_{offset}/01_Indicator'
            dest = f'/dfs/user/666466/06_prod_data/02_FactorData/{day}/offset_{offset}/01_Indicator'
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.copytree(source, dest)


def copy_norm2_signal(trading_list, signal_list, offset_list):
    # path = '/dfs/user/666466/06_prod_data/02_FactorData/20250317/offset_50/03_signal/20241213_ic_ic_v7unifac/history_files/signalNorm2Value'
    for day in trading_list:
        for signal in signal_list:
            for offset in offset_list:
                logger.info("copy signal norm2 files, day={}, offset={}", day, offset)
                dest = f'/dfs/user/666466/06_prod_data/02_FactorData/{day}/offset_{offset}/03_signal/{signal}/history_files/signalNorm2Value'
                if os.path.exists(dest):
                    shutil.rmtree(dest)
                source = f'/dfs/user/666466/03_mobius/02_FactorData/{day}/offset_{offset}/03_signal/{signal}/history_files/signalNorm2Value'
                shutil.copytree(source, dest)

   

if __name__ == '__main__':
    s = FactorData()
    day = '20250417'
    trading_list = s.tradingday(day, -62)
    # copy_indicator(trading_list[-14:], ['0', '50', '55'])
    # copy_factor(trading_list, ['0', '50', '55'])
    trading_list = s.tradingday(day, -31)
    signals = ['20241213_ic_ic_v7unifac', '20241213_ic_ic_v7unifac_crn', '20241213_if_if_v7c',
               '20241213_if_if_v7_crn', '20241213_im_im_v1unifac', '20241213_im_im_v1unifac_crn']
    # copy_signal(trading_list, signals, ['0'])
    trading_list = s.tradingday(day, -22)
    copy_norm2_signal(trading_list, signals, ['50', '55'])

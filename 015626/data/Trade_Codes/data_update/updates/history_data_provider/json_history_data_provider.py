import os
from datetime import datetime

from common.tools import *

from loguru import logger
from shutil import copyfile

from xquant.factordata import FactorData



class JsonHistoryDataProvider:
    def __init__(self, base_date, source_dir, save_dir):
        fd_service = FactorData()
        self.base_date = base_date
        self.all_dates = fd_service.tradingday(base_date, -7)
        self.source_data_dir = os.path.join(source_dir, base_date)
        self.dest_data_dir = os.path.join(save_dir, base_date)

    def prepare(self):
        for i in range(0, len(self.all_dates) - 1):
            dt = self.all_dates[i]
            source_file = os.path.join(self.source_data_dir, dt)
            dest_file = os.path.join(self.dest_data_dir, dt)
            if not os.path.exists(source_file):
                logger.warning("source file not exists, filename={}", source_file)
                exit(1)
            if not os.path.exists(self.dest_data_dir):
                os.makedirs(self.dest_data_dir)
            logger.info("copy file, base_date={}, copy_date={}", self.base_date, dt)
            copyfile(source_file, dest_file)


if __name__ == "__main__":
    # execute this script before trading day, this will get pre-6-trading-day history data
    cur_date = datetime.now().strftime("%Y%m%d")
    base_dates = [get_next_trading_day(cur_date)]
    source_dir = r'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/mobius_data_for_prod/minuteData'
    save_dir = r'/data/user/018728/cpp_projects/csi_calculator/history_data'
    for dt in base_dates:
        logger.info("prepare history data, base_date={}", dt)
        history_data_provider = JsonHistoryDataProvider(dt, source_dir, save_dir)
        history_data_provider.prepare()
        logger.info("prepare history data done")

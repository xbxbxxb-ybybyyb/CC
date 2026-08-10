import sys
sys.path.append('/data/user/017024/Diamond_2_0')

import pandas as pd
from multiprocessing.pool import Pool

from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
from overnight.naming_config import trade_stop_time
from overnight.factor_generator import prepare_history



need_days = [i.strftime('%Y%m%d') for i in udt.get_trading_date_range(20211207, 20211224)]

def func1(date):
    try:
        print(date, trade_stop_time.strftime('%H%M'))
        prepare_history(trade_date = date, has_hist=False, need_raw=False)
    except Exception as e:
        print(e)
        pd.Series(e).to_csv('/data/user/017024/waiting_for_delete/' + date + '_hist_{}.csv'.format(trade_stop_time.strftime('%H%M')))


if __name__ == '__main__':
    with Pool() as pool:
        pool.map(func1, need_days)

from xquant.compute.aimr import AIMR
from xquant.factordata import FactorData
import datetime as dt
import pandas as pd
import json
import sys
import os
from function_tools import get_trading_days

# os.chdir('/data/user/012913/IndexFuture/factor_framework')


start_date = dt.datetime.today().date().strftime('%Y%m%d')
start_date = sys.argv[1]
end_date = sys.argv[2]

# end_date = start_date

# trading_days = FactorData().tradingday('19900101', start_date)
trading_days = get_trading_days('19900101', start_date)
# trading_days = [i for i in trading_days if i >= start_date]

if not start_date in trading_days:
    print('Invalid trading day!!!')

else:
    params = {
        'parallel_list': ["{},{}".format(trading_days[-2], end_date)],
        'tag': 'update_future_tick',
        'cpu': 10,
        'gpu': 0,
        'memory': 100000
    }

    AIMR.runTasks('update_future_tick.py', json.dumps(params))

    params = {
        'parallel_list': ["{},{}".format(trading_days[-1], end_date)],
        'tag': 'clean_tick_csv',
        'cpu': 20,
        'gpu': 0,
        'memory': 100000
    }

    AIMR.runTasks('clean_tick_csv.py', json.dumps(params))

    params = {
        'parallel_list': ["{},{}".format(start_date, end_date)],
        'tag': 'future_tick_to_minute',
        'cpu': 10,
        'gpu': 0,
        'memory': 100000
    }
    AIMR.runTasks('future_tick_to_minute.py', json.dumps(params))

    params = {
        'parallel_list': ["{},{}".format(start_date, end_date)],
        'tag': 'update_index_data',
        'cpu': 10,
        'gpu': 0,
        'memory': 50000
    }
    AIMR.runTasks('update_index_data.py', json.dumps(params))

    params = {
        'parallel_list': ["{},{}".format(start_date, end_date)],
        'tag': 'update_index_weight_hset',
        'cpu': 10,
        'gpu': 0,
        'memory': 50000
    }
    AIMR.runTasks('update_index_weight_hset.py', json.dumps(params))

    params = {
        'parallel_list': ["{},{}".format(start_date, end_date)],
        'tag': 'update_future_universe',
        'cpu': 20,
        'gpu': 0,
        'memory': 100000,
    }
    AIMR.runTasks('update_future_universe.py', json.dumps(params))

    params = {
        'parallel_list': ["{},{}".format(start_date, end_date)],
        'tag': 'update_industry_data',
        'cpu': 20,
        'gpu': 0,
        'memory': 100000,
    }
    AIMR.runTasks('update_industry_data.py', json.dumps(params))

    params = {
        'parallel_list': ["{},{}".format(start_date, end_date)],
        'tag': 'update_cfg_data',
        'cpu': 10,
        'gpu': 0,
        'memory': 100000
    }
    AIMR.runTasks('update_cfg_data.py', json.dumps(params))
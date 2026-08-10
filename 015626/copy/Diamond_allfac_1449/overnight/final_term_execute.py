import os, time
import logging
import pandas as pd
import datetime as dt
from multiprocessing import Process
from overnight.naming_config import *
from xquant.xqutils.helper import link
from overnight.factor_generator import executor
from overnight.utility import add_file_logger, scheduler
from overnight.get_amp import get_amp_last5d, get_std_intraday
from overnight.retrieve_data_from_third_party import retrieve_alla_helper, retrieve_misc_helper, retrieve_mdconstant_helper
from overnight.retrieve_level2_from_third_party import retrieve_p1_hfdata_helper, retrieve_all_hfdata_helper, get_delta_time
lm = link.LinkMessage()

def final_funcs():
    target_trigger_time = pd.Timedelta(hours=trade_stop_time.hour, minutes=trade_stop_time.minute + 1)
#    target_trigger_time = pd.Timedelta(hours=14, minutes=47)
    def final_funcs_helper():
        logger1 = add_file_logger('Diamond_2_0', level=logging.DEBUG, file_name=os.path.join(log_path, dt.datetime.now().strftime('%Y%m%d'),\
                                  'Dia_1449_' + dt.datetime.now().strftime('%H%M%S') + '.log'))
        lm.sendMessage(str(dt.datetime.now()) + " start overnight final job" )
        logger1.info('start to retrieve level2 data')
        retrieve_all_hfdata_helper(get_delta_time(trade_mid_time, 1), get_delta_time(trade_stop_time, 1))
        logger1.info('has retrieved level2 data')
        lm.sendMessage(str(dt.datetime.now()) + " level2 data done!" )
        
        print(str(dt.datetime.now()) + '*** final execute ***')

        while True:
            if os.path.exists(os.path.join(trade_root, 'hot', pd.Timestamp.now().strftime('%Y%m%d'), 'alla_misc_done.success')):
                break
            lm.sendMessage('wait alla and misc data flag!')
            time.sleep(2)

        logger1.info('start final execution')
        executor()
        logger1.info('final execution has completed')
        print(str(dt.datetime.now()) + '*** final execute finish ***')
        lm.sendMessage(str(dt.datetime.now()) + " overnight signal done!" )
    scheduler(final_funcs_helper, target_trigger_time, delay=2000)

def mid_funcs():
    target_trigger_time = pd.Timedelta(hours=trade_mid_time.hour, minutes=trade_mid_time.minute + 1)
    def mid_funcs_helper():
        lm.sendMessage(str(dt.datetime.now()) + " start overnight mid job" )
        print(str(dt.datetime.now()) + '*** retrieve alla mid term minute ***')
        retrieve_alla_helper(trade_start_time, trade_mid_time)
        print(str(dt.datetime.now()) + '*** retrieve level2 data ***')
        retrieve_p1_hfdata_helper(trade_start_time, get_delta_time(trade_mid_time, 1))
        print(str(dt.datetime.now()) + '*** retrieve mdconstant ***')
        retrieve_mdconstant_helper()
        print(str(dt.datetime.now()) + '*** mid term finish ***')
        get_amp_last5d()
        get_std_intraday()
        lm.sendMessage(str(dt.datetime.now()) + " overnight mid job data done!")
    scheduler(mid_funcs_helper, target_trigger_time, delay=2000)

if __name__ == '__main__':
    handlers = list()
    handlers.append(Process(target=mid_funcs))
    handlers.append(Process(target=final_funcs))
    [p.start() for p in handlers]
    [p.join() for p in handlers]


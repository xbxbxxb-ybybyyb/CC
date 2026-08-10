import os
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
lm = link.LinkMessage()




def final_funcs():
    target_trigger_time = pd.Timedelta(hours=trade_stop_time.hour, minutes=trade_stop_time.minute + 1)
#    target_trigger_time = pd.Timedelta(hours=14, minutes=47)
    def final_funcs_helper():
        logger1 = add_file_logger('Diamond_2_0', level=logging.DEBUG, file_name=os.path.join(log_path, dt.datetime.now().strftime('%Y%m%d'),\
                                  'Dia_1449_' + dt.datetime.now().strftime('%H%M%S') + '.log'))
        lm.sendMessage(str(dt.datetime.now()) + " start overnight final job" )
        logger1.info('start to retrieve alla last term minute')
        # print(str(dt.datetime.now()) + '*** retrieve alla last term minute ***')
        retrieve_alla_helper(trade_mid_time, trade_stop_time)
        logger1.info('has retrieved alla last term minute')
        # print(str(dt.datetime.now()) + '*** retrieve misc minute ***')
        logger1.info('start to retrieve misc minute')
        retrieve_misc_helper(trade_start_time, trade_stop_time)
        logger1.info('has retrieved misc minute')
        print(str(dt.datetime.now()) + '*** final execute ***')
        logger1.info('start final execution')
        executor()
        logger1.info('final execution has completed')
        print(str(dt.datetime.now()) + '*** final execute finish ***')
        lm.sendMessage(str(dt.datetime.now()) + " overnight signal done!" )
    scheduler(final_funcs_helper, target_trigger_time, delay=2000)

def mid_funcs():
    lm.sendMessage(str(dt.datetime.now()) + " start overnight mid job" )
    print(str(dt.datetime.now()) + '*** retrieve alla mid term minute ***')
    retrieve_alla_helper(trade_start_time, trade_mid_time)
    print(str(dt.datetime.now()) + '*** retrieve mdconstant ***')
    retrieve_mdconstant_helper()
    print(str(dt.datetime.now()) + '*** mid term finish ***')
    get_amp_last5d()
    get_std_intraday()
    lm.sendMessage(str(dt.datetime.now()) + " overnight mid job data done!")

if __name__ == '__main__':
    handlers = list()
    handlers.append(Process(target=mid_funcs))
    handlers.append(Process(target=final_funcs))
    [p.start() for p in handlers]
    [p.join() for p in handlers]


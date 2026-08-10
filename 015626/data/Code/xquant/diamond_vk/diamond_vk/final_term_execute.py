from overnight.factor_generator import *
from overnight.insight_retrieve_mdconstant import *
from overnight.insight_retrieve_alla import *
from overnight.insight_retrieve_misc_minute import *
from overnight.naming_config import *
from overnight.utility import *
from multiprocessing import Process
import datetime
from xquant.xqutils.helper import link
lm = link.LinkMessage()






def final_funcs():
    target_trigger_time = pd.Timedelta(hours=trade_stop_time.hour, minutes=trade_stop_time.minute + 1)
#    target_trigger_time = pd.Timedelta(hours=14, minutes=47)
    def final_funcs_helper():
        logger1 = add_file_logger('Diamond_2_0', level=logging.DEBUG, file_name='/data/user/017024/waiting_for_delete/log/Diamond_2_0_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.log')
        lm.sendMessage(str(datetime.datetime.now()) + " start overnight final job" )
        logger1.info('start to retrieve alla last term minute')
        # print(str(datetime.datetime.now()) + '*** retrieve alla last term minute ***')
        retrieve_alla_helper(trade_mid_time, trade_stop_time, release_resource=False)
        logger1.info('has retrieved alla last term minute')
        # print(str(datetime.datetime.now()) + '*** retrieve misc minute ***')
        logger1.info('start to retrieve misc minute')
        retrieve_misc_minute_helper(release_resource=True)
        logger1.info('has retrieved misc minute')
        print(str(datetime.datetime.now()) + '*** final execute ***')
        logger1.info('start final execution')
        executor()
        logger1.info('final execution has completed')
        print(str(datetime.datetime.now()) + '*** final execute finish ***')
        lm.sendMessage(str(datetime.datetime.now()) + " overnight signal done!" )
    scheduler(final_funcs_helper, target_trigger_time, delay=2000)

def mid_funcs():
    nowdate = datetime.datetime.now().date().strftime('%Y%m%d')
    if not os.path.exists(os.path.join(trade_root, 'hot', nowdate, 'edb.h5')):
        lm.sendMessage('edb data is not exists!')
        raise Exception('edb data is not exists!')
    lm.sendMessage(str(datetime.datetime.now()) + " start overnight mid job" )
    print(str(datetime.datetime.now()) + '*** retrieve alla mid term minute ***')
    retrieve_alla_helper(trade_start_time, trade_mid_time, release_resource=False)
    print(str(datetime.datetime.now()) + '*** retrieve mdconstant ***')
    retrieve_mdconstant_helper(release_resource=True)
    # print(str(datetime.datetime.now()) + '*** prepare history ***')
    # prepare_history()
    print(str(datetime.datetime.now()) + '*** mid term finish ***')
    lm.sendMessage(str(datetime.datetime.now()) + " overnight mid job data done!")

if __name__ == '__main__':
    handlers = list()
    handlers.append(Process(target=mid_funcs))
    handlers.append(Process(target=final_funcs))
    [p.start() for p in handlers]
    [p.join() for p in handlers]


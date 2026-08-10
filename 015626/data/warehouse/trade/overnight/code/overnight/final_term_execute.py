from overnight.factor_generator import *
from overnight.insight_retrieve_mdconstant import *
from overnight.insight_retrieve_alla import *
from overnight.insight_retrieve_misc_minute import *
from overnight.utility import *
from multiprocessing import Process
from xquant.xqutils.helper import link
lm = link.LinkMessage()

def final_funcs():
    target_trigger_time = pd.Timedelta(hours=trade_stop_time.hour, minutes=trade_stop_time.minute + 1)
#    target_trigger_time = pd.Timedelta(hours=14, minutes=47)
    def final_funcs_helper():
        lm.sendMessage(str(datetime.datetime.now()) + " start overnight final job" )
        print('*** retrieve alla last term minute ***')
        retrieve_alla_helper(trade_mid_time, trade_stop_time, release_resource=False)
        print('*** retrieve misc minute ***')
        retrieve_misc_minute_helper(release_resource=True)
        print('*** final execute ***')
        executor()
        print('*** final execute finish ***')
        lm.sendMessage(str(datetime.datetime.now()) + " overnight signal done!" )
    scheduler(final_funcs_helper, target_trigger_time, delay=2000)

def mid_funcs():
    lm.sendMessage(str(datetime.datetime.now()) + " start overnight mid job" )
    print('*** retrieve alla mid term minute ***')
    retrieve_alla_helper(trade_start_time, trade_mid_time, release_resource=False)
    print('*** retrieve mdconstant ***')
    retrieve_mdconstant_helper(release_resource=True)
    print('*** prepare history ***')
    prepare_history()
    print('*** mid term finish ***')
    lm.sendMessage(str(datetime.datetime.now()) + " overnight mid job data done!" )

if __name__ == '__main__':
    handlers = list()
    handlers.append(Process(target=mid_funcs))
    handlers.append(Process(target=final_funcs))
    [p.start() for p in handlers]
    [p.join() for p in handlers]


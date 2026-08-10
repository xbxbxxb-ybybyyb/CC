from diamond_vk.factor_generator import *
from diamond_vk.insight_retrieve_mdconstant import *
from diamond_vk.insight_retrieve_alla import *
from diamond_vk.insight_retrieve_misc_minute import *
from diamond_vk.naming_config import *
from diamond_vk.utility import *
from multiprocessing import Process
import datetime
from xquant.xqutils.helper import link
lm = link.LinkMessage()

def final_funcs():
    target_trigger_time = pd.Timedelta(hours=trade_stop_time.hour, minutes=trade_stop_time.minute + 1)
#    target_trigger_time = pd.Timedelta(hours=14, minutes=47)
    def final_funcs_helper():
        lm.sendMessage(str(datetime.datetime.now()) + " start diamond_vk final job" )
        executor()
    scheduler(final_funcs_helper, target_trigger_time, delay=2000)

def mid_funcs():
    f = FactorGenerator()
    f.prepare_hist_data()
    f.dump_hist_data()
    lm.sendMessage(str(datetime.datetime.now()) + " diamond_vk history data done!")

if __name__ == '__main__':
    handlers = list()
    handlers.append(Process(target=mid_funcs))
    handlers.append(Process(target=final_funcs))
    [p.start() for p in handlers]
    [p.join() for p in handlers]


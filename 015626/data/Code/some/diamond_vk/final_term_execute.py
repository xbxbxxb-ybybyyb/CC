from diamond_vk.factor_generator import *
from diamond_vk.naming_config import *
from diamond_vk.utility import *
from insight_retrieve_ccbond import retrieve_ccbond_helper
from insight_retrieve_ccbond_stock import retrieve_ccbond_stock_helper
from insight_retrieve_mdconstant import retrieve_mdconstant_helper
from multiprocessing import Process
import datetime
from xquant.xqutils.helper import link
lm = link.LinkMessage()

def delayed_time(time, time_delta=datetime.timedelta(minutes=1)):
    assert isinstance(time, datetime.time) and isinstance(time_delta, datetime.timedelta)
    return (datetime.datetime.combine(datetime.date.today(), time) + time_delta).time()
    
def final_funcs():
    target_trigger_time = pd.Timedelta(hours=trade_stop_time.hour, minutes=trade_stop_time.minute+1)
#    target_trigger_time = pd.Timedelta(hours=14, minutes=56)
    def final_funcs_helper():
        lm.sendMessage(str(datetime.datetime.now()) + " start diamond_vk final job" )
        retrieve_ccbond_helper(mid_job_time, ref_close_end_time)
        lm.sendMessage(str(datetime.datetime.now()) + " final job data done" )
        executor()
    scheduler(final_funcs_helper, target_trigger_time, delay=2000)

def history_data_funcs():
    f = FactorGenerator()
    f.prepare_hist_data()
    f.dump_hist_data()
    lm.sendMessage(str(datetime.datetime.now()) + " diamond_vk history data done!")
    
def get_ccbond_minute_mid():
    mid_job_delayed_time = delayed_time(mid_job_time)
    target_trigger_time = pd.Timedelta(hours=mid_job_delayed_time.hour, minutes=mid_job_delayed_time.minute)
#    target_trigger_time = pd.Timedelta(hours=14, minutes=55)
    def ccbond_minute_mid_helper():
        lm.sendMessage(str(datetime.datetime.now()) + " start ccbond mid job" )
        retrieve_ccbond_helper(morning_start_time, mid_job_time)
        lm.sendMessage(str(datetime.datetime.now()) + " end ccbond mid job" )
    scheduler(ccbond_minute_mid_helper, target_trigger_time, delay=2000)


def get_ccbond_stock_minute():
    stock_ref_limit_delayed_time = delayed_time(stock_ref_limit_end_time)
    target_trigger_time = pd.Timedelta(hours=stock_ref_limit_delayed_time.hour, minutes=stock_ref_limit_delayed_time.minute)
#    target_trigger_time = pd.Timedelta(hours=14, minutes=54)
    def ccbond_stock_minute_helper():
        lm.sendMessage(str(datetime.datetime.now()) + " start ccbond stock minute job" )
        retrieve_ccbond_stock_helper(morning_start_time, stock_ref_limit_end_time)
        lm.sendMessage(str(datetime.datetime.now()) + " end ccbond stock minute job" )
    scheduler(ccbond_stock_minute_helper, target_trigger_time, delay=2000)


def get_stock_mdconstant():
    lm.sendMessage(str(datetime.datetime.now()) + " start mdconstant job" )
    retrieve_mdconstant_helper()
    lm.sendMessage(str(datetime.datetime.now()) + " end mdconstant job" )

#for dd in [20221228,20221229,20221230]:
#    f = FactorGenerator()
#    f.prepare_hist_data(trade_date = dd)
#    f.dump_hist_data()
#    lm.sendMessage(str(datetime.datetime.now()) + " diamond_vk history data done!")
#    executor(trade_date = dd)


if __name__ == '__main__':
    handlers = list()
    handlers.append(Process(target=history_data_funcs))
    handlers.append(Process(target=get_stock_mdconstant))
    handlers.append(Process(target=get_ccbond_minute_mid))
    handlers.append(Process(target=get_ccbond_stock_minute))
    handlers.append(Process(target=final_funcs))
    [p.start() for p in handlers]
    [p.join() for p in handlers]

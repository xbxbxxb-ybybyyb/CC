import datetime
from multifactor.data.utils import *
from xquant.xqutils.helper import link


_, end_date, _ = check_update_date()

flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'
def minute_flag_check(date):
    path1 = flag_rootpath + str(date) + '/' + str(date) + '_gen_factors_and_model.success'
    return os.path.exists(path1)
    
print('start check flag')
while True:
    lm = link.LinkMessage()
    if minute_flag_check(end_date):
        lm.sendMessage(str(datetime.datetime.now()) + " gen factors and model success" )
        print(str(datetime.datetime.now()) + " gen factors and model success")
        break
    lm.sendMessage(str(datetime.datetime.now()) + " gen factors and model fail...   next check time: 5 minutes later" )
    print(str(datetime.datetime.now()) + " gen factors and model fail...   next check time: 5 minutes later" )
    time.sleep(300)
    del(lm)

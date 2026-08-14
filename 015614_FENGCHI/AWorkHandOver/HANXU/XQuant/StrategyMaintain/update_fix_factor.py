import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

from TSmodel.RealTime.DailyUpdate import get_fix_factor_list, init_update, store_factor, multiprocess
from dataApi.sendInfo import send_message
import time

start_date1 = 20140801
end_date1 = 20200630

start_date2 = 0
end_date2 = None

factor_address = '/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/'
#factor_list = get_fix_factor_list(True, factor_address)
#init_update(restore_start_date=start_date1, end_date=end_date1)

#def _func1(sub_list, line=0):
#    for factor_name in sub_list:
#        store_factor(factor_name, restore_start_date=start_date1, end_date=end_date1)
#multiprocess(36, _func1, factor_list)

if (time.gmtime().tm_hour + 8) % 24 > 17:

    init_update(restore_start_date=start_date2, end_date=end_date2)
    send_message(['015664'], 'Fix标签更新成功')
else:
    factor_list = get_fix_factor_list(True, factor_address)
    def _func2(sub_list, line=0):
        for factor_name in sub_list:
            store_factor(factor_name, restore_start_date=start_date2, end_date=end_date2)
    multiprocess(36, _func2, factor_list)
#    _func2(factor_list, line=0)
    send_message(['015664'], 'Fix线下因子更新成功')
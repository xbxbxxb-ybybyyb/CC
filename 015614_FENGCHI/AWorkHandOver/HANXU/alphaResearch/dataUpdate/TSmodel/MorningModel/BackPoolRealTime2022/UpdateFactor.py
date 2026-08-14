import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

from TSmodel.MorningModel.MorningDailyUpdate.DailyUpdate import update_factor, multiprocess
from TSmodel.MorningModel.MorningDailyUpdate.DTFactorTest4RealTime import TSFactorTest, CSFactorTest
from dataApi.tradeDate import get_recent_trade_date, get_pre_trade_date, get_date_range
from HFfactor.MinFactorSuper.Utility.ExtendNumpy import get_numpy_head
from TSmodel.MorningModel.PreprocessFactor import get_morning_factor_list
import numpy as np
import pandas as pd
import os
import time
import gc

print(time.strftime('%Y-%m-%d %H:%M:%S'), 'Start Update Factor.')
amend_date = 0
recent_date = amend_date if amend_date else get_recent_trade_date(dividing_point=19)
data_address = '/data/group/800442/800319/HFfactor/MorningFactor/data/'
factor_list = get_morning_factor_list(False)


def _func_factor(sub_list, line=0):
    for factor_name in sub_list:
        update_factor(recent_date, factor_name=factor_name, data_address=data_address)


multiprocess(36, _func_factor, factor_list)
print(time.strftime('%Y-%m-%d %H:%M:%S'), 'Finish Store Factor.')


factor_list = [f'{y}_{x}' for x in get_morning_factor_list(False) for y in ['WC', 'WCN', 'T40WC', 'T40WCN']]
end_date = get_pre_trade_date(get_recent_trade_date(dividing_point=19), 6)
recent_amend_date = get_pre_trade_date(recent_date, 6)
amend_days = len(get_date_range(recent_amend_date, end_date))
start_date = get_pre_trade_date(end_date, amend_days)
numpy_head = get_numpy_head((len(get_date_range(20140801, end_date)), 64), 'float64')
csft = CSFactorTest(start_date=start_date, end_date=end_date, address=data_address)
csft.set_basic_data('future930t30h135d')


def _func_cs_test(sub_list, line=0):
    for name in sub_list:
        file = f'/data/group/800442/800319/HFfactor/MorningFactor/real_time_test/cs_test/{name}.npy'
        if not os.path.exists(file):
            fp = np.memmap(file, dtype='uint8', mode='w+', shape=(128,))
            fp[:] = numpy_head
            del fp
        else:
            fp = np.memmap(file, dtype='uint8', mode='r+', shape=(128,))
            fp[:] = numpy_head
            del fp
        factor = csft.set_factor(name, address=f'{data_address}/factor/')
        cs_result = np.ascontiguousarray(csft.cs_test(factor))[-amend_days:]
        fp = np.memmap(file, dtype='float64', mode='r+', shape=cs_result.shape,
                       offset=(len(get_date_range(20140801, end_date)) - amend_days) * 64 * 8 + 128)
        fp[:] = cs_result
        del fp

if amend_days > 0:
    multiprocess(10, _func_cs_test, factor_list)
    print(time.strftime('%Y-%m-%d %H:%M:%S'), 'Finish CSTest Factor.')
else:
    print(time.strftime('%Y-%m-%d %H:%M:%S'), 'No Need CSTest Factor.')
del csft
gc.collect()



# def _func_temp1(sub_list, line=0):
#     for name in sub_list:
#         try:
#             file = f'/data/group/800442/800319/HFfactor/MorningFactor/real_time_test/cs_test/{name}.npy'
#             factor = csft.set_factor(name, address=f'{data_address}/factor/')
#             cs_result = np.ascontiguousarray(csft.cs_test(factor))
#             np.save(file, cs_result)
#         except:
#             print(name)
# multiprocess(15, _func_temp1, factor_list)
#
#
# def _func_temp2(sub_list, line=0):
#     for name in sub_list:
#         try:
#             file = f'/data/group/800442/800319/HFfactor/MorningFactor/real_time_test/cs_test/{name}.npy'
#             fp = np.memmap(file, dtype='uint8', mode='r+', shape=(128,))
#             fp[:] = numpy_head
#             del fp
#             factor = csft.set_factor(name, address=f'{data_address}/factor/')
#             cs_result = np.ascontiguousarray(csft.cs_test(factor))[-amend_days:]
#             fp = np.memmap(file, dtype='float64', mode='r+', shape=cs_result.shape,
#                            offset=(len(get_date_range(20140801, end_date)) - amend_days) * 64 * 8 + 128)
#             fp[:] = cs_result
#             del fp
#         except:
#             print(name)
# _func_temp2(factor_list)
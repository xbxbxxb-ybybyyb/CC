import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

from TSmodel.MorningModel.BackPoolRealTime2022.XGB import train_xgb
from TSmodel.MorningModel.MorningDailyUpdate.DailyUpdate import update_factor, multiprocess
from TSmodel.MorningModel.MorningDailyUpdate.DTFactorTest4RealTime import TSFactorTest, CSFactorTest
from TSmodel.MorningModel.PreprocessFactor import get_morning_factor_list
from dataApi.tradeDate import get_date_range
from dataApi.tradeDate import get_pre_trade_date, get_recent_trade_date
from HFfactor.MinFactorSuper.Utility.ExtendNumpy import get_numpy_head
import time
import gc
import os
import pandas as pd
import numpy as np

print(time.strftime('%Y-%m-%d %H:%M:%S'), 'Start Update Factor.')
amend_date = 0
recent_date = amend_date if amend_date else get_recent_trade_date(dividing_point=19)
data_address = '/data/group/800442/800319/HFfactor/MorningFactor/data/'
factor_list = get_morning_factor_list(True)


def _func_factor(sub_list, line=0):
    for factor_name in sub_list:
        update_factor(recent_date, factor_name=factor_name, data_address=data_address)


multiprocess(36, _func_factor, factor_list)
print(time.strftime('%Y-%m-%d %H:%M:%S'), 'Finish Store Factor.')

factor_list = [f'{y}_{x}' for x in get_morning_factor_list(True) for y in ['WC', 'WCN', 'T40WC', 'T40WCN']]

end_date = get_pre_trade_date(get_recent_trade_date(dividing_point=19), 6)
numpy_head = get_numpy_head((len(get_date_range(20140801, end_date)), 64), 'float64')


def _func_cs_test(sub_list, line=0):
    for name in sub_list:
        file = f'/data/group/800442/800319/HFfactor/MorningFactor/real_time_test/cs_test/{name}.npy'
        if not os.path.exists(file):
            fp = np.memmap(file, dtype='uint8', mode='w+', shape=(128,))
            fp[:] = numpy_head
            del fp
            recent_amend_date = 20140801
            amend_days = len(get_date_range(recent_amend_date, end_date))
            start_date = 20140801
        else:
            recent_amend_date = get_pre_trade_date(int(np.load(file)[-1, 0]), -1)
            amend_days = len(get_date_range(recent_amend_date, end_date))
            start_date = get_pre_trade_date(end_date, amend_days)
            fp = np.memmap(file, dtype='uint8', mode='r+', shape=(128,))
            fp[:] = numpy_head
            del fp

        csft = CSFactorTest(start_date=start_date, end_date=end_date, address=data_address)
        csft.set_basic_data('future930t30h135d')
        factor = csft.set_factor(name, address=f'{data_address}/factor/')
        cs_result = np.ascontiguousarray(csft.cs_test(factor))[-amend_days:]
        fp = np.memmap(file, dtype='float64', mode='r+', shape=cs_result.shape,
                       offset=(len(get_date_range(20140801, end_date)) - amend_days) * 64 * 8 + 128)
        fp[:] = cs_result
        del fp, csft
        gc.collect()
        print(time.strftime('%Y%m%d %H:%M:%S'),
              f"{name} is CSTest from {recent_amend_date} to {end_date} successfully.")


multiprocess(36, _func_cs_test, factor_list)
print(time.strftime('%Y-%m-%d %H:%M:%S'), 'Finish CSTest Factor.')

# Time 100min
tsft = TSFactorTest(start_date=20140801, end_date=end_date, address=data_address)
if os.path.exists('/data/group/800442/800319/HFfactor/MorningFactor/real_time_test/month_tags.npy'):
    month_tags = np.load('/data/group/800442/800319/HFfactor/MorningFactor/real_time_test/month_tags.npy')
    if month_tags[-1] == tsft.month_tags[-1]:
        # redo_ts_test = False
        redo_ts_test = True
    else:
        redo_ts_test = True
else:
    redo_ts_test = True
if redo_ts_test:
    tsft.set_basic_data('future930t30h135d')


    def _func_ts_test(sub_list, line=0):
        for name in sub_list:
            factor = tsft.set_factor(name, address=f'{data_address}/factor/')
            ts_result = tsft.ts_test(factor)
            pd.to_pickle(ts_result,
                         f'/data/group/800442/800319/HFfactor/MorningFactor/real_time_test/ts_test/{name}.pkl')


    multiprocess(36, _func_ts_test, factor_list)
    np.save('/data/group/800442/800319/HFfactor/MorningFactor/real_time_test/month_tags.npy', tsft.month_tags)
    print(time.strftime('%Y-%m-%d %H:%M:%S'), 'Finish TSTest Factor.')
else:
    print(time.strftime('%Y-%m-%d %H:%M:%S'), 'No Need TSTest Factor.')


gen_list = [
    "True|['WC', 'T40WC']|ts_ic_t_select|1200|0.7|True",
    "False|['WCN', 'T40WCN']|ts_ic_mean_select|1200|0.7|True",
    "True|['WCN', 'T40WCN']|group_dist_select|1200|0.7|True",
    "True|WC|ts_ret_t_select|1200|0.7|True",
]
pred_end = get_recent_trade_date()


for model_gen in gen_list:
    train_xgb(model_gen, pred_end)

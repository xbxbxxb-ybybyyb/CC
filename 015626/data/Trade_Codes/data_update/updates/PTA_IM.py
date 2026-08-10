import sys
sys.path.insert(4,'/data/user/016700/')
from TT.back_test_tick_multisignal_filter_open import *
sys.path.insert(4,'/data/user/015626/JupyterNotebooks/utils/')
sys.path.insert(4,'/data/user/015626/data/share/Code/strategy_back_test/')
# from strategy_backtest_tick import *

import pandas as pd
import numpy as np
from multifactor.IO import IO
import multifactor.utility.dt as udt
#%matplotlib inline
import datetime
import os
import glob
import gzip
import shutil
#from icecream import ic
from multifactor.data.utils import *
from dateutil.relativedelta import relativedelta
from operators_cc import drop_dup
import json

ticker = 'IM.CFE'

filt_bool = True
filt_name = 'futures_long_vol'
filter_bar = 0.00045
sdate,eedate,cdate_list = check_update_date()
for edate in cdate_list:
    date = str(edate)[:4] + '-' + str(edate)[4:6] + '-' + str(edate)[6:]
    #date = '2022-05-26'
    
    if 'IC' in ticker.upper():
        multiplier = 200
        trail = ''
        slip = 0.8
        machine = '#503301'
    elif 'IF' in ticker.upper():
        multiplier = 300
        trail = '_if'
        slip = 0.6
        machine = '#503302'
    elif 'IM' in ticker.upper():
        multiplier = 200
        trail = '_im'
        slip = 0.8
        machine = '#503303'
    
    if machine == '#503301':
        strat_ip = '168.11.233.17'
    elif machine == '#503302':
        strat_ip = '168.11.233.110'
    elif machine == '#503303':
        strat_ip = '168.11.233.111'
        
    contractl = pd.read_excel('/data/user/016700/Data/para/Mobius_%s/MobiusStrategy_%s_%s.xlsx'%(date.replace('-', ''), ticker[:2], date.replace('-', '') + machine))['开仓列表'].iloc[0]
    contractl = [item + 'E' for item in contractl.split(',')]
    if 'IF' in ticker.upper():
        model_date_list = [ '20240329_if_if_v7c_orig_norm2', '20240329_if_if_v7_crn_norm2']
        #model_date_list = ['20240329_if_if_v6nl', '20240329_if_if_v7c_orig']
    elif 'IC' in ticker.upper():    
        model_date_list = ['20240329_ic_ic_v7unifac_orig_norm2', '20240329_ic_ic_v7unifac_crn_norm2']
        #model_date_list = ['20240329_ic_ic_v7unifac_orig', '20240329_ic_ic_v7c_orig', '20240329_ic_ic_short_v3c']
    elif 'IM' in ticker.upper():    
        model_date_list = ['20240329_im_im_v1unifac_crn_norm2', '20240329_im_im_v1unifac_orig_norm2']
    
    cash_dict = {}

    cash_dict['20240329_if_if_v7c_orig'] = 0e8
    cash_dict['20240329_if_if_v7_crn'] = 0e8    
    cash_dict['20240329_if_if_v7c_orig_norm2'] = 2.5e8
    cash_dict['20240329_if_if_v7_crn_norm2'] = 2.5e8
    cash_dict['20240329_if_if_v7c'] = 0e8
    
    cash_dict['20240329_ic_ic_v7unifac'] = 0e8
    cash_dict['20240329_ic_ic_v7unifac_orig'] = 0e8
    cash_dict['20240329_ic_ic_v7unifac_crn'] = 0e8
    cash_dict['20240329_ic_ic_v7unifac_orig_norm2'] = 2.5e8
    cash_dict['20240329_ic_ic_v7unifac_crn_norm2'] = 2.5e8

    cash_dict['20240329_im_im_v1unifac_orig'] = 0e8
    cash_dict['20240329_im_im_v1unifac_crn'] = 0e8
    cash_dict['20240329_im_im_v1unifac_orig_norm2'] = 3.5e8
    cash_dict['20240329_im_im_v1unifac_crn_norm2'] = 3.5e8

    pos_divnum = 10


    pos_dict = {}



    pos_dict['20240329_ic_ic_v7unifac'] = {(0, 0.0001): (0.0, 0.0),
                    (0.0001, 0.0002): (0.0, 0.333/10),
                    (0.0002, 0.0003): (0.0/10, 0.666/10),
                    (0.0003, 0.0004): (0.0/10, 1.0/10),
                    (0.0004, 0.0006): (0.0/10, 1.0/10),
                    (0.0006, 0.0007): (0.333/10, 1.0/10),
                    (0.0007, 0.0008): (0.666/10, 1.0/10),
                    (0.0008, 100): (1.0/10, 1.0/10)             
                   }
    
    pos_dict['20240329_if_if_v7c'] = {(0, 0.0001): (0.0, 0.0),
                    (0.0001, 0.0002): (0.0, 0.333/10),
                    (0.0002, 0.0003): (0.0/10, 0.666/10),
                    (0.0003, 0.0004): (0.0/10, 1.0/10),
                    (0.0004, 0.0006): (0.0/10, 1.0/10),
                    (0.0006, 0.0007): (0.333/10, 1.0/10),
                    (0.0007, 0.0008): (0.666/10, 1.0/10),
                    (0.0008, 100): (1.0/10, 1.0/10)             
                   }
    
    pos_dict['20240329_ic_ic_v7unifac_crn'] = {(0,        0.1): (0.0,       0.0),
                    (0.1,       0.2):  (0.0/10,   0.5/10),
                    (0.2,       0.8):  (0.0/10,   1/10),
                    (0.8,       0.85): (0.25/10,  1.0/10),
                    (0.85,      0.9):  (0.5/10,   1.0/10),
                    (0.9,       0.95): (0.75/10,  1.0/10),
                    (0.95,      100):  (1.0/10,   1.0/10) }



    pos_dict['20240329_ic_ic_v7unifac_orig'] = {
                (0,    0.2):  (0,        0),
                (0.2,  0.3):  (0,        0.5/pos_divnum),
                (0.3,  0.8):  (0,        1/pos_divnum),
                (0.8,  0.85): (0.25/pos_divnum,   1/pos_divnum),
                (0.85, 0.9):  (0.5/pos_divnum,    1/pos_divnum),
                (0.9,  0.95): (0.75/pos_divnum,   1/pos_divnum),
                (0.95, 100):  (1/pos_divnum,      1/pos_divnum)}

    
    pos_dict['20240329_ic_ic_v7unifac_crn_norm2'] = {(0,         0.07): (0.0,       0.0),
                                                     (0.07,      0.15):  (0.0/10,   0.5/10),
                                                     (0.15,      0.7):  (0.0/10,   1/10),
                                                     (0.7,       0.75): (0.25/10,  1.0/10),
                                                     (0.75,      0.8):  (0.5/10,   1.0/10),
                                                     (0.8,       0.85): (0.75/10,  1.0/10),
                                                     (0.85,      100):  (1.0/10,   1.0/10) }



    pos_dict['20240329_ic_ic_v7unifac_orig_norm2'] = { (0,         0.15): (0.0,       0.0),
                                                       (0.15,      0.25): (0.0/10,   0.5/10),
                                                       (0.25,      0.61): (0.0/10,   1/10),
                                                       (0.61,      0.67): (0.25/10,  1.0/10),
                                                       (0.67,      0.73): (0.5/10,   1.0/10),
                                                       (0.73,      0.8):  (0.75/10,  1.0/10),
                                                       (0.8,       100):  (1.0/10,   1.0/10) }
    
    pos_dict['20240329_if_if_v7c_orig'] = {(0,        0.1): (0.0,       0.0),
                    (0.1,       0.2):  (0.0/10,   0.5/10),
                    (0.2,       0.8):  (0.0/10,   1/10),
                    (0.8,       0.85): (0.25/10,  1.0/10),
                    (0.85,      0.9):  (0.5/10,   1.0/10),
                    (0.9,       0.95): (0.75/10,  1.0/10),
                    (0.95,      100):  (1.0/10,   1.0/10) }

    pos_dict['20240329_if_if_v7_crn'] = {(0,        0.1): (0.0,       0.0),
                    (0.1,       0.2):  (0.0/10,   0.5/10),
                    (0.2,       0.8):  (0.0/10,   1/10),
                    (0.8,       0.85): (0.25/10,  1.0/10),
                    (0.85,      0.9):  (0.5/10,   1.0/10),
                    (0.9,       0.95): (0.75/10,  1.0/10),
                    (0.95,      100):  (1.0/10,   1.0/10) }
    
    
    
    pos_dict['20240329_if_if_v7c_orig_norm2'] = { (0,         0.07): (0.0,       0.0),
                                                (0.07,      0.15):  (0.0/10,   0.5/10),
                                                (0.15,      0.61):  (0.0/10,   1/10),
                                                (0.61,       0.67): (0.25/10,  1.0/10),
                                                (0.67,      0.73):  (0.5/10,   1.0/10),
                                                (0.73,       0.8): (0.75/10,  1.0/10),
                                                (0.8,      100):  (1.0/10,   1.0/10) }

    pos_dict['20240329_if_if_v7_crn_norm2'] = { (0,         0.07): (0.0,       0.0),
                                                (0.07,      0.15):  (0.0/10,   0.5/10),
                                                (0.15,      0.7):  (0.0/10,   1/10),
                                                (0.7,       0.75): (0.25/10,  1.0/10),
                                                (0.75,      0.8):  (0.5/10,   1.0/10),
                                                (0.8,       0.85): (0.75/10,  1.0/10),
                                                (0.85,      100):  (1.0/10,   1.0/10) }
                                    
    
    pos_dict['20240329_im_im_v1unifac_crn'] = {(0,        0.1): (0.0,       0.0),
                    (0.1,       0.2):  (0.0/10,   0.5/10),
                    (0.2,       0.8):  (0.0/10,   1/10),
                    (0.8,       0.85): (0.25/10,  1.0/10),
                    (0.85,      0.9):  (0.5/10,   1.0/10),
                    (0.9,       0.95): (0.75/10,  1.0/10),
                    (0.95,      100):  (1.0/10,   1.0/10) }



    pos_dict['20240329_im_im_v1unifac_orig'] = {
                (0,    0.2):  (0,        0),
                (0.2,  0.3):  (0,        0.5/pos_divnum),
                (0.3,  0.8):  (0,        1/pos_divnum),
                (0.8,  0.85): (0.25/pos_divnum,   1/pos_divnum),
                (0.85, 0.9):  (0.5/pos_divnum,    1/pos_divnum),
                (0.9,  0.95): (0.75/pos_divnum,   1/pos_divnum),
                (0.95, 100):  (1/pos_divnum,      1/pos_divnum)}

    
    pos_dict['20240329_im_im_v1unifac_crn_norm2'] = { (0,         0.07): (0.0,       0.0),
                                                (0.07,      0.15):  (0.0/10,   0.5/10),
                                                (0.15,      0.73):  (0.0/10,   1/10),
                                                (0.73,       0.78): (0.25/10,  1.0/10),
                                                (0.78,      0.83):  (0.5/10,   1.0/10),
                                                (0.83,       0.88): (0.75/10,  1.0/10),
                                                (0.88,      100):  (1.0/10,   1.0/10) }



    pos_dict['20240329_im_im_v1unifac_orig_norm2'] = { (0,         0.15): (0.0,       0.0),
                                                        (0.15,      0.25):  (0.0/10,   0.5/10),
                                                        (0.25,      0.61):  (0.0/10,   1/10),
                                                        (0.61,       0.67): (0.25/10,  1.0/10),
                                                        (0.67,      0.73):  (0.5/10,   1.0/10),
                                                        (0.73,       0.8): (0.75/10,  1.0/10),
                                                        (0.8,      100):  (1.0/10,   1.0/10) }



    pos_dict['20240329_im_im_v1unifac_orig'] = {
                (0,   0.2): (0,        0),
                (0.2, 0.3): (0,        0.5/pos_divnum),
                (0.3, 0.8): (0,        1/pos_divnum),
                (0.8, 0.9): (0.5/pos_divnum,   1/pos_divnum),
                (0.9, 100): (1/pos_divnum,     1/pos_divnum)}
    
    
    log_file = '/data/group/800466/StrategyLog/prd/MobiusStrategy-%s.log' % (date)
    if not os.path.exists(log_file):
        with gzip.open('%s.gz' % log_file, 'rb') as f_in:
            with open(log_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)



    strategy_id_holder = []
    with open(log_file, "r") as f:
        line = f.readline()
        while line:
            for contract in contractl:
                if (contract[:-1] in line):#and ('-300-' in line):
                    stragety_id = line.split(' INFO')[0].split('[')[-1]
                    strategy_id_holder.append(stragety_id)
                line = f.readline()

    #stragety_id = strategy_id_holder[-1]
    for stragety_id2 in strategy_id_holder:
        if strat_ip in stragety_id2:
            stragety_id = stragety_id2
    print(stragety_id)
    
    
    # get_filter
    if filt_bool == True:
        result_list = []
        mapping_dict = {'raw':'ReCalculationFACTORVALUE','norm':'ReCalculationFACTORNORMALIZEVALUE'}
        
        fac_type = 'norm'
        factor_list = []
        factor_count = 0
        dt_list = []
        dt_count = 0
        values_list = []
        with open(log_file, "r") as f:
            line = f.readline()
            while line:
                if stragety_id in line:
                    if line.find("FactorInitSuccess:") != -1:
                        start = line.find("Factors=")
                        start += len("Factors=")
                        end = line.find(']', start)
                        factor_list = [elem.strip() for elem in line[start + 1:end].strip().split(",")]
                        factor_count = len(factor_list)
                    elif line.find("FactorManager - %s:" % mapping_dict[fac_type]) != -1:
                        d_start = line.find('TradeDate=')
                        d_start += len("TradeDate=")
                        day = line[d_start:d_start + 8]
                        try:
                            a = int(day)
                        except:
                            print(line)
    
                        t_start = line.find("TIMESTAMP=")
                        t_start += len("TIMESTAMP=")
                        t_end = line.find(" ", t_start)
                        timestamp = line[t_start:t_end]
                        if len(timestamp) == 5:
                            timestamp = '0' + timestamp
    
                        datetime_str = day + ' ' + timestamp
                        dt = datetime.datetime.strptime(datetime_str, '%Y%m%d %H%M%S')
                        dt_list.append(dt)
    
                        v_start = line.find("VALUE=")
                        v_start += len("VALUE=")
                        values = line.strip()[v_start + 1:-2].strip().split(',')
                        for value in values:
                            if value.strip():
                                values_list.append(float(value))
                            else:
                                values_list.append(np.nan)
    
                line = f.readline()
        dt_count = len(dt_list)
        values_list = np.array(values_list).reshape(dt_count, factor_count)
        new_df = pd.DataFrame(values_list, index=dt_list)
        new_df.columns = factor_list
        new_df.index.name = 'dt'
        xiufu_df = new_df.loc[~new_df.index.duplicated()].sort_index()
    
    
        factor_list = []
        factor_count = 0
        dt_list = []
        dt_count = 0
        values_list = []
        
        with open(log_file, "r") as f:
            line = f.readline()
            while line:
                if stragety_id in line:
                    if line.find("FactorInitSuccess:") != -1:
                        start = line.find("Factors=")
                        start += len("Factors=")
                        end = line.find(']', start)
                        factor_list = [elem.strip() for elem in line[start + 1:end].strip().split(",")]
                        factor_count = len(factor_list)
                    elif line.find("FactorManager - FACTORNORMALIZEVALUE:") != -1:
                        d_start = line.find('TradeDate=')
                        d_start += len("TradeDate=")
                        day = line[d_start:d_start + 8]
                        try:
                            a = int(day)
                        except:
                            print(line)
        
                        t_start = line.find("TIMESTAMP=")
                        t_start += len("TIMESTAMP=")
                        t_end = line.find(" ", t_start)
                        timestamp = line[t_start:t_end]
                        if len(timestamp) == 5:
                            timestamp = '0' + timestamp
        
                        datetime_str = day + ' ' + timestamp
                        dt = datetime.datetime.strptime(datetime_str, '%Y%m%d %H%M%S')
                        dt_list.append(dt)
        
                        v_start = line.find("VALUE=")
                        v_start += len("VALUE=")
                        values = line.strip()[v_start + 1:-2].strip().split(',')
                        for value in values:
                            if value.strip():
                                values_list.append(float(value))
                            else:
                                values_list.append(np.nan)
        
                line = f.readline()
        dt_count = len(dt_list)
        values_list = np.array(values_list).reshape(dt_count, factor_count)
        new_df = pd.DataFrame(values_list, index=dt_list)
        new_df.columns = factor_list
        new_df.index.name = 'dt'
        norm_df = new_df.loc[~new_df.index.duplicated()].sort_index()
        
    
        norm_df.loc[xiufu_df.index] = xiufu_df
        filter_trade1 = norm_df[filt_name + trail]
        filter_research1 = pd.read_hdf('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/%s_filters/minute_norm/%s.h5'%(ticker.split('.')[0], filt_name + trail))
        filter_trade = (filter_trade1 > filter_bar)
        filter_research = (filter_research1 > filter_bar)
    
    def get_line(line, print_flag = False):
        linesplit = line.split(';')
        signal = []
        rawsignal = []
        coef = []
        planQty = []
        changeside = []
        targetminmax = []
        availablePosition = []
        unfinished = []
        for i in range(len(linesplit)-1):
            xline = linesplit[i]
            signal.append(float(xline.split('signal=')[-1].split(',')[0]))
            rawsignal.append(float(xline.split('rawSignal=')[-1].split(',')[0]))
            coef.append(float(xline.split('coef=')[-1].split(',')[0]))
            planQty.append(int(float(xline.split('planQty=')[-1].split(',')[0])))
            changeside.append(xline.split('changeSie=')[-1].split(',')[0])
            targetminmax.append([int(float(xline.split('targetMin=')[-1].split(',')[0])), int(float(xline.split('targetMax=')[-1].split(',')[0]))])
            availablePosition.append(int(float(xline.split('availablePosition=')[-1].split(',')[0])))
            unfinished.append(int(float(xline.split('unfinished=')[-1].split(',')[0])))

        xline = linesplit[-1]
        strategyNetPosition = int(float(xline.split('strategyNetPosition=')[-1].split(',')[0]))
        strategyUnfinished = [int(float(xline.split('strategyUnfinished=')[-1].split(',')[0])),int(float(xline.split('longUnFinishedQty=')[-1].split(',')[0])),int(float(xline.split('shortUnFinishedQty=')[-1].split(',')[0]))]
        availablelongshortPosition = [int(float(xline.split('availableLongPosition=')[-1].split(',')[0])),int(float(xline.split('availableShortPosition=')[-1].split(',')[0]))]
        plannedOrderQty=None
        if 'NeedTrade=True' in xline:
            plannedOrderQty = int(float(xline.split('plannedOrderQty=')[-1].split(',')[0]))

        beginTime = linesplit[-1].split('beginTime=')[-1].split(',')[0]
        if print_flag:
            print(' ')
            print('beginTime:', beginTime)
            print('signal',signal)
            print('availablePosition',availablePosition)
            print('targetminmax',targetminmax)
            print('planQty',planQty)
            print('changeside',changeside)
            print('unfinished',unfinished)
            print('**********')
            print('strategyNetPosition',strategyNetPosition)
            print('strategyUnfinished',strategyUnfinished)
            print('availablelongshortPosition',availablelongshortPosition)
            print('plannedOrderQty',plannedOrderQty)
            print(' ')
            signal.append(beginTime)
        return signal,rawsignal,coef,beginTime, unfinished

    def get_recal_line(line):
        linesplit = line.split(';')
        signal = []
        rawsignal = []
        coef = []
        planQty = []
        changeside = []
        targetminmax = []
        availablePosition = []
        unfinished = []
        for i in range(len(linesplit)-1):
            xline = linesplit[i]
            signal.append(float(xline.split('signal=')[-1].split(',')[0]))
            rawsignal.append(float(xline.split('rawSignal=')[-1].split(',')[0]))
            coef.append(float(xline.split('coef=')[-1].split(',')[0]))

        return signal,rawsignal,coef,dt

    def get_deal_vol_per_sig2(deal_vol, need_trade_num_persig):
        if deal_vol == 0:
            return [0] * len(need_trade_num_persig)
        #assert 0 < deal_vol / np.sum(need_trade_num_persig) <= 1
        deal_vol_per_sig = []
        close_num = 0
        open_list = []
        open_index_list = []
        for i in range(len(need_trade_num_persig)):
            x = need_trade_num_persig[i]
            if np.sign(deal_vol) * np.sign(x) <= 0:
                deal_vol_per_sig.append(x)
                close_num += x
            else:
                open_list.append(x)
                open_index_list.append(i)
                deal_vol_per_sig.append('wait')

        deal_vol2 = deal_vol - close_num

        total_open_num = np.sum(open_list)
        if deal_vol2 > 0:
            open_allocate_list = [np.floor(deal_vol2 * x / total_open_num) for x in open_list]
            open_allocate_list[np.argmax(open_allocate_list)] = open_allocate_list[np.argmax(open_allocate_list)] + (deal_vol2 - np.sum(open_allocate_list))
        else:
            open_allocate_list = [np.ceil(deal_vol2 * x / total_open_num) for x in open_list]
            open_allocate_list[np.argmin(open_allocate_list)] = open_allocate_list[np.argmin(open_allocate_list)] + (deal_vol2 - np.sum(open_allocate_list))

        for i in range(len(open_list)):
            deal_vol_per_sig[open_index_list[i]] = open_allocate_list[i]
        assert np.sum(deal_vol_per_sig) == deal_vol
        return deal_vol_per_sig


    def check_fenpei(line):
        ssline = line.split('totalTradeQty=')[-1].split(',')
        totalTradeQty = int(float(ssline[0]))
        dlist = []
        tlist = []
        for i in range(1, len(ssline) - 1):
            dlist.append(int(float(ssline[i].split('=')[1].split(' ')[0])))
            tlist.append(int(float(ssline[i].split('=')[-1])))
        #print(get_deal_vol_per_sig2(totalTradeQty, tlist))
        #print(dlist)
        #assert get_deal_vol_per_sig2(totalTradeQty, tlist) == dlist
        return dlist
    #     print('&&&&&&&&&&&&&&&&&&',line.split(' ')[0],totalTradeQty, tlist, dlist)

    t = []
    with open(log_file, "r") as f:
        line = f.readline()
        count = 1
        signal_list = []
        while line:
            if stragety_id in line:
                if 'PlaceTradeQty' in line:
                    if 'planTime=' not in line:
                        temp_time = line[:19].split('T')
                        temp_time1 = temp_time[0] +  ' ' + temp_time[1]
                        temp_time1 = temp_time1[:-2] + '00'
                        temp_time1 = pd.to_datetime(temp_time1)
                        temp_time1 = temp_time1 - relativedelta(minutes = 1)
                        t.append([temp_time1] + check_fenpei(line))
                if 'NeedTrade=' in line:
                    temp_time = line[:19].split('T')
                    temp_time1 = temp_time[0] +  ' ' + temp_time[1]
                    temp_time1 = temp_time1[:-2] + '00'
                    temp_time1 = pd.to_datetime(temp_time1)
                    temp_time1 = temp_time1 - relativedelta(minutes = 1)
    #                 print('&&&&&&&&&&&',line.split(' ')[0])
                    signal_list.append(get_line(line))
    #                 print(line)
    #                 print(line.split(' - ')[-1])
                if 'NormalPlaceOrderSuccess' in line:
                    symbol = line.split('symbol=')[-1].split(', price')[0]
                    direction = line.split('side=')[-1].split(', positionEffect')[0] + line.split('positionEffect=')[-1].split(', tickPrice')[0]
                    time = line.split('tickTime=')[-1].split('.')[0]
                    #print(time, symbol, direction, count)
                    count += 1
            line = f.readline()
    sig_trade_df = pd.DataFrame(t, columns = ['dt'] + model_date_list).set_index('dt')


    model_num = [i+1 for i in range(len(model_date_list))]

    import bottleneck as bk
    def ts_std(data, d):
        # moving time-series rank for the past d periods
        if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
            raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
        if d == 1:
            output = data
        else:
            if isinstance(data, np.ndarray):
                output = bk.move_std(data, window=d, min_count=int(d / 2), axis=0, ddof=1)
            if isinstance(data, pd.DataFrame):
                output = pd.DataFrame(bk.move_std(data, window=d, min_count=int(d / 2), axis=0, ddof=1),
                                      index=data.index, columns=data.columns)
            elif isinstance(data, pd.Series):
                output = pd.Series(bk.move_std(data, window=d, min_count=int(d / 2), axis=0, ddof=1),
                                   index=data.index, name=data.name)
        return output

    def get_line(line, print_flag = False):
        linesplit = line.split(';')
        signal = []
        rawsignal = []
        coef = []
        planQty = []
        changeside = []
        targetminmax = []
        availablePosition = []
        unfinished = []
        for i in range(len(linesplit)-1):
            xline = linesplit[i]
            signal.append(float(xline.split('signal=')[-1].split(',')[0]))
            rawsignal.append(float(xline.split('rawSignal=')[-1].split(',')[0]))
            coef.append(float(xline.split('coef=')[-1].split(',')[0]))
            planQty.append(int(float(xline.split('planQty=')[-1].split(',')[0])))
            changeside.append(xline.split('changeSie=')[-1].split(',')[0])
            targetminmax.append([int(float(xline.split('targetMin=')[-1].split(',')[0])), int(float(xline.split('targetMax=')[-1].split(',')[0]))])
            availablePosition.append(int(float(xline.split('availablePosition=')[-1].split(',')[0])))
            unfinished.append(int(float(xline.split('unfinished=')[-1].split(',')[0])))

        xline = linesplit[-1]
        strategyNetPosition = int(float(xline.split('strategyNetPosition=')[-1].split(',')[0]))
        strategyUnfinished = [int(float(xline.split('strategyUnfinished=')[-1].split(',')[0])),int(float(xline.split('longUnFinishedQty=')[-1].split(',')[0])),int(float(xline.split('shortUnFinishedQty=')[-1].split(',')[0]))]
        availablelongshortPosition = [int(float(xline.split('availableLongPosition=')[-1].split(',')[0])),int(float(xline.split('availableShortPosition=')[-1].split(',')[0]))]
        plannedOrderQty=None
        if 'NeedTrade=True' in xline:
            plannedOrderQty = int(float(xline.split('plannedOrderQty=')[-1].split(',')[0]))

        beginTime = linesplit[-1].split('beginTime=')[-1].split(',')[0]
        if print_flag:
            print(' ')
            print('beginTime:', beginTime)
            print('signal',signal)
            print('availablePosition',availablePosition)
            print('targetminmax',targetminmax)
            print('planQty',planQty)
            print('changeside',changeside)
            print('unfinished',unfinished)
            print('**********')
            print('strategyNetPosition',strategyNetPosition)
            print('strategyUnfinished',strategyUnfinished)
            print('availablelongshortPosition',availablelongshortPosition)
            print('plannedOrderQty',plannedOrderQty)
            print(' ')
            signal.append(beginTime)
        return signal,rawsignal,coef,beginTime

    def get_recal_line(line):
        signal = []
        rawsignal = []
        coef = []

        dt = line.split('time=')[-1].split(',')[0]
        linesplit = line.split('[')[-1].split(']')[0].split(';')
        for i in range(len(linesplit)-1):
            xline = linesplit[i]
            signal.append(float(xline.split('signal=')[-1].split(',')[0]))
            rawsignal.append(float(xline.split('rawSignal=')[-1].split(',')[0]))
            coef.append(float(xline.split('coef=')[-1].split('rawSignal')[0]))

        return signal,rawsignal,coef,dt

    signal_list = []
    rawsignal_list = []
    coef_list = []
    dt_list = []

    re_signal_list = []
    re_rawsignal_list = []
    re_coef_list = []
    re_dt_list = []

    with open(log_file, "r") as f:
        line = f.readline()
        while line:
            if stragety_id in line:
                if (line.find("Generated new tradePlan") != -1):
                    try:
                        signal,rawsignal,coef,dt = get_line(line, print_flag=False)
                        signal_list.append(signal)
                        rawsignal_list.append(rawsignal)
                        coef_list.append(coef)
                        dt_list.append(dt)
                    except Exception as e:
                        print(line, e)
                elif (line.find("RePredict: ") != -1):
                    try:
                        signal,rawsignal,coef,dt = get_recal_line(line)
                        re_signal_list.append(signal)
                        re_rawsignal_list.append(rawsignal)
                        re_coef_list.append(coef)
                        re_dt_list.append(dt)
                    except Exception as e:
                        print(line, e)
            line = f.readline()


    dt_index = [pd.to_datetime((pd.to_datetime(x)-datetime.timedelta(minutes=1)).strftime('%Y%m%d %H:%M:%S')) for x in dt_list]
    if dt_index[115].hour == 12:
        dt_index[115] = pd.Timestamp(date + ' 112900')
    signal_df = pd.DataFrame(signal_list, columns = ['signal%s_java_%s' % (model_num[x],model_date_list[x]) for x in range(len(model_date_list))], index=dt_index)
    rawsignal_df = pd.DataFrame(rawsignal_list, columns = ['rawsignal%s_java_%s' % (model_num[x],model_date_list[x]) for x in range(len(model_date_list))], index=dt_index)
    coef_df = pd.DataFrame(coef_list, columns = ['std%s_java_%s' % (model_num[x],model_date_list[x]) for x in range(len(model_date_list))], index=dt_index)
    log_df = pd.concat([signal_df,rawsignal_df, coef_df], axis = 1)
    log_df.index.name = 'dt'

    re_dt_index = [pd.to_datetime((pd.to_datetime(x)).strftime('%Y%m%d %H:%M:%S')) for x in re_dt_list]

    re_signal_df = pd.DataFrame(re_signal_list, columns = ['signal%s_java_%s' % (model_num[x],model_date_list[x]) for x in range(len(model_date_list))], index=re_dt_index)
    re_rawsignal_df = pd.DataFrame(re_rawsignal_list, columns = ['rawsignal%s_java_%s' % (model_num[x],model_date_list[x]) for x in range(len(model_date_list))], index=re_dt_index)
    re_coef_df = pd.DataFrame(re_coef_list, columns = ['std%s_java_%s' % (model_num[x],model_date_list[x]) for x in range(len(model_date_list))], index=re_dt_index)
    re_log_df = pd.concat([re_signal_df,re_rawsignal_df, re_coef_df], axis = 1)
    re_log_df.index.name = 'dt'

    log_df = log_df.reindex(set(log_df.index) - set(re_log_df.index)).append(re_log_df).sort_index()
    if 'IM' not in ticker.upper():
        a = IO.read_data([20210101,date.replace('-','')+'235959'], columns = ['close'], alt = '/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_FUTURES/MINUTE/%s_MINUTE.h5' % ticker[:2])
    else:
        a = IO.read_data([20210101,date.replace('-','')+'235959'], columns = ['close'], alt = '/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_FUTURES/MINUTE/backup/%s_MINUTE.h5' % ticker[:2])
    recent_future = IO.read_data([date.replace('-', '')], alt = '/data/group/800466/warehouse/prod/MD/MarketData/MD/UNIVERSE/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
    recent_future = recent_future.xs(ticker, level = 1)['contract_00'].tolist()[0][:-1] + 'E'
    print(recent_future)
    #recent_future = [item for item in list(para['合约代码'])][0] + 'E'

    a = a.xs(recent_future, level = 1).between_time('930','1456').sort_index()
    a = ts_std(a.pct_change(),30).loc[date.replace('-','')]
    a.columns = ['std_python']

    python_model = [log_df, a]
    for i in range(len(model_date_list)):
        model_date1 = model_date_list[i]
        model_date = model_date1.replace('_norm2', '') 
        if 'norm2' in model_date1:
            try:
                b = pd.read_pickle('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/%s/model_value/model_norm2/%s/pred_comb2.pkl' % (str(model_date), date.replace('-','')))
            except:
                temp_model_date = model_date.split('_orig')[0]
                b = pd.read_pickle('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/%s/model_value/model_norm2/%s/pred_comb2.pkl' % (str(temp_model_date), date.replace('-','')))
        else:
              
            try:
                b = pd.read_pickle('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/%s/model_value/model_norm/%s/pred_comb2.pkl' % (str(model_date), date.replace('-','')))
            except:
                temp_model_date = model_date.split('_orig')[0]
                b = pd.read_pickle('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/%s/model_value/model_norm/%s/pred_comb2.pkl' % (str(temp_model_date), date.replace('-','')))
        if 'norm2' not in model_date1:
            if 'crn' not in model_date:
                b = b * 2 - 1
        b = b.loc[date].to_frame()
        b.columns = ['rawsignal%s_python_%s' % (model_num[i], model_date1)]
        python_model.append(b)
    result = pd.concat(python_model, axis = 1)

    for i in range(len(model_date_list)):
        model_date = model_date_list[i]
        if ('orig' in model_date) or ('short' in model_date) or ('unifac' in model_date and '_orig' in model_date) or ('if_v7c' in model_date and '_orig' in model_date) or ('crn' in model_date and '_adj' not in model_date):
            result['signal%s_python_%s'%(model_num[i],model_date)] = result['rawsignal%s_python_%s'%(model_num[i],model_date)]

        else:
            result['signal%s_python_%s'%(model_num[i],model_date)] = result['rawsignal%s_python_%s'%(model_num[i],model_date)] * result['std_python']


    df_all = []
    pos_list = []
    cash_list = []

    for i, model_name in enumerate(model_date_list):
        #model_name = model_name1.replace('_norm2', '')
        signal = result['signal%s_java_'%str(i+1) + model_name]
        df_all.append(signal)
        signal_list1 = [{'signal':signal,'pos_dict':pos_dict[model_name],'cash':cash_dict[model_name]}]
        pos_list.append(pos_dict[model_name])
        cash_list.append(cash_dict[model_name])

        start_date = int(date.replace('-',''))
        end_date = int(date.replace('-',''))
        signal_name = '%s_sim4' % str.lower(ticker[:2])
        date_suffix = ''

        today = date.replace('-', '')
        save_root_path = '/data/group/800466/warehouse/prod/tradingstats/Mobius/tracking/back_test/%s/%s/%s' % (today, ticker[:2], model_name)
        name_prefix = '_all'
        save_path = save_root_path

        ts = TS_BACK_TEST(signal_list1, save_signal_list = True, c_rate=2.4 / 100000, ticker = ticker, stop_loss = -0.005,tickslippage = slip, max_wait_tick_num = 2,
                              closing_start_time = [14,45],start_date=start_date, end_date=end_date, save_path=save_path, name_prefix=name_prefix,
                              filter_series = filter_trade, filter_open = True, filter_close = False)
        Aabgc = ts.back_test()
    # signal4 = result['signal4_java_20220415_ic']
    #signal_list1 = [{'signal':signal1,'pos_dict':pos_dict1,'cash':3e8}, {'signal':signal2,'pos_dict':pos_dict2,'cash':2e8}, {'signal':signal3,'pos_dict':pos_dict3,'cash':1e8}]
    #signal_list1 = [{'signal':signal1,'pos_dict':pos_dict1,'cash':3e8}]


    signal_list1 = []
    for i, signal in enumerate(df_all):
        signal_list1.append({'signal':signal,'pos_dict':pos_list[i],'cash':cash_list[i]})

    start_date = int(date.replace('-',''))
    end_date = int(date.replace('-',''))
    date_suffix = ''

    today = date.replace('-', '')
    save_root_path = '/data/group/800466/warehouse/prod/tradingstats/Mobius/tracking/back_test/%s/%s/CONCAT/' % (today, ticker[:2])
    name_prefix = '_all'
    save_path = save_root_path

    ts = TS_BACK_TEST(signal_list1, save_signal_list = True, c_rate=2.4 / 100000, ticker = ticker, stop_loss = -0.005,tickslippage = slip, max_wait_tick_num = 2,
                          closing_start_time = [14,45],start_date=start_date, end_date=end_date, save_path=save_path, name_prefix=name_prefix,
                          filter_series = filter_trade, filter_open = True, filter_close = False)
    wwccd = ts.back_test()

    df_all = []
    pos_list = []
    cash_list = []

    for i, model_name in enumerate(model_date_list):
        if ('short' in model_name.lower()) or ('raw' in model_name.lower()):
            signal = result['rawsignal%s_python_'%str(i+1) + model_name]
        else:
            signal = result['signal%s_python_'%str(i+1) + model_name]
        df_all.append(signal)
        signal_list1 = [{'signal':signal,'pos_dict':pos_dict[model_name],'cash':cash_dict[model_name]}]
        pos_list.append(pos_dict[model_name])
        cash_list.append(cash_dict[model_name])

        start_date = int(date.replace('-',''))
        end_date = int(date.replace('-',''))
        signal_name = '%s_sim4' % str.lower(ticker[:2])
        date_suffix = ''

        today = date.replace('-', '')
        save_root_path = '/data/group/800466/warehouse/prod/tradingstats/Mobius/tracking/back_test/%s/%s/%s' % (today, ticker[:2], model_name + '_research')
        name_prefix = '_all'
        save_path = save_root_path

        ts = TS_BACK_TEST(signal_list1, save_signal_list = True, c_rate=2.4 / 100000, ticker = ticker, stop_loss = -0.005,tickslippage = slip, max_wait_tick_num = 2,
                              closing_start_time = [14,45],start_date=start_date, end_date=end_date, save_path=save_path, name_prefix=name_prefix,
                              filter_series = filter_research, filter_open = True, filter_close = False)
        Aabgc = ts.back_test()


    signal_list1 = []
    for i, signal in enumerate(df_all):
        signal_list1.append({'signal':signal,'pos_dict':pos_list[i],'cash':cash_list[i]})

    start_date = int(date.replace('-',''))
    end_date = int(date.replace('-',''))
    date_suffix = ''

    today = date.replace('-', '')
    save_root_path = '/data/group/800466/warehouse/prod/tradingstats/Mobius/tracking/back_test/%s/%s/CONCAT_research/' % (today, ticker[:2])
    name_prefix = '_all'
    save_path = save_root_path

    ts = TS_BACK_TEST(signal_list1, save_signal_list = True, c_rate=2.4 / 100000, ticker = ticker, stop_loss = -0.005,tickslippage = slip, max_wait_tick_num = 2,
                          closing_start_time = [14,45],start_date=start_date, end_date=end_date, save_path=save_path, name_prefix=name_prefix,
                          filter_series = filter_research, filter_open = True, filter_close = False)
    wwccd = ts.back_test()


    holder = [] 
    for file in model_date_list:
        if ('CONCAT'not in str(file).upper()):
            try:
                temp = pd.read_csv('/data/group/800466/warehouse/prod/tradingstats/Mobius/tracking/back_test/%s/%s/' % (today, ticker[:2]) + file + '/' + '_all_daily_return.csv')
                pnl = (temp['daily_return'].iloc[-1])
                cash = cash_dict[file]
                #print(file, pnl)
                holder.append(pnl * cash)
            except:
                holder.append(0)
        if ('CONCAT' in str(file).upper()):
            try:
                temp1 = pd.read_csv('/data/group/800466/warehouse/prod/tradingstats/Mobius/tracking/back_test/%s/%s/' % (today, ticker[:2]) + file + '/' + '_all_daily_return.csv')
                pnl1 = (temp1['daily_return'].iloc[-1])
                cash1 = np.nansum(cash_list)
                pnl_all = cash1 * pnl1
            except:
                holder.append(0)

    profit_divide = pd.DataFrame(holder, index = model_date_list, columns = ['back_test_pnl'])

    b = date.replace('-', '')
    para = pd.read_excel('/data/user/016700/Data/para/Mobius_%s/MobiusStrategy_%s.xlsx'%(str(b).replace('-', ''), ticker[:2] + '_'+ str(b).replace('-', '') + machine), sheet_name = '期初持仓列表')
    future_traded = [item[:-3] for item in list(para['合约代码'])]
    trading_stats = pd.read_excel('/data/user/011477/order/O32/51606/综合信息查询_成交回报明细_%s_51606.xls'%b)
    trading_stats = trading_stats.loc[trading_stats['日期'].isna() == False]
    trading_stats['成交时间1'] = pd.to_datetime(trading_stats['成交时间'].apply(lambda x: (b + str(x).replace(':', ''))[:-2]))
    future_traded = list(set(list(trading_stats['证券代码'])))
    future_traded = [item for item in future_traded if ticker[:2] in item.upper()]
    #trading_stats = trading_stats[(trading_stats['证券代码'].isin(future_traded))&(trading_stats['组合编号'] == 5160604) & (trading_stats['成交时间1'] >= pd.to_datetime(b + '0939')) & (trading_stats['成交时间1'] <= pd.to_datetime(b + '1450'))].sort_values(by = '成交时间')
    #trading_stats = trading_stats[(trading_stats['证券代码'].isin(future_traded))&(trading_stats['组合编号'].isin([5160701])) & (trading_stats['成交时间1'] >= pd.to_datetime(b + '0939')) & (trading_stats['成交时间1'] <= pd.to_datetime(b + '1450'))].sort_values(by = '成交时间')
    trading_stats = trading_stats[(trading_stats['组合编号'].isin([5160701, 5160702])) & (trading_stats['成交时间1'] >= pd.to_datetime(b + '0939')) & (trading_stats['成交时间1'] <= pd.to_datetime(b + '1450'))].sort_values(by = '成交时间')
    
    ddata = pd.read_hdf('/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_SIF_TICK_TO_DAILY_ALL_CONTRACT.h5').reset_index().set_index('dt')
    ddata.Ticker = ddata.Ticker.apply(lambda x: x[:-4])
    settle = ddata[ddata.Ticker.isin(future_traded)].loc[date, ['Ticker', 'settle']]

    try:
        trading_stats['发生金额(全价)'] = trading_stats['发生金额(全价)'].apply(lambda x:float(x.replace(',', '')))
        print('#')
    except:
        pass

    if len(np.shape(settle)) == 1:
        settle = settle.to_frame().T

    yesterday = str(udt.get_trading_day_offset(b, -1)[0])[:10].replace('-','')
    settle_yesterday = ddata[ddata.Ticker.isin(future_traded)].loc[yesterday, ['Ticker', 'settle']]

    if len(np.shape(settle_yesterday)) == 1:
        settle_yesterday = settle_yesterday.to_frame().T

    tomorrow = str(udt.get_trading_day_offset(b, 1)[0])[:10].replace('-','')
    para_tomorrow = pd.read_excel('/data/user/016700/Data/para/Mobius_%s/MobiusStrategy_%s.xlsx'%(str(tomorrow).replace('-', ''), ticker[:2] + '_'+ str(tomorrow).replace('-', '')+ machine) , sheet_name = '期初持仓列表')
    li_con = set(para['合约代码']) - set(para_tomorrow['合约代码']) 

    if len(li_con) != 0:
        temp_roww = pd.DataFrame([list(li_con)[0], 1, 0, 0], index = para_tomorrow.columns).T
        para_tomorrow['平仓优先级'] = para_tomorrow['平仓优先级'] + 1 
        para_tomorrow = pd.concat([para_tomorrow, temp_roww])
        para_tomorrow = para_tomorrow.sort_values(by = '平仓优先级')
    
    dfff = pd.read_excel('/data/user/011477/order/tradingReport/tradingStat_%s.xlsx'%yesterday, sheet_name='Tri_51606')#.set_index('委托方向')
    l = dfff['组合名称']
    l = [item for item in l if ('5160702' in item)][0]
    positions = dfff[dfff['组合名称'] == l]['期货持仓'].iloc[0]
    dic_temp = json.loads(positions.replace("'", '"'))

    dffff = pd.read_excel('/data/user/011477/order/tradingReport/tradingStat_%s.xlsx'%b, sheet_name='Tri_51606')#.set_index('委托方向')
    l = dffff['组合名称']
    l = [item for item in l if  (('5160702' in item))][0]
    positions_new = dffff[dffff['组合名称'] == l]['期货持仓'].iloc[0]
    dic_temp_new = json.loads(positions_new.replace("'", '"'))
    contract_temp_list = list(set(list(dic_temp_new.keys())))
    contract_temp_list = [item for item in contract_temp_list if ticker[:2] in item]

    df_para_tomorrow = pd.DataFrame(index = list(set([item[:-2]  for item in contract_temp_list])), columns = ['多头持仓','空头持仓'])
    for key in contract_temp_list:
        contract_name = key[:-2] 
        if ticker[:2] in contract_name:
            print(contract_name)
            if '多' in key:            
                df_para_tomorrow.loc[contract_name, '多头持仓'] = dic_temp_new[key]
            if '空' in key:
                df_para_tomorrow.loc[contract_name, '空头持仓'] = dic_temp_new[key]
    df_para_tomorrow = df_para_tomorrow.sort_index()


    df_para = pd.DataFrame(index = list(set([item[:-2] for item in contract_temp_list])), columns = ['多头持仓','空头持仓'])
    for key in contract_temp_list:
        contract_name = key[:-2]
        if ticker[:2] in contract_name:
            print(contract_name)
            if key in dic_temp.keys():
                if '多' in key:            
                    df_para.loc[contract_name, '多头持仓'] = dic_temp[key]
                if '空' in key:
                    df_para.loc[contract_name, '空头持仓'] = dic_temp[key]
            else:
                if '多' in key:            
                    df_para.loc[contract_name, '多头持仓'] = 0
                if '空' in key:
                    df_para.loc[contract_name, '空头持仓'] = 0
    df_para = df_para.sort_index()
    yesterday_spread = (df_para['多头持仓'] - df_para['空头持仓']) * settle_yesterday.set_index('Ticker')['settle'] * multiplier
    today_spread = (df_para_tomorrow['多头持仓'] - df_para_tomorrow['空头持仓']) * settle.set_index('Ticker')['settle'] * multiplier
    pairs_profit = (today_spread - yesterday_spread).sum()
    pnl_bf = (trading_stats['发生金额(全价)']).sum()

    tc = (trading_stats['成交数量'] * trading_stats['成交价格'] * multiplier * 0.00002323).sum()
    pnl = pnl_bf - tc + pairs_profit


    df = pd.DataFrame()
    df['成交时间'] = trading_stats['成交时间']
    df['合约'] = trading_stats['证券名称']
    df['成交价'] = trading_stats['成交价格']
    df['成交量'] = trading_stats['成交数量']
    df['发生金额'] = trading_stats['发生金额(全价)']
    df['委托方向'] = trading_stats['委托方向']
    df = df.set_index('成交时间')
    df['交易费用'] = df['成交量'] * df['成交价'] * multiplier * 0.00002323
    #df.to_excel('/data/group/800466/warehouse/prod/tradingstats/Mobius/log_%s.xlsx'%b)

    pnl_df = pd.DataFrame()
    pnl_df['date'] = [datetime.datetime.strptime(str(b),"%Y%m%d")]
    pnl_df['pnl'] = [pnl]
    pnl_df = pnl_df.set_index('date')
    pnl_df['transaction_cost'] = tc
    pnl_df['contracts_traded'] = trading_stats[trading_stats['委托方向'].isin(['买入平仓', '买入开仓'])]['成交数量'].sum()
    pnl_df['单边金额总数（买入）'] = abs(trading_stats[trading_stats['委托方向'].isin(['买入平仓', '买入开仓'])]['发生金额(全价)'].sum())
    pnl_df_fh = pd.read_excel('/data/group/800466/warehouse/prod/tradingstats/Mobius/pnl%s.xlsx'%trail, index_col = 0, date_parser = True)
    if 'contracts_traded' not in pnl_df.columns:
        pnl_df['contracts_traded'] = np.nan
        pnl_df['单边金额总数（买入）'] = np.nan

    tempdf = pd.concat([pnl_df_fh, pnl_df]).sort_index()#.to_excel('/data/group/800466/warehouse/prod/tradingstats/Mobius/pnl.xlsx')
    tempdf = tempdf[~tempdf.index.duplicated(keep='last')]
    #tempdf.to_excel('/data/group/800466/warehouse/prod/tradingstats/Mobius/pnl%s.xlsx'%trail)
    try:
        a = df.copy().reset_index()#.set_index('成交时间')
        a['dt'] = pd.to_datetime(a['成交时间'].apply(lambda x: '%s '%trading_stats['日期'].iloc[0] + x[:-2] + '00'))
        a = a.set_index('dt')
        order_price = np.sign(a['发生金额']).groupby(a.index).apply(lambda x:x.mode()).reset_index().set_index('dt')['发生金额'] * abs(a['成交价'].groupby(a['成交价'].index).mean())
        contract = a['合约'].iloc[0]+'.CFE'
        if 'IM' not in ticker.upper():
            twap = pd.read_hdf('/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_FUTURES/MINUTE/%s_MINUTE.h5'%ticker[:2])['twap']
        else:
            twap = pd.read_hdf('/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_FUTURES/MINUTE/backup/%s_MINUTE.h5'%ticker[:2])['twap']
        twap = twap.xs(contract, level = 1).loc[trading_stats['日期'].iloc[0]]

    

        comparison1 = pd.concat([order_price, twap.loc[order_price.index] ], axis = 1)
        comparison1.columns = ['actual', 'twap']
        comparison1.twap * np.sign(comparison1.actual)

        order_stats = pd.concat([comparison1.actual, comparison1.twap * np.sign(comparison1.actual), a['成交价'].groupby(a.index).count()], axis = 1)
        order_stats.columns = ['directional_deal_price', 'directional_twap', 'deal_counts']
        order_stats['transaction_cost_by_points'] = ((comparison1.twap * np.sign(comparison1.actual) - comparison1.actual)*a['成交价'].groupby(a.index).count()).sum()/(len(a))
    except:
        order_stats = pd.DataFrame()
    
    try:
        bt = pd.read_csv('/data/group/800466/warehouse/prod/tradingstats/Mobius/tracking/back_test/%s/%s/CONCAT/_all_minute_trade_detail.csv'% (today, ticker[:2])).loc[:, ['deal_time','dealflag', 'deal_weighted_price_close', 'deal_weighted_price_open', 'deal_contract_num']].set_index('deal_time')
        bt['deal_weighted_price'] = pd.concat([bt['deal_weighted_price_close'], bt['deal_weighted_price_open']], axis = 1).mean(axis = 1)
        bt.index.name = 'dt'
        bt.index = pd.to_datetime(bt.index)
        d = {'Bo': -1, 'Sc': 1, 'Bc': -1, 'So': -1, 'B':1, 'S':1, 'no_direction':0}
        bt['sign'] = bt['dealflag'].apply(lambda x: d[x])

        order_stats3 = pd.concat([abs(order_stats['directional_deal_price']), -np.sign(order_stats['directional_deal_price']) * order_stats['deal_counts'], (bt['deal_weighted_price']), (bt['deal_contract_num'])], axis = 1)
        order_stats3.columns = [ 'deal_price_trade', 'deal_counts_trade', 'deal_price_backtest', 'deal_counts_backtest']

        tttemp = pd.concat([bt['deal_weighted_price'] * bt['sign'], bt['deal_contract_num']], axis = 1)
        tttemp.columns = ['deal_weighted_price', 'deal_contract_num']
        sell = tttemp.loc[tttemp.deal_weighted_price > 0]
        buy = tttemp.loc[tttemp.deal_weighted_price < 0]

        order_stats3['backtest_minus_trade'] = -(-(order_stats3['deal_price_trade'] * order_stats3['deal_counts_trade']).sum() + \
                                            (order_stats3['deal_price_backtest'] * order_stats3['deal_counts_backtest']).sum()) * multiplier
        order_stats3['backtest_minus_trade'].iloc[1:] = np.nan
    except:
        order_stats3 = pd.DataFrame()
    
    try:
        bt_r = pd.read_csv('/data/group/800466/warehouse/prod/tradingstats/Mobius/tracking/back_test/%s/%s/CONCAT/_all_minute_trade_detail.csv'% (today, ticker[:2])).loc[:, ['deal_time','dealflag',  'deal_weighted_price_close', 'deal_weighted_price_open', 'deal_contract_num']].set_index('deal_time')
        bt_r.index.name = 'dt'
        bt_r.index = pd.to_datetime(bt_r.index)
        bt_r['deal_weighted_price'] = pd.concat([bt_r['deal_weighted_price_close'], bt_r['deal_weighted_price_open']], axis = 1).mean(axis = 1)
        bt_r['sign'] = bt_r['dealflag'].apply(lambda x: d[x])
        order_stats4 = pd.concat([(bt['deal_weighted_price'] * bt['sign']), bt['deal_contract_num'], (bt_r['deal_weighted_price'] * bt_r['sign']), bt_r['deal_contract_num']], axis = 1)
        order_stats4.columns = [ 'trade_backtest_price', 'trade_backtest_count', 'research_backtest_price', 'research_backtest_count']
        order_stats4['research_minus_trade_in_backtest'] =  - ((order_stats4['research_backtest_price'] * order_stats4['research_backtest_count']).sum() - \
                                            (order_stats4['trade_backtest_price'] * order_stats4['trade_backtest_count']).sum()) * multiplier
        order_stats4['research_minus_trade_in_backtest'].iloc[1:] = np.nan
    except:
        order_stats4 = pd.DataFrame()

    try:
        if sig_trade_df.sum().sum() == 0:
            pass
        else:
            sig_trade_df.iloc[-1] =  sig_trade_df.iloc[-1] + (-sig_trade_df.sum())
        sig_trade_df = sig_trade_df.sort_index()

        bf = -(sig_trade_df.multiply(twap.loc[sig_trade_df.index], axis = 0) * multiplier) 
        bf = bf - abs(bf)* 0.000024

        #order_stats5 = bf.sum().to_frame()
        order_stats5 = profit_divide#.to_frame()
        order_stats5.columns = ['back_test_pnl']
    except:
        order_stats5 = pd.DataFrame()
        
    try:
        trade_sig_holder = pd.DataFrame()
        research_sig_holder = pd.DataFrame()
        for item in result.columns:

            if ('_java_' in item) and ('raw' not in item) and ('signal' in item):
                temp = result[item]
                temp.name = item.split('_java_')[-1] + '_trade'
                trade_sig_holder = pd.concat([trade_sig_holder, temp], axis = 1)
            elif('_python_' in item):
                if (('short' in item) or ('orig' in item)) and ('raw' in item):
                    temp = result[item]
                    temp.name = item.split('_python_')[-1] + '_research'
                    research_sig_holder = pd.concat([research_sig_holder, temp], axis = 1)
                elif (('short' not in item) and ('orig' not in item)) and ('raw' not in item):
                    temp = result[item]
                    temp.name = item.split('_python_')[-1] + '_research'
                    research_sig_holder = pd.concat([research_sig_holder, temp], axis = 1)
                else:
                    pass
            else:
                pass

        final_sig_result = pd.concat([trade_sig_holder ,research_sig_holder], axis = 1)


        order_stats6 = pd.DataFrame()
        for item in model_date_list:
            order_stats6 = pd.concat([order_stats6, final_sig_result[item+'_trade']], axis = 1)
            order_stats6 = pd.concat([order_stats6, final_sig_result[item+'_research']], axis = 1)
    except:
        order_stats6 = pd.DataFrame()
    
    di = {}
    for item in model_date_list:
        try:
            temp_trade = pd.read_csv('/data/group/800466/warehouse/prod/tradingstats/Mobius/tracking/back_test/%s/%s/%s/_all_daily_return.csv'%(date.replace('-', ''), ticker[:2].upper(), item), index_col = 0)['daily_return']
        except:
            temp_trade = pd.Series([0], index = [date], name = 'daily_return')
            temp_trade.index.name = 'date'
        try:
            temp_research = pd.read_csv('/data/group/800466/warehouse/prod/tradingstats/Mobius/tracking/back_test/%s/%s/%s/_all_daily_return.csv'%(date.replace('-', ''), ticker[:2].upper(), item + '_research'), index_col = 0)['daily_return']
        except:
            temp_research = pd.Series([0], index = [date], name = 'daily_return')
            temp_research.index.name = 'date'

        temp_trade.name = item[12:] + '_trade'
        temp_research.name = item[12:] + '_research'
        try:
            sig_corr = order_stats6[item + '_trade'].corr(order_stats6[item + '_research'])
        except:
            sig_corr = np.nan
        temp_new = pd.concat([temp_trade, temp_research], axis = 1)
        temp_new['corr'] = sig_corr
        #
        temp_new.index = pd.to_datetime(temp_new.index)
        try:
            temp_old = pd.read_excel('/data/group/800466/warehouse/prod/tradingstats/Mobius/%s_comparisons.xlsx'%ticker[:2].upper(), sheet_name = str(item[12:].replace('_crn', '_crn')), index_col = 0)
        except:
            temp_old = pd.DataFrame()
        temp_all = drop_dup(pd.concat([temp_old, temp_new]), k = 'last')
        
        di[item[12:].replace('_crn', '_crn')] = temp_all


    with pd.ExcelWriter('/data/group/800466/warehouse/prod/tradingstats/Mobius/%s_comparisons.xlsx'%ticker[:2].upper()) as writer:
        for strat in di.keys():
            print(strat)
            di[strat].index = pd.to_datetime(di[strat].index)
            di[strat].sort_index().to_excel(writer, sheet_name=str(strat), index=True)
    

    with pd.ExcelWriter('/data/group/800466/warehouse/prod/tradingstats/Mobius/log/log_%s_%s.xlsx'%(b, trail)) as writer:

        df.to_excel(writer, sheet_name="成交情况", index=True)
        order_stats.to_excel(writer, sheet_name="交易成本分析", index=True)
        #order_stats2.to_excel(writer, sheet_name="买卖委托-实际成交对比", index=True)
        order_stats3.to_excel(writer, sheet_name="实盘-回测对比", index=True)
        order_stats6.to_excel(writer, sheet_name="实盘-研究信号值对比", index=True)
        order_stats4.to_excel(writer, sheet_name="实盘-研究信号回测结果对比", index=True)
        order_stats5.to_excel(writer, sheet_name="收益分解", index=True)
        pd.concat([filter_trade1, filter_research1], axis = 1).loc[b].to_excel(writer, sheet_name="过滤指标对比", index=True)
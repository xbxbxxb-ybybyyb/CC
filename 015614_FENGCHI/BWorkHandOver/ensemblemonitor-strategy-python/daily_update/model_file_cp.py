# @Time : 2021/6/16 19:29
# @Author : Zhichen Lu
# @File : model_file_cp.py

import pandas as pd
import shutil
import os
import configparser

conf = configparser.ConfigParser()
conf.read('/data/group/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])

source_path =  '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_%s_train200_test10_factor_num400_norm_window_40.pkl'
target_path = '/data/user/015664/AFuckingTrigger/OnlineModel/XGB_%s.pkl'

for each in ['ic_half_c','ic_half_t','ic_half_d']:
    actual_source = source_path%each
    actual_target = target_path%each[-1:]
    if not os.path.exists(actual_target.replace('.pkl','/')):
        os.mkdir(actual_target.replace('.pkl','/'))
    if not os.path.exists(actual_target.replace('.pkl','_val_pred/')):
        os.mkdir(actual_target.replace('.pkl','_val_pred/'))
    if not os.path.exists(actual_target.replace('.pkl','_model_conf/')):
        os.mkdir(actual_target.replace('.pkl','_model_conf/'))
    if not os.path.exists(actual_target.replace('.pkl','_factor_list/')):
        os.mkdir(actual_target.replace('.pkl','_factor_list/'))

    for idx,cell in para_list[:136]:
        print(cell)
        shutil.copy(actual_source.replace('.pkl','/')+'%d.pkl'%cell[1],
                    actual_target.replace('.pkl','/')+'%d.pkl'%cell[1])

        shutil.copy(actual_source.replace('.pkl', '_val_pred/') + '%d.pkl' % cell[1],
                    actual_target.replace('.pkl', '_val_pred/') + '%d.pkl' % cell[1])

        shutil.copy(actual_source.replace('.pkl', '_model_conf/') + '%d.json' % cell[1],
                    actual_target.replace('.pkl', '_model_conf/') + '%d.json' % cell[1])
        if os.path.exists(actual_source.replace('.pkl', '_factor_list/') + '%d.pkl' % cell[1]):
            shutil.copy(actual_source.replace('.pkl', '_factor_list/') + '%d.pkl' % cell[1],
                    actual_target.replace('.pkl', '_factor_list/') + '%d.pkl' % cell[1])

del actual_source,actual_target
monthly_target = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_%s_train200_test10_factor_num400.pkl'

for each in  ['ic_half_c','ic_half_t','ic_half_d']:
    actual_source = monthly_target % each.replace('_half','')
    actual_target = target_path %each[-1:]
    for idx,cell in para_list[136:]:
        if os.path.exists(actual_source.replace('.pkl', '/') + '%d.pkl' % cell[1]):
            shutil.copy(actual_source.replace('.pkl', '/') + '%d.pkl' % cell[1],
                    actual_target.replace('.pkl', '/') + '%d.pkl' % cell[1])
        if os.path.exists(actual_source.replace('.pkl', '_val_pred/') + '%d.pkl' % cell[1]):
            shutil.copy(actual_source.replace('.pkl', '_val_pred/') + '%d.pkl' % cell[1],
                    actual_target.replace('.pkl', '_val_pred/') + '%d.pkl' % cell[1])

        shutil.copy(actual_source.replace('.pkl', '_model_conf/') + '%d.json' % cell[1],
                    actual_target.replace('.pkl', '_model_conf/') + '%d.json' % cell[1])
        if os.path.exists(actual_source.replace('.pkl', '_factor_list/') + '%d.pkl' % cell[1]):
            shutil.copy(actual_source.replace('.pkl', '_factor_list/') + '%d.pkl' % cell[1],
                    actual_target.replace('.pkl', '_factor_list/') + '%d.pkl' % cell[1])
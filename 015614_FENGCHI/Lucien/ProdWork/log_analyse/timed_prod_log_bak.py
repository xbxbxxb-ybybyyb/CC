# coding: utf-8
# Author：fengchi863
# Date ：2025/1/13 13:40

import sys
import os
sys.path.append('/data/user/015614/Lucien')

from shutil import copyfile
import datetime as dt
import pandas as pd

# 备份这部分日志

def copy_file(dept_location, dest_location, env='prod', strategy_name='Europa'):
    dest_location = dest_location.replace('.log.gz', f'-{env}.log.gz')
    if os.path.exists(dept_location):
        copyfile(dept_location, dest_location)
        print(f'{strategy_name}_{env}完成备份')
    else:
        print(f'没有{strategy_name}_{env}')

#################################### 复制实盘和仿真log ####################################
nowdate = dt.datetime.now().strftime('%Y%m%d')
# nowdate = '20250227'
nowdate_h = pd.Timestamp(nowdate).strftime('%Y-%m-%d')
print('nowdate=%s' % str(nowdate))

#%% EventDriven-Ext1-%s
copy_file('/data/group/800463/StrategyLog/sim/EventDriven_Ext1-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/EventDriven_Ext1-%s.log.gz' % nowdate_h, env='UAT', strategy_name='EventDriven_Ext1')
copy_file('/data/group/800463/StrategyLog/prd/SHEX.EventDriven_Ext1-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/SHEX.EventDriven_Ext1-%s.log.gz' % nowdate_h, env='prod', strategy_name='EventDriven_Ext1')
copy_file('/data/group/800463/StrategyLog/prd/SZEX.EventDriven_Ext1-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/SZEX.EventDriven_Ext1-%s.log.gz' % nowdate_h, env='prod', strategy_name='EventDriven_Ext1')

#%% Jupiter
copy_file('/data/group/800463/StrategyLog/sim/JupiterStrategy-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/JupiterStrategy-%s.log.gz' % nowdate_h, env='UAT', strategy_name='Jupiter')
copy_file('/data/group/800463/StrategyLog/prd/SHEX.JupiterStrategy-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/SHEX.JupiterStrategy-%s.log.gz' % nowdate_h, env='prod', strategy_name='Jupiter')
copy_file('/data/group/800463/StrategyLog/prd/SZEX.JupiterStrategy-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/SZEX.JupiterStrategy-%s.log.gz' % nowdate_h, env='prod', strategy_name='Jupiter')

#%% EventDrivenCpp
copy_file('/data/group/800463/StrategyLog/prd/SZEX.EventDrivenCpp-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/SZEX.EventDrivenCpp-%s.log.gz' % nowdate_h, env='prod', strategy_name='EventDrivenCpp')
copy_file('/data/group/800463/StrategyLog/prd/SHEX.EventDrivenCpp-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/SHEX.EventDrivenCpp-%s.log.gz' % nowdate_h, env='prod', strategy_name='EventDrivenCpp')
copy_file('/data/group/800463/StrategyLog/sim/EventDrivenCpp-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/EventDrivenCpp-%s.log.gz' % nowdate_h, env='UAT', strategy_name='EventDrivenCpp')
# copy_file('/data/group/800463/StrategyLog/sim/EventDrivenCpp-%s.log.gz' % nowdate_h,
#           '/data/group/800463/日内强势股/log/EventDrivenCpp-%s.log.gz' % nowdate_h, env='night')

#%% Saturn
copy_file('/data/group/800463/StrategyLog/prd/SZEX.SaturnStrategy-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/SZEX.SaturnStrategy-%s.log.gz' % nowdate_h, env='prod', strategy_name='SaturnStrategy')
copy_file('/data/group/800463/StrategyLog/prd/SHEX.SaturnStrategy-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/SHEX.SaturnStrategy-%s.log.gz' % nowdate_h, env='prod', strategy_name='SaturnStrategy')
copy_file('/data/group/800463/StrategyLog/sim/SaturnStrategy-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/SaturnStrategy-%s.log.gz' % nowdate_h, env='UAT', strategy_name='SaturnStrategy')


#%% Metis
copy_file('/data/group/800463/StrategyLog/prd/SZEX.MetisStrategy-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/SZEX.MetisStrategy-%s.log.gz' % nowdate_h, env='prod', strategy_name='MetisStrategy')
copy_file('/data/group/800463/StrategyLog/prd/SHEX.MetisStrategy-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/SHEX.MetisStrategy-%s.log.gz' % nowdate_h, env='prod', strategy_name='MetisStrategy')
copy_file('/data/group/800463/StrategyLog/sim/MetisStrategy-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/MetisStrategy-%s.log.gz' % nowdate_h, env='UAT', strategy_name='MetisStrategy')


#%% Leda
copy_file('/data/group/800463/StrategyLog/prd/SZEX.LedaStrategy-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/SZEX.LedaStrategy-%s.log.gz' % nowdate_h, env='prod', strategy_name='LedaStrategy')
copy_file('/data/group/800463/StrategyLog/prd/SHEX.LedaStrategy-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/SHEX.LedaStrategy-%s.log.gz' % nowdate_h, env='prod', strategy_name='LedaStrategy')
copy_file('/data/group/800463/StrategyLog/sim/LedaStrategy-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/LedaStrategy-%s.log.gz' % nowdate_h, env='UAT', strategy_name='LedaStrategy')

#%% EuropaMDStrategy
copy_file('/data/group/800463/StrategyLog/sim/EuropaMDStrategy-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/EuropaMDStrategy-%s.log.gz' % nowdate_h, env='UAT', strategy_name='EuropaMDStrategy')

#%% EventDriven_test1
copy_file('/data/group/800463/StrategyLog/prd/SHEX.EventDriven_test1-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/SHEX.EventDriven_test1-%s.log.gz' % nowdate_h, env='prod', strategy_name='EventDriven_test1')
copy_file('/data/group/800463/StrategyLog/prd/SZEX.EventDriven_test1-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/SZEX.EventDriven_test1-%s.log.gz' % nowdate_h, env='prod', strategy_name='EventDriven_test1')

#%% EventDriven_Ext2
copy_file('/data/group/800463/StrategyLog/prd/SZEX.EventDriven_Ext2-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/SZEX.EventDriven_Ext2-%s.log.gz' % nowdate_h, env='prod', strategy_name='EventDriven_Ext2')
copy_file('/data/group/800463/StrategyLog/prd/SHEX.EventDriven_Ext2-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/SHEX.EventDriven_Ext2-%s.log.gz' % nowdate_h, env='prod', strategy_name='EventDriven_Ext2')
copy_file('/data/group/800463/StrategyLog/sim/EventDriven_Ext2-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/EventDriven_Ext2-%s.log.gz' % nowdate_h, env='UAT', strategy_name='EventDriven_Ext2')

#%% JupiterBj
copy_file('/data/group/800463/StrategyLog/sim/JupiterStrategy_BJ-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/JupiterStrategy_BJ-%s.log.gz' % nowdate_h, env='UAT', strategy_name='JupiterBj')
copy_file('/data/group/800463/StrategyLog/prd/SZEX.JupiterStrategy_BJ-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/SZEX.JupiterStrategy_BJ-%s.log.gz' % nowdate_h, env='prod', strategy_name='JupiterBj')

#%% Ceres
copy_file('/data/group/800463/StrategyLog/sim/CeresStrategy-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/CeresStrategy-%s.log.gz' % nowdate_h, env='UAT', strategy_name='Ceres')
copy_file('/data/group/800463/StrategyLog/prd/SZEX.CeresStrategy-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/SZEX.CeresStrategy-%s.log.gz' % nowdate_h, env='prod', strategy_name='Ceres')
copy_file('/data/group/800463/StrategyLog/prd/SHEX.CeresStrategy-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/SHEX.CeresStrategy-%s.log.gz' % nowdate_h, env='prod', strategy_name='Ceres')

#%% Mimas
copy_file('/data/group/800463/StrategyLog/sim/MimasStrategy-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/MimasStrategy-%s.log.gz' % nowdate_h, env='UAT', strategy_name='Mimas')
# copy_file('/data/group/800463/StrategyLog/prd/SZEX.MimasStrategy-%s.log.gz' % nowdate_h,
#           '/data/group/800463/日内强势股/log/SZEX.MimasStrategy-%s.log.gz' % nowdate_h, env='prod', strategy_name='Mimas')
# copy_file('/data/group/800463/StrategyLog/prd/SHEX.MimasStrategy-%s.log.gz' % nowdate_h,
#           '/data/group/800463/日内强势股/log/SHEX.MimasStrategy-%s.log.gz' % nowdate_h, env='prod', strategy_name='Mimas')

#%% UniTradeTool
copy_file('/data/group/800463/StrategyLog/sim/MimasStrategy-%s.log.gz' % nowdate_h,
          '/data/group/800463/日内强势股/log/MimasStrategy-%s.log.gz' % nowdate_h, env='UAT', strategy_name='Mimas')
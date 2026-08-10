# -*- coding: utf-8 -*-
"""
# data update master
"""

import os
from multifactor.data.utils import *

dir_path = os.path.dirname(os.path.realpath(__file__))+'\\'
#dir_path ='D:\\012315\\Code\\AlphaFactor\\AlphaSystem\\PythonVersion\\Data\\'
print (dir_path)
os.chdir(dir_path)
from update_wind_htsc import first_job, second_job
from update_wind import update_wind
from updater_universe import updater_universe
from BarraRiskFactor_daily import update_risk_factor_daily


def flag_check(date):
    path = 'Z:\\warehouse\\prod\\LOCAL_DATA\\FLAG\\' + str(date) +'\\' + str(date) + '_' + 'RDF.success'
    return os.path.exists(path)
sdate,edate,cdate_list = check_update_date()
flag_root = 'Z:\\warehouse\\prod\\LOCAL_DATA\\FLAG\\' + str(edate) + '\\'
if not os.path.exists(flag_root):
    os.mkdir(flag_root)



first_job(sdate, edate)
flag_path = 'Z:\\warehouse\\prod\\LOCAL_DATA\\HTSC_FLAG\\' + str(edate) + '_' + 'rdf_csv.success'
with open(flag_path,'w') as file:
    pass


print('------wait--------')
while True:
    if flag_check(edate):
        break
flag_path1 = flag_root + str(edate) + '_' + 'MD.start'
with open(flag_path1,'w') as file:
    pass 
try:
    print('update_wind start')
    update_wind(sdate,edate)
except Exception as e:
    flag_path1 = flag_root + str(edate) + '_' + 'MD.failed'
    with open(flag_path1,'w') as file:
        pass 



flag_path1 = flag_root + str(edate) + '_' + 'UNIV.start'
with open(flag_path1,'w') as file:
    pass 
try:
    print('update universe start')
    updater_universe(sdate,edate)
    flag_path1 = flag_root + str(edate) + '_' + 'UNIV.success'
    with open(flag_path1,'w') as file:
        pass
except Exception as e:
    flag_path1 = flag_root + str(edate) + '_' + 'UNIV.failed'
    with open(flag_path1,'w') as file:
        pass 


flag_path1 = flag_root + str(edate) + '_' + 'RISK.start'
with open(flag_path1,'w') as file:
    pass
try:    
    print('update risk start')
    update_risk_factor_daily(sdate,edate)
    flag_path1 = flag_root + str(edate) + '_' + 'RISK.success'
    with open(flag_path1,'w') as file:
        pass
except Exception as e:
    flag_path1 = flag_root + str(edate) + '_' + 'RISK.failed'
    with open(flag_path1,'w') as file:
        pass


second_job(sdate,edate)




































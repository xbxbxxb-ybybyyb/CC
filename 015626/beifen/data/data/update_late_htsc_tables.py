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
from update_wind_htsc import late_job
sdate,edate,cdate_list = check_update_date()
late_job(sdate,edate)




































import inspect, os
import sys
code_base = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.dirname(code_base))
sys.path.insert(0, '..')
from factor_utility.factor_tool import *

operation_x = 'append'
operation_x = 'create'

if operation_x =='create':
	sdate_limit = 20090101
	edate_limit = 20191201#None
	sdate_limit = 20220101
	edate_limit = 20221231
	new_date_time = 23  #
	sdate_x,edate_x,cdate_list_x = check_update_date(sdate=sdate_limit,edate=edate_limit,new_date_time=new_date_time)
else:
	new_date_time = 20
	sdate_x,edate_x,cdate_list_x = check_update_date(sdate=None,edate=None,new_date_time=new_date_time)
	#sdate_x,edate_x = 20191209,20191210

parallel_x = False if operation_x =='create' else True
factor_base_x = os.path.join(data_save_path,'factor')#r'A:\zhisj\factor',
base_path_x = os.path.join(data_save_path,'data','factor_library')#r'A:\zhisj\data\factor_library',

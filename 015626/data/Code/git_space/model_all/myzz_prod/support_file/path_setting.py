# -*- coding: utf-8 -*-
# set base folder for all script
import platform,os

if platform.system()=='Windows':
	sys_env = 'windows'
else:
	sys_env = 'linux'

if sys_env=='linux':
	data_source_path = '/data/group/800080' # disk Z name
	data_save_path = '/data/user/015626/model' # disk A name
elif sys_env=='windows':
	data_source_path = 'Z:\\' # disk Z name
	data_save_path = r'A:\weiych' # disk A name
else:
	print ('sys_env input error! ~ %s)'%(sys_env))
	raise Exception

##### warehouse prod side
path_dict = {'wind':os.path.join(data_source_path,'warehouse/prod/DATABASE/WIND'),
             'derived':os.path.join(data_source_path,'warehouse/prod/DATABASE'),
             'suntime':os.path.join(data_source_path,'warehouse/prod/DATABASE/SUNTIME')}
flag_path_data = os.path.join(data_source_path,'warehouse/prod/LOCAL_DATA/FLAG')

h5_path_listing_delisting = os.path.join(data_source_path,'warehouse','prod','ETC','CHINA_STOCK','WIND','STOCK_LISTING_DELISTING_DATE.h5')


root_path = os.path.join(data_source_path,'warehouse/prod')
root_path_local = os.path.join(data_save_path,'warehouse/prod')

##### alpha local side
alpha_path = os.path.join(data_save_path,'stock/alpha')
h5_factor_base = os.path.join(alpha_path,'factor')

#h5_factor_base
#A:\012315\stock\alpha
#r'A:\zhisj\factor',



















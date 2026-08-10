# -*- coding: utf-8 -*-
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import statsmodels.api as sm
from functools import reduce,partial
from scipy import linalg
import scipy.optimize as optimize
import time
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
import pickle,dill
from sklearn import linear_model
import os
import random

from pathlib import Path
from collections import Iterable


import traceback
import sys

from concurrent.futures import ProcessPoolExecutor as Pool
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from multiprocessing import Process, Manager

from line_profiler import LineProfiler
import numba
import time
import scipy.io as sio

import multifactor.utility.dt as tdt
from multifactor.IO import IO
from multifactor.IO.IO_enums import *

import logging
import datetime

from sys import exit
import shutil
from shutil import copyfile,copytree,copy2
import errno

import inspect, os
import sys
code_base = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.dirname(code_base))
sys.path.insert(0, '..')

from support_file.path_setting import *


seed = 2018
random.seed(seed)
np.random.seed(seed)
os.environ['PYTHONHASHSEED'] = str(seed)

plt.style.use('ggplot')
pd.options.display.float_format = '{:,.5f}'.format

data_prod_base = os.path.join(data_source_path,'warehouse','prod')
h5_path_listing_delisting = os.path.join(data_prod_base,'ETC','CHINA_STOCK','WIND','STOCK_LISTING_DELISTING_DATE.h5')

wind_db_path = {'wind':os.path.join(data_prod_base,'DATABASE','WIND'),
								'derived':os.path.join(data_prod_base,'DATABASE'),
								'suntime':os.path.join(data_prod_base,'DATABASE','SUNTIME')
									}

minute_base_path = os.path.join(data_prod_base,'LOCAL_DATA','CSV','WIND','MINUTE')
flag_path_data = os.path.join(data_prod_base,'LOCAL_DATA','FLAG')


################################################################################################################


###########
"""factor update"""

def get_start_date(cdate_list,data_length):
		fdate_list_dt = IO.read_data([20090101,20300101],ftype=FType.CALENDAR).index.get_level_values(0)
		fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
		idx = fdate_list.index(cdate_list[0])-data_length
		min_index= max(0,idx)
		start_date = fdate_list[min_index]
		if idx<0:
				print ('Not enough data: will use first available date:',str(start_date))
		return start_date

def find_nearest_date(date,date_list):
		nearest_date = min(date_list, key=lambda x: abs(x - date) if x <= date else 100)
		return nearest_date

def get_current_date(new_date_time=18,print_info=False):
	"""if current date is not pass new_date_time such as 18 (6pm)
		 it will return previous trading day
	"""
	current_time = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
	current_date = int(current_time[:8])
	current_hour = int(current_time[9:11])
	print('Current time: ' + str(current_time))
	fdate_list_dt = IO.read_data([20090101, 20300101], ftype=FType.CALENDAR).index.get_level_values(0)
	fdate_list = [int(dt.datetime.strftime(i, '%Y%m%d')) for i in fdate_list_dt]
	nearest_date = min(fdate_list, key=lambda x: abs(x - current_date) if x <= current_date else 100)
	if current_hour < new_date_time and nearest_date == current_date:
		current_date_use = fdate_list[fdate_list.index(current_date) - 1]
		if print_info:
			print('Not till refresh time ' + str(new_date_time) + ':00')
			print('Use previous trading date: ' + str(current_date_use))
	elif current_hour >= new_date_time and nearest_date == current_date:
		if print_info:
			print('Right on time: ' + str(current_date))
		current_date_use = current_date
	elif nearest_date < current_date:
		current_date_use = nearest_date
	elif nearest_date > current_date:
		current_date_use = fdate_list[fdate_list.index(nearest_date) - 1]
	return current_date_use

def get_next_date(new_date_time=18,print_info=False):
		"""if current date is not pass new_date_time such as 18 (6pm)
			 it will return previous trading day
		"""
		current_time = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
		current_date = int(current_time[:8])
		current_hour = int(current_time[9:11])
		print('Current time: ' + str(current_time))
		fdate_list_dt = IO.read_data([20090101, 20300101], ftype=FType.CALENDAR).index.get_level_values(0)
		fdate_list = [int(dt.datetime.strftime(i, '%Y%m%d')) for i in fdate_list_dt]
		nearest_date = min(fdate_list, key=lambda x: abs(x - current_date) if x <= current_date else 100)
		next_date = fdate_list[fdate_list.index(nearest_date)+1]
		if current_hour < new_date_time and nearest_date == next_date:
				next_date = fdate_list[fdate_list.index(next_date) - 1]
				if print_info:
						print('Not till refresh time ' + str(new_date_time) + ':00')
						print('Use previous trading date: ' + str(current_date))
		elif nearest_date < next_date:
				next_date = nearest_date
		elif current_hour >= new_date_time and nearest_date == next_date:
				if print_info:
						print('Right on time: ' + str(next_date))
		return next_date


def date_period_handler(sdate=None, edate=None,new_date_time=18,print_info=False):
		last_day = get_current_date(new_date_time,print_info)
		if sdate is None and edate is None:
				sdate = last_day
				edate = last_day
				if print_info:
						print('update for one day: ' + str(sdate))
		if sdate is not None and edate is None:
				edate = last_day
		else:
				fdate_list_dt = IO.read_data([20090101, 20300101], ftype=FType.CALENDAR).index.get_level_values(0)
				fdate_list = [int(dt.datetime.strftime(i, '%Y%m%d')) for i in fdate_list_dt]
				cdate_list = [i for i in fdate_list if i <= min(edate, last_day) and i >= sdate]
				if len(cdate_list)==0:
						print ('input date not valid: %d - %d'%(sdate,edate))
						raise Exception
				else:
						sdate, edate = cdate_list[0], cdate_list[-1]
		return sdate, edate


def check_update_date(sdate=None, edate=None, use_len=None,new_date_time=20,print_info=False):
		# check_update_date(sdate=None,edate=None)
		if sdate is not None and edate is not None:
				if sdate>edate:
						print ('date input error: %s - %s '%(sdate,edate))
						raise Exception
		use_len = 0 if use_len is None else use_len
		sdate, edate = date_period_handler(sdate, edate,new_date_time,print_info)
		fdate_list_dt = IO.read_data([20090101, 20300101], ftype=FType.CALENDAR).index.get_level_values(0)
		fdate_list = [int(dt.datetime.strftime(i, '%Y%m%d')) for i in fdate_list_dt]
		cdate_list = [i for i in fdate_list if i >= sdate and i <= edate]
		idx = max(0, fdate_list.index(cdate_list[0]) - use_len)
		sdate_prev = fdate_list[idx]
		if print_info:
			print('-' * 20, '\ndata used: %d - %d ' % (sdate_prev, edate))
			print('factor data: %d - %d \ntotal count: %d' % (sdate_prev, edate, len(cdate_list)))
			print('-' * 20)
		return sdate_prev, edate, cdate_list



def get_friday_info(sdate,edate):
    # must have full calendar info to decide last day of the month,quarter,year
    qtr_end = [3,6,9,12]
    year_end = [12]
    td_df = IO.read_data([20000101, 20500101], ftype=FType.CALENDAR)
    td_df = td_df.reset_index().set_index('dt').drop(columns = ['Ticker'])
    td_list_full = td_df.index.tolist()
    td_df['weekday'] = [i.weekday()+1 for i in td_list_full]
    td_df['year_month'] = ['%d-%d'%(i.year,i.month) for i in td_list_full]
    td_df['day_month'] = td_df['calendar'].groupby(td_df['year_month']).cumcount()+1
    td_df['days_in_month'] = td_df['day_month'].groupby(td_df['year_month']).transform(np.max)
    td_df['day_month_left'] = td_df['days_in_month'] - td_df['day_month']
    td_df_slice = td_df[td_df['weekday']==5]
    td_df_slice['dt'] = td_df_slice.index.tolist()
    end_of_week_list = td_df_slice['dt'].tolist()
    end_of_month_list = td_df_slice.groupby(td_df_slice['year_month']).last()['dt'].tolist()
    end_of_quarter_list = [i for i in end_of_month_list if i.month in qtr_end]
    end_of_year_list = [i for i in end_of_month_list if i.month in year_end]
    td_df['end_of_week'] = [1 if i in end_of_week_list else 0 for i in td_list_full]
    td_df['end_of_month'] = [1 if i in end_of_month_list else 0 for i in td_list_full]
    td_df['end_of_quarter'] = [1 if i in end_of_quarter_list else 0 for i in td_list_full]
    td_df['end_of_year'] = [1 if i in end_of_year_list else 0 for i in td_list_full]
    td_df = td_df.loc[str(sdate):str(edate)]
    return td_df

def get_rebal_list(sdate,edate,rebal_mode='end_of_month'):
    friday_info = get_friday_info(sdate,edate)
    date_list = friday_info.index.tolist()
    rebal_info = friday_info[rebal_mode]
    rebal_spec_list = rebal_info[rebal_info>0].index.tolist()
    date_num,rebal_num = len(friday_info),len(rebal_spec_list)
    rebal_s,rebal_e = rebal_spec_list[0],rebal_spec_list[-1]
    print('Mode: %s | %s ~ %s (%d days) | %s ~ %s (%d iterations)|'%(rebal_mode,str(sdate),str(edate),date_num,rebal_s,rebal_e,rebal_num))
    #idx_list_rebal = [i for i in range(date_num) if date_list[i] in rebal_spec_list]
    #freq_sparsity =[idx_list_rebal[i] - idx_list_rebal[i+1] for i in range(len(idx_list_rebal)-1)]
    return rebal_spec_list

def get_rebal_list_smart(sdate,edate,rebal_mode_dict={'month_week':'20210101'}):
    # sparse2dense ~ month_week, quarter_month, quarter_week
    # days for switch based on trading day
    switch_day = pd.Timestamp(str(list(rebal_mode_dict.values())[0]))
    rebal_type_list = list(rebal_mode_dict.keys())[0].split('_')
    rebal_mode1 = 'end_of_%s'%(rebal_type_list[0])
    rebal_mode2 = 'end_of_%s'%(rebal_type_list[1])
    rebal_list1 = get_rebal_list(sdate,edate,rebal_mode=rebal_mode1)
    rebal_list2 = get_rebal_list(sdate,edate,rebal_mode=rebal_mode2)
    rl1 = [i for i in rebal_list1 if i<switch_day]
    rl2 = [i for i in rebal_list2 if i>=switch_day]
    rebal_spec_list = rl1 + rl2
    print('get rebal list: %s %s ~ %s | %d iterations(%d)'%(rebal_type_list,sdate,edate,len(rebal_spec_list),len(rebal_mode2)))
    return rebal_spec_list


####################

def print_current_time():
	return dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def show_time_spent(ts):
		if ts>60:
				time_spent = (str((round((ts)/60,2)))+' minutes')
		else:
				time_spent = (str((round((ts),2)))+' seconds')
		return time_spent

def print_time(toc,tic,show_time=True,remain_iter=None):
		ts = toc-tic
		time_spent = show_time_spent(ts)
		if remain_iter is not None:
				time_spent_total = '/ remain %s'%(show_time_spent(ts*remain_iter))
		else:
				time_spent_total = ''
		time_str = ' (used %s%s) '%(time_spent,time_spent_total)
		if show_time:
				time_str = time_str +'- '+ print_current_time()
		return time_str


import pickle,dill

def save_pickle(save_dict,save_path):
	print ('saving data to:\n',save_path)
	folder= os.path.dirname(save_path)
	if not os.path.exists(folder):
		os.makedirs(folder)
	if os.path.exists(save_path):
		print('remove existing one')
		os.remove(save_path)
	with open(save_path, 'wb') as input:
		pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
	return

def read_pickle(save_path=None,verbose=True):
	tic = time.time()
	with open(save_path, 'rb') as input:
			save_dict = pickle.load(input)
	toc = time.time()
	if verbose:
			print('loading done - %s - %s   '%(print_time(toc,tic),save_path))
	return save_dict

def find_file(root_path=h5_factor_base,suffix='h5',file_name_only=False):
    factor_path_dict = {}
    for path, subdirs, files in os.walk(root_path):
      for name in files:
          if suffix in name:
              fac_name = name[:name.find('.')]
              factor_path_dict[fac_name] = os.path.join(path, name)
    if file_name_only:
        factor_path_dict = {fac:os.path.basename(fac).replace('.%s'%(suffix),'') for fac in factor_path_dict}
        factor_path_dict = list(factor_path_dict.values())
    return factor_path_dict

def get_all_pred_helper(pred_root):
    print('get pred raw from: %s'%(pred_root))
    pd_dict = find_file(pred_root,'pkl')
    res_md = {i:read_pickle(pd_dict[i])['prediction'] for i in pd_dict}
    pred_raw_df = pd.DataFrame(res_md).dropna(how='all')
    ml = pred_raw_df.columns.tolist()
    print('%s ~ %s: %d models'%(pred_raw_df.index[0],pred_raw_df.index[-1],len(ml)))
    print(ml)
    return pred_raw_df


def read_all_pickle_helper(pkl_root):
    pickle_dict = find_file(pkl_root,'pkl')
    val_dict = {i:read_pickle(pickle_dict[i]) for i in pickle_dict}
    val_df = pd.concat(list(val_dict.values()),axis=1)
    return val_df


def copy2_verbose(src, dst):
		print('Copying {0}'.format(src))
		shutil.copy2(src,dst)


def copy_folder(src, dest):
	def _logpath(path, names):
			path = os.path.join(dest,'move_process_check.log')
			logging.info('Working in %s' % path)
			return []   # nothing will be ignored

	if os.path.exists(dest):
			print ('remove destination folder - %s'%(dest))
			shutil.rmtree(dest)
	try:
			print ('start copying:')
			print ('src: %s'%(src))
			print ('dest: %s'%(dest))
			shutil.copytree(src, dest, ignore=_logpath,copy_function=copy2_verbose)
	except OSError as e:
			# If the error was caused because the source wasn't a directory
			if e.errno == errno.ENOTDIR:
					shutil.copy(src, dest)
			else:
					print('Directory not copied. Error: %s' % e)
	return

def copy_file_list(src_root,des_root,file_list,suffix=''):
	if not os.path.exists(des_root):
		os.makedirs(des_root)
	else:
		print ('remove existing one')
		shutil.rmtree(des_root)
		os.makedirs(des_root)

	if suffix is not '' and suffix.find('.')<0:
		suffix = '.'+suffix
	for fac_name in file_list:
		source = os.path.join(src_root,'%s%s'%(fac_name,suffix))
		target = os.path.join(des_root,'%s%s'%(fac_name,suffix))
		try:
			copyfile(source, target)
		except IOError as e:
			print("Unable to copy file. %s" % e)
		except:
			print("Unexpected error:", sys.exc_info())
	return


def delete_folder(folder_name):
	if os.path.exists(folder_name):
		print('fold removed: %s'%(folder_name))
		shutil.rmtree(folder_name)
	else:
		print('fold not exists')
	return


def concat_pd_spec(exist_df,update_df,use_update=False,dropna=True, spec=False):
    if spec == True:
        exist_df[(exist_df.index.hour == 9) & (exist_df.index.minute == 30)] = 9999
        update_df[(update_df.index.hour == 9) & (update_df.index.minute == 30)] = 9999
    if dropna:
        update_df = update_df.dropna()
        exist_df = exist_df.dropna()
    if spec == True:
        exist_df[(exist_df.index.hour == 9) & (exist_df.index.minute == 30)] = np.nan
        update_df[(update_df.index.hour == 9) & (update_df.index.minute == 30)] = np.nan
    if isinstance(use_update,bool):
        if use_update:
            new_index = update_df.index[0]
            update_df_slice = update_df
            exist_df_slice = exist_df.loc[:new_index]
            if new_index in exist_df_slice.index:
                exist_df_slice = exist_df_slice.iloc[:-1]
        else:
            new_index = exist_df.index[-1]
            exist_df_slice = exist_df
            update_df_slice = update_df.loc[new_index:]
            if new_index in update_df_slice.index:
                update_df_slice = update_df_slice.iloc[1:]
    else:
        exist_df_slice = exist_df.loc[:use_update]
        new_index = exist_df_slice.index[-1]
        update_df_slice = update_df.loc[new_index:]
    if len(exist_df_slice)>0:
        sdate_exist,edate_exist = exist_df_slice.index[0],exist_df_slice.index[-1]
    else:
        sdate_exist,edate_exist = '',''
    if len(update_df_slice)>0:
        sdate_update,edate_update = update_df_slice.index[0],update_df_slice.index[-1]
    else:
        sdate_update,edate_update = '',''
    print('ConcatPD: use_update:%s dropna:%s |exists:%s ~ %s | update: %s ~ %s'%(use_update,dropna,sdate_exist,edate_exist,sdate_update,edate_update))
    pred_cat_df = pd.concat([exist_df_slice,update_df_slice],axis=0)
    return pred_cat_df


import os
import shutil
import sys
from datetime import datetime
from loguru import logger
from xquant.factordata import FactorData
factorData = FactorData()

from param_generator.generator import Generator


def prepare_trading_day(testcase_base_path, target_date, batch_run_stock_list=None, load_his_data=None, work_indicator_folder=None,
						minute_shift=0, replay_data_date=None, real_env=False, mode='sim', work_index_weight_folder=None):
	# 参数文件生成的目标路径, 需要改路径的写入权限
	# testcase_base_path = os.getcwd()
	# testcase_base_path = "/data/user/019906/018728/cpp_projects/csi_calculator/testcase_v6_history_data/"
	# testcase_base_path = "/data/user/019906/018728/cpp_projects/csi_calculator/testcase_v6_history_data_index_stock_change/"

	# 填写前段参数的zone
	front_param_zone = '304301'

	# 后端参数config.json文件所在文件夹地址, 可不指定, 默认为: testcase_base_path 的路径加上日期(target_date)文件夹
	backend_params_dirpath = os.path.join(os.getcwd(), target_date)

	# 填写铃客通知的员工工号
	user_ids = ['019906']

	generator = Generator(real_env=real_env)
	logger.info("Begin preparing parameters, trading_date={}", target_date)
	generator.write_params_file(mode=mode, base_path=testcase_base_path, gen_trading_day=target_date,
								backend_params_dirpath=backend_params_dirpath, zone=front_param_zone,
								zone_ids=[front_param_zone], batch_run_stock_list=batch_run_stock_list,
								load_his_data=load_his_data, work_indicator_folder=work_indicator_folder,
								minute_shift=minute_shift, work_index_weight_folder=work_index_weight_folder)
	generator.write_request_file(base_path=testcase_base_path, date=target_date, version='v3', replay_data_date=replay_data_date)

	if real_env==False:
		channel_list = ["stock_sh_1", "stock_sh_2", "stock_sh_3", "stock_sh_4", "stock_sh_5", "stock_sh_6",
						"stock_sz_2011", "stock_sz_2012", "stock_sz_2013", "stock_sz_2014", "stock_sz_2015",
						"future", "index"]
		for channel_name in channel_list:
			generator.write_request_file_for_channel(base_path=testcase_base_path, date=target_date, channel_name=channel_name)
			# channel_dir = os.path.join(testcase_base_path, target_date, channel_name)
			channel_dir = os.path.join(testcase_base_path, channel_name)
			channel_dir_config = os.path.join(channel_dir, f"offset_{minute_shift}")
			if not os.path.exists(channel_dir_config):
				os.makedirs(channel_dir_config)
			shutil.copy(f"{testcase_base_path}/offset_{minute_shift}/config.json", channel_dir_config)
			shutil.copy(f"{testcase_base_path}/settings.json", channel_dir)
	logger.info("Finish preparing parameters done, trading_date={}", target_date)

def delete_indicator_file(date_list, symbol_list, indicator_folder, minute_shift):
	for date in date_list:
		for symbol in symbol_list:
			file_path = f"{indicator_folder}/{date}/offset_{minute_shift}/01_Indicator/{symbol}"
			try:
				# 使用 remove() 方法删除文件
				os.remove(file_path)
				print(f'{file_path} 文件删除成功')
			except FileNotFoundError:
				print(f'{file_path} 文件未找到')
			except PermissionError:
				print(f'没有权限删除 {file_path} 文件')
			except Exception as e:
				print(f'删除文件时发生其他错误: {e}')
def check_indicator_file_exist(date_list, symbol_list, indicator_folder, minute_shift):
	ret = True
	for date in date_list:
		for symbol in symbol_list:
			file_path = f"{indicator_folder}/{date}/offset_{minute_shift}/01_Indicator/{symbol}"
			if not os.path.exists(file_path):
				logger.error(f"Indicator not exist, path={file_path}")
				ret = False
	return ret

def prepare_param_for_history_dates(history_dates, test_case_root_folder, batch_run_stock_list, work_indicator_folder,
									minute_shift=0, work_index_weight_folder=None):
	# base_dates = ['20250116', '20250117', '20250120', '20250121', '20250122', '20250123']
	base_dates = history_dates[:6]
	logger.info(f"Prepare param without load history data for dates={base_dates}")
	for dt in base_dates:
		test_case_base_folder_index_stock_change = os.path.join(test_case_root_folder, dt,
																f"offset_{minute_shift}/01_Indicator/index_stock_change")
		prepare_trading_day(test_case_base_folder_index_stock_change,dt, batch_run_stock_list=batch_run_stock_list, load_his_data=False,
							work_indicator_folder=work_indicator_folder, minute_shift=minute_shift, work_index_weight_folder=work_index_weight_folder)

	# base_dates = ['20250124', '20250127', '20250205',
	# 		  '20250206', '20250207', '20250210', '20250211', '20250212', '20250213', '20250214', '20250217', '20250218',
	# 		  '20250219', '20250220', '20250221', '20250224', '20250225', '20250226', '20250227', '20250228', '20250303']
	base_dates = history_dates[6:]
	logger.info(f"Prepare param with load history data for dates={base_dates}")
	for dt in base_dates:
		test_case_base_folder_index_stock_change = os.path.join(test_case_root_folder, dt,
																f"offset_{minute_shift}/01_Indicator/index_stock_change")
		prepare_trading_day(test_case_base_folder_index_stock_change,dt, batch_run_stock_list=batch_run_stock_list, load_his_data=None,
							work_indicator_folder=work_indicator_folder, minute_shift=minute_shift, work_index_weight_folder=work_index_weight_folder)


def prepare_daily_param(dt, testcase_base_path, work_indicator_folder, minute_shift=None, replay_data_date=None, real_env=False, mode='sim'):
	prepare_trading_day(testcase_base_path, dt, work_indicator_folder=work_indicator_folder, minute_shift=minute_shift,
						replay_data_date=replay_data_date, real_env=real_env, mode=mode)


if __name__ == '__main__':
	sys.stdout = open(os.devnull, 'w')
	prepare_param_for_history_dates()

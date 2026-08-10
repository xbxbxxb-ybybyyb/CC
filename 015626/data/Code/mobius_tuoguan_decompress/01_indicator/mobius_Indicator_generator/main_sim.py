import os
from datetime import datetime
from loguru import logger
from param_generator.generator import Generator
from common.tools import *


'''
使用该脚本将值testcase_base_path文件夹路径下生成如下形式的参数
└── 20240424				# 目标交易日日期
    ├── params.json			# 策略前端参数(供客户端使用), 即: 第一层参数
    ├── settings.json		# 策略一体化框架参数(后端参数), 即: 第二层参数
    └── config.json			# 策略自身参数(后端参数), 即:第三层参数
'''

def prepare_next_trading_day():
	# 填写当前日期, 参数生成为下一个交易日
	# cur_date = datetime.now().strftime("%Y%m%d")
	cur_date = "20250314"
	target_date = get_next_trading_day(cur_date)
	minute_shift=0

	# 参数文件生成的目标路径, 需要改路径的写入权限
	# testcase_base_path = os.getcwd()
	testcase_base_path = f"/dfs/user/019906/03_mobius/xdev_param/offset_{minute_shift}"

	# 填写前段参数的zone
	front_param_zone = '303312'

	# 后端参数config.json文件所在文件夹地址, 可不指定, 默认为: testcase_base_path 的路径加上日期(target_date)文件夹
	# backend_params_dirpath = os.path.join(os.getcwd(), target_date)
	backend_params_dirpath = os.path.join("/data/cppParam-xdev/MobiusCrossSectionCalculator",f"offset_{minute_shift}", target_date)

	# 填写铃客通知的员工工号
	user_ids = ['019906']

	generator = Generator(real_env=True)
	logger.info("Begin preparing parameters, trading_date={}", target_date)
	# generator.write_params_file(mode='sim', base_path=testcase_base_path, gen_trading_day=target_date, backend_params_dirpath=backend_params_dirpath,
	# 							zone=front_param_zone, zone_ids=[front_param_zone])
	generator.write_params_file(mode='sim', base_path=testcase_base_path, gen_trading_day=target_date,
								backend_params_dirpath=backend_params_dirpath,
								zone=front_param_zone, zone_ids=[front_param_zone],
								batch_run_stock_list=None,
								load_his_data=None, minute_shift=minute_shift)
	logger.info("Finish preparing parameters done, trading_date={}", target_date)


if __name__ == '__main__':
	prepare_next_trading_day()

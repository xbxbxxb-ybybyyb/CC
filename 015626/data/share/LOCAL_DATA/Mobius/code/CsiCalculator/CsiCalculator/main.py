import os
from datetime import datetime
from loguru import logger
from generator import Generator
from common.tools import *


def prepare_next_trading_day():
	# 参数文件生成所在路径
	# testcase_base_path = os.getcwd()
	testcase_base_path = "/data/user/018728/cpp_projects/csi_calculator/testcase"
	cur_date = datetime.now().strftime("%Y%m%d")
	# cur_date = "20231119"
	target_date = get_next_trading_day(cur_date)
	# 后端参数地址
	# backend_params_dirpath = os.path.join(os.getcwd(), target_date)
	# 填写铃客通知的员工工号
	user_ids = ['018728']
	generator = Generator(user_ids)
	logger.info("Begin preparing parameters, trading_date={}", target_date)
	generator.write_params_file(testcase_base_path, target_date)
	logger.info("Finish preparing parameters done, trading_date={}", target_date)


if __name__ == '__main__':
	prepare_next_trading_day()

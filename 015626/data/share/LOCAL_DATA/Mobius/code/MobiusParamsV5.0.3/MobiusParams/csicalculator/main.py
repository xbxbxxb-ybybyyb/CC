import os
from datetime import datetime
from loguru import logger

from history_data_provider.json_history_data_provider import *
from params.params_generator import *
from request.request_generator import *

if __name__ == '__main__':
	# 参数文件生成所在路径
	testcase_base_path = os.getcwd()
	# testcase_base_path = "/data/user/018728/cpp_projects/csi_calculator/testcase"
	cur_date = datetime.now().strftime("%Y%m%d")
	dates = [get_next_trading_day(cur_date)]
	# 后端参数地址
	backend_params_dirpath = os.path.join(os.getcwd(), dates[0])
	for dt in dates:
		logger.info("Begin preparing parameters, base_date={}", dt)
		write_params_file(testcase_base_path, dt, backend_params_dirpath)
		logger.info("Finish preparing parameters done, base_date={}", dt)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

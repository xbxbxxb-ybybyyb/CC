import sys
import os
from loguru import logger
import notice
from datetime import date
from xquant.factordata import FactorData
from generate_model_param import gen_request_json
from generate_model_param import gen_params_json 
from check_log import check_log_file
from loguru import logger

def send_link_message(msg):
    lm = notice.LinkMessage()
    lm.sendMessage(msg)


def generate_param(today, next_day, offset, variety):
    request_file = 'request.json'
    params_file = 'params.json'
    root_data_path = '/dfs/user/666466/03_mobius/02_FactorData'
    template_path = '/dfs/user/666466/01_params/template/model'
    dest_model_path = '/dfs/user/666466/01_params'

    dest = os.path.join(dest_model_path, today + '_check', 'offset_' + offset, 'model', variety)
    gen_request_json(dest, os.path.join(template_path, request_file), today, root_data_path, offset)
    gen_params_json(dest, os.path.join(template_path, params_file), variety, next_day, root_data_path, offset)


def run_java(today, offset, variety):
    logger.info("start to run java, variety={}, offset={}, date={}", variety, offset, today)   
    cmd_str = 'sh start_model_check.sh {} {} {}'.format(today, offset, variety)
    logger.info("cmd={}, variety={}, offset={}, date={}", cmd_str, variety, offset, today)   
    os.system(cmd_str)


def data_check(today, offset, variety):
    s = FactorData()
    trading_list = s.tradingday(today, 2)

    next_day = trading_list[-1]

    logger.info("start to check data variety={}, offset={}, date={}", variety, offset, today)   
    generate_param(today, next_day, offset, variety)

    run_java(today, offset, variety)
    log_file = '/dfs/user/666466/11_log/{}_check/offset_{}/model/MobiusModel_{}_{}_{}_check.log'.format(today, offset, variety, today, offset)
    return check_log_file(log_file)



if __name__ == '__main__':
    if data_check('20250421', '0', 'IM') == 0:
        with open('/dfs/user/666466/04_flags/20250421/offset_0/model/20250421.success', "w") as f:
            f.close()



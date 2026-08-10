import os
from generate_model_param import param_entry
from generate_model_param import param_entry2
from check_log import check_log_file
from loguru import logger
from datetime import date
from xquant.factordata import FactorData
from data_check import data_check
from gen_signal_norm2 import rank_index
import notice
import sys

# 发送铃克消息
def send_link_message(msg):
    lm = notice.LinkMessage()
    lm.sendMessage(msg)


def create_flag(today, offset, variety):
    root = '/dfs/user/666466/04_flags/'
    flag_file = os.path.join(root, today, 'offset_' + offset, 'model', variety)
    if not os.path.exists(flag_file):
        os.makedirs(flag_file, exist_ok=True)
    flag_file = os.path.join(flag_file, today + '.success')
    with open(flag_file, "w") as f:
        f.write('')
        f.close()


def run_model(today, offset):
    logger.info("generate model params")
    param_entry(today, offset)
    logger.info("start java app for model")
    send_link_message("启动Java生成信号，日期={}, offset={}".format(today, offset))
    variety_list = ['IC', 'IF', 'IM']
    norm2_pass = True
    for variety in variety_list:
        cmd_str = 'sh start_model.sh {} {} {}'.format(today, offset, variety)
        os.system(cmd_str)
        logger.info("check log")
        send_link_message("开始检查norm2信号日志，日期={}, offset={}, variety={}".format(today, offset, variety))
        if 0 == check_log_file('/dfs/user/666466/11_log/{}/offset_{}/model/MobiusModel_{}_{}_{}.log'.format(today, offset, variety, today, offset)):
            rank_index([today], variety, offset) 
            if data_check(today, offset, variety) == 0:
                create_flag(today, offset, variety)
        else:
            norm2_pass = False

    if norm2_pass:
        param_entry2(today, offset)
        for variety in variety_list:
            cmd_str = 'sh start_model.sh {} {} {}'.format(today, offset, variety)
            os.system(cmd_str)
            logger.info("check [rank_type=norm] log")
            send_link_message("开始检查norm信号日志，日期={}, offset={}, variety={}".format(today, offset, variety))
            if 0 == check_log_file('/dfs/user/666466/11_log/{}/offset_{}/model/MobiusModel_{}_{}_{}.log'.format(today, offset, variety, today, offset)):
                logger.info('[rank=norm] check log pass, {}, {}, {}', today, offset, variety)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        exit()

    offset = '50'
    today = sys.argv[1]

    logger.info("model will run, today={}, offset={}", today, offset)
    run_model(today, offset)

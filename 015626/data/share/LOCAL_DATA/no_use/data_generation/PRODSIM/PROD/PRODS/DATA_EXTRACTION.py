from xquant.compute.aimr import AIMR
from xquant.factordata import FactorData
from xquant.xqutils.helper import link
import time
import json
import pandas as pd
from loguru import logger
import os
from link import LinkMessage
import shutil
import subprocess
import settings
import multifactor.utility.dt as udt
from multifactor.data.utils import *

logger.add(os.path.join(settings.LOG_DIR, "历史分钟数据准备-{time}.log"), enqueue=True)
lm = LinkMessage()
s = FactorData()

flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'


def get_500_300_list(date_str):
    zz500_stock_list = []
    hs300_stock_list = []
    try:
        #with pd.HDFStore(settings.WEIGHT_FILE, mode='r') as hdf_store:
        #    index_weight_hs300 = hdf_store.select('index_weight_hs300', where="dt='{}'".format(date_str))
        #    index_weight_zz500 = hdf_store.select('index_weight_zz500', where="dt='{}'".format(date_str))

        #hs300_stock_list = index_weight_hs300[index_weight_hs300['index_weight_hs300'] > 0].index.get_level_values(
        #    1).to_list()
        #zz500_stock_list = index_weight_zz500[index_weight_zz500['index_weight_zz500'] > 0].index.get_level_values(
        #    1).to_list()
        logger.info(date_str)
        hs300 = pd.read_hdf(settings.WEIGHT_FILE, key = 'index_weight_hs300')
        hs300 = hs300.loc[pd.to_datetime(date_str)]
        hs300_stock_list = hs300[hs300['index_weight_hs300'] > 0].index.to_list()
        zz500 = pd.read_hdf(settings.WEIGHT_FILE, key = 'index_weight_zz500')
        zz500 = zz500.loc[pd.to_datetime(date_str)]
        zz500_stock_list = zz500[zz500['index_weight_zz500'] > 0].index.to_list()
    except:
        logger.error("权重文件读取异常")
        lm.sendMessage()
    return zz500_stock_list, hs300_stock_list


def is_index_stock_changed(today):
    logger.info("当前运行日期: {}".format(today))

    past_2_trading_days = s.tradingday(today, -2)
    logger.info("查询权重日期为: {}".format(past_2_trading_days))

    current_zz500, current_hs300 = get_500_300_list(past_2_trading_days[0])
    next_zz500, next_hs300 = get_500_300_list(past_2_trading_days[1])

    is_changed = True

    if len(current_zz500) != 500 or len(next_zz500) != 500 or len(current_hs300) != 300 or len(next_hs300) != 300:
        logger.error("股票列表数量不足")
        lm.sendMessage("股票列表数量不足")
    elif set(current_zz500) == set(next_zz500) and set(current_hs300) == set(next_hs300):
        is_changed = False

    return is_changed


def dump_index_weight(date_str, path_str):
    # date_str = '20201231'

    # path_str = '/data/user/010793/FUTUREDATA/UNIVERSE/'
    s = FactorData()
    SZ50_data = s.hset('INDEX', date_str, 'SZ50', 1)
    HS300_data = s.hset('INDEX', date_str, 'HS300', 1)
    ZZ500_data = s.hset('INDEX', date_str, 'ZZ500', 1)

    SZ50_data.to_csv(path_str + date_str + '_SZ50.csv')
    HS300_data.to_csv(path_str + date_str + '_HS300.csv')
    ZZ500_data.to_csv(path_str + date_str + '_ZZ500.csv')


def str_convert(s):
    #    s = '20210101'
    s_l = list(s)
    s_l.insert(4, '-')
    s_l.insert(7, '-')
    s_m = ''.join(s_l)
    return s_m


def list_join(parm_list, date_list):
    ret = list()
    for parm in parm_list:
        ret.append(parm + '_' + date_list[0])

    return ret


def list_item_add(parm_list, date_str):
    ret = list()
    for parm in parm_list:
        ret.append(parm + '_' + date_str)

    return ret


def generate_his_data(today_str, days, target_folder):
    tmp_folder = os.path.join(settings.MINUTEDATA_DIR, "tmp")

    if not os.path.exists(tmp_folder):
        os.mkdir(tmp_folder)
    else:
        shutil.rmtree(tmp_folder)
        os.mkdir(tmp_folder)

    parm_list = s.tradingday(today_str, -days)
    params = {
        "tag": "xquant",
        "cpu": 24,
        "gpu": 0,
        "memory": 16000,
        "preferred_gpu": 1,
        "subtask_limit_num": days
    }
    parm_list = list_item_add(parm_list, today_str)
    params["parallel_list"] = parm_list
    print(params)
    # job.py文件为用户自定义的并行任务文件
    a = time.time()

    AIMR.runTasks('generate_his_data.py', json.dumps(params))

    print('done!!!')
    b = time.time()
    lm = link.LinkMessage()
    lm.sendMessage(today_str + ' all transfer jobs done, delay: ' + str((b - a) / 60) + 'min')
    cmd = "rsync -avz {}/*  {}".format(tmp_folder, target_folder)
    retcode = subprocess.call(cmd, shell=True)
    logger.info("shell 输出 :{}".format(retcode))


def generateHistoryData(date_str):
    #    获取当前交易日，定时任务设置在只在交易日19：00后运行
    #date_str = time.strftime('%Y%m%d', time.localtime(time.time()))
    #date_str = '20220817'
    date_str = str(date_str)
    last_trading_day = s.tradingday(date_str, -1)
    coming_trading_days = s.tradingday(date_str, 2)
    if date_str in coming_trading_days:
        next_trading_day = coming_trading_days[1]
    else:
        next_trading_day = coming_trading_days[0]
    logger.info("下一交易日: {}".format(next_trading_day))

    target_folder = os.path.join(settings.MINUTEDATA_DIR, next_trading_day)
    if os.path.exists(target_folder):
        logger.info("{}文件夹存在，删除文件夹".format(target_folder))
        shutil.rmtree(target_folder)
    os.makedirs(target_folder)

    logger.info("last trade day: ".format(last_trading_day[0]))
    next_zz500, next_hs300 = get_500_300_list(last_trading_day[0])
    
    #    判断预估明日的成分股是否调整
    is_changed = is_index_stock_changed(date_str)

    #    配置并行任务参数
    if is_changed:
        # 生成过去21天数据
        generate_his_data(date_str, 21, target_folder)
    else:
        source_folder = os.path.join(settings.MINUTEDATA_DIR, last_trading_day[0])
        if not os.path.exists(source_folder):
            logger.error("前一交易日历史分钟数据文件夹不存在")
            lm.sendMessage("前一交易日历史分钟数据文件夹不存在")
            # 生成过去21天数据
            generate_his_data(date_str, 21, target_folder)
        else:
            cmd = "rsync -avz {}/*  {}".format(source_folder, target_folder)
            retcode = subprocess.call(cmd, shell=True)
            logger.info("shell 输出 :{}".format(retcode))
            file_list = os.listdir(target_folder)
            if len(file_list) != 21:
                logger.error("拷贝前一交易日历史分钟数据文件数量异常")
                lm.sendMessage("拷贝前一交易日历史分钟数据文件数量异常")
                shutil.rmtree(target_folder)
                generate_his_data(date_str, 21, target_folder)
            else:
                file_list.sort()
                os.remove(os.path.join(target_folder, file_list[0]))
                # 新增最新的一天数据
                generate_his_data(date_str, 1, target_folder)
        today_file = target_folder + '/' + date_str
        if os.path.exists(today_file):
            size = str(os.path.getsize(today_file))
            lm.sendMessage(date_str +' size=' + size)
        else:
            lm.sendMessage(date_str + ' not exists!')

def minute_flag_check(date):
    path0 = flag_rootpath + str(date) + '/' + str(date) + '_tick_concat.success'
    path1 = flag_rootpath + str(date) + '/' + str(date) + '_CFG.success'
    path2 = flag_rootpath + str(date) + '/' + str(date) + '_INDUSTRY.success'
    path3 = flag_rootpath + str(date) + '/' + str(date) + '_INDEX.success'
    path4 = flag_rootpath + str(date) + '/' + str(date) + '_stock_index_future_universe.success'
    return os.path.exists(path0) and os.path.exists(path1) and os.path.exists(path2) and os.path.exists(path3) and os.path.exists(path4)

if __name__ == '__main__':
    
    sdate,edate,cdate_list = check_update_date()
    for date_str in cdate_list:
        while True:
            if minute_flag_check(date_str):
                break
            time.sleep(60)
        print('##################### flag check finished! #####################')
        generateHistoryData(date_str)

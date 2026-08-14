# coding: utf-8
# Author：fengchi863
# Date ：2020/5/30 12:21

import logging
import time
from multiprocessing import Pool

import pandas as pd

from HyperoptApi import hyperopt_wrapper
from conf.model_param_config import *

logger = logging.getLogger()
logger.setLevel(logging.INFO)
rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
log_path = '/data/group/800319/junkData/IntraFactorModel/best_model_hyper_params/Logs/'

log_name = log_path + 'xgb_rise_down_zero_%s.log' % rq
logfile = log_name

fh = logging.FileHandler(logfile, mode='w')
fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
# 第三步，定义handler的输出格式
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
# 第四步，将logger添加到handler里面
logger.addHandler(fh)

root_path = '/data/group/800319/junkData/IntraFactorModel/'


def get_obj(model_type, metrics_type, stk_list, label):
    if model_type not in model_choice:
        raise Exception('Undefined model type')
    model = model_choice[model_type][0](start_date=20170103, end_date=20181231)

    def objective(params):
        pool = Pool(20)
        result_list = {}
        for stk in stk_list:
            para = (stk, label, params)
            result_list[stk] = pool.apply_async(model.training_methodology, (*para,))
            # result_list[stk] = model.training_methodology(stk, label, params)
        metrics_list = []
        for stk in result_list:
            try:
                metrics_list.append(result_list[stk].get()[1][metrics_type])
            except:
                model.training_methodology(stk, label, params)
                logger.info('Wrong:' + str(stk) + str(params))
        result = -1 * np.nanmean(metrics_list)
        logger.info(str(result) + '\t' + str(params))
        return result

    return objective


def run(model_type, metrics_type, stk_list, label):
    objective = get_obj(model_type, metrics_type, stk_list, label)
    best = hyperopt_wrapper(objective, model_choice[model_type][1], max_evals=100)
    return best


para_pool = pd.read_pickle(
    '/data/group/800319/junkData/IntraFactorModel/best_model_hyper_params/para_optimization_pool.pkl')
logger.info('股票池:' + str(para_pool))
best = run('xgb', 'acc', para_pool, 'rise_down_zero')
logger.info('best:' + str(best))
pd.to_pickle(best, root_path + 'best_hyper_params/xgb_param_rise_down_zero.pkl')

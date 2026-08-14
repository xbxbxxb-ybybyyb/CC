# @Time : 2021/3/9 15:14
# @Author : Zhichen Lu
# @File : run_NNExtractor.py
from xquant.compute.aimr import AIMR
import configparser
import os
import json
# conf = configparser.ConfigParser()
# conf.read('/data/group/800319/strategy_local_path_offline/period_info.ini')
# para_list = eval(conf['period_info']['period_info'])
# model_path = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/NNExtractor_ic_half_t_train200_test10_factor_num600_norm_window_40_model_conf/'
# para_list = list(filter(lambda x : not os.path.exists(model_path+'%d.h5'%x[1][1]),para_list))
# idx_list = [x[0] for x in para_list]
# idx_list = list(filter(lambda x : x<73,idx_list))

idx_list = list(range(73))
idx_list = [idx_list[len(idx_list)*i//9:(i+1)*len(idx_list)//9] for i in range(9)]
#idx_list = idx_list[len(idx_list)*i//7:len(idx_list)*(i+1)//7]

params = {
    "parallel_list": idx_list,
    "tag":"xquant",
    "cpu":2,
    "gpu":0,
    "memory":1024*60,
    "preferred_gpu":0
}

AIMR.runTasks('./model/DTCOnlineTest/NNExtractor.py',json.dumps(params))
print("end")
# @Time : 2021/11/23 19:18
# @Author : Zhichen Lu
# @File : exute_file.py
import sys
sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/FactorCalculator_', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/training', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/preprocess', '/data/user/015664/TriggeredTrading'])

import os
from xquant.compute.aimr import AIMR

idx_list = list(range(24,134))
# num = 18
# idx = 4#int(AIMR.getParam())
# idx_list = idx_list[len(idx_list)*idx//num:len(idx_list)*(idx+1)//num]
indicator = 'ic_d'
for i in idx_list:
    param_dict = {
        'pi':i,#第几期
        'feval':indicator,#因子选择指标
        'u':50,#特征数
        'epo':100,#epochs
        'r':0.005,#学习率
        'g':1,#是否使用GPU
        'e':'/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/',
        'o':f'/data/group/800442/800319/MillenniumFalcon/GNNRes/SWMatrix_ic_t/SWMatrix_{indicator}'


    }

    para_line = ''
    for each in param_dict:
        para_line += f' -{each} {param_dict[each]}'

    os.system(f'python3 /data/user/015664/TriggeredTrading/MillenniumFalcon/GraphNN/relation_rank_lstm_ForFix.py '+para_line)


import pandas as pd
import os
from dataApi.FixFactorRollPrepare import  loadFixTensorize
import configparser
from MillenniumFalcon.GraphNN.relation_rank_lstm_ForFix import get_fix_factor_evaluation

conf = configparser.ConfigParser()
conf.read('/data/group/800442/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])

file_list = os.listdir('/data/group/800442/800319/MillenniumFalcon/GNNRes/SWMatrix/')

for each in file_list:
    res = pd.read_pickle(f'/data/group/800442/800319/MillenniumFalcon/GNNRes/SWMatrix/{each}')
    best_valid_pred, best_valid_gt, best_valid_mask, best_test_pred, best_test_gt, best_test_mask = res['res']
    factor_list = get_fix_factor_evaluation('ic_c',100,20170104)
    compare = pd.DataFrame({'actual_label':best_test_gt.flatten(),'prediction':best_test_pred.flatten()})
    print(each,compare.corr())
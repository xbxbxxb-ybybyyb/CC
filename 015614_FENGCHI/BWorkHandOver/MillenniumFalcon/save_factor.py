# @Time : 2021/9/22 9:16
# @Author : Zhichen Lu
# @File : save_factor.py
import sys; print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/FactorCalculator_', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/training', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/preprocess', '/data/user/015664/TriggeredTrading'])

from dataApi.LoadingTool import trans_df2arr
import pandas as pd
import numpy as np
import os,gc,itertools
from tqdm import tqdm

# from MillenniumFalcon.basic_conf import _date_list,_code_list

# source_path = '/data/group/800442/800319/HFfactor/CrossIndustryCorrDot/data_3d_arr/'
# target_path = '/data/group/800442/800319/HFfactor/CrossIndustryCorrDot/data/'

# source_path = '/data/group/800442/800319/HFfactor/CrossIndutryMean/data_3d_arr/'
# target_path = '/data/group/800442/800319/HFfactor/CrossIndutryMean/data/'

source_path = '/data/group/800442/800319/HFfactor/CrossIndutryMean20211104/data_3d_arr/'
target_path = '/data/group/800442/800319/HFfactor/CrossIndutryMean20211104/data2/'


if not os.path.exists(target_path):
    os.makedirs(target_path)
file_list = os.listdir(source_path)


def out_file_formated(file_name,source_path,target_path):
    if os.path.exists(f'{target_path}{file_name}'):
        return
    bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    factor = np.load(f'{source_path}{file_name}')
    factor = factor.reshape((factor.shape[0]*factor.shape[1],factor.shape[2]))
    index = pd.MultiIndex.from_tuples(list(itertools.product(_date_list,bar_list)))
    factor = pd.DataFrame(factor,index=index,columns=_code_list)
    factor_arr = trans_df2arr(factor,start_date=20140801,end_date=_date_list[-1],roll=True)
    factor_arr = factor_arr.astype('float32')
    factor_arr = np.ascontiguousarray(factor_arr)
    np.save(f'{target_path}{file_name}',factor_arr)
    print(file_name,'done')

if __name__ == '__main__':
    from xquant.compute.aimr import AIMR
    from dataApi.tradeDate import get_date_range, get_pre_trade_date
    from dataApi.stockList import get_all_stock_ever_appear

    _code_list = get_all_stock_ever_appear(20210531)
    _date_list = get_date_range(20140701, 20211027)
    _cal_date_list = get_date_range(get_pre_trade_date(_date_list[0], 40), _date_list[-1])

    i = 0#int(AIMR.getParam())
    num = 20
    total = len(file_list)
    para_list = file_list[total*i//num:total*(i+1)//num]
    for each in tqdm(para_list):
        out_file_formated(each,source_path,target_path)

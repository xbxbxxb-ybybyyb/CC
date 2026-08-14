# @Time : 2021/8/30 14:05
# @Author : Zhichen Lu
# @File : FixFactorCrosslize.py
import sys
sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/EnsembleMonitor', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading'])


import numpy as np
import pandas as pd
from CrossFT.basic.crossUtils import *
from CrossFT.basic.crossOperators import *
from online_conf import local_config_path
import itertools
from dataApi.LoadingTool import trans_df2arr
from tqdm import tqdm
from multiprocessing import Pool
from dataApi.usefulTools import delay

FACTOR_PATH = '/data/group/800002/alpha_factor/lib/x_factor_lib/'
availabel_factor_list = pd.read_pickle('/data/group/800319/strategy_local_path3/available_factor_list.pkl')
_bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
_date_list = get_date_range(20140701, 20210531)
_code_list = np.load('/arch1/group/800442/800319/AAcross/basic/code_list.npy').tolist()


def _load_pickle_frame(file_name, date_list, code_list):

    factor_address = '/data/group/800002/alpha_factor/lib/x_factor_lib/'
    freq = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    df_dic = {}
    for time in freq:
        df = pd.read_pickle(factor_address + 'Fix%s_' % time + file_name + '.pkl')
        df.index = df.index.map(int)
        df.columns = df.columns.map(trans_windcode2int)
        df = df.loc[date_list[0]: date_list[-1]]
        df = df.reindex(columns=code_list)
        df_dic[time] = df
    return np.r_['0,3', tuple(df_dic[x].values for x in freq)].transpose(1, 0, 2)

def group_crosslize_factor(factor_name,start,end,out_path,outtype='arr'):
    factor = _load_pickle_frame(factor_name,_date_list,code_list=_code_list)
    group_factor = load_material('sw1', _date_list[0], _date_list[-1],freq='30mins',address= '/arch1/group/800442/800319/AAcross/basic/groups')
    group_factor = delay(group_factor[:,:7,:])
    sw_group = sameshape(factor,group_factor)
    mean = st2groupst(factor,sw_group,cross_mean)
    std = st2groupst(factor,sw_group,cross_std)
    group_normalized_factor = (factor - mean)/std
    group_normalized_factor = pd.DataFrame(group_normalized_factor.reshape((factor.shape[0]*factor.shape[1],factor.shape[-1])),
                                           index=pd.MultiIndex.from_tuples(list(itertools.product(_date_list,_bar_list))),
                                           columns=_code_list)
    if outtype=='arr':
        factor_arr = trans_df2arr(group_normalized_factor,start,end,roll=True)
        np.save(f'{out_path}/{factor_name}.npy',np.ascontiguousarray(factor_arr.astype('float32')))
    elif outtype=='df':
        pd.to_pickle(group_normalized_factor,f'{out_path}/{factor_name}.pkl')
    else:
        raise Exception('Wrong type')
    print(factor_name,'done')


def main():
    out_path = '/data/group/800442/800319/HFfactor/RealTimeFixRollCrosslizeDelay1SW/data/'
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    for fname in tqdm(availabel_factor_list):
        if os.path.exists(f'{out_path}{fname}.npy'):
            continue
        group_crosslize_factor(fname,20140801,20210531,out_path)
        print(fname)

def main_multi(n,target_list):
    out_path = '/data/group/800442/800319/HFfactor/RealTimeFixRollCrosslizeDelay1SW/data/'
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    bar = tqdm(total=len(target_list))

    def update(*para):
        bar.update()
        if bar.last_print_n >= bar.total:
            bar.close()

    pool = Pool(n)
    for fname in target_list:
        if os.path.exists(f'{out_path}{fname}.npy'):
            continue
        pool.apply_async(group_crosslize_factor,(fname,20140801,20210531,out_path),callback=update)

    pool.close()
    pool.join()

if __name__ == '__main__':
    # main()

    i = 4

    main_multi(6,availabel_factor_list[i*250:(i+1)*250])



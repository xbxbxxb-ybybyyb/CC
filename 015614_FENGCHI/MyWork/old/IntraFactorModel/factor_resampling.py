# @Time : 2020/4/28 17:14
# @Author : Zhichen Lu
# @File : factor_resampling.py

import os
from multiprocessing import Pool

import gc
import pandas as pd

# base_path = '/data/group/800319/storeFactor/intrafactor/'
outpath = '/data/group/800319/junkData/IntraFactorModel/intrafactor_from2017_whole_mkt_temp20200708/'
stk_factor_path = '/data/group/800319/junkData/IntraFactorModel/FactorByStock_from2017_whole_mkt/'

# trash_list = os.listdir(outpath)
# for each in trash_list:
#     os.remove(stk_factor_path+re)

trash_list = os.listdir(outpath)
# for each in trash_list:
def wraper(each):
    os.remove(outpath + each)
    print(each, 'done')


pool = Pool(20)
pool.map(wraper, trash_list)
pool.close()
pool.join()

for path in [outpath, stk_factor_path]:
    if not os.path.exists(path):
        os.mkdir(path)

for path in [outpath, stk_factor_path]:
    if not os.path.exists(path):
        os.mkdir(path)


def out_pitches(factor_name):
    file_list = os.listdir(outpath)
    file_list = list(filter(lambda x: factor_name + '_' in x, file_list))
    if len(file_list) == 3561:
        print(factor_name, 'already finished')
        return 0
    factor = pd.read_hdf(base_path + factor_name, factor_name.replace('.h5', ''))
    factor_name = factor_name.replace('.h5', '').strip()
    for col in factor.columns:
        if os.path.exists(outpath + factor_name + '_%d.pkl' % col):
            continue
        pd.to_pickle(factor.loc[(20170103, 925):(20191231, 1500), [col]], outpath + factor_name + '_%d.pkl' % col)
        # print(factor_name,col)
    del factor
    gc.collect()
    print(factor_name, 'done')


def calc_pitches(n):
    file_list = os.listdir(base_path)
    # exist_list = '\nalpha168 done\nfactor64 done\nfactor106 done\nalpha153 done\nfactor98 done\nalpha142 done\nfactor71 done\nalpha163 done\nalpha133_1 done\nalpha9 done\nfactor81 done\nalpha184 done\nfactor99 done\nfactor_dev04 done\nalpha10 done\nalpha36 done\nfactor110 done\nalpha13 done\nalpha2 done\nalpha191 done\nfactor86 done\nfactor91 done\nalpha39 done\nalpha18 done\nalpha170 done\nalpha41 done\nboll3 done\nalpha14 done\nalpha145 done\nalpha169 done\nfactor68 done\nalpha29 done\nalpha53 done\nalpha32 done\nboll1 done\nfactor74 done\nalpha38 done\nboll8 done\nboll5 done\nalpha124 done\nalpha35 done\nalpha135 done\nfactor103 done\nalpha4 done\nalpha31 done\nfactor62 done\nalpha1 done\nfactor94 done\nalpha129 done\nboll4 done\nalpha188 done\nalpha60 done\nfactor101 done\nalpha166 done\nfactor73 done\nfactor112 done\nalpha178 done\nalpha49 done\nalpha19 done\nboll6 done\nalpha47 done\nalpha24 done\nalpha156 done\nalpha21 done\nalpha161 done\nalpha50 done\nboll2 done\nalpha43 done\nalpha176 done\nboll11 done\nalpha45 done\nfactor118 done\nalpha56 done\nfactor87 done\nalpha151 done\nalpha126_2 done\nalpha139 done\nfactor90 done\nfactor_dev02 done\nfactor63 done\nboll7 done\nalpha123 done\nalpha25 done\nfactor75 done\nfactor_dev05 done\nalpha133_2 done\nalpha134 done\nfactor61 done\nalpha180 done\nalpha28 done\nalpha42 done\nfactor113 done\nalpha17 done\nalpha3 done\nalpha164 done\nalpha23 done\nalpha16 done\nalpha7 done\nalpha127 done\nalpha58 done\nboll12 done\nfactor114 done\nalpha179 done\nfactor_dev01 done\nfactor83 done\nfactor120 done\nfactor_dev08 done\nalpha22 done\nalpha37 done\nfactor69 done\nalpha175 done\nfactor_dev07 done\nfactor_dev03 done\nalpha40 done\nalpha174 done\nalpha5 done\nalpha187 done\nalpha140 done\nalpha141 done\nfactor92 done\nalpha8 done\nalpha171 done\nboll10 done\nalpha57 done\nalpha12 done\nalpha181 done\nfactor119 done\nalpha27 done\nalpha189 done\nalpha126_1 done\nalpha122 done\nfactor107 done\nfactor78 done\nfactor72 done\nalpha59 done\nalpha11 done\nalpha147 done\nalpha167 done\nalpha46 done\nfactor105 done\nalpha48 done\nalpha177 done\nfactor116 done\nalpha55 done\nalpha52 done\nboll5 done\nfactor_dev05 done\nalpha5 done\nfactor75 done\n'
    # exist_list = exist_list.split('\n')
    # exist_list = [x.split(' ')[0] for x in exist_list]
    # file_list = list(filter(lambda x : not x.strip('.h5') in exist_list,file_list))
    pool = Pool(n)
    r = pool.map(out_pitches, file_list)
    pool.close()
    pool.join()

pitches_list = os.listdir(outpath)
# factor_list = list(set([x.split('_')[0] for x in pitches_list]))
stk_list = list(set([x.split('_')[-1] for x in pitches_list]))

def calc_FactorByStock(stk_id):
    if os.path.exists(stk_factor_path + stk_id):
        print(stk_id, 'exist')
        return 0
    file_list = list(filter(lambda x: '_' + stk_id in x, pitches_list))
    factor_df = pd.DataFrame()
    for file_name in file_list:
        temp_factor = pd.read_pickle(outpath + file_name)
        temp_factor.columns = [file_name.strip(stk_id).strip().strip('_')]
        factor_df = pd.concat([factor_df, temp_factor], axis=1)
    pd.to_pickle(factor_df, stk_factor_path + stk_id)
    del factor_df
    gc.collect()
    print(stk_id, 'done')

def wraper(stk_id):
    calc_FactorByStock(stk_id)
    gc.collect()


if __name__ == "__main__":
    # calc_FactorByStock('2618.pkl')
    # calc_FactorByStock('603227.pkl')
    # calc_pitches(5)
    # calc_pitches
    # print(1,stk_list)
    pool = Pool(10)
    stk_list.sort()
    # # 倒序
    r = pool.map(wraper, stk_list)
    pool.close()
    pool.join()

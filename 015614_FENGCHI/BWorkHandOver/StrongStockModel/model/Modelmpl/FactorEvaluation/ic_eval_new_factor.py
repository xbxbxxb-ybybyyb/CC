# @Time : 2021/8/2 13:28
# @Author : Zhichen Lu
# @File : ic_eval_new_factor.py
import pandas as pd
import os
from StrongStockModel.conf.path_config import root_path
from tqdm import tqdm

out_path = f'{root_path}external_data/Delta毒株疫情时代因子评估/'
if not os.path.exists(out_path):
    os.mkdir(out_path)

path_wyl = '/arch1/group/800442/800319/MinFactor/TestResult/20210730WYL/result/'
path_wyl2 = '/arch1/group/800442/800319/MinFactor/TestResult/20210802WYL/result/'
path_hx = '/arch1/group/800442/800319/MinFactor/TestResult/20210722HANXU/result/'

file_list = os.listdir(path_hx)
indicator_list = [ 'ic_all_dtc', 'ic_all_d', 'ic_all_t', 'ic_all_c',
       'ic_all_dt', 'ic_all_tc', 'ic_all_dc', 'ic_h1_dtc', 'ic_h1_d',
       'ic_h1_t', 'ic_h1_c', 'ic_h1_dt', 'ic_h1_tc', 'ic_h1_dc', 'ic_h2_dtc',
       'ic_h2_d', 'ic_h2_t', 'ic_h2_c', 'ic_h2_dt', 'ic_h2_tc', 'ic_h2_dc']


for each in file_list:
    date = int(each[:-5])
    h1_date = int(each[:-5])//10000* 10000+101

    hx = pd.read_excel(f'{path_hx}{each}',index_col=0)
    wyl = pd.read_excel(f'{path_wyl}{each}',index_col=0)
    wyl2 = pd.read_excel(f'{path_wyl2}{each}',index_col=0)

    for indicator in indicator_list:

        if '1' in indicator:
            target_indicator = indicator.replace('1','')
            target_date = h1_date
        elif '2' in indicator:
            target_indicator = indicator.replace('2','')
            target_date = date
        else:
            target_date = date
            target_indicator = indicator

        for sub in ['HX_union_WYL', 'HX', 'WYL','WYL2']:
            if not os.path.exists(f'{out_path}{sub}/{target_indicator}/'):
                os.makedirs(f'{out_path}{sub}/{target_indicator}/')
        res_hx = hx[indicator].apply(abs).sort_values(ascending=False)#.index.tolist()[:200]
        pd.to_pickle(res_hx,f'{out_path}HX/{target_indicator}/{target_date}.pkl')

        res_wyl = wyl[indicator].apply(abs).sort_values(ascending=False)#.index.tolist()[:200]
        pd.to_pickle(res_wyl,f'{out_path}WYL/{target_indicator}/{target_date}.pkl')

        res_wyl2 = wyl2[indicator].apply(abs).sort_values(ascending=False)#.index.tolist()[:200]
        pd.to_pickle(res_wyl2,f'{out_path}WYL2/{target_indicator}/{target_date}.pkl')

        res_union = pd.concat([hx[indicator],wyl[indicator],wyl2[indicator]]).apply(abs).sort_values(ascending=False)

        pd.to_pickle(res_union,f'{out_path}HX_union_WYL/{target_indicator}/{target_date}.pkl')


sub = 'HX'
for sub in ['HX','WYL','HX_union_WYL']:
    all_res = set([])
    for indicator in ['ic_h_d','ic_h_t','ic_h_c','ic_all_d', 'ic_all_t', 'ic_all_c']:
        path = f'/data/group/800442/800319/junkData/StrongStock/external_data/Delta毒株疫情时代因子评估/{sub}/{indicator}/'
        res = set([])
        file_list = os.listdir(path)
        for each in file_list:
            temp = pd.read_pickle(f'/data/group/800442/800319/junkData/StrongStock/external_data/Delta毒株疫情时代因子评估/{sub}/{indicator}/{each}')
            res = res.union(temp.index.tolist()[:200])
        pd.to_pickle(res,f'/data/group/800442/800319/junkData/StrongStock/external_data/Delta毒株疫情时代因子评估/{sub}/{indicator}_all_union.pkl')

        all_res = all_res.union(res)
    pd.to_pickle(all_res,f'/data/group/800442/800319/junkData/StrongStock/external_data/Delta毒株疫情时代因子评估/{sub}_selected.pkl')

factor_HX = pd.read_pickle(f'/data/group/800442/800319/junkData/StrongStock/external_data/Delta毒株疫情时代因子评估/HX_selected.pkl')
factor_HX_uion_WYL = pd.read_pickle(f'/data/group/800442/800319/junkData/StrongStock/external_data/Delta毒株疫情时代因子评估/HX_union_WYL_selected.pkl')

pd.to_pickle(factor_HX - factor_HX_uion_WYL,f'/data/group/800442/800319/junkData/StrongStock/external_data/Delta毒株疫情时代因子评估/HX_sub_selected.pkl')




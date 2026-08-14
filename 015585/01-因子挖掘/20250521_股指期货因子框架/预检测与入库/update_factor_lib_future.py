# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
import IO
import warnings
warnings.filterwarnings('ignore')

def summary_inf(in_pkl, out_pkl,factor_type):
    res = {'in_score':in_pkl['check_score_res'].values[-1][-1],
           'out_score':out_pkl['check_score_res'].values[-1][-1],
           'in_IC_tot':in_pkl['corr_sta']['value']['corr_tot'],
           'in_IC_mean_std':in_pkl['corr_sta']['value']['corr_month_mean_std'],
           'out_IC_tot':out_pkl['corr_sta']['value']['corr_tot'],
           'out_IC_mean_std':out_pkl['corr_sta']['value']['corr_month_mean_std'],
           'Mutual_Info':out_pkl['corr_sta']['value']['mic_tot']}
    res['tot_score'] = res['in_score'] + res['out_score']

    score = 30 if factor_type in ['T-1_factor'] else 60 # qyh：这里要根据评分阈值改
    linear_test = (res['tot_score']>score) & (res['out_score'] / res['in_score']>0.6)
    res['bank_type'] = 'linear' if linear_test else 'nonlinear'
    return res


in_interval = [20220801, 20231231] # qyh:先模拟了一个样本内外时间，后续看情况调整
out_interval = [20240101, 20241231]
max_corr = 0.7
# qyh：以下地址全部要改
factor_data_path='/data/user/018107/factor_zoo1/all_factor/europa/'#因子数据
pre_check_path= '/data/user/018107/factor_zoo1/all_precheck/europa/'#预检测
factor_test_path='/data/user/018107/factor_zoo1/all_factortest/europa/all/'#因子报告
res_path = '/data/user/018107/factor_zoo1/factor_lib_v3/' #结果地址
res_public_path = '/data/group/800463/data/project1_public/factor_lib_v3/' #公共结果地址
sft_basic_path = '%s/sft_init_europa.h5'%(res_path) #初始地址 qyh：看情况改成sft_init_future.h5
all_factor_for_left=pd.read_pickle('/data/user/018107/factor_zoo1/factor_bank/europa/20231102/all_factor_df.pkl').loc[pd.Timestamp(str(in_interval[0])):pd.Timestamp(str(out_interval[1]))]

# 读取因子列表
df_dic = pd.read_excel('/data/user/018107/factor_zoo1/alternate_factor_inf.xlsx', sheet_name=None)#qyh：要改
# df_dic['emotion_factor']=df_dic['emotion_factor'][df_dic['emotion_factor']['factor_in']]
test_factor_inf = pd.concat(df_dic.values(),sort=False).reset_index()
other_basic_list= list(test_factor_inf[test_factor_inf['factor_owner'].isin(['other_basic'])]['factor_name'].values)
test_factor_inf = test_factor_inf[~((test_factor_inf['factor_type'].isin(['label','other']))|(test_factor_inf['factor_owner']=='other_basic'))]
test_factor_inf= test_factor_inf[test_factor_inf['factor_type'].isin(['T-1_factor', 'TTransaction', 'TEmotion', 'T-1_Emotion','TTickabAll','TOrder',
                                                                      'LastTouchTTick','TTransaction_TTickab', 'TTransaction_TOrder', 'TOrder_TTickab'])]

check_res_cols = ['factor_name', 'pre_check', 'in_score', 'out_score', 'in_IC_tot', 'in_IC_mean_std', 'out_IC_tot', 'out_IC_mean_std', 'Mutual_Info', 'tot_score', 'bank_type', '入库情况', '入库时间', '出库时间']
test_date_list = list(test_factor_inf['factor_date'].unique())
test_date_list.sort()

last_test_date = test_date_list[-2]#如果是None，则是从头开始；如果是test_date_list[-2]，则是从上一日期开始
start_index = 0 if last_test_date is None else test_date_list.index(last_test_date)+1

for test_date in test_date_list[start_index:]:
    print('-'*40, test_date, '-'*40)
    if last_test_date is None:
        start_index = 0
        all_factor_df = IO.read_data([in_interval[0], out_interval[1]], alt=sft_basic_path)
        check_res_inf = pd.DataFrame(columns=check_res_cols)
    else:
        start_index = test_date_list.index(last_test_date)
        all_factor_df = pd.read_pickle(res_path + 'all_factor_df/all_factor_df_%s.pkl' % (last_test_date))
        check_res_inf = pd.read_excel(res_path + 'check_res/check_res_tot_europa_%d.xlsx' % (last_test_date))[check_res_cols] # qyh：这里要改策略名

    day_factor_inf = test_factor_inf[test_factor_inf['factor_date']==test_date].copy()
    for index, inf in day_factor_inf.iterrows():
        factor_name, factor_type, factor_owner = inf['factor_name'], inf['factor_type'], inf['factor_owner']

        #预检测
        pre_check = pd.read_pickle('%s/%s.pkl' % (pre_check_path, factor_name))
        pre_check['check_inf'] ='pass' if pre_check['预检测']=='pass' else pre_check.astype('str').sum().replace('not pass','').replace('pass','')
        factor_res = {'factor_name':factor_name, 'pre_check': pre_check['check_inf']}
        if factor_res['pre_check']!='pass':
            check_res_inf = check_res_inf.append(pd.DataFrame(factor_res.values(), index=factor_res.keys()).T)[check_res_cols]
            print(factor_res)
            continue

        #因子报告
        in_pkl = pd.read_pickle('%s/%d_%d/%s.pkl'%(factor_test_path, in_interval[0], in_interval[1], factor_name))
        out_pkl = pd.read_pickle('%s/%d_%d/%s.pkl' % (factor_test_path, out_interval[0], out_interval[1], factor_name))

        #因子值
        if factor_type not in ['T-1_Emotion','TEmotion']:
            test_factor_df = IO.read_data([in_interval[0], out_interval[1]], alt='%s/%s/%s.h5'%(factor_data_path,factor_name, factor_name) )
        else:
            test_factor_df =pd.read_pickle('%s/%s/%s.pkl' % (factor_data_path, factor_name, factor_name)).loc[pd.Timestamp(str(in_interval[0])):pd.Timestamp(str(out_interval[1]))]

        # 样本筛选，qyh:这里删去了filter
        all_factor_df1 = all_factor_df.copy()

        test_factor_df = test_factor_df.reindex(all_factor_df.index)
        test_factor_df1 = test_factor_df.reindex(all_factor_df1.index)
        corr_factor_ser = all_factor_df1.rank().corrwith(test_factor_df1[factor_name].rank()).abs() #比直接使用spearman更快
        high_corr_factor_list = list(corr_factor_ser[corr_factor_ser>max_corr].index) if len(all_factor_df.columns)>0 else []
        high_corr_factor_list=[f for f in high_corr_factor_list if f in list(test_factor_inf['factor_name'].values)+other_basic_list]
        factor_res = {**factor_res, **summary_inf(in_pkl, out_pkl,factor_type)}
        #---------------------------------------------------------------------------------------------------------------
        #score = 30 if factor_type in ['T-1_factor'] else 60
        if factor_res['bank_type'] !='linear':
            #入库门槛
            factor_res['入库情况'] = '入库失败-未达到入库阈值'

        else:
            if len(high_corr_factor_list)==0:
                # 因子库内没有高相关
                factor_res['入库情况'] = '入库成功-没有高相关'
            else:
                # 因子库内存在高相关因子
                high_corr_other_basic=[f for f in high_corr_factor_list if f in other_basic_list]
                if len(high_corr_other_basic)>0:
                    #与other_basic类因子高相关，无法入库
                    factor_res['入库情况'] = '入库失败-与other_basic类因子高相关%s' % (high_corr_other_basic)
                else:
                    corr_factor_bank_type = 'linear' if 'linear' in list(check_res_inf[check_res_inf['factor_name'].isin(high_corr_factor_list)]['bank_type']) else 'nonlinear'
                    if (factor_res['bank_type'] == 'linear') and (corr_factor_bank_type == 'nonlinear'):
                        # 挤出高相关因子
                        factor_res['入库情况'] = '入库成功-挤出高相关非线性因子%s'%(high_corr_factor_list)
                    elif (factor_res['bank_type'] == 'nonlinear') and (corr_factor_bank_type == 'linear'):
                        # 新因子未非线性，无法入库
                        factor_res['入库情况'] = '入库失败-存在高相关线性因子%s'%(high_corr_factor_list)
                    elif (factor_res['bank_type'] == 'linear') and (corr_factor_bank_type == 'linear'):
                        # 都为线性，比较得分
                        corr_max_tot_score = check_res_inf[check_res_inf['factor_name'].apply(lambda x:x in high_corr_factor_list)]['tot_score'].max()
                        if factor_res['tot_score'] - corr_max_tot_score >= 5:
                            factor_res['入库情况'] = '入库成功-挤出线性高相关因子%s'%(high_corr_factor_list)
                        else:
                            factor_res['入库情况'] = '入库失败-存在得分更高的线性高相关因子%s'%(high_corr_factor_list)
                    elif (factor_res['bank_type'] == 'nonlinear') and (corr_factor_bank_type == 'nonlinear'):
                        # 都为非线性，比较互信息
                        corr_max_mic = check_res_inf[check_res_inf['factor_name'].apply(lambda x:x in high_corr_factor_list)]['Mutual_Info'].max()
                        if (factor_res['Mutual_Info'] / corr_max_mic -1 > 0.05):
                            factor_res['入库情况'] = '入库成功-挤出非线性高相关因子%s'%(high_corr_factor_list)
                        else:
                            factor_res['入库情况'] = '入库失败-存在互信息更高的非线性高相关因子%s'%(high_corr_factor_list)

        factor_res['入库时间'] = test_date if factor_res['入库情况'][:4] == '入库成功' else np.nan
        factor_res['出库时间'] = np.nan
        # ---------------------------------------------------------------------------------------------------------------
        check_res_inf = check_res_inf.append(pd.DataFrame(factor_res.values(), index=factor_res.keys()).T)
        if (np.isnan(factor_res['入库时间'])==False):
            all_factor_df[factor_name] = test_factor_df[factor_name]
            if (len(high_corr_factor_list)>0):
                check_res_inf.loc[check_res_inf['factor_name'].apply(lambda x:x in high_corr_factor_list), '出库时间'] = test_date
                all_factor_df = all_factor_df.drop(high_corr_factor_list, axis=1)
        print(factor_res)

    all_factor_df.to_pickle(res_path + 'all_factor_df/all_factor_df_%s.pkl' % (test_date))
    check_res_inf_ = test_factor_inf.join(check_res_inf.set_index('factor_name'), on='factor_name').sort_values(['factor_date','index'])
    check_res_inf_ = check_res_inf_[check_res_inf_['factor_date']<=test_date].drop(columns=['factor_explain','填充值','是否针对注册制做调整','T-1日类别','逻辑类别','是否低耗时因子'])
    check_res_inf_.to_excel(res_path + 'check_res/check_res_tot_europa_%d.xlsx' % (test_date),index=False)
    last_test_date = test_date
    #输出结果
    update_file=res_path+'sft_update_europa.h5' # qyh：这里修改
    if not os.path.exists(update_file):
        IO.pd_hdf5_writer(all_factor_df, update_file, dataset='data')
    else:
        IO.pd_hdf5_writer(all_factor_df, update_file, dataset='data', override=True)

    #公共地址输出结果
    check_res_inf_.to_excel(res_public_path + 'check_res_tot_europa.xlsx', index=False) # qyh：这里修改
    update_public_file=res_public_path+'sft_update_europa.h5' # qyh：这里修改
    if not os.path.exists(update_public_file):
        IO.pd_hdf5_writer(all_factor_df.loc[pd.to_datetime(str(in_interval[0])):pd.to_datetime(str(in_interval[1]))], update_public_file, dataset='data')
    else:
        IO.pd_hdf5_writer(all_factor_df.loc[pd.to_datetime(str(in_interval[0])):pd.to_datetime(str(in_interval[1]))], update_public_file, dataset='data', override=True)



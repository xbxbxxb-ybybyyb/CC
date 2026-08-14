# -*- coding: utf-8 -*-
from xquant.compute.aimr import AIMR
import os
import pandas as pd
import numpy as np
import datetime as dt
import importlib
import IO
from xquant.factordata import FactorData
import run_factor_demo_parallel_im as run
import sys
s = FactorData()
def get_use_data(py_code):
    def remove_space(code):
        while (len(code)>0 and code[0]==' '):
            code = code[1:]
        return code
    data_dic = {'/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5': 'MD',
                '/data/group/800463/data/generalStrong/minute5/': 'minute5',
                '/data/group/800463/data/generalStrong/ordersheet5_new/': 'ordersheet5',
                '/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5': 'AShareMoneyFlow',
                '/data/group/800080/warehouse/prod/RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5': 'RISK',
                '/data/group/800080/warehouse/prod/DATABASE/WIND/AShareEODDerivativeIndicator/AShareEODDerivativeIndicator.h5': 'AShareEODDerivativeIndicator',
                '/data/group/800080/warehouse/prod/DATABASE/WIND/AIndexEODPrices/AIndexEODPrices.h5':'AIndexEODPrices',
                '/data/group/800080/warehouse/prod/DATABASE/WIND/AIndexValuation/AIndexValuation.h5':'AIndexValuation',
                '/data/group/800080/warehouse/prod/DATABASE/WIND/AShareDescription/AShareDescription.h5': 'AShareDescription',
                '/data/group/800080/warehouse/prod/UNIV/CHINA_STOCK/DAILY/OPTM/UNIV_CHINA_STOCK_DAILY_OPTM.h5':'UNIV',
                '/data/group/800463/data/generalStrong/concept_h5_except_300/':'concept'
                }
    data_use_list = []
    for i in range(len(py_code)):
        code = py_code[i]
        code = remove_space(code)
        if (len(code)==0) or (code[0] == '#'):
            continue

        if ('/data/group/' in code) or ('/data/user/' in code):
            use_data = code
            for key, value in data_dic.items():
                if key in code:
                    use_data = value
                    break
            data_use_list.append(use_data)
    return data_use_list

def format_check(factor_name, factor_type, check_date, before_submit_name_list):
    print('代码格式检查', dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    if factor_name in before_submit_name_list:
        return '因子名称之前已经出现过;' ,None

    if factor_type not in ['T-1_factor', 'TTickabAll',]:
        return '因子类型不符合规定;', None
    try:
        modname = 'func_check.factor_%d.factor_%s' % (check_date, factor_name)
        module = importlib.import_module(modname)
    except Exception as e:
        return '文件名不符合规定-%s;'%(e), None

    try:
        func = getattr(module, 'factor_%s' % (factor_name))
    except Exception as e:
        return '函数名不符合规定-%s;'%(e), None

    try:
        ret_dic = func(None, None, None, True) if factor_type in ['T-1_factor', 'other'] else func(None, True)
        factor = list(ret_dic.keys())
        if factor_type in ['T-1_factor', 'other']:
            if 'data' in factor:
                factor.remove('data')
            elif check_date>20200101:#check_date>20200402:
                return 'return_fillna_dic中没有data字段', None

        if factor[0] != factor_name:
            return 'return_fillna_dic不符合规定;', None

        if (factor_type in ['T-1_factor', 'other']) and (check_date>20200101):
            dic_use_data = ret_dic['data']
            f = open('func_check/factor_%d/factor_%s.py'%(check_date, factor_name))
            py_code = f.readlines()
            real_use_data = get_use_data(py_code)
            if (len(set(dic_use_data) - set(real_use_data))>0) or (len(set(real_use_data)-set(dic_use_data))>0):
                return 'return_fillna_dic中data列举错误,列举%s-实际使用%s;'%(dic_use_data, real_use_data), None
    except Exception as e:
        print(e)
        return 'return_fillna_dic不符合规定-%s;'%(e), None

    try:
        # trans_df = pd.read_pickle('/data/group/800463/data/project1_prod/transaction_test_001_ezt/20160104.pkl')
        tick_df = pd.read_pickle('/dfs/group/800463/data/projectF_prod/IM_tick/20220801/143000000.pkl') # /data/group/800463/data/project1_prod/tickab_test_001/20160104.pkl
        # order_df = pd.read_pickle('/data/group/800463/data/project1_prod/order_test_001/20160104.pkl')
        if (factor_type in ['T-1_factor', 'other']):
            factor_df = func(20200206, 20200206, IO)
            if factor_df.columns[0] != factor_name:
                return '列名与因子名不符;', None
        # elif factor_type in ['TTransaction']:
        #     trans_df = trans_df[trans_df['ff_shares']==trans_df['ff_shares'].iloc[0]]
        #     factor_dic = func(trans_df)
        #     if list(factor_dic.keys())[0] != factor_name:
        #         return '字典key与因子名不符;', None
        # elif factor_type in ['TOrder']:
        #     order_df = order_df[order_df['ff_shares'] == order_df['ff_shares'].iloc[0]]
        #     factor_dic = func(order_df)
        #     if list(factor_dic.keys())[0] != factor_name:
        #         return '字典key与因子名不符;', None
        elif factor_type == 'TTickabAll':
            # tick_df = tick_df[tick_df['ff_shares'] == tick_df['ff_shares'].iloc[0]]
            factor_dic = func(tick_df)
            if list(factor_dic.keys())[0] != factor_name:
                return '字典key与因子名不符;', None
    except Exception as e:
        return '函数运行出错-%s'%(e), None

    return 'pass', func


def value_same_check(func, factor_name, result_path,filter_df):
    print('因子一致检查', dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    long_interval = [20220801, 20250430]
    short_interval_list = s.tradingday(20150901, 20150907) # qyh:以后有t_1_factor这里也要改
    short_interval_list += s.tradingday(20190925, 20190930)
    short_interval_list += s.tradingday(20190715, 20190731)
    short_interval_list = [int(tradingday) for tradingday in short_interval_list]

    try:
        if os.path.exists('%s%s_%d_%d.pkl'%(result_path, factor_name, long_interval[0], long_interval[1])):
            long_df = pd.read_pickle('%s%s_%d_%d.pkl'%(result_path, factor_name, long_interval[0], long_interval[1]))
        else:
            long_df = func(long_interval[0], long_interval[1], IO)
            long_df = long_df.fillna(func(None, None, None, return_fillna_dic=True))
            if not os.path.exists(result_path):
                os.makedirs(result_path)
            long_df.to_pickle('%s%s_%d_%d.pkl'%(result_path, factor_name, long_interval[0], long_interval[1]))
        if int(np.isinf(long_df).sum())>0:
            return '因子值存在inf'
    except Exception as e:
        return '函数测试出错-测试区间:%d-%d-%s'%(long_interval[0], long_interval[1], e)

    try:
        fill_dic = func(None, None, None, return_fillna_dic=True)
        for short_date in short_interval_list:
            if os.path.exists('%s%s_%d_%d.pkl'%(result_path, factor_name, short_date, short_date)):
                short_df = pd.read_pickle('%s%s_%d_%d.pkl'%(result_path, factor_name, short_date, short_date))
            else:
                short_df = func(short_date, short_date, IO).fillna(fill_dic)
                short_df.to_pickle('%s%s_%d_%d.pkl' % (result_path, factor_name, short_date, short_date))
            short_df = short_df.loc[pd.Timestamp(str(short_date))]
            tmp_long_df = long_df.loc[pd.Timestamp(str(short_date))]
            basic_index = filter_df.loc[pd.Timestamp(str(short_date))].index
            if np.nanmax((short_df - tmp_long_df).abs().values) > 1e-8:
                print('因子值不一致1-计算区间:%d-%d和%d-%d'%(long_interval[0], long_interval[1], short_date, short_date))
                print((short_df - tmp_long_df).abs().idxmax(),np.nanmax((short_df - tmp_long_df).abs().values))
                return '因子值不一致1-计算区间:%d-%d和%d-%d'%(long_interval[0], long_interval[1], short_date, short_date)
            if np.nanmax((short_df.reindex(basic_index).fillna(fill_dic) - tmp_long_df.reindex(basic_index).fillna(fill_dic)).abs().values) > 1e-8:
                return '因子值不一致2-计算区间:%d-%d和%d-%d'%(long_interval[0], long_interval[1], short_date, short_date)
    except Exception as e:
        return '函数测试出错-测试区间:%d-%d-%s'%(short_date, short_date, e)
    return 'pass'

def run_func_test(func,factor_name, factor_type, basic_file_path,factor_data_path):
    start_date, end_date=20160101,20190930
    run_start_date,run_end_date=20150901,20230331
    print('函数运行检查', dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    factor_file_path = factor_data_path + '%s/' % (factor_name)
    if not os.path.exists(factor_file_path):
        os.makedirs(factor_file_path)
    try:
        if not os.path.exists(factor_file_path+'/%s.h5'%(factor_name)):
            run.run_factor(func,factor_name=factor_name,factor_type=factor_type,
                                              start_date=run_start_date,end_date=run_end_date,
                                              basic_file_path=basic_file_path,
                                              result_path=factor_file_path,
                                              # emotion_data=emotion_data,
                                              append_next_tradingday=False,
                                              interval_res=False,
                                              data_path_dic=data_path_dic)
        factor_df = IO.read_data([start_date,end_date],alt=factor_file_path+'/%s.h5'%(factor_name))
        if int(np.isinf(factor_df).sum())>0:
            return '因子值存在inf'
        if factor_df[factor_df.columns[0]].std() == 0:
            return '因子值全部值为常数'
        if factor_df.columns[0] != factor_name:
            return '列名与因子名不符'
    except Exception as e:
        return '函数运行出错-计算区间:%d-%d-%s' % (run_start_date, run_end_date, e)
    return 'pass'

def score_check(factor_name,filter_df_2225,factor_data_path):
    print('因子测试', dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    factor_file_path = factor_data_path + '%s/' % (factor_name)
    try:
        all_sample_df = pd.read_hdf(factor_file_path + '/%s.h5' % (factor_name))

        same_rate = (all_sample_df.reindex(filter_df_2225.index)[factor_name].value_counts().max() / len(all_sample_df.reindex(filter_df_2225.index)))
        if same_rate > 0.8:
            return '相同值比例较高-%.2f%%' % (same_rate * 100)
        if ('yzhan' in factor_name) and (same_rate > 0.2):
            return '相同值比例较高-%.2f%%' % (same_rate * 100)

        factor_mean = abs(all_sample_df.reindex(filter_df_2225.index)[factor_name].mean())
        factor_std = all_sample_df.reindex(filter_df_2225.index)[factor_name].std()
        factor_lsd = factor_std / factor_mean
        if (factor_mean < 0.001) and (factor_std < 0.001):
            return '因子波动小-std:%.8f,mean:%.8f' % (factor_mean, factor_std)

        if factor_lsd < 0.01:
            print('离散度太低-暂未为筛选指标！！！！！！！！！！！')

        return 'pass'
    except Exception as e:
        return e

def pre_check(factor_name, factor_type, factor_date,check_res_path, before_submit_name_list,basic_file_path,factor_data_path,filter_df,filter_df_2225):
    check_dic = {'代码格式检查': '', '因子值一致性检查': '', '函数运行检查': '', '因子测试' : '','预检测':'not pass'}

    check_dic['代码格式检查'], func = format_check(factor_name, factor_type, factor_date, before_submit_name_list)
    if check_dic['代码格式检查']!='pass': return pd.Series(check_dic)

    if factor_type in ['T-1_factor', 'other']:
        check_dic['因子值一致性检查'] = value_same_check(func, factor_name, check_res_path + '/same_test/',filter_df)
    else:
        check_dic['因子值一致性检查'] = 'pass'
    if check_dic['因子值一致性检查'] != 'pass': return pd.Series(check_dic)

    check_dic['函数运行检查'] = run_func_test(func,factor_name, factor_type, basic_file_path,factor_data_path)
    if check_dic['函数运行检查'] != 'pass': return pd.Series(check_dic)

    check_dic['因子测试'] = score_check(factor_name,filter_df_2225,factor_data_path)

    if check_dic['因子测试']=='pass':
        check_dic['预检测'] = 'pass'
    return pd.Series(check_dic)

check_res_path = '/data/user/018107/factor_zoo1/europa_precheck/' # qyh:这里修改
if not os.path.exists(check_res_path): os.makedirs(check_res_path)
basic_file_path = '/dfs/user/015585/00_股指期货策略/Basic_future_20220801_20250430.h5' # '/data/group/800463/project/project1_prod/left_v2212/Basic_zt_test/Basic_zt_001.h5'
label_file_path = '/dfs/user/015585/00_股指期货策略/sft_basic_formal_20220801_20250430.h5' # /data/group/800463/project/project1_prod/left_v2212/Label_zt_test/Label_zt_001.h5
factor_data_path = '/data/user/018107/factor_zoo1/europa_factor_ezt/' # /data/user/018107/factor_zoo1/europa_factor_ezt/，qyh: 这里要改
data_path_dic= {
    # 'TTransaction': '/data/group/800463/data/project1_prod/transaction_test_001_ezt/',
    # 'LastTouchTTick':'/data/group/800463/data/project1_prod/last_touch_t_tick/',
    # 'MarketTTick':'/data/group/800463/data/project1_prod/market_t_tick/',
    # 'Market1TTick':'/data/group/800463/data/project1_prod/market_t_tick/',
    # 'MarketIndTTick':'/data/group/800463/data/project1_prod/market_t_tick/',
    # 'TOrder':'/data/group/800463/data/project1_prod/order_test_001/',
    'TTickabAll': '/dfs/group/800463/data/projectF_prod/IM_tick/',
}
# emotion_data = {'Basic_zt': '/data/group/800463/project/project1_prod/left_v2212/Basic_zt/Basic_zt.h5',
#                 'Label_zt': '/data/group/800463/project/project1_prod/left_v2212/Label_zt/Label_zt.h5'}
#all_df = pd.read_pickle('/data/user/013600/factor_manager_v2/all_factor_bank/test_001/all_factor_20150901_20220225.pkl')
all_df=pd.read_hdf(basic_file_path)
all_df['T_o2pre']=pd.read_hdf(label_file_path)['label']
# filter_df = all_df[(all_df['ZT_Time']<=143000000)& (all_df['open_is_zt']==0)&(all_df['T_o2pre']>=-0.05)&(all_df['after_not_ul_len']>10)
#                 &(all_df['pre_close']>=2)&(all_df['high_price']<(all_df['trigger_price']))& (all_df['last_is_zt']==0)]
filter_df_2225=all_df.loc[pd.Timestamp('20220801'):pd.Timestamp('20250430')] # 原来是filter_df

param = AIMR.getParam()
#param = '/data/user/018107/factor_zoo1/all_factor_alternate_update.xlsx-2120'
print(param)
param_list = param.split('-')
file_path = param_list[0]
index_list = param_list[1].split(';')
index_list = [int(index) for index in index_list]
df_dic = pd.read_excel(file_path, sheet_name=None)
all_factor_inf = pd.concat(df_dic.values(),sort=False).reset_index()
factor_inf = all_factor_inf.reindex(index_list)

for index, inf in factor_inf.iterrows():
    print(index, 'in', list(factor_inf.index))
    factor_name, factor_type, factor_owner = inf['factor_name'], inf['factor_type'], inf['factor_owner']
    factor_date = inf['check_date'] if 'check_date' in inf else inf['factor_date']
    if factor_type not in ['T-1_factor', 'TTickabAll', 'TTransaction', 'TOrder',
                           'TTransaction_TTickab', 'TTransaction_TOrder', 'TOrder_TTickab',
                           'LastTouchTTick','MarketTTick','Market1TTick','MarketIndTTick',
                           'TEmotion', 'T-1_Emotion','other']:
        check_dic = {'代码格式检查': '未支持的因子类型%s'%factor_type, '因子值一致性检查': '', '函数运行检查': '', '因子测试': '', '预检测': 'not pass'}
        print(check_dic)
        pd.Series(check_dic).to_pickle(check_res_path + '%s.pkl' % (factor_name))
        continue


    if factor_type in ['TEmotion', 'T-1_Emotion','other']:
        check_dic = {'代码格式检查': '', '因子值一致性检查': '', '函数运行检查': '', '因子测试': '', '预检测': 'pass'}
        print(check_dic)
        pd.Series(check_dic).to_pickle(check_res_path + '%s.pkl' % (factor_name))
        continue

    print('%s,%s,%s'%( factor_name,factor_type,factor_date))
    before_submit_name_list = all_factor_inf.loc[:index]['factor_name'].to_list()[:-1]
    check_ser = pre_check(factor_name, factor_type, factor_date,check_res_path, before_submit_name_list,basic_file_path,factor_data_path,all_df,filter_df_2225) # qyh:倒数第二个变量如果有filter_df要改
    print(check_ser, '\n')
    check_ser.to_pickle(check_res_path + '%s.pkl' % (factor_name))
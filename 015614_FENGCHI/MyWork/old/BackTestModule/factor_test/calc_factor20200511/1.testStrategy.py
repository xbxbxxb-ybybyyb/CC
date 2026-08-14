# coding: utf-8
# Author：fengchi863
# Date ：2020/5/11 11:06

'''
为了检查路径依赖问题，测试top20因子的不同路径下的因子表现
选择测试这四天的因子表现
'''

import pandas as pd
import time, os, gc
from dataApi.StrategyBackTest_different_start_poin import StrategyBackTest
from multiprocessing import Pool

factor_result_analysis_output_path = '/data/group/800319/junkData/temp_factor_by_fc/StrategyBackTest/strats_append_with_defalt_factor_20200428/'
factor_result_analysis = pd.read_excel(factor_result_analysis_output_path + \
                                       '日内因子净值回测结果(20200428全量)_(0.5, 200, 400).xlsx', sheet_name='全量测试结果', index_col=0)
factor_list = factor_result_analysis.sort_values('累计超额收益率', ascending=False).iloc[:20]['因子名称'].tolist()

def main(factor_name, append_factor_name, turnover, target_holding_num, buy_pool_num, date, para_sign, daily_factor=None):

    # 初始化，约125s
    result_output_path = '/data/group/800319/junkData/temp_factor_by_fc/StrategyBackTest/strats_append_with_defalt_factor_20200511/'

    if not os.path.exists(result_output_path):
        os.mkdir(result_output_path)
    if os.path.exists(result_output_path+'%s_evaluation_%s.xlsx'%(factor_name,str(date))):
        print(result_output_path+'%s_evaluation_%s.xlsx'%(factor_name,str(date)),'已存在')
        return

    print('开始初始化...')
    strat = StrategyBackTest(start_date=date)
    try:
        daily_factor_name = 'default'
        if not daily_factor is None:
            daily_factor_name = daily_factor.split('/')[-1].replace('.h5', '')
            daily_factor = pd.read_hdf(daily_factor, daily_factor_name)
            daily_factor = daily_factor.loc[date:]

        factor = pd.read_hdf(
            '/data/group/800319/storeFactor/original_intrafactor/%s.h5' % factor_name,
            factor_name)
        print(turnover, target_holding_num, buy_pool_num, date, factor_name, 'start')

        append_factor = pd.read_pickle('/data/group/800319/appendFactor/%s.pkl' % append_factor_name)
        strat.evaluation_and_report(factor, daily_selected_pool=daily_factor,
                                    output_path=result_output_path,
                                    turnover=turnover,
                                    target_holding_num=target_holding_num,
                                    buy_pool_num=buy_pool_num,
                                    file_name='%s_evaluation_%s'%(factor_name,str(date)),
                                    append_factor=append_factor, append_ascending=True, para=para_sign)  # 回测并输出结果，约750s
    except:
        pd.DataFrame().to_excel(result_output_path + '%s_evaluation_%s_wrong.xlsx'%(factor_name,str(date)))

def wraper(para):
    factor_name, append_factor_name, turnover, target_holding_num, buy_pool_num, date, para_sign = para
    main(factor_name, append_factor_name, turnover, target_holding_num, buy_pool_num, date, para_sign)
    gc.collect()

if __name__=="__main__":
    para_list = []
    factor_name_list = []
    num_list = [(200,400)]

    factor_name_list = factor_list # 先运行一个因子的 10
    ## 倒序跑
    # factor_name_list = factor_name_list[::-1][:100]

    test_date_list = [20170103, 20170314, 20170315, 20170502]

    for factor_name in factor_name_list:
        for turnover in [0.5]:
            for num in num_list:
                for date in test_date_list:
                    target_holding_num, buy_pool_num = num
                    para_list.append((factor_name, 'AppendFactor2_3', turnover, target_holding_num, buy_pool_num, date, (0, 1)))
    pool = Pool(3)
    r = pool.map(wraper, para_list)
    pool.close()
    pool.join()
    # wraper(para_list[0])

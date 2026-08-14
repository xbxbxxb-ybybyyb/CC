# coding: utf-8
# Author：fengchi863
# Date ：2020/5/8 15:24

import pandas as pd
import time, os
from dataApi.StrategyBackTest import StrategyBackTest
from multiprocessing import Pool

factor_root_path = '/data/group/800319/storeFactor/original_intrafactor/'

print('初始化...准备回测...')
e = time.time()
strat = StrategyBackTest()
print('初始化时间' + str(time.time()-e))

def main(factor_name, turnover, target_holding_num, buy_pool_num):

    # 初始化，约125s
    result_output_path = '/data/group/800319/junkData/temp_factor_by_fc/StrategyBackTest/boll_factor_20200508/'

    if not os.path.exists(result_output_path):
        os.mkdir(result_output_path)
    if os.path.exists(result_output_path+'%s_evaluation_%s.xlsx'%(factor_name,str((turnover, target_holding_num, buy_pool_num)))):
        print(result_output_path+'%s_evaluation_%s.xlsx'%(factor_name.replace(' ',''),str((turnover, target_holding_num, buy_pool_num))),'已存在')
        return
    # else:
    #     print(factor_name.replace(' ',''),str((turnover, target_holding_num, buy_pool_num)))
    try:
        factor = pd.read_hdf(
            '/data/group/800319/storeFactor/original_intrafactor/%s.h5' % factor_name,
            factor_name)
        print(turnover, target_holding_num, buy_pool_num, factor_name, 'start')
        strat.evaluation_and_report(factor,
            output_path=result_output_path,
            turnover = turnover,
            target_holding_num=target_holding_num,
            buy_pool_num=buy_pool_num,
            file_name='%s_evaluation_%s'%(factor_name.replace(' ',''),str((turnover, target_holding_num, buy_pool_num)))) #回测并输出结果，约750s
        # strat.output_trading_record(output_path='/data/group/800319/junkData/temp_factor_by_fc/strats_191/',
        #                             file_name='%s_trading_record_%s'%(factor_name.replace(' ',''), str((turnover, target_holding_num, buy_pool_num))))
    except:
        pd.DataFrame().to_excel(result_output_path + '%s_evaluation_%s_wrong.xlsx'%(factor_name.replace(' ',''),str((turnover, target_holding_num, buy_pool_num))))

def wraper(para):
    factor_name, turnover, target_holding_num, buy_pool_num = para
    main(factor_name, turnover, target_holding_num, buy_pool_num)

if __name__ == "__main__":
    para_list = []
    append_factor_df = pd.read_excel('日内因子补充20200508.xlsx', sheet_name='因子补充', index_col=0)
    factor_names = append_factor_df['因子名称'].tolist()

    num_list = [(200, 400)]
    factor_name_list = factor_names  # 先运行一个因子的 10
    for factor_name in factor_name_list:
        if factor_name in ['boll4_20', 'boll10_20', 'boll6_20']:
            factor_name = factor_name.split('_')[0]
        for turnover in [0.5]:
            for num in num_list:
                target_holding_num, buy_pool_num = num
                para_list.append((factor_name, turnover, target_holding_num, buy_pool_num))
    pool = Pool(9)
    r = pool.map(wraper, para_list)
    pool.close()
    pool.join()

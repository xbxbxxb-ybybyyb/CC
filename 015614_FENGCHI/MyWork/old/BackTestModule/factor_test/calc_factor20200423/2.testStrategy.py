# coding: utf-8
# Author：fengchi863
# Date ：2020/4/23 17:51
'''
策略回测第二个版本上147个因子的全量测试
为什么是147个呢？因为factor106这个因子两个同名了，而且本身相关性很高，所以剔除了一个
本次只测试换手率的三个不同的参数（0.1,0.3,0.5）,200,400
由于是4月23日开始编写，所以文件夹后缀命名为20200423
需要提前将日内因子测试文件表格保存到/data/group/800319/junkData/temp_factor_by_fc/StrategyBackTest/
'''

import pandas as pd
import time
from dataApi.StrategyBackTest import StrategyBackTest
from multiprocessing import Pool

print('初始化...准备回测...')
e = time.time()
strat = StrategyBackTest()
print('初始化时间' + str(time.time()-e))

def main(factor_name, turnover, target_holding_num, buy_pool_num):

    # 初始化，约125s
    result_output_path = '/data/group/800319/junkData/temp_factor_by_fc/StrategyBackTest/strats_append_with_defalt_factor_20200428/'

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

if __name__=="__main__":
    para_list = []
    factor_name_list = []
    import os
    file_dir = r'/data/group/800319/storeFactor/original_intrafactor'
    factor_name_list = sorted([os.path.splitext(x)[0] for x in os.listdir(file_dir)])
    # num_list = [(200,400), (300,600), (500,800)]
    num_list = [(200,400)]

    factor_name_list = factor_name_list # 先运行一个因子的 10
    ## 倒序跑
    # factor_name_list = factor_name_list[::-1][:100]
    for factor_name in factor_name_list:
        for turnover in [0.1, 0.3, 0.5]:
            for num in num_list:
                target_holding_num, buy_pool_num = num
                para_list.append((factor_name, turnover, target_holding_num, buy_pool_num))
    pool = Pool(9)
    r = pool.map(wraper, para_list)
    pool.close()
    pool.join()

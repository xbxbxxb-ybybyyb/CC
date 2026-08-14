# coding: utf-8
# Author：fengchi863
# Date ：2020/4/16 9:17

# import sys
# sys.path.append('/data/group/800319')
import  os
import time
import pandas as pd
from dataApi.StrategyBackTest import StrategyBackTest
from multiprocessing import Pool

def main(factor_name, holding_time, turnover, target_holding_num, buy_pool_num, trade_num):

    # 初始化，约125s
    # base_path = '/data/group/800319/junkData/temp_factor_by_fc/StrategyBackTest/strats_append_with_defalt_factor_20200415/'
    # base_path = '/data/group/800319/junkData/temp_factor_by_fc/StrategyBackTest/strats_append_with_defalt_factor_20200420/'
    base_path = '/data/group/800319/junkData/temp_factor_by_fc/StrategyBackTest/strats_append_with_defalt_factor_20200421/'

    if not os.path.exists(base_path):
        os.mkdir(base_path)
    if os.path.exists(base_path+'%s_evaluation_%s.xlsx'%(factor_name.replace(' ',''),str((turnover, target_holding_num, buy_pool_num)))):
        # print(base_path+'%s_evaluation_%s.xlsx'%(factor_name.replace(' ',''),str((turnover, target_holding_num, buy_pool_num))),'已存在')
        return
    else:
        print(factor_name.replace(' ',''),str((turnover, target_holding_num, buy_pool_num)))
        # check_wrong_list.append(factor_name.replace(' ','')+str((turnover, target_holding_num, buy_pool_num)))
        # return #测试
    try:
        strat = StrategyBackTest(holding_minutes=holding_time)
        # factor = pd.read_hdf(
        #     '/data/group/800319/storeFactor/%s.h5' % factor_name,
        #     factor_name)
        factor = pd.read_hdf(
            '/data/group/800319/storeFactor/combine_ffactor20200421/%s.h5' % factor_name,
            factor_name)
        print(holding_time, trade_num, turnover, target_holding_num, buy_pool_num, factor_name, 'start')
        strat.evaluation_and_report(factor,
            output_path=base_path,
            turnover = turnover,
            target_holding_num=target_holding_num,
            buy_pool_num=buy_pool_num,
            bar_order_stk_num=trade_num,
            append_order_num=trade_num,
            file_name='%s_evaluation_%s'%(factor_name.replace(' ',''),str((turnover, target_holding_num, buy_pool_num)))) #回测并输出结果，约750s
        # strat.output_trading_record(output_path='/data/group/800319/junkData/temp_factor_by_fc/strats_191/',
        #                             file_name='%s_trading_record_%s'%(factor_name.replace(' ',''), str((turnover, target_holding_num, buy_pool_num))))
    except:
        pd.DataFrame().to_excel(base_path + '%s_evaluation_%s_wrong.xlsx'%(factor_name.replace(' ',''),str((turnover, target_holding_num, buy_pool_num))))

def wraper(para):
    factor_name, holding_minutes, turnover, target_holding_num, buy_pool_num, trade_num = para
    main(factor_name, holding_minutes, turnover, target_holding_num, buy_pool_num, trade_num)

if __name__=="__main__":
    para_list = []
    factor_name_list = []
    import os
    file_dir = r'/data/group/800319/storeFactor/combine_ffactor20200421'
    factor_name_list = sorted([os.path.splitext(x)[0] for x in os.listdir(file_dir)])
    # factor_name_list.remove('corrcoef')
    # num_list = [(200,400), (300,600), (500,800)]
    num_list = [(200,400)]

    factor_name_list = factor_name_list # 先运行一个因子的 10
    ## 倒序跑
    # factor_name_list = factor_name_list[::-1][:100]
    for holding_minutes in [1]:
        for trade_num in [1]:
            for factor_name in factor_name_list:
                # for turnover in [0.1, 0.3, 0.5]:
                for turnover in [0.1]:
                    for num in num_list:
                        target_holding_num, buy_pool_num = num
                        para_list.append((factor_name, holding_minutes, turnover, target_holding_num, buy_pool_num, trade_num))
    pool = Pool(9)
    r = pool.map(wraper, para_list)
    pool.close()
    pool.join()

    # print(check_wrong_list)
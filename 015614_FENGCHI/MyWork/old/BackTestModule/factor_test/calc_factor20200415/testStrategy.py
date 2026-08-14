# import sys
# sys.path.append('/data/group/800319')
import  os
import pandas as pd
from dataApi.StrategyBackTest import StrategyBackTest
import time
from multiprocessing import Pool

def main(factor_name,holding_time,turning_over):

    # 初始化，约125s
    base_path = '/data/group/800319/junkData/temp_factor_by_fc/StrategyBackTest/strats_append_with_defalt_factor_20200415/'
    if not os.path.exists(base_path):
        os.mkdir(base_path)
    strat = StrategyBackTest(holding_minutes=holding_time)
    # factor_name = 'factor_dev03'#['factor_dev01','factor_dev02','factor_dev03','factor_dev04','factor_dev07','factor_dev08']:
    for trade_num in [1]:#[1,2,3,4,5]:
        # for turning_over in [0.6,0.8,1]:
        if os.path.exists(base_path+'%s_evaluation_%s'%(factor_name,str((holding_time,trade_num,turning_over)))):
            pass#continue
        # try:
        e = time.time()
        factor = pd.read_hdf(
            '/data/group/800319/storeFactor/%s.h5' % factor_name,
            factor_name)
        print(holding_time, trade_num, turning_over, factor_name, 'start')
        strat.evaluation_and_report(factor,
            output_path=base_path,
            file_name='%s_evaluation_%s'%(factor_name,str((holding_time,trade_num,turning_over))),
                                        turnover=turning_over, bar_order_stk_num=trade_num,append_order_num=trade_num) #回测并输出结果， 约750s
        strat.output_trading_record(output_path='/data/group/800319/junkData/temp_factor_by_fc/strats_191/',
                                    file_name='%s_trading_record_%s'%(factor_name,str((holding_time,trade_num,turning_over))))
        print(holding_time,trade_num,turning_over,time.time()-e)
            # except:
            #     print(str((holding_time,trade_num,turning_over)),'wrong----------------------------------------')
#
def wraper(para):
    factor_name, holding_time,turning_over = para
    main(factor_name, holding_time, turning_over)

if __name__=="__main__":
    # main(1,0.6)
    para_list = []
    factor_name_list = ['factor_dev01','factor_dev02','factor_dev03','factor_dev04','factor_dev07','factor_dev08']
    for holding_minutes in [1]:
        for factor_name in factor_name_list:
            for turnover in [0.6]: # [0.3,0.5,0.6,0.8,1]
                para_list.append((factor_name,holding_minutes,turnover))
    pool = Pool(6)
    r = pool.map(wraper,para_list)
    pool.close()
    pool.join()

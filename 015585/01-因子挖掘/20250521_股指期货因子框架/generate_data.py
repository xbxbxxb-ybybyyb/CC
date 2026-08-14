# -*- coding: utf-8 -*-
from xquant.factordata import FactorData
s = FactorData()
from xquant.thirdpartydata.multifactor.IO import *
from xquant.marketdata import MarketData
mdp = MarketData()
'''
股指期货数据准备，根据basic_file，按精确到时分秒的时间戳准备数据
落地文件按交易日建立文件夹，内部再按30S间隔存储文件(后来改为8个时点）
数据来源：存储好了的所有IM数据，在 path = /dfs/group/800463/data/futures_data/IM/tick/
'''
def check_dir(path):  # 路径生成函数
    if not os.path.exists(path):
        os.makedirs(path)

def store_hf_data_for_one_day(date, Basic_next_hf_finish, result_path_tick, data_ori_path = '/dfs/group/800463/data/futures_data/IM/tick/'):
    tradingday = str(date)
    print(tradingday, 'future data storing.......')
    basic_data_in_the_day = Basic_next_hf_finish[Basic_next_hf_finish['date'] == date] # 先把当日所有时分秒的basic取出来，降低IO开销
    future = basic_data_in_the_day.index[0][1] # 当日对应的期货合约
    tick_all_day = pd.read_pickle(f'{data_ori_path}{future.replace(".CF","")}/{tradingday}.pkl')
    for index, row in basic_data_in_the_day.reset_index().iterrows(): # 不同时分秒
        # print(index)
        try:
            time = row['time'] # int格式
            tick_df_time = tick_all_day[(tick_all_day['MDTime'] < time)]
            tick_df_time['cuttime'] = time # 补充截断时间
            tick_df_time['dt'] = pd.Timestamp(tradingday)
            tick_df_time['Ticker'] = future
            tick_df_time = tick_df_time.set_index(['dt','Ticker'])
            check_dir(f'{result_path_tick}{tradingday}/')
            tick_df_time.to_pickle(f'{result_path_tick}{tradingday}/{time}.pkl')
        except Exception as e:
            print(future, tradingday, e)
            pass
    return

if __name__ == '__main__':
    from multiprocessing import Pool
    from xquant.factordata import FactorData
    s = FactorData()
    data_ori_path = '/dfs/group/800463/data/futures_data/IM/tick/'
    result_path_tick='/dfs/group/800463/data/projectF_prod/IM_tick/'

    pool = Pool(24)
    task_list = []
    all_Basic_next_hf_finish = pd.read_hdf(f'/dfs/user/015585/00_股指期货策略/Basic_future_20220801_20250430.h5').sort_index()
    print(all_Basic_next_hf_finish.shape)
    for tradingday in s.tradingday(20220801, 20250430):
        Basic_next_hf_finish = all_Basic_next_hf_finish[all_Basic_next_hf_finish['date'] == tradingday]
        task_list.append(pool.apply_async(store_hf_data_for_one_day,args=(tradingday,
                                                         Basic_next_hf_finish,
                                                         result_path_tick,
                                                         data_ori_path)))
    pool.close()
    pool.join()
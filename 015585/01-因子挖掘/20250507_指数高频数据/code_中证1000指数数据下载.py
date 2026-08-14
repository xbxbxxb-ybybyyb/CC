# -*- coding: utf-8 -*-
from xquant.factordata import FactorData
s = FactorData()
from xquant.thirdpartydata.multifactor.IO import *
from xquant.marketdata import MarketData
import IO
mdp = MarketData()

def hf_preprocessing(data_type, md_df):
    if data_type == 'Index':
        use_col = ['MDDate', 'MDTime', 'PreClosePx', 'LastPx', 'OpenPx', 'ClosePx', 'HighPx', 'LowPx',
                   'TotalVolumeTrade', 'TotalValueTrade', 'HTSCSecurityID']
        md_df = md_df[use_col]
        md_df['MDTime'] = md_df['MDTime'].astype(int)
        return md_df

def check_dir(path):  # 路径生成函数
    if not os.path.exists(path):
        os.makedirs(path)

def store_hf_data_for_one_day(date, Basic_next_hf_finish, cut_MDTime, result_path_tick):
    tradingday = str(date)
    print(tradingday, cut_MDTime, 'data storing.......')
    basic_data_in_the_day = Basic_next_hf_finish.loc[pd.Timestamp(tradingday)]
    tick_data_of_the_day_list = []
    for index, row in basic_data_in_the_day.reset_index().iterrows():
        stock = row['Ticker']
        pre_close = row['S_DQ_PRECLOSE']
        try:
            tick_md_df = mdp.get_data_by_date('Index', stock, tradingday)
            tick_md_df['MDTime'] = tick_md_df['MDTime'].astype(int)
            tick_md_df = hf_preprocessing('Index', tick_md_df)
            available_tick_data = tick_md_df[tick_md_df['MDTime'] <= cut_MDTime] # !!!! 这里注意check有没有等号
            available_tick_data = available_tick_data[(available_tick_data['MDTime'] >= 91500000) & (available_tick_data['MDTime'] >= 91500000)]
            available_tick_data = available_tick_data[~((available_tick_data['MDTime'] > 113000000) & (available_tick_data['MDTime'] < 130000000))]
            # available_tick_data['pre_close'] = pre_close
            tick_data_of_the_day_list.append(available_tick_data)

        except Exception as e:
            print(stock, tradingday, e)
            pass
    tick_data_of_the_day = pd.concat(tick_data_of_the_day_list)

    tick_data_of_the_day['dt'] = tick_data_of_the_day['MDDate'].apply(lambda x: pd.Timestamp(x))
    tick_data_of_the_day['Ticker'] = tick_data_of_the_day['HTSCSecurityID']
    tick_data_of_the_day = tick_data_of_the_day.set_index(['dt', 'Ticker']).drop(columns=['MDDate','HTSCSecurityID'])
    tick_data_of_the_day.to_pickle(result_path_tick + str(tradingday) + '.pkl')
    return
if __name__ == '__main__':
    from multiprocessing import Pool
    # from multiprocessing.pool import ThreadPool as Pool
    from xquant.factordata import FactorData
    s = FactorData()

    result_path_tick='/dfs/group/800463/public/index_data/ZZ1000/'
    if not os.path.exists(result_path_tick):
        os.makedirs(result_path_tick)

    pool = Pool(24)
    task_list = []
    all_Basic_next_hf_finish = IO.read_data([20250514, 20250818],universe=['000852.SH'],
                                            alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AIndexEODPrices/AIndexEODPrices.h5')
    print(all_Basic_next_hf_finish.shape)
    for tradingday in s.tradingday('20250514', '20250818'):
        Basic_next_hf_finish = all_Basic_next_hf_finish.loc[pd.Timestamp(tradingday):pd.Timestamp(tradingday)]
        task_list.append(pool.apply_async(store_hf_data_for_one_day,args=(tradingday,
                                                         Basic_next_hf_finish,
                                                         150000000,
                                                         result_path_tick,)))
    pool.close()
    pool.join()
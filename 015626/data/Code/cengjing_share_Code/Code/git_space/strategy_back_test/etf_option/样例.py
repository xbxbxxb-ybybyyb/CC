# ETF
# sig = pd.read_hdf('/data/user/020529/share/signal/mobius_shift/IM_CRN_Predict00_Norm1.h5')
sig = pd.read_hdf('/data/user/020529/share/signal/mobius_trend/IM_ProdV1UF_WR12_30_Norm2.h5')

back_test_sdate, back_test_edate =  20230101, 20240101

ticker = '512100.SH'

# pos_dict2 = {(0, 0.1): (0, 0),
#              (0.1, 0.2): (0, 0.5),
#              (0.2, 0.8): (0, 1),
#              (0.8, 0.9): (0.5, 1),
#              (0.9, 100): (1, 1.0)}

pos_dict2 = {(0, 0): (0, 0),
             (0, 0.8): (0, 1/10),
             (0.8, 100): (1/10, 1/10)}

initial_cash1 = 1e7

signal_list = [{'signal':sig,'pos_dict':pos_dict2,'cash':initial_cash1}]

factor_name = ticker + '_etf'
name = f'{factor_name}_{initial_cash1//1e7}e7_prod'
a1 = v_order(signal_list, ticker=ticker, ticker_kind='etf', start_date=back_test_sdate, end_date=back_test_edate, tickslippage = 1000,
                 save_signal_list = True, 
                 save_path=f'/data/user/015626/data/share/LOCAL_DATA/Mobius/backtest_multipath_merge/{ticker}/{back_test_sdate}_{back_test_edate}/{name}',
                 name_prefix=name, max_wait_tick_num = 1, max_deal_volume_in_minute = 10000000, volume_per_order = 100000,
                 c_rate = 0, fee_fixed = 0, face_value = 1, min_deal_vol_in_bar = None,n_jobs = 24,
                 tick_root_path = '/arch1/group/800466/warehouse/prod/MD/CHINA_FUND/ETF/Tick/', 
                 data_root_path = '/data/user/015626/data/share/MD/CHINA_FUND/MINUTE/MD_CHINA_ETF_MINUTE.h5')
result0345 = a1.back_test() 


# 期权
sig00 = pd.read_hdf('/data/user/020529/share/signal/mobius_shift/IM_CRN_Predict00_Norm1.h5')
sig00[sig00 > 0] = 0
sig00 *= -1

back_test_sdate, back_test_edate =  20230101, 20240101

ticker = 'MO.CFE'

pos_dict2 = {(0, 0.1): (0, 0),
             (0.1, 0.2): (0, 0.05),
             (0.2, 0.8): (0, 1.0/10),
             (0.8, 0.9): (0.05, 1.0/10),
             (0.9, 100): (0.1, 1.0/10)}


initial_cash1 = 1e8

signal_list = [{'signal':sig00,'pos_dict':pos_dict2,'cash':initial_cash1}]

factor_name = ticker + '_short_buyput_1e8_min10'
name = f'{factor_name}_prod'
a1 = v_order(signal_list, ticker=ticker, ticker_kind = 'option', start_date=back_test_sdate, end_date=back_test_edate, tickslippage = 1000,
                 save_signal_list = True, 
                 save_path=f'/data/user/015626/data/share/LOCAL_DATA/Mobius/backtest_multipath_merge/{ticker}/{back_test_sdate}_{back_test_edate}/{name}',
                 name_prefix=name, max_wait_tick_num = 2, max_deal_volume_in_minute = 500, volume_per_order = 3,
                 c_rate = 0, fee_fixed = 15, face_value = None, min_deal_vol_in_bar = 10,n_jobs = 24,
                 tick_root_path = '/data/user/016700/Data/Options_Related/MD/CHINA_OPTIONS/TICK/STOCK_INDEX_OPTIONS/', 
                 data_root_path = '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/ATTEMPTS/put_basics.h5')
result0345 = a1.back_test() 
indicators = ['amplitude', 'volume','AbsDistance', 'BidAskVol_close']

future_data = pd.read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE/FUTURE_DATA_2020.pkl')

for suffix in ['','_if']:
    high = future_data[f'high{suffix}'].between_time('930', '1456').rolling(3, min_periods = 1).max()
    low = future_data[f'low{suffix}'].between_time('930', '1456').rolling(3, min_periods = 1).min()
    amplitude = (high / low).replace([np.inf, -np.inf], np.nan) - 1 
    temp_mask = future_data['recent_month_mask'].between_time('930', '1456')
    fac = amplitude[temp_mask].mean(axis = 1)
    fac.to_pickle(f'/data/user/015626/data/share/LOCAL_DATA/Mobius/filters/amplitude{suffix}.pkl')
    
    temp_raw = future_data[f'volume{suffix}'].between_time('930', '1456')
    temp_mask = future_data['recent_month_mask'].between_time('930', '1456')
    fac = temp_raw.rolling(3, min_periods = 1).mean()[temp_mask].mean(axis = 1)
    fac.to_pickle(f'/data/user/015626/data/share/LOCAL_DATA/Mobius/filters/volume{suffix}.pkl')
    
    temp_raw = future_data[f'AbsDistance{suffix}'].between_time('930', '1456')
    temp_mask = future_data['recent_month_mask'].between_time('930', '1456')
    fac = temp_raw.rolling(3, min_periods = 1).mean()[temp_mask].mean(axis = 1)
    fac.to_pickle(f'/data/user/015626/data/share/LOCAL_DATA/Mobius/filters/AbsDistance{suffix}.pkl')
    
    BidAskVol = future_data[f'BidAskVol{suffix}'].between_time('930', '1456')
    close = future_data[f'close{suffix}'].between_time('930', '1456')
    BidAskVol_close = (BidAskVol / close).replace([np.inf, -np.inf], np.nan)
    temp_mask = future_data['recent_month_mask'].between_time('930', '1456')
    fac = BidAskVol_close[temp_mask].mean(axis = 1)
    fac.to_pickle(f'/data/user/015626/data/share/LOCAL_DATA/Mobius/filters/BidAskVol_close{suffix}.pkl')

indicators_t_ic = {'amplitude':0.002, 'volume':300, 'AbsDistance':0.006, 'BidAskVol_close':0.00008}
indicators_t_if = {'amplitude':0.002, 'volume':400, 'AbsDistance':0.006, 'BidAskVol_close':0.000075}

back_test_sdate, back_test_edate = 20220701, 20230630

f_list = []
for ind, t in indicators_t_ic.items():
    filter_df = pd.read_pickle(f'/data/user/015626/data/share/LOCAL_DATA/Mobius/filters/{ind}.pkl').loc[pd.to_datetime('20210101'):]
    filter_df = abs(filter_df)
    filter_df = filter_df >= t
    filter_df = filter_df.astype('int')
    f_list.append(filter_df)
filter_df_num = pd.concat(f_list, axis = 1).sum(axis = 1)
filter_df = (filter_df_num >= 2).astype('int')
filter_df.to_pickle('/data/user/015626/data/share/LOCAL_DATA/Mobius/filters/final/IC_filters.pkl')

# ticker = 'IC.CFE'
# factor = pd.read_pickle('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/20230224_ic_ic_v7c/model_value/model_norm/20230711/pred_comb2.pkl')
# factor = factor * 2 - 1

# signal1 = factor

# pos_dict1 = {(0, 0.2): (0, 0),
#              (0.2, 0.3): (0, 0.5/10),
#              (0.3, 0.8): (0, 1.0/10),
#              (0.8, 0.9): (0.5/10, 1.0/10),
#              (0.9, 1.1): (1.0/10, 1.0/10)}

# initial_cash1 = 2e8

# signal_list = [{'signal':signal1,'pos_dict':pos_dict1,'cash':initial_cash1}]

# name = '20230224_ic_ic_v7c_orgin'
# a = TS_BACK_TEST(signal_list, ticker=ticker, start_date=back_test_sdate, end_date=back_test_edate,tickslippage = 1.2, save_signal_list = False, save_path=f'/data/user/015626/data/share/LOCAL_DATA/Mobius/filters/backtest/{ticker}/{name}',
#                  name_prefix=name)
# result = a.back_test() # 测试全部

# name = '20230224_ic_ic_v7c_filter'
# a = TS_BACK_TEST(signal_list, ticker=ticker, start_date=back_test_sdate, end_date=back_test_edate,tickslippage = 1.2, save_signal_list = False, save_path=f'/data/user/015626/data/share/LOCAL_DATA/Mobius/filters/backtest/{ticker}/{name}',
#                  name_prefix=name, filter_series = filter_df, filter_open = True, filter_close = False)
# result = a.back_test() # 测试全部

ticker = 'IC.CFE'
factor = pd.read_pickle('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/20230526_ic_ic_v7unifac/model_value/model_norm/20230630/pred_comb2.pkl')
factor = factor * 2 - 1

signal1 = factor

pos_dict1 = {(0, 0.2): (0, 0),
             (0.2, 0.3): (0, 0.5/10),
             (0.3, 0.8): (0, 1.0/10),
             (0.8, 0.9): (0.5/10, 1.0/10),
             (0.9, 1.1): (1.0/10, 1.0/10)}

initial_cash1 = 2e8

signal_list = [{'signal':signal1,'pos_dict':pos_dict1,'cash':initial_cash1}]

a = TS_BACK_TEST(signal_list, ticker=ticker, start_date=back_test_sdate, end_date=back_test_edate,tickslippage = 1.2, save_signal_list = False, save_path=f'/data/user/015626/data/share/LOCAL_DATA/Mobius/filters/backtest2/{ticker}/origin',
                 name_prefix='origin')
result = a.back_test() # 测试全部

name = '20230526_ic_ic_v7unifac_filter'
a = TS_BACK_TEST(signal_list, ticker=ticker, start_date=back_test_sdate, end_date=back_test_edate,tickslippage = 1.2, save_signal_list = False, save_path=f'/data/user/015626/data/share/LOCAL_DATA/Mobius/filters/backtest2/{ticker}/{name}',
                 name_prefix=name, filter_series = filter_df, filter_open = True, filter_close = False)
result = a.back_test() # 测试全部

f_list = []
for ind, t in indicators_t_if.items():
    ind = ind + '_if'
    filter_df = pd.read_pickle(f'/data/user/015626/data/share/LOCAL_DATA/Mobius/filters/{ind}.pkl').loc[pd.to_datetime('20210101'):]
    filter_df = abs(filter_df)
    filter_df = filter_df >= t
    filter_df = filter_df.astype('int')
    f_list.append(filter_df)
filter_df_num = pd.concat(f_list, axis = 1).sum(axis = 1)
filter_df = (filter_df_num >= 2).astype('int')
filter_df.to_pickle('/data/user/015626/data/share/LOCAL_DATA/Mobius/filters/final/IF_filters.pkl')

ticker = 'IF.CFE'
factor = pd.read_pickle('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/20221230_if_if_v6nl/model_value/model_norm/20230711/pred_comb2.pkl')
factor = factor * 2 - 1

signal1 = factor

pos_dict1 = {(0, 0.2): (0, 0),
             (0.2, 0.3): (0, 0.5/10),
             (0.3, 0.8): (0, 1.0/10),
             (0.8, 0.9): (0.5/10, 1.0/10),
             (0.9, 1.1): (1.0/10, 1.0/10)}

initial_cash1 = 2e8

signal_list = [{'signal':signal1,'pos_dict':pos_dict1,'cash':initial_cash1}]

a = TS_BACK_TEST(signal_list, ticker=ticker, start_date=back_test_sdate, end_date=back_test_edate, tickslippage = 0.8, save_signal_list = False, save_path=f'/data/user/015626/data/share/LOCAL_DATA/Mobius/filters/backtest2/{ticker}/origin',
                 name_prefix='origin')
result = a.back_test() # 测试全部

name = '20221230_if_if_v6nl_filter'
a = TS_BACK_TEST(signal_list, ticker=ticker, start_date=back_test_sdate, end_date=back_test_edate, tickslippage = 0.8, save_signal_list = False, save_path=f'/data/user/015626/data/share/LOCAL_DATA/Mobius/filters/backtest2/{ticker}/{name}',
                 name_prefix=name, filter_series = filter_df, filter_open = True, filter_close = False)
result = a.back_test() # 测试全部
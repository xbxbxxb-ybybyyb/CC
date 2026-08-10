import sys
sys.path.insert(4,'/dfs/user/012398/working_code/prod_zhangf/')
from multifactor.IO import IO
import multifactor.utility.dt as dt
import pandas as pd
import numpy as np
from para import para_dict

data = IO.read_data([20160101,20250501],alt = '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/MD/DAILY/MD_MAIN_CHINA_COMMODITY_DAILY.h5')

blacklist = ['ZC.CZC','IMS.SHF','SCTAS.INE','TC.CZC','EFS.CFE','AFS.CFE','LR.CZC','JR.CZC','PM.CZC','RI.CZC',
                        'BB.DCE','RS.CZC','WR.SHF','WH.CZC','FB.DCE','CY.CZC','RR.DCE','PR.CZC','PS.GFE','LG.DCE']
tickerlist_all = np.unique(data.index.get_level_values(level=1))
tickerlist = [i for i in tickerlist_all if i not in blacklist]
        
daily_df = pd.read_hdf('/dfs/user/012398/data/strategy/comm_cta/daily/res/daily_df_newmd_20_3.h5')
univ_data = pd.read_hdf('/dfs/group/800466/warehouse/test/CHINA_COMMODITIES/UNIV/test.h5')
univ_data = univ_data[univ_data['amt_1e10']]
rt = data['close']/data['pre_close']-1
std_list = []
for ticker in tickerlist:
    rt_ticker = rt.xs(ticker, level = 1)
    rt_std = rt_ticker.rolling(20,min_periods=10).std()
    std_list.append(rt_std)
std_df = pd.concat(std_list,axis=1)
std_df.columns = tickerlist
std_df = std_df.stack()

tradingdays = dt.get_trading_date_range(20230101,20250101)
tickerlist = tickerlist.copy()

for t in range(1,len(tradingdays)):
    pre_date = tradingdays[t-1]
    test_date = tradingdays[t]
    para = pd.read_csv('/dfs/user/012398/data/strategy/comm_cta/daily/res/daily_para/para_%s.csv' % (pre_date.strftime('%Y%m%d')),index_col = 0)
    data_date = data.loc[test_date]
    pos_list = []
    for ticker in para.index:
        ticker_para = para.loc[ticker]
        ticker_close = data_date.loc[ticker]['close']
        ticker_std = std_df.loc[test_date]
        std_in_thd = para_dict['std_in_dict'][ticker]
        std_out_thd = para_dict['std_out_dict'][ticker]
        if ticker_para['pos'] == 0:
            if (ticker not in univ_data.loc[test_date].index) | (ticker not in ticker_std.index):
                tmp_pos = 0                
            elif (ticker_std.loc[ticker] < std_in_thd) & (ticker_close > ticker_para['longin_down']) & (ticker_close < ticker_para['longin_up']):
                tmp_pos = 1
            elif (ticker_std.loc[ticker] < std_in_thd) & (ticker_close > ticker_para['shortin_down']) & (ticker_close < ticker_para['shortin_up']):
                tmp_pos = -1
            else:
                tmp_pos = 0
        elif ticker_para['pos'] == 1:
            if ((ticker in ticker_std.index) & (ticker_std.loc[ticker] > std_out_thd)) | \
               (ticker_close > ticker_para['longout_up']) | (ticker_close < ticker_para['longout_down']):
                tmp_pos = 0
            else:
                tmp_pos = 1
        elif ticker_para['pos'] == -1:
            if ((ticker in ticker_std.index) & (ticker_std.loc[ticker] > std_out_thd)) | \
               (ticker_close > ticker_para['shortout_up']) | (ticker_close < ticker_para['shortout_down']):
                tmp_pos = 0
            else:
                tmp_pos = -1
        else:
            raise('Something wrong with pos ! %s' % ticker)
        pos_list.append(tmp_pos)
    pos_target = pd.Series(pos_list,index = para.index)
    pos_real = daily_df.loc[test_date]['pos']
    if len(set(pos_target.index) - set(pos_real.index)) > 0: # wrong length with ticker
        print('Wrong length with ticker! %s' % test_date.strftime('%Y%m%d'))
        raise Exception
    elif len(set(pos_real.index) - set(pos_target.index)) > 0:
        difflist = list(set(pos_real.index) - set(pos_target.index))
        if pos_real[difflist].abs().sum() > 0:
            print('Wrong ticker position! %s' % test_date.strftime('%Y%m%d'))
            raise Exception
    else:
        if (pos_target - pos_real).abs().sum() > 0:
            print('Wrong position! %s' % test_date.strftime('%Y%m%d'))
            raise Exception
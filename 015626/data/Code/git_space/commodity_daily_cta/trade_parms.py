import sys
sys.path.insert(4,'/dfs/user/012398/working_code/prod_zhangf/')
from multifactor.IO import IO
import multifactor.utility.dt as dt
import pandas as pd
import numpy as np
from para import para_dict

import re
def find_str(s):
    s_str = ''.join(re.findall(r'[A-Za-z]',s))
    return s_str.upper()
     
exchange_dict = {'上期所':'SHF','郑商所':'ZCE','广期所':'GFE','能源交易所':'INE','大商所':'DCE'}

def find_x_range(numbers, threshold):
    sum19 = sum(numbers)
    sum_sq19 = sum(x**2 for x in numbers)
    a = 19
    b = -2*sum19
    c = 20 * sum_sq19 - sum19 ** 2 - 400 * (threshold ** 2)
    delta = b**2 - 4*a*c
    if delta <= 0:
        return None # no solvers
    else:
        sq_delta = np.sqrt(delta)
        x1 = (-b - sq_delta) / (2 * a)
        x2 = (-b + sq_delta) / (2 * a)
        return (x1,x2)


class Parms():
    def __init__(self, start_date = 20160101, end_date = 20250501):
        # data_main        
        data_main = IO.read_data([start_date, end_date],alt = 
                '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/MD/DAILY/MD_MAIN_CHINA_COMMODITY_DAILY.h5')
        tcs = data_main.index.get_level_values(level=1)
        idx = [type(i) == str for i in tcs]
        data_main= data_main[idx]
        # data_all contracts
        pre_date = dt.get_trading_day_offset(start_date,-1)[0]
        data_all = IO.read_data([pre_date, end_date],alt = 
                    '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/MD/DAILY/MD_CHINA_FUTURE_DAILY.h5')
      
        
        tickerlist = pd.read_csv('/data/group/800466/warehouse/prod/tradingstats/Spiral/trend_strategy/data/tickerlist.csv',index_col=0)['0'].tolist()  
        univ_data = pd.read_hdf('/data/group/800466/warehouse/prod/tradingstats/Spiral/trend_strategy/data/univ_data.h5')
        multip = pd.read_csv('/data/group/800466/warehouse/prod/tradingstats/Spiral/trend_strategy/data/mult.csv',index_col=0)
        sharesadj = pd.read_hdf('/data/group/800466/warehouse/prod/tradingstats/Spiral/trend_strategy/data/sharesadj.h5')
        std_df = pd.read_hdf('/data/group/800466/warehouse/prod/tradingstats/Spiral/trend_strategy/data/std_df.h5')
        basis_df = pd.read_hdf('/data/group/800466/warehouse/prod/tradingstats/Spiral/trend_strategy/data/basis_ratio.h5')
        
        # refresh stdin dict and stdout dict
        stdindict = para_dict['std_in_dict']
        stdoutdict = para_dict['std_out_dict']
        
        for ticker in tickerlist:
            if ticker not in stdindict.keys():
                stdindict[ticker] = 0.02
            stdoutdict[ticker] = stdindict[ticker]+0.01
            
        para_dict['std_in_dict'] = stdindict
        para_dict['std_out_dict'] = stdoutdict
        
        self.data_main = data_main
        self.data_all = data_all
        self.multip = multip
        self.para_dict = para_dict
        self.univ_data = univ_data
        self.sharesadj = sharesadj
        self.tickerlist = tickerlist
        
        self.std_df = std_df
        self.basis_df = basis_df
    
    def calc_basis_ratio(self, trading_day):
        if not isinstance(trading_day,pd.Timestamp):
            trading_day = pd.Timestamp(trading_day)
        test_all = self.data_all.loc[trading_day]
        basis_ratio_list = []
        for ticker in self.tickerlist:
            test = test_all[test_all['prod_id'] == ticker]
            if len(test) < 3:
                basis_ratio = np.nan
            else:
                # main                
                idx_main = test['oi'].argmax()
                main_contract = test.index[idx_main]
                # secmain
                test1 = test[test.index != main_contract]
                idx_secmain = test1['oi'].argmax()
                secmain_contract = test1.index[idx_secmain]
                # thirdmain
                test2 = test[~test.index.isin([main_contract,secmain_contract])]
                idx_thirdmain = test2['oi'].argmax()
                thirdmain_contract = test2.index[idx_thirdmain]
                # get close price
                close_main = test.loc[main_contract]['close']
                close_secmain = test.loc[secmain_contract]['close']
                close_thirdmain = test.loc[thirdmain_contract]['close']
                
                main_ym = re.findall(r'\d+',main_contract)[0]
                secmain_ym = re.findall(r'\d+',secmain_contract)[0]
                thirdmain_ym = re.findall(r'\d+',thirdmain_contract)[0]
                
                first_str_list = [main_ym[0],secmain_ym[0],thirdmain_ym[0]]
                if ('9' in first_str_list) and ('0' in first_str_list):
                    main_ym = '1' + main_ym if main_ym[0] != '9' else main_ym
                    secmain_ym = '1' + secmain_ym if secmain_ym[0] != '9' else secmain_ym
                    thirdmain_ym = '1' + thirdmain_ym if thirdmain_ym[0] != '9' else thirdmain_ym
                else:
                    main_ym = '1' + main_ym
                    secmain_ym = '1' + secmain_ym
                    thirdmain_ym = '1' + thirdmain_ym
                
                main_ym_int = int(main_ym)
                secmain_ym_int = int(secmain_ym)
                thirdmain_ym_int = int(thirdmain_ym)                
                pd_s = pd.Series([close_main,close_secmain,close_thirdmain],index = [main_ym_int,secmain_ym_int,thirdmain_ym_int])                                
                #pd_s.index = [contract2yearmonth(i) for i in pd_s.index]
                pd_s = pd_s.sort_index()
                
                if (pd_s.iloc[0] - pd_s.iloc[1]) * (pd_s.iloc[1] - pd_s.iloc[2]) <= 0:
                    basis_ratio = np.nan
                else:
                    basis_ratio = (pd_s.iloc[2] - pd_s.iloc[0]) / ((pd_s.index[2] - pd_s.index[0])%88) * 12 / close_main
            basis_ratio_list.append(basis_ratio)
        
        basis_ratio_df = pd.Series(basis_ratio_list,index = self.tickerlist)
        basis_ratio_df.name = 'basis_ratio'
        basis_ratio_df.index.name = 'Ticker'
        return basis_ratio_df.to_frame()            
                            
    def get_action_param_ticker_trend(self, set_date, ticker, pos = 0):
        trade_date = dt.get_trading_day_offset(set_date,0)[0]        
        pre_date = dt.get_trading_day_offset(trade_date, -70)[0]
            
        data_slice = self.data_main.loc[pre_date:trade_date]
        days_slice = np.unique(data_slice.index.get_level_values(level=0))
        if (trade_date not in days_slice) | (pre_date not in days_slice):
            raise('data missing!')
        
        prod_data = data_slice.xs(ticker,level=1)
        clsadj = prod_data['close'] - prod_data['gap']
        clsadj = clsadj.sort_index(ascending=False)
        pricelist = clsadj.iloc[:59].tolist()
        rt = prod_data['close']/prod_data['pre_close']-1
        rt = rt.sort_index(ascending=False)
        rtlist = rt.iloc[:9].tolist()
        
        tr_daily = pd.concat([abs(prod_data['high'] - prod_data['low']),abs(prod_data['high']-prod_data['pre_close']),
                              abs(prod_data['low']-prod_data['pre_close'])],axis=1).max(axis=1)
        tr_daily = tr_daily.sort_index(ascending=False)
        trlist = tr_daily.iloc[:19].tolist()            
        
        basis_ticker = self.basis_df.xs(ticker,level=1)['basis_ratio']
        basis_ticker = basis_ticker.reindex(prod_data.index)
        basis_ticker = basis_ticker.sort_index(ascending=False)
        basislist = basis_ticker.iloc[:4].tolist()
        
        if (len(pricelist) < 59) | (len(rtlist) < 9) | (len(basislist) < 4):
            price_longin_down = np.nan
            price_longin_up = np.nan
            price_shortin_down = np.nan
            price_shortin_up = np.nan
            price_longout_down = np.nan
            price_longout_up = np.nan
            price_shortout_down = np.nan
            price_shortout_up = np.nan
            contract_cur = 'N/A'
            cls_cur = np.nan
            print('wrong length of price or ret or basis!')
        
        else:
            data_use = self.data_all[self.data_all['prod_id'] == ticker]
            #data_use = data_use[data_use['expiration_days'] > 20]
            # cur date
            data_ticker_cur = data_use.loc[trade_date]
            data_ticker_cur1 = data_ticker_cur[data_ticker_cur['expiration_days'] > 20]
            
            idx = data_ticker_cur1['oi'].argmax()
            contract_cur = data_ticker_cur1.index[idx]  # predict next day contract
            cls_cur = data_ticker_cur1['close'].iloc[idx]
            
            contract_pre = self.data_main.loc[(trade_date, ticker)]['contract'] # current day contract
            
            clsorg0 = data_ticker_cur.loc[(contract_cur,'close')]
            cls_pre = data_ticker_cur.loc[(contract_pre,'close')]
                                    
            gap0 = prod_data.loc[trade_date, 'gap'] + clsorg0 - cls_pre
            
            ## set parameters
            std_in_thd = 1
            std_out_thd = 1
                        
            daily_ret_out = para_dict['daily_ret_out']
            lw = para_dict['sw']

            ####################################################################################
            # 1. Postion is 0, find the long parm
            # subject to ma condition

            if pos == 0:
                x1 = sum(pricelist[:4])/4 # cls > ma5
                x2 = sum(pricelist[4:9])-sum(pricelist[:4]) #ma5 > ma10
                x3 = sum(pricelist[9:19]) - sum(pricelist[:9]) # ma10 > ma20
                x4 = 2*sum(pricelist[19:29]) - sum(pricelist[:19]) # ma20 > ma30
                x5 = sum(pricelist[29:59]) - sum(pricelist[:29]) # ma30 > ma60
                rx = find_x_range(rtlist, std_in_thd)

                if rx is None:
                    price_longin_down = np.nan
                    price_longin_up = np.nan
                    price_shortin_down = np.nan
                    price_shortin_up = np.nan
                else:
                    price_in_down_std = clsorg0 * (1 + rx[0])
                    price_in_up_std = clsorg0 * (1 + rx[1])
                    # calc longin ma price
                    price_longin_ma = max([x1,x2,x3,x4,x5]) + gap0    
                    price_shortin_ma = min([x1,x2,x3,x4,x5]) + gap0
                    
                    # calc long in price    
                    if price_in_up_std <= price_longin_ma:
                        price_longin_down = np.nan
                        price_longin_up = np.nan
                    elif (price_in_down_std <= price_longin_ma):
                        price_longin_down = price_longin_ma
                        price_longin_up = price_in_up_std
                    else:
                        price_longin_down = price_in_down_std
                        price_longin_up = price_in_up_std
                    
                    # calc short in price    
                    if price_shortin_ma <= price_in_down_std:
                        price_shortin_down = np.nan
                        price_shortin_up = np.nan
                    elif (price_shortin_ma < price_in_up_std):
                        price_shortin_down = price_in_down_std
                        price_shortin_up = price_shortin_ma
                    else:
                        price_shortin_down = price_in_down_std
                        price_shortin_up = price_in_up_std
                
                price_longout_down = np.nan
                price_longout_up = np.nan
                price_shortout_down = np.nan
                price_shortout_up = np.nan   
                
            elif pos == 1:    
                ########################################################################        
                price_longout_turtle = min(pricelist[:lw]) + gap0 # turtle out
                #(2) dailyreturn out: dailyretlongout = (rt < -daily_ret_out)
                price_longout_dailyret = clsorg0 * (1-daily_ret_out)
                price_longout_0 = max(price_longout_turtle, price_longout_dailyret)
                            
                #(3) stdout: 
                rxout = find_x_range(rtlist, std_out_thd)

                if rxout is None:
                    print('must be out!')
                    price_longout_down = np.inf
                    price_longout_up = -np.inf
                else:
                    price_out_down_std = clsorg0*(1+rxout[0])
                    price_out_up_std = clsorg0*(1+rxout[1])

                    if price_longout_0 >= price_out_up_std: #must be out
                        price_longout_down = np.inf
                        price_longout_up = -np.inf
                    elif price_longout_0 >= price_out_down_std:
                        price_longout_down = price_longout_0
                        price_longout_up = price_out_up_std
                    else:
                        price_longout_down = price_out_down_std
                        price_longout_up = price_out_up_std
                
                price_longin_down = np.nan
                price_longin_up = np.nan
                price_shortin_down = np.nan
                price_shortin_up = np.nan
                price_shortout_down = np.nan
                price_shortout_up = np.nan

            elif pos == -1:
                ##################################################################################
            
                price_shortout_turtle = max(pricelist[:lw]) + gap0 # turtle out
                #(2) dailyreturn out: dailyretlongout = (rt < -daily_ret_out)
                price_shortout_dailyret = clsorg0 * (1 + daily_ret_out)
                price_shortout_0 = min(price_shortout_turtle, price_shortout_dailyret)
                            
                #(3) stdout: 
                rxout = find_x_range(rtlist, std_out_thd)
                if rxout is None:
                    print('must be out!')
                    price_shortout_down = np.inf
                    price_shortout_up = -np.inf
                else:
                    price_out_std_down = clsorg0*(1+rxout[0])
                    price_out_std_up = clsorg0*(1+rxout[1])

                    if price_shortout_0 <= price_out_std_down: #must be out
                        price_shortout_down = np.inf
                        price_shortout_up = -np.inf
                        
                    elif price_shortout_0 <= price_out_std_up:
                        price_shortout_down = price_out_std_down
                        price_shortout_up = price_shortout_0
                    else:
                        price_shortout_down = price_out_std_down
                        price_shortout_up = price_out_std_up
                price_longin_down = np.nan
                price_longin_up = np.nan
                price_shortin_down = np.nan
                price_shortin_up = np.nan
                price_longout_down = np.nan
                price_longout_up = np.nan
            
            else:
                price_longin_down = np.nan
                price_longin_up = np.nan
                price_shortin_down = np.nan
                price_shortin_up = np.nan
                price_longout_down = np.nan
                price_longout_up = np.nan
                price_shortout_down = np.nan
                price_shortout_up = np.nan
        
        action_parm = {'maincontract':contract_cur,'longin_down':price_longin_down,'longin_up':price_longin_up,'shortin_down':price_shortin_down,'shortin_up':price_shortin_up,
                      'longout_down':price_longout_down,'longout_up':price_longout_up,'shortout_down':price_shortout_down,'shortout_up':price_shortout_up,
                      'rtlist':str(rtlist),'trlist':str(trlist),'basislist':str(basislist),'cls_main_org':cls_cur}
        action_df = pd.DataFrame.from_dict(action_parm,orient = 'index')
        action_df.columns = [ticker]
        action_df = action_df.T
        action_df.index.name = 'Ticker'
        return action_df
    
    def get_action_param_ticker_basis(self, set_date, ticker, pos = 0):
        trade_date = dt.get_trading_day_offset(set_date,0)[0]        
        pre_date = dt.get_trading_day_offset(trade_date, -70)[0]
        data_slice = self.data_main.loc[pre_date:trade_date]
        days_slice = np.unique(data_slice.index.get_level_values(level=0))
        if (trade_date not in days_slice) | (pre_date not in days_slice):
            raise('data missing!')
        
        prod_data = data_slice.xs(ticker,level=1)
        clsadj = prod_data['close'] - prod_data['gap']
        clsadj = clsadj.sort_index(ascending=False)
        pricelist = clsadj.iloc[:59].tolist()
        rt = prod_data['close']/prod_data['pre_close']-1
        rt = rt.sort_index(ascending=False)
        rtlist = rt.iloc[:9].tolist()
        
        tr_daily = pd.concat([abs(prod_data['high'] - prod_data['low']),abs(prod_data['high']-prod_data['pre_close']),
                              abs(prod_data['low']-prod_data['pre_close'])],axis=1).max(axis=1)
        tr_daily = tr_daily.sort_index(ascending=False)
        trlist = tr_daily.iloc[:19].tolist()            
        
        # basis list
        basis_ticker = self.basis_df.xs(ticker,level=1)['basis_ratio']
        basis_ticker = basis_ticker.reindex(prod_data.index)
        basis_ticker = basis_ticker.sort_index(ascending=False)
        basislist = basis_ticker.iloc[:4].tolist()
        
        if (len(pricelist) < 59) | (len(rtlist) < 9) | (len(basislist) < 4):
            price_longin_down = np.nan
            price_longin_up = np.nan
            price_shortin_down = np.nan
            price_shortin_up = np.nan
            price_longout_down = np.nan
            price_longout_up = np.nan
            price_shortout_down = np.nan
            price_shortout_up = np.nan
            contract_cur = 'N/A'
            cls_cur = np.nan
            print('wrong length of price or ret or basis!')
        
        else:
            data_use = self.data_all[self.data_all['prod_id'] == ticker]
            data_ticker_cur = data_use.loc[trade_date]
            data_ticker_cur1 = data_ticker_cur[data_ticker_cur['expiration_days'] > 20]
            
            idx = data_ticker_cur1['oi'].argmax()
            contract_cur = data_ticker_cur1.index[idx]  # predict next day contract
            cls_cur = data_ticker_cur1['close'].iloc[idx]            
            contract_pre = self.data_main.loc[(trade_date, ticker)]['contract'] # current day contract
            
            clsorg0 = data_ticker_cur.loc[(contract_cur,'close')]
            cls_pre = data_ticker_cur.loc[(contract_pre,'close')]                                    
            gap0 = prod_data.loc[trade_date, 'gap'] + clsorg0 - cls_pre
                        
            ## set parameters
            std_in_thd = 1
            std_out_thd = 1
                        
            lw = para_dict['sw']

            ####################################################################################
            # 1. Postion is 0, find the long parm
            # subject to ma condition

            if pos == 0:
                x6 = sum(pricelist[4:19])/3 - sum(pricelist[:4]) # ma5 > ma20
                rx = find_x_range(rtlist, std_in_thd)

                if rx is None:
                    price_longin_down = np.nan
                    price_longin_up = np.nan
                    price_shortin_down = np.nan
                    price_shortin_up = np.nan
                else:
                    price_in_down_std = clsorg0 * (1 + rx[0])
                    price_in_up_std = clsorg0 * (1 + rx[1])
                    # calc longin ma price
                    price_longin_ma = x6 + gap0    
                    price_shortin_ma = x6 + gap0
                    
                    # calc long in price    
                    if price_in_up_std <= price_longin_ma:
                        price_longin_down = np.nan
                        price_longin_up = np.nan
                    elif (price_in_down_std <= price_longin_ma):
                        price_longin_down = price_longin_ma
                        price_longin_up = price_in_up_std
                    else:
                        price_longin_down = price_in_down_std
                        price_longin_up = price_in_up_std
                    
                    # calc short in price    
                    if price_shortin_ma <= price_in_down_std:
                        price_shortin_down = np.nan
                        price_shortin_up = np.nan
                    elif (price_shortin_ma < price_in_up_std):
                        price_shortin_down = price_in_down_std
                        price_shortin_up = price_shortin_ma
                    else:
                        price_shortin_down = price_in_down_std
                        price_shortin_up = price_in_up_std
                
                price_longout_down = np.nan
                price_longout_up = np.nan
                price_shortout_down = np.nan
                price_shortout_up = np.nan   
                
            elif pos == 1:    
                price_longout_turtle = min(pricelist[:lw]) + gap0 # turtle out
                price_longout_0 = price_longout_turtle
                rxout = find_x_range(rtlist, std_out_thd)

                if rxout is None:
                    print('must be out!')
                    price_longout_down = np.inf
                    price_longout_up = -np.inf
                else:
                    price_out_down_std = clsorg0*(1+rxout[0])
                    price_out_up_std = clsorg0*(1+rxout[1])

                    if price_longout_0 >= price_out_up_std: #must be out
                        price_longout_down = np.inf
                        price_longout_up = -np.inf
                    elif price_longout_0 >= price_out_down_std:
                        price_longout_down = price_longout_0
                        price_longout_up = price_out_up_std
                    else:
                        price_longout_down = price_out_down_std
                        price_longout_up = price_out_up_std
                
                price_longin_down = np.nan
                price_longin_up = np.nan
                price_shortin_down = np.nan
                price_shortin_up = np.nan
                price_shortout_down = np.nan
                price_shortout_up = np.nan

            elif pos == -1:            
                price_shortout_turtle = max(pricelist[:lw]) + gap0 # turtle out
                price_shortout_0 = price_shortout_turtle
                            
                #(3) stdout: 
                rxout = find_x_range(rtlist, std_out_thd)
                if rxout is None:
                    print('must be out!')
                    price_shortout_down = np.inf
                    price_shortout_up = -np.inf
                else:
                    price_out_std_down = clsorg0*(1+rxout[0])
                    price_out_std_up = clsorg0*(1+rxout[1])

                    if price_shortout_0 <= price_out_std_down: #must be out
                        price_shortout_down = np.inf
                        price_shortout_up = -np.inf
                        
                    elif price_shortout_0 <= price_out_std_up:
                        price_shortout_down = price_out_std_down
                        price_shortout_up = price_shortout_0
                    else:
                        price_shortout_down = price_out_std_down
                        price_shortout_up = price_out_std_up
                price_longin_down = np.nan
                price_longin_up = np.nan
                price_shortin_down = np.nan
                price_shortin_up = np.nan
                price_longout_down = np.nan
                price_longout_up = np.nan
            
            else:
                price_longin_down = np.nan
                price_longin_up = np.nan
                price_shortin_down = np.nan
                price_shortin_up = np.nan
                price_longout_down = np.nan
                price_longout_up = np.nan
                price_shortout_down = np.nan
                price_shortout_up = np.nan
            
        # action: 
        #longin: price_longin_down < price < price_longin_up
        #shortin: price_shortin_down < price < price_shortin_up
        #longout: (price < price_longout_down) or (price > price_longout_up)
        #shortin: (price < price_shortout_down) or (price > price_shortout_up)

        action_parm = {'maincontract':contract_cur,'longin_down':price_longin_down,'longin_up':price_longin_up,'shortin_down':price_shortin_down,'shortin_up':price_shortin_up,
                      'longout_down':price_longout_down,'longout_up':price_longout_up,'shortout_down':price_shortout_down,'shortout_up':price_shortout_up,
                      'rtlist':str(rtlist),'trlist':str(trlist),'basislist':str(basislist),'cls_main_org':cls_cur}
        action_df = pd.DataFrame.from_dict(action_parm,orient = 'index')
        action_df.columns = [ticker]
        action_df = action_df.T
        action_df.index.name = 'Ticker'
        return action_df
    
    
    def get_trade_parameters(self, date, pos_df, get_cfe = True, strategy = 'trend'):
        cols_select = ['pos','hds','intime','inpriceorg','inpriceadj','incontract','curpriceorg','curpriceadj','curcontract','shares']
        data_all = self.data_all
        amt_max = data_all.groupby(['dt','prod_id'])['amount'].max()
        univ = amt_max[amt_max > 1e6]
        univlist = univ.loc[pd.Timestamp(date)].index        
        trade_date = dt.get_trading_day_offset(date,0)[0]        
        pre_date = dt.get_trading_day_offset(date, -100)[0]
        data_slice = self.data_main.loc[pre_date:trade_date]        
        
        # get trend parms：
        para_list = []
        for ticker in pos_df.index:
            prod_data = data_slice.xs(ticker,level=1)
            price_len = len(prod_data) 
            if price_len < 59:
                continue
            if (get_cfe & (ticker[-3:] != 'CFE')) | ((not get_cfe)&(ticker[-3:] == 'CFE')):                
                continue                            
            pos = pos_df.loc[ticker,'pos']
            if ((pos == 0)&((ticker not in univlist) | (self.para_dict['std_in_dict'][ticker] == 0))) | ((abs(pos) > 0) & (abs(pos) < 0.5)):
                continue
            hold_df = pos_df.loc[[ticker]]
            hold_df = hold_df[cols_select]
            if strategy == 'trend':
                action_df = self.get_action_param_ticker_trend(date, ticker, pos = pos)
            elif strategy == 'basis':
                action_df = self.get_action_param_ticker_basis(date, ticker, pos = pos)
            else:
                raise ValueError('strategy can only trend or basis!')                
            tmp = pd.concat([hold_df,action_df],axis=1)
            # contract to test with is main to trade
            data_all1 = data_all.loc[pd.Timestamp(date)]
            contract = data_all1[(data_all1['prod_id'] == ticker)&(data_all1['expiration_days']>20)].sort_values(by = 'oi',ascending=False).index[:4]
            contract = ','.join(contract)
            tmp['contractlist'] = contract
            if pos == 0:
                tmp['std_thd'] = self.para_dict['std_in_dict'][ticker]
            else:
                tmp['std_thd'] = self.para_dict['std_out_dict'][ticker]            
            para_list.append(tmp)
        para_df = pd.concat(para_list)        
        
        shares_adj_cur = self.sharesadj.loc[date]
        shares_adj_cur.name = 'shares_adj'        
        basis_ratio_df = self.calc_basis_ratio(date)
        std_df = self.std_df.loc[pd.Timestamp(date)]
        
        para_df1 = para_df.join(shares_adj_cur).join(self.multip).join(basis_ratio_df).join(std_df)
        para_df1['shares1'] = round(self.para_dict['cap'] / para_df1['curpriceorg']/para_df1['multiplier']*para_df1['shares_adj'])
        para_df1['shares_target'] = para_df1['shares'].where(para_df1['pos']!=0, other = para_df1['shares1'])
        para_df1['cap'] = self.para_dict['cap']/10000
        para_df1['t1'] = '14:55:00'
        para_df1['t2'] = '14:59:30'
        para_df1['expiration_days'] = self.data_all.loc[pd.Timestamp(date)].loc[para_df['curcontract']]['expiration_days'].values
        return para_df1
        
    def get_trade_parameters_add_true_position(self, date, pos_df_trend, pos_df_basis, ratio_list = [1,1], get_cfe = False):
        # need to wait flags!
        # ratio_list should be money [trend: basis]:1:0, all give to trend, 1:1, equal weight
        
        para_df_trend = self.get_trade_parameters(date, pos_df_trend, get_cfe = get_cfe, strategy = 'trend')
        para_df_basis = self.get_trade_parameters(date, pos_df_basis, get_cfe = get_cfe, strategy = 'basis')
                                
        pos = pd.read_excel('/data/user/011477/Arrow/' + date + '_Spiral.xlsx',sheet_name = 'Spiral持仓情况')
        pos = pos[pos['当前数量']!=0]
        pos['exchange_id'] = pos['交易市场'].apply(lambda x: exchange_dict[x])
        pos['contract_holding'] = pos['证券代码'].apply(lambda x:x.upper()) + '.' + pos['exchange_id']
        pos['Ticker'] = pos['证券代码'].apply(lambda x:find_str(x)) + '.' + pos['exchange_id']
        pos['shares_holding'] = pos['当前数量']
        pos = pos.set_index('Ticker')
        
        trend_target = pos_df_trend[['pos','shares']].reindex(pos.index)
        basis_target = pos_df_basis[['pos','shares']].reindex(pos.index)
                
        sharespct = trend_target['shares'] / (trend_target['shares']*ratio_list[0] + basis_target['shares']*ratio_list[1])
        sharespct = sharespct.fillna(1)

        pos['shares_trend'] = round(pos['shares_holding'] * sharespct,0)
        pos['shares_basis'] = pos['shares_holding'] - pos['shares_trend']

        # get trend parameters
        para_df_trend = pd.concat([para_df_trend,pos[['contract_holding','shares_trend']]],axis=1).rename(columns = {'shares_trend':'shares_holding'})
        para_df_trend.index.name = 'Ticker'
        para_df_trend['pos'] = para_df_trend['pos'].fillna(0)
        para_df_trend['shares_holding'] = para_df_trend['shares_holding'].fillna(0)
        para_df_trend['curcontract'] = para_df_trend['curcontract'].where(pd.isna(para_df_trend['contract_holding']),other = para_df_trend['contract_holding'])
        para_df_trend['prod_id'] = [i.split('.')[0] for i in para_df_trend.index]
        para_df_trend['exchange'] = [i.split('.')[1] for i in para_df_trend.index]
        para_df_trend = para_df_trend.sort_values(by = ['exchange','prod_id'])
        if get_cfe:
            para_df_trend = para_df_trend[para_df_trend['exchange'] == 'CFE']
        else:
            para_df_trend = para_df_trend[para_df_trend['exchange'] != 'CFE']
        ## slice trend parm to trade and track       
        para_trend_fortrade = para_df_trend[['pos','shares_holding','curcontract','maincontract','contractlist','longin_down','longin_up','shortin_down','shortin_up',\
                                     'longout_down','longout_up','shortout_down','shortout_up','cap','t1','t2','std_thd','multiplier','rtlist','trlist',\
                                     'basislist','cls_main_org']]
        para_trend_forwind = para_df_trend[['multiplier','pos','shares_holding','shares_target','hds','intime','inpriceorg','curcontract',
                                 'expiration_days', 'basis_ratio', 'std_10d', 'std_thd',
                                    'longin_down','shortin_up','longout_down','shortout_up']]
        
        para_trend_forwind.index = [i.replace('ZCE','CZC') if i.endswith('ZCE') else i for i in para_trend_forwind.index]
        para_trend_forwind['curcontract'] = para_trend_forwind['curcontract'].apply(lambda x:x.replace('ZCE','CZC') if x.endswith('ZCE') else x)
        para_trend_forwind.index.name = 'Ticker'
        
        # get basis parameters
        para_df_basis = pd.concat([para_df_basis,pos[['contract_holding','shares_basis']]],axis=1).rename(columns = {'shares_basis':'shares_holding'})
        para_df_basis.index.name = 'Ticker'
        para_df_basis['pos'] = para_df_basis['pos'].fillna(0)
        para_df_basis['shares_holding'] = para_df_basis['shares_holding'].fillna(0)
        para_df_basis['curcontract'] = para_df_basis['curcontract'].where(pd.isna(para_df_basis['contract_holding']),other = para_df_basis['contract_holding'])
        para_df_basis['prod_id'] = [i.split('.')[0] for i in para_df_basis.index]
        para_df_basis['exchange'] = [i.split('.')[1] for i in para_df_basis.index]
        para_df_basis = para_df_basis.sort_values(by = ['exchange','prod_id'])
        if get_cfe:
            para_df_basis = para_df_basis[para_df_basis['exchange'] == 'CFE']
        else:
            para_df_basis = para_df_basis[para_df_basis['exchange'] != 'CFE']
        ## slice basis parm to trade and track       
        para_basis_fortrade = para_df_basis[['pos','shares_holding','curcontract','maincontract','contractlist','longin_down','longin_up','shortin_down','shortin_up',\
                                     'longout_down','longout_up','shortout_down','shortout_up','cap','t1','t2','std_thd','multiplier','rtlist','trlist',\
                                     'basislist','cls_main_org']]
        para_basis_forwind = para_df_basis[['multiplier','pos','shares_holding','shares_target','hds','intime','inpriceorg','curcontract',
                                 'expiration_days', 'basis_ratio', 'std_10d', 'std_thd',
                                    'longin_down','shortin_up','longout_down','shortout_up']]
        
        para_basis_forwind.index = [i.replace('ZCE','CZC') if i.endswith('ZCE') else i for i in para_basis_forwind.index]
        para_basis_forwind['curcontract'] = para_basis_forwind['curcontract'].apply(lambda x:x.replace('ZCE','CZC') if x.endswith('ZCE') else x)
        para_basis_forwind.index.name = 'Ticker'        
        
        return para_trend_fortrade, para_trend_forwind, para_basis_fortrade, para_basis_forwind
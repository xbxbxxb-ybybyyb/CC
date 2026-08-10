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

def contract2yearmonth(contract):
    num_str = '1' + re.findall(r'\d+',contract)[0]
    return int(num_str)
     
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


class Pos_4():
    def __init__(self, start_date = 20160101, end_date = 20250501):
        # data_main        
        data_main = IO.read_data([start_date, end_date],alt = 
                '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/MD/DAILY/MD_MAIN_CHINA_COMMODITY_DAILY.h5')
        tcs = data_main.index.get_level_values(level=1)
        idx = [type(i) == str for i in tcs]
        data_main= data_main[idx]
        blacklist = ['ZC.ZCE','IMS.SHF','SCTAS.INE','TC.ZCE','EFS.CFE','AFS.CFE','LR.ZCE','JR.ZCE','PM.ZCE','RI.ZCE',
                        'BB.DCE','RS.ZCE','WR.SHF','WH.ZCE','FB.DCE','CY.ZCE','RR.DCE','PR.ZCE','LG.DCE',
                        'TS.CFE','TF.CFE','T.CFE','TL.CFE','IH.CFE','IM.CFE',
                        'BR.SHF','BU.SHF','FU.SHF','PB.SHF','SS.SHF','PG.DCE','PP.DCE','PF.ZCE','PK.ZCE','SF.ZCE']
        # ticker list to trade
        tickerlist_all = np.unique(data_main.index.get_level_values(level=1))
        tickerlist = [i for i in tickerlist_all if i not in blacklist]
        
        # data_all contracts
        pre_date = dt.get_trading_day_offset(start_date,-1)[0]
        data_all = IO.read_data([pre_date, end_date],alt = 
                    '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/MD/DAILY/MD_CHINA_FUTURE_DAILY.h5')
        
        # univ data
#        univ_data = pd.read_hdf('/dfs/group/800466/warehouse/test/CHINA_COMMODITIES/UNIV/test_amt10.h5')
#        univ_data = univ_data[univ_data['amt_1e10']]
        
        amt_max = data_all.groupby(['dt','prod_id'])['amount'].max()
        tmp = amt_max[amt_max > 1e6]
        tmp.loc[:] = True
        tmp = tmp.unstack().shift(1)
        tmp.columns.name = 'Ticker'
        univ_data = pd.DataFrame(tmp.stack(),columns = ['amt_1e10'])
        
        # multip
        info = pd.read_csv('/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/INFO/WIND_CFuturesContPro.csv')
        # delete simulation and IB codes
        info.loc[:,'EXCHANGE'] = [i.split('.')[1] for i in info['S_INFO_WINDCODE']]
        info.loc[:,'sim'] = [len(i.split('-')) for i in info['S_INFO_CODE']]
        info.loc[:,'sim2'] = [len(i.split('_')) for i in info['S_INFO_CODE']]
        info_select = info[(info['EXCHANGE']!='IB') & (info['sim'] < 2)& (info['sim2'] < 2)]                    
        info_select.loc[:,'Ticker'] = info_select['S_INFO_CODE'] + '.' + info_select['EXCHANGE']
        info_select.loc[:,'multiplier'] = info_select['S_INFO_PUNIT'].where(np.isnan(info_select['S_INFO_CEMULTIPLIER']),other = info_select['S_INFO_CEMULTIPLIER'])
        info_select['Ticker'] = [i.split('.')[0] + '.ZCE' if i.split('.')[1] == 'CZC' else i for i in info_select['Ticker']]
        multip = info_select.groupby('Ticker')[['multiplier']].last()
        bllist = ['IFM.CFE','SCTAS.INE']
        multip = multip.loc[~multip.index.isin(bllist)]
        
        
        sharesadj_list = []
        for ticker in tickerlist:
            prod_data = data_main.xs(ticker,level=1)
            tr_daily = pd.concat([abs(prod_data['high'] - prod_data['low']),abs(prod_data['high']-prod_data['pre_close']),abs(prod_data['low']-prod_data['pre_close'])],axis=1).max(axis=1)
            atr = tr_daily.rolling(20,min_periods = 10).mean()
            w = prod_data['close'] / atr
            sharesadj_list.append(w)
        sharesadj = pd.concat(sharesadj_list,axis=1) / 20
        sharesadj[sharesadj > 10] = 10
        sharesadj.columns = tickerlist
        
        # refresh stdin dict and stdout dict
        stdindict = para_dict['std_in_dict']
        stdoutdict = para_dict['std_out_dict']
        
        for ticker in tickerlist:
            if not ticker.endswith('CFE'):
                stdindict[ticker] = 0.01
            stdoutdict[ticker] = stdindict[ticker] + 0.01            
        para_dict['std_in_dict'] = stdindict
        para_dict['std_out_dict'] = stdoutdict
        
        self.data_main = data_main
        self.data_all = data_all
        self.multip = multip
        self.para_dict = para_dict
        self.univ_data = univ_data
        self.sharesadj = sharesadj
        self.tickerlist = tickerlist
        std_list = []
        for ticker in tickerlist:
            data_prod = data_main.xs(ticker,level=1)
            rt = data_prod['close'] / data_prod['pre_close'] - 1
            rt_std = rt.rolling(10,min_periods = 10).std()
            rt_std.name = ticker
            std_list.append(rt_std)
        self.std_df = pd.DataFrame(pd.concat(std_list,axis=1).stack(),columns = ['std_20d']).sort_index()   
    
    def get_trade_df(self, daily_df):
        ticker_list = np.unique(daily_df.index.get_level_values(level = 1))
        trade_df_list = []
        feerate = self.para_dict['feetotal']
        for ticker in ticker_list:
            mult = self.multip.loc[ticker,'multiplier']
            df_ticker = daily_df.xs(ticker,level=1)
            df_ticker_trade = df_ticker[df_ticker['pos'].diff().fillna(0) !=0]
            in_df = df_ticker_trade[df_ticker_trade['pos']!=0][['pos','shares','sharesadj','intime','inpriceorg','inpriceadj']].set_index('intime')
            out_df = df_ticker_trade[df_ticker_trade['pos']==0][['intime','extime','expriceorg','expriceadj','hds']].set_index('intime')
            trade_df = pd.concat([in_df,out_df],axis=1)
            trade_df['open_money'] = trade_df['inpriceorg'] * trade_df['shares'] * mult        
            trade_df['perpnl'] = (trade_df['expriceadj'] - trade_df['inpriceadj']) * trade_df['pos'] * trade_df['shares'] * mult - trade_df['shares'] * (trade_df['inpriceorg'] + trade_df['expriceorg'])*mult*feerate
            trade_df['perret'] = trade_df['perpnl'] / trade_df['open_money']
            trade_df['Ticker'] = ticker
            trade_df_list.append(trade_df.reset_index())
        pertrade_df = pd.concat(trade_df_list,axis=0).set_index(['Ticker','intime'])
        return pertrade_df
    
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
                idx_main = test['volume'].argmax()
                main_contract = test.index[idx_main]
                # secmain
                test1 = test[test.index != main_contract]
                idx_secmain = test1['volume'].argmax()
                secmain_contract = test1.index[idx_secmain]
                # thirdmain
                test2 = test[~test.index.isin([main_contract,secmain_contract])]
                idx_thirdmain = test2['volume'].argmax()
                thirdmain_contract = test2.index[idx_thirdmain]
                # get close price
                close_main = test.loc[main_contract]['close']
                close_secmain = test.loc[secmain_contract]['close']
                close_thirdmain = test.loc[thirdmain_contract]['close']
                
                pd_s = pd.Series([close_main,close_secmain,close_thirdmain],index = [main_contract,secmain_contract,thirdmain_contract])
                pd_s.index = [contract2yearmonth(i) for i in pd_s.index]
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
                       
    def singlebacktest(self, ticker, use_univ = True):
        # 1、para prepare        
        prod_data = self.data_main.xs(ticker,level=1)
        # multiplier
        #mult = prod_data['multiplier']
        mult = self.multip.loc[ticker,'multiplier']
        
        ## trade parameters
        lw = self.para_dict['lw']        
        sw = self.para_dict['sw']
        daily_ret_out = self.para_dict['daily_ret_out']
        cap = self.para_dict['cap']
        feetotal = self.para_dict['feetotal']        
        std_in_thd = self.para_dict['std_in_dict'][ticker]
        std_out_thd = self.para_dict['std_out_dict'][ticker]    
        
        ## variables
        clsorg = prod_data['close']
        clsadj = prod_data['close']-prod_data['gap']        
        rt = prod_data['close']/prod_data['pre_close']-1
        rt_std = rt.rolling(10,min_periods =10).std()
       
        ## turtle signal
        eH = clsadj.rolling(lw,min_periods = int(lw/2)).max().shift(1)
        eL = clsadj.rolling(lw, min_periods = int(lw/2)).min().shift(1)
        xH = clsadj.rolling(sw,min_periods = int(sw/2)).max().shift(1)
        xL = clsadj.rolling(sw,min_periods = int(sw/2)).min().shift(1)
        #emid = (eH+eL)/2                
        turtlelongin = (clsadj > eH).astype(int)
        turtleshortin = (clsadj < eL).astype(int)
        turtlelongout = (clsadj < xL).astype(int)
        turtleshortout = (clsadj > xH).astype(int)
        ## masignal
               
        ## dailyret signal
        dailyretlongout = (rt < -daily_ret_out)
        dailyretshortout = (rt > daily_ret_out)
        
        ## std signal
        stdin = (rt_std < std_in_thd)
        stdout = (rt_std > std_out_thd)
        
        ### signal construct
        longin =  turtlelongin & stdin
        shortin =  turtleshortin & stdin
        
        
        # 3、 signal backtest
        poslist = [0]
        poslist2 = [0]
        hdslist = [0]  # holding period
        
        intimelist = [pd.NaT]
        inpriceorglist = [np.nan]
        inpriceadjlist = [np.nan]
        incontractlist = ['N/A']
        
        extimelist = [pd.NaT]
        expriceorglist = [np.nan]
        expriceadjlist = [np.nan]
        excontractlist = ['N/A']
        
        curpriceorglist = [np.nan]
        curpriceadjlist = [np.nan]
        curcontractlist = ['N/A']
        
        shareslist = [0]
        sharesadjlist = [0]
        dailypnllist = [0]
        
        hds = 0
        cur_pos = 0
        cur_pos_real = 0
        
        for i in range(1,len(prod_data)):
            cur_date = prod_data.index[i]
            curcontract = prod_data['contract'].iloc[i]
            curpriceorg = clsorg.iloc[i]
            curpriceadj = clsadj.iloc[i]
            sharesadj = self.sharesadj.loc[cur_date,ticker]
            
            if cur_pos == 0:   
                hds = 0     
                if (use_univ & (ticker not in self.univ_data.loc[cur_date].index)):  # check ticker in universe
                    cur_pos = 0
                    cur_pos_real = 0
                    intime = pd.NaT
                    inpriceorg = np.nan
                    inpriceadj = np.nan
                    extime = pd.NaT
                    expriceorg = np.nan
                    expriceadj = np.nan
                    incontract = 'N/A'            
                    excontract = 'N/A'
                    shares = 0
                    pnl = 0                    
                    
                elif longin.iloc[i]:            
                    cur_pos = 1
                    cur_pos_real = 1
                    intime = cur_date
                    inpriceorg = clsorg.iloc[i]
                    inpriceadj = clsadj.iloc[i]                    
                    extime = pd.Timestamp('20991231')
                    expriceorg = np.nan
                    expriceadj = np.nan
                    incontract = prod_data['contract'].iloc[i]
                    excontract = 'N/A'
                    shares = round(cap / clsorg.iloc[i]/mult * sharesadj)                    
                    pnl = -inpriceorg * shares * mult * feetotal * cur_pos
                    
                                        
                elif shortin.iloc[i]:
                    cur_pos = -1
                    cur_pos_real = -1
                    intime = cur_date
                    inpriceorg = clsorg.iloc[i]
                    inpriceadj = clsadj.iloc[i]
                    extime = pd.Timestamp('20991231')
                    expriceorg = np.nan
                    expriceadj = np.nan
                    incontract = prod_data['contract'].iloc[i]
                    excontract = 'N/A'
                    shares = round(cap / clsorg.iloc[i]/mult * sharesadj)
                    pnl = -inpriceorg * shares * mult * feetotal * (-cur_pos)
                                        
                else:
                    cur_pos = 0
                    intime = pd.NaT
                    inpriceorg = np.nan
                    inpriceadj = np.nan
                    extime = pd.NaT
                    expriceorg = np.nan
                    expriceadj = np.nan
                    incontract = 'N/A'            
                    excontract = 'N/A'
                    shares = 0
                    pnl = 0
                    
                poslist.append(cur_pos)
                poslist2.append(cur_pos_real)
                hdslist.append(hds)
                
                intimelist.append(intime)
                inpriceorglist.append(inpriceorg)
                inpriceadjlist.append(inpriceadj)
                incontractlist.append(incontract)
                
                extimelist.append(extime)
                expriceorglist.append(expriceorg)
                expriceadjlist.append(expriceadj)
                excontractlist.append(excontract)
    
                curpriceorglist.append(curpriceorg)
                curpriceadjlist.append(curpriceadj)
                curcontractlist.append(curcontract)
                
                shareslist.append(shares)
                sharesadjlist.append(sharesadj)
                dailypnllist.append(pnl)
                    
            elif cur_pos > 0:
                pnl = (clsadj.iloc[i] - clsadj.iloc[i-1])*shares*mult*cur_pos
                hds = hds + 1
                if turtlelongout.iloc[i]:
                    cur_pos = 0
                    cur_pos_real = 0
                    extime = cur_date
                    expriceorg = clsorg.iloc[i]
                    expriceadj = clsadj.iloc[i]
                    excontract = prod_data['contract'].iloc[i]            
                    pnl = pnl - expriceorg * shares * mult * feetotal
                    shares = 0                    
                    
                    
                elif dailyretlongout.iloc[i] | stdout.iloc[i]:
                    #cur_pos = 1e-8
                    cur_pos = 0
                    cur_pos_real = 0
                    
                    extime = cur_date
                    expriceorg = clsorg.iloc[i]
                    expriceadj = clsadj.iloc[i]
                    excontract = prod_data['contract'].iloc[i]            
                    pnl = pnl - expriceorg * shares * mult * feetotal
                    shares = 0                    
                    
                    
                else:
                    pass
            
                poslist.append(cur_pos)
                poslist2.append(cur_pos_real)
                hdslist.append(hds)
                
                intimelist.append(intime)
                inpriceorglist.append(inpriceorg)
                inpriceadjlist.append(inpriceadj)
                incontractlist.append(incontract)
                
                extimelist.append(extime)
                expriceorglist.append(expriceorg)
                expriceadjlist.append(expriceadj)
                excontractlist.append(excontract)
    
                curpriceorglist.append(curpriceorg)
                curpriceadjlist.append(curpriceadj)
                curcontractlist.append(curcontract)
                
                shareslist.append(shares)
                sharesadjlist.append(sharesadj)
                dailypnllist.append(pnl)
    
                    
            elif cur_pos < 0:
                pnl = (clsadj.iloc[i] - clsadj.iloc[i-1]) * shares * mult * cur_pos
                hds = hds + 1
                if turtleshortout.iloc[i]:
                    cur_pos = 0
                    cur_pos_real = 0
                    extime = cur_date
                    expriceorg = clsorg.iloc[i]
                    expriceadj = clsadj.iloc[i]
                    excontract = prod_data['contract'].iloc[i]            
                    pnl = pnl - expriceorg * shares * mult * feetotal
                    shares = 0
                    
                    
                elif dailyretshortout.iloc[i] | stdout.iloc[i]:
                    #cur_pos = -1e-8
                    cur_pos = 0
                    cur_pos_real = 0
                    
                    extime = cur_date
                    expriceorg = clsorg.iloc[i]
                    expriceadj = clsadj.iloc[i]
                    excontract = prod_data['contract'].iloc[i]            
                    pnl = pnl - expriceorg * shares * mult * feetotal
                    shares = 0
                    
                
                else:
                    pass
                
                poslist.append(cur_pos)
                poslist2.append(cur_pos_real)
                hdslist.append(hds)
                
                intimelist.append(intime)
                inpriceorglist.append(inpriceorg)
                inpriceadjlist.append(inpriceadj)
                incontractlist.append(incontract)
                
                extimelist.append(extime)
                expriceorglist.append(expriceorg)
                expriceadjlist.append(expriceadj)
                excontractlist.append(excontract)
    
                curpriceorglist.append(curpriceorg)
                curpriceadjlist.append(curpriceadj)
                curcontractlist.append(curcontract)
                
                shareslist.append(shares)
                sharesadjlist.append(sharesadj)
                dailypnllist.append(pnl)
                
            else:
                raise ValueError("something wrong with position!")
        df = pd.DataFrame.from_dict({'pos':poslist, 'pos2':poslist2,'hds':hdslist,
                                     'intime':intimelist,'inpriceorg':inpriceorglist,'inpriceadj':inpriceadjlist,'incontract':incontractlist,
                                     'extime':extimelist,'expriceorg':expriceorglist,'expriceadj':expriceadjlist,'excontract':excontractlist,
                                     'curpriceorg':curpriceorglist,'curpriceadj':curpriceadjlist,'curcontract':curcontractlist,
                                     'shares':shareslist,'sharesadj':sharesadjlist,'dailypnl':dailypnllist})
        df['dailyret'] = df['dailypnl'] / cap
        df.index = prod_data.index
        df.index.name = 'dt'
        sigin = longin.astype(int) - shortin.astype(int)
        return df,sigin
       
    def backtest(self, tickerlist, use_univ = True):
        dflist = []
        siginlist = []
        for ticker in tickerlist:
            df,sigin = self.singlebacktest(ticker, use_univ = use_univ)
            df['Ticker'] = ticker
            df = df.reset_index()
            dflist.append(df)
            sigin.name = 'sig'
            sigin.index.name = 'dt'
            sigin = sigin.to_frame()
            sigin['Ticker'] = ticker
            sigin = sigin.reset_index()
            siginlist.append(sigin)
        daily_df = pd.concat(dflist,axis=0).set_index(['dt','Ticker']).sort_index()
        pertrade_df = self.get_trade_df(daily_df)
        sigin_df = pd.concat(siginlist,axis=0)        
        sigin_df = sigin_df.set_index(['dt','Ticker']).sort_index()
        return daily_df, pertrade_df,sigin_df
            
    def get_trade_parameters_ticker(self, set_date, ticker, pos = 0):
        #set_date = '201241228'
        #ticker = 'AU.SHF'
        #pos = 0
        ## prepare data, past 100 days for use
        
        trade_date = dt.get_trading_day_offset(set_date,0)[0]        
        pre_date = dt.get_trading_day_offset(trade_date, -100)[0]
            
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
        rtlist = rt.iloc[:19].tolist()
        
        tr_daily = pd.concat([abs(prod_data['high'] - prod_data['low']),abs(prod_data['high']-prod_data['pre_close']),
                              abs(prod_data['low']-prod_data['pre_close'])],axis=1).max(axis=1)
        tr_daily = tr_daily.sort_index(ascending=False)
        trlist = tr_daily.iloc[:19].tolist()            
        
        clsorg = prod_data['close'].loc[trade_date]
        
        if (len(pricelist) < 59) | (len(rtlist) < 19):
            price_longin_down = np.nan
            price_longin_up = np.nan
            price_shortin_down = np.nan
            price_shortin_up = np.nan
            price_longout_down = np.nan
            price_longout_up = np.nan
            price_shortout_down = np.nan
            price_shortout_up = np.nan
            contract_cur = 'N/A'
            print('wrong length of price or ret!')
        
        else:
            data_use = self.data_all[self.data_all['prod_id'] == ticker]
            #data_use = data_use[data_use['expiration_days'] > 20]
            # cur date
            data_ticker_cur = data_use.loc[trade_date]
            data_ticker_cur1 = data_ticker_cur[data_ticker_cur['expiration_days'] > 20]
            
            idx = data_ticker_cur1['oi'].argmax()
            contract_cur = data_ticker_cur1.index[idx]  # predict next day contract

            # pre date            
#            data_ticker_pre = data_use.loc[trade_date_1]
#            idx = data_ticker_pre['oi'].argmax()
#            contract_pre = data_ticker_pre.index[idx]

            contract_pre = self.data_main.loc[(trade_date, ticker)]['contract'] # current day contract
            #cls_pre = self.data.loc[(trade_date, ticker)]['close']   # current main contract close price

            clsorg0 = data_ticker_cur.loc[(contract_cur,'close')]
            cls_pre = data_ticker_cur.loc[(contract_pre,'close')]
                                    
            gap0 = prod_data.loc[trade_date, 'gap'] + clsorg0 - cls_pre
            
            
            ## set parameters
            #std_in_thd = para_dict['std_in_dict'][ticker]
            #std_out_thd = para_dict['std_out_dict'][ticker]
            std_in_thd = 1
            std_out_thd = 1
                        
            daily_ret_out = para_dict['daily_ret_out']
            lw = para_dict['lw']
            sw = para_dict['sw']

            ####################################################################################
            # 1. Postion is 0, find the long parm
            # subject to ma condition

            if pos == 0:
                
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
                    price_longin_turtle = max(pricelist[:lw]) + gap0
                    price_shortin_turtle = min(pricelist[:lw]) + gap0
                    
                    # calc long in price    
                    if price_in_up_std <= price_longin_turtle:
                        price_longin_down = np.nan
                        price_longin_up = np.nan
                    elif (price_in_down_std <= price_longin_turtle):
                        price_longin_down = price_longin_turtle
                        price_longin_up = price_in_up_std
                    else:
                        price_longin_down = price_in_down_std
                        price_longin_up = price_in_up_std
                    
                    # calc short in price    
                    if price_shortin_turtle <= price_in_down_std:
                        price_shortin_down = np.nan
                        price_shortin_up = np.nan
                    elif (price_shortin_turtle < price_in_up_std):
                        price_shortin_down = price_in_down_std
                        price_shortin_up = price_shortin_turtle
                    else:
                        price_shortin_down = price_in_down_std
                        price_shortin_up = price_in_up_std
                
                price_longout_down = np.nan
                price_longout_up = np.nan
                price_shortout_down = np.nan
                price_shortout_up = np.nan   
                
            elif pos == 1:    
                ########################################################################
                # 3. Pos is 1, find the longout parm
                # xH = clsadj.rolling(sw,min_periods = int(sw/2)).max().shift(1)
                # xL = clsadj.rolling(sw,min_periods = int(sw/2)).min().shift(1)
                #(1) turtle longout: turtlelongout = (clsadj < xL)

                price_longout_turtle = min(pricelist[:sw]) + gap0 # turtle out
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
                # 3. Pos is -1, find the shortout parm
                # xH = clsadj.rolling(sw,min_periods = int(sw/2)).max().shift(1)
                # xL = clsadj.rolling(sw,min_periods = int(sw/2)).min().shift(1)
                #(1) turtle longout: turtlelongout = (clsadj > xH)

                price_shortout_turtle = max(pricelist[:sw]) + gap0 # turtle out
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
            
        # action: 
        #longin: price_longin_down < price < price_longin_up
        #shortin: price_shortin_down < price < price_shortin_up
        #longout: (price < price_longout_down) or (price > price_longout_up)
        #shortin: (price < price_shortout_down) or (price > price_shortout_up)

        action_parm = {'maincontract':contract_cur,'longin_down':price_longin_down,'longin_up':price_longin_up,'shortin_down':price_shortin_down,'shortin_up':price_shortin_up,
                      'longout_down':price_longout_down,'longout_up':price_longout_up,'shortout_down':price_shortout_down,'shortout_up':price_shortout_up,
                      'rtlist':str(rtlist),'trlist':str(trlist),'cls_main_org':clsorg}
        action_df = pd.DataFrame.from_dict(action_parm,orient = 'index')
        action_df.columns = [ticker]
        action_df = action_df.T
        action_df.index.name = 'Ticker'
        return action_df
    
    def get_trade_parameters(self, date, pos_df, omit_dce = True):        
        para_df_list = []
        cols_select = ['pos','hds','intime','inpriceorg','inpriceadj','incontract','curpriceorg','curpriceadj','curcontract','shares']
        data_all = self.data_all        
        amt_max = data_all.groupby(['dt','prod_id'])['amount'].max()
        univ = amt_max[amt_max > 1e6]
        univlist = univ.loc[pd.Timestamp(date)].index
        
        trade_date = dt.get_trading_day_offset(date,0)[0]        
        pre_date = dt.get_trading_day_offset(date, -100)[0]
        data_slice = self.data_main.loc[pre_date:trade_date]        
        for ticker in pos_df.index:
            prod_data = data_slice.xs(ticker,level=1)
            price_len = len(prod_data) 
            if price_len < 59:
                continue
            if omit_dce & (ticker[-3:] in ['DCE','CFE']):
                continue
                
            pos = pos_df.loc[ticker,'pos']
            if ((pos == 0)&((ticker not in univlist) | (self.para_dict['std_in_dict'][ticker] == 0))) | ((abs(pos) > 0) & (abs(pos) < 0.5)):
                continue
            hold_df = pos_df.loc[[ticker]]
            hold_df = hold_df[cols_select]
            action_df = self.get_trade_parameters_ticker(date, ticker, pos = pos)
            tmp = pd.concat([hold_df,action_df],axis=1)
            # contract to test with is main to trade
            data_all1 = data_all.loc[pd.Timestamp(date)]
            contract = data_all1[(data_all1['prod_id'] == ticker)&(data_all1['expiration_days']>20)].sort_values(by = 'oi',ascending=False).index[:3]
            contract = ','.join(contract)
            tmp['contractlist'] = contract
            if pos == 0:
                tmp['std_thd'] = self.para_dict['std_in_dict'][ticker]
            else:
                tmp['std_thd'] = self.para_dict['std_out_dict'][ticker]            
            para_df_list.append(tmp)
        para_df = pd.concat(para_df_list)
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
        para_df1['shares_holding'] = 0
        para_df1['exchange'] = [i.split('.')[1] for i in para_df1.index]
        para_df1['prod_id'] = [i.split('.')[0] for i in para_df1.index]
        para_df1 = para_df1.sort_values(by = ['exchange','prod_id'])
#        para_df = para_df1[['pos','hds','intime','inpriceorg','curcontract','maincontract','cls_main_org','shares_target',
#                            'longin_down','longin_up','shortin_down','shortin_up','longout_down','longout_up','shortout_down','shortout_up']]
        para_df_fortrade = para_df1[['pos','shares_holding','curcontract','maincontract','contractlist','longin_down','longin_up','shortin_down','shortin_up',\
                                     'longout_down','longout_up','shortout_down','shortout_up','cap','t1','t2','std_thd','multiplier','rtlist','trlist',\
                                     'cls_main_org']]
        
        para_forwind = para_df1[['multiplier','pos','shares_holding','shares_target','hds','intime','inpriceorg','curcontract',
                                 'expiration_days', 'basis_ratio', 'std_20d', 'std_thd',
                                 'longin_down','shortin_up','longout_down','shortout_up']]
                
        para_forwind.index = [i.replace('ZCE','CZC') if i.endswith('ZCE') else i for i in para_forwind.index]
        para_forwind['curcontract'] = para_forwind['curcontract'].apply(lambda x:x.replace('ZCE','CZC') if x.endswith('ZCE') else x)
        para_forwind.index.name = 'Ticker'
        return para_df_fortrade, para_forwind
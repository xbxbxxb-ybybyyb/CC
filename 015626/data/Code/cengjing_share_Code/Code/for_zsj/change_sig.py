# normalize 
def rolling_normalize_quantile(x, p = 1200, winsorize = True):
    up = x.rolling(p,min_periods = int(p/2)).quantile(0.99)
    down = x.rolling(p,min_periods=int(p/2)).quantile(0.01)
    xnorm = ((x-down)/(up-down))*2-1
    if winsorize:
        xnorm[xnorm>1] = 1
        xnorm[xnorm<-1] = -1
    return xnorm

# amt adj
def get_open_amt(ticker = '000906'):
    data = pd.read_pickle('/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/index/indexMinute_'+ticker+'.pkl',compression='gzip')
    amt = data.xs(int(ticker),level=1)[['minute','amt']]
    amt_df = amt.reset_index().set_index(['dt','minute'])['amt'].unstack()
    amt_df = amt_df/1e8
    amt_sum = amt_df.cumsum(axis=1)
    mnew = amt_sum[925]
    mnew = mnew.reset_index()
    mnew['dt'] = mnew['dt'].apply(lambda x:pd.Timestamp(str(x)))
    mnew = mnew.set_index('dt')
    return mnew

def get_amt_adj(start_date,end_date,ticker ='IC.CFE'):
	if ticker == 'IC.CFE':
		open_amt = get_open_amt('000905')
	elif ticker == 'IF.CFE':
		open_amt = get_open_amt('000300')
	else:
		raise ValueError('Wrong ticker!')
	start_date = IO.str_date_parser(start_date)
	end_date = udt.get_trading_day_offset(end_date,1)[0]
	open_amt = open_amt.loc[start_date:end_date]  # for IC, we use zz500
	amt_adj = rolling_normalize_quantile(open_amt,120,winsorize=True)*0.5+1
	amt_adj.columns=['amt_adj']
	return amt_adj

# ret_std adj
def get_ret_std_adj(start_date,end_date,ticker = 'IC.CFE'):	
	start_date = IO.str_date_parser(start_date)
	end_date = udt.get_trading_day_offset(end_date,1)[0]
	minute_data = IO.read_data([start_date,end_date],alt = 
								'/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_STOCK_INDEX_SPOT_MINUTE.h5')
	minute_data = minute_data.xs(ticker,level=1)
	minute_data['ret'] = minute_data['close_spot']/minute_data['close_spot'].shift(1)-1
	rt = minute_data['ret']
	rt[(rt.index.hour==9)&(rt.index.minute==30)]=0
	rt_std = rt.rolling(240*2,min_periods=240).std()
	rt_std_adj = rolling_normalize_quantile(rt_std,240*120,winsorize=True)*0.5+1
	rt_std_adj.name='rt_std_adj'
	rt_std_adj = rt_std_adj.to_frame()
	return rt_std_adj
# equal weight of the two

def get_sig_adj(start_date, end_date, ticker='IC.CFE'):
    start_date = IO.str_date_parser(start_date)
    end_date = IO.str_date_parser(end_date)
    start_date_prev = udt.get_trading_day_offset(start_date, -200)[0]
    end_date = udt.get_trading_day_offset(end_date, 1)[0]
    amt_adj = get_amt_adj(start_date_prev,end_date,ticker=ticker)
    rt_std_adj = get_ret_std_adj(start_date_prev,end_date,ticker=ticker)
    sig_adj = pd.concat([amt_adj,rt_std_adj],axis=1).sort_index()
    sig_adj['amt_adj']=sig_adj['amt_adj'].fillna(method='pad')
    sig_adj= sig_adj[sig_adj.index.hour!=0]
    adjcom = sig_adj.mean(axis=1)
    adjcom.name = 'sig_adj'
    return adjcom.loc[start_date:end_date]

# final result adjustment
def change_sig(path, sdate = 20150101, edate = 20201204, change_ticker = 'IC.CFE'):
    sigorg = pd.read_hdf(path)*2-1
    sigorg.index.name='dt'
    adjcom = get_sig_adj(sdate,edate,ticker=change_ticker)
    sig_res = sigorg*adjcom
    sig_res.name = 'sig_res'
    sig_res = sig_res.to_frame()
    return sig_res
with open('/dfs/user/015626/JupyterNotebooks/utils/imports.txt', 'r') as file:
	code = file.read()
	exec(code)

class Pos:
	def __init__(self, open_time=None, open_num = None, open_px = None, open_px_badj=None, open_atr=None, open_atr_rank=None, in_bd_high=0, in_bd_low=None, 
				 open_contract = None, close_time=None, close_num = None, close_px = None, close_px_badj=None, close_atr = None, close_atr_rank = None, 
				 out_bd_high = None, out_bd_low = None, close_contract = None):
		self.open_time = open_time
		self.open_num = open_num
		self.open_px = open_px
		self.open_px_badj = open_px_badj
		self.open_atr = open_atr
		self.open_atr_rank = open_atr_rank
		self.in_bd_high = in_bd_high
		self.in_bd_low = in_bd_low
		self.open_contract = open_contract
		self.close_time = close_time
		self.close_num = close_num
		self.close_px = close_px
		self.close_px_badj = close_px_badj
		self.close_atr = close_atr
		self.close_atr_rank = close_atr_rank
		self.out_bd_high = out_bd_high
		self.out_bd_low = out_bd_low
		self.close_contract = close_contract

def strategy_evaluate(_trade, _pnl):
	trade = _trade.copy()
	pnl = _pnl.copy().reset_index()
	trade['holding_time'] = trade.apply(lambda x:len(udt.get_trading_date_range(x.open_time, x.close_time)) - 1, axis = 1)
	trade['dt'] = trade['open_time']
	trade['date'] = trade['dt'].apply(lambda x: x.date())
	trade['pos'] = trade['open_num']
	# ===新建一个dataframe保存回测指标
	results = pd.DataFrame()

	# ===计算累积净值
	pnl['equity_curve'] = pnl.change.cumsum()+1
	results.loc[0, '累积净值'] = round(pnl['equity_curve'].iloc[-1], 5)

	# 计算夏普比率
	pnl['date'] = pnl['dt'].apply(lambda x: x.date())
	sharpedailyreturn = pnl.groupby('date')['change'].sum().to_frame()
	tradedays = len(sharpedailyreturn)
	sharpe_ratio = round(sharpedailyreturn['change'].mean() / sharpedailyreturn['change'].std() * np.sqrt(252), 3)
	results.loc[0, '夏普比率'] = sharpe_ratio

	# ===计算年化收益
	annual_return = (pnl['equity_curve'].iloc[-1] / pnl['equity_curve'].iloc[0] - 1) * (
			'365 days 00:00:00' / (pnl['dt'].iloc[-1] - pnl['dt'].iloc[0]))

	results.loc[0, '年化收益'] = format(round(annual_return, 3), '.2%')

	sharpedailyreturn['equity_curve'] = sharpedailyreturn['change'].cumsum()
	sharpedailyreturn = sharpedailyreturn.reset_index()
	# ===计算最大回撤
	# 计算当日之前的资金曲线的最高点
	sharpedailyreturn['max2here'] = sharpedailyreturn['equity_curve'].expanding().max()
	# 计算到历史最高值到当日的跌幅，drowdwon
	sharpedailyreturn['dd2here'] = sharpedailyreturn['equity_curve'] - sharpedailyreturn['max2here']
	# 计算最大回撤，以及最大回撤结束时间
	end_date, max_draw_down = tuple(sharpedailyreturn.sort_values(by=['dd2here']).iloc[0][['date', 'dd2here']])
	# 计算最大回撤开始时间
	start_date = sharpedailyreturn[sharpedailyreturn['date'] <= end_date].sort_values(by='equity_curve', ascending=False).iloc[0][
		'date']
	# 将无关的变量删除
	sharpedailyreturn.drop(['max2here', 'dd2here'], axis=1, inplace=True)
	sharpedailyreturn = sharpedailyreturn.set_index('date')
	results.loc[0, '最大回撤'] = format(max_draw_down, '.2%')
	results.loc[0, '最大回撤开始时间'] = str(start_date)
	results.loc[0, '最大回撤结束时间'] = str(end_date)
	

	# ===年化收益/回撤比
	results.loc[0, '年化收益/回撤比'] = round(abs(annual_return / max_draw_down), 2)
	
	# ===统计每笔交易
	results.loc[0, '总交易笔数'] = len(trade)  # 交易笔数
	results.loc[0, '最大每天交易笔数'] = trade.groupby('date')['open_time'].count().max()
	results.loc[0, '亏损笔数'] = len(trade.loc[trade['change'] <= 0])  # 亏损笔数
	results.loc[0, '盈利笔数'] = len(trade.loc[trade['change'] > 0])  # 盈利笔数
	results.loc[0, '胜率'] = format(results.loc[0, '盈利笔数'] / len(trade), '.2%')  # 胜率
	
	longtrade = trade[trade['pos'] == 1]
	shorttrade = trade[trade['pos'] == -1]
	results.loc[0, '做多笔数'] = len(longtrade)  
	if len(longtrade)  > 0:
		results.loc[0, '做多胜率'] = format(len(longtrade[longtrade.change > 0]) / len(longtrade), '.2%')  # 胜率
	else:
		results.loc[0, '做多胜率'] = np.nan
	results.loc[0, '做空笔数'] = len(shorttrade)
	if len(shorttrade) > 0:
		results.loc[0, '做空胜率'] = format(len(shorttrade[shorttrade.change > 0]) / len(shorttrade), '.2%')  # 胜率
	else:
		results.loc[0, '做空胜率'] = np.nan
	results.loc[0, '每笔交易平均盈亏'] = format(trade['change'].mean(), '.4%')  # 每笔交易平均盈亏
	results.loc[0, '盈亏收益比'] = round(trade.loc[trade['change'] > 0]['change'].mean() / \
									trade.loc[trade['change'] < 0][
										'change'].mean() * (-1), 2)  # 盈亏比

	results.loc[0, '单笔最大盈利'] = format(trade['change'].max(), '.2%')  # 单笔最大盈利
	results.loc[0, '单笔最大亏损'] = format(trade['change'].min(), '.2%')  # 单笔最大亏损

	# ===统计持仓时间
	trade['持仓时间'] = trade['holding_time']
	max_minutes = trade['持仓时间'].max()
	results.loc[0, '单笔最长持有时间'] = str(int(max_minutes)) + ' bar'  # 单笔最长持有时间

	min_minutes = trade['持仓时间'].min()
	results.loc[0, '单笔最短持有时间'] = str(int(min_minutes)) + ' bar'  # 单笔最短持有时间

	mean_minutes = trade['持仓时间'].mean()
	results.loc[0, '平均持仓周期'] = str(round(mean_minutes, 1)) + ' bar'  # 平均持仓周期

	if len(longtrade) > 0:
		results.loc[0, '做多收益'] = format(longtrade.change.sum(), '.4%')
		results.loc[0, '做多盈亏比'] = round(longtrade.loc[longtrade['change'] > 0]['change'].mean() / longtrade.loc[longtrade['change'] < 0]['change'].mean() * (-1), 2)  
	else:
		results.loc[0, '做多收益'] = np.nan
		results.loc[0, '做多盈亏比'] = np.nan
	if len(shorttrade) > 0:
		results.loc[0, '做空收益'] = format(shorttrade.change.sum(), '.4%')
		results.loc[0, '做空盈亏比'] = round(shorttrade.loc[shorttrade['change'] > 0]['change'].mean() / shorttrade.loc[shorttrade['change'] < 0]['change'].mean() * (-1), 2)  
	else:
		results.loc[0, '做空收益'] = np.nan
		results.loc[0, '做空盈亏比'] = np.nan

	results = results.T
	results.columns = ['num']
	return results

def back_test(ticker_list = ['AU.SHF', 'RB.SHF'],

			in_break_days = 32,
			in_mean_list = [5, 10, 20, 30, 60], # 随便传入长度大于等于2的list即可，元素从小到大排列

			out_break_days = 14,
			atr_period = 14,
			atr_rank_maxt = 0.3,
			atr_rank_mint = -0.8,

			stop_loss_atr_ratio = -1.5,
			stop_profit_atr_ratio = 1.5,
			stop_profit_atr_rankt = 0.5,

			day_ret_t = -0.05,

			signal_kind = 'break', # break表示突破信号，其余字符串（建议average）表示均线
			deal_price_col = 'final5_twap', # final5_twap   close
			start_date = 20160101,
			end_date = 20230101):
	finaldf = []
	final_pnldf = []

	for ticker in ticker_list:
		df = IO.read_data([start_date, end_date], universe = ticker, alt = '/dfs/group/800466/warehouse/prod/MD/CHINA_COMMODITY/DAILY/MD_MAIN_CHINA_COMMODITY_DAILY2.h5')
		if len(df) < 120:
			continue
		df['final5_twap'] = df['final5_twap'].fillna(df['close']) 
		df['dealpx'] = df[deal_price_col]
		df['dealpx_backadj'] = df['dealpx'] - df['gap']
		df['close_backadj'] = df['close'] - df['gap']
		df['high_backadj'] = df['high'] - df['gap']
		df['low_backadj'] = df['low'] - df['gap']

		df['tr'] = pd.concat([df['high_backadj'] - df['low_backadj'], abs(df['high_backadj'] - df['close_backadj'].shift()), abs(df['close_backadj'].shift() - df['low_backadj'])], axis = 1).max(axis = 1)  
		df['atr'] = abs(ts_mean(df['tr'], atr_period) / df['close'])
		df['atr_rank'] = ts_rank(df['atr'], 120)

		df['in_bd_high'] = df['close_backadj'].rolling(in_break_days).max().shift()
		df['in_bd_low'] = df['close_backadj'].rolling(in_break_days).min().shift()
		df['out_bd_high'] = df['close_backadj'].rolling(out_break_days).max().shift()
		df['out_bd_low'] = df['close_backadj'].rolling(out_break_days).min().shift()

		columns_list = df.reset_index().columns.tolist()
		contract_idx = columns_list.index('wind_code')
		dt_idx = columns_list.index('dt')
		close_idx = columns_list.index('close')
		close_backadj_idx = columns_list.index('close_backadj')
		dealpx_idx = columns_list.index('dealpx')
		dealpx_backadj_idx = columns_list.index('dealpx_backadj')
		in_bd_high_idx = columns_list.index('in_bd_high')
		in_bd_low_idx = columns_list.index('in_bd_low')
		out_bd_high_idx = columns_list.index('out_bd_high')
		out_bd_low_idx = columns_list.index('out_bd_low')
		atr_rank_idx = columns_list.index('atr_rank')
		atr_idx = columns_list.index('atr')

		max_hold_num = 1
		volume_per_order = 1

		dfv = df.reset_index().values
		close_backadj_list = df['close_backadj'].tolist()
		now_hold_num = 0
		now_hold_time = 0
		finish_list = []

		pnl_dict = {}

		now_pos = None
		for i in range(1, len(dfv)):
			row = dfv[i]
			now_contract = row[contract_idx]
			now_time = row[dt_idx]
			close = row[close_idx]
			close_backadj = row[close_backadj_idx]
			dealpx = row[dealpx_idx]
			dealpx_backadj = row[dealpx_backadj_idx]
			atr_rank = row[atr_rank_idx]
			atr = row[atr_idx]
			in_bd_high = row[in_bd_high_idx]
			in_bd_low = row[in_bd_low_idx]
			out_bd_high = row[out_bd_high_idx]
			out_bd_low = row[out_bd_low_idx]

			if now_hold_num == 0:
				if atr_rank >= atr_rank_mint and atr_rank <= atr_rank_maxt:
					if signal_kind == 'break':
						if close_backadj > in_bd_high:
							now_hold_num = 1
							now_pos = Pos(now_time, now_hold_num, dealpx, dealpx_backadj, atr, atr_rank, in_bd_high, in_bd_low, now_contract)
						elif close_backadj < in_bd_low:
							now_hold_num = -1
							now_pos = Pos(now_time, now_hold_num, dealpx, dealpx_backadj, atr, atr_rank, in_bd_high, in_bd_low, now_contract)
					else:
						if close_backadj > np.nanmean(close_backadj_list[i + 1 - in_mean_list[0] : i + 1]):
							average_flag = True
							for j in range(1, len(in_mean_list)):
								if np.nanmean(close_backadj_list[i + 1 - in_mean_list[j-1] : i + 1]) <= np.nanmean(close_backadj_list[i + 1 - in_mean_list[j] : i + 1]):
									average_flag = False
									break
							if average_flag:
								now_hold_num = 1
								now_pos = Pos(now_time, now_hold_num, dealpx, dealpx_backadj, atr, atr_rank, in_bd_high, in_bd_low, now_contract)
						
						elif close_backadj < np.nanmean(close_backadj_list[i + 1 - in_mean_list[0] : i + 1]):
							average_flag = True
							for j in range(1, len(in_mean_list)):
								if np.nanmean(close_backadj_list[i + 1 - in_mean_list[j-1] : i + 1]) >= np.nanmean(close_backadj_list[i + 1 - in_mean_list[j] : i + 1]):
									average_flag = False
									break
							if average_flag:
								now_hold_num = -1
								now_pos = Pos(now_time, now_hold_num, dealpx, dealpx_backadj, atr, atr_rank, in_bd_high, in_bd_low, now_contract)
					
				pnl_dict[now_time] = (close - dealpx) / dealpx * np.sign(now_hold_num)
			
			elif now_hold_num != 0:
				now_profit = ((close_backadj - now_pos.open_px_badj) / now_pos.open_px) * np.sign(now_hold_num)
				day_ret = (close_backadj - dfv[i-1][close_backadj_idx]) / dfv[i-1][close_idx]
				
				stop_flag = now_profit < (stop_loss_atr_ratio * now_pos.open_atr) or (now_profit > (stop_profit_atr_ratio * now_pos.open_atr) and atr_rank > stop_profit_atr_rankt)
				close_flag = False

				if now_hold_num > 0 and (close_backadj < out_bd_low or day_ret < day_ret_t or stop_flag):
					close_flag = True
				elif now_hold_num < 0 and (close_backadj > out_bd_high or day_ret > day_ret_t * -1 or stop_flag):
					close_flag = True
				elif i == len(dfv) - 1:
					close_flag = True
					
				if close_flag:
					now_pos.close_time = now_time
					now_pos.close_num = now_hold_num
					now_pos.close_px = dealpx
					now_pos.close_px_badj = dealpx_backadj
					now_pos.close_atr = atr
					now_pos.close_atr_rank = atr_rank
					now_pos.out_bd_high = out_bd_high
					now_pos.out_bd_low = out_bd_low
					now_pos.close_contract = now_contract
					pnl_dict[now_time] = ((dealpx_backadj - dfv[i-1][close_backadj_idx]) / close) * np.sign(now_hold_num)
					finish_list.append(now_pos)
					now_hold_num = 0
				else:
					pnl_dict[now_time] = ((close_backadj - dfv[i-1][close_backadj_idx]) / close) * np.sign(now_hold_num)
		
		finishdf = [[ticker, x.open_time, x.open_num, x.open_px, x.open_px_badj, x.open_atr, x.open_atr_rank, x.in_bd_high, x.in_bd_low, x.open_contract, x.close_time, x.close_num, x.close_px, x.close_px_badj, x.close_atr, x.close_atr_rank, x.out_bd_high, x.out_bd_low, x.close_contract] for x in finish_list]
		finishdf = pd.DataFrame(finishdf, columns=['Ticker', 'open_time', 'open_num', 'open_px', 'open_px_badj', 'open_atr', 'open_atr_rank', 'in_bd_high', 'in_bd_low', 'open_contract', 'close_time', 'close_num', 'close_px', 'close_px_badj', 'close_atr', 'close_atr_rank', 'out_bd_high', 'out_bd_low', 'close_contract'])
		finishdf['change'] = ((finishdf['close_px_badj'] - finishdf['open_px_badj']) / finishdf['open_px']) * np.sign(finishdf['open_num'])
		pnl = pd.DataFrame(pnl_dict, index = [ticker]).T
		pnl.index.name = 'dt'

		finaldf.append(finishdf)
		final_pnldf.append(pnl)

	finishdf = pd.concat(finaldf).sort_values(by = ['open_time', 'close_time'])
	pnl = pd.concat(final_pnldf, axis = 1)
	pnl['total'] = pnl.mean(axis = 1)
	pnl['total'].cumsum().plot()

	total_result = strategy_evaluate(finishdf, pnl['total'].to_frame(name = 'change'))
	total_result.columns = ['total']
	rlist = [total_result]
	for ticker in ticker_list:
	    select = finishdf[finishdf['Ticker']  == ticker]
	    if len(select) == 0:
	        print(ticker, 'no trade')
	        continue
	    result = strategy_evaluate(select, pnl[ticker].dropna().to_frame(name = 'change'))
	    result.columns = [ticker]
	    rlist.append(result)
	result = pd.concat(rlist, axis = 1).sort_values(by = ['累积净值'], ascending=False, axis = 1)

	return result, finishdf, pnl
kind_0 = 'IC'
kind_1 = 'IH'
save_path = '/data/user/015626/data/share/LOCAL_DATA/Mobius/style_factor/'
os.makedirs(save_path, exist_ok=True)

spot_data = pd.read_pickle('/dfs/group/800466/warehouse/prod/MD/CHINA_FUTURES/MINUTE/INSAMPLE/SPOT_DATA_insample.pkl')
future_data = pd.read_pickle('/dfs/group/800466/warehouse/prod/MD/CHINA_FUTURES/MINUTE/INSAMPLE/FUTURE_DATA_insample.pkl')

r_0 = future_data['close'].pct_change()[future_data['recent_month_mask']].mean(axis = 1)
r_1 = future_data['close_ih'].pct_change()[future_data['recent_month_mask']].mean(axis = 1)
p_0 = future_data['position'][future_data['recent_month_mask']].mean(axis = 1)
p_1 = future_data['position_ih'][future_data['recent_month_mask']].mean(axis = 1)
factor = ts_corr(r_0, p_0, 30) - ts_corr(p_0, p_1, 30)

factor = factor.to_frame()
factor.columns = ['MinuteRtnInterestCorrDelta']
factor.to_hdf(os.path.join(save_path, 'MinuteRtnInterestCorrDelta.h5'), key = 'h5')

r_0 = spot_data['close_spot'].pct_change()
r_1 = spot_data['close_spot_ih'].pct_change()
factor = ts_skew(r_0 -r_1, 100)

factor = factor.to_frame()
factor.columns = ['MinuteRtnDeltaSkew']
factor.to_hdf(os.path.join(save_path, 'MinuteRtnDeltaSkew.h5'), key = 'h5')

relative_turnover = spot_data['amount_spot'] / spot_data['amount_spot_ih']
rtn_delta = spot_data['close_spot'].pct_change() - spot_data['close_spot_ih'].pct_change()
factor = relative_turnover.rolling(100).corr(rtn_delta)
factor.loc[factor.index.hour > 12] *= -1

factor = factor.to_frame()
factor.columns = ['MinuteRelativeTurnoverRtnDeltaCorr']
factor.to_hdf(os.path.join(save_path, 'MinuteRelativeTurnoverRtnDeltaCorr.h5'), key = 'h5')

price_delta = future_data['close'].pct_change()[future_data['recent_month_mask']].mean(axis = 1) - future_data['close_ih'].pct_change()[future_data['recent_month_mask']].mean(axis = 1)
index_price_delta = spot_data['close_spot'].pct_change() - spot_data['close_spot_ih'].pct_change()
spot_cum_r = (1 + index_price_delta).cumprod()
future_cum_r = (1 + price_delta).cumprod()
factor = spot_cum_r / ts_max(spot_cum_r, 30) - future_cum_r / ts_max(future_cum_r, 30)

factor = factor.to_frame()
factor.columns = ['MinuteSpotFutureRtnDeltaDrawdown']
factor.to_hdf(os.path.join(save_path, 'MinuteSpotFutureRtnDeltaDrawdown.h5'), key = 'h5')

price_delta = future_data['close'].pct_change()[future_data['recent_month_mask']].mean(axis = 1) - future_data['close_ih'].pct_change()[future_data['recent_month_mask']].mean(axis = 1)
index_price_delta = spot_data['close_spot'].pct_change() - spot_data['close_spot_ih'].pct_change()
spot_cum_r = (1 + index_price_delta).cumprod()
future_cum_r = (1 + price_delta).cumprod()
factor = spot_cum_r / ts_min(spot_cum_r, 60) - future_cum_r / ts_min(future_cum_r, 60)

factor = factor.to_frame()
factor.columns = ['MinuteSpotFutureRtnDeltaBounce']
factor.to_hdf(os.path.join(save_path, 'MinuteSpotFutureRtnDeltaBounce.h5'), key = 'h5')
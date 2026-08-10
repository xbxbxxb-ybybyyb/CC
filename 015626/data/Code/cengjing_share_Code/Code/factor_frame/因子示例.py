'''
因子示例，分别包括期货类因子与成分股类因子。其中期货类因子的数据包括，主力期货合约，同期货其他合约，其他期货合约，指数信息。
'''

class MinuteMTM10(FutureFactor):
	'''
	期货类因子
	'''
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Future_Data'] = ['close']
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        close = data['close'].values[-11:]
        close_rtn = close[1:] / close[:-1] - 1
        
        return np.nanmean(close_rtn)


class MinuteMTM10(FutureFactor):
	'''
	期货类因子应用指数数据
	'''
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        close = data['close_000905.SH'].values[-11:]
        close_rtn = close[1:] / close[:-1] - 1
        
        return np.nanmean(close_rtn)

class MinuteICIFCorr(FutureFactor):
	'''
	期货类因子应用多品种数据
	'''
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Other_Variety'] = {'IC':['close'],'IF':['close']}
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        close_ic = data['close_IC'].values[-30:]
        close_if = data['close_IF'].values[-30:]
        
        corr = np.corrcoef(close_ic,close_if)[0,1]
        
        return corr

class MinuteSpotFutureDiffRtn(FutureFactor):
	'''
	期货类因子应用多合约数据
	'''
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Other_Future_Insturment'] = {'02':['close'],'03':['close']}
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        close_02 = data['close_02'].values[-30:]
        close_03 = data['close_03'].values[-30:]
        index_close = data['close_000905.SH'].values[-30:]
        
        close_diff = close_02 - close_03
        spot_future_rtn = close_diff / index_close
        
        return np.nanmean(spot_future_rtn)

class MinuteIndexRtnSkew(FutureFactor):
    '''
    成分股类因子
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close']
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        close = data['close'].values[-31:]
        close_rtn = close[1:] / close[:-1] - 1
        close_skew = stats.skew(close_rtn,axis=1)
        
        return np.nanmean(close_skew)
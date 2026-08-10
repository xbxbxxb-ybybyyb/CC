import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
# ret_sharpe
class fac_38(FactorGenerator):
    def __init__(self):
        required_columns=['close']

        super(fac_38, self).__init__(required_columns=required_columns
                                  )
        

    def rolling_linear_reg(self, x, y, window_size):
        x2=np.power(x,2)
        xy=x*y
        window = np.ones(int(window_size))
        a1=np.convolve(xy, window, 'full')*window_size
        a2=np.convolve(x, window, 'full')*np.convolve(y, window, 'full')
        b1=np.convolve(x2, window, 'full')*window_size
        b2=np.power(np.convolve(x, window, 'full'),2)
        alphas=(a1-a2)/(b1-b2)
        betas=(np.convolve(y, window, 'full')-alphas*np.convolve(x, window, 'full'))/float(window_size)
        alphas=alphas[:-1*(window_size-1)] #numpy array of rolled alpha
        betas=betas[:-1*(window_size-1)] 
        alphas[:window_size-1] = np.nan
        return alphas
    
    def on_bar(self, data, aa, bb):


        close_spot = data['close'].values
        
        ind = list(range(len(close_spot)))

        m_vwap_ind_r = self.rolling_linear_reg(ind, close_spot, aa)
        #factor = pd.Series(data['close_spot_if'].rolling(25, min_periods = 1).skew()).to_frame()
        factor = pd.Series(m_vwap_ind_r).to_frame()
        factor.index = data['close'].index
        factor.columns = [self.__class__.__name__]

        factor = ts_rank(factor, bb * 300)

        return factor

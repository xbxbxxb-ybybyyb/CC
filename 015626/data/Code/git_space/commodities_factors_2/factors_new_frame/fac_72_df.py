from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor



def irr_filter(input_signal, window):
    alpha = 2 / (window + 1)
    b0 = alpha - (alpha ** 2) / 4
    b1 = (alpha ** 2) / 2
    b2 = -(alpha - (3 * alpha ** 2) / 4)
    a1 = -2 * (1 - alpha)
    a2 = (1 - alpha) ** 2
    y = np.zeros_like(input_signal)
    for n in range(len(input_signal)):
        if n == 0:
            y[n] = b0 * input_signal[n]
        elif n == 1:
            y[n] = b0 * input_signal[n] + b1 * input_signal[n-1] - a1 * y[n-1]
        else:
            y[n] = (b0 * input_signal[n] + b1 * input_signal[n-1] + b2 * input_signal[n-2] - a1 * y[n-1] - a2 * y[n-2])
    return y

def rolling_normalize_array(sig, window):
    sig_max = move_max_bk(sig,window,min_count = int(window/2))
    sig_min = move_min_bk(sig,window,min_count = int(window/2))
    sig_roll_norm = (sig - sig_min) / (sig_max - sig_min) * 2 - 1
    return sig_roll_norm

class fac_72_df(FutureFactor):    
    def __init__(self, ticker, freq = 1):
        super().__init__()
        self.factor_name = self.__class__.__name__
        self.days_past = int(freq) * 6 # different product should be different
        self.required_columns = ['close', 'close_secmain']
        self.normalize_size = 1500
        self.normalize_type = 'ts_rank'
        self.ticker = ticker
        self.freq = freq
        self.price_level_5_list = []
        self.price_level_5_secmain_list = []        
    
    def calculate(self, data):                
        coef = int(self.bars_dict[self.ticker]/self.freq)
        N = max(coef * 5, 500)
        cls = data['close'][-N:]        
        pl = rolling_normalize_array(cls, coef * 5)        
        price_level_5 = irr_filter(pl[-15:], 3)[-1]
        self.price_level_5_list.append(price_level_5)
        fac_1 = ts_reg_residual(np.array(self.price_level_5_list[-210:]), 210)[-1]
        

        cls_secmain = data['close_secmain'][-N:]       
        pl_secmain = rolling_normalize_array(cls_secmain, coef * 5)        
        price_level_5_secmain = irr_filter(pl_secmain[-20:], 4)[-1]
        self.price_level_5_secmain_list.append(price_level_5_secmain)
        fac_2 = ts_reg_residual(np.array(self.price_level_5_secmain_list[-150:]), 150)[-1]
        factor = fac_1 + fac_2
        return fac_1

    def pre_calculate(self,data):
        self.price_level_5_list = []
        self.price_level_5_secmain_list = []   
        coef = int(self.bars_dict[self.ticker] / self.freq)
        N = max(coef * 5, 500)
        for i in range(210, -1, -1):
            if i == 0:
                cls = data['close'][-N:]
                cls_secmain = data['close_secmain'][-N:]
                
                
            else:
                cls = data['close'][-(N+i):-i]
                cls_secmain = data['close_secmain'][-(N+i):-i]
            pl = rolling_normalize_array(cls,coef * 5)
            if len(pl) < 3:
                price_level_5 = np.nan
            else:
                price_level_5 = irr_filter(pl[-15:],3)[-1]
            self.price_level_5_list.append(price_level_5)
            pl_secmain = rolling_normalize_array(cls_secmain,coef * 5)
            if len(pl_secmain) < 3:
                price_level_5_secmain = np.nan
            else:
                price_level_5_secmain = irr_filter(pl_secmain[-20:],4)[-1]
            self.price_level_5_secmain_list.append(price_level_5_secmain)
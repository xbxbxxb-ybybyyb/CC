import numpy as np

def ema_1(factor_array1,d,alpha):
    factor_array = np.array(factor_array1)
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    flag = np.isnan(factor_array) | np.isnan(weight)
    flag1 = np.sum(flag, axis=-1)  # 缺失值个数
    flag2 = np.where(flag1 <= int(d / 2), 1, np.nan)
    factor_array[flag] = np.nan
    weight[flag] = np.nan
    factor = np.nansum(factor_array[-d:] * weight) / np.nansum(weight) # truncate_ema_1
    return factor

def ema_span_1(factor_array, d, span):
    return ema_1(factor_array, d = d, alpha=2 / (span + 1))
    
class fac_34_aug_orig_1min_df(FutureFactor):

    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker # 'AG.SHF', 'A.DCE'
        self.freq = freq # 1, 3, 5, 15

        self.days_past = 1 * freq
        self.required_columns = ['close', 'open', 'high', 'low']
        self.normalize_size = 600
        self.normalize_type = 'ts_rank'
        
        self.factor_name = self.__class__.__name__
        # 定义预计算缓存序列，想定义几个就定义几个
        self.t_pcor2_list = []
        self.t_pcor2_10_list = []
    
    def calculate(self, data):
        mean_num = 2
        hh = np.nanmax(data['high'][-mean_num:]) - np.nanmin(data['low'][-mean_num:])
        if abs(hh) < 1e-8:
            hh = np.nan
        temp = -1 * (np.nanmean(data['open'][-mean_num:]) - data['close'][-1]) / hh
        temp = 0 if np.isinf(temp) else temp
        self.t_pcor2_list.append(temp)
        self.t_pcor2_list = self.t_pcor2_list[-10:]
        self.t_pcor2_10_list.append(np.nanmean(self.t_pcor2_list))
        self.t_pcor2_10_list = self.t_pcor2_10_list[-100:]
        return ema_span_1(self.t_pcor2_10_list, 100, 45)

    def pre_calculate(self, data):
        mean_num = 2
        for i in range(120):
            if i == 0:

                hh = np.nanmax(data['high'][-(i + mean_num):]) - np.nanmin(data['low'][-(i + mean_num):])
                if abs(hh) < 1e-8:
                    hh = np.nan
                temp = -1 * (np.nanmean(data['open'][-(i + mean_num):]) - data['close'][-(i+1)]) / hh
            else:

                hh = np.nanmax(data['high'][-(i + mean_num):-i]) - np.nanmin(data['low'][-(i + mean_num):-i])
                if abs(hh) < 1e-8:
                    hh = np.nan
                temp = -1 * (np.nanmean(data['open'][-(i + mean_num):-i]) - data['close'][-(i+1)]) / hh
            temp = 0 if np.isinf(temp) else temp
            self.t_pcor2_list.append(temp)
        self.t_pcor2_list.reverse()
        n = 10
        for i in range(120):
            if i == 0:
                self.t_pcor2_10_list.append(np.nanmean(self.t_pcor2_list[-n:]))
            else:
                self.t_pcor2_10_list.append(np.nanmean(self.t_pcor2_list[-(i+n):-i]))
        self.t_pcor2_10_list.reverse()
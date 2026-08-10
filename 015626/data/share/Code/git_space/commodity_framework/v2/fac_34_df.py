import numpy as np

class fac_34_df(FutureFactor):

    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker # 'AG.SHF', 'A.DCE'
        self.freq = freq # 1, 3, 5, 15

        self.days_past = 1 * freq
        self.required_columns = ['close', 'open', 'high', 'low']
        self.normalize_size = 2 * self.bars_dict[ticker]
        self.normalize_type = 'ts_rank'
        
        self.factor_name = self.__class__.__name__
        # 定义预计算缓存序列，想定义几个就定义几个
        self.t_pcor2_list = []
    
    def calculate(self, data):
        mean_num = 3
        hh = np.nanmax(data['high'][-mean_num:]) - np.nanmin(data['low'][-mean_num:])
        if abs(hh) < 1e-8:
            hh = np.nan
        temp = -1 * (np.nanmean(data['open'][-mean_num:]) - data['close'][-1]) / hh
        temp = 0 if np.isinf(temp) else temp
        self.t_pcor2_list.append(temp)

        t_pcor2_diff_list = np.array(self.t_pcor2_list[1:]) - np.array(self.t_pcor2_list[:-1])
        self.t_pcor2_list = self.t_pcor2_list[-10:]

        _ = np.nanstd(t_pcor2_diff_list[-10:], ddof = 1)
        if abs(_) < 1e-8:
            _ = np.nan
        _2 = np.sqrt(np.nanstd(data['close'][-8:], ddof = 1))
        if abs(_2) < 1e-8:
            _2 = np.nan
        fac = np.nanmean(self.t_pcor2_list) / _ / _2
        
        return fac

    def pre_calculate(self, data):
        mean_num = 3
        for i in range(15):
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
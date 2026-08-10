import os
from utils.help_functions_wsc import read_pickle, save_pickle, pd_writer


class FactorGeneratorXdy:
    __data__ = None
    __ticker__=None
    def __init__(self, factor_name = 'test', lookback_bars = 5000, required_columns = None,
                 savepath = '/data/user/017024/share/overnight/alpha'):
        self.factor_name = factor_name
        self.lookback_bars = lookback_bars
        self.required_columns = required_columns
        self.savepath = savepath

    @classmethod
    def prepare_hot_data(inst, start_date, end_date):
        start_date = str(start_date)
        end_date = str(end_date)
        data_dict = read_pickle('/data/user/015626/data/share/MD/CHINA_FUTURES/daily/overnight/OUTSAMPLE/spot_daily_overnight.pkl')

        for key in data_dict.keys():
             data_dict[key] = data_dict[key].loc[start_date: end_date]

        inst.__data__ = data_dict


    def slicer(self):
        return {col:self.__data__[col].copy() for col in self.required_columns}

    def __callback__(self, start_date, end_date):
        data = self.slicer()
        savepath = self.savepath
        if not os.path.exists(savepath):
            os.makedirs(savepath)
        factor = self.on_bar(data)
        start_date = str(start_date)
        end_date = str(end_date)
        factor = factor.loc[start_date:end_date]
        pd_writer(factor, savepath)
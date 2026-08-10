from future_factor import FutureFactor


class MinuteStyleRtnDiff(FutureFactor):
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Index_Id'] = {'000016.SH': ['close'], '000300.SH': ['close'], '000905.SH': ['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 60
        close_50 = data['close_000016.SH'].values
        close_300 = data['close_000300.SH'].values
        close_500 = data['close_000905.SH'].values
        rtn_50 = close_50[-1] / close_50[-lb - 1] - 1
        rtn_300 = close_300[-1] / close_300[-lb - 1] - 1
        rtn_500 = close_500[-1] / close_500[-lb - 1] - 1
        rtn_min, rtn_max = min(rtn_50, rtn_300, rtn_500), max(rtn_50, rtn_300, rtn_500)
        f = (rtn_500 - rtn_min) / (rtn_max - rtn_min)
        return f

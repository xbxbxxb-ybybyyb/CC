from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
class MinMax(BaseFactor):
    factor_type = "DAY"
    reform_window = 20
    lag = 0
    depend_data = ["FactorData.Basic_factor.close_minute"]
    def calc_single(self, database):
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        ret = MinuteClose.pct_change(periods=1)
        return -ret.max()-ret.min()
    def reform(self, temp_result):
        temp_result = Util.rolling_process(temp_result,'mean',10,1)
        temp_result = Util.rolling_process(temp_result, 'min', 10, 1)
        return temp_result


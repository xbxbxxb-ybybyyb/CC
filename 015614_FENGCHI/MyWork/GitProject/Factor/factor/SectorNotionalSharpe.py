from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import time

class SectorNotionalSharpe(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.amt","FactorData.Basic_factor.sw_indcode1"]
    lag = 0
    reform_window = 5
    def calc_single(self, database):
        t1 = time.time()

        data = database.depend_data['FactorData.Basic_factor.sw_indcode1'].iloc[-1].to_frame('industry')
        data['amt'] = database.depend_data['FactorData.Basic_factor.amt'].iloc[-1]
        data['result'] = data.groupby(by='industry')['amt'].apply(lambda x:x-x.mean())
        return -data['result']
    def reform(self, temp_result):
        return Util.rolling_process(temp_result, 'mean', self.reform_window, 1)/Util.rolling_process(temp_result, 'std', self.reform_window, 1)







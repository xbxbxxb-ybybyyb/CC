# coding: utf-8
# Author：fengchi863
# Date ：2021/2/23 11:17

from ShortTermTrading.conf.path_conf import root_path
from xquant.factordata import FactorData
fd = FactorData()

class ProfitReportStrategy:
    def __init__(self):
        fd = FactorData()
        self.fd = fd
        return

    def get_date_predict_table(self):
        date_predict = self.fd.get_factor_value('WIND_AShareIssuingDatePredict',
                                           report_period=['>=20140101', '<=20201231'])
        col = ['S_INFO_WINDCODE', 'REPORT_PERIOD', 'S_STM_PREDICT_ISSUINGDATE', 'S_STM_ACTUAL_ISSUINGDATE']
        date_predict = date_predict[col]
        date_predict = date_predict[date_predict['REPORT_PERIOD'].astype(int) % 10000 == 1231]
        return date_predict

    def get_yugao_table(self):
        yugao_df = fd.get_factor_value('WIND_AShareProfitNotice',
                                       S_PROFITNOTICE_PERIOD=['>=20140101', '<=20201231'])
        col = ['S_INFO_WINDCODE', 'S_PROFITNOTICE_DATE', 'S_PROFITNOTICE_PERIOD', 'S_PROFITNOTICE_STYLE',
               'S_PROFITNOTICE_SIGNCHANGE', 'S_PROFITNOTICE_FIRSTANNDATE']
        yugao_df = yugao_df[col]
        yugao_df = yugao_df[yugao_df['S_PROFITNOTICE_PERIOD'].astype(int) % 10000 == 1231]
        return yugao_df

    def get_kuaibao_table(self):
        kuaibao_df = fd.get_factor_value('WIND_AShareProfitExpress',
                                         report_period=['>=20140101', '<=20201231'])
        col = ['S_INFO_WINDCODE', 'REPORT_PERIOD', 'ANN_DT']
        kuaibao_df = kuaibao_df[col]
        kuaibao_df = kuaibao_df[kuaibao_df['REPORT_PERIOD'].astype(int) % 10000 == 1231]
        return kuaibao_df
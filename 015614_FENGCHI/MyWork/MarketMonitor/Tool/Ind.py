# coding: utf-8
# Author：fengchi863
# Date ：2021/11/15 18:09

from ShortTermTrading.dataApi import indName, getData
from FaaMonitor.Util.DtUtil import DtUtil


class Ind:
    def __init__(self):
        yes_date = DtUtil.get_yesterday_date()
        ind1 = getData.get_daily_1factor('SW1', date_list=[yes_date]).iloc[0].to_dict()
        ind2 = getData.get_daily_1factor('SW2', date_list=[yes_date]).iloc[0].to_dict()
        ind3 = getData.get_daily_1factor('SW3', date_list=[yes_date]).iloc[0].to_dict()

        self.ind1 = ind1
        self.ind2 = ind2
        self.ind3 = ind3
        # fd = FactorData()
        # sw1 = fd.hind('SW', 1)[['industry_name', 'industry_code']].set_index('industry_code').to_dict()['industry_name']
        # sw_inds = fd.hind('SW', 2)
        # sw_inds['industry_code'] = sw_inds['industry_code'].map(lambda x: x + '0' * 10)
        # sw_inds['一级行业'] = sw_inds['industry_code'].map(lambda x: sw1[x[:4]])
        # index_sectors = fd.get_factor_value('WIND_IndexContrasSector')[['S_INFO_INDEXCODE']]
        # sw_index_sector = pd.merge(sw_inds, index_sectors, how='left', left_on='industry_code', right_on='S_INFO_INDUSTRYCODE')

    def get_sw1_name(self, stk_id):
        if stk_id in self.ind1.keys():
            return indName.sw_level1[self.ind1[stk_id]]
        else:
            return stk_id

    def get_sw2_name(self, stk_id):
        if stk_id in self.ind1.keys():
            return indName.sw_level2[self.ind2[stk_id]]
        else:
            return stk_id

    def get_sw3_name(self, stk_id):
        if stk_id in self.ind1.keys():
            return indName.sw_level3[self.ind3[stk_id]]
        else:
            return stk_id

Ind = Ind()
# if __name__ == '__main__':
#     ind = Ind()
#     ind.get_sw1_name(601688)
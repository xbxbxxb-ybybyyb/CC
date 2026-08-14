# coding: utf-8
# Author：fengchi863
# Date ：2020/12/16 15:03

from ShortTermTrading.dataApi import getData
from ShortTermTrading.dataApi import tradeDate
from ShortTermTrading.ConceptApi.ConceptApi import get_1factor_concept, get_basic_values, Get_Concept_Code

start_date = 20200101
end_date = 20201201
shift_start_date = tradeDate.get_pre_trade_date(start_date, offset=30)
date_list = tradeDate.get_date_range(shift_start_date, end_date)

basic_values = get_basic_values('Active_Concept')
concept = Get_Concept_Code()
concept_dict = concept.to_dict()['S_INFO_NAME']
daily_hot_concept = basic_values.rename(columns=concept_dict)
concept_code_list = list(concept_dict.keys())
concept_list = daily_hot_concept.columns.tolist() # 中文所有概念板块列表

# concept_pctchg = get_1factor_concept(factor='涨跌幅', concept=concept_code_list, start_date=shift_start_date, end_date=end_date)
# concept_pctchg.to_pickle('/data/group/800319/fengchi/pattern_test/temp_data/minute_concept_pctchg_%d_%d.pkl' % (shift_start_date, end_date))
#
# tmp = get_1factor_concept(factor='板块分钟成交额', concept=concept_code_list, start_date=shift_start_date, end_date=end_date)
# tmp.to_pickle('/data/group/800319/fengchi/pattern_test/temp_data/minute_concept_amt_%d_%d.pkl' % (shift_start_date, end_date))


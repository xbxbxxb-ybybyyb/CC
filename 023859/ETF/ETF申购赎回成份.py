import pandas as pd
from xquant.thirdpartydata.factordata import FactorData
s = FactorData()

ChinaETFPchRedmMembers = s.get_factor_value('WING_ChinaETFPchRedmMembers', S_INFO_WINDCODE=etf_list, TRADE_DT=['>='+str(start_date), '<='+str(end_date)])

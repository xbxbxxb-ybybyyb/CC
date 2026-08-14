# coding: utf-8
# Author：fengchi863
# Date ：2020/3/30 15:52

from util import *
from dataApi.interdayTest import FactorBackTest

'''
因子逻辑：
根据前N日行业内涨跌幅来进行定义
N取了1、2、3、4、5、10
'''
root_path = '/data/group/800319/junkData/temp_factor_by_fc/'

start_date = 20170101
end_date = 20191231
ref_days = 10
N = 5 # 前N日涨跌幅
index_code = 'ZZ500'

close = get_daily_1factor('close_badj')
close_pct_chg = close.pct_change(N).shift(1).loc[start_date:end_date]

pct_chg_by_industry = pd.DataFrame(index=close_pct_chg.index)
for sw1_code in sw1_dict.keys():
    pct_chg_by_industry = pd.concat([pct_chg_by_industry, close_pct_chg[sw1_dict[sw1_code]].rank(pct=True)], axis=1)

print('开始进行回测')
factor = pct_chg_by_industry
fbt = FactorBackTest(group=10)
fbt.load_factor(factor)
fbt.calc_group_ret()
print(fbt.calc_ic().mean())
fbt.report(factor=factor, address=root_path, file_name='junk_factor')

'''
N=1: 0.01377 由于pctchg与alpha在行业内的分位数计算其实是一样的，所以基本与alpha_by_industry一样
N=2: 0.00881 
N=3: 0.00495
N=5: 0.00043
'''
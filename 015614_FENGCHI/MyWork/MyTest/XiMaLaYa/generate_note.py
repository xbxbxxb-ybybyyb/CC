# coding: utf-8
# Author：fengchi863
# Date ：2021/6/3 21:07

from ShortTermTrading.dataApi import getData, tradeDate, stockList, indName
from xquant.factordata import FactorData
from FaaMonitor.Util.DtUtil import DtUtil
from FaaMonitor.Util.MyUtil import MyUtil
from FaaMonitor.Util.tools import send_file
import os
import pandas as pd, numpy as np

verbose = True
add_ad = False

fd = FactorData()

start_date = 20210101
end_date = DtUtil.get_yesterday_date()
date_list = tradeDate.get_date_range(start_date, end_date)
mkt_cap = getData.get_daily_1factor('a_mkt_cap', date_list=date_list)
mkt_cap = mkt_cap.iloc[-1].sort_values(ascending=False)
stk_list = mkt_cap.index.tolist()

# 读取文件，去掉已经讲过的
has_stk_id_list = os.listdir('output/')
has_stk_id_list = list(map(lambda x: int(x[:-4]), has_stk_id_list))

stk_id = None
for ele in stk_list:
    if ele in has_stk_id_list:
        continue
    else:
        stk_id = ele
        break

stk_code = stockList.trans_int2windcode(stk_id)
stk_name = MyUtil.get_1stock_name(stk_code)

df1 = fd.get_factor_value('WIND_AShareIntroduction', S_INFO_WINDCODE=stk_code)
province = df1['S_INFO_PROVINCE'].values[0]
city = df1['S_INFO_CITY'].values[0]
found_date = df1['S_INFO_FOUNDDATE'].values[0][:4]
office = df1['S_INFO_OFFICE'].values[0]
main_business = df1['S_INFO_MAIN_BUSINESS'].values[0]
main_business = main_business[5:-1]

df2 = fd.get_factor_value('WIND_AShareDescription', S_INFO_WINDCODE=stk_code)
list_date = df2['S_INFO_LISTDATE'].values[0][:4]

exchmarket = df2['S_INFO_EXCHMARKET'].apply(lambda x: '上交所' if x=='SSE' else '深交所').values[0]
list_board_name = df2['S_INFO_LISTBOARDNAME'].values[0]

df3 = getData.get_daily_1factor('SW1', date_list=date_list)
SW1 = indName.sw_level1[df3.iloc[-1][stk_id]]
df3 = getData.get_daily_1factor('SW2', date_list=date_list)
SW2 = indName.sw_level2[df3.iloc[-1][stk_id]]
df3 = getData.get_daily_1factor('SW3', date_list=date_list)
SW3 = indName.sw_level3[df3.iloc[-1][stk_id]]

sentence1 = f'三分钟认识一家上市公司。[=0.5秒]今天要讲的企业是{stk_name}[=0.2秒]。{stk_name}，办公地址为{office}。' + \
            f'公司成立于{found_date}年，{list_date}年于{exchmarket}{list_board_name}上市，股票代码为<figure>{stk_code[:-3]}</figure type=ordinal>。' + \
            f'公司主要产品及业务包括{main_business}，申万一级行业为{SW1}，二级行业为{SW2}，三级行业为{SW3}[=0.2秒]。'

df4 = fd.get_factor_value('WIND_AShareBalanceSheet', S_INFO_WINDCODE=stk_code,
                          REPORT_PERIOD=['20201231'], STATEMENT_TYPE=['408001000'])

tot_assets = df4['TOT_ASSETS'].values[0] / 1e8
tot_assets = '%.2f' % tot_assets
total_net_assets = df4['TOT_SHRHLDR_EQY_INCL_MIN_INT'].values[0] / 1e8
total_net_assets = '%.2f' % total_net_assets

df5 = fd.get_factor_value('WIND_AShareIncome', S_INFO_WINDCODE=stk_code,
                          REPORT_PERIOD=['20201231'], STATEMENT_TYPE=['408001000'])

oper_rev = df5['OPER_REV'].values[0] / 1e8
oper_rev = '%.2f' % oper_rev
net_profit_tot = df5['NET_PROFIT_AFTER_DED_NR_LP'].values[0] / 1e8
net_profit_tot = '%.2f' % net_profit_tot

df5 = fd.get_factor_value('WIND_AShareStyleCoefficient', S_INFO_WINDCODE=stk_code)
gross_oper_netprofit = df5['GROSS_OPER_NETPROFIT'].values[-1]
gross_oper_netprofit = '%.2f' % (gross_oper_netprofit * 100)

sentence2 = f'[=0.5秒]截至2020年末，公司总资产{tot_assets}亿，净资产{total_net_assets}亿，营业收入{oper_rev}亿，净利润{net_profit_tot}亿，最近一年净利润年增长率为{gross_oper_netprofit}%。[=0.2秒]'

end_sentence = '[=1秒]如果对您有所帮助，可以分享给您的朋友，感谢观看[=1秒]。'

to_sentence1 = '\n\n'

to_sentence2 = '\n\n'

ad_sentence = '超低佣金证券开户，佣金低至万一，一年可节省上千元！[=0.2秒]有需要的朋友请关注公众号“中长线投资笔记”，回复“开户”[=0.2秒]，即可获取开户专属链接。[=1秒]'

if add_ad:
    output = sentence1 + '\n' + \
             to_sentence1 + '\n' + \
             sentence2 + '\n' + \
             to_sentence2 + '\n' + \
             end_sentence
else:
    output = sentence1 + '\n' + \
             to_sentence1 + '\n' + \
             sentence2 + '\n' + \
             to_sentence2 + '\n' + \
             end_sentence + '\n' + \
             ad_sentence

print(output)
print('总字数%d' % len(output))

if verbose:
    fh = open('output/%d.txt' % stk_id, 'w', encoding='utf-8')
    fh.write(output)
    fh.close()

fh = open('tmp_output/%d.txt' % stk_id, 'w', encoding='utf-8')
fh.write(output)
fh.close()
send_file(['015614'], 'tmp_output/%d.txt' % stk_id)
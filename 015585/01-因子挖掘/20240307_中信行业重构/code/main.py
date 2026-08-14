import pandas as pd
import numpy as np
import os
import sys
import IO
from xquant.factordata import FactorData
s = FactorData()
'''
1、md数据取每天股票列表，接口取其所属中信一级行业、二级行业，按天存成文件，最后合并
2、统计20150701-20240305，所有行业平均每天的股票个数
3、对逻辑意义不同 or 股票个数较多的行业，用枚举法列明拆分逻辑
4、根据拆分逻辑生成新的行业名称，记录编码
'''
# md数据取每天股票列表
start_date = '20150701'
end_date = '20240305'
md_data = IO.read_data([start_date, end_date],
                          columns=['amt'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
date_list = list(md_data.index.get_level_values(0).unique())
date_list = [i.strftime('%Y%m%d') for i in date_list]
# # 接口取其所属中信一级行业、二级行业，按天存成文件，最后合并
# res = pd.DataFrame()
# print('取中信一级/二级行业')
# for date in date_list:
#     sys.stdout.write('\r' + date)
#     sys.stdout.flush()
#     stock_date_list = list(md_data.loc[pd.Timestamp(date)].index) # 当日的股票列表
#     res1_date = s.hsi(stock_date_list, date, 'CITICS', 1).drop(['industry_type'],axis=1)
#     res2_date = s.hsi(stock_date_list, date, 'CITICS', 2).drop(['industry_type'],axis=1)
#     res1_date['dt'] = pd.Timestamp(date)
#     res2_date['dt'] = pd.Timestamp(date)
#     res1_date.columns = ['Ticker','indu_code1','indu_name1','dt']
#     res2_date.columns = ['Ticker','indu_code2','indu_name2','dt']
#     res_date = pd.merge(res1_date,res2_date,on = ['dt','Ticker']).set_index(['dt','Ticker'])
#     res_date.to_pickle('/data/user/015585/01-因子挖掘/20240307_中信行业重构/file/' + date + '.pkl')
#     res = res.append(res_date)
# res.to_pickle('/data/user/015585/01-因子挖掘/20240307_中信行业重构/file/all_indu_ori.pkl')
res = pd.read_pickle('/data/user/015585/01-因子挖掘/20240307_中信行业重构/file/all_indu_ori.pkl')
# 一些二级行业被更新，从wind历史表中获取名称,归类到最新二级分类中
wind_induname = s.get_factor_value('WIND_AShareIndustriesCode')
res['is_nan1'] = res['indu_code1'].apply(lambda x : 1 if type(x) == float else 0) # 如果一级行业code为空，则剔除
res = res[res['is_nan1'] == 0]
res['is_nan2'] = res['indu_name2'].apply(lambda x : 1 if type(x) == float else 0) # 对二级行业name为空，但有code的标的，补充名称
suplist_inducode2 = list(res[res['is_nan2'] == 1]['indu_code2'].unique())
supdic_inducode2 = {} # 记录要补充的二级行业代码和名字
for inducode2 in suplist_inducode2:
    name2_list = wind_induname[wind_induname['INDUSTRIESCODE'] == inducode2.ljust(16,'0')]['INDUSTRIESNAME'].unique()
    if len(name2_list) == 1:
        name2 = name2_list[0]
        res.loc[res['indu_code2'] == inducode2, 'indu_name2'] = name2
        supdic_inducode2[inducode2] = name2
    else:
        print('找到2个以上/找不到名称:',inducode2)
# 统计20150701-20240305，所有一级行业平均每天的股票个数
indu_num_stats = res.groupby(['indu_name1','dt']).count()['indu_code1'].groupby('indu_name1').mean().sort_values(ascending = False)
# 拆分逻辑
'''
1、对一些一级行业拆分为二级（包含了逻辑显著不同的二级行业/一级行业过大）
非银行金融（逻辑）
食品饮料（逻辑）
农林牧渔（逻辑）
有色金属（逻辑）
机械
基础化工
医药
电子
计算机
电力设备及新能源
汽车
电力及公用事业
2、再把一些二级(一级）行业合并
'''
# 拆分
split_indu1 = ['非银行金融','食品饮料','农林牧渔','有色金属','机械','基础化工','医药','计算机','电力设备及新能源','汽车','电力及公用事业']
res['indu_name_step1'] = res['indu_name1']
res['indu_code_step1'] = res['indu_code1'].apply(lambda x : 'new_' + x if type(x) == str else x)
res.loc[res['indu_name1'].isin(split_indu1),'indu_name_step1'] = res.loc[res['indu_name1'].isin(split_indu1),'indu_name2'] # 要拆分的行业，用二级行业赋值step1
res.loc[res['indu_name1'].isin(split_indu1),'indu_code_step1'] = \
    res.loc[res['indu_name1'].isin(split_indu1),'indu_code2'].apply(lambda x : 'new_' + x if type(x) == str else x) # 要拆分的行业，用二级行业赋值step1
# 合并
merge_indu2 = {
               '其他金融':['多元金融','综合金融'],
               '普通食品饮料':['饮料','食品'],
               '其他农业':['林业','农产品加工Ⅱ'],
               '其他金属':['工业金属','稀有金属'],
               '汽车整车与销售':['乘用车Ⅱ','商用车','汽车销售及服务Ⅱ'],
               '西药':['化学制药','生物医药Ⅱ','其他医药医疗'],
               '无机化学品':['化学纤维','化学原料'],
               '工业有机化学品':['塑料及制品','橡胶及制品','其他化学制品Ⅱ'],
               '电气电源设备':['电气设备','电源设备','电站设备Ⅱ'],
               '软件与计算机服务':['计算机软件','云服务','产业互联网','IT服务']}
code_merge_indu2 = {'其他金融':'new_1',
               '普通食品饮料':'new_2',
               '其他农业':'new_3',
               '其他金属':'new_4',
               '汽车整车与销售':'new_5',
               '西药':'new_6',
               '无机化学品':'new_7',
               '工业有机化学品':'new_8',
               '电气电源设备':'new_9',
               '软件与计算机服务':'new_10'}
res['indu_name_step2'] = res['indu_name_step1']
res['indu_code_step2'] = res['indu_code_step1']
for merge_indu,ori_indu in merge_indu2.items():
    print(merge_indu,ori_indu)
    res.loc[res['indu_name_step1'].isin(ori_indu), 'indu_name_step2'] = merge_indu
    res.loc[res['indu_name_step2'] == merge_indu, 'indu_code_step2'] = code_merge_indu2[merge_indu]

dic_num_code = {} # 把最终确定的行业给予数字编码1,2,3,....,49
tmp_count = 1
res['final_indu_number'] = 0
for i in list(res['indu_code_step2'].unique()):
    dic_num_code[i] = tmp_count
    res.loc[res['indu_code_step2'] == i,'final_indu_number'] = tmp_count
    tmp_count += 1

res[['indu_code1', 'indu_name1', 'indu_code2', 'indu_name2', 'indu_name_step2',
       'indu_code_step2', 'final_indu_number']].to_pickle('/data/user/015585/01-因子挖掘/999-share/for sss/tmp/20240307_中信行业分类.pkl')

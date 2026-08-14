import pandas as pd
import IO
import numpy as np
from xquant.thirdpartydata.factordata import FactorData

s = FactorData()

dict_gogoal_zxzx = {
    'rpt_forecast_stk':'DWD_EXP_RESEARCHREPORT',
    'rpt_rating_adjust':'DWD_EXP_REPORTRATINGADJ',
    'rpt_earnings_adjust':'DWD_EXP_RESEARCHREPORTADJ',
    'rpt_organ_information':'EXP_ORALIST',
    'rpt_rating_compare': 'DWD_EXP_RPTRATINGCOMPARE',
    'rpt_report_type':'DWD_EXP_REPORTTYPE',
    # 一致预期
    'con_forecast_stk':'DWD_EXP_FORECASTSECU',
    'con_rating_stk':'DWD_EXP_FORECASTSCHEDULE',
    'con_target_price_stk':'DWD_EXP_FORECASTSCHEDULE',
    'con_forecast_roll_stk':'DWD_EXP_FORECASTSECUDERIVED'
}
start_date = '20240101'
start_date2 = '20250401'
save_path = '/data/user/015585/01-因子挖掘/20250415_朝阳永续数据/file/'
df1 = s.get_factor_value(f'GOGOAL2_{dict_gogoal_zxzx["rpt_forecast_stk"]}',
                          WRITINGDATE=[f'>={start_date}'],)
print(df1.shape)
df1.to_pickle(f'{save_path}{dict_gogoal_zxzx["rpt_forecast_stk"]}.pkl')

df2 = s.get_factor_value(f'GOGOAL2_{dict_gogoal_zxzx["rpt_rating_adjust"]}',
                         currentcreatedate=[f'>={start_date}'],)
print(df2.shape)
df2.to_pickle(f'{save_path}{dict_gogoal_zxzx["rpt_rating_adjust"]}.pkl')

df3 = s.get_factor_value(f'GOGOAL2_{dict_gogoal_zxzx["rpt_earnings_adjust"]}',
                         currentcreatedate=[f'>={start_date}'],)
print(df3.shape)
df3.to_pickle(f'{save_path}{dict_gogoal_zxzx["rpt_earnings_adjust"]}.pkl')

df4 = s.get_factor_value(f'GOGOAL2_{dict_gogoal_zxzx["rpt_organ_information"]}',)
print(df4.shape)
df4.to_pickle(f'{save_path}{dict_gogoal_zxzx["rpt_organ_information"]}.pkl')

df5 = s.get_factor_value(f'GOGOAL2_{dict_gogoal_zxzx["rpt_report_type"]}',)
print(df5.shape)
df5.to_pickle(f'{save_path}{dict_gogoal_zxzx["rpt_report_type"]}.pkl')


df6 = s.get_factor_value(f'GOGOAL2_{dict_gogoal_zxzx["con_forecast_stk"]}',
                         forecastdate=[f'>={start_date2}'],)
print(df6.shape)
df6.to_pickle(f'{save_path}{dict_gogoal_zxzx["con_forecast_stk"]}.pkl')

df7 = s.get_factor_value(f'GOGOAL2_{dict_gogoal_zxzx["con_rating_stk"]}',
                         forecastdate=[f'>={start_date2}'],)
print(df7.shape)
df7.to_pickle(f'{save_path}{dict_gogoal_zxzx["con_rating_stk"]}.pkl')

df8 = s.get_factor_value(f'GOGOAL2_{dict_gogoal_zxzx["con_target_price_stk"]}',
                         forecastdate=[f'>={start_date2}'],)
print(df8.shape)
df8.to_pickle(f'{save_path}{dict_gogoal_zxzx["con_target_price_stk"]}.pkl')

df9 = s.get_factor_value(f'GOGOAL2_{dict_gogoal_zxzx["con_forecast_roll_stk"]}',
                         forecastdate=[f'>={start_date2}'],)
print(df9.shape)
df9.to_pickle(f'{save_path}{dict_gogoal_zxzx["con_forecast_roll_stk"]}.pkl')

# 逐个分析时效性
df1 = pd.read_pickle(f'{save_path}{dict_gogoal_zxzx["rpt_forecast_stk"]}.pkl')
for col in ['writingdate', 'entrytime', 'updatetime', 'groundtime']:
    col = col.upper()
    df1[col] = df1[col].apply(pd.Timestamp)
print('=========DWD_EXP_RESEARCHREPORT, 卖方预测数据表========')
print('GROUND - WRITING')
print((df1['GROUNDTIME'] - df1['WRITINGDATE']).quantile([0.25,0.5,0.75,0.99]))
print('ENTRY - GROUND')
df1_filter = df1[df1['WRITINGDATE'] >= pd.Timestamp('20250101')]
print((df1_filter['ENTRYTIME'] - df1_filter['GROUNDTIME']).quantile([0.25,0.5,0.75,0.99]))
print('结论：24年以来，朝阳永续入表较研报撰写时间，75%会延迟2天以内，99%会延迟一周以内；25年以来，信息技术部落地最多延迟1小时')
print('建议：取朝阳永续落地时间（GROUNDTIME）向后1.5小时作为历史数据的真实入表时间')

df2 = pd.read_pickle(f'{save_path}{dict_gogoal_zxzx["rpt_rating_adjust"]}.pkl')
for col in ['CURRENTCREATEDATE', 'entrytime', 'updatetime', 'groundtime']:
    col = col.upper()
    df2[col] = df2[col].apply(pd.Timestamp)
print('=========DWD_EXP_REPORTRATINGADJ, 报告评级调整表========')
print('GROUND - CURRENTCREATEDATE(本次评级日期)')
print((df2['GROUNDTIME'] - df2['CURRENTCREATEDATE']).quantile([0.25,0.5,0.75,0.99]))
print('ENTRY - GROUND')
df2_filter = df2[df2['CURRENTCREATEDATE'] >= pd.Timestamp('20250101')]
print((df2_filter['ENTRYTIME'] - df2_filter['GROUNDTIME']).quantile([0.25,0.5,0.75,0.99]))
print('结论：同样，朝阳永续落地会延迟1-7天，资讯写入最多延迟1小时')
print('建议：使用GROUNDTIME延迟1.5小时')

df6 = pd.read_pickle(f'{save_path}{dict_gogoal_zxzx["con_forecast_stk"]}.pkl')
for col in ['FORECASTDATE', 'entrytime', 'updatetime', 'groundtime']:
    col = col.upper()
    df6[col] = df6[col].apply(pd.Timestamp)
print('=========DWD_EXP_FORECASTSECU, 个股一致预期数据表========')
print('GROUND - FORECASTDATE(一致预期日期)')
print((df6['GROUNDTIME'] - df6['FORECASTDATE']).quantile([0.25,0.5,0.75,0.99]))
print('ENTRY - GROUND')
df6_filter = df6[df6['FORECASTDATE'] >= pd.Timestamp('20250101')]
print((df6_filter['ENTRYTIME'] - df6_filter['GROUNDTIME']).quantile([0.25,0.5,0.75,0.9,0.99]))
print('结论：一致预期数据，朝阳永续落地时间一般在当日晚间7点15之前发布，信息技术部入表时间大多在8点15之前，4月以来有2-3天在9点前完成')
print('建议：一致预期日期即为所求，一致预期日期是交易日 + 节假日/周末的最后一天')

df7 = pd.read_pickle(f'{save_path}{dict_gogoal_zxzx["con_rating_stk"]}.pkl')
for col in ['FORECASTDATE', 'entrytime', 'updatetime', 'groundtime']:
    col = col.upper()
    df7[col] = df7[col].apply(pd.Timestamp)
print('=========DWD_EXP_FORECASTSCHEDULE, 个股一致预期评级表========')
print('GROUND - FORECASTDATE(一致预期日期)')
print((df7['GROUNDTIME'] - df7['FORECASTDATE']).quantile([0.25,0.5,0.75,0.99]))
print('ENTRY - GROUND')
df7_filter = df7[df7['FORECASTDATE'] >= pd.Timestamp('20250101')]
print((df7_filter['ENTRYTIME'] - df7_filter['GROUNDTIME']).quantile([0.25,0.5,0.75,0.9,0.99]))
print('结论：一致预期数据，朝阳永续落地时间一般在当日晚间7点15之前发布，信息技术部入表时间大多在8点15之前，4月以来有1天在8点40完成')
print('建议：一致预期日期即为所求，一致预期日期是交易日 + 节假日/周末的最后一天')

df9 = pd.read_pickle(f'{save_path}{dict_gogoal_zxzx["con_forecast_roll_stk"]}.pkl')
for col in ['FORECASTDATE', 'entrytime', 'updatetime', 'groundtime']:
    col = col.upper()
    df9[col] = df9[col].apply(pd.Timestamp)
print('=========DWD_EXP_FORECASTSECUDERIVED, 个股一致预期滚动数据表========')
print('GROUND - FORECASTDATE(一致预期日期)')
print((df9['GROUNDTIME'] - df9['FORECASTDATE']).quantile([0.25,0.5,0.75,0.99]))
print('ENTRY - GROUND')
df9_filter = df9[df9['FORECASTDATE'] >= pd.Timestamp('20250101')]
print((df9_filter['ENTRYTIME'] - df9_filter['GROUNDTIME']).quantile([0.25,0.5,0.75,0.9,0.99]))
print('结论：一致预期数据，朝阳永续落地时间一般在当日晚间7点15之前发布，信息技术部入表时间大多在8点15之前，4月以来有1天在8点40完成')
print('建议：一致预期日期即为所求，一致预期日期是交易日 + 节假日/周末的最后一天')

# 验证历史数据区间，手动执行下述代码
for data in dict_gogoal_zxzx:
    df = s.get_factor_value(f'GOGOAL2_{dict_gogoal_zxzx[data]}',
                            FORECASTDATE=['>=20120101', '<=20120131'],)
    print(data)
    print(df.shape)
# tmp = df9[['FORECASTDATE','TRADINGCODE','GROUNDTIME','ENTRYTIME','UPDATETIME']]
# tmp.groupby('FORECASTDATE')['ENTRYTIME'].max()

# tmp = s.get_factor_value(f'GOGOAL2_{dict_gogoal_zxzx["rpt_forecast_stk"]}',
#                           WRITINGDATE=[f'>={20120101}', '<=20120131'],)






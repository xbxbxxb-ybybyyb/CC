import pandas as pd
import os
import IO
from xquant.thirdpartydata.factordata import FactorData

s = FactorData()


root_path = '/dfs/group/900001/XDB/00_MarketData/00_StockData/03_FinancialData/01_SuntimeData/'

table_list = ['DWD_EXP_RESEARCHREPORT','DWD_EXP_REPORTRATINGADJ','DWD_EXP_RESEARCHREPORTADJ',
              'EXP_ORALIST',
              'DWD_EXP_RPTRATINGCOMPARE','DWD_EXP_REPORTTYPE','DWD_EXP_FORECASTSECU','DWD_EXP_FORECASTSCHEDULE','DWD_EXP_FORECASTSCHEDULE','DWD_EXP_FORECASTSECUDERIVED',]
# 是否有相关文件夹
list_file = os.listdir(root_path)
for i in table_list:
    if i not in list_file:
        print(i, '无相关文件夹')
    else:
        print(i, '有相关文件夹')
'''
只有 DWD_EXP_FORECASTSECUDERIVED
'''
# 验证 DWD_EXP_FORECASTSECUDERIVED
table_name = 'DWD_EXP_FORECASTSECUDERIVED'
df_new = IO.read_data([20250501,20250510], alt = f'{root_path}{table_name}/{table_name}.h5')
print(df_new.columns)
df_new.groupby('dt')['ID'].count()

df_new_xquant = s.get_factor_value('GOGOAL2_DWD_EXP_FORECASTSECUDERIVED',
                        FORECASTDATE=['>=20250501', '<=20250510'], )
df_new_xquant.groupby('FORECASTDATE')['ID'].count()


df_his = IO.read_data([20120101,20120131], alt = f'{root_path}{table_name}/{table_name}.h5')
df_his.groupby('dt')['ID'].count()

# 卖方预测数据的告警阈值
dict_gogoal_zxzx = {
    'rpt_forecast_stk':'DWD_EXP_RESEARCHREPORT',
    'rpt_rating_adjust':'DWD_EXP_REPORTRATINGADJ',
    'rpt_earnings_adjust':'DWD_EXP_RESEARCHREPORTADJ',
    'rpt_rating_compare': 'DWD_EXP_RPTRATINGCOMPARE',
    'rpt_report_type':'DWD_EXP_REPORTTYPE',
    # 一致预期
    'con_forecast_stk':'DWD_EXP_FORECASTSECU',
    'con_rating_stk':'DWD_EXP_FORECASTSCHEDULE',
    'con_target_price_stk':'DWD_EXP_FORECASTSCHEDULE',
    'con_forecast_roll_stk':'DWD_EXP_FORECASTSECUDERIVED'
}
save_path = '/data/user/015585/01-因子挖掘/20250415_朝阳永续数据/file/'
for i in dict_gogoal_zxzx.keys():
    df = pd.read_pickle(f'{save_path}{dict_gogoal_zxzx[i]}.pkl')
    df['dt'] = df['GROUNDTIME'].apply(lambda x : str(x).split(' ')[0])
    print(dict_gogoal_zxzx[i])
    print(df.groupby('dt').count()['ID'])

# 卖方预测数据的GROUNDTIME

for i in dict_gogoal_zxzx.keys():
    df = s.get_factor_value(f'GOGOAL2_{dict_gogoal_zxzx[i]}',
                              currentcreatedate=['>=20120101','<=20120131'],)
    df['dt'] = df['GROUNDTIME'].apply(lambda x : str(x).split(' ')[0])
    print(dict_gogoal_zxzx[i])
    print(df.groupby('dt').count()['ID'])




import pandas as pd
import os
import IO
from xquant.thirdpartydata.factordata import FactorData

s = FactorData()

root_path = '/data/group/800080/warehouseJG/prod/DATABASE/SUNTIME/'
for i in os.listdir(root_path):
    print(i)
for i in os.listdir(root_path):
    if i not in  ['EXP_ORALIST', 'DWD_EXP_RPTRATINGCOMPARE', 'DWD_EXP_REPORTTYPE', 'DWD_EXP_RPTGOGOALRATING']:
        df = IO.read_data([20250517, 20250523], alt = f'{root_path}{i}/{i}.h5')
    else:
        df = pd.read_hdf(f'{root_path}{i}/{i}.h5')
    print(i)
    print(df.head())

'''
DWD_EXP_RESEARCHREPORTADJ
DWD_EXP_REPORTTYPE
DWD_EXP_FORECASTSCHEDULE
DWD_EXP_REPORTTARGETPRICEADJ
DWD_EXP_RPTRATINGCOMPARE
DWD_EXP_RESEARCHREPORT
DWD_EXP_FORECASTSECUDERIVED
DWD_EXP_RPTGOGOALRATING
DWD_EXP_FORECASTSECU
DWD_EXP_REPORTRATINGADJ
EXP_ORALIST
'''
i = 'EXP_ORALIST'
if i not in ['EXP_ORALIST', 'DWD_EXP_RPTRATINGCOMPARE', 'DWD_EXP_REPORTTYPE', 'DWD_EXP_RPTGOGOALRATING']:
    df = IO.read_data([20250517, 20250523], alt=f'{root_path}{i}/{i}.h5')
else:
    df = pd.read_hdf(f'{root_path}{i}/{i}.h5')
# df.groupby('dt').count()['ID']
# 之前存储的xquant数据
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
save_path = '/data/user/015585/01-因子挖掘/20250415_朝阳永续数据/file/'

df1 = pd.read_pickle(f'{save_path}{dict_gogoal_zxzx["rpt_forecast_stk"]}.pkl')


start_date = '20250501'
save_path = '/data/user/015585/01-因子挖掘/20250415_朝阳永续数据/file/'
df_tmp = s.get_factor_value(f'GOGOAL2_{dict_gogoal_zxzx["rpt_forecast_stk"]}',
                          WRITINGDATE=[f'>={start_date}'],)
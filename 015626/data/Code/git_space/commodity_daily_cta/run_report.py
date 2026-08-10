from gen_report import final_generate_pdf,generate_basis_std_pdf
import sys
sys.path.insert(4,'/dfs/user/012398/working_code/prod_zhangf/')
sys.path.insert(4,'.')
import multifactor.utility.dt as dt
import pandas as pd
import datetime, os, time

curdate = dt.get_trading_day_offset(pd.Timestamp(datetime.date.today()),1)[0]
update_date = pd.Timestamp(datetime.date.today()).strftime('%Y%m%d')
#update_date = '20250825'
start_date = '20100101'
end_date = update_date
prev_date = dt.get_trading_day_offset(end_date,-5)[0].strftime('%Y%m%d')

flag_path = os.path.join('/data/group/800466/warehouse/prod/tradingstats/Spiral/other/flag')
report_path = '/data/group/800466/warehouse/prod/tradingstats/Spiral/report'
if not os.path.exists(report_path):
    os.makedirs(report_path)
    
def data_flag_check(date):    
    flag1 = os.path.join(flag_path,'cta_trend_' + date + '.success')
    flag2 = os.path.join(flag_path,'cta_basis_' + date + '.success')
    return os.path.exists(flag1) & os.path.exists(flag2)

print('------wait strategy flag')
while True:
    if data_flag_check(end_date):
        break
    time.sleep(60)
print('flag check finished!')

daily_df_trend = pd.read_hdf('/data/group/800466/warehouse/prod/tradingstats/Spiral/trend_strategy/data/daily_df_fix.h5')
daily_df_basis = pd.read_hdf('/data/group/800466/warehouse/prod/tradingstats/Spiral/basis_strategy/data/daily_df_fix.h5')
trade_df_trend = pd.read_hdf('/data/group/800466/warehouse/prod/tradingstats/Spiral/trend_strategy/data/trade_df_fix.h5')
trade_df_basis = pd.read_hdf('/data/group/800466/warehouse/prod/tradingstats/Spiral/basis_strategy/data/trade_df_fix.h5')

basis_ratio_all = pd.read_hdf('/data/group/800466/warehouse/prod/tradingstats/Spiral/trend_strategy/data/basis_ratio.h5')
std_df = pd.read_hdf('/data/group/800466/warehouse/prod/tradingstats/Spiral/trend_strategy/data/std_df.h5')
    
pdf_name = 'LongTermCTA_TrendBasis_20100101_' + end_date + '.pdf'
pdf_name_nodcecfe = 'LongTermCTA_TrendBasis_noDCECFE_20100101_' + end_date + '.pdf'
pdf_name_nodce = 'LongTermCTA_TrendBasis_noDCE_20100101_' + end_date + '.pdf'

basis_std_rptname = 'CTA_MarketStats_report_20100101_' + end_date + '.pdf'

report_name = os.path.join(report_path,pdf_name)
report_name_nodcecfe = os.path.join(report_path,pdf_name_nodcecfe)
report_name_nodce = os.path.join(report_path,pdf_name_nodce)
basis_std_rptname = os.path.join(report_path, basis_std_rptname)

final_generate_pdf(trade_df_trend, daily_df_trend, trade_df_basis, daily_df_basis, start_date, '20250101', end_date, report_name, has_DCE = True, has_CFE = True, need_perticker_pdf = True)
final_generate_pdf(trade_df_trend, daily_df_trend, trade_df_basis, daily_df_basis, start_date, '20250101', end_date, report_name_nodcecfe, has_DCE = False, has_CFE = False, need_perticker_pdf = False)
final_generate_pdf(trade_df_trend, daily_df_trend, trade_df_basis, daily_df_basis, start_date, '20250101', end_date, report_name_nodce, has_DCE = False, has_CFE = True, need_perticker_pdf = False)
generate_basis_std_pdf(basis_ratio_all, std_df, 20100101, prev_date,end_date, os.path.join(report_path, basis_std_rptname))
import sys
sys.path.insert(4,'/dfs/user/012398/working_code/prod_zhangf/')
import multifactor.utility.dt as dt
from comm_cta_basis import Pos_basis as Pos
from gen_report import final_generate_pdf,generate_basis_std_pdf
import pandas as pd
import os,time
import datetime
import warnings
warnings.filterwarnings('ignore')
from SEND_FILE import send_file

curdate = dt.get_trading_day_offset(pd.Timestamp(datetime.date.today()),1)[0]
update_date = pd.Timestamp(datetime.date.today()).strftime('%Y%m%d')
#curdate = pd.Timestamp('20250820')
#update_date = '20250819'
start_date = '20100101'
end_date = update_date
para_date = update_date

res_path = '/data/group/800466/warehouse/prod/tradingstats/Spiral/basis_strategy'
para_path = os.path.join(res_path, 'para')
para_path1 = '/dfs/group/800466/trade/spiral/para_basis'
report_path = os.path.join(res_path,'report')
data_path = os.path.join(res_path,'data')
flag_path = os.path.join('/data/group/800466/warehouse/prod/tradingstats/Spiral/other/flag')

for pa in [res_path, report_path, para_path, para_path1, data_path, flag_path]:
    if not os.path.exists(pa):
        os.makedirs(pa)

def data_flag_check(date):
    flagpath = '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/FLAG'
    flagname = str(date) + '_commodity_daily_data.success'
    check_path = os.path.join(flagpath, str(date), flagname)
    return os.path.exists(check_path)
    
print('------wait data flag')
while True:
    if data_flag_check(end_date):
        break
    time.sleep(60)
print('flag check finished!')

commcta = Pos(start_date, end_date)
tickerlist = commcta.tickerlist
commcta.calc_basis_ratio_all(start_date,end_date,use_cache=False)
#basis_ratio_all = commcta.calc_basis_ratio_all(start_date,end_date)
basis_ratio_all = commcta.basis_df
daily_df, trade_df, sigin_df = commcta.backtest(tickerlist,use_univ = True)
mltip = commcta.multip
univ_data = commcta.univ_data
sharesadj = commcta.sharesadj
std_df = commcta.std_df

tickerlist = commcta.tickerlist

print('save data')
daily_df.to_hdf(os.path.join(data_path,'daily_df_fix.h5'),key = 'daily_df')
trade_df.to_hdf(os.path.join(data_path,'trade_df_fix.h5'),key = 'trade_df')
sigin_df.to_hdf(os.path.join(data_path,'sigin_df.h5'),key = 'sigin_df')

# gen trading parameters
#para_df_fortrade,para_forwind = commcta.get_trade_parameters(para_date, daily_df.loc[pd.Timestamp(para_date)],omit_dce = True)
#para_df_fortrade.to_csv(os.path.join(para_path1, 'para_basis_'+ curdate.strftime('%Y%m%d') + '.csv'))
#para_forwind.to_excel(os.path.join(para_path, 'para_basis_forwind_'+ curdate.strftime('%Y%m%d') + '.xlsx'))
#para_df_fortrade_all,para_forwind_all = commcta.get_trade_parameters(para_date, daily_df.loc[pd.Timestamp(para_date)],omit_dce=False)
#para_forwind_all.to_excel(os.path.join(para_path, 'para_basis_all_forwind_'+ curdate.strftime('%Y%m%d') + '.xlsx'))

#reportname_2010 = 'LongTermCTA_Basis_2010_' + end_date + '.pdf'
#reportname_2016 = 'LongTermCTA_Basis_2016_' + end_date + '.pdf'
#reportname_2025 = 'LongTermCTA_Basis_2025_' + end_date + '.pdf'
#final_generate_pdf(trade_df, daily_df, 20100101, end_date, os.path.join(report_path,reportname_2010))
#final_generate_pdf(trade_df, daily_df, 20160101, end_date, os.path.join(report_path,reportname_2016))
#final_generate_pdf(trade_df, daily_df, 20250101, end_date, os.path.join(report_path,reportname_2025))

flag_path_success = os.path.join(flag_path, 'cta_basis_' + end_date + '.success')
with open(flag_path_success,'w'):
    pass
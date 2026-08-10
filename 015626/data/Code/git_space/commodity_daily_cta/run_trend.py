import sys
sys.path.insert(4,'/dfs/user/012398/working_code/prod_zhangf/')
import multifactor.utility.dt as dt
from comm_cta_trend import Pos_trend as Pos
from gen_report import final_generate_pdf,generate_basis_std_pdf
import pandas as pd
import os,time
import datetime
import warnings
warnings.filterwarnings('ignore')
from SEND_FILE import send_file

#curdate = pd.Timestamp(datetime.date.today())
#if dt.get_trading_day_offset(curdate,0)[0] == curdate:
#    update_date = dt.get_trading_day_offset(curdate,-1)[0].strftime('%Y%m%d')
#else:
#    update_date = dt.get_trading_day_offset(curdate,0)[0].strftime('%Y%m%d')

curdate = dt.get_trading_day_offset(pd.Timestamp(datetime.date.today()),1)[0]
update_date = pd.Timestamp(datetime.date.today()).strftime('%Y%m%d')
#curdate = pd.Timestamp('20250818')
#update_date = '20250815'
start_date = '20100101'
end_date = update_date
para_date = update_date

res_path = '/data/group/800466/warehouse/prod/tradingstats/Spiral/trend_strategy'
para_path = os.path.join(res_path, 'para')
#pos_path = os.path.join(res_path, 'daily_pos')
para_path1 = '/dfs/group/800466/trade/spiral/para'
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
mltip.to_csv(os.path.join(data_path,'mult.csv'))
univ_data.to_hdf(os.path.join(data_path,'univ_data.h5'),key = 'univ')
sharesadj.to_hdf(os.path.join(data_path,'sharesadj.h5'),key = 'sharesadj')
std_df.to_hdf(os.path.join(data_path,'std_df.h5'),key = 'std_df')
basis_ratio_all.to_hdf(os.path.join(data_path,'basis_ratio.h5'),key = 'basis_ratio')
pd.Series(tickerlist).to_csv(os.path.join(data_path,'tickerlist.csv'))

# gen trading parameters
#para_df_fortrade,para_forwind = commcta.get_trade_parameters(para_date, daily_df.loc[pd.Timestamp(para_date)],omit_dce = True)
#para_df_fortrade.to_csv(os.path.join(para_path1, 'para_'+ curdate.strftime('%Y%m%d') + '.csv'))
#para_forwind.to_excel(os.path.join(para_path, 'para_forwind_'+ curdate.strftime('%Y%m%d') + '.xlsx'))
#para_df_fortrade_all,para_forwind_all = commcta.get_trade_parameters(para_date, daily_df.loc[pd.Timestamp(para_date)],omit_dce=False)
#para_forwind_all.to_excel(os.path.join(para_path, 'para_all_forwind_'+ curdate.strftime('%Y%m%d') + '.xlsx'))

#reportname_2010 = 'LongTermCTA_Trend_2010_' + end_date + '.pdf'
#reportname_2016 = 'LongTermCTA_Trend_2016_' + end_date + '.pdf'
#reportname_2025 = 'LongTermCTA_Trend_2025_' + end_date + '.pdf'
#basis_std_rptname = 'CTA_MarketStats_report_2010_' + end_date + '.pdf'
#final_generate_pdf(trade_df, daily_df, 20100101, end_date, os.path.join(report_path,reportname_2010))
#final_generate_pdf(trade_df, daily_df, 20160101, end_date, os.path.join(report_path,reportname_2016))
#final_generate_pdf(trade_df, daily_df, 20250101, end_date, os.path.join(report_path,reportname_2025))
#generate_basis_std_pdf(basis_ratio_all, std_df, 20100101, end_date, os.path.join(report_path, basis_std_rptname))

flag_path_success = os.path.join(flag_path, 'cta_trend_' + end_date + '.success')
with open(flag_path_success,'w'):
    pass
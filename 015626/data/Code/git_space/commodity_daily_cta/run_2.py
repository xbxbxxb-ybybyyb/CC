import sys
sys.path.insert(4,'/dfs/user/012398/working_code/prod_zhangf/')
import multifactor.utility.dt as dt
from comm_cta_2 import Pos_2
from gen_report import final_generate_pdf
import pandas as pd
import os, time
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
#curdate = pd.Timestamp('20250811')
#update_date = '20250808'

start_date = '20160101'
end_date = update_date
para_date = update_date

res_path = '/data/group/800466/warehouse/prod/tradingstats/Spiral'
para_path = os.path.join(res_path, 'daily_para_2')
pos_path = os.path.join(res_path, 'daily_pos_2')
para_path1 = '/dfs/group/800466/trade/spiral/para2'
report_path = os.path.join(res_path,'report_2')
data_path = os.path.join(res_path,'data_2')

for pa in [res_path, report_path, para_path, para_path1, pos_path, data_path]:
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


commcta = Pos_2(start_date, end_date)
tickerlist = commcta.tickerlist
daily_df, trade_df, sigin_df = commcta.backtest(tickerlist = tickerlist, use_univ = True)
mltip = commcta.multip
univ_data = commcta.univ_data
sharesadj = commcta.sharesadj

print('save data')
daily_df.to_hdf(os.path.join(data_path, 'daily_df_2.h5'),key = 'daily_df')
trade_df.to_hdf(os.path.join(data_path, 'trade_df_2.h5'),key = 'trade_df')
sigin_df.to_hdf(os.path.join(data_path, 'sigin_df_2.h5'),key = 'sigin_df')
mltip.to_csv(os.path.join(data_path,'mult.csv'))
univ_data.to_hdf(os.path.join(data_path, 'univ_data.h5'),key = 'univ')
sharesadj.to_hdf(os.path.join(data_path, 'sharesadj.h5'),key = 'sharesadj')

pos_df = daily_df[['pos']].abs().groupby('dt').sum()
rt_df = daily_df.groupby('dt')[['dailypnl','dailyret']].sum()
res_df = pd.concat([pos_df, rt_df],axis=1).loc['2019':].to_csv(os.path.join(data_path,'daily_ret.csv'))
# gen trading parameters
#daily_df = pd.read_hdf(os.path.join(res_path,'daily_df_fix.h5'))
#trade_df = pd.read_hdf(os.path.join(res_path,'trade_df_fix.h5'))
para_df_fortrade,para_forwind = commcta.get_trade_parameters(para_date, daily_df.loc[pd.Timestamp(para_date)],omit_dce = True)
para_df_fortrade.to_csv(os.path.join(para_path, 'para_'+ curdate.strftime('%Y%m%d') + '.csv'))
para_df_fortrade.to_csv(os.path.join(para_path1, 'para_'+ curdate.strftime('%Y%m%d') + '.csv'))
para_forwind.to_excel(os.path.join(para_path, 'para_forwind2_'+ curdate.strftime('%Y%m%d') + '.xlsx'))

para_df_fortrade_all,para_forwind_all = commcta.get_trade_parameters(para_date, daily_df.loc[pd.Timestamp(para_date)],omit_dce=False)
para_df_fortrade_all.to_csv(os.path.join(para_path, 'para_all_'+ curdate.strftime('%Y%m%d') + '.csv'))
para_forwind_all.to_excel(os.path.join(para_path, 'para_all_forwind2_'+ curdate.strftime('%Y%m%d') + '.xlsx'))

reportname_2019 = 'Commodity_Daily_CTA_report_2_20190101_' + end_date + '.pdf'
reportname_2025 = 'Commodity_Daily_CTA_report_2_20250101_' + end_date + '.pdf'
final_generate_pdf(trade_df, daily_df, 20190101, end_date, os.path.join(report_path,reportname_2019))
final_generate_pdf(trade_df, daily_df, 20250101, end_date, os.path.join(report_path,reportname_2025))

send_file(['012398','015626'],os.path.join(para_path,'para_forwind2_' + curdate.strftime('%Y%m%d') + '.xlsx'))
send_file(['012398','015626'],os.path.join(para_path,'para_all_forwind2_' + curdate.strftime('%Y%m%d') + '.xlsx'))
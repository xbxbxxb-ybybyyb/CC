import sys
sys.path.insert(4,'/dfs/user/012398/working_code/prod_zhangf/')
import multifactor.utility.dt as dt
from trade_parms import Parms
import pandas as pd
import os,time
import datetime
import warnings
warnings.filterwarnings('ignore')
from SEND_FILE import send_file

curdate = dt.get_trading_day_offset(pd.Timestamp(datetime.date.today()),1)[0]
update_date = pd.Timestamp(datetime.date.today()).strftime('%Y%m%d')
#curdate = pd.Timestamp('20250915')
#update_date = '20250912'
start_date = dt.get_trading_day_offset(update_date,-80)[0]
end_date = update_date
para_date = update_date

# trend_path
res_path_trend = '/data/group/800466/warehouse/prod/tradingstats/Spiral/trend_strategy'
para_path_trend = os.path.join(res_path_trend, 'para')
para_path1_trend = '/dfs/group/800466/trade/spiral/para'

# basis_path
res_path_basis = '/data/group/800466/warehouse/prod/tradingstats/Spiral/basis_strategy'
para_path_basis = os.path.join(res_path_basis, 'para')
para_path1_basis = '/dfs/group/800466/trade/spiral/para_basis'

flag_path = os.path.join('/data/group/800466/warehouse/prod/tradingstats/Spiral/other/flag')

def data_flag_check(date):    
    flag1 = os.path.join(flag_path,'cta_trend_' + date + '.success')
    flag2 = os.path.join(flag_path,'cta_basis_' + date + '.success')
    return os.path.exists(flag1) & os.path.exists(flag2)

def holding_pos_check(date):
    #flagpath = '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/FLAG'
    flagpath = '/data/user/011477/Arrow/'
    flagname = str(date) + '_Spiral.xlsx'
    check_path = os.path.join(flagpath, flagname)
    return os.path.exists(check_path)
        
print('------wait strategy flag')
while True:
    if data_flag_check(end_date) & holding_pos_check(end_date):
        break
    time.sleep(60)
print('flag check finished!')

commparms = Parms(start_date, end_date)

daily_df_trend = pd.read_hdf('/data/group/800466/warehouse/prod/tradingstats/Spiral/trend_strategy/data/daily_df_fix.h5').loc[pd.Timestamp(para_date)]
daily_df_basis = pd.read_hdf('/data/group/800466/warehouse/prod/tradingstats/Spiral/basis_strategy/data/daily_df_fix.h5').loc[pd.Timestamp(para_date)]

# gen pnl
df_trend = pd.read_hdf('/data/group/800466/warehouse/prod/tradingstats/Spiral/trend_strategy/data/daily_df_fix.h5')
df_basis = pd.read_hdf('/data/group/800466/warehouse/prod/tradingstats/Spiral/basis_strategy/data/daily_df_fix.h5')
pnl_trend = df_trend.groupby('dt')['dailypnl'].sum()
pnl_basis = df_basis.groupby('dt')['dailypnl'].sum()
pnl_trend.name = 'pnl_trend'
pnl_basis.name = 'pnl_basis'
pnl_total = pd.concat([pnl_trend,pnl_basis],axis=1)
pnl_total.to_csv('/data/group/800466/warehouse/prod/tradingstats/Spiral/pnl_backtest.csv')

para_trend_fortrade, para_trend_forwind, para_basis_fortrade, para_basis_forwind = \
                    commparms.get_trade_parameters_add_true_position(para_date, daily_df_trend, daily_df_basis, get_cfe= False)

para_trend_fortrade_cfe, para_trend_forwind_cfe, para_basis_fortrade_cfe, para_basis_forwind_cfe = \
                    commparms.get_trade_parameters_add_true_position(para_date, daily_df_trend, daily_df_basis, get_cfe = True)
# gen trend parms
para_trend_fortrade.to_csv(os.path.join(para_path1_trend, 'para_'+ curdate.strftime('%Y%m%d') + '.csv'))
para_trend_forwind.to_excel(os.path.join(para_path_trend, 'para_trend_forwind_'+ curdate.strftime('%Y%m%d') + '.xlsx'))
para_trend_forwind_cfe.to_excel(os.path.join(para_path_trend, 'para_trend_cfe_forwind_'+ curdate.strftime('%Y%m%d') + '.xlsx'))

# gen basis parms
para_basis_fortrade.to_csv(os.path.join(para_path1_basis, 'para_basis_'+ curdate.strftime('%Y%m%d') + '.csv'))
para_basis_forwind.to_excel(os.path.join(para_path_basis, 'para_basis_forwind_'+ curdate.strftime('%Y%m%d') + '.xlsx'))
para_basis_forwind_cfe.to_excel(os.path.join(para_path_basis, 'para_basis_cfe_forwind_'+ curdate.strftime('%Y%m%d') + '.xlsx'))

send_file(['012398','015626'],os.path.join(para_path_trend,'para_trend_forwind_' + curdate.strftime('%Y%m%d') + '.xlsx'))
send_file(['012398','015626'],os.path.join(para_path_trend,'para_trend_cfe_forwind_' + curdate.strftime('%Y%m%d') + '.xlsx'))
send_file(['012398','015626'],os.path.join(para_path_basis,'para_basis_forwind_' + curdate.strftime('%Y%m%d') + '.xlsx'))
send_file(['012398','015626'],os.path.join(para_path_basis,'para_basis_cfe_forwind_' + curdate.strftime('%Y%m%d') + '.xlsx'))
import sys
sys.path.insert(4,'/dfs/user/012398/working_code/prod_zhangf/')
import multifactor.utility.dt as dt
from comm_cta_5 import Pos_5
from gen_report import final_generate_pdf
import pandas as pd
import os, time
import datetime
import warnings
warnings.filterwarnings('ignore')
from SEND_FILE import send_file

curdate = pd.Timestamp('20250812')
update_date = '20250811'

start_date = '20100101'
end_date = update_date
para_date = update_date

res_path = '/data/group/800466/warehouse/prod/tradingstats/Spiral'
para_path = os.path.join(res_path, 'daily_para_5')
pos_path = os.path.join(res_path, 'daily_pos_5')
#para_path1 = '/dfs/group/800466/trade/spiral/para2'
report_path = os.path.join(res_path,'report_5')
data_path = os.path.join(res_path,'data_5')

for pa in [res_path, report_path, para_path, pos_path, data_path]:
    if not os.path.exists(pa):
        os.makedirs(pa)

commcta = Pos_5(start_date, end_date)
tickerlist = commcta.tickerlist
#basis_ratio_all = commcta.calc_basis_ratio_all(start_date,end_date)
#basis_ratio_all.to_hdf(os.path.join(data_path, 'basis_ratio.h5'),key = 'basis_ratio')
basis_ratio_all = pd.read_hdf('/data/group/800466/warehouse/prod/tradingstats/Spiral/data_5/basis_ratio.h5')
daily_df, trade_df, sigin_df = commcta.backtest(tickerlist,basis_ratio_all,use_univ = True)
mltip = commcta.multip
univ_data = commcta.univ_data
sharesadj = commcta.sharesadj

print('save data')
daily_df.to_hdf(os.path.join(data_path, 'daily_df.h5'),key = 'daily_df')
trade_df.to_hdf(os.path.join(data_path, 'trade_df.h5'),key = 'trade_df')
sigin_df.to_hdf(os.path.join(data_path, 'sigin_df.h5'),key = 'sigin_df')
mltip.to_csv(os.path.join(data_path,'mult.csv'))
univ_data.to_hdf(os.path.join(data_path, 'univ_data.h5'),key = 'univ')
sharesadj.to_hdf(os.path.join(data_path, 'sharesadj.h5'),key = 'sharesadj')
pos_df = daily_df[['pos']].abs().groupby('dt').sum()
rt_df = daily_df.groupby('dt')[['dailypnl','dailyret']].sum()
res_df = pd.concat([pos_df, rt_df],axis=1).loc['2010':].to_csv(os.path.join(data_path,'daily_ret.csv'))

#reportname_2019 = 'Commodity_Daily_CTA_report_5_in(ma,std,basis)_out(turtle,std,dailyret)_20190101_' + end_date + '.pdf'
#reportname_2016 = 'Commodity_Daily_CTA_report_5_in(ma,std,basis)_out(turtle,std,dailyret)_20160101_' + end_date + '.pdf'
reportname_2010 = 'Commodity_Daily_CTA_report_5_in(ma,std,basis_uplow8_mean5)_out(turtle,std,dailyret)_20100101_' + end_date + '.pdf'
#final_generate_pdf(trade_df, daily_df, 20190101, end_date, os.path.join(report_path,reportname_2019))
#final_generate_pdf(trade_df, daily_df, 20160101, end_date, os.path.join(report_path,reportname_2016))
final_generate_pdf(trade_df, daily_df, 20100101, end_date, os.path.join(report_path,reportname_2010))


from multifactor.backtest.factor_test import SingleFactorTest
from multifactor.IO import IO
from multifactor.IO.IO_enums import *


sdate,edate = 20170101,20180701

# factor_path = r'W:\guozj\stacking\h5_file\20190401_LR_base4.h5'
factor_path = '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5'
result_folder = '/data/user/013160/debug_single_factor/'

factor_data = IO.read_data([sdate,edate],columns=['close'],alt=factor_path)
sft = SingleFactorTest(sdate, edate, universe='alpha_universe', holding_period=1,benchmark='alpha_universe',
                        transaction_cost=0.002,segment_number=20,seg_by_industry=False,
                        ret_price='vwap',ret_shift=True)
sft.load_factor(factor_data=factor_data,name=factor_data.columns[0])
sft.shoot(result_folder=result_folder)


                 

# @Time : 2022/2/23 14:57
# @Author : Zhichen Lu
# @File : reload_barra_factor.py
from dataApi.getData import get_daily_1factor,trans_windcode2int
from dataApi.tradeDate import get_date_range
from dataApi.stockList import get_all_stock_ever_appear
from tqdm import tqdm
import pandas as pd
import os

BARRA_FACTOR_PATH = '/data/group/800442/800319/junkData/BarraFactor/'

barra_factor = ['Beta', 'BookToPrice', 'DividendYield', 'EarningsQuality', 'EarningsVariability', 'EarningsYield', 'Growth', 'Industry', 'InvestmentQuality',
                    'Leverage', 'Liquidity', 'LongTermReversal', 'MidCapitalization', 'Momentum', 'Profitability', 'ResidualVolatility', 'Size']
import time
e = time.time()
barra_dim = {}
factor_name = 'Beta'
stk_list = get_all_stock_ever_appear(20220222)
for factor_name in tqdm(barra_factor):
    if os.path.exists(f'{BARRA_FACTOR_PATH}/{factor_name}.h5'):
        continue
    factor = pd.read_hdf('/data/group/800002/basic_data/full/financial_data/RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5',factor_name)[factor_name].unstack()
    factor.columns = factor.columns.map(trans_windcode2int)
    factor.index = factor.index.map(lambda x : int(x.strftime('%Y%m%d')))
    factor = factor.loc[20100104:].reindex(stk_list,axis=1)
    factor.to_hdf(f'{BARRA_FACTOR_PATH}/{factor_name}.h5',factor_name,type='t')

    # check = get_daily_1factor(factor_name,date_list=get_date_range(20140101,20140531),diy_address=BARRA_FACTOR_PATH)
    # check.index[0],check.index[-1]
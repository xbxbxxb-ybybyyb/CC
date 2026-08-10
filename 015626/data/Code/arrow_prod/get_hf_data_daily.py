import numpy as np
import pandas as pd
import datetime
import concurrent.futures
import xquant_data

today = datetime.datetime.today().strftime('%Y%m%d')

dc = pd.read_pickle('/data/user/000072/LYM_STOCKS/stock_universe/daily_universe/universe_all/universe_' + today + '.pkl')
dc = dc[dc.dt == pd.Timestamp(today)].set_index(['dt', 'Ticker'])
#dc = dc[dc.dt >= pd.Timestamp('20230224')]

#dc['selected'] = True
#dc_1 = dc.set_index(['dt', 'Ticker']).unstack().shift(-1).stack().reset_index()
#dc = pd.concat([dc, dc_1]).drop_duplicates()[['dt', 'Ticker']].set_index(['dt', 'Ticker'])


# pa = '/data/user/000072/LYM_STOCKS/data/auction/data/'
#pa = '/arch0/group/800466/warehouse/prod/MD/CHINA_STOCK/'
pa = '/data/group/800466/warehouse/prod/MD/CHINA_STOCK/'

xquant_data.retrieve_level2_by_h5(dc, pa, 'Order_RAW', 24, force_override = False)
xquant_data.retrieve_level2_by_h5(dc, pa, 'Order', 24, force_override = False)
xquant_data.retrieve_level2_by_h5(dc, pa, 'Stock', 24, force_override = False)
xquant_data.retrieve_level2_by_h5(dc, pa, 'Transaction', 24, force_override = False)
import pandas as pd
import numpy as np

info = pd.read_csv('/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/INFO/WIND_CFuturesContPro.csv')
# delete simulation and IB codes
info['EXCHANGE'] = [i.split('.')[1] for i in info['S_INFO_WINDCODE']]
info['sim'] = [len(i.split('-')) for i in info['S_INFO_CODE']]
info['sim2'] = [len(i.split('_')) for i in info['S_INFO_CODE']]
info_select = info[(info['EXCHANGE']!='IB') & (info['sim'] < 2)& (info['sim2'] < 2)]                    
info_select['Ticker'] = info_select['S_INFO_CODE'] + '.' + info_select['EXCHANGE']
info_select['multiplier'] = info_select['S_INFO_PUNIT'].where(np.isnan(info_select['S_INFO_CEMULTIPLIER']),other = info_select['S_INFO_CEMULTIPLIER'])
multip = info_select.groupby('Ticker')[['multiplier']].last()
bllist = ['IFM.CFE','SCTAS.INE']
multip = multip.loc[~multip.index.isin(bllist)]
multip.to_csv('/dfs/group/800466/warehouse/test/CHINA_COMMODITIES/INFO/multiplier.csv')

import pandas as pd
import numpy as np
import os
import IO
from datetime import datetime
from xquant.thirdpartydata.fic_api_data import FicApiData
fad = FicApiData()
totalCount = 74042
resource = "ZX_CONCEPTION"
paramMaps = {}
orderBy = "TRADINGCODE"
rownum = 10000
startrow = 0
#
res = pd.DataFrame()
for i in range(0,int(totalCount/rownum)+1):
    startrow = i*rownum
    print(i,startrow)
    result_dict = fad.get_fic_api_data(resource, paramMaps, startrow=startrow, rownum=rownum,
                                   orderBy=orderBy)
    res_i = pd.DataFrame(result_dict['data'])
    res = res.append(res_i)
res = res[['CONCEPTTYPE','CONCEPTTYPECODE','CONCEPTTYPENAME','ENTRYDATE','TRADINGCODE']]
res.columns = ['themetype','themeID','themeName','entrydate','Ticker']
res['entrydate'] = res['entrydate'].apply(lambda x : datetime.fromtimestamp(x/1000))
res['Ticker'] = res['Ticker'].apply(lambda x : str(x) + '.SH' if str(x).startswith('6') else str(x) + '.SZ')
res['shsz'] = res['Ticker'].apply(lambda x : 0 if x.startswith('8') else 1)
res = res[res['shsz'] == 1]
res.to_pickle('/dfs/user/015585/20240327-同花顺概念热度/file/ths_theme_basicinfo_xquant.pkl')
# md_data
themeID_list = list(set(res['themeID']))
themeID_list.sort()
md_data = IO.read_data([20150701, 20240520],
                      columns=['amt'],
                      alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md_data = pd.DataFrame(index = md_data.index,columns = themeID_list)
date_list = list(set(md_data.index.get_level_values(0)))
date_list.sort()
res_all = pd.DataFrame() # 最终结果，包括dt ticker themeID
# for Ticker,Ticker_df in res.groupby('Ticker'):
for date in date_list:
    res_date = res[res['entrydate'] < date][['themeID','Ticker']]
    res_date['dt'] = date
    res_date = res_date.set_index(['dt','Ticker'])
    res_date.to_pickle('/dfs/user/015585/20240327-同花顺概念热度/file_thsmember/' + date.strftime('%Y%m%d') + '.pkl')
    res_all = res_all.append(res_date)
    print(date,res_all.shape)
res_all.to_pickle('/dfs/user/015585/20240327-同花顺概念热度/file/res_theme_stock_xquant.pkl')
import os
import IO
import shutil
import pandas as pd
import datetime as dt
import multiprocessing
from xquant.factordata import FactorData
import warnings
warnings.filterwarnings("ignore")
s=FactorData()

#初始化参数
parallel_num=20
path='/data/user/018107/Data_Week/'
path_block=path+'BlockData/'
DATE_MAX='20991231'
begin_date='20220101'
now_date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]
if os.path.exists(path_block):
    shutil.rmtree(path_block)
os.makedirs(path_block)
os.makedirs(path_block+'each_block/')



#读取指数成分股数据
member0=s.get_factor_value('WIND_AIndexMembersWIND', S_CON_INDATE='<20200101', F_INFO_WINDCODE="like'884%'")#进出记录需要取全部时间区间，数量超过上限分为两部分。
#member1=s.get_factor_value('WIND_AIndexMembersWIND', S_CON_INDATE='>=20200101', F_INFO_WINDCODE="like'884%'")
member1=s.get_factor_value('WIND_AIndexMembersWIND', S_CON_INDATE=['>=20200101', '<20220101'], F_INFO_WINDCODE="like'884%'")
member2=s.get_factor_value('WIND_AIndexMembersWIND', S_CON_INDATE='>=20220101', F_INFO_WINDCODE="like'884%'")
wind_member=pd.concat([member0,member1,member2],ignore_index=True)
wind_member['S_CON_OUTDATE']=wind_member['S_CON_OUTDATE'].fillna(DATE_MAX) #如果未调出，为缺失值，替换为极大值
wind_member=wind_member[['F_INFO_WINDCODE', 'S_CON_WINDCODE', 'S_CON_INDATE', 'S_CON_OUTDATE', 'OPDATE']].astype(str)
wind_member.columns=['block', 'Ticker', 'indt', 'outdt', 'opdt']
wind_member=wind_member[wind_member['Ticker'].str.endswith(('.SZ','.SH'))]
wind_member=wind_member[wind_member['Ticker'].str.startswith(('0','3','6'))]
for dtcol in ['indt', 'outdt', 'opdt']:
   wind_member[dtcol]=pd.to_datetime(wind_member[dtcol])
#wind_member.to_pickle(path_block + 'wind_member.pkl')


#获取交易日期列表
date_df=pd.DataFrame()
date_df['dt']=s.tradingday(begin_date, now_date)
date_df['dt']=pd.to_datetime(date_df['dt'])

#读取股票基本资料中的退市时间
AShareDescription=s.get_factor_value('WIND_AShareDescription')
AShareDescription['S_INFO_DELISTDATE']=pd.to_datetime(AShareDescription['S_INFO_DELISTDATE'].fillna(DATE_MAX))
AShareDescription.set_index('S_INFO_WINDCODE',inplace=True)
AShareDescription.loc['689009.SH','S_INFO_DELISTDATE']=pd.to_datetime(DATE_MAX)


#获取指数发布日期
AIndexDescription0=s.get_factor_value('WIND_AIndexDescription',S_INFO_WINDCODE="like'884%'")
AIndexDescription0=AIndexDescription0[['S_INFO_WINDCODE', 'S_INFO_LISTDATE']]
AIndexDescription0.columns=['block','list_dt']
AIndexDescription0['list_dt']=pd.to_datetime(AIndexDescription0['list_dt'])
AIndexDescription0.set_index('block',inplace=True)

#根据指数k线图计算发布日期
ccpt_daily_data = s.get_factor_value('WIND_AIndexWindIndustriesEOD',TRADE_DT=['>='+begin_date,'<='+now_date],S_INFO_WINDCODE="like'884%'")
ccpt_daily_data=ccpt_daily_data[(ccpt_daily_data['S_DQ_HIGH']-ccpt_daily_data['S_DQ_LOW'])>0][['TRADE_DT','S_INFO_WINDCODE']]
ccpt_daily_data.columns=['dt','block']
ccpt_daily_data['dt']=pd.to_datetime(ccpt_daily_data['dt'])
AIndexDescription=ccpt_daily_data.sort_values(['block','dt']).groupby('block')[['dt']].first()
AIndexDescription.columns=['list_dt']

#并行化生成板块数据
def run_block_data_parallel(block):
    member = wind_member[wind_member['block'] == block]
    d_list = []
    for i in range(len(member)):
        Ticker = member.iloc[i]['Ticker']
        indate = member.iloc[i]['indt']
        outdate = member.iloc[i]['outdt']
        d = date_df[date_df['dt'] > indate]
        d = d[d['dt'] <= outdate]
        d = d[d['dt'] <= AShareDescription.loc[Ticker, 'S_INFO_DELISTDATE']]  # 把股票退市后的数据删掉
        d['Ticker'] = Ticker
        d_list.append(d)
    block_member = pd.concat(d_list, ignore_index=True).drop_duplicates()
    block_member[block] = 1

    # 删除指数发布前的日期
    if block in AIndexDescription.index:
        list_dt = AIndexDescription.loc[block, 'list_dt']
    elif block in AIndexDescription0.index:
        list_dt = AIndexDescription0.loc[block, 'list_dt']
    else:
        print('Warning Miss ' + block)
        list_dt = member['opdt'].min()
    block_member = block_member[block_member['dt'] >= list_dt]

    # 保存数据
    if len(block_member) > 0:
        block_member.set_index(['dt', 'Ticker'], inplace=True)
        block_member.to_pickle(path_block + 'each_block/' + block + '.pkl')

pool = multiprocessing.Pool(parallel_num)
factor_parallel = pool.map(run_block_data_parallel, wind_member['block'].unique())
pool.close()
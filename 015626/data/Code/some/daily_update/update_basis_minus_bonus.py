import json,datetime,os,glob
from multiprocessing.pool import Pool
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
from multifactor.data.utils import *
import numpy as np
pd.set_option('max_columns', 200)
import glob
import bottleneck as bk
from tqdm import tqdm

# 获取各个合约的终止日期
def get_contract_end_dt():
    from xquant.factordata import FactorData
    s = FactorData()
    contract_end_dt = s.get_factor_value('WIND_CFuturesDescription', FS_INFO_SCCODE=['IF'])
    contract_end_dt = contract_end_dt[['S_INFO_CODE','S_INFO_DELISTDATE']].dropna().rename(columns = {'S_INFO_CODE':'contract','S_INFO_DELISTDATE':'end_dt'})
    contract_end_dt['contract'] = contract_end_dt.contract.apply(lambda x:int(x[2:6]))
    contract_end_dt['end_dt'] = pd.to_datetime(contract_end_dt['end_dt'])
    return contract_end_dt.set_index('contract').sort_index()

# 获取每天的4个合约
def get_contract_everyday():
    
    def get_contract_everyday_help(g):
        alist = [int(x[2:6]) for x in g.index.get_level_values(1).unique().tolist()]
        alist.sort()
        return pd.DataFrame(alist).T
    
    df1 = IO.read_data(select_str='PROD_ID == "IF.CFE"', columns = ['PROD_ID'], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_SIF_TICK_TO_MINUTE_ALL_CONTRACT.h5')
    df1 = df1.groupby(df1.index.get_level_values(0).date).apply(lambda x:get_contract_everyday_help(x)).reset_index(level = 1, drop = True)
    df1.index.name = 'dt'
    df1.index = pd.to_datetime(df1.index)
    return df1

# 获取每天进行计算的三个合约
def get_tri_contract():
    contract_end_dt = get_contract_end_dt()
    contractdf = get_contract_everyday()

    contract_end_dt = contract_end_dt.reset_index().rename(columns = {'contract':0})
    contractdf = pd.merge(contractdf.reset_index(), contract_end_dt, on = [0], how = 'left')

    contractdf['expiration_days'] = contractdf.apply(lambda x:len(udt.get_trading_date_range(x['dt'], x['end_dt'])), axis = 1)

    contractdf_v1 = contractdf[contractdf.expiration_days > 5]
    contractdf_v2 = contractdf[contractdf.expiration_days <= 5]

    tri1 = contractdf_v1[~(contractdf_v1[1]%100).isin([3,6,9,12])][['dt',0,2,3]]
    tri2 = contractdf_v1[(contractdf_v1[1]%100).isin([3,6,9,12])][['dt',0,1,2]]
    tri2.columns = ['dt',0,2,3]
    tri3 = contractdf_v2[['dt',1,2,3]]
    tri3.columns = ['dt',0,2,3]
    return tri1.append(tri2).append(tri3).set_index('dt').sort_index()

# 获取每天的分红点数 包含准确的h5以及进行预测的excel
def get_div_everyday():
    pathlist = glob.glob('/data/user/015626/data/share/IndexDividends/IndexDividends_*.xlsx')
    pathlist.sort(reverse=True)
    i = 0
    # excel有的时候会有问题，所以判断excel中是否有数据
    while True:
        excel_dict = pd.read_excel(pathlist[i], sheet_name=None)
        if len(excel_dict.keys()) >= 6:
            break
        else:
            i = i + 1
            
    year_flag = datetime.datetime.now().year + 1
    div_dict = {'ZZ500_details':'IC.CFE','HS300_details':'IF.CFE','SH50_details':'IH.CFE',
               'ZZ500_details_%d' % year_flag:'IC.CFE', 'HS300_details_%d' % year_flag:'IF.CFE', 'SH50_details_%d' % year_flag:'IH.CFE'}
    div_pred = pd.DataFrame()
    for k, v in div_dict.items():
        if k in excel_dict.keys():
            key_div = excel_dict[k]
            key_div = key_div.groupby('exrights_exdividend_date')['point'].sum().to_frame().reset_index()
            key_div.columns = ['dt','divpoint']
            key_div['Ticker'] = v
            key_div['dt'] = pd.to_datetime(key_div['dt'].astype('str'))
            key_div = key_div.set_index(['dt','Ticker'])
            div_pred = div_pred.append(key_div)

    everyday_h5 = IO.read_data(columns = ['divpoint'], alt = '/data/user/015626/data/share/IndexDividends/details/IndexDividends_Details.h5')
    everyday_h5 = everyday_h5.append(div_pred.loc[~div_pred.index.isin(everyday_h5.index)].sort_index())
    return everyday_h5

# 获取三个合约从当日起存续期内的分红点数
def get_tridiv():
    # 获取每个合约的结束日期
    tri = get_tri_contract()
    tri = tri.stack().reset_index(level = 1, drop = True).to_frame()
    tri.columns = ['contract']
    tri = tri.reset_index().set_index(['contract'])
    contract_end_dt = get_contract_end_dt()
    tridiv = tri.join(contract_end_dt, how = 'left')
    tridiv = tridiv.reset_index().sort_values(by = ['dt','contract'])
    
    # 计算每个合约当日起始的存续期内的分红点数
    everyday_h5 = get_div_everyday()
    for t in ['IC.CFE','IF.CFE','IH.CFE']:
        temp = everyday_h5.xs(t, level = 1)
        temp.loc[pd.to_datetime('20110104'),'divpoint'] = 0
        temp = temp.sort_index()
        for x in tridiv.index:
            tridiv.loc[x, t] = temp.loc[tridiv.loc[x]['dt'] : tridiv.loc[x]['end_dt']].sum()['divpoint']
    tridiv = tridiv.sort_values(['dt','contract']).set_index(['dt','contract'])
    return tridiv

def get_month_diff(a0, a1):
    assert a0 < a1
    y0 = a0 // 100
    y1 = a1 // 100
    if y0 == y1:
        return a1 - a0
    else:
        return 12 - a0 % 100 + a1 % 100
        
def get_spread(a):
#     jiacha1 = (a.iloc[2]['close_minus_div'] - a.iloc[1]['close_minus_div']) / get_month_diff(a.iloc[1]['contract'], a.iloc[2]['contract'])
    jiacha2 = (a.iloc[1]['close_minus_div'] - a.iloc[0]['close_minus_div']) / get_month_diff(a.iloc[0]['contract'], a.iloc[1]['contract'])
    return jiacha2

def get_close_minus_div():
    #获取三个合约从当日起存续期内的分红点数
    tridiv = get_tridiv()
    tridiv.to_pickle('/data/user/015626/data/share/MD/CHINA_FUTURES/daily/basis_without_bonus/tridiv.pkl')
    # 读取期货分钟数据
    allminute = IO.read_data(columns=['close','PROD_ID'], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_SIF_TICK_TO_MINUTE_ALL_CONTRACT.h5')
    allminute = allminute.reset_index(level = 1)
    allminute = allminute.between_time(datetime.time(9,30), datetime.time(14,49))
    allminute['contract'] = allminute.Ticker.apply(lambda x:int(x[2:6]))

    result_list = []
    for ticker in ['IC.CFE','IF.CFE','IH.CFE']:
        mdf = allminute[allminute.PROD_ID == ticker]
        mdf = mdf[['contract','close']].reset_index().set_index(['dt','contract'])
        
        mdiv = tridiv[[ticker]]
        mdiv.columns = ['div_points']
        mdiv = mdiv.unstack().reindex(mdf.index.get_level_values(0).unique(), method = 'pad').stack()
        df = mdiv.join(mdf, how = 'left')
        # 期货收盘价扣除分红 应该是加 ！！！
        df['close_minus_div'] = df['close'] + df['div_points']
        
        spreaddf = df.reset_index(level = 1)[['contract','close_minus_div']].groupby('dt').apply(lambda x:get_spread(x))
        ddf = spreaddf.groupby(spreaddf.index.date).mean().to_frame()
        ddf.columns = [ticker]
        ddf.index.name = 'dt'
        ddf.index = pd.to_datetime(ddf.index)
        result_list.append(ddf)
    
    result = pd.concat(result_list, axis = 1)
    return result

def run():
    # 计算基差
    ddf = get_close_minus_div()
    ddf = ddf.stack().to_frame()
    ddf.columns = ['basis_minus_bonus']
    ddf.index.names = ['dt','Ticker']
    
    # 读取现货数据
    spot = IO.read_data(columns = ['close_spot'], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_STOCK_INDEX_SPOT_MINUTE.h5')
    spot = spot.unstack()
    spot = spot.at_time(datetime.time(14,49))
    spot.index = pd.to_datetime(spot.index.date)
    spot = spot.stack()
    spot.index.names = ['dt','Ticker']

    # 计算比率
    newdf = ddf.join(spot, how = 'left')
    newdf['basis_minus_bonus_ratio'] = newdf.basis_minus_bonus / newdf.close_spot
    
    h5_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/basis_without_bonus/basis_without_bonus.h5'
    
    if os.path.exists(h5_path):
        IO.pd_hdf5_writer(newdf, h5_path, dataset='basis_without_bonus', override=True)
    else:
        IO.pd_hdf5_writer(newdf, h5_path, dataset='basis_without_bonus')

def minute_flag_check(date):
    path1 = '/data/group/800080/warehouse/prod/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_MINUTE.success'
    path3 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_spot_minute.success'
    return os.path.exists(path1) and os.path.exists(path3)

print('start')     

sdate,flag_date,cdate_list = check_update_date()


print('------wait minute flag')
while True:
    if minute_flag_check(flag_date):
        break
    time.sleep(60)
print('flag check finished!')
   
run()
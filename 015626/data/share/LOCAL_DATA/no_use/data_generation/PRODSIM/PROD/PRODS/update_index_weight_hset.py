'''
if reload history data, you should remove csv in SH50 by hand first.
weiych
warning: 本代码中hset接口获取的是前一日对本日的权重的预测
'''


from xquant.factordata import FactorData
s = FactorData()
from multifactor.IO import IO
import pandas as pd

from multifactor.IO import IO
from multifactor.data.utils import *
import time
import os
import multifactor.utility.dt as udt
from xquant.compute.aimr import AIMR


ROOT_PATH = '/data/group/800466/warehouse/prod/MD/MarketData/'

def get_next_trading_date(date):
    return str(udt.get_trading_day_offset(date, 1)[0])[:10].replace('-','')
    
def retriver(cdate_list, index_list, csv_path):
#    namedict = {'HS300':'index_weight_hs300','SH50':'index_weight_sh50','ZZ500':'index_weight_zz500'}
    for date in cdate_list:
        next_trading_date = get_next_trading_date(date)
        date = str(date)
        for index in index_list:
            df = s.hset('INDEX', next_trading_date, index, weightType = 1)
            if len(df) == 0:
                continue
            df = df.reset_index()[['stock','weight']]
            df = df.rename(columns = {'stock':'Ticker','weight':index})
            df = df.set_index('Ticker')
            if not os.path.exists(os.path.join(csv_path,index)):
                os.makedirs(os.path.join(csv_path,index))
            df.to_csv(csv_path + index + '/' + date + '.csv')
            print(index, ' ', date, '  retriver done')
    
    
def update_universe_raw(cdate_list,csv_path,h5_path,factor_list,operation='append'):
    weight_list = ['index_weight_sh50','index_weight_hs300','index_weight_zz500']
    dump_list = [str(i) + '.csv' for i in cdate_list]
    pre_cwd = os.getcwd()
    df_list = []
    for date in cdate_list:
        tmp_list = []
        df = get_stock_list(date)
        df.reset_index(inplace=True)
        df['dt'] = dt.datetime.strptime(str(date),'%Y%m%d')
        df.set_index(['dt','Ticker'],inplace=True)
        tmp_list.append(df)
        for factor_name in factor_list:
            if factor_name == 'SH50':
                weight_name = 'index_weight_sh50'
                bool_name = 'index_50'
            elif factor_name == 'ZZ500':
                weight_name = 'index_weight_zz500'
                bool_name = 'index_500'
            elif factor_name == 'HS300':
                weight_name = 'index_weight_hs300'
                bool_name = 'index_300'

            if factor_name == 'SH50' and date < 20100101:
                continue
            fname = csv_path+factor_name+'/'+str(date)+'.csv'
            dat = pd.read_csv(fname)
            dat['dt'] = dt.datetime.strptime(str(date),'%Y%m%d')
            dat.set_index(['dt','Ticker'],inplace=True)
            dat.columns = [weight_name]
            dat = pd.concat([df,dat],axis=1)
            dat.fillna(0,inplace=True)
            # dat[bool_name] = dat[weight_name] > 0
            dat[weight_name] = dat[weight_name] / 100.0

            if len(dat)>0:
                tmp_list.append(dat[[weight_name]])


        df = pd.concat(tmp_list,axis=1)

        for col in weight_list:
            if col not in df.columns:
                continue
            df[col].fillna(0,inplace=True)
        df_list.append(df)
    df = pd.concat(df_list)
    print(df)
    for colume in df.columns:
        if colume == 'alla':
            continue
        if operation == 'append':
            IO.pd_hdf5_writer(df[[colume]],h5_path,dataset=colume,append=True)
        else:
            IO.pd_hdf5_writer(df[[colume]],h5_path,dataset=colume)

def get_stock_list(date):
    df = s.get_factor_value('WIND_AShareDescription',factors = ['S_INFO_WINDCODE','S_INFO_LISTDATE', 'S_INFO_DELISTDATE']) 
    df = df.rename(columns = {'S_INFO_WINDCODE':'Ticker'}).set_index('Ticker').sort_index().fillna(20990101).astype('int')
    tmp_df = df[df['S_INFO_DELISTDATE'] > date]
    tmp_df = tmp_df[tmp_df['S_INFO_LISTDATE'] <= date]
    tmp_df['alla'] = True
    tmp_df = tmp_df[['alla']]
    return tmp_df            
#def get_stock_list(date):
#    table_name = 'AShareDescription'
#    h5_path = '/data/group/800080/warehouse/prod/DATABASE/WIND/'
#    table_path = h5_path + table_name + '/' +  table_name + '.h5'
#    df = IO.read_data([20090101,21000101],columns=['S_INFO_LISTDATE', 'S_INFO_DELISTDATE'],alt = table_path)
#    df.reset_index('dt', inplace=True)
#    df.drop('dt', axis=1, inplace=True)   
#    df.fillna(20990101, inplace = True)

#    tmp_df = df[df['S_INFO_DELISTDATE'] > date]
#    tmp_df = tmp_df[tmp_df['S_INFO_LISTDATE'] <= date]
#    tmp_df['alla'] = True
#    tmp_df = tmp_df[['alla']]
#    return tmp_df

if __name__ == '__main__':

    #args = AIMR.getParam().split(',')

    #start_date, end_date = '20210922', '20210922'
    #a, b, c = check_update_date()
    sdate, edate, cdate_list = check_update_date()

    flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'
    end_date = edate
    
    flag_root = flag_rootpath + str(end_date) + '/'
    
    print('wait_minute_flag')
    
    flag_check_path = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/' + str(end_date) + '/' + str(end_date)+'_' + 'INDEX.success'
    while True:
        if os.path.exists(flag_check_path) == True:
            print('start')
            break
        time.sleep(60)
    csv_path = '{}/LOCAL_DATA/CSV/stock_universe/'.format(ROOT_PATH)
    h5_path_source = '{}/MD/UNIVERSE/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5'.format(ROOT_PATH)
    factor_list = ['HS300', 'ZZ500', 'SH50']

    fileflag = True
    while fileflag:
        retriver(cdate_list, factor_list, csv_path)
        if os.path.exists(csv_path + 'SH50' + '/' + str(cdate_list[-1]) + '.csv'):
            print('retriver finish!')
            fileflag = False
        else:
            print('file not retriver!')
            time.sleep(300)

    
    update_universe_raw(cdate_list,csv_path,h5_path_source,factor_list,operation='append')

    print('h5 is done.')
    yesterday = str(udt.get_trading_day_offset(end_date, -1)[0])[:10].replace('-','')
    weight_sum = IO.read_data([yesterday, end_date], alt = '/data/group/800466/warehouse/prod/MD/MarketData/MD/UNIVERSE/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5').loc[str(end_date)].sum()
    wsall = abs(weight_sum - 1 ).sum()
    if wsall < 0.001:
        
        flag_path_success = flag_root + str(end_date) + '_' + 'WEIGHT.success'
        with open(flag_path_success,'w') as file:
            pass
    else:
        from xquant.xqutils.helper import link
        lm = link.LinkMessage()
        lm.sendMessage(str(list(weight_sum)))
        del lm
        
        
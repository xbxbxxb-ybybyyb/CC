import os
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from multifactor.data.utils import *
import multifactor.utility.dt as udt
import numpy as np
pd.set_option('max_columns', 200)
import json
from xquant.xqutils.helper import link
from xquant.investment.strategyfile import *


def included(A, B):
    for item in A:
        if item not in B:
            print(item)
            return False
    return True

def minute_flag_check(date):
    flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'
    path = flag_rootpath + str(date) + '/' + 'trade_files.success'
    return os.path.exists(path) 



def CHECK(path = None, cat = 'IC'):
    ERROR_LIST = []
    if path == None:        
        _,date,_ = check_update_date()        
        while True:
            if minute_flag_check(date):
                break
            time.sleep(60)
        print('flag check finished!')
        
        next_date = udt.get_trading_day_offset(str(date),1)[0].strftime('%Y%m%d')
        default_path = '/data/user/016700/Data/para/Mobius_%s/MobiusStrategy_%s_%s.xlsx'%(next_date, cat.upper(), next_date)
        if '_IC' in default_path:
            machine = '#503301'
        elif '_IF' in default_path:
            machine = '#503302'
        elif '_IM' in default_path:
            machine = '#503303'
        savepath = os.path.join('/data/user/016700/Data/para/', 'Mobius_' + str(next_date))
        para_path = (os.path.join(savepath, 'MobiusStrategy_%s.xlsx' % (cat.upper() + '_' +str(next_date) + machine)))
        IBP = pd.read_excel(default_path.replace('.xlsx', machine + '.xlsx'), sheetname = 'InitialBasicParam')
        MPZ = pd.read_excel(default_path.replace('.xlsx', machine + '.xlsx'), sheetname = '信号模型配置列表')
        QCCC = pd.read_excel(default_path.replace('.xlsx', machine + '.xlsx'), sheetname = '期初持仓列表')
        CSLB = pd.read_excel(default_path.replace('.xlsx', machine + '.xlsx'), sheetname = '信号到仓位配置参数')
        ZZ500 = pd.read_excel(default_path.replace('.xlsx', machine + '.xlsx'), sheetname = '中证500成分股收盘价信息')
        HS300 = pd.read_excel(default_path.replace('.xlsx', machine + '.xlsx'), sheetname = '沪深300成分股收盘价信息')
    else:    
        para_path = path
        IBP = pd.read_excel(path, sheetname = 'InitialBasicParam')
        MPZ = pd.read_excel(path, sheetname = '信号模型配置列表')
        QCCC = pd.read_excel(path, sheetname = '期初持仓列表')
        CSLB = pd.read_excel(path, sheetname = '信号到仓位配置参数')
        ZZ500 = pd.read_excel(path, sheetname = '中证500成分股收盘价信息')
        HS300 = pd.read_excel(path, sheetname = '沪深300成分股收盘价信息')
        next_date = str(IBP['交易日期'].iloc[0])
        date = udt.get_trading_day_offset(str(next_date),-1)[0].strftime('%Y%m%d')
        if cat != None:
            cat = path.split('/')[-1].split('.')[-2].split('_')[-2]
        else:
            pass
    jyzh = str(IBP['买入交易账户'].iloc[0])
    if not os.path.exists(IBP['行情分钟数据目录'].iloc[0]):
        ERROR_LIST.append(['InitialBasicParam - 盘前数据路径不存在'])
    if len(os.listdir(IBP['行情分钟数据目录'].iloc[0])) != 21:
        ERROR_LIST.append(['InitialBasicParam - 盘前数据文件数量有误'])

    if not os.path.exists(IBP['历史因子文件目录'].iloc[0]):
        ERROR_LIST.append(['InitialBasicParam - 历史因子文件目录不存在'])
    if not os.path.exists(IBP['因子配置文件'].iloc[0]):
        ERROR_LIST.append(['InitialBasicParam - 因子配置文件不存在'])

    with open(IBP['因子配置文件'].iloc[0], 'r') as openfile:
        json_object = json.load(openfile)
    name_holder = [item['FactorName'] for item in json_object]  
    for path in MPZ['对应模型目录']:
        temp = list(pd.read_csv(path + 'factor_name_mapping.csv')['factor_name'])
        dummies_list = [item[:-3] for item in os.listdir('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/dummies/minute_norm/')]
        dummies_list2 = [item[:-3]+'.0' for item in os.listdir('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/dummies/minute_norm/')]
        temp = list(set(temp) - set(dummies_list)- set(dummies_list2))
        if not included(temp, name_holder):
            ERROR_LIST.append(['InitialBasicParam - json因子不足'])

    if not list(IBP['买入交易账户']) == list(IBP['卖出交易账户']):
        ERROR_LIST.append(['买卖交易账户不一致'])

    if not ((len(MPZ) == MPZ['信号编号'].iloc[-1]) and (len(set(MPZ['信号编号'])) == len(MPZ))):
        ERROR_LIST.append(['信号模型配置列表 - 信号编号数字错误'])

    for item in list(MPZ['对应模型目录']):
        if not os.path.exists(item):
            ERROR_LIST.append(['信号模型配置列表 - 模型目录不存在'])
    for item in list(MPZ['历史信号文件目录']):
        if not os.path.exists(item):
            ERROR_LIST.append(['信号模型配置列表 - 历史信号文件目录不存在'])
        else:
            for file in os.listdir(item):
                if (os.path.getsize(item + '/' + file)) == 0:
                    ERROR_LIST.append(['信号模型配置列表 - 历史信号文件目录存在空值文件'])
    for item in list(MPZ['初始资金（千万元）']):
        if not int(item) <= 100:
            ERROR_LIST.append(['信号模型配置列表 -初始资金潜在错误']) 
    for item in list(MPZ['波动率时间窗口']):
        if not int(item) <= 30:
            ERROR_LIST.append(['信号模型配置列表 - 波动率时间窗口潜在错误']) 
    
    for i, path in enumerate(list(MPZ['历史信号文件目录'])):   
        if path.split('/')[-1] == 'historySignal':
            if MPZ['Rank计算方法'][i] != 'norm':
                ERROR_LIST.append(['信号到仓位配置参数 - 信号%s: 对应标准化方法（norm, norm2）不匹配'%(str(i))])
        elif path.split('/')[-1] == 'signalNorm2Value':
            if MPZ['Rank计算方法'][i] != 'norm2':
                ERROR_LIST.append(['信号到仓位配置参数 - 信号%s: 对应标准化方法（norm, norm2）不匹配'%(str(i))])
        else:
            pass
    

    
    dfff = pd.read_excel('/data/user/011477/order/tradingReport/tradingStat_%s.xlsx'%date, sheet_name='Tri_51606')#.set_index('委托方向')
    l = dfff['组合名称']
    l = [item for item in l if (('mobius' in item.lower()) & (jyzh in item)) | (('hongye' in item.lower()) & (jyzh in item))][0]
    positions = dfff[dfff['组合名称'] == l]['期货持仓'].iloc[0]
    dic_temp = json.loads(positions.replace("'", '"'))
    
                    
    if not ((len(QCCC) == QCCC['平仓优先级'].iloc[-1]) and (len(set(list(QCCC['平仓优先级']))) == len(QCCC))):
        ERROR_LIST.append(['期初持仓列表 - 平仓优先级编号数字错误'])

    #if not QCCC['多头持仓'].sum() == QCCC['空头持仓'].sum():
    #    ERROR_LIST.append(['期初持仓列表 - 多空持仓数量潜在错误'])
    
    

    sig_no_list = list(set(CSLB['所属信号编号'].astype(int)))
    if not sig_no_list == list(set(MPZ['信号编号'].astype(int))):
        ERROR_LIST.append(['信号到仓位配置参数/信号模型配置列表 - 信号编号不匹配'])
    if len(ERROR_LIST) ==0:
        for i in sig_no_list:

            temp_para = CSLB[CSLB['所属信号编号'] == i].reset_index(drop = True)
            for j in range(len(temp_para)):

                if j >0:
                    cur = temp_para.iloc[j]
                    pre = temp_para.iloc[j-1]
                    if not (pre['信号右边界'] == cur['信号左边界']):
                        ERROR_LIST.append(['信号到仓位配置参数 - 信号%s: 信号阈值不一致，出现在第%s和第%s行'%(str(i), str(j-1), str(j))])


            #if not int((temp_para['仓位右边界'].sum() - temp_para['仓位左边界'].sum()) / temp_para['仓位右边界'].iloc[-1]) == (temp_para['仓位左边界'] == 0).sum() - (temp_para['仓位右边界'] == 0).sum():
            #    ERROR_LIST.append(['信号到仓位配置参数 - 信号%s: 仓位阈值不一致'%(str(i))])

            vol_window = MPZ[MPZ['信号编号'] == temp_para['所属信号编号'].iloc[0]]['波动率时间窗口'].iloc[0]
            if vol_window == 0:
                if temp_para['信号右边界'].iloc[0] <0.01:
                     ERROR_LIST.append(['信号到仓位配置参数 - 信号%s: 对应波动率窗口的参数有潜在错误'%(str(i))])
            if vol_window > 0:
                if temp_para['信号右边界'].iloc[0] >0.01:
                     ERROR_LIST.append(['信号到仓位配置参数 - 信号%s: 对应波动率窗口的参数有潜在错误'%(str(i))])
    else:
        pass

    if len(ZZ500) != 500:
        weightdf = IO.read_data([date, next_date], alt = '/data/group/800466/warehouse/prod/MD/MarketData/MD/UNIVERSE/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5').droplevel(0)
        list_500 = list(weightdf[weightdf['index_weight_zz500']!= 0].index)
        missing_500 = list(set(list_500) - set(ZZ500['股票代码']))
        ERROR_LIST.append(['中证500成分股缺失', missing_500])

    if len(HS300) != 300:
        weightdf = IO.read_data([date, next_date], alt = '/data/group/800466/warehouse/prod/MD/MarketData/MD/UNIVERSE/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5').droplevel(0)
        list_300 = list(weightdf[weightdf['index_weight_hs300']!= 0].index)
        missing_300 = list(set(list_300) - set(hs300['股票代码']))
        ERROR_LIST.append(['沪深300成分股缺失', missing_300])

    if len(ERROR_LIST) > 0:
        lm = link.LinkMessage()
        lm.sendMessage('%s日%s品种参数有误,  %s'%(next_date, cat, str(ERROR_LIST)))
        
    else:
        lm = link.LinkMessage()
        lm.sendMessage('%s日%s品种参数检查无误'%(next_date, cat))
        lm.sendMessage(' ------ %s日%s单边持仓%s张 ------ '%(next_date, cat, str(QCCC['多头持仓'].sum())))

        file_info = upload_strategy_file(strategy_id="MobiusStrategy", strategy_date= str(next_date), file_type=1,
                                                 upload_file_path = para_path, is_delete=False, is_ready = 1)
        assert file_info == True
        
        
    del lm       
           
        

if __name__ == '__main__':
    _,date,_ = check_update_date()
    def minute_flag_check(date):
        flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'
        flag_path = flag_rootpath + str(date) + '/'
        path = flag_rootpath + str(date) + '/' + 'trade_files_factors.success'
        path2 = flag_rootpath + str(date) + '/' + 'trade_files.success'
        path3 = flag_path + str(date) + '_norm2_generation.success'
        path4 = flag_rootpath + str(date) + '/' + 'trade_files_factors2.success'
        print(path)
        print(path2)
        print(path3)
        return os.path.exists(path) and os.path.exists(path2) and os.path.exists(path3) and os.path.exists(path4)

    while True:
        if minute_flag_check(date):
            break
        time.sleep(60)
    print('flag check finished!')
    next_date = udt.get_trading_day_offset(str(date),1)[0].strftime('%Y%m%d')
    #CHECK('/data/user/016700/Data/para/Mobius_%s/MobiusStrategy_IC_%s#503301.xlsx'%(next_date, next_date))
    #CHECK('/data/user/016700/Data/para/Mobius_%s/MobiusStrategy_IF_%s#503301.xlsx'%(next_date, next_date))
    #CHECK('/data/user/016700/Data/para/Mobius_%s/MobiusStrategy_IM_%s#503302.xlsx'%(next_date, next_date))
    #CHECK('/data/user/016700/Data/para/Mobius_%s/MobiusStrategy_IM_%s#503305.xlsx'%(next_date, next_date))
    for cat in ['IC', 'IF', 'IM']:
        CHECK(cat = cat)
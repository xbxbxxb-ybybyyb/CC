import pandas as pd
import numpy as np
import cvxpy as cp
import time,datetime
import os
from multiprocessing import Pool
from xquant.xqutils.helper import link
import requests,json,datetime,time,sys
from tqdm import tqdm
from xquant.thirdpartydata.marketdata import MarketData
from xquant.factordata import FactorData
sys.path.append('/data/group/800319')
from FaaMonitor.dataApi import getData,tradeDate,stockList

###可用factor列表########
# stock_pool：股票池
# Limit_price：涨停价
# Limit_stock：个股当日是否涨停
# Bad_Board_stock：个股当日是否烂板
# Open_Board_stock：个股当日是否炸板
# Limit_High：个股当日连板高度
# Power_stock：个股当日是否强势
# Active_Concept：每日活跃板块
# Active_Stock：每日活跃板块的活跃个股
# UnActive_Stock：每日活跃板块的不活跃个股
# Concept_Close：概念板块的每日收盘价
# Concept_Pct：概念板块的每日涨跌幅
# Concept_num：概念板块每日的股票数量
# Active_Concept_small：每日活跃小版块
# Active_Concept_middle：每日活跃中板块
# Active_Concept_big：每日活跃大板块
# Dragon_Stock：市场中的龙头个股
def get_basic_values(factor,start_date=20130101,end_date=None,read_path='/data/group/800319/Daily_ConCept/RawData/BasicData/'):
    date_list=getData.get_date_range(start_date,end_date)
    BasicData=pd.read_hdf(read_path+factor+'.h5',key=factor).loc[date_list]
    return BasicData

###可用factor列表########
# Limit_stock_inday：个股日内是否涨停
# Open_Board_inday：个股日内是否炸板
# Limit_High_min：个股日内的连板高度
def get_minute_values(factor,start_date=20140101,end_date=None,basic_date=20130101,read_path='/data/group/800319/Daily_ConCept/RawData/BasicData/'):
    date_list = getData.get_date_range(start_date, end_date)
    start_date=date_list[0]
    end_date=date_list[-1]
    basic_list = getData.get_date_range(basic_date, end_date)

    start_row=(basic_list.index(start_date))*242
    end_row=(basic_list.index(end_date)+1)*242
    BasicData = pd.read_hdf(read_path + factor + '.h5', key=factor,start=start_row,stop=end_row)
    return BasicData

###可用factor列表########
# Concept_StockList：概念板块的全部个股
# Concept_ActiveList：概念板块的活跃个股
# Concept_UnActiveList：概念板块的不活跃个股
# Concept_DragonList：概念板块的龙头个股
def get_concept_values(factor,concept,start_date=20140101,end_date=None,read_path='/data/group/800319/Daily_ConCept/RawData/'):
    date_list = getData.get_date_range(start_date, end_date=20210416)
    ConceptData=pd.read_hdf(read_path+factor+'/'+concept+'.h5',key=concept).loc[date_list]
    return ConceptData

###获取个股在历史周期所处的概念板块##
# Concept_StockList：概念板块的全部个股
# Concept_ActiveList：概念板块的活跃个股
# Concept_UnActiveList：概念板块的不活跃个股
# Concept_DragonList：概念板块的龙头个股
def get_1stock_concept(factor,stock,start_date=20140101,end_date=None,read_path='/data/group/800319/Daily_ConCept/RawData/'):
    date_list = getData.get_date_range(start_date, end_date)
    concept_list=[x[:-3] for x in os.listdir(read_path+factor)]

    df=[]
    for concept in concept_list:
        concept_result=pd.read_hdf(read_path+factor+'/'+concept+'.h5',key=concept,columns=[stock]).loc[date_list]
        if len(concept_result.columns)>0:
            concept_result.columns=[concept]
            df.append(concept_result)
    if len(df)>0:
        df = pd.concat(df, axis=1)
    return df

###获取板块的日内信息###########
# 涨跌幅
# 分钟涨跌幅
# 连板高度
# 涨停数量
# 炸板率
# 炸板个股下跌幅度
# 板块个股数量
# 昨日龙头股数量
# 龙头股涨跌幅
# 龙头股涨停数量
# 龙头股炸板率
# 昨日涨停数量
# 昨日涨停股今日涨跌幅
# 昨日涨停股连板率
# 昨日烂板数量
# 昨日烂板股今日涨跌幅
# 昨日栏板股连板率
# 近期强势股数量
# 近期强势股涨跌幅
# 近期强势股股封板数量
# 近期活跃股数量
# 近期活跃股涨跌幅
def get_factor_1concept(concpet,factor=None,start_date=20140101,end_date=None,read_path='/data/group/800319/Daily_ConCept/RawData/Concept_IndayData/'):
    date_list = getData.get_date_range(start_date, end_date)
    df=[]
    if factor==None:
        for date in date_list:
            BasicData=pd.read_hdf(read_path +str(date)+'/' +concpet + '.h5', key=concpet)
            df.append(BasicData)
        df = pd.concat(df, axis=0)
    elif type(factor)==list:
        for date in date_list:
            BasicData=pd.read_hdf(read_path +str(date)+'/' +concpet + '.h5', key=concpet,columns=factor)
            df.append(BasicData)
        df = pd.concat(df, axis=0)
    else:
        for date in date_list:
            BasicData=pd.read_hdf(read_path +str(date)+'/' +concpet + '.h5', key=concpet,columns=[factor])
            df.append(BasicData)
        df = pd.concat(df, axis=0)

    return df

##获取某一个指标在多个板块之间的结果##
def get_1factor_concept(factor,concept=None,start_date=20140101,end_date=None,use_update_time=True,read_path='/data/group/800319/Daily_ConCept/RawData/Concept_IndayData/'):
    date_list=getData.get_date_range(start_date,end_date)
    start_date=date_list[0]
    end_date=date_list[-1]
    if concept==None:
        concept_list = [x[:-3] for x in os.listdir(read_path + str(start_date))]
    elif type(concept)==list:
        concept_list=concept
    elif type(concept)==str:
        concept_list=[concept]
    if type(factor)==list:
        print('必须输入单一因子值，不能为list')
        return None
    if use_update_time==True:
        ##获取概念板块的基准日##
        s=FactorData()
        concept_daily = s.get_factor_value('WIND_AIndexDescription',factors=['S_INFO_WINDCODE', 'S_INFO_LISTDATE', 'S_INFO_NAME', 'EXPIRE_DATE'])
        concept_daily=concept_daily.set_index('S_INFO_WINDCODE')
        if len(list(set(concept_list).difference(set(concept_daily.index))))>0:
            print('存在部分概念出现问题，剔除该部分概念：',list(set(concept_list).difference(set(concept_daily.index))))

        concept_list=list(set(concept_daily.index).intersection(set(concept_list)))
        concept_daily=concept_daily.loc[concept_list]
        df = []
        for concept in tqdm(concept_list):
            concept_start_date=concept_daily.loc[concept,'S_INFO_LISTDATE']
            ########如果为NaN，就用开始日期########
            if pd.isna(concept_start_date)==True:
                concept_start_date=start_date
            ###########如果开始日期在start_date前，就用start_date############
            elif int(concept_start_date)<=start_date:
                concept_start_date=start_date
            ############如果开始日期在end_date后，就不包含这个概念#############
            elif int(concept_start_date)>=end_date:
                continue

            concept_end_date = concept_daily.loc[concept, 'EXPIRE_DATE']
            if pd.isna(concept_end_date)==True:
                concept_end_date=end_date
            ###########如果在end_date之后，就用concept_end_date############
            elif int(concept_end_date) > end_date:
                concept_end_date = end_date
            ###########如果在start_date前，就不包括这个概念################
            elif int(concept_end_date)<=start_date:
                continue

            BasicData=get_factor_1concept(concept,factor,int(concept_start_date),int(concept_end_date))
            BasicData.columns=[concept]
            df.append(BasicData)
        df = pd.concat(df, axis=1)
        df=df.dropna(how='all', axis=1)
        return df
    else:
        df = []
        for concept in tqdm(concept_list):
            BasicData = get_factor_1concept(concept, factor, start_date, end_date)
            BasicData.columns = [concept]
            df.append(BasicData)
        df = pd.concat(df, axis=1)
        df = df.dropna(how='all', axis=1)

        return df

########查询某个概念板块在某日是否进入活跃板块#########
def Inqure_Conept_oneday(concept,date):
    #######查询板块前10日的全部情况###########
    date_list = getData.get_date_range(20130101, date)
    start_date=date_list[date_list.index(date)-10]
    date_list=getData.get_date_range(start_date,date)
    #######先查询在10日内是否是活跃板块，如果是，直接输出#######
    Active_Concept=get_basic_values('Active_Concept',start_date=start_date,end_date=date)
    if (concept not in Active_Concept.columns):
        print('该板块无数据或者被剔除')
        return None
    else:
        if (len(Active_Concept[concept][Active_Concept[concept]==True])>0):
            date_show=Active_Concept[concept][Active_Concept[concept] == True].index.to_list()
            print('该板块在10日内出现过，出现日期为:',date_show)

        ######先获取板块交易数据########
        Concept_Pct = get_basic_values('Concept_Pct',start_date=start_date,end_date=date)  #全部版块的日间涨幅
        Concept_num = get_basic_values('Concept_num', start_date=start_date, end_date=date)  #每日各个板块的股票数量
        Stock_price = getData.get_daily_1factor('pct_chg',date_list=date_list)  #获取全市场个股的涨跌幅
        Limit_stock =get_basic_values('Limit_stock',start_date=start_date,end_date=date)  #获取当日涨停价
        ######如果再10日内均没有出现过，查询原因#######
        #只考虑当天，进行循环，先计算股票数量，确定板块大小
        length=Concept_num.loc[date,concept]
        if length<5:
            print(date,':数量小于5个被剔除，该板块内个股数量为',length)
        ##如果是小板块##
        elif ((length >= 5) & (length <= 10)):
            print(date,':小概念')
            ########获取当日的全部小版块，并选取小版块内涨幅大于4%的部分
            concept_list_small = (Concept_num.loc[date] >= 5) & (Concept_num.loc[date] <= 10)
            concept_list_small = concept_list_small & (Concept_Pct.loc[date] >= 4)
            if concept_list_small[concept]==False:
                print('绝对涨跌幅不满足被剔除，该板块绝对涨幅为',Concept_Pct.loc[date,concept])
            else:
                ##获取当日的概念个股及涨跌幅####
                Concept_Stock=get_concept_values('Concept_StockList',concept,start_date=start_date, end_date=date)
                concept_stock_today=Concept_Stock.loc[date][Concept_Stock.loc[date]==True].index.to_list()
                stock_pct_today = (Stock_price.loc[date, concept_stock_today])
                if (((stock_pct_today >= 5).sum() < 2) | (stock_pct_today.max() <= 9)):
                    print('概念板块内个股涨幅不满足要求', stock_pct_today)
                else:
                    stock_pct_today = (Limit_stock.loc[date_list[date_list.index(date) - 20]:date, concept_stock_today])
                    if (stock_pct_today).sum().max() <= 1:
                        print('概念板块内个股近20日内最大涨停次数不满足要求', (stock_pct_today).sum().max())
                    else:
                        #####如果都满足要求，就要看当天活跃板块的排名##########
                        concept_small=concept_list_small[concept_list_small==True].index.to_list()
                        for concept_other in concept_small:
                            ##获取概念个股及涨跌幅####
                            Concept_Stock = get_concept_values('Concept_StockList', concept_other, start_date=start_date,end_date=date)
                            concept_stock_today = Concept_Stock.loc[date][Concept_Stock.loc[date] == True].index.to_list()
                            stock_pct_today = (Stock_price.loc[date, concept_stock_today])
                            if (((stock_pct_today >= 5).sum() < 2) | (stock_pct_today.max() <= 9)):
                                concept_list_small.loc[concept_other] = False
                            else:  #######板块内近20天累计最高一板不放进来########
                                stock_pct_today = (Limit_stock.loc[date_list[date_list.index(date) - 20]:date, concept_stock_today])
                                if (stock_pct_today).sum().max() <= 1:
                                    concept_list_small.loc[concept_other] = False
                        #####先把不满足要求的板块都剔除，在满足要求的板块中排名#######
                        concept_small = concept_list_small[concept_list_small == True].index.to_list()
                        Concept_Rank=Concept_Pct.loc[date,concept_small].dropna().sort_values(ascending=False)
                        if len(Concept_Rank.loc[:concept])>3:
                            print('概念板块间排名不满足要求，排名第', len(Concept_Rank.loc[:concept]))
                        else:
                            print('当日满足要求选入')
                        print(Concept_Rank)

        ##如果是中板块##
        elif ((length > 10) & (length <= 30)):
            print(date,':中概念')
            concept_list_middle = (Concept_num.loc[date] >= 11) & (Concept_num.loc[date] <= 30)
            concept_list_middle = concept_list_middle & (Concept_Pct.loc[date] >= 3)
            if concept_list_middle[concept]==False:
                print('绝对涨跌幅不满足被剔除，该板块绝对涨幅为',Concept_Pct.loc[date,concept])
            else:
                ##获取当日的概念个股及涨跌幅####
                Concept_Stock=get_concept_values('Concept_StockList',concept,start_date=start_date, end_date=date)
                concept_stock_today=Concept_Stock.loc[date][Concept_Stock.loc[date]==True].index.to_list()
                stock_pct_today = (Stock_price.loc[date, concept_stock_today])
                ######获取前30%个股的涨幅均值
                stock_pct = stock_pct_today.sort_values(ascending=False).iloc[:int(round(len(stock_pct_today) * 0.3, ))]
                if (((stock_pct >= 5).sum() < 2) | (stock_pct.max() <= 9)):
                    print('概念板块内个股涨幅不满足要求')
                    print(stock_pct)
                else:
                    stock_pct_today = (Limit_stock.loc[date_list[date_list.index(date) - 20]:date, concept_stock_today])
                    if (stock_pct_today).sum().max() <= 1:
                        print('概念板块内个股近20日内最大涨停次数不满足要求', (stock_pct_today).sum().max())
                    else:
                        #####如果都满足要求，就要看当天活跃板块的排名##########
                        concept_middle = concept_list_middle[concept_list_middle == True].index.to_list()
                        for concept_other in concept_middle:
                            ##获取概念个股及涨跌幅####
                            Concept_Stock = get_concept_values('Concept_StockList', concept_other, start_date=start_date,end_date=date)
                            concept_stock_today = Concept_Stock.loc[date][Concept_Stock.loc[date] == True].index.to_list()
                            stock_pct_today = (Stock_price.loc[date, concept_stock_today])
                            if (((stock_pct_today >= 5).sum() < 2) | (stock_pct_today.max() <= 9)):
                                concept_list_middle.loc[concept_other] = False
                            else:  #######板块内近20天累计最高一板不放进来########
                                stock_pct_today = (Limit_stock.loc[date_list[date_list.index(date) - 20]:date, concept_stock_today])
                                if (stock_pct_today).sum().max() <= 1:
                                    concept_list_middle.loc[concept_other] = False
                        #####先把不满足要求的板块都剔除，在满足要求的板块中排名#######
                        concept_middle = concept_list_middle[concept_list_middle == True].index.to_list()
                        Concept_Rank=Concept_Pct.loc[date,concept_middle].dropna().sort_values(ascending=False)
                        if len(Concept_Rank.loc[:concept])>3:
                            print('概念板块间排名不满足要求，排名第', len(Concept_Rank.loc[:concept]))
                        else:
                            print('当日满足要求选入')
                        print(Concept_Rank)

        ##如果是大板块##
        if length > 30:
            print(date,':大概念')
            concept_list_big = (Concept_num.loc[date] >= 31)
            concept_list_big = concept_list_big & (Concept_Pct.loc[date] >= 2)
            if concept_list_big[concept] == False:
                print('绝对涨跌幅不满足被剔除，该板块绝对涨幅为', Concept_Pct.loc[date, concept])
            else:
                ##获取当日的概念个股及涨跌幅####
                Concept_Stock = get_concept_values('Concept_StockList', concept, start_date=start_date, end_date=date)
                concept_stock_today = Concept_Stock.loc[date][Concept_Stock.loc[date] == True].index.to_list()
                stock_pct_today = (Stock_price.loc[date, concept_stock_today])
                ######获取前20%个股的涨幅均值
                stock_pct = stock_pct_today.sort_values(ascending=False).iloc[:int(round(len(stock_pct_today) * 0.2, ))]
                if (((stock_pct >= 4).sum() < 2) | ((stock_pct > 9).sum() < 2)):
                    print('概念板块内个股涨幅不满足要求', stock_pct)
                else:
                    stock_pct_today = (Limit_stock.loc[date_list[date_list.index(date) - 20]:date, concept_stock_today])
                    if (stock_pct_today).sum().max() <= 1:
                        print('概念板块内个股近20日内最大涨停次数不满足要求', (stock_pct_today).sum().max())
                    else:
                        #####如果都满足要求，就要看当天活跃板块的排名##########
                        concept_big = concept_list_big[concept_list_big == True].index.to_list()
                        for concept_other in concept_big:
                            ##获取概念个股及涨跌幅####
                            Concept_Stock = get_concept_values('Concept_StockList', concept_other, start_date=start_date,end_date=date)
                            concept_stock_today = Concept_Stock.loc[date][Concept_Stock.loc[date] == True].index.to_list()
                            stock_pct_today = (Stock_price.loc[date, concept_stock_today])
                            if (((stock_pct_today >= 5).sum() < 2) | (stock_pct_today.max() <= 9)):
                                concept_list_big.loc[concept_other] = False
                            else:  #######板块内近20天累计最高一板不放进来########
                                stock_pct_today = (Limit_stock.loc[date_list[date_list.index(date) - 20]:date, concept_stock_today])
                                if (stock_pct_today).sum().max() <= 1:
                                    concept_list_big.loc[concept_other] = False
                        #####先把不满足要求的板块都剔除，在满足要求的板块中排名#######
                        concept_big = concept_list_big[concept_list_big == True].index.to_list()
                        Concept_Rank=Concept_Pct.loc[date,concept_big].dropna().sort_values(ascending=False)
                        if len(Concept_Rank.loc[:concept])>3:
                            print('概念板块间排名不满足要求，排名第', len(Concept_Rank.loc[:concept]))
                        else:
                            print('当日满足要求选入')
                        print(Concept_Rank)

##########输出概念板块的历史情况########
#形成dataframe:日期，活跃小板块名称，活跃中板块名称，活跃大板块名称，板块活跃个股数量，板块活跃个股列表
def Get_Active_Concept(start_date,end_date,read_path='/data/group/800319/Daily_ConCept/RawData/BasicData/',save_path='/data/user/015624/'):
    date_list=getData.get_date_range(start_date,end_date)
    #######读取数据#######
    concept_list_small=get_basic_values('Active_Concept_small',start_date=start_date,end_date=end_date,read_path=read_path)
    concept_list_middle=get_basic_values('Active_Concept_middle',start_date=start_date,end_date=end_date,read_path=read_path)
    concept_list_big=get_basic_values('Active_Concept_big',start_date=start_date,end_date=end_date,read_path=read_path)
    Active_Stock=get_basic_values('Active_Stock',start_date=start_date,end_date=end_date,read_path=read_path)
    ##先把概念板块代码和名称调整##
    s = FactorData()
    index_label = s.get_factor_value('WIND_INDEXCONTRASTSECTOR',factors=['S_INFO_INDEXCODE', 'S_INFO_NAME', 'S_INFO_INDUSTRYCODE', 'S_INFO_INDUSTRYCODE2'])
    index_label.set_index('S_INFO_INDEXCODE', inplace=True)
    ##再把概念板块代码和名称调整##
    concept_list_small.columns=pd.Series(concept_list_small.columns).apply(lambda x:index_label.loc[x,'S_INFO_NAME'])
    concept_list_middle.columns=pd.Series(concept_list_middle.columns).apply(lambda x:index_label.loc[x,'S_INFO_NAME'])
    concept_list_big.columns=pd.Series(concept_list_big.columns).apply(lambda x:index_label.loc[x,'S_INFO_NAME'])
    ##最后把股票代码和名称调整##
    stock_name = s.get_factor_value('WIND_AShareDescription', factors=['S_INFO_WINDCODE', 'S_INFO_NAME'])
    stock_name.set_index('S_INFO_WINDCODE', inplace=True)
    Active_Stock.columns=pd.Series(Active_Stock.columns).apply(lambda x:stockList.trans_int2windcode(x))
    Active_Stock.columns=pd.Series(Active_Stock.columns).apply(lambda x:stock_name.loc[x,'S_INFO_NAME'])
    ####循环写入#######
    Concept_Today=pd.DataFrame(index=date_list,columns=['活跃小板块','活跃中板块','活跃大板块','板块活跃个股数量','板块活跃个股列表'])
    for date in date_list:
        Concept_Today.loc[date,'活跃小板块'] = concept_list_small.loc[date][concept_list_small.loc[date]==True].index.to_list()
        Concept_Today.loc[date, '活跃中板块'] = concept_list_middle.loc[date][concept_list_middle.loc[date] == True].index.to_list()
        Concept_Today.loc[date, '活跃大板块'] = concept_list_big.loc[date][concept_list_big.loc[date] == True].index.to_list()
        Concept_Today.loc[date, '板块活跃个股数量'] = Active_Stock.loc[date].sum()
        Concept_Today.loc[date, '板块活跃个股列表'] =Active_Stock.loc[date][Active_Stock.loc[date]==True].index.to_list()

    Concept_Today.to_excel(save_path+str(start_date)+'-'+str(end_date)+'每日活跃概念板块.xlsx',index=True)

#############获取概念板块对应代码####################
def Get_Concept_Code():
    s = FactorData()
    index_label = s.get_factor_value('WIND_INDEXCONTRASTSECTOR',factors=['S_INFO_INDEXCODE', 'S_INFO_NAME', 'S_INFO_INDUSTRYCODE','S_INFO_INDUSTRYCODE2'])
    index_label.set_index('S_INFO_INDEXCODE', inplace=True)

    concept_list = os.listdir('/data/group/800319/Daily_ConCept/RawData/Concept_StockList/')
    concept_list = [x[:-3] for x in concept_list]
    index_label=index_label.loc[concept_list]
    return index_label[['S_INFO_NAME']]

#############获取板块纳入日期###################
def Get_Concept_Time(concept_list=None):
    s = FactorData()
    concept_daily = s.get_factor_value('WIND_AIndexDescription',factors=['S_INFO_WINDCODE', 'S_INFO_LISTDATE', 'S_INFO_NAME', 'EXPIRE_DATE'])
    concept_daily = concept_daily.set_index('S_INFO_WINDCODE')
    if concept_list == None:
        return concept_daily
    else:
        return concept_daily.loc[concept_list]



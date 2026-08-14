import pandas as pd
import pickle
import numpy as np
import time, datetime,os
from xquant.thirdpartydata.marketdata import MarketData
from xquant.factordata import FactorData

##########数据回滚模块：保存位置在外层，数据位置在里层#########
def get_data_fromopen(date,concept_name,save_path='/data/group/800442/800319/RealTime_Data/'):
    ma = MarketData()
    #1、先获取最新时间段的文件名称
    concept_result_name = sorted(os.listdir(save_path + date+ '/' + concept_name))[-1]
    concept_result = pd.read_pickle(save_path + date+ '/' + concept_name +'/'+concept_result_name)  # 获取读取的股票列表
    factor_list = list(set(concept_result.keys()))
    security_list = set(concept_result[factor_list[0]].columns)

    concept_dict ={}

    for factor in factor_list:
        result_list=[]
        for code in security_list:
            Result = ma.getMDSecurityKLineDataFrame(code,str(date)+ '091500',str(date)+'150000', 10, 20)
            Tmp_series=Result.set_index('MDTime')[factor]
            Tmp_series.rename(code, inplace=True)
            result_list.append(Tmp_series)

        calc_df=pd.concat(result_list,axis=1)
        calc_df.index = (calc_df.index.astype(int) / 100000).astype(int)

        if (factor == 'TotalValueTrade'):
            calc_df = calc_df / 10000
        elif (factor == 'TotalVolumeTrade'):
            calc_df =calc_df / 100
        else:
            calc_df = calc_df.copy()

        concept_dict[factor] = calc_df

    with open(save_path + date +'/'+ 'temp_' + concept_name + '.pkl', 'wb') as f:
        pickle.dump(concept_dict, f)

# 1、获取一个板块的指定因子数据
def get_oneconcept_alldata(concept_name,factor_list=None,read_path='/data/group/800442/800319/RealTime_Data/'):

    date = datetime.datetime.now().strftime('%Y%m%d')  # 获取今天日期
    concept_result_name = sorted(os.listdir(read_path + date+'/'+concept_name+'/'))
    while len(concept_result_name) == 0:
        time.sleep(3)
        print('数据尚未写入')
        concept_result_name = sorted(os.listdir(read_path + date + '/' + concept_name + '/'))

    factor_alldata_result = pd.read_pickle(read_path + date+'/'+concept_name+'/' + concept_result_name[-1])  #获取读取的股票列表
    Result_dict = {}

    if factor_list == None:
        factor_list = list(factor_alldata_result.keys())

    for factor in factor_list:
        factor_data = factor_alldata_result[factor]
        # 如果因子结果＞925，说明并非开盘前就运行了，那就要补全之前的数据
        if factor_data.index[0]>925:
            #确定数据是否补全，如果已经补全，直接读入补全的数据，如果没有，那就写入
            if os.path.exists(read_path + date + '/'+ 'temp_' + concept_name + '.pkl')==False:
                get_data_fromopen(date,concept_name)

            temp_data = pd.read_pickle(read_path + date + '/'+ 'temp_' + concept_name + '.pkl')[factor]

            # 最后拼接起来作为结果
            factor_data = temp_data.append(factor_data)
            factor_data = factor_data.groupby(level=0).first()

        if ((factor=='TotalVolumeTrade') or (factor=='TotalValueTrade')):
            factor_data.fillna(0,inplace=True)

        Result_dict[factor] = factor_data

    return Result_dict

# 2、获取多个板块的一个因子
def get_allconcept_onedata(factor,concept_list=None,read_path='/data/group/800442/800319/RealTime_Data/'):

    date = datetime.datetime.now().strftime('%Y%m%d')  # 获取今天日期
    Result_dict = {}

    if concept_list==None:
        concept_list = os.listdir(read_path + date +'/')
        concept_list = [x[5:-4] if 'temp_' in x else x for x in concept_list]
        concept_list = list(set(concept_list))

    for concept_name in concept_list:
        factor_data = get_oneconcept_alldata(concept_name=concept_name,factor_list=[factor],read_path=read_path)[factor]
        Result_dict[concept_name] = factor_data

    return Result_dict

# 3、盘前数据准备模块，9:10分后再提取
def data_prepare(date):
    # 如果日期是当日，就9:10分后提取，昨收价，最高价，最低价
    if date == datetime.datetime.now().strftime('%Y%m%d'):
        while int(datetime.datetime.now().strftime('%H%M'))<=912:
            print('行情中心数据9:10后才更新，为防止数据缺失，9:12开始更新数据')
            time.sleep(10)

    s = FactorData()
    all_data = s.get_factor_value('Basic_factor', stock=[], mddate=[date], factor_names=['mdc_pre_close','mdc_maxpx','mdc_minpx',])
    all_data.dropna(how='all',inplace=True)
    all_data.columns = ['pre_close','max_price','min_price']

    return all_data

# 4、获取板块股票数量
def get_concept_num():
    Conept_AllStock = pd.read_excel('/data/group/800442/800319/Concept_monitor/概念板块分工及对应个股.xlsx', sheet_name=0,index_col=0).iloc[:, :3]
    Conept_DelStock = set(pd.read_excel('/data/group/800442/800319/Concept_monitor/概念板块分工及对应个股.xlsx', sheet_name=1, index_col=0)['子主题名称'].dropna())
    concept_Num = pd.DataFrame(columns=['Stock_Num'])
    for concept in sorted(list(set(Conept_AllStock['子主题']))):
        if (len(set(Conept_AllStock[Conept_AllStock['子主题'] == concept].index)) < 50) & (
                len(set(Conept_AllStock[Conept_AllStock['子主题'] == concept].index)) > 5) \
                & (concept not in Conept_DelStock):
            concept_Num.loc[concept] = len(set(Conept_AllStock[Conept_AllStock['子主题'] == concept].index))

    return concept_Num

# 5、板块整体数据，即板块之间的涨跌幅，成交额，成交量，涨幅在N%以上的个股数量
def get_concept_value(factor,concept_list=None,read_path='/data/group/800442/800319/RealTime_Data/'):
    date = datetime.datetime.now().strftime('%Y%m%d')  # 获取今天日期
    all_data = data_prepare(date)

    # (1)板块涨跌幅
    if factor == 'Pct_Change':
        Result_dict = get_allconcept_onedata('ClosePx', concept_list=concept_list, read_path=read_path)
        concept_result = pd.DataFrame(columns=list(Result_dict.keys()))

        all_data = all_data['pre_close'].loc[date]
        for concept in concept_result.columns:
            calc_df = Result_dict[concept].fillna(method = 'ffill')/all_data.loc[Result_dict[concept].columns]-1
            concept_result[concept] = round(calc_df.mean(axis=1),4)

        return concept_result

    # (2)板块涨停数量
    elif factor == 'Max_Num':
        Result_dict = get_allconcept_onedata('ClosePx', concept_list=concept_list, read_path=read_path)
        concept_result = pd.DataFrame(columns=list(Result_dict.keys()))

        all_data = all_data['max_price'].loc[date]
        for concept in concept_result.columns:
            calc_df = Result_dict[concept].fillna(method = 'ffill')==all_data.loc[Result_dict[concept].columns]
            concept_result[concept] = calc_df.sum(axis=1)

        return concept_result

    # (3)板块跌停数量
    elif factor == 'Min_Num':
        Result_dict = get_allconcept_onedata('ClosePx', concept_list=concept_list, read_path=read_path)
        concept_result = pd.DataFrame(columns=list(Result_dict.keys()))

        all_data = all_data['min_price'].loc[date]
        for concept in concept_result.columns:
            calc_df = Result_dict[concept].fillna(method = 'ffill')==all_data.loc[Result_dict[concept].columns]
            concept_result[concept] = calc_df.sum(axis=1)

        return concept_result

    # (4)板块涨幅在N%以上的股票数量
    elif factor[:6]=='UpNum_':
        Result_dict = get_allconcept_onedata('ClosePx', concept_list=concept_list, read_path=read_path)
        concept_result = pd.DataFrame(columns=list(Result_dict.keys()))

        bigger_pct = int(factor[6:])*0.01
        all_data = all_data['pre_close'].loc[date]
        for concept in concept_result.columns:
            calc_df = Result_dict[concept].fillna(method = 'ffill') / all_data.loc[Result_dict[concept].columns] - 1
            concept_result[concept] = (calc_df>=bigger_pct).sum(axis=1)

        return concept_result

    # (5)板块涨幅在N%以下的股票数量
    elif factor[:8] == 'DownNum_':
        Result_dict = get_allconcept_onedata('ClosePx', concept_list=concept_list, read_path=read_path)
        concept_result = pd.DataFrame(columns=list(Result_dict.keys()))

        bigger_pct = int(factor[8:]) * 0.01
        all_data = all_data['pre_close'].loc[date]
        for concept in concept_result.columns:
            calc_df = Result_dict[concept].fillna(method = 'ffill') / all_data.loc[Result_dict[concept].columns] - 1
            concept_result[concept] = (calc_df <= bigger_pct).sum(axis=1)

        return concept_result

    # (6)板块平均成交量
    elif factor == 'TotalVolumeTrade':
        Result_dict = get_allconcept_onedata('TotalVolumeTrade', concept_list=concept_list, read_path=read_path)
        concept_result = pd.DataFrame(columns=list(Result_dict.keys()))

        for concept in concept_result.columns:
            concept_result[concept] = round(Result_dict[concept].fillna(0).mean(axis=1),2)

        return concept_result

    # (7)板块平均成交额
    elif factor == 'TotalValueTrade':
        Result_dict = get_allconcept_onedata('TotalValueTrade', concept_list=concept_list, read_path=read_path)
        concept_result = pd.DataFrame(columns=list(Result_dict.keys()))

        for concept in concept_result.columns:
            concept_result[concept] = round(Result_dict[concept].fillna(0).mean(axis=1),2)

        return concept_result

# 6、给定股票池的股票数据
def get_stock_factor(factor_list,stock_list):
    time.sleep(2)
    ma = MarketData()
    date = datetime.datetime.now().strftime('%Y%m%d')
    stock_dict={}
    for factor in factor_list:
        result_list = []
        if factor=='MeanPrice':
            for code in stock_list:
                Result = ma.getMDSecurityKLineDataFrame(code, str(date) + '091500', str(date) + '150000', 10, 20).set_index('MDTime')
                Tmp_Volume = Result['TotalVolumeTrade']
                Tmp_Amt = Result['TotalValueTrade']
                Tmp_series = round(Tmp_Amt.cumsum()/Tmp_Volume.cumsum(),2)
                Tmp_series.rename(code, inplace=True)
                result_list.append(Tmp_series)
        else:
            for code in stock_list:
                Result = ma.getMDSecurityKLineDataFrame(code, str(date) + '091500', str(date) + '150000', 10, 20)
                Tmp_series = Result.set_index('MDTime')[factor]
                Tmp_series.rename(code, inplace=True)
                result_list.append(Tmp_series)

        calc_df = pd.concat(result_list, axis=1)
        calc_df.index = (calc_df.index.astype(int) / 100000).astype(int)

        if (factor == 'TotalValueTrade'):
            calc_df = calc_df / 10000
        elif (factor == 'TotalVolumeTrade'):
            calc_df = calc_df / 100
        else:
            calc_df = calc_df.copy()

        stock_dict[factor] = calc_df

    return stock_dict

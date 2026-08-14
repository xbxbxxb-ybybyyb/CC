# -*- coding: utf-8 -*-
import pandas as pd
import json
import os
import datetime

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, bytes):
                return str(obj, encoding='utf-8')
            return json.JSONEncoder.default(self, obj)
        except UnicodeDecodeError:
            pass

def generate_zuhe_uat(choose_param_df,date, saturn_config_Df, ceres_config_Df):
    zuhe_df = choose_param_df.copy()
    zuhe_df.index.rename('证券代码',inplace=True)
    zuhe_df['买入交易账户'] = '20000002'
    zuhe_df['卖出交易账户'] = '20000002'
    zuhe_df['买入证券数量'] = '10000000'
    zuhe_df['卖出证券数量'] = zuhe_df['期初可用仓位']
    zuhe_df = zuhe_df[['买入交易账户','卖出交易账户','买入证券数量','卖出证券数量']]
    sh_stockIDs = []
    sz_stockIDs = []
    sell_zuhe_df = zuhe_df[zuhe_df['卖出证券数量']!='0']
    nosell_zuhe_df = zuhe_df[zuhe_df['卖出证券数量']=='0']
    saturn_stocks = saturn_config_Df['股票代码'].values.tolist()
    ceres_stocks = ceres_config_Df['股票代码'].values.tolist()
    saturn_zuhe_df = nosell_zuhe_df[nosell_zuhe_df.index.isin(saturn_stocks)]
    ceres_zuhe_df = nosell_zuhe_df[nosell_zuhe_df.index.isin(ceres_stocks)]
    nosell_zuhe_df = nosell_zuhe_df[~nosell_zuhe_df.index.isin(saturn_stocks+ceres_stocks)]
    print(zuhe_df.shape,sell_zuhe_df.shape,nosell_zuhe_df.shape,saturn_zuhe_df.shape, ceres_zuhe_df.shape)
    for stock in nosell_zuhe_df.index.tolist():
        if '.SZ' in stock:
            sz_stockIDs.append(stock)
    zuhe_commonPath = r'/data/group/800463/xiely/daily/daily-zuhe-prod-O45-SZ-new/'
    for filename in os.listdir(zuhe_commonPath):
        os.remove(os.path.join(zuhe_commonPath,filename))
    nosell_zuhe_df.loc[sz_stockIDs[:500]].to_excel(zuhe_commonPath + 'new-O45组合-SZ-first-'+date+'.xlsx',header=True, encoding='gbk')
    nosell_zuhe_df.loc[sz_stockIDs[500:1000]].to_excel(zuhe_commonPath + 'new-O45组合-SZ-second-'+date+'.xlsx',header=True, encoding='gbk')
    nosell_zuhe_df.loc[sz_stockIDs[1000:1500]].to_excel(zuhe_commonPath + 'new-O45组合-SZ-third-'+date+'.xlsx',header=True, encoding='gbk')
    nosell_zuhe_df.loc[sz_stockIDs[1500:]].to_excel(zuhe_commonPath + 'new-O45组合-SZ-fourth-'+date+'.xlsx',header=True, encoding='gbk')
    if len(sell_zuhe_df)>0:
        sell_zuhe_df.to_excel(zuhe_commonPath + 'new-O45组合-SZ-sell-'+date+'.xlsx',header=True, encoding='gbk')
    if len(saturn_zuhe_df)>0:
        saturn_zuhe_df.to_excel(zuhe_commonPath + 'new-O45组合-SZ-saturn-'+date+'.xlsx',header=True, encoding='gbk')
    if len(ceres_zuhe_df)>0:
        ceres_zuhe_df.to_excel(zuhe_commonPath + 'new-O45组合-SZ-ceres-'+date+'.xlsx',header=True, encoding='gbk')
    
def generate_paramsJson():
    today = datetime.date.today()
    date = today.strftime('%Y%m%d')
    
    commonPath = r'/data/group/800463/xiely/daily/'
    filepath = commonPath + 'excels/param-'+date+'-prod-O45-SZ-new.xlsx'
    
    param_df = pd.read_excel(filepath,sheet_name='InitialBasicParam',encoding='gbk')
    saturn_factor_df = pd.read_pickle(r'/data/group/800463/param/param/param-%s-prod-O45_saturn.pkl'%date)
        
    indexDf = pd.read_excel(filepath,sheet_name='指数',encoding='gbk')
    indexDf['股票代码'] = indexDf['股票代码'].apply(lambda x: {'股票代码':x})

    ZT_ZTDf = pd.read_excel(filepath,sheet_name='T-1日涨停股票',encoding='gbk')
    ZT_ZTDf['股票代码'] = ZT_ZTDf['股票代码'].apply(lambda x: {'股票代码':x})
    
    NIZZT_ZTDf = pd.read_excel(filepath,sheet_name='T-1日非一字涨停的涨停股票',encoding='gbk')
    NIZZT_ZTDf['股票代码'] = NIZZT_ZTDf['股票代码'].apply(lambda x: {'股票代码':x})
    
    CB_Df = pd.read_excel(filepath,sheet_name='T-1日触板股票',encoding='gbk')
    CB_Df['股票代码'] = CB_Df['股票代码'].apply(lambda x: {'股票代码':x}) 
    
    pat3_Df = pd.read_excel(filepath,sheet_name='T-1日形态3股票',encoding='gbk')
    pat3_Df['股票代码'] = pat3_Df['股票代码'].apply(lambda x: {'股票代码':x}) 

    pat4_Df = pd.read_excel(filepath,sheet_name='T-1日形态4股票',encoding='gbk')
    pat4_Df['股票代码'] = pat4_Df['股票代码'].apply(lambda x: {'股票代码':x}) 

    selected_pat4_Df = pd.read_excel(filepath,sheet_name='T-1日筛选后形态4股票',encoding='gbk')
    selected_pat4_Df['股票代码'] = selected_pat4_Df['股票代码'].apply(lambda x: {'股票代码':x}) 

    selected_pat2_Df = pd.read_excel(filepath,sheet_name='T-1日筛选后形态2股票',encoding='gbk')
    selected_pat2_Df['股票代码'] = selected_pat2_Df['股票代码'].apply(lambda x: {'股票代码':x}) 
    
    open_nzt_Df = pd.read_excel(filepath,sheet_name='T-1日开盘非涨停收盘涨停股票',encoding='gbk')
    open_nzt_Df['股票代码'] = open_nzt_Df['股票代码'].apply(lambda x: {'股票代码':x})  
    
    all_CB_Df = pd.read_excel(filepath,sheet_name='T-1日全部触板股票',encoding='gbk')
    all_CB_Df['股票代码'] = all_CB_Df['股票代码'].apply(lambda x: {'股票代码':x})   
    
    stockInfo_Df = pd.read_excel(filepath,sheet_name='股票数据',encoding='gbk')
    stockInfo_Df['股票数据'] = stockInfo_Df.apply(lambda x: {'股票代码':x['股票代码'],'昨收价':x['昨收价'],'昨日最高价':x['昨日最高价'],'昨日流通股份':x['昨日流通股份']},axis=1)

    total_stockInfo_Df = pd.read_excel(filepath,sheet_name='全部股票数据',encoding='gbk')
    total_stockInfo_Df['股票数据'] = total_stockInfo_Df.apply(lambda x: {'股票代码':x['股票代码'],'昨收价':x['昨收价'],'昨日最高价':x['昨日最高价']},axis=1)    
    
    saturn_config_Df = pd.read_excel(filepath,sheet_name='saturn配置参数',encoding='gbk')
    saturn_config_Df = saturn_config_Df.fillna('')
    saturn_config_Df['saturn配置参数'] = saturn_config_Df.apply(lambda x: {'股票代码':x['股票代码'],'saturn节点标识':str(x['saturn节点标识']),'计算和预测开始时间':x['计算和预测开始时间'],\
    '买入开始时间':x['买入开始时间'],'o2pre阈值':x['o2pre阈值'],'saturn策略样本筛选阈值':x['saturn策略样本筛选阈值'],'区间目标金额':x['区间目标金额'],'投票2目标金额':x['投票2目标金额'],'投票3目标金额':x['投票3目标金额'],'投票4目标金额':x['投票4目标金额'],\
    '投票5目标金额':x['投票5目标金额'],'投票6目标金额':x['投票6目标金额'],'投票大于等于7目标金额':x['投票大于等于7目标金额'],'投票2目标金额add':x['投票2目标金额add'],\
    '投票3目标金额add':x['投票3目标金额add'],'投票4目标金额add':x['投票4目标金额add'],'投票5目标金额add':x['投票5目标金额add'],'投票6目标金额add':x['投票6目标金额add'],'投票大于等于7目标金额add':x['投票大于等于7目标金额add'],\
    '模型目录':x['模型目录']},axis=1)   

    saturn_cs_Df = pd.read_excel(filepath,sheet_name='saturn截面订阅列表',encoding='gbk')
    saturn_cs_Df['saturn截面订阅列表'] = saturn_cs_Df.apply(lambda x: {'股票代码':x['股票代码'],'上市一字涨停开板后交易日数量':x['上市一字涨停开板后交易日数量'], '前一个交易日形态': x['前一个交易日形态']}, axis=1) 

    ceres_config_Df = pd.read_excel(filepath,sheet_name='ceres配置参数',encoding='gbk')
    if len(ceres_config_Df)>0:
        ceres_config_Df = ceres_config_Df.fillna('')
        ceres_config_Df['ceres配置参数'] = ceres_config_Df.apply(lambda x: {'股票代码':x['股票代码'],'ceres节点标识':str(x['ceres节点标识']),'计算和预测开始时间':x['计算和预测开始时间'],\
        '买入开始时间':x['买入开始时间'],'区间目标金额':x['区间目标金额'],'投票2目标金额':x['投票2目标金额'],'投票3目标金额':x['投票3目标金额'],'投票4目标金额':x['投票4目标金额'],\
        '投票5目标金额':x['投票5目标金额'],'投票6目标金额':x['投票6目标金额'],\
        '模型目录':x['模型目录']},axis=1)   

    ceres_cs_Df = pd.read_excel(filepath,sheet_name='ceres截面订阅列表',encoding='gbk')
    ceres_cs_Df['ceres截面订阅列表'] = ceres_cs_Df.apply(lambda x: {'股票代码':x['股票代码'],'上市一字涨停开板后交易日数量':x['上市一字涨停开板后交易日数量']}, axis=1) 
   
    sell_config_Df = pd.read_excel(filepath,sheet_name='sell配置参数',encoding='gbk')
    sell_config_Df = sell_config_Df.fillna('')
    sell_config_Df['sell配置参数'] = sell_config_Df.apply(lambda x: {'股票代码':x['股票代码'],'sell节点标识':str(x['sell节点标识']),'计算和预测开始时间':x['计算和预测开始时间'],\
    'v1阈值':x['v1阈值'],'v3阈值':x['v3阈值'],'v1模型目录':x['v1模型目录'],'v3模型目录':x['v3模型目录']},axis=1)   

    sell_cs_Df = pd.read_excel(filepath,sheet_name='sell截面订阅列表',encoding='gbk')
    sell_cs_Df['sell截面订阅列表'] = sell_cs_Df.apply(lambda x: {'股票代码':x['股票代码'],'上市一字涨停开板后交易日数量':x['上市一字涨停开板后交易日数量'], '前一个交易日形态': x['前一个交易日形态']}, axis=1) 
    
    param_df['symbol'] = param_df['股票代码']
    param_df.set_index('symbol',inplace=True)
  
    choose_param_df = param_df.astype(str)
    generate_zuhe_uat(choose_param_df,date,saturn_config_Df, ceres_config_Df)
    
    commonPath = commonPath+'daily-param/'
    date = date+'-prod-O45-SZ-new'
    os.mkdir(commonPath+date)
    for stock in choose_param_df.index:
        params = {}
        for col in choose_param_df.columns:
            params[col] = choose_param_df.loc[stock,col]
        params['指数'] = indexDf['股票代码'].values.tolist()
        params['T-1日涨停股票'] = ZT_ZTDf['股票代码'].values.tolist()
        params['T-1日非一字涨停的涨停股票'] = NIZZT_ZTDf['股票代码'].values.tolist()
        params['T-1日触板股票'] = CB_Df['股票代码'].values.tolist()
        params['T-1日形态3股票'] = pat3_Df['股票代码'].values.tolist()
        params['T-1日形态4股票'] = pat4_Df['股票代码'].values.tolist()
        params['T-1日筛选后形态4股票'] = selected_pat4_Df['股票代码'].values.tolist()
        params['T-1日筛选后形态2股票'] = selected_pat2_Df['股票代码'].values.tolist()
        params['T-1日开盘非涨停收盘涨停股票'] = open_nzt_Df['股票代码'].values.tolist()
        params['T-1日全部触板股票'] = all_CB_Df['股票代码'].values.tolist()
        
        params['股票数据'] = stockInfo_Df['股票数据'].values.tolist()
        if stock not in stockInfo_Df['股票代码'].values.tolist():
            params['股票数据'].append(total_stockInfo_Df[total_stockInfo_Df['股票代码']==stock]['股票数据'].values[0])
        if stock in saturn_config_Df['股票代码'].values.tolist():
            print('saturn: ', stock)
            params['saturn配置参数'] = saturn_config_Df[saturn_config_Df['股票代码']==stock]['saturn配置参数'].values.tolist()
            params['saturn截面订阅列表'] =  saturn_cs_Df['saturn截面订阅列表'].values.tolist()
            params['saturn历史因子'] = saturn_factor_df[saturn_factor_df['股票代码']==stock]['saturn历史因子'].values[0]
        else:
            params['saturn配置参数'] = []
            params['saturn截面订阅列表'] = []      
        if stock in ceres_config_Df['股票代码'].values.tolist():
            print('ceres: ', stock)
            params['ceres配置参数'] = ceres_config_Df[ceres_config_Df['股票代码']==stock]['ceres配置参数'].values.tolist()
            params['ceres截面订阅列表'] =  ceres_cs_Df['ceres截面订阅列表'].values.tolist()
        else:
            params['ceres配置参数'] = []
            params['ceres截面订阅列表'] = [] 
        if stock in sell_config_Df['股票代码'].values.tolist():
            print('sell: ', stock)
            params['sell配置参数'] = sell_config_Df[sell_config_Df['股票代码']==stock]['sell配置参数'].values.tolist()
            params['sell截面订阅列表'] =  sell_cs_Df['sell截面订阅列表'].values.tolist()
            params['T-1日触板股票Sell'] = CB_Df['股票代码'].values.tolist()
            params['T-1日形态4股票Sell'] = pat4_Df['股票代码'].values.tolist()
            params['T-1日筛选后形态4股票Sell'] = selected_pat4_Df['股票代码'].values.tolist()
            params['T-1日筛选后形态2股票Sell'] = selected_pat2_Df['股票代码'].values.tolist()
            params['形态2 T-3日~T-2日o2ul之和Sell'] = params['形态2 T-3日~T-2日o2ul之和']
            params['形态4 T-3日~T-2日o2ul之和Sell'] = params['形态4 T-3日~T-2日o2ul之和']
            params['T-3日~T-1日形态2样本总数量Sell'] = params['T-3日~T-1日形态2样本总数量']
            params['T-3日~T-1日形态4样本总数量Sell'] = params['T-3日~T-1日形态4样本总数量']
        else:
            params['sell配置参数'] = []
            params['sell截面订阅列表'] = []
            params['T-1日触板股票Sell'] = []
            params['T-1日形态4股票Sell'] = []
            params['T-1日筛选后形态4股票Sell'] = []
            params['T-1日筛选后形态2股票Sell'] = []
            params['形态2 T-3日~T-2日o2ul之和Sell'] = 0
            params['形态4 T-3日~T-2日o2ul之和Sell'] = 0
            params['T-3日~T-1日形态2样本总数量Sell'] = 0
            params['T-3日~T-1日形态4样本总数量Sell'] = 0   
        with open(commonPath+date+'/'+stock+'.json','w',encoding='utf-8') as f:
            jsonObj = json.dumps(params,cls = MyEncoder, ensure_ascii=False,indent=2)
            f.write(jsonObj)
            
generate_paramsJson()
# -*- coding: utf-8 -*-
import pandas as pd
import datetime
today = datetime.date.today()
date = today.strftime('%Y%m%d')
#date = '20221104'
pd.set_option('display.max_columns', 20)
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.width', 180)

prod_params = pd.read_excel(r'/data/group/800463/xiely/daily/excels/param-%s-prod-O45-SZ-new.xlsx'%date, sheet_name = None)
#prod_params = pd.read_excel(r'/data/group/800463/xiely/daily/excels/param-%s-prod-O45-SH-new.xlsx'%date, sheet_name = None)

def check_jupiter(prod_param, Flag):
    Flag_SH_SZ = (prod_param['股票代码'].str.endswith('.SH'))
    Flag_isCyb = (prod_param['股票代码'].str.startswith('30'))
    print(Flag)
    print('参数总数量：', len(prod_param))
    print(prod_param.count()[prod_param.count()!=len(prod_param)], '前一日收盘涨停数量: ',prod_param['前一日是否收盘涨停'].sum())
    for col in ['参数目录','JupiterNew模型目录','取消订阅非必要行情时间','允许卖出结束时间',\
                '交易所监控的时间长度(秒)','距离第一次触发最大下单延时毫秒数','交易所监控的涨跌幅范围','下单前Tick最大延时毫秒数','jupiter是否反向卖出',\
                'JupiterN买入下单方式','JupiterNew买入下单方式',\
                'saturn和ceres是否反向买入','saturn和ceres是否反向卖出','saturn和ceres挂单后jupiter是否需要加仓','是否触发预热',\
                '突破后涨停板挂单被防对敲后再次尝试次数','早盘延时tick截止时间点','买入成交量占比上边界','模型预热次数','五日流动性限制额','当日触发前流动性限制系数','最后一笔买单拉升幅度阈值','强制撤单时间点']:
        print(col+': max', prod_param[col].max(), '   min',prod_param[col].min())
    
    for col in ['下单前Trade最大延时毫秒数','交易所监控的较大额度','交易所监控的较大额度']:
        print(len(prod_param[Flag_SH_SZ]),'SH%s: max'%col, prod_param[Flag_SH_SZ][col].max(), '   min',prod_param[Flag_SH_SZ][col].min())
        print(len(prod_param[~Flag_SH_SZ]),'SZ%s: max'%col, prod_param[~Flag_SH_SZ][col].max(), '   min',prod_param[~Flag_SH_SZ][col].min())   
        
    print('股票代码==订阅消息Key ', len(prod_param[prod_param['股票代码']==prod_param['订阅消息Key']]))     
    
    for col in ['最大涨跌幅度','拆单笔数上限']:
        print(len(prod_param[Flag_isCyb]),'Cyb %s: max'%col, prod_param[Flag_isCyb][col].max(), '   min',prod_param[Flag_isCyb][col].min())
        print(len(prod_param[~Flag_isCyb]),'~Cyb %s: max'%col, prod_param[~Flag_isCyb][col].max(), '   min',prod_param[~Flag_isCyb][col].min())

    for name in ['NL1目标金额','NL2目标金额','NL3目标金额','NL4目标金额','NL5目标金额',\
        'NL1目标金额_add','NL2目标金额_add','NL3目标金额_add','NL4目标金额_add','NL5目标金额_add',\
        'NewL1目标金额','NewL2目标金额','NewL3目标金额','NewL4目标金额','NewL5目标金额',\
        'mrisk下单模式','mrisk拆单间隔毫秒数','Jupiter拆单v2单笔下单金额上限','mrisk重新下单等待时长(毫秒)','对敲重新下单等待时长(毫秒)']:
        print(name+': max', prod_param[name].max(), '   min',prod_param[name].min())
    ycbd_5_list = pd.read_excel(r'/data/group/800463/stock_list/ycbd_list/ycbd_list_%s.xlsx'%date)
    ycbd_5_list = ycbd_5_list['stk_code'].values.tolist()
    isin_ycbd_5 = (prod_param['股票代码'].isin(ycbd_5_list))
    print('ycbd_5_len: ', len(prod_param[isin_ycbd_5]), len(prod_param[~isin_ycbd_5]))
    print('ycbd_5 单票持仓总规模上限: max', prod_param[isin_ycbd_5]['单票持仓总规模上限'].max(), '   min',prod_param[isin_ycbd_5]['单票持仓总规模上限'].min())
    print('not_ycbd_5 单票持仓总规模上限: max', prod_param[~isin_ycbd_5]['单票持仓总规模上限'].max(), '   min',prod_param[~isin_ycbd_5]['单票持仓总规模上限'].min())

    for sum_col in ['是否使用原有卖出逻辑','是否使用静态数据查询','是否需要买入','小单测试','自营买单查询预热','jupiter因子是否串行计算']:
        print(sum_col + ' sum', prod_param[sum_col].sum())      
    print(prod_param['Jupiter策略启动组合'].value_counts())
    print('是否验证模式=0 sum: ', len(prod_param[prod_param['是否验证模式']==0]))
#    print('Event开关=1 sum: ', len(prod_param[prod_param['Event开关']==1]))
    print(prod_param[prod_param['是否验证模式']==1][['股票代码','期初可用仓位','saturn历史因子']])
    jupiter_beforeTFactors = prod_param['因子数据'].apply(lambda x: 1 if 'nan' in x else 0)
    jupiter_beforeTFactors_num = prod_param['因子数据'].apply(lambda x: len(x.split(';')))
    print('jupiter T-1日含有nan因子的数目: ' + str(jupiter_beforeTFactors.sum()))
    print('jupiter T-1日因子的个数: min ' + str(jupiter_beforeTFactors_num.min()) + ', max ' + str(jupiter_beforeTFactors_num.max()))

    europa_beforeTFactors = prod_param['europa历史因子'].apply(lambda x: 1 if 'nan' in x else 0)
    europa_beforeTFactors_num = prod_param['europa历史因子'].apply(lambda x: len(x.split(';')))
    print('europa T-1日含有nan因子的数目: ' + str(europa_beforeTFactors.sum()))
    print('europa T-1日因子的个数: min ' + str(europa_beforeTFactors_num.min()) + ', max ' + str(europa_beforeTFactors_num.max()))

    saturn_beforeTFactors = prod_param['saturn历史因子'].dropna().apply(lambda x: 1 if 'nan' in x else 0)
    saturn_beforeTFactors_num = prod_param['saturn历史因子'].dropna().apply(lambda x: len(x.split(';')))
    print('saturn T-1日含有nan因子的数目: ' + str(saturn_beforeTFactors.sum()))
    print('saturn T-1日因子的个数: min ' + str(saturn_beforeTFactors_num.min()) + ', max ' + str(saturn_beforeTFactors_num.max()))

    ceres_beforeTFactors = prod_param['ceres历史因子'].dropna().apply(lambda x: 1 if 'nan' in x else 0)
    ceres_beforeTFactors_num = prod_param['ceres历史因子'].dropna().apply(lambda x: len(x.split(';')))
    print('ceres T-1日含有nan因子的数目: ' + str(ceres_beforeTFactors.sum()))
    print('ceres T-1日因子的个数: min ' + str(ceres_beforeTFactors_num.min()) + ', max ' + str(ceres_beforeTFactors_num.max()))
    
    
    sell_beforeTFactors = prod_param['sell历史因子'].dropna().apply(lambda x: 1 if 'nan' in x else 0)
    sell_beforeTFactors_num = prod_param['sell历史因子'].dropna().apply(lambda x: len(x.split(';')))
    print('sell T-1日含有nan因子的数目: ' + str(sell_beforeTFactors.sum()))
    if sell_beforeTFactors.sum()>0:
        print('sell T-1_nan: ', prod_param[prod_param['sell历史因子'].fillna(' ').str.contains('nan')]['股票代码'].values)
    print('sell T-1日因子的个数: min ' + str(sell_beforeTFactors_num.min()) + ', max ' + str(sell_beforeTFactors_num.max()))

    print('自营接口异常是否打印客户端: max', prod_param['自营接口异常是否打印客户端'].max(), '   min',prod_param['自营接口异常是否打印客户端'].min(), ' sum',prod_param['自营接口异常是否打印客户端'].sum())
    print('是否打印Trade信息: max', prod_param['是否打印Trade信息'].max(), '   min',prod_param['是否打印Trade信息'].min(), ' sum',prod_param['是否打印Trade信息'].sum())
    print('期初持仓不为0数目: ', (prod_param['期初可用仓位']!=0).astype(int).sum())
    print('期初持仓不为0数目: ', (prod_param[prod_param['期初可用仓位']!=0]['股票代码'].values.tolist()))
    print('不需要买入票: ', (prod_param[prod_param['是否需要买入']==0]['股票代码'].values.tolist()))
  
    for name in ['单标的tick截取毫秒数','买入的巨大额度','买入的巨大股数','撤单监控的巨大额度','撤单监控的巨大股数','Jupiter首次下单量下限','Jupiter首次下单市场占比','最近一笔查询是否使用委托','买入成交量占比上边界(无拉抬)','交易所监控的较大股数(无拉抬)','交易所监控的较大额度(无拉抬)','交易所监控的反向交易涨跌幅范围']:
        print(name+': max', prod_param[name].max(), '   min',prod_param[name].min())

def check_other_sheet(p_params, sheet_names):
    for sheet_name in sheet_names:
        p_param = p_params[sheet_name]
        if len(p_param)>len(p_param.dropna()):
            print(sheet_name+' has NAN.', '\n', p_param[p_param.isnull().T.any()])
    
def check_saturn(prod_param, Flag):
    Flag_isCyb = (prod_param['股票代码'].str.startswith('30'))
    print('\n'+Flag)
    print('参数总数量：', len(prod_param))
    print('saturn模型目录: max', prod_param['模型目录'].max(), '   min',prod_param['模型目录'].min())
    print('saturn节点标识: max', prod_param['saturn节点标识'].max(), '   min',prod_param['saturn节点标识'].min(), ' 930', (prod_param['saturn节点标识']==930).astype(int).sum(), ' 931',(prod_param['saturn节点标识']==931).astype(int).sum())
    print('计算和预测开始时间: max', prod_param['计算和预测开始时间'].max(), '   min',prod_param['计算和预测开始时间'].min())
    print('买入开始时间: max', prod_param['买入开始时间'].max(), '   min',prod_param['买入开始时间'].min())
    print('saturn策略样本筛选阈值: max', prod_param['saturn策略样本筛选阈值'].max(), '   min',prod_param['saturn策略样本筛选阈值'].min())
    
    print(len(prod_param[Flag_isCyb]),'Cyb o2pre阈值: max', prod_param[Flag_isCyb]['o2pre阈值'].max(), '   min',prod_param[Flag_isCyb]['o2pre阈值'].min())
    print(len(prod_param[~Flag_isCyb]),'~Cyb o2pre阈值: max', prod_param[~Flag_isCyb]['o2pre阈值'].max(), '   min',prod_param[~Flag_isCyb]['o2pre阈值'].min())

    columns = ['区间目标金额','投票2目标金额','投票3目标金额','投票4目标金额','投票5目标金额','投票6目标金额','投票大于等于7目标金额',\
    '投票2目标金额add','投票3目标金额add','投票4目标金额add','投票5目标金额add','投票6目标金额add','投票大于等于7目标金额add']
    for c in columns: 
        print('%s: max'%c, prod_param[c].max(), '   min',prod_param[c].min())
        
def check_sell(prod_param, Flag):
    print('\n'+Flag)
    print('参数总数量：', len(prod_param))
    print('v1模型目录: max', prod_param['v1模型目录'].max(), '   min',prod_param['v1模型目录'].min())
    print('v3模型目录: max', prod_param['v3模型目录'].max(), '   min',prod_param['v3模型目录'].min())
    print('sell节点标识: max', prod_param['sell节点标识'].max(), '   min',prod_param['sell节点标识'].min(), ' 930', (prod_param['sell节点标识']==930).astype(int).sum(), ' 931',(prod_param['sell节点标识']==931).astype(int).sum())
    print('计算和预测开始时间: max', prod_param['计算和预测开始时间'].max(), '   min',prod_param['计算和预测开始时间'].min())
    

    columns = ['v1阈值','v3阈值']
    for c in columns: 
        print('%s: max'%c, prod_param[c].max(), '   min',prod_param[c].min())
 
def check_ceres(prod_param, Flag):
    print('\n'+Flag)
    print('参数总数量：', len(prod_param))
    print('ceres模型目录: max', prod_param['模型目录'].max(), '   min',prod_param['模型目录'].min())
    print('ceres节点标识: max', prod_param['ceres节点标识'].max(), '   min',prod_param['ceres节点标识'].min(), ' 930', (prod_param['ceres节点标识']==930).astype(int).sum(), ' 931',(prod_param['ceres节点标识']==931).astype(int).sum())
    print('计算和预测开始时间: max', prod_param['计算和预测开始时间'].max(), '   min',prod_param['计算和预测开始时间'].min())
    print('买入开始时间: max', prod_param['买入开始时间'].max(), '   min',prod_param['买入开始时间'].min())
    
    columns = ['区间目标金额','投票2目标金额','投票3目标金额','投票4目标金额','投票5目标金额','投票6目标金额']
    for c in columns: 
        print('%s: max'%c, prod_param[c].max(), '   min',prod_param[c].min())


    
check_jupiter(prod_params['InitialBasicParam'], 'prod-jupiter')
check_other_sheet(prod_params, set(prod_params.keys())-set(['InitialBasicParam','saturn配置参数','ceres配置参数']))
saturn_param = prod_params['saturn配置参数']
ceres_param = prod_params['ceres配置参数']
sell_param = prod_params['sell配置参数']
check_saturn(saturn_param[saturn_param['saturn节点标识']==930], 'saturn-S0')
check_saturn(saturn_param[saturn_param['saturn节点标识']==931], 'saturn-S1')
check_ceres(ceres_param[ceres_param['ceres节点标识']==930], 'ceres-S1')
check_ceres(ceres_param[ceres_param['ceres节点标识']==931], 'ceres-S1')
check_sell(sell_param[sell_param['sell节点标识']==930], 'sell-S0')
check_sell(sell_param[sell_param['sell节点标识']==931], 'sell-S1')
import pandas as pd
import numpy as np
import os
import datetime
from multifactor.data.utils import *
import warnings
import multifactor.utility.dt as udt
from multifactor.data.utils import *
from xquant.xqutils.helper import link
import json

warnings.filterwarnings("ignore")
_,eedate,date_list = check_update_date()
edate = str(eedate)

user_ids = [
        '012315',
        '012398',
        '015626',  
        '016700',
        '017024',
        '020529'

    ]

for edate in date_list:
    date = udt.get_trading_day_offset(edate,1)[0].strftime('%Y%m%d')
    print(date)
    b = date
    yesterday = str(udt.get_trading_day_offset(b, -1)[0])[:10].replace('-','')

    



    def path_check(b = b):
        path1 = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/settlements/%s.pkl'%b
        path2 = '/data/user/011477/order/O32/51606/综合信息查询_成交回报明细_%s_51606.xls'%b
        if os.path.exists(path1) and os.path.exists(path2):
            return True
        else:
            return False

    print('------wait data flag')
    while True:
        if path_check(date):
            break
        time.sleep(5)


    settle_today = pd.read_pickle('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/settlements/%s.pkl'%date)['settle'].to_frame()
    settle_today['证券代码'] = settle_today.index


    ddata = pd.read_hdf('/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_SIF_TICK_TO_DAILY_ALL_CONTRACT.h5').reset_index().set_index('dt')
    ddata.Ticker = ddata.Ticker.apply(lambda x: x[:-4])

    for category in ['IC', 'IF', 'IM']:
        ticker = category + '.CF'
        tc = 0
        pnl = 0
        contract_traded = 0
        amount_traded = 0
        trade_profit = 0

        if category == 'IC':
            beishu = 200
            trail = ''
            machine_list = ['#503301']
        elif category == 'IF':
            beishu = 300
            trail = '_if'
            machine_list = ['#503302']
        elif category == 'IM':
            beishu = 200
            trail = '_im'
            machine_list = ['#503303'] 

        for machine in machine_list:   
            #future_traded = [item[:-3] for item in list(pd.read_excel('/data/user/016700/Data/para/Mobius_%s/MobiusStrategy_%s_%s.xlsx'%(str(b).replace('-', ''), category, str(b).replace('-', '') + machine), sheetname = '期初持仓列表')['合约代码'])]
            print('/data/user/011477/order/O32/51606/综合信息查询_成交回报明细_%s_51606.xls'%b)
            trading_stats = pd.read_excel('/data/user/011477/order/O32/51606/综合信息查询_成交回报明细_%s_51606.xls'%b)
            trading_stats = trading_stats.loc[trading_stats['日期'].isna() == False]
            trading_stats['成交时间1'] = pd.to_datetime(trading_stats['成交时间'].apply(lambda x: (b + str(x).replace(':', ''))[:-2]))
            future_traded = [item for item in ddata['Ticker'].loc[yesterday] if category.upper() in item]

            if category == 'IC':
                FLAG = 1
                trading_stats = trading_stats[(trading_stats['证券代码'].isin(future_traded))&(trading_stats['组合编号'].isin([5160602, 5160702])) & (trading_stats['操作员'].isin(['张玮聪'])) & (trading_stats['成交时间1'] >= pd.to_datetime(b + '0939')) & (trading_stats['成交时间1'] <= pd.to_datetime(b + '1450'))].sort_values(by = '成交时间')
            elif category == 'IM':
                FLAG = 0
                trading_stats = trading_stats[(trading_stats['证券代码'].isin(future_traded))&(trading_stats['组合编号'].isin([5160701, 5160702])) & (trading_stats['成交时间1'] >= pd.to_datetime(b + '0930')) & (trading_stats['成交时间1'] <= pd.to_datetime(b + '1455'))].sort_values(by = '成交时间')
            else:
                FLAG = 1
                trading_stats = trading_stats[(trading_stats['证券代码'].isin(future_traded))&(trading_stats['组合编号'].isin([5160701, 5160702])) & (trading_stats['操作员'].isin(['张玮聪'])) & (trading_stats['成交时间1'] >= pd.to_datetime(b + '0939')) & (trading_stats['成交时间1'] <= pd.to_datetime(b + '1450'))].sort_values(by = '成交时间')

            def direction(x):
                if '买'  in x:
                    return 1
                elif '卖' in x:
                    return -1
                else:
                    pass

            df_trade = trading_stats.set_index('成交时间1')
            df_trade.index.name = 'dt'

            settle = settle_today.loc[future_traded]
            settle_yesterday = ddata[ddata.Ticker.isin(future_traded)].loc[yesterday, ['Ticker', 'settle']]

            try:
                trading_stats['发生金额(全价)'] = trading_stats['发生金额(全价)'].apply(lambda x:float(x.replace(',', '')))
                print('#')
            except:
                pass

            if len(np.shape(settle)) == 1:
                settle = settle.to_frame().T



            if len(np.shape(settle_yesterday)) == 1:
                settle_yesterday = settle_yesterday.to_frame().T

            tomorrow = str(udt.get_trading_day_offset(b, 1)[0])[:10].replace('-','')

            print('/data/user/011477/order/tradingReport/tradingStat_%s.xlsx'%yesterday)
            dfff = pd.read_excel('/data/user/011477/order/tradingReport/tradingStat_%s.xlsx'%yesterday, sheet_name='Tri_51606')#.set_index('委托方向')
            l = dfff['组合名称']
            l = [item for item in l if ('5160702' in item)][0]
            positions = dfff[dfff['组合名称'] == l]['期货持仓'].iloc[0]
            dic_temp = json.loads(positions.replace("'", '"'))

            contract_temp_list = list(settle.index)

            df_para = pd.DataFrame(index = list(set([item for item in contract_temp_list])), columns = ['多头持仓','空头持仓'])

            for key in contract_temp_list:
                if ticker[:2] in key:
                    if FLAG == 0:
                        try:   

                            df_para.loc[key, '多头持仓'] = dic_temp[key + '多仓']
                        except:
                            df_para.loc[key, '多头持仓'] = 0
                        try:    
                            df_para.loc[key, '空头持仓'] = dic_temp[key + '空仓']
                        except:
                            df_para.loc[key, '空头持仓'] = 0
                    else:
                        try:   

                            dtcc = dic_temp[key + '多仓']
                        except:
                            dtcc = 0
                        try:    
                            ktcc = dic_temp[key + '空仓']
                        except:
                            ktcc = 0

                        dkcc = np.nanmin([dtcc, ktcc])
                        df_para.loc[key, '多头持仓'] = dkcc
                        df_para.loc[key, '空头持仓'] = dkcc

            df_para = df_para.sort_index().fillna(0)

            ts_temp = trading_stats[['证券代码', '发生金额(全价)','成交数量', '委托方向']].set_index('证券代码')
            ts_temp['发生金额']  = ts_temp['发生金额(全价)'] / beishu
            dffff = ts_temp.join(settle_today)
            trade_profit_temp = ((-np.sign(dffff['发生金额']) * (dffff['settle'] * dffff['成交数量'] - abs(dffff['发生金额']))) * beishu).sum()
            holding_yesterday = ((df_para['多头持仓'] - df_para['空头持仓']) * settle_yesterday.set_index('Ticker')['settle']).sum() * beishu
            holding_today = ((df_para['多头持仓'] - df_para['空头持仓']) * settle_today['settle']).sum() * beishu
            tc_temp = abs(ts_temp['发生金额(全价)']).sum() * 0.00002323

            pnl_temp = trade_profit_temp + (holding_today - holding_yesterday) - tc_temp
            trade_profit = trade_profit_temp + trade_profit
            df = pd.DataFrame()
            df['成交时间'] = trading_stats['成交时间']
            df['合约'] = trading_stats['证券名称']
            df['成交价'] = trading_stats['成交价格']
            df['成交量'] = trading_stats['成交数量']
            df['发生金额'] = trading_stats['发生金额(全价)']
            df['委托方向'] = trading_stats['委托方向']
            df = df.set_index('成交时间')
            df['交易费用'] = df['成交量'] * df['成交价'] * beishu * 0.000023 * 1.01
            #df.to_excel('/data/group/800466/warehouse/prod/tradingstats/Mobius/log_%s.xlsx'%b)
            contract_traded_temp = trading_stats[trading_stats['委托方向'].isin(['买入平仓', '买入开仓'])]['成交数量'].sum()
            amount_traded_temp = abs(trading_stats[trading_stats['委托方向'].isin(['买入平仓', '买入开仓'])]['发生金额(全价)'].sum())

            tc = tc + tc_temp 
            pnl = pnl + pnl_temp
            contract_traded = contract_traded + contract_traded_temp
            amount_traded = amount_traded + amount_traded_temp

        pnl_df = pd.DataFrame()
        pnl_df['date'] = [datetime.datetime.strptime(str(b),"%Y%m%d")]
        pnl_df['pnl'] = [pnl]
        pnl_df['trading_pnl'] = [trade_profit]
        print(category, pnl)
        pnl_df = pnl_df.set_index('date')
        pnl_df['transaction_cost'] = tc
        pnl_df['单边金额总数（买入）'] = amount_traded
        pnl_df['contracts_traded'] = contract_traded

        pnl_df_fh = pd.read_excel('/data/group/800466/warehouse/prod/tradingstats/Mobius/pnl%s.xlsx'%trail, index_col = 0, date_parser = True)
        if 'contracts_traded' not in pnl_df.columns:
            pnl_df['contracts_traded'] = 0
            pnl_df['单边金额总数（买入）'] = np.nan

        tempdf = pd.concat([pnl_df_fh, pnl_df]).sort_index()
        tempdf = tempdf[~tempdf.index.duplicated(keep='last')]
        tempdf.to_excel('/data/group/800466/warehouse/prod/tradingstats/Mobius/pnl%s.xlsx'%trail)


        lm = link.LinkMessage(user_ids)
        lm.sendMessage('%s: %s万'%(category, round(pnl / 10000, 2)))
        del lm

# -*- coding: utf-8 -*-
from xquant.factordata import FactorData
s = FactorData()
from xquant.thirdpartydata.multifactor.IO import *
from xquant.marketdata import MarketData
mdp = MarketData()

def change_code_for_mdp(code, date):
    if (code == '601360.SH') and (date < '20180228'):
        return '601313.SH'
    elif (code == '001872.SZ') and (date < '20181226'):
        return '000022.SZ'
    else:
        return code


def hf_preprocessing(data_type, md_df, btTime=None):
    if (data_type == 'Stock') or (data_type == 'StockAllDay') or (data_type == 'StockAllDayNoTradingPhaseCode'):  # TICK
        use_col = ['MDDate', 'MDTime', 'HTSCSecurityID', 'TradingPhaseCode', 'PreClosePx', 'NumTrades',
                   'TotalVolumeTrade', 'TotalValueTrade', 'LastPx', 'OpenPx', 'ClosePx', 'HighPx', 'LowPx', 'MaxPx',
                   'MinPx', 'TotalBidQty', 'TotalOfferQty', 'WeightedAvgBidPx', 'WeightedAvgOfferPx'] + \
                  ['Buy%dPrice' % (i) for i in range(1, 11)] + ['Sell%dPrice' % (i) for i in range(1, 11)] + \
                  ['Buy%dOrderQty' % (i) for i in range(1, 11)] + ['Sell%dOrderQty' % (i) for i in range(1, 11)] + \
                  ['Buy%dNumOrders' % (i) for i in range(1, 11)] + ['Sell%dNumOrders' % (i) for i in range(1, 11)] + \
                  ['Buy1NoOrders', 'Buy1OrderDetail', 'Sell1NoOrders', 'Sell1OrderDetail']
        md_df = md_df[use_col]
        md_df['vol'] = md_df['TotalVolumeTrade'] - md_df['TotalVolumeTrade'].shift(1)
        md_df['amt'] = md_df['TotalValueTrade'] - md_df['TotalValueTrade'].shift(1)
        '''
        1:集合竞价；2:集合竞价最后一条；3:连续竞价；4:上午连续竞价最后一条；5:尾盘集合竞价；6:收盘最后一条
        '''
        if data_type != 'StockAllDayNoTradingPhaseCode':
            md_df = pd.concat([md_df[md_df['TradingPhaseCode'] == '1'],
                               md_df[md_df['TradingPhaseCode'] == '2'],#.drop_duplicates(['TradingPhaseCode'], keep='first'),
                               md_df[md_df['TradingPhaseCode'] == '3'],
                               md_df[md_df['TradingPhaseCode'] == '4'].drop_duplicates(['TradingPhaseCode'], keep='first'),
                               md_df[md_df['TradingPhaseCode'] == '5'],
                               md_df[md_df['TradingPhaseCode'] == '6'].drop_duplicates(['TradingPhaseCode'], keep='first'),
                               ]).sort_values(by='MDTime').reset_index(drop=True)
        md_df['MDTime'] = md_df['MDTime'].astype(int)
        if data_type == 'Stock':
            md_df = md_df[md_df['MDTime'] <= btTime]  # 泛强势股的数据筛选
        elif data_type == 'StockAllDay':
            md_df = md_df  # 使用全部的数据
        # tick去重
        repeat_filter_cols = ['NumTrades', 'TotalVolumeTrade', 'TotalValueTrade', 'LastPx', 'TotalBidQty', 'TotalOfferQty',
                              'WeightedAvgBidPx', 'WeightedAvgOfferPx', 'TradingPhaseCode'] + \
                             ['Buy%dPrice' % (i) for i in range(1, 11)] + ['Sell%dPrice' % (i) for i in range(1, 11)] + \
                             ['Buy%dOrderQty' % (i) for i in range(1, 11)] + ['Sell%dOrderQty' % (i) for i in range(1, 11)]

        def find_repeat_tick(tick_data, repeat_filter_cols):
            tick_data['inf_str'] = tick_data[repeat_filter_cols].apply(lambda x: str(x.values), axis=1)
            tick_data['last_inf_str'] = tick_data['inf_str'].shift(1)
            return tick_data['inf_str'] == tick_data['last_inf_str']

        # md_df['repeat_filter'] = find_repeat_tick(md_df.copy(), repeat_filter_cols)
        # md_df = md_df[~md_df['repeat_filter']]
        md_df = md_df[md_df['MDTime'] >= 91500000]
        return md_df
    elif data_type == 'Index':
        use_col = ['MDTime', 'PreClosePx', 'LastPx', 'OpenPx', 'ClosePx', 'HighPx', 'LowPx', 'HTSCSecurityID']
        md_df = md_df[use_col]
        md_df['MDTime'] = md_df['MDTime'].astype(int)
        md_df = md_df[md_df['MDTime'] <= btTime]  # 泛强势股的数据筛选
        return md_df
    elif data_type == 'WMinute':  # 前N日的分钟数据，不包括当日
        use_col = ['HTSCSecurityID', 'MDDate', 'MDTime', 'OpenPx', 'ClosePx', 'HighPx', 'LowPx', 'NumTrades',
                   'TotalVolumeTrade', 'TotalValueTrade']
        md_df = md_df[use_col]
        md_df['MDTime'], md_df['MDDate'] = md_df['MDTime'].astype(int), md_df['MDDate'].astype(int)
        return md_df
    elif data_type in ['Transaction', 'TransactionAllDay']:  # 逐笔成交
        use_col = ['MDDate', 'MDTime', 'TradeIndex', 'TradeBuyNo', 'TradeSellNo', 'TradeType', 'TradeBSFlag', 'TradePrice', 'TradeQty', 'TradeMoney',
                   'HTSCSecurityID']
        md_df = md_df[use_col]
        md_df['MDTime'], md_df['MDDate'] = md_df['MDTime'].astype(int), md_df['MDDate'].astype(int)
        # 处理'TradeBSFlag'
        temp_BSFlag = md_df['TradeBSFlag'].copy()
        temp_BSFlag[md_df['TradeBuyNo'] < md_df['TradeSellNo']] = 2.0
        temp_BSFlag[md_df['TradeBuyNo'] > md_df['TradeSellNo']] = 1.0
        md_df['TradeBSFlag'] = temp_BSFlag
        md_df.loc[md_df['MDTime'] < 92900000, 'TradeBSFlag'] = 0
        md_df['TradeMoney'] = md_df['TradePrice'] * md_df['TradeQty']
        if data_type == 'TransactionAllDay':
            return md_df
        elif data_type == 'Transaction':
            return md_df[md_df['MDTime'] <= btTime]
    elif data_type in ['OrderAllDay']:
        md_df = md_df.rename(columns={'OrderNo': 'OrderIndex'})[
            ['MDDate', 'MDTime', 'OrderIndex', 'OrderPrice', 'OrderQty', 'OrderBSFlag', 'HTSCSecurityID']]
        md_df = md_df[md_df['OrderPrice'] > 0]
        md_df['MDTime'] = md_df['MDTime'].astype(int)
        return md_df

def check_dir(path):  # 路径生成函数
    if not os.path.exists(path):
        os.makedirs(path)

def store_hf_data_for_one_day(date, Basic_next_hf_finish, cut_MDTime, result_path_tick, result_path_transaction):
    tradingday = str(date)
    print(tradingday, cut_MDTime, 'data storing.......')
    basic_data_in_the_day = Basic_next_hf_finish.loc[pd.Timestamp(tradingday)]
    tick_data_of_the_day = pd.DataFrame()
    transaction_data_of_the_day = pd.DataFrame()
    for index, row in basic_data_in_the_day.reset_index().iterrows():
        print(index)
        stock = row['Ticker']
        pre_close = row['pre_close']
        ff_shares = row['float_shares']
        # lzt_label_pattern = row['lzt_label_pattern']
        # after_not_ul_len = row['after_not_ul_len']
        mdp_code = change_code_for_mdp(code=stock, date=tradingday)
        try:
            tick_md_df = mdp.get_data_by_date('Stock', mdp_code, tradingday)
            tick_md_df['MDTime'] = tick_md_df['MDTime'].astype(int)
            tick_md_df = hf_preprocessing('StockAllDay', tick_md_df)
            used_cols = ['MDDate', 'MDTime', 'HTSCSecurityID', 'TradingPhaseCode', 'NumTrades',
                 'TotalVolumeTrade', 'TotalValueTrade', 'LastPx', 'HighPx', 'LowPx',
                 'TotalBidQty', 'TotalOfferQty', 'WeightedAvgBidPx', 'WeightedAvgOfferPx'] + \
                ['Buy%dPrice' % (i) for i in range(1, 11)] + ['Sell%dPrice' % (i) for i in range(1, 11)] + \
                ['Buy%dOrderQty' % (i) for i in range(1, 11)] + ['Sell%dOrderQty' % (i) for i in range(1, 11)] + \
                ['Buy%dNumOrders' % (i) for i in range(1, 11)] + ['Sell%dNumOrders' % (i) for i in range(1, 11)]
            tick_md_df = tick_md_df[used_cols]
            available_tick_data=tick_md_df[tick_md_df['MDTime']<cut_MDTime]

            # transaction_md_df = hf_preprocessing('TransactionAllDay', mdp.get_data_by_date('Transaction', mdp_code, tradingday))
            # available_transaction_data = transaction_md_df[transaction_md_df['MDTime'] < cut_MDTime]

            available_tick_data['pre_close'] = pre_close
            available_tick_data['ff_shares'] = ff_shares
            # available_tick_data['lzt_label_pattern'] = lzt_label_pattern
            # available_tick_data['after_not_ul_len'] = after_not_ul_len

            # available_transaction_data['pre_close'] = pre_close
            # available_transaction_data['ff_shares'] = ff_shares
            # available_transaction_data['lzt_label_pattern'] = lzt_label_pattern
            # available_transaction_data['after_not_ul_len'] = after_not_ul_len


            tick_data_of_the_day = pd.concat([tick_data_of_the_day, available_tick_data])
            # transaction_data_of_the_day = pd.concat([transaction_data_of_the_day, available_transaction_data])

        except Exception as e:
            print(stock, tradingday, e)
            pass
    tick_data_of_the_day['dt'] = tick_data_of_the_day['MDDate'].apply(lambda x: pd.Timestamp(x))
    tick_data_of_the_day['Ticker'] = tick_data_of_the_day['HTSCSecurityID']
    tick_data_of_the_day = tick_data_of_the_day.set_index(['dt', 'Ticker']).drop(columns=['MDDate','HTSCSecurityID'])
    tick_data_of_the_day.to_pickle(result_path_tick + str(tradingday) + '.pkl')

    # transaction_data_of_the_day['dt'] = transaction_data_of_the_day['MDDate'].apply(lambda x: pd.Timestamp(str(x)))
    # transaction_data_of_the_day['Ticker'] = transaction_data_of_the_day['HTSCSecurityID']
    # transaction_data_of_the_day = transaction_data_of_the_day.set_index(['dt', 'Ticker']).drop(columns=['MDDate','HTSCSecurityID'])
    # transaction_data_of_the_day.to_pickle(result_path_transaction + str(tradingday) + '.pkl')

if __name__ == '__main__':
    from multiprocessing import Pool
    # from multiprocessing.pool import ThreadPool as Pool
    from xquant.factordata import FactorData
    s = FactorData()

    result_path_tick='/dfs/user/015585/20241210-P4基础数据/tick_allday/'
    result_path_transaction='/dfs/user/015585/20241210-P4基础数据/trade_931/'
    if not os.path.exists(result_path_tick):
        os.makedirs(result_path_tick)
    # if not os.path.exists(result_path_transaction):
    #     os.makedirs(result_path_transaction)

    pool = Pool(30)
    task_list = []
    # all_Basic_next_hf_finish = pd.read_pickle('/data/user/015585/01-因子挖掘/20230703-暑期实习生数据准备/code/filter_df.pkl').sort_index()
    all_Basic_next_hf_finish = pd.read_pickle('/data/user/018107/share_file/for_qyh/basic_p4_20160101_20191231.pkl').sort_index()
    print(f'样本数量：{all_Basic_next_hf_finish.shape}')
    for tradingday in s.tradingday('20160101', '20191231'):
        Basic_next_hf_finish = all_Basic_next_hf_finish.loc[pd.Timestamp(tradingday):pd.Timestamp(tradingday)]
        task_list.append(pool.apply_async(store_hf_data_for_one_day,args=(tradingday,
                                                         Basic_next_hf_finish,
                                                         153000000,
                                                         result_path_tick,
                                                         result_path_transaction)))
        # store_hf_data_for_one_day(tradingday,Basic_next_hf_finish,94000000,result_path_tick,result_path_transaction)
    pool.close()
    pool.join()
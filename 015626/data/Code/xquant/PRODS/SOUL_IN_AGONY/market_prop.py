def calc(item, cat = cat):
    try:
        tempdf = pd.read_excel(item, encoding = 'gbk', sheetname = 'InitialBasicParam')
        date = str(tempdf['交易日期'][0])
        jyzh = tempdf['买入交易账户'][0]
        trading_stats = pd.read_excel('/data/user/011477/order/O32/51606/综合信息查询_成交回报明细_%s_51606.xls'%date)
        trading_stats = trading_stats.loc[trading_stats['日期'].isna() == False]
        trading_stats['成交时间1'] = pd.to_datetime(trading_stats['成交时间'].apply(lambda x: (date + str(x).replace(':', ''))[:-2]))
        trading_stats = trading_stats[(trading_stats['组合编号'].isin([jyzh])) & (trading_stats['成交时间1'] >= pd.to_datetime(date + '0939')) & (trading_stats['成交时间1'] <= pd.to_datetime(date + '1450'))].sort_values(by = '成交时间')
        
        contract_list = list(set(trading_stats['证券代码']))
        contract_list = sorted([item for item in contract_list if cat in item])
        records = pd.DataFrame()
        for contract in contract_list:
            contract_temp = contract.replace(cat, '') + '.CFE'
            ts_temp = trading_stats[trading_stats['证券代码'] == contract]
            record_temp1 = ts_temp['成交数量'].groupby(ts_temp['成交时间1']).count()
            record_temp2 = record_temp1 / volume[contract_temp].loc[record_temp1.index]
            records = pd.concat([records, record_temp2])
        return records
    except:
        print(item)
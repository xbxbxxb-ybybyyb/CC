def aggregate_order_SH(order, transaction):
    orderdf = pd.DataFrame()
    if (len(order) > 100) & (len(transaction) > 100):
        order = reform_sh_order(order, transaction, append_cancel_orders=True)
        order['dt'] = order.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
        order['minute'] = order.dt.map(lambda x: x.replace(second=0,microsecond=0))
        order['otindex'] = order['OrderNO'] # 用来标记order的序号
        order = order[order.OrderPrice > 0]
        order['OrderAmt'] = order.OrderPrice * order.OrderQty

        # 处理非撤单
        transaction['tran_dt'] = transaction.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
        # transaction['tran_minute'] = transaction.tran_dt.map(lambda x: x.replace(second=0,microsecond=0))
        transaction = transaction[transaction.TradePrice != 0]
        transaction.loc[transaction.TradeBSFlag == 1, 'otindex'] = transaction['TradeSellNo']
        transaction.loc[transaction.TradeBSFlag == 2, 'otindex'] = transaction['TradeBuyNo']
        
#        order_tran_minute_info = get_order_tran_minute_info(order.copy(), transaction.copy())

        order_normal = order[order.OrderType != 10]
        order_tran_minute_info = get_order_tran_minute_info(order_normal.copy(), transaction.copy())
        order_normal = pd.merge(transaction[['tran_dt','TradeBuyNo', 'TradeSellNo', 'TradeType', 'TradeBSFlag', 'TradePrice', 'TradeQty', 'TradeMoney','otindex']], order_normal, on=['otindex'], how = 'outer')

        order_normal = order_normal.sort_values(by = 'tran_dt')
        order_normal['dt'] = order_normal['dt'].fillna(order_normal['tran_dt'])
        order_normal['hold_time'] = order_normal.apply(lambda x:get_order_holdtime(x['dt'], x['tran_dt']), axis = 1)
        order_normal_first = order_normal.drop_duplicates(subset='otindex', keep = 'first')
        order_normal = order_normal.drop_duplicates(subset='otindex', keep = 'last')
        order_normal_first['first_hold_time'] = order_normal_first['hold_time']
        order_normal = pd.merge(order_normal, order_normal_first[['first_hold_time','otindex']], how = 'left')
        order_normal['finish_time'] = order_normal['hold_time'] - order_normal['first_hold_time'] # 一个订单从开始交易到交易结束花了多久
        order_normal['tran_minute'] = order_normal.tran_dt.map(lambda x: x.replace(second=0,microsecond=0))

        # 处理撤单
        order_cancel = order[order.OrderType == 10]
        order_cancel_list = order_cancel.otindex.tolist()
        order_cancel_temp = order[order.otindex.isin(order_cancel_list)]
        order_cancel_temp = order_cancel_temp.groupby('otindex').agg({'dt':lambda x:get_order_holdtime(x.iloc[0], x.iloc[-1])})
        order_cancel_temp = order_cancel_temp.reset_index()
        order_cancel_temp.columns = ['otindex','hold_time']
        order_cancel = pd.merge(order_cancel, order_cancel_temp, on=['otindex'],how = 'left')
        
        orderdf = pd.concat([handle_normal_order(order_normal), handle_cancel_order(order_cancel), order_tran_minute_info], axis = 1)
    return orderdf

def get_order_tran_minute_info(order, transaction):
    transaction['tran_minute'] = transaction.tran_dt.map(lambda x: x.replace(second=0,microsecond=0))
    buy_order = order[order.OrderBSFlag == 1]
    sell_order = order[order.OrderBSFlag == 2]
    buy_order['TradeBuyNo'] = buy_order['otindex']
    sell_order['TradeSellNo'] = sell_order['otindex']

    buy_tranorder = pd.merge(transaction[['tran_dt','tran_minute','TradeBuyNo',  'TradeType', 'TradeBSFlag', 'TradePrice', 'TradeQty', 'TradeMoney']], buy_order, on=['TradeBuyNo'], how = 'left')
    sell_tranorder = pd.merge(transaction[['tran_dt','tran_minute','TradeSellNo', 'TradeType', 'TradeBSFlag', 'TradePrice', 'TradeQty', 'TradeMoney']], sell_order, on=['TradeSellNo'], how = 'left')
    buy_tranorder = buy_tranorder.sort_values(by = 'tran_dt')
    buy_tranorder['minute'] = buy_tranorder['minute'].fillna(buy_tranorder['tran_minute'])
    sell_tranorder = sell_tranorder.sort_values(by = 'tran_dt')
    sell_tranorder['minute'] = sell_tranorder['minute'].fillna(sell_tranorder['tran_minute'])

    buy_tranorder_thismin = buy_tranorder[buy_tranorder.tran_minute == buy_tranorder.minute]
    buy_tranorder_othermin = buy_tranorder[buy_tranorder.tran_minute != buy_tranorder.minute]

    sell_tranorder_thismin = sell_tranorder[sell_tranorder.tran_minute == sell_tranorder.minute]
    sell_tranorder_othermin = sell_tranorder[sell_tranorder.tran_minute != sell_tranorder.minute]

    buy_order_money_thismin = buy_tranorder_thismin.groupby(['minute', 'TradeBuyNo'])['TradeMoney','TradeQty'].sum().reset_index()
    buy_small_order_thismin = buy_order_money_thismin[buy_order_money_thismin.TradeMoney <= 40000]
    buy_mid_order_thismin = buy_order_money_thismin[(buy_order_money_thismin.TradeMoney > 40000) & (buy_order_money_thismin.TradeMoney <= 200000)]
    buy_big_order_thismin = buy_order_money_thismin[(buy_order_money_thismin.TradeMoney > 200000) & (buy_order_money_thismin.TradeMoney <= 1000000)]
    buy_super_order_thismin = buy_order_money_thismin[(buy_order_money_thismin.TradeMoney > 1000000)]
    buy_small_order_thismin = buy_small_order_thismin.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_smallorder_count_thismin','TradeMoney':'buy_smallorder_money_thismin','TradeQty':'buy_smallorder_volume_thismin'})
    buy_mid_order_thismin = buy_mid_order_thismin.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_midorder_count_thismin','TradeMoney':'buy_midorder_money_thismin','TradeQty':'buy_midorder_volume_thismin'})
    buy_big_order_thismin = buy_big_order_thismin.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_bigorder_count_thismin','TradeMoney':'buy_bigorder_money_thismin','TradeQty':'buy_bigorder_volume_thismin'})
    buy_super_order_thismin = buy_super_order_thismin.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_superorder_count_thismin','TradeMoney':'buy_superorder_money_thismin','TradeQty':'buy_superorder_volume_thismin'})

    buy_tranorder_othermin['minute'] = buy_tranorder_othermin['tran_minute']
    buy_order_money_othermin = buy_tranorder_othermin.groupby(['minute', 'TradeBuyNo'])['TradeMoney','TradeQty'].sum().reset_index()
    buy_small_order_othermin = buy_order_money_othermin[buy_order_money_othermin.TradeMoney <= 40000]
    buy_mid_order_othermin = buy_order_money_othermin[(buy_order_money_othermin.TradeMoney > 40000) & (buy_order_money_othermin.TradeMoney <= 200000)]
    buy_big_order_othermin = buy_order_money_othermin[(buy_order_money_othermin.TradeMoney > 200000) & (buy_order_money_othermin.TradeMoney <= 1000000)]
    buy_super_order_othermin = buy_order_money_othermin[(buy_order_money_othermin.TradeMoney > 1000000)]
    buy_small_order_othermin = buy_small_order_othermin.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_smallorder_count_othermin','TradeMoney':'buy_smallorder_money_othermin','TradeQty':'buy_smallorder_volume_othermin'})
    buy_mid_order_othermin = buy_mid_order_othermin.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_midorder_count_othermin','TradeMoney':'buy_midorder_money_othermin','TradeQty':'buy_midorder_volume_othermin'})
    buy_big_order_othermin = buy_big_order_othermin.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_bigorder_count_othermin','TradeMoney':'buy_bigorder_money_othermin','TradeQty':'buy_bigorder_volume_othermin'})
    buy_super_order_othermin = buy_super_order_othermin.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_superorder_count_othermin','TradeMoney':'buy_superorder_money_othermin','TradeQty':'buy_superorder_volume_othermin'})

    sell_order_money_thismin = sell_tranorder_thismin.groupby(['minute', 'TradeSellNo'])['TradeMoney','TradeQty'].sum().reset_index()
    sell_small_order_thismin = sell_order_money_thismin[sell_order_money_thismin.TradeMoney <= 40000]
    sell_mid_order_thismin = sell_order_money_thismin[(sell_order_money_thismin.TradeMoney > 40000) & (sell_order_money_thismin.TradeMoney <= 200000)]
    sell_big_order_thismin = sell_order_money_thismin[(sell_order_money_thismin.TradeMoney > 200000) & (sell_order_money_thismin.TradeMoney <= 1000000)]
    sell_super_order_thismin = sell_order_money_thismin[(sell_order_money_thismin.TradeMoney > 1000000)]
    sell_small_order_thismin = sell_small_order_thismin.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_smallorder_count_thismin','TradeMoney':'sell_smallorder_money_thismin','TradeQty':'sell_smallorder_volume_thismin'})
    sell_mid_order_thismin = sell_mid_order_thismin.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_midorder_count_thismin','TradeMoney':'sell_midorder_money_thismin','TradeQty':'sell_midorder_volume_thismin'})
    sell_big_order_thismin = sell_big_order_thismin.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_bigorder_count_thismin','TradeMoney':'sell_bigorder_money_thismin','TradeQty':'sell_bigorder_volume_thismin'})
    sell_super_order_thismin = sell_super_order_thismin.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_superorder_count_thismin','TradeMoney':'sell_superorder_money_thismin','TradeQty':'sell_superorder_volume_thismin'})

    sell_tranorder_othermin['minute'] = sell_tranorder_othermin['tran_minute']
    sell_order_money_othermin = sell_tranorder_othermin.groupby(['minute', 'TradeSellNo'])['TradeMoney','TradeQty'].sum().reset_index()
    sell_small_order_othermin = sell_order_money_othermin[sell_order_money_othermin.TradeMoney <= 40000]
    sell_mid_order_othermin = sell_order_money_othermin[(sell_order_money_othermin.TradeMoney > 40000) & (sell_order_money_othermin.TradeMoney <= 200000)]
    sell_big_order_othermin = sell_order_money_othermin[(sell_order_money_othermin.TradeMoney > 200000) & (sell_order_money_othermin.TradeMoney <= 1000000)]
    sell_super_order_othermin = sell_order_money_othermin[(sell_order_money_othermin.TradeMoney > 1000000)]
    sell_small_order_othermin = sell_small_order_othermin.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_smallorder_count_othermin','TradeMoney':'sell_smallorder_money_othermin','TradeQty':'sell_smallorder_volume_othermin'})
    sell_mid_order_othermin = sell_mid_order_othermin.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_midorder_count_othermin','TradeMoney':'sell_midorder_money_othermin','TradeQty':'sell_midorder_volume_othermin'})
    sell_big_order_othermin = sell_big_order_othermin.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_bigorder_count_othermin','TradeMoney':'sell_bigorder_money_othermin','TradeQty':'sell_bigorder_volume_othermin'})
    sell_super_order_othermin = sell_super_order_othermin.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_superorder_count_othermin','TradeMoney':'sell_superorder_money_othermin','TradeQty':'sell_superorder_volume_othermin'})

    bsorder_thisothermin = pd.concat([buy_tranorder_thismin.groupby('minute')['TradeMoney'].sum(),buy_tranorder_othermin.groupby('minute')['TradeMoney'].sum(),sell_tranorder_thismin.groupby('minute')['TradeMoney'].sum(),sell_tranorder_othermin.groupby('minute')['TradeMoney'].sum()], axis = 1)

    bsorder_thisothermin.columns = ['buy_order_money_thismin','buy_order_money_othermin','sell_order_money_thismin','sell_order_money_othermin']

    order_tran = pd.concat([bsorder_thisothermin,buy_small_order_thismin,buy_mid_order_thismin,buy_big_order_thismin,buy_super_order_thismin,
                           buy_small_order_othermin,buy_mid_order_othermin,buy_big_order_othermin,buy_super_order_othermin,
                           sell_small_order_thismin,sell_mid_order_thismin,sell_big_order_thismin,sell_super_order_thismin,
                           sell_small_order_othermin,sell_mid_order_othermin,sell_big_order_othermin,sell_super_order_othermin], axis = 1)
    return order_tran
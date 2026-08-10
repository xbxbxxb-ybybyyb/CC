def unix_time_to_datetime(var):
    return datetime.datetime.fromtimestamp(var/1000)

trade = pd.read_csv('/data/user/012245/var/Market/um/monthly/BTCUSDT/BTCUSDT-trades-2023-03.csv')[-10000:]
# trade = pd.read_pickle('/data/user/015626/data/research/MD/trade/btc_2022.pkl')
trade['dt'] = trade.time.apply(lambda x : unix_time_to_datetime(x))
trade = trade.rename(columns = {'is_buyer_maker':'trade_bs_flag'})
trade_bs_flag_dict = {False:1,True:-1}
trade['trade_bs_flag'] = trade.trade_bs_flag.apply(lambda x:trade_bs_flag_dict[x])

order_kind_split_list = [1000,5000,15000]
def aggregate_trade(trade, T = '30S'):
    trade['trade_money'] = trade.price * trade.qty
    trade['price_path'] = trade.price.diff()
    trade['price_path_abs'] = abs(trade.price_path)

    for c in ['open','high','low','twap']:
        trade[c] = trade['price']

    trade_buy = trade[trade.trade_bs_flag == 1]
    trade_sell = trade[trade.trade_bs_flag == -1]

    split_dict = {'trade_bs_flag':'count', 'trade_money':'sum', 'qty':'sum'}
    buy_small_order = trade_buy[trade_buy.trade_money <= order_kind_split_list[0]]
    buy_mid_order = trade_buy[(trade_buy.trade_money > order_kind_split_list[0]) & (trade_buy.trade_money <= order_kind_split_list[1])]
    buy_big_order = trade_buy[(trade_buy.trade_money > order_kind_split_list[1]) & (trade_buy.trade_money <= order_kind_split_list[-1])]
    buy_super_order = trade_buy[(trade_buy.trade_money > order_kind_split_list[-1])]
    buy_small_order = buy_small_order.resample(rule=T,on='dt', label='left', closed='left').agg(split_dict).rename(columns = {'trade_bs_flag':'buy_smallorder_count','trade_money':'buy_smallorder_money','qty':'buy_smallorder_volume'})
    buy_mid_order = buy_mid_order.resample(rule=T,on='dt', label='left', closed='left').agg(split_dict).rename(columns = {'trade_bs_flag':'buy_midorder_count','trade_money':'buy_midorder_money','qty':'buy_midorder_volume'})
    buy_big_order = buy_big_order.resample(rule=T,on='dt', label='left', closed='left').agg(split_dict).rename(columns = {'trade_bs_flag':'buy_bigorder_count','trade_money':'buy_bigorder_money','qty':'buy_bigorder_volume'})
    buy_super_order = buy_super_order.resample(rule=T,on='dt', label='left', closed='left').agg(split_dict).rename(columns = {'trade_bs_flag':'buy_superorder_count','trade_money':'buy_superorder_money','qty':'buy_superorder_volume'})

    sell_small_order = trade_sell[trade_sell.trade_money <= order_kind_split_list[0]]
    sell_mid_order = trade_sell[(trade_sell.trade_money > order_kind_split_list[0]) & (trade_sell.trade_money <= order_kind_split_list[1])]
    sell_big_order = trade_sell[(trade_sell.trade_money > order_kind_split_list[1]) & (trade_sell.trade_money <= order_kind_split_list[-1])]
    sell_super_order = trade_sell[(trade_sell.trade_money > order_kind_split_list[-1])]
    sell_small_order = sell_small_order.resample(rule=T,on='dt', label='left', closed='left').agg(split_dict).rename(columns = {'trade_bs_flag':'sell_smallorder_count','trade_money':'sell_smallorder_money','qty':'sell_smallorder_volume'})
    sell_mid_order = sell_mid_order.resample(rule=T,on='dt', label='left', closed='left').agg(split_dict).rename(columns = {'trade_bs_flag':'sell_midorder_count','trade_money':'sell_midorder_money','qty':'sell_midorder_volume'})
    sell_big_order = sell_big_order.resample(rule=T,on='dt', label='left', closed='left').agg(split_dict).rename(columns = {'trade_bs_flag':'sell_bigorder_count','trade_money':'sell_bigorder_money','qty':'sell_bigorder_volume'})
    sell_super_order = sell_super_order.resample(rule=T,on='dt', label='left', closed='left').agg(split_dict).rename(columns = {'trade_bs_flag':'sell_superorder_count','trade_money':'sell_superorder_money','qty':'sell_superorder_volume'})


    trade_temp = trade.resample(rule=T,on='dt', label='left', closed='left').agg({'open':'first','high':'max','low':'min','twap':'mean','price':'last','qty':'sum','trade_money':'sum','price_path_abs':'sum','price_path':'sum','trade_bs_flag':'count'})
    trade_temp_buy = trade_buy.resample(rule=T,on='dt', label='left', closed='left').agg({'qty':'sum','trade_money':'sum','trade_bs_flag':'count'}).add_prefix('buy_')

    trade_temp = pd.concat([trade_temp, trade_temp_buy, sell_small_order, sell_mid_order, sell_big_order, 
                            sell_super_order, buy_small_order, buy_mid_order, buy_big_order, buy_super_order], axis = 1)#trade_temp.join(trade_temp_buy, how = 'left')
    trade_temp = trade_temp.rename(columns = {'price':'close','trade_bs_flag':'trade_count','buy_trade_bs_flag':'buy_trade_count','buy_qty':'buy_volume','buy_trade_money':'buy_amount','trade_money':'amount','qty':'volume'})

    for c in ['volume','amount','trade_count']:
        trade_temp['sell_%s' % c] = trade_temp[c] - trade_temp['buy_%s' % c]

    for col in ['order_count','order_money','order_volume']:
        for k in ['small', 'mid', 'big', 'super']: 
            trade_temp[f'{k}{col}'] = 0
            for c in ['buy','sell']:
                trade_temp[f'{k}{col}'] = trade_temp[f'{k}{col}'] + trade_temp[f'{c}_{k}{col}']

    trade_temp['vwap'] = trade_temp['amount'] / trade_temp['volume'].replace(0, np.nan)
    clist = trade_temp.columns.tolist()
    ffill_list = ['open','high','low','close', 'twap', 'vwap']
    fill0_list = list(set(clist) - set(ffill_list))
    trade_temp[ffill_list] = trade_temp[ffill_list].fillna(method = 'ffill')
    trade_temp[fill0_list] = trade_temp[fill0_list].fillna(value = 0)
    trade_temp = trade_temp[clist]
    return trade_temp

result = aggregate_trade(trade, '30S')
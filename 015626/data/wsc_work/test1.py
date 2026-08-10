def ft_1_931(temp_order_data, temp_trans_data, temp_stock_data, temp_withd_data):
    temp_stock_data_last = temp_stock_data.iloc[-1]

    df_1['amount'] = temp_trans_data['TradeMoney'].sum()
    df_1['amount_buy'] = temp_trans_data[temp_trans_data['TradeBSFlag'] == 1]['TradeMoney'].sum()
    df_1['amount_sell'] = temp_trans_data[temp_trans_data['TradeBSFlag'] == 2]['TradeMoney'].sum()
    df_1['withdraw_amount'] = temp_withd_data['OrderMoney'].sum()
    df_1['withdraw_amount_buy'] = temp_withd_data[temp_withd_data['OrderBSFlag'] == 1]['OrderMoney'].sum()
    df_1['withdraw_amount_sell'] = temp_withd_data[temp_withd_data['OrderBSFlag'] == 2]['OrderMoney'].sum()
    df_1['order_amount'] = temp_order_data['OrderMoney'].sum()
    df_1['order_amount_buy'] = temp_order_data[temp_order_data['OrderBSFlag'] == 1]['OrderMoney'].sum()
    df_1['order_amount_sell'] = temp_order_data[temp_order_data['OrderBSFlag'] == 2]['OrderMoney'].sum()
    df_1['tick_amount_5_buy'] = np.nansum(
        [temp_stock_data_last[f'Buy{i}Price'] * temp_stock_data_last[f'Buy{i}OrderQty'] for i in range(1, 6)])
    df_1['tick_amount_5_sell'] = np.nansum(
        [temp_stock_data_last[f'Sell{i}Price'] * temp_stock_data_last[f'Sell{i}OrderQty'] for i in range(1, 6)])
    df_1['tick_amount_5'] = df_1['tick_amount_5_buy'] + df_1['tick_amount_5_sell']
    df_1['tick_amount_10_buy'] = np.nansum(
        [temp_stock_data_last[f'Buy{i}Price'] * temp_stock_data_last[f'Buy{i}OrderQty'] for i in range(1, 11)])
    df_1['tick_amount_10_sell'] = np.nansum(
        [temp_stock_data_last[f'Sell{i}Price'] * temp_stock_data_last[f'Sell{i}OrderQty'] for i in range(1, 11)])
    df_1['tick_amount_10'] = df_1['tick_amount_10_buy'] + df_1['tick_amount_10_sell']
    df_1['tick_amount_all_buy'] = temp_stock_data_last['TotalBidQty'] * temp_stock_data_last['WeightedAvgBidPx']
    df_1['tick_amount_all_sell'] = temp_stock_data_last['TotalOfferQty'] * temp_stock_data_last['WeightedAvgOfferPx']
    df_1['tick_amount_all'] = df_1['tick_amount_all_buy'] + df_1['tick_amount_all_sell']

    df_1['volume'] = temp_trans_data['TradeQty'].sum()
    df_1['volume_buy'] = temp_trans_data[temp_trans_data['TradeBSFlag'] == 1]['TradeQty'].sum()
    df_1['volume_sell'] = temp_trans_data[temp_trans_data['TradeBSFlag'] == 2]['TradeQty'].sum()
    df_1['withdraw_volume'] = temp_withd_data['OrderQty'].sum()
    df_1['withdraw_volume_buy'] = temp_withd_data[temp_withd_data['OrderBSFlag'] == 1]['OrderQty'].sum()
    df_1['withdraw_volume_sell'] = temp_withd_data[temp_withd_data['OrderBSFlag'] == 2]['OrderQty'].sum()
    df_1['order_volume'] = temp_order_data['OrderQty'].sum()
    df_1['order_volume_buy'] = temp_order_data[temp_order_data['OrderBSFlag'] == 1]['OrderQty'].sum()
    df_1['order_volume_sell'] = temp_order_data[temp_order_data['OrderBSFlag'] == 2]['OrderQty'].sum()
    df_1['tick_volume_5_buy'] = np.nansum([temp_stock_data_last[f'Buy{i}OrderQty'] for i in range(1, 6)])
    df_1['tick_volume_5_sell'] = np.nansum([temp_stock_data_last[f'Sell{i}OrderQty'] for i in range(1, 6)])
    df_1['tick_volume_5'] = df_1['tick_volume_5_buy'] + df_1['tick_volume_5_sell']
    df_1['tick_volume_10_buy'] = np.nansum([temp_stock_data_last[f'Buy{i}OrderQty'] for i in range(1, 11)])
    df_1['tick_volume_10_sell'] = np.nansum([temp_stock_data_last[f'Sell{i}OrderQty'] for i in range(1, 11)])
    df_1['tick_volume_10'] = df_1['tick_volume_10_buy'] + df_1['tick_volume_10_sell']
    df_1['tick_volume_all_buy'] = temp_stock_data_last['TotalBidQty']
    df_1['tick_volume_all_sell'] = temp_stock_data_last['TotalOfferQty']
    df_1['tick_volume_all'] = df_1['tick_volume_all_buy'] + df_1['tick_volume_all_sell']

    df_1['num'] = temp_trans_data.shape[0]
    df_1['num_buy'] = temp_trans_data[temp_trans_data['TradeBSFlag'] == 1].shape[0]
    df_1['num_sell'] = temp_trans_data[temp_trans_data['TradeBSFlag'] == 2].shape[0]
    df_1['num_buy_unique'] = temp_trans_data[
        temp_trans_data['TradeBSFlag'] == 1]['TradeBuyNo'].unique().shape[0]
    df_1['num_sell_unique'] = temp_trans_data[
        temp_trans_data['TradeBSFlag'] == 2]['TradeSellNo'].unique().shape[0]
    df_1['num_unique'] = df_1['num_buy_unique'] + df_1['num_sell_unique']
    df_1['num_unique_buy'] = temp_trans_data['TradeBuyNo'].unique().shape[0]
    df_1['num_unique_sell'] = temp_trans_data['TradeSellNo'].unique().shape[0]
    df_1['withdraw_num'] = temp_withd_data.shape[0]
    df_1['withdraw_num_buy'] = temp_withd_data[temp_withd_data['OrderBSFlag'] == 1].shape[0]
    df_1['withdraw_num_sell'] = temp_withd_data[temp_withd_data['OrderBSFlag'] == 2].shape[0]
    df_1['order_num'] = temp_order_data.shape[0]
    df_1['order_num_buy'] = temp_order_data[temp_order_data['OrderBSFlag'] == 1].shape[0]
    df_1['order_num_sell'] = temp_order_data[temp_order_data['OrderBSFlag'] == 2].shape[0]
    df_1['tick_num_5_buy'] = np.nansum([temp_stock_data_last[f'Buy{i}NumOrders'] for i in range(1, 6)])
    df_1['tick_num_5_sell'] = np.nansum([temp_stock_data_last[f'Sell{i}NumOrders'] for i in range(1, 6)])
    df_1['tick_num_5'] = df_1['tick_num_5_buy'] + df_1['tick_num_5_sell']
    df_1['tick_num_10_buy'] = np.nansum([temp_stock_data_last[f'Buy{i}NumOrders'] for i in range(1, 11)])
    df_1['tick_num_10_sell'] = np.nansum([temp_stock_data_last[f'Sell{i}NumOrders'] for i in range(1, 11)])
    df_1['tick_num_10'] = df_1['tick_num_10_buy'] + df_1['tick_num_10_sell']
    return df_1


def ft_4o_931(temp_order_data, temp_trans_data, temp_withd_data, bms_threshold=(4e4, 2e5)):
    temp_order_data_big = temp_order_data[temp_order_data['OrderMoney'] > bms_threshold[1]]
    temp_order_data_mid = temp_order_data[
        (temp_order_data['OrderMoney'] > bms_threshold[0]) & (temp_order_data['OrderMoney'] <= bms_threshold[1])]
    temp_order_data_small = temp_order_data[temp_order_data['OrderMoney'] <= bms_threshold[0]]
    temp_withd_data_big = temp_withd_data[temp_withd_data['OrderMoney'] > bms_threshold[1]]
    temp_withd_data_mid = temp_withd_data[
        (temp_withd_data['OrderMoney'] > bms_threshold[0]) & (temp_withd_data['OrderMoney'] <= bms_threshold[1])]
    temp_withd_data_small = temp_withd_data[temp_withd_data['OrderMoney'] <= bms_threshold[0]]


    df_1['order_big_amount'] = temp_order_data_big['OrderMoney'].sum()
    df_1['order_big_amount_buy'] = temp_order_data_big[temp_order_data_big['OrderBSFlag'] == 1][
        'OrderMoney'].sum()
    df_1['order_big_amount_sell'] = temp_order_data_big[temp_order_data_big['OrderBSFlag'] == 2][
        'OrderMoney'].sum()
    df_1['order_big_amount_buy_dealed'] = \
        temp_trans_data[temp_trans_data['TradeBuyNo'].isin(temp_order_data_big['OrderNI'])][
            'TradeMoney'].sum()
    df_1['order_big_amount_sell_dealed'] = \
        temp_trans_data[temp_trans_data['TradeSellNo'].isin(temp_order_data_big['OrderNI'])][
            'TradeMoney'].sum()
    df_1['order_big_amount_dealed'] = df_1['order_big_amount_buy_dealed'] + df_1['order_big_amount_sell_dealed']
    df_1['order_big_amount_buy_withdraw'] = temp_withd_data_big[temp_withd_data_big['OrderBSFlag'] == 1][
        'OrderMoney'].sum()
    df_1['order_big_amount_sell_withdraw'] = temp_withd_data_big[temp_withd_data_big['OrderBSFlag'] == 2][
        'OrderMoney'].sum()
    df_1['order_big_amount_withdraw'] = df_1['order_big_amount_buy_withdraw'] + df_1[
        'order_big_amount_sell_withdraw']
    df_1['order_big_volume'] = temp_order_data_big['OrderQty'].sum()
    df_1['order_big_volume_buy'] = temp_order_data_big[temp_order_data_big['OrderBSFlag'] == 1][
        'OrderQty'].sum()
    df_1['order_big_volume_sell'] = temp_order_data_big[temp_order_data_big['OrderBSFlag'] == 2][
        'OrderQty'].sum()
    df_1['order_big_volume_buy_dealed'] = \
        temp_trans_data[temp_trans_data['TradeBuyNo'].isin(temp_order_data_big['OrderNI'])]['TradeQty'].sum()
    df_1['order_big_volume_sell_dealed'] = \
        temp_trans_data[temp_trans_data['TradeSellNo'].isin(temp_order_data_big['OrderNI'])][
            'TradeQty'].sum()
    df_1['order_big_volume_dealed'] = df_1['order_big_volume_buy_dealed'] + df_1['order_big_volume_sell_dealed']
    df_1['order_big_volume_buy_withdraw'] = temp_withd_data_big[temp_withd_data_big['OrderBSFlag'] == 1][
        'OrderQty'].sum()
    df_1['order_big_volume_sell_withdraw'] = temp_withd_data_big[temp_withd_data_big['OrderBSFlag'] == 2][
        'OrderQty'].sum()
    df_1['order_big_volume_withdraw'] = df_1['order_big_volume_buy_withdraw'] + df_1[
        'order_big_volume_sell_withdraw']
    df_1['order_big_num'] = temp_order_data_big.shape[0]
    df_1['order_big_num_buy'] = temp_order_data_big[temp_order_data_big['OrderBSFlag'] == 1].shape[0]
    df_1['order_big_num_sell'] = temp_order_data_big[temp_order_data_big['OrderBSFlag'] == 2].shape[0]
    df_1['order_big_num_buy_dealed'] = \
        temp_trans_data[temp_trans_data['TradeBuyNo'].isin(temp_order_data_big['OrderNI'])].shape[0]
    df_1['order_big_num_sell_dealed'] = \
        temp_trans_data[temp_trans_data['TradeSellNo'].isin(temp_order_data_big['OrderNI'])].shape[0]
    df_1['order_big_num_dealed'] = df_1['order_big_num_buy_dealed'] + df_1['order_big_num_sell_dealed']
    df_1['order_big_num_buy_dealed_unique'] = len(
        set(temp_trans_data['TradeBuyNo']).intersection(temp_order_data_big['OrderNI']))
    df_1['order_big_num_sell_dealed_unique'] = len(
        set(temp_trans_data['TradeSellNo']).intersection(temp_order_data_big['OrderNI']))
    df_1['order_big_num_dealed_unique'] = df_1['order_big_num_buy_dealed_unique'] + df_1[
        'order_big_num_sell_dealed_unique']
    df_1['order_big_num_dealed_unique_buy'] = temp_trans_data[(temp_trans_data['TradeBuyNo'].isin(
        temp_order_data_big['OrderNI'])) | (temp_trans_data['TradeSellNo'].isin(
        temp_order_data_big['OrderNI']))]['TradeBuyNo'].unique().shape[0]
    df_1['order_big_num_dealed_unique_sell'] = temp_trans_data[(temp_trans_data['TradeBuyNo'].isin(
        temp_order_data_big['OrderNI'])) | (temp_trans_data['TradeSellNo'].isin(
        temp_order_data_big['OrderNI']))]['TradeSellNo'].unique().shape[0]
    df_1['order_big_num_buy_withdraw'] = temp_withd_data_big[temp_withd_data_big['OrderBSFlag'] == 1].shape[0]
    df_1['order_big_num_sell_withdraw'] = temp_withd_data_big[temp_withd_data_big['OrderBSFlag'] == 2].shape[0]
    df_1['order_big_num_withdraw'] = df_1['order_big_num_buy_withdraw'] + df_1['order_big_num_sell_withdraw']

    df_1['order_mid_amount'] = temp_order_data_mid['OrderMoney'].sum()
    df_1['order_mid_amount_buy'] = temp_order_data_mid[temp_order_data_mid['OrderBSFlag'] == 1][
        'OrderMoney'].sum()
    df_1['order_mid_amount_sell'] = temp_order_data_mid[temp_order_data_mid['OrderBSFlag'] == 2][
        'OrderMoney'].sum()
    df_1['order_mid_amount_buy_dealed'] = \
        temp_trans_data[temp_trans_data['TradeBuyNo'].isin(temp_order_data_mid['OrderNI'])][
            'TradeMoney'].sum()
    df_1['order_mid_amount_sell_dealed'] = \
        temp_trans_data[temp_trans_data['TradeSellNo'].isin(temp_order_data_mid['OrderNI'])][
            'TradeMoney'].sum()
    df_1['order_mid_amount_dealed'] = df_1['order_mid_amount_buy_dealed'] + df_1['order_mid_amount_sell_dealed']
    df_1['order_mid_amount_buy_withdraw'] = temp_withd_data_mid[temp_withd_data_mid['OrderBSFlag'] == 1][
        'OrderMoney'].sum()
    df_1['order_mid_amount_sell_withdraw'] = temp_withd_data_mid[temp_withd_data_mid['OrderBSFlag'] == 2][
        'OrderMoney'].sum()
    df_1['order_mid_amount_withdraw'] = df_1['order_mid_amount_buy_withdraw'] + df_1[
        'order_mid_amount_sell_withdraw']
    df_1['order_mid_volume'] = temp_order_data_mid['OrderQty'].sum()
    df_1['order_mid_volume_buy'] = temp_order_data_mid[temp_order_data_mid['OrderBSFlag'] == 1][
        'OrderQty'].sum()
    df_1['order_mid_volume_sell'] = temp_order_data_mid[temp_order_data_mid['OrderBSFlag'] == 2][
        'OrderQty'].sum()
    df_1['order_mid_volume_buy_dealed'] = \
        temp_trans_data[temp_trans_data['TradeBuyNo'].isin(temp_order_data_mid['OrderNI'])]['TradeQty'].sum()
    df_1['order_mid_volume_sell_dealed'] = \
        temp_trans_data[temp_trans_data['TradeSellNo'].isin(temp_order_data_mid['OrderNI'])][
            'TradeQty'].sum()
    df_1['order_mid_volume_dealed'] = df_1['order_mid_volume_buy_dealed'] + df_1['order_mid_volume_sell_dealed']
    df_1['order_mid_volume_buy_withdraw'] = temp_withd_data_mid[temp_withd_data_mid['OrderBSFlag'] == 1][
        'OrderQty'].sum()
    df_1['order_mid_volume_sell_withdraw'] = temp_withd_data_mid[temp_withd_data_mid['OrderBSFlag'] == 2][
        'OrderQty'].sum()
    df_1['order_mid_volume_withdraw'] = df_1['order_mid_volume_buy_withdraw'] + df_1[
        'order_mid_volume_sell_withdraw']
    df_1['order_mid_num'] = temp_order_data_mid.shape[0]
    df_1['order_mid_num_buy'] = temp_order_data_mid[temp_order_data_mid['OrderBSFlag'] == 1].shape[0]
    df_1['order_mid_num_sell'] = temp_order_data_mid[temp_order_data_mid['OrderBSFlag'] == 2].shape[0]
    df_1['order_mid_num_buy_dealed'] = \
        temp_trans_data[temp_trans_data['TradeBuyNo'].isin(temp_order_data_mid['OrderNI'])].shape[0]
    df_1['order_mid_num_sell_dealed'] = \
        temp_trans_data[temp_trans_data['TradeSellNo'].isin(temp_order_data_mid['OrderNI'])].shape[0]
    df_1['order_mid_num_dealed'] = df_1['order_mid_num_buy_dealed'] + df_1['order_mid_num_sell_dealed']
    df_1['order_mid_num_buy_dealed_unique'] = len(
        set(temp_trans_data['TradeBuyNo']).intersection(temp_order_data_mid['OrderNI']))
    df_1['order_mid_num_sell_dealed_unique'] = len(
        set(temp_trans_data['TradeSellNo']).intersection(temp_order_data_mid['OrderNI']))
    df_1['order_mid_num_dealed_unique'] = df_1['order_mid_num_buy_dealed_unique'] + df_1[
        'order_mid_num_sell_dealed_unique']
    df_1['order_mid_num_dealed_unique_buy'] = temp_trans_data[(temp_trans_data['TradeBuyNo'].isin(
        temp_order_data_mid['OrderNI'])) | (temp_trans_data['TradeSellNo'].isin(
        temp_order_data_mid['OrderNI']))]['TradeBuyNo'].unique().shape[0]
    df_1['order_mid_num_dealed_unique_sell'] = temp_trans_data[(temp_trans_data['TradeBuyNo'].isin(
        temp_order_data_mid['OrderNI'])) | (temp_trans_data['TradeSellNo'].isin(
        temp_order_data_mid['OrderNI']))]['TradeSellNo'].unique().shape[0]
    df_1['order_mid_num_buy_withdraw'] = temp_withd_data_mid[temp_withd_data_mid['OrderBSFlag'] == 1].shape[0]
    df_1['order_mid_num_sell_withdraw'] = temp_withd_data_mid[temp_withd_data_mid['OrderBSFlag'] == 2].shape[0]
    df_1['order_mid_num_withdraw'] = df_1['order_mid_num_buy_withdraw'] + df_1['order_mid_num_sell_withdraw']

    df_1['order_small_amount'] = temp_order_data_small['OrderMoney'].sum()
    df_1['order_small_amount_buy'] = temp_order_data_small[temp_order_data_small['OrderBSFlag'] == 1][
        'OrderMoney'].sum()
    df_1['order_small_amount_sell'] = temp_order_data_small[temp_order_data_small['OrderBSFlag'] == 2][
        'OrderMoney'].sum()
    df_1['order_small_amount_buy_dealed'] = \
        temp_trans_data[temp_trans_data['TradeBuyNo'].isin(temp_order_data_small['OrderNI'])][
            'TradeMoney'].sum()
    df_1['order_small_amount_sell_dealed'] = \
        temp_trans_data[temp_trans_data['TradeSellNo'].isin(temp_order_data_small['OrderNI'])][
            'TradeMoney'].sum()
    df_1['order_small_amount_dealed'] = df_1['order_small_amount_buy_dealed'] + df_1[
        'order_small_amount_sell_dealed']
    df_1['order_small_amount_buy_withdraw'] = temp_withd_data_small[temp_withd_data_small['OrderBSFlag'] == 1][
        'OrderMoney'].sum()
    df_1['order_small_amount_sell_withdraw'] = temp_withd_data_small[temp_withd_data_small['OrderBSFlag'] == 2][
        'OrderMoney'].sum()
    df_1['order_small_amount_withdraw'] = df_1['order_small_amount_buy_withdraw'] + df_1[
        'order_small_amount_sell_withdraw']
    df_1['order_small_volume'] = temp_order_data_small['OrderQty'].sum()
    df_1['order_small_volume_buy'] = temp_order_data_small[temp_order_data_small['OrderBSFlag'] == 1][
        'OrderQty'].sum()
    df_1['order_small_volume_sell'] = temp_order_data_small[temp_order_data_small['OrderBSFlag'] == 2][
        'OrderQty'].sum()
    df_1['order_small_volume_buy_dealed'] = \
        temp_trans_data[temp_trans_data['TradeBuyNo'].isin(temp_order_data_small['OrderNI'])][
            'TradeQty'].sum()
    df_1['order_small_volume_sell_dealed'] = \
        temp_trans_data[temp_trans_data['TradeSellNo'].isin(temp_order_data_small['OrderNI'])][
            'TradeQty'].sum()
    df_1['order_small_volume_dealed'] = df_1['order_small_volume_buy_dealed'] + df_1[
        'order_small_volume_sell_dealed']
    df_1['order_small_volume_buy_withdraw'] = temp_withd_data_small[temp_withd_data_small['OrderBSFlag'] == 1][
        'OrderQty'].sum()
    df_1['order_small_volume_sell_withdraw'] = temp_withd_data_small[temp_withd_data_small['OrderBSFlag'] == 2][
        'OrderQty'].sum()
    df_1['order_small_volume_withdraw'] = df_1['order_small_volume_buy_withdraw'] + df_1[
        'order_small_volume_sell_withdraw']
    df_1['order_small_num'] = temp_order_data_small.shape[0]
    df_1['order_small_num_buy'] = temp_order_data_small[temp_order_data_small['OrderBSFlag'] == 1].shape[0]
    df_1['order_small_num_sell'] = temp_order_data_small[temp_order_data_small['OrderBSFlag'] == 2].shape[0]
    df_1['order_small_num_buy_dealed'] = \
        temp_trans_data[temp_trans_data['TradeBuyNo'].isin(temp_order_data_small['OrderNI'])].shape[0]
    df_1['order_small_num_sell_dealed'] = \
        temp_trans_data[temp_trans_data['TradeSellNo'].isin(temp_order_data_small['OrderNI'])].shape[0]
    df_1['order_small_num_dealed'] = df_1['order_small_num_buy_dealed'] + df_1['order_small_num_sell_dealed']
    df_1['order_small_num_buy_dealed_unique'] = len(
        set(temp_trans_data['TradeBuyNo']).intersection(temp_order_data_small['OrderNI']))
    df_1['order_small_num_sell_dealed_unique'] = len(
        set(temp_trans_data['TradeSellNo']).intersection(temp_order_data_small['OrderNI']))
    df_1['order_small_num_dealed_unique'] = df_1['order_small_num_buy_dealed_unique'] + df_1[
        'order_small_num_sell_dealed_unique']
    df_1['order_small_num_dealed_unique_buy'] = temp_trans_data[(temp_trans_data['TradeBuyNo'].isin(
        temp_order_data_small['OrderNI'])) | (temp_trans_data['TradeSellNo'].isin(
        temp_order_data_small['OrderNI']))]['TradeBuyNo'].unique().shape[0]
    df_1['order_small_num_dealed_unique_sell'] = temp_trans_data[(temp_trans_data['TradeBuyNo'].isin(
        temp_order_data_small['OrderNI'])) | (temp_trans_data['TradeSellNo'].isin(
        temp_order_data_small['OrderNI']))]['TradeSellNo'].unique().shape[0]
    df_1['order_small_num_buy_withdraw'] = temp_withd_data_small[temp_withd_data_small['OrderBSFlag'] == 1].shape[0]
    df_1['order_small_num_sell_withdraw'] = temp_withd_data_small[temp_withd_data_small['OrderBSFlag'] == 2].shape[0]
    df_1['order_small_num_withdraw'] = df_1['order_small_num_buy_withdraw'] + df_1[
        'order_small_num_sell_withdraw']
    return df_1


def ft_4t_931(temp_trans_data, bms_threshold=(4e4, 2e5)):
    temp_trans_data_unique_buy_1 = temp_trans_data.groupby('TradeBuyNo')[['TradeQty', 'TradeMoney']].sum()
    temp_trans_data_unique_buy_2 = temp_trans_data.groupby('TradeBuyNo')[['TradeBSFlag']].first()
    temp_trans_data_unique_buy = pd.concat([temp_trans_data_unique_buy_1, temp_trans_data_unique_buy_2], axis=1)
    temp_trans_data_unique_sell_1 = temp_trans_data.groupby('TradeSellNo')[['TradeQty', 'TradeMoney']].sum()
    temp_trans_data_unique_sell_2 = temp_trans_data.groupby('TradeSellNo')[['TradeBSFlag']].first()
    temp_trans_data_unique_sell = pd.concat([temp_trans_data_unique_sell_1, temp_trans_data_unique_sell_2], axis=1)
    temp_trans_data_unique_buy_big = temp_trans_data_unique_buy[
        temp_trans_data_unique_buy['TradeMoney'] > bms_threshold[1]]
    temp_trans_data_unique_buy_mid = temp_trans_data_unique_buy[
        (temp_trans_data_unique_buy['TradeMoney'] > bms_threshold[0]) & (
                temp_trans_data_unique_buy['TradeMoney'] <= bms_threshold[1])]
    temp_trans_data_unique_buy_small = temp_trans_data_unique_buy[
        temp_trans_data_unique_buy['TradeMoney'] <= bms_threshold[0]]
    temp_trans_data_unique_sell_big = temp_trans_data_unique_sell[
        temp_trans_data_unique_sell['TradeMoney'] > bms_threshold[1]]
    temp_trans_data_unique_sell_mid = temp_trans_data_unique_sell[
        (temp_trans_data_unique_sell['TradeMoney'] > bms_threshold[0]) & (
                temp_trans_data_unique_sell['TradeMoney'] <= bms_threshold[1])]
    temp_trans_data_unique_sell_small = temp_trans_data_unique_sell[
        temp_trans_data_unique_sell['TradeMoney'] <= bms_threshold[0]]


    df_1['unique_buy_big_amount'] = temp_trans_data_unique_buy_big['TradeMoney'].sum()
    df_1['unique_buy_big_amount_buy'] = temp_trans_data_unique_buy_big[
        temp_trans_data_unique_buy_big['TradeBSFlag'] == 1]['TradeMoney'].sum()
    df_1['unique_buy_big_amount_sell'] = temp_trans_data_unique_buy_big[
        temp_trans_data_unique_buy_big['TradeBSFlag'] == 2]['TradeMoney'].sum()
    df_1['unique_buy_big_volume'] = temp_trans_data_unique_buy_big['TradeQty'].sum()
    df_1['unique_buy_big_volume_buy'] = temp_trans_data_unique_buy_big[
        temp_trans_data_unique_buy_big['TradeBSFlag'] == 1]['TradeQty'].sum()
    df_1['unique_buy_big_volume_sell'] = temp_trans_data_unique_buy_big[
        temp_trans_data_unique_buy_big['TradeBSFlag'] == 2]['TradeQty'].sum()
    df_1['unique_buy_big_num'] = temp_trans_data_unique_buy_big.shape[0]
    df_1['unique_buy_big_num_buy'] = temp_trans_data_unique_buy_big[
        temp_trans_data_unique_buy_big['TradeBSFlag'] == 1].shape[0]
    df_1['unique_buy_big_num_sell'] = temp_trans_data_unique_buy_big[
        temp_trans_data_unique_buy_big['TradeBSFlag'] == 2].shape[0]
    df_1['unique_sell_big_amount'] = temp_trans_data_unique_sell_big['TradeMoney'].sum()
    df_1['unique_sell_big_amount_buy'] = temp_trans_data_unique_sell_big[
        temp_trans_data_unique_sell_big['TradeBSFlag'] == 1]['TradeMoney'].sum()
    df_1['unique_sell_big_amount_sell'] = temp_trans_data_unique_sell_big[
        temp_trans_data_unique_sell_big['TradeBSFlag'] == 2]['TradeMoney'].sum()
    df_1['unique_sell_big_volume'] = temp_trans_data_unique_sell_big['TradeQty'].sum()
    df_1['unique_sell_big_volume_buy'] = temp_trans_data_unique_sell_big[
        temp_trans_data_unique_sell_big['TradeBSFlag'] == 1]['TradeQty'].sum()
    df_1['unique_sell_big_volume_sell'] = temp_trans_data_unique_sell_big[
        temp_trans_data_unique_sell_big['TradeBSFlag'] == 2]['TradeQty'].sum()
    df_1['unique_sell_big_num'] = temp_trans_data_unique_sell_big.shape[0]
    df_1['unique_sell_big_num_buy'] = temp_trans_data_unique_sell_big[
        temp_trans_data_unique_sell_big['TradeBSFlag'] == 1].shape[0]
    df_1['unique_sell_big_num_sell'] = temp_trans_data_unique_sell_big[
        temp_trans_data_unique_sell_big['TradeBSFlag'] == 2].shape[0]
    df_1['unique_buy_mid_amount'] = temp_trans_data_unique_buy_mid['TradeMoney'].sum()
    df_1['unique_buy_mid_amount_buy'] = temp_trans_data_unique_buy_mid[
        temp_trans_data_unique_buy_mid['TradeBSFlag'] == 1]['TradeMoney'].sum()
    df_1['unique_buy_mid_amount_sell'] = temp_trans_data_unique_buy_mid[
        temp_trans_data_unique_buy_mid['TradeBSFlag'] == 2]['TradeMoney'].sum()
    df_1['unique_buy_mid_volume'] = temp_trans_data_unique_buy_mid['TradeQty'].sum()
    df_1['unique_buy_mid_volume_buy'] = temp_trans_data_unique_buy_mid[
        temp_trans_data_unique_buy_mid['TradeBSFlag'] == 1]['TradeQty'].sum()
    df_1['unique_buy_mid_volume_sell'] = temp_trans_data_unique_buy_mid[
        temp_trans_data_unique_buy_mid['TradeBSFlag'] == 2]['TradeQty'].sum()
    df_1['unique_buy_mid_num'] = temp_trans_data_unique_buy_mid.shape[0]
    df_1['unique_buy_mid_num_buy'] = temp_trans_data_unique_buy_mid[
        temp_trans_data_unique_buy_mid['TradeBSFlag'] == 1].shape[0]
    df_1['unique_buy_mid_num_sell'] = temp_trans_data_unique_buy_mid[
        temp_trans_data_unique_buy_mid['TradeBSFlag'] == 2].shape[0]
    df_1['unique_sell_mid_amount'] = temp_trans_data_unique_sell_mid['TradeMoney'].sum()
    df_1['unique_sell_mid_amount_buy'] = temp_trans_data_unique_sell_mid[
        temp_trans_data_unique_sell_mid['TradeBSFlag'] == 1]['TradeMoney'].sum()
    df_1['unique_sell_mid_amount_sell'] = temp_trans_data_unique_sell_mid[
        temp_trans_data_unique_sell_mid['TradeBSFlag'] == 2]['TradeMoney'].sum()
    df_1['unique_sell_mid_volume'] = temp_trans_data_unique_sell_mid['TradeQty'].sum()
    df_1['unique_sell_mid_volume_buy'] = temp_trans_data_unique_sell_mid[
        temp_trans_data_unique_sell_mid['TradeBSFlag'] == 1]['TradeQty'].sum()
    df_1['unique_sell_mid_volume_sell'] = temp_trans_data_unique_sell_mid[
        temp_trans_data_unique_sell_mid['TradeBSFlag'] == 2]['TradeQty'].sum()
    df_1['unique_sell_mid_num'] = temp_trans_data_unique_sell_mid.shape[0]
    df_1['unique_sell_mid_num_buy'] = temp_trans_data_unique_sell_mid[
        temp_trans_data_unique_sell_mid['TradeBSFlag'] == 1].shape[0]
    df_1['unique_sell_mid_num_sell'] = temp_trans_data_unique_sell_mid[
        temp_trans_data_unique_sell_mid['TradeBSFlag'] == 2].shape[0]
    df_1['unique_buy_small_amount'] = temp_trans_data_unique_buy_small['TradeMoney'].sum()
    df_1['unique_buy_small_amount_buy'] = temp_trans_data_unique_buy_small[
        temp_trans_data_unique_buy_small['TradeBSFlag'] == 1]['TradeMoney'].sum()
    df_1['unique_buy_small_amount_sell'] = temp_trans_data_unique_buy_small[
        temp_trans_data_unique_buy_small['TradeBSFlag'] == 2]['TradeMoney'].sum()
    df_1['unique_buy_small_volume'] = temp_trans_data_unique_buy_small['TradeQty'].sum()
    df_1['unique_buy_small_volume_buy'] = temp_trans_data_unique_buy_small[
        temp_trans_data_unique_buy_small['TradeBSFlag'] == 1]['TradeQty'].sum()
    df_1['unique_buy_small_volume_sell'] = temp_trans_data_unique_buy_small[
        temp_trans_data_unique_buy_small['TradeBSFlag'] == 2]['TradeQty'].sum()
    df_1['unique_buy_small_num'] = temp_trans_data_unique_buy_small.shape[0]
    df_1['unique_buy_small_num_buy'] = temp_trans_data_unique_buy_small[
        temp_trans_data_unique_buy_small['TradeBSFlag'] == 1].shape[0]
    df_1['unique_buy_small_num_sell'] = temp_trans_data_unique_buy_small[
        temp_trans_data_unique_buy_small['TradeBSFlag'] == 2].shape[0]
    df_1['unique_sell_small_amount'] = temp_trans_data_unique_sell_small['TradeMoney'].sum()
    df_1['unique_sell_small_amount_buy'] = temp_trans_data_unique_sell_small[
        temp_trans_data_unique_sell_small['TradeBSFlag'] == 1]['TradeMoney'].sum()
    df_1['unique_sell_small_amount_sell'] = temp_trans_data_unique_sell_small[
        temp_trans_data_unique_sell_small['TradeBSFlag'] == 2]['TradeMoney'].sum()
    df_1['unique_sell_small_volume'] = temp_trans_data_unique_sell_small['TradeQty'].sum()
    df_1['unique_sell_small_volume_buy'] = temp_trans_data_unique_sell_small[
        temp_trans_data_unique_sell_small['TradeBSFlag'] == 1]['TradeQty'].sum()
    df_1['unique_sell_small_volume_sell'] = temp_trans_data_unique_sell_small[
        temp_trans_data_unique_sell_small['TradeBSFlag'] == 2]['TradeQty'].sum()
    df_1['unique_sell_small_num'] = temp_trans_data_unique_sell_small.shape[0]
    df_1['unique_sell_small_num_buy'] = temp_trans_data_unique_sell_small[
        temp_trans_data_unique_sell_small['TradeBSFlag'] == 1].shape[0]
    df_1['unique_sell_small_num_sell'] = temp_trans_data_unique_sell_small[
        temp_trans_data_unique_sell_small['TradeBSFlag'] == 2].shape[0]
    return df_1


def ft_5_931(temp_stock_data, temp_daily_data, trunc_time):
    temp_stock_data_last = temp_stock_data.iloc[-1]
    temp_stock_data_c = temp_stock_data.between_time('9:30', trunc_time, include_end=False)
    temp_preclose = replace_zero_num(temp_daily_data['S_DQ_PRECLOSE'])
    temp_limit = replace_zero_num(temp_daily_data['S_DQ_LIMIT'])
    temp_stopping = replace_zero_num(temp_daily_data['S_DQ_STOPPING'])
    temp_open = replace_zero_num(temp_stock_data.between_time('9:25', '9:30', include_end=False)['LastPx'].iloc[-1])
    temp_close = replace_zero_num(temp_stock_data_last['LastPx'])


    df_1['s1'] = temp_close / temp_preclose - 1
    df_1['s2'] = (temp_stock_data_last['Sell1Price'] - temp_close) / replace_zero_num(
        temp_stock_data_last['Sell1Price'] - temp_stock_data_last['Buy1Price'])
    temp_buy_adj_5 = np.nansum([temp_stock_data_last[f'Buy{i}Price'] * temp_stock_data_last[f'Buy{i}OrderQty'] for i in
                                range(1, 6)]) / replace_zero_num(
        np.nansum([temp_stock_data_last[f'Buy{i}OrderQty'] for i in range(1, 6)]))
    temp_sell_adj_5 = np.nansum(
        [temp_stock_data_last[f'Sell{i}Price'] * temp_stock_data_last[f'Sell{i}OrderQty'] for i in
         range(1, 6)]) / replace_zero_num(np.nansum([temp_stock_data_last[f'Sell{i}OrderQty'] for i in range(1, 6)]))
    df_1['s3'] = (temp_sell_adj_5 - temp_close) / replace_zero_num(temp_sell_adj_5 - temp_buy_adj_5)
    df_1['s4'] = (temp_stock_data_last['WeightedAvgOfferPx'] - temp_close) / replace_zero_num(
        temp_stock_data_last['WeightedAvgOfferPx'] - temp_stock_data_last['WeightedAvgBidPx'])
    df_1['s5'] = temp_close / replace_zero_num(temp_open) - 1
    df_1['s6'] = (temp_stock_data_c['LastPx'].idxmax() - temp_stock_data_c['LastPx'].index[0]) / (
            temp_stock_data_c['LastPx'].index[-1] - temp_stock_data_c['LastPx'].index[0])
    df_1['s7'] = (temp_stock_data_c['LastPx'].idxmin() - temp_stock_data_c['LastPx'].index[0]) / (
            temp_stock_data_c['LastPx'].index[-1] - temp_stock_data_c['LastPx'].index[0])
    df_1['s8'] = temp_stock_data_c.loc[temp_stock_data_c['LastPx'].idxmax()]['TotalValueTrade'] / \
                 temp_stock_data_c['TotalValueTrade'].iloc[-1]
    df_1['s9'] = temp_stock_data_c.loc[temp_stock_data_c['LastPx'].idxmin()]['TotalValueTrade'] / \
                 temp_stock_data_c['TotalValueTrade'].iloc[-1]

    df_1['s10'] = ts_pct_change(temp_stock_data_c['LastPx'], 1).std()
    df_1['s11'] = ts_pct_change(temp_stock_data_c['LastPx'], 1).skew()
    df_1['s12'] = ts_pct_change(temp_stock_data_c['LastPx'], 1).kurt()
    df_1['s13'] = temp_stock_data_c['LastPx'].corr(temp_stock_data_c['amount'])
    df_1['s14'] = temp_stock_data_c['ret'].corr(temp_stock_data_c['amount'])

    df_1['s15'] = temp_stock_data_c['LastPx'].iloc[0] / replace_zero_num(temp_preclose) - 1
    df_1['s16'] = temp_stock_data_c['LastPx'].iloc[0] / replace_zero_num(temp_open) - 1
    df_1['s17'] = temp_stock_data_c['LastPx'].max() / replace_zero_num(temp_preclose) - 1
    df_1['s18'] = temp_stock_data_c['LastPx'].max() / replace_zero_num(temp_open) - 1
    df_1['s19'] = temp_stock_data_c['LastPx'].min() / replace_zero_num(temp_preclose) - 1
    df_1['s20'] = temp_stock_data_c['LastPx'].min() / replace_zero_num(temp_open) - 1
    df_1['s21'] = temp_stock_data_c['LastPx'].max() / replace_zero_num(
        temp_stock_data_c['LastPx'].min()) - 1
    df_1['s22'] = temp_stock_data_c['LastPx'].max() == temp_limit
    df_1['s23'] = temp_stock_data_c['LastPx'].min() == temp_stopping
    return df_1


def ft_regoa_931(temp_order_data):
    temp_order_data_b = temp_order_data[temp_order_data['OrderBSFlag'] == 1]
    temp_order_data_s = temp_order_data[temp_order_data['OrderBSFlag'] == 2]

    time_norm_t = temp_order_data.groupby('time_norm')[['time_norm']].first()
    amount_norm_t = temp_order_data.groupby('time_norm')[['OrderMoney']].sum()
    price_norm_t = (amount_norm_t / temp_order_data.groupby('time_norm')[['OrderQty']].sum().values) / temp_preclose
    temp_p1 = LinearRegression().fit(time_norm_t, price_norm_t)
    temp_a1 = LinearRegression().fit(time_norm_t, amount_norm_t)
    temp_p2 = LinearRegression().fit(temp_order_data[['OrderNI_adj']], temp_order_data[['price_norm']])
    temp_a2 = LinearRegression().fit(temp_order_data[['OrderNI_adj']], temp_order_data[['OrderMoney']])
    df_1['p_time_order_coef_a'] = temp_p1.coef_[0][0]
    df_1['p_time_order_resi_a'] = get_residual(temp_p1, time_norm_t, price_norm_t).std().values[0]
    df_1['a_time_order_coef_a'] = temp_a1.coef_[0][0]
    df_1['a_time_order_resi_a'] = get_residual(temp_a1, time_norm_t, amount_norm_t).std().values[0]
    df_1['p_seq_order_coef_a'] = temp_p2.coef_[0][0]
    df_1['p_seq_order_resi_a'] = \
        get_residual(temp_p2, temp_order_data[['OrderNI_adj']], temp_order_data[['price_norm']]).std().values[0]
    df_1['a_seq_order_coef_a'] = temp_a2.coef_[0][0]
    df_1['a_seq_order_resi_a'] = \
        get_residual(temp_a2, temp_order_data[['OrderNI_adj']], temp_order_data[['OrderMoney']]).std().values[0]

    temp_order_data_b = temp_order_data[temp_order_data['OrderBSFlag'] == 1]
    temp_order_data_s = temp_order_data[temp_order_data['OrderBSFlag'] == 2]

    time_norm_t_b = temp_order_data_b.groupby('time_norm')[['time_norm']].first()
    amount_norm_t_b = temp_order_data_b.groupby('time_norm')[['OrderMoney']].sum()
    price_norm_t_b = (amount_norm_t_b / temp_order_data_b.groupby('time_norm')[
        ['OrderQty']].sum().values) / temp_preclose
    temp_p5 = LinearRegression().fit(time_norm_t_b, price_norm_t_b)
    temp_a5 = LinearRegression().fit(time_norm_t_b, amount_norm_t_b)
    temp_p6 = LinearRegression().fit(temp_order_data_b[['OrderNI_adj']], temp_order_data_b[['price_norm']])
    temp_a6 = LinearRegression().fit(temp_order_data_b[['OrderNI_adj']], temp_order_data_b[['OrderMoney']])
    df_1['p_time_order_coef_b_a'] = temp_p5.coef_[0][0]
    df_1['p_time_order_resi_b_a'] = get_residual(temp_p5, time_norm_t_b, price_norm_t_b).std().values[0]
    df_1['a_time_order_coef_b_a'] = temp_a5.coef_[0][0]
    df_1['a_time_order_resi_b_a'] = get_residual(temp_a5, time_norm_t_b, amount_norm_t_b).std().values[0]
    df_1['p_seq_order_coef_b_a'] = temp_p6.coef_[0][0]
    df_1['p_seq_order_resi_b_a'] = \
        get_residual(temp_p6, temp_order_data_b[['OrderNI_adj']], temp_order_data_b[['price_norm']]).std().values[0]
    df_1['a_seq_order_coef_b_a'] = temp_a6.coef_[0][0]
    df_1['a_seq_order_resi_b_a'] = \
        get_residual(temp_a6, temp_order_data_b[['OrderNI_adj']], temp_order_data_b[['OrderMoney']]).std().values[0]

    time_norm_t_s = temp_order_data_s.groupby('time_norm')[['time_norm']].first()
    amount_norm_t_s = temp_order_data_s.groupby('time_norm')[['OrderMoney']].sum()
    price_norm_t_s = (amount_norm_t_s / temp_order_data_s.groupby('time_norm')[
        ['OrderQty']].sum().values) / temp_preclose
    temp_p5 = LinearRegression().fit(time_norm_t_s, price_norm_t_s)
    temp_a5 = LinearRegression().fit(time_norm_t_s, amount_norm_t_s)
    temp_p6 = LinearRegression().fit(temp_order_data_s[['OrderNI_adj']], temp_order_data_s[['price_norm']])
    temp_a6 = LinearRegression().fit(temp_order_data_s[['OrderNI_adj']], temp_order_data_s[['OrderMoney']])
    df_1['p_time_order_coef_s_a'] = temp_p5.coef_[0][0]
    df_1['p_time_order_resi_s_a'] = get_residual(temp_p5, time_norm_t_s, price_norm_t_s).std().values[0]
    df_1['a_time_order_coef_s_a'] = temp_a5.coef_[0][0]
    df_1['a_time_order_resi_s_a'] = get_residual(temp_a5, time_norm_t_s, amount_norm_t_s).std().values[0]
    df_1['p_seq_order_coef_s_a'] = temp_p6.coef_[0][0]
    df_1['p_seq_order_resi_s_a'] = \
        get_residual(temp_p6, temp_order_data_s[['OrderNI_adj']], temp_order_data_s[['price_norm']]).std().values[0]
    df_1['a_seq_order_coef_s_a'] = temp_a6.coef_[0][0]
    df_1['a_seq_order_resi_s_a'] = \
        get_residual(temp_a6, temp_order_data_s[['OrderNI_adj']], temp_order_data_s[['OrderMoney']]).std().values[0]

    df_1['p_time_order_coef_bts_a'] = df_1['p_time_order_coef_b_a'] / replace_zero_num(df_1['p_time_order_coef_s_a'])
    df_1['p_time_order_resi_bts_a'] = df_1['p_time_order_resi_b_a'] / replace_zero_num(df_1['p_time_order_resi_s_a'])
    df_1['a_time_order_coef_bts_a'] = df_1['a_time_order_coef_b_a'] / replace_zero_num(df_1['a_time_order_coef_s_a'])
    df_1['a_time_order_resi_bts_a'] = df_1['a_time_order_resi_b_a'] / replace_zero_num(df_1['a_time_order_resi_s_a'])
    df_1['p_seq_order_coef_bts_a'] = df_1['p_seq_order_coef_b_a'] / replace_zero_num(df_1['p_seq_order_coef_s_a'])
    df_1['p_seq_order_resi_bts_a'] = df_1['p_seq_order_resi_b_a'] / replace_zero_num(df_1['p_seq_order_resi_s_a'])
    df_1['a_seq_order_coef_bts_a'] = df_1['a_seq_order_coef_b_a'] / replace_zero_num(df_1['a_seq_order_coef_s_a'])
    df_1['a_seq_order_resi_bts_a'] = df_1['a_seq_order_resi_b_a'] / replace_zero_num(df_1['a_seq_order_resi_s_a'])
    return df_1


def ft_regoc_931(temp_order_data, trunc_time):
    trunc_time_hour = int(trunc_time.split(':')[0])
    trunc_time_minute = int(trunc_time.split(':')[1])
    temp_order_data_c = temp_order_data.between_time('9:30', trunc_time)
    temp_order_data_c['time_norm'] = [time_norm(i,
        start_time=pd.Timestamp(i_date.year, i_date.month, i_date.day, 9, 30),
        end_time=pd.Timestamp(i_date.year, i_date.month, i_date.day, trunc_time_hour, trunc_time_minute)) for i
        in temp_order_data_c.index]
    temp_order_data_c_b = temp_order_data_c[temp_order_data_c['OrderBSFlag'] == 1]
    temp_order_data_c_s = temp_order_data_c[temp_order_data_c['OrderBSFlag'] == 2]

    time_norm_t = temp_order_data_c.groupby('time_norm')[['time_norm']].first()
    amount_norm_t = temp_order_data_c.groupby('time_norm')[['OrderMoney']].sum()
    price_norm_t = (amount_norm_t / temp_order_data_c.groupby('time_norm')[['OrderQty']].sum().values) / temp_preclose
    temp_p1 = LinearRegression().fit(time_norm_t, price_norm_t)
    temp_a1 = LinearRegression().fit(time_norm_t, amount_norm_t)
    temp_p2 = LinearRegression().fit(temp_order_data_c[['OrderNI_adj']], temp_order_data_c[['price_norm']])
    temp_a2 = LinearRegression().fit(temp_order_data_c[['OrderNI_adj']], temp_order_data_c[['OrderMoney']])
    df_1['p_time_order_coef_c'] = temp_p1.coef_[0][0]
    df_1['p_time_order_resi_c'] = get_residual(temp_p1, time_norm_t, price_norm_t).std().values[0]
    df_1['a_time_order_coef_c'] = temp_a1.coef_[0][0]
    df_1['a_time_order_resi_c'] = get_residual(temp_a1, time_norm_t, amount_norm_t).std().values[0]
    df_1['p_seq_order_coef_c'] = temp_p2.coef_[0][0]
    df_1['p_seq_order_resi_c'] = \
        get_residual(temp_p2, temp_order_data_c[['OrderNI_adj']], temp_order_data_c[['price_norm']]).std().values[0]
    df_1['a_seq_order_coef_c'] = temp_a2.coef_[0][0]
    df_1['a_seq_order_resi_c'] = \
        get_residual(temp_a2, temp_order_data_c[['OrderNI_adj']], temp_order_data_c[['OrderMoney']]).std().values[0]

    temp_order_data_c_b = temp_order_data_c[temp_order_data_c['OrderBSFlag'] == 1]
    temp_order_data_c_s = temp_order_data_c[temp_order_data_c['OrderBSFlag'] == 2]

    time_norm_t_b = temp_order_data_c_b.groupby('time_norm')[['time_norm']].first()
    amount_norm_t_b = temp_order_data_c_b.groupby('time_norm')[['OrderMoney']].sum()
    price_norm_t_b = (amount_norm_t_b / temp_order_data_c_b.groupby('time_norm')[
        ['OrderQty']].sum().values) / temp_preclose
    temp_p5 = LinearRegression().fit(time_norm_t_b, price_norm_t_b)
    temp_a5 = LinearRegression().fit(time_norm_t_b, amount_norm_t_b)
    temp_p6 = LinearRegression().fit(temp_order_data_c_b[['OrderNI_adj']], temp_order_data_c_b[['price_norm']])
    temp_a6 = LinearRegression().fit(temp_order_data_c_b[['OrderNI_adj']], temp_order_data_c_b[['OrderMoney']])
    df_1['p_time_order_coef_b_c'] = temp_p5.coef_[0][0]
    df_1['p_time_order_resi_b_c'] = get_residual(temp_p5, time_norm_t_b, price_norm_t_b).std().values[0]
    df_1['a_time_order_coef_b_c'] = temp_a5.coef_[0][0]
    df_1['a_time_order_resi_b_c'] = get_residual(temp_a5, time_norm_t_b, amount_norm_t_b).std().values[0]
    df_1['p_seq_order_coef_b_c'] = temp_p6.coef_[0][0]
    df_1['p_seq_order_resi_b_c'] = \
        get_residual(temp_p6, temp_order_data_c_b[['OrderNI_adj']], temp_order_data_c_b[['price_norm']]).std().values[0]
    df_1['a_seq_order_coef_b_c'] = temp_a6.coef_[0][0]
    df_1['a_seq_order_resi_b_c'] = \
        get_residual(temp_a6, temp_order_data_c_b[['OrderNI_adj']], temp_order_data_c_b[['OrderMoney']]).std().values[0]

    time_norm_t_s = temp_order_data_c_s.groupby('time_norm')[['time_norm']].first()
    amount_norm_t_s = temp_order_data_c_s.groupby('time_norm')[['OrderMoney']].sum()
    price_norm_t_s = (amount_norm_t_s / temp_order_data_c_s.groupby('time_norm')[
        ['OrderQty']].sum().values) / temp_preclose
    temp_p5 = LinearRegression().fit(time_norm_t_s, price_norm_t_s)
    temp_a5 = LinearRegression().fit(time_norm_t_s, amount_norm_t_s)
    temp_p6 = LinearRegression().fit(temp_order_data_c_s[['OrderNI_adj']], temp_order_data_c_s[['price_norm']])
    temp_a6 = LinearRegression().fit(temp_order_data_c_s[['OrderNI_adj']], temp_order_data_c_s[['OrderMoney']])
    df_1['p_time_order_coef_s_c'] = temp_p5.coef_[0][0]
    df_1['p_time_order_resi_s_c'] = get_residual(temp_p5, time_norm_t_s, price_norm_t_s).std().values[0]
    df_1['a_time_order_coef_s_c'] = temp_a5.coef_[0][0]
    df_1['a_time_order_resi_s_c'] = get_residual(temp_a5, time_norm_t_s, amount_norm_t_s).std().values[0]
    df_1['p_seq_order_coef_s_c'] = temp_p6.coef_[0][0]
    df_1['p_seq_order_resi_s_c'] = \
        get_residual(temp_p6, temp_order_data_c_s[['OrderNI_adj']], temp_order_data_c_s[['price_norm']]).std().values[0]
    df_1['a_seq_order_coef_s_c'] = temp_a6.coef_[0][0]
    df_1['a_seq_order_resi_s_c'] = \
        get_residual(temp_a6, temp_order_data_c_s[['OrderNI_adj']], temp_order_data_c_s[['OrderMoney']]).std().values[0]

    df_1['p_time_order_coef_bts_c'] = df_1['p_time_order_coef_b_c'] / replace_zero_num(df_1['p_time_order_coef_s_c'])
    df_1['p_time_order_resi_bts_c'] = df_1['p_time_order_resi_b_c'] / replace_zero_num(df_1['p_time_order_resi_s_c'])
    df_1['a_time_order_coef_bts_c'] = df_1['a_time_order_coef_b_c'] / replace_zero_num(df_1['a_time_order_coef_s_c'])
    df_1['a_time_order_resi_bts_c'] = df_1['a_time_order_resi_b_c'] / replace_zero_num(df_1['a_time_order_resi_s_c'])
    df_1['p_seq_order_coef_bts_c'] = df_1['p_seq_order_coef_b_c'] / replace_zero_num(df_1['p_seq_order_coef_s_c'])
    df_1['p_seq_order_resi_bts_c'] = df_1['p_seq_order_resi_b_c'] / replace_zero_num(df_1['p_seq_order_resi_s_c'])
    df_1['a_seq_order_coef_bts_c'] = df_1['a_seq_order_coef_b_c'] / replace_zero_num(df_1['a_seq_order_coef_s_c'])
    df_1['a_seq_order_resi_bts_c'] = df_1['a_seq_order_resi_b_c'] / replace_zero_num(df_1['a_seq_order_resi_s_c'])
    return df_1


def ft_lym_931(temp_order_data, temp_withd_data, temp_stock_data):
    trunc_time_hour = int(trunc_time.split(':')[0])
    trunc_time_minute = int(trunc_time.split(':')[1])
    temp_order_data_last1min = temp_order_data.between_time(f'{trunc_time_hour}:{trunc_time_minute-1}', trunc_time, include_end=False)
    temp_stock_data_last1min = temp_stock_data.between_time(f'{trunc_time_hour}:{trunc_time_minute-1}', trunc_time, include_end=False)
    temp_stock_data_auction = temp_stock_data.between_time('9:15', '9:25', include_end=False)
    temp_order_data_b = temp_order_data[temp_order_data['OrderBSFlag'] == 1]
    temp_order_data_s = temp_order_data[temp_order_data['OrderBSFlag'] == 2]
    temp_order_data_last1min_b = temp_order_data_last1min[temp_order_data_last1min['OrderBSFlag'] == 1]
    temp_order_data_last1min_s = temp_order_data_last1min[temp_order_data_last1min['OrderBSFlag'] == 2]
    temp_stock_data_last = temp_stock_data.iloc[-1]

    df_1['i1'] = temp_stock_data_last['TotalBidQty'] * temp_stock_data_last['WeightedAvgBidPx'] / replace_zero_num(
        temp_stock_data_last['TotalBidQty'] * temp_stock_data_last['WeightedAvgBidPx'] +
        temp_stock_data_last['TotalOfferQty'] * temp_stock_data_last['WeightedAvgOfferPx'])
    df_1['i2'] = temp_stock_data_last['LastPx'] / temp_preclose - 1
    df_1['i3'] = temp_trans_data['TradeBuyNo'].unique().shape[0] / replace_zero_num(temp_trans_data.shape[0])
    df_1['i4'] = temp_trans_data['TradeSellNo'].unique().shape[0] / replace_zero_num(temp_trans_data.shape[0])
    df_1['i6'] = temp_trans_data['TradeQty'].mean() / replace_zero_num(temp_trans_data['TradeQty'].median())
    temp_1 = temp_trans_data.groupby('TradeBuyNo')['TradeQty'].sum()
    temp_2 = temp_trans_data.groupby('TradeSellNo')['TradeQty'].sum()
    df_1['i7'] = temp_1.nlargest(temp_1.shape[0] // 10).sum() / replace_zero_num(temp_1.sum())
    df_1['i8'] = temp_2.nlargest(temp_2.shape[0] // 10).sum() / replace_zero_num(temp_2.sum())
    df_1['i10'] = temp_trans_data['TradeIndex'].corr(temp_trans_data['TradeBuyNo'])
    df_1['i11'] = temp_trans_data['TradeIndex'].corr(temp_trans_data['TradeSellNo'])
    df_1['i13'] = temp_order_data_b['OrderPrice'].corr(temp_order_data_b['OrderQty'])
    df_1['i14'] = temp_order_data_s['OrderPrice'].corr(temp_order_data_s['OrderQty'])
    df_1['i15'] = temp_order_data_b['time_int'].corr(temp_order_data_b['OrderPrice'])
    df_1['i16'] = temp_order_data_s['time_int'].corr(temp_order_data_s['OrderPrice'])
    df_1['i17'] = temp_order_data_b['time_int'].corr(temp_order_data_b['OrderMoney'])
    df_1['i18'] = temp_order_data_s['time_int'].corr(temp_order_data_s['OrderMoney'])
    df_1['i19'] = temp_order_data_b.groupby('dt')['OrderMoney'].sum().corr(
        temp_order_data_b.groupby('dt')['time_int'].first())
    df_1['i20'] = temp_order_data_s.groupby('dt')['OrderMoney'].sum().corr(
        temp_order_data_s.groupby('dt')['time_int'].first())
    df_1['i35'] = (temp_order_data_last1min_b['OrderPrice'] / temp_preclose - 1).std()
    df_1['i36'] = (temp_order_data_last1min_s['OrderPrice'] / temp_preclose - 1).std()
    df_1['i37'] = (temp_order_data_last1min['OrderPrice'] / temp_preclose - 1).std()
    df_1['i38'] = (temp_order_data_b['OrderPrice'] / temp_preclose - 1).skew()
    df_1['i39'] = (temp_order_data_s['OrderPrice'] / temp_preclose - 1).skew()
    df_1['i40'] = (temp_order_data['OrderPrice'] / temp_preclose - 1).skew()
    df_1['i41'] = (temp_order_data_last1min_b['OrderPrice'] / temp_preclose - 1).skew()
    df_1['i42'] = (temp_order_data_last1min_s['OrderPrice'] / temp_preclose - 1).skew()
    df_1['i43'] = (temp_order_data_b['OrderPrice'] / temp_preclose - 1).kurt()
    df_1['i44'] = (temp_order_data_s['OrderPrice'] / temp_preclose - 1).kurt()
    df_1['i45'] = (temp_order_data['OrderPrice'] / temp_preclose - 1).kurt()
    df_1['i46'] = (temp_order_data_last1min_b['OrderPrice'] / temp_preclose - 1).kurt()
    df_1['i47'] = (temp_order_data_last1min_s['OrderPrice'] / temp_preclose - 1).kurt()
    df_1['i48'] = (temp_order_data_last1min['OrderPrice'] / temp_preclose - 1).kurt()
    df_1['i50'] = (temp_stock_data_last1min['TotalBidQty'] > temp_stock_data_last1min['TotalOfferQty']).sum() / \
                  replace_zero_num(temp_stock_data_last1min.shape[0])
    df_1['i55'] = replace_zero(temp_stock_data_auction['Buy1Price']).corr(temp_stock_data_auction['Buy1OrderQty'])
    df_1['i56'] = temp_stock_data_last['TotalValueTrade'] / replace_zero_num(temp_stock_data_last['NumTrades'])
    df_1['i57'] = temp_trans_data['TradeMoney'].sum() / replace_zero_num(
        temp_trans_data['TradeBuyNo'].unique().shape[0])
    df_1['i58'] = temp_trans_data['TradeMoney'].sum() / replace_zero_num(
        temp_trans_data['TradeSellNo'].unique().shape[0])
    df_1['i59'] = np.nansum([temp_stock_data_last[f'Buy{i}Price'] * temp_stock_data_last[f'Buy{i}OrderQty'] for i in
                             range(1, 6)]) / replace_zero_num(np.nansum(
        [temp_stock_data_last[f'Buy{i}Price'] * temp_stock_data_last[f'Buy{i}OrderQty'] for i in
         range(1, 6)]) + np.nansum(
        [temp_stock_data_last[f'Sell{i}Price'] * temp_stock_data_last[f'Sell{i}OrderQty'] for i in range(1, 6)]))
    df_1['i60'] = np.nansum([temp_stock_data_last[f'Buy{i}Price'] * temp_stock_data_last[f'Buy{i}OrderQty'] for i in
                             range(1, 11)]) / replace_zero_num(np.nansum(
        [temp_stock_data_last[f'Buy{i}Price'] * temp_stock_data_last[f'Buy{i}OrderQty'] for i in
         range(1, 11)]) + np.nansum(
        [temp_stock_data_last[f'Sell{i}Price'] * temp_stock_data_last[f'Sell{i}OrderQty'] for i in range(1, 11)]))
    df_1['i61'] = (temp_stock_data_last['Buy5Price'] - temp_stock_data_last['Sell5Price']) / replace_zero_num(
        temp_stock_data_last['Buy5Price'])
    df_1['i62'] = (temp_stock_data_last['Buy10Price'] - temp_stock_data_last['Sell10Price']) / replace_zero_num(
        temp_stock_data_last['Buy10Price'])
    df_1['i64'] = temp_stock_data_last1min['LastPx'].max() / replace_zero(temp_stock_data_last1min['LastPx']).min() - 1
    df_1['i66'] = temp_stock_data_last1min['LastPx'].max() / replace_zero(temp_stock_data_last1min['LastPx']).iloc[
        0] - 1
    df_1['i67'] = temp_stock_data_last1min['LastPx'].min() / replace_zero(temp_stock_data_last1min['LastPx']).iloc[
        0] - 1
    df_1['i69'] = temp_stock_data_last1min['LastPx'].max() / replace_zero(temp_trans_data['TradePrice']).dropna().iloc[
        0] - 1 if replace_zero(temp_trans_data['TradePrice']).count() > 0 else np.nan
    df_1['i70'] = temp_stock_data_last1min['LastPx'].min() / replace_zero(temp_trans_data['TradePrice']).dropna().iloc[
        0] - 1 if replace_zero(temp_trans_data['TradePrice']).count() > 0 else np.nan
    df_1['i72'] = temp_withd_data['OrderQty'].sum() / replace_zero_num(temp_order_data['OrderQty'].sum())
    df_1['i73'] = temp_withd_data[temp_withd_data['OrderBSFlag'] == 1]['OrderQty'].sum() / replace_zero_num(
        temp_order_data_b['OrderQty'].sum())
    df_1['i74'] = temp_withd_data[temp_withd_data['OrderBSFlag'] == 2]['OrderQty'].sum() / replace_zero_num(
        temp_order_data_s['OrderQty'].sum())

    temp_3 = pd.merge(temp_order_data_last1min[['OrderPrice', 'OrderQty', 'OrderBSFlag']], temp_stock_data_last1min[['LastPx']],
                      left_index=True, right_index=True, how='outer')
    temp_3['LastPx'] = temp_3['LastPx'].fillna(method='ffill')
    temp_3_1 = temp_3[(temp_3['OrderBSFlag'] == 1) & (temp_3['OrderPrice'] > temp_3['LastPx'])]
    temp_3_2 = temp_3[(temp_3['OrderBSFlag'] == 2) & (temp_3['OrderPrice'] < temp_3['LastPx'])]
    df_1['i75'] = temp_3_1['OrderQty'].sum() / replace_zero_num(temp_3_1['OrderQty'].sum() + temp_3_2['OrderQty'].sum())
    df_1['i76'] = (temp_3_1['OrderPrice'] * temp_3_1['OrderQty']).sum() / replace_zero_num(
        (temp_3_1['OrderPrice'] * temp_3_1['OrderQty']).sum() + (temp_3_2['OrderPrice'] * temp_3_2['OrderQty']).sum())
    df_1['i77'] = ((temp_3_1['OrderPrice'] - temp_3_1['LastPx']) * temp_3_1['OrderQty']).sum() / replace_zero_num(
        ((temp_3_1['OrderPrice'] - temp_3_1['LastPx']) * temp_3_1['OrderQty']).sum() + (
                (temp_3_2['OrderPrice'] - temp_3_2['LastPx']) * temp_3_2['OrderQty']).sum())
    df_1['i78'] = temp_trans_data['TradeMoney'].sum() / replace_zero_num(temp_1.shape[0])
    df_1['i79'] = temp_trans_data['TradeMoney'].sum() / replace_zero_num(temp_2.shape[0])
    df_1['i80'] = (temp_stock_data_last1min['LastPx'].iloc[-1] - temp_stock_data_last1min['LastPx'].iloc[
        0]) / temp_preclose
    df_1['i82'] = temp_trans_data[temp_trans_data['TradeBSFlag'] == 1]['TradeMoney'].sum() / replace_zero_num(
        temp_trans_data['TradeMoney'].sum())
    df_1['i83'] = ((temp_trans_data['TradeBuyNo'] - temp_trans_data['TradeSellNo']) * temp_trans_data[
        'TradeQty']).sum() / replace_zero_num(temp_trans_data['TradeQty'].sum())
    df_1['i85'] = temp_order_data_b[temp_order_data_b['OrderPrice'] == temp_limit]['OrderQty'].sum() / \
                  replace_zero_num(temp_order_data_b['OrderQty'].sum())
    df_1['i86'] = temp_order_data_s[temp_order_data_s['OrderPrice'] == temp_stopping]['OrderQty'].sum() / \
                  replace_zero_num(temp_order_data_s['OrderQty'].sum())

    df_1['j1'] = temp_stock_data_last['LastPx'] / replace_zero(
        temp_trans_data['TradePrice']).dropna().iloc[0] - 1 if replace_zero(
        temp_trans_data['TradePrice']).count() > 0 else np.nan
    df_1['j2'] = temp_order_data['OrderPrice'].corr(temp_order_data['OrderQty'])
    df_1['j3'] = temp_order_data['time_int'].corr(temp_order_data['OrderPrice'])
    df_1['j4'] = temp_order_data['time_int'].corr(temp_order_data['OrderQty'])
    df_1['j5'] = temp_order_data.groupby('dt')['OrderQty'].sum().corr(temp_order_data.groupby('dt')['time_int'].first())
    df_1['j6'] = temp_order_data.groupby('dt')['OrderPrice'].mean().corr(
        temp_order_data.groupby('dt')['time_int'].first())
    df_1['j7'] = temp_order_data_b.groupby('dt')['OrderPrice'].mean().corr(
        temp_order_data_b.groupby('dt')['time_int'].first())
    df_1['j8'] = temp_order_data_s.groupby('dt')['OrderPrice'].mean().corr(
        temp_order_data_s.groupby('dt')['time_int'].first())
    df_1['j9'] = (temp_order_data_b['OrderPrice'] / temp_preclose - 1).std()
    df_1['j10'] = (temp_order_data_s['OrderPrice'] / temp_preclose - 1).std()
    df_1['j11'] = (temp_order_data['OrderPrice'] / temp_preclose - 1).std()
    df_1['j12'] = (temp_order_data_last1min['OrderPrice'] / temp_preclose - 1).skew()
    df_1['j13'] = ts_pct_change(temp_stock_data_last1min['LastPx'], 1).std()
    df_1['j14'] = ts_pct_change(temp_stock_data_last1min['LastPx'], 1).skew()
    df_1['j15'] = ts_pct_change(temp_stock_data_last1min['LastPx'], 1).kurt()
    df_1['j16'] = ts_pct_change(replace_zero(temp_stock_data_auction['Buy1Price']), 1).std()
    df_1['j17'] = ts_pct_change(replace_zero(temp_stock_data_auction['Buy1Price']), 1).skew()
    df_1['j18'] = ts_pct_change(replace_zero(temp_stock_data_auction['Buy1Price']), 1).kurt()
    df_1['j19'] = (temp_stock_data_last1min['Buy1OrderQty'] > temp_stock_data_last1min['Sell1OrderQty']).sum() / \
                  replace_zero_num(temp_stock_data_last1min.shape[0])
    df_1['j20'] = ts_pct_change(temp_stock_data_last1min['LastPx'], 1).corr(temp_stock_data_last1min['volume'])
    df_1['j21'] = (temp_stock_data_last['Buy1Price'] - temp_stock_data_last['Sell1Price']) / replace_zero_num(
        temp_stock_data_last['Buy1Price'])
    df_1['j22'] = temp_withd_data[temp_withd_data['OrderBSFlag'] == 1]['OrderQty'].sum() / replace_zero_num(
        temp_withd_data['OrderQty'].sum())
    return df_1


def ft_regtc_931(temp_trans_data, trunc_time):
    trunc_time_hour = int(trunc_time.split(':')[0])
    trunc_time_minute = int(trunc_time.split(':')[1])
    temp_trans_data_c = temp_trans_data.between_time('9:30', trunc_time, include_end=False)
    temp_trans_data_c['time_norm_c'] = [
        time_norm(i,
                  start_time=pd.Timestamp(i_date.year, i_date.month, i_date.day, 9, 30),
                  end_time=pd.Timestamp(i_date.year, i_date.month, i_date.day, trunc_time_hour, trunc_time_minute))
        for i in temp_trans_data_c.index]


    temp_p1 = LinearRegression().fit(temp_trans_data_c[['time_norm_c']], temp_trans_data_c[['price_norm']])
    temp_a1 = LinearRegression().fit(temp_trans_data_c[['time_norm_c']], temp_trans_data_c[['TradeMoney']])
    temp_p3 = LinearRegression().fit(temp_trans_data_c[['TradeIndex_adj']], temp_trans_data_c[['price_norm']])
    temp_a3 = LinearRegression().fit(temp_trans_data_c[['TradeIndex_adj']], temp_trans_data_c[['TradeMoney']])

    df_1['p_time_trans_coef_c'] = temp_p1.coef_[0][0]
    df_1['p_time_trans_resi_c'] = \
        get_residual(temp_p1, temp_trans_data_c[['time_norm_c']], temp_trans_data_c[['price_norm']]).std().values[0]
    df_1['a_time_trans_coef_c'] = temp_a1.coef_[0][0]
    df_1['a_time_trans_resi_c'] = \
        get_residual(temp_a1, temp_trans_data_c[['time_norm_c']], temp_trans_data_c[['TradeMoney']]).std().values[0]
    df_1['p_seq_trans_coef_c'] = temp_p3.coef_[0][0]
    df_1['p_seq_trans_resi_c'] = \
        get_residual(temp_p3, temp_trans_data_c[['TradeIndex_adj']], temp_trans_data_c[['price_norm']]).std().values[0]
    df_1['a_seq_trans_coef_c'] = temp_a3.coef_[0][0]
    df_1['a_seq_trans_resi_c'] = \
        get_residual(temp_a3, temp_trans_data_c[['TradeIndex_adj']], temp_trans_data_c[['TradeMoney']]).std().values[0]

    # 以下是groupby的结果
    time_norm_c_t = temp_trans_data_c.groupby('time_norm_c')[['time_norm_c']].first()
    amount_norm_c_t = temp_trans_data_c.groupby('time_norm_c')[['TradeMoney']].sum()
    price_norm_c_t = (amount_norm_c_t / temp_trans_data_c.groupby('time_norm_c')[
        ['TradeQty']].sum().values) / temp_preclose
    time_norm_c_b = temp_trans_data_c.groupby('TradeBuyNo_adj')[['TradeBuyNo_adj']].first()
    amount_norm_c_b = temp_trans_data_c.groupby('TradeBuyNo_adj')[['TradeMoney']].sum()
    price_norm_c_b = (amount_norm_c_b / temp_trans_data_c.groupby('TradeBuyNo_adj')[
        ['TradeQty']].sum().values) / temp_preclose
    time_norm_c_s = temp_trans_data_c.groupby('TradeSellNo_adj')[['TradeSellNo_adj']].first()
    amount_norm_c_s = temp_trans_data_c.groupby('TradeSellNo_adj')[['TradeMoney']].sum()
    price_norm_c_s = (amount_norm_c_s / temp_trans_data_c.groupby('TradeSellNo_adj')[
        ['TradeQty']].sum().values) / temp_preclose


    temp_p5 = LinearRegression().fit(time_norm_c_t, price_norm_c_t)
    temp_p6 = LinearRegression().fit(time_norm_c_b, price_norm_c_b)
    temp_p7 = LinearRegression().fit(time_norm_c_s, price_norm_c_s)
    temp_a5 = LinearRegression().fit(time_norm_c_t, amount_norm_c_t)
    temp_a6 = LinearRegression().fit(time_norm_c_b, amount_norm_c_b)
    temp_a7 = LinearRegression().fit(time_norm_c_s, amount_norm_c_s)

    df_1['p_time_g_trans_coef_c'] = temp_p5.coef_[0][0]
    df_1['p_seq_gb_trans_coef_c'] = temp_p6.coef_[0][0]
    df_1['p_seq_gs_trans_coef_c'] = temp_p7.coef_[0][0]
    df_1['p_time_g_trans_resi_c'] = get_residual(temp_p5, time_norm_c_t, price_norm_c_t).std().values[0]
    df_1['p_seq_gb_trans_resi_c'] = get_residual(temp_p6, time_norm_c_b, price_norm_c_b).std().values[0]
    df_1['p_seq_gs_trans_resi_c'] = get_residual(temp_p7, time_norm_c_s, price_norm_c_s).std().values[0]
    df_1['a_time_g_trans_coef_c'] = temp_a5.coef_[0][0]
    df_1['a_seq_gb_trans_coef_c'] = temp_a6.coef_[0][0]
    df_1['a_seq_gs_trans_coef_c'] = temp_a7.coef_[0][0]
    df_1['a_time_g_trans_resi_c'] = get_residual(temp_a5, time_norm_c_t, amount_norm_c_t).std().values[0]
    df_1['a_seq_gb_trans_resi_c'] = get_residual(temp_a6, time_norm_c_b, amount_norm_c_b).std().values[0]
    df_1['a_seq_gs_trans_resi_c'] = get_residual(temp_a7, time_norm_c_s, amount_norm_c_s).std().values[0]
    return df_1


def ft_regtl_931(temp_trans_data, trunc_time):
    trunc_time_hour = int(trunc_time.split(':')[0])
    trunc_time_minute = int(trunc_time.split(':')[1])
    temp_trans_data_l = temp_trans_data.between_time(f'{trunc_time_hour}:{trunc_time_minute - 1}', trunc_time, include_end=False)
    temp_trans_data_l['time_norm_l'] = [
        time_norm(i,
                  start_time=pd.Timestamp(i_date.year, i_date.month, i_date.day, trunc_time_hour, trunc_time_minute - 1),
                  end_time=pd.Timestamp(i_date.year, i_date.month, i_date.day, trunc_time_hour, trunc_time_minute))
        for i in temp_trans_data_l.index]


    temp_p2 = LinearRegression().fit(temp_trans_data_l[['time_norm_l']], temp_trans_data_l[['price_norm']])
    temp_a2 = LinearRegression().fit(temp_trans_data_l[['time_norm_l']], temp_trans_data_l[['TradeMoney']])
    temp_p4 = LinearRegression().fit(temp_trans_data_l[['TradeIndex_adj']], temp_trans_data_l[['price_norm']])
    temp_a4 = LinearRegression().fit(temp_trans_data_l[['TradeIndex_adj']], temp_trans_data_l[['TradeMoney']])

    df_1['p_time_trans_coef_l'] = temp_p2.coef_[0][0]
    df_1['p_time_trans_resi_l'] = \
        get_residual(temp_p2, temp_trans_data_l[['time_norm_l']], temp_trans_data_l[['price_norm']]).std().values[0]
    df_1['a_time_trans_coef_l'] = temp_a2.coef_[0][0]
    df_1['a_time_trans_resi_l'] = \
        get_residual(temp_a2, temp_trans_data_l[['time_norm_l']], temp_trans_data_l[['TradeMoney']]).std().values[0]
    df_1['p_seq_trans_coef_l'] = temp_p4.coef_[0][0]
    df_1['p_seq_trans_resi_l'] = \
        get_residual(temp_p4, temp_trans_data_l[['TradeIndex_adj']], temp_trans_data_l[['price_norm']]).std().values[0]
    df_1['a_seq_trans_coef_l'] = temp_a4.coef_[0][0]
    df_1['a_seq_trans_resi_l'] = \
        get_residual(temp_a4, temp_trans_data_l[['TradeIndex_adj']], temp_trans_data_l[['TradeMoney']]).std().values[0]

    # 以下是groupby的结果
    time_norm_l_t = temp_trans_data_l.groupby('time_norm_l')[['time_norm_l']].first()
    amount_norm_l_t = temp_trans_data_l.groupby('time_norm_l')[['TradeMoney']].sum()
    price_norm_l_t = (amount_norm_l_t / temp_trans_data_l.groupby('time_norm_l')[
        ['TradeQty']].sum().values) / temp_preclose
    time_norm_l_b = temp_trans_data_l.groupby('TradeBuyNo_adj')[['TradeBuyNo_adj']].first()
    amount_norm_l_b = temp_trans_data_l.groupby('TradeBuyNo_adj')[['TradeMoney']].sum()
    price_norm_l_b = (amount_norm_l_b / temp_trans_data_l.groupby('TradeBuyNo_adj')[
        ['TradeQty']].sum().values) / temp_preclose
    time_norm_l_s = temp_trans_data_l.groupby('TradeSellNo_adj')[['TradeSellNo_adj']].first()
    amount_norm_l_s = temp_trans_data_l.groupby('TradeSellNo_adj')[['TradeMoney']].sum()
    price_norm_l_s = (amount_norm_l_s / temp_trans_data_l.groupby('TradeSellNo_adj')[
        ['TradeQty']].sum().values) / temp_preclose

    temp_p8 = LinearRegression().fit(time_norm_l_t, price_norm_l_t)
    temp_p9 = LinearRegression().fit(time_norm_l_b, price_norm_l_b)
    temp_p10 = LinearRegression().fit(time_norm_l_s, price_norm_l_s)
    temp_a8 = LinearRegression().fit(time_norm_l_t, amount_norm_l_t)
    temp_a9 = LinearRegression().fit(time_norm_l_b, amount_norm_l_b)
    temp_a10 = LinearRegression().fit(time_norm_l_s, amount_norm_l_s)

    df_1['p_time_g_trans_coef_l'] = temp_p8.coef_[0][0]
    df_1['p_seq_gb_trans_coef_l'] = temp_p9.coef_[0][0]
    df_1['p_seq_gs_trans_coef_l'] = temp_p10.coef_[0][0]
    df_1['p_time_g_trans_resi_l'] = get_residual(temp_p8, time_norm_l_t, price_norm_l_t).std().values[0]
    df_1['p_seq_gb_trans_resi_l'] = get_residual(temp_p9, time_norm_l_b, price_norm_l_b).std().values[0]
    df_1['p_seq_gs_trans_resi_l'] = get_residual(temp_p10, time_norm_l_s, price_norm_l_s).std().values[0]
    df_1['a_time_g_trans_coef_l'] = temp_a8.coef_[0][0]
    df_1['a_seq_gb_trans_coef_l'] = temp_a9.coef_[0][0]
    df_1['a_seq_gs_trans_coef_l'] = temp_a10.coef_[0][0]
    df_1['a_time_g_trans_resi_l'] = get_residual(temp_a8, time_norm_l_t, amount_norm_l_t).std().values[0]
    df_1['a_seq_gb_trans_resi_l'] = get_residual(temp_a9, time_norm_l_b, amount_norm_l_b).std().values[0]
    df_1['a_seq_gs_trans_resi_l'] = get_residual(temp_a10, time_norm_l_s, amount_norm_l_s).std().values[0]
    return df_1


def func_931(params, daily_data, trunc_time='9:31', bms_threshold=(4e4, 2e5)):
    df_1 = pd.Series(dtype='object')

    i_date = params[0]
    i_stk = params[1]
    i_date_str = i_date.strftime('%Y%m%d')


    temp_order_data = get_level2_data(i_date_str, i_stk, 'Order', mode='other', end_time_str=trunc_time)
    temp_trans_data = get_level2_data(i_date_str, i_stk, 'Transaction', mode='other', end_time_str=trunc_time)
    temp_stock_data = get_level2_data(i_date_str, i_stk, 'Stock', mode='other', end_time_str=trunc_time)
    temp_order_raw_data = get_level2_data(i_date_str, i_stk, 'Order_RAW', mode='other', end_time_str=trunc_time)
    temp_order_data = market_order_handler(temp_order_data)
    temp_withd_data = get_cancel_data(temp_order_data, temp_order_raw_data, temp_trans_data, suffix=i_stk[-2:])
    temp_trans_data = temp_trans_data[temp_trans_data['TradeType'] == 0]
    temp_daily_data = daily_data.loc[params]
    
    temp_order_data['time_int'] = [int(i.strftime('%H%M%S%f')) for i in temp_order_data.index]
    temp_order_data['time_norm'] = [time_norm(i,
        start_time=pd.Timestamp(i_date.year, i_date.month, i_date.day, 9, 15),
        end_time=pd.Timestamp(i_date.year, i_date.month, i_date.day, trunc_time_hour, trunc_time_minute)) for i
        in temp_order_data.index]
    temp_order_data['price_norm'] = temp_order_data['OrderPrice'] / temp_preclose
    temp_order_data['OrderNI_adj'] = temp_order_data['OrderNI_adj'] / 1e6
    temp_stock_data['time_int'] = [int(i.strftime('%H%M%S%f')) for i in temp_stock_data.index]
    temp_stock_data['amount'] = temp_stock_data['TotalValueTrade'].diff()
    temp_stock_data['volume'] = temp_stock_data['TotalVolumeTrade'].diff()
    temp_stock_data['ret'] = temp_stock_data['LastPx'].pct_change()
    temp_trans_data['TradeIndex_adj'] = temp_trans_data['TradeIndex'] / 1e6  # 为了让斜率的量纲不至于太小
    temp_trans_data['TradeBuyNo_adj'] = temp_trans_data['TradeBuyNo'] / 1e6
    temp_trans_data['TradeSellNo_adj'] = temp_trans_data['TradeSellNo'] / 1e6
    temp_trans_data['price_norm'] = temp_trans_data['TradePrice'] / temp_preclose


    ft_1 = ft_1_931(temp_order_data, temp_trans_data, temp_stock_data, temp_withd_data)
    ft_4o = ft_4o_931(temp_order_data, temp_trans_data, temp_withd_data)
    ft_4t = ft_4t_931(temp_trans_data)
    ft_5 = ft_5_931(temp_stock_data, temp_daily_data, trunc_time)
    ft_regoa = ft_regoa_931(temp_order_data)
    ft_regoc = ft_regoc_931(temp_order_data, trunc_time)
    ft_lym = ft_lym_931(temp_order_data, temp_withd_data, temp_stock_data)
    ft_regtc = ft_regtc_931(temp_trans_data, trunc_time)   
    df_result = pd.concat([ft_1, ft_4o, ft_4t, ft_5, ft_regoa, ft_regoc_931, ft_lym, ft_regtc], axis=1)

    return df_result



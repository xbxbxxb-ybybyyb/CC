class TickBackTest:
    """
    股指期货tick撮合成交
    """

    def __init__(self, order_situation, capital_limit):
        """
        类初始化
        :param order_situation: dataframe
            等待撮合的挂单数据，需包含如下信息：时间，状态（买入开仓，卖出平仓，卖出开仓，买入平仓），价格，数量
        :param capital_limit: float
            资金上限
        """
        """
        一些问题：没成交的单子怎么处理（加个撤单时间参数，挂单时间超过多少秒就撤单），是否留隔夜单
        """

    start_time = i_date + dt.time_delta(hours=start_deal_time1 // 1e4, minutes=(start_deal_time1 // 100) % 100,
                                        seconds=start_deal_time1 % 100)


def per_tick_trade(df_tick_raw, trade_df_tick, trade_list, trade_num):
    """
    对单根tick进行撮合
    :param df_tick_raw: pd.dataframe
        包含股指期货tick信息的dataframe
    :param trade_df_tick: pd.series
        进行遍历的那根tick
    :param trade_list: list
        存放交易结果的list
    :param trade_num: int
        待交易的股指期货合约张数
    :return: trade_list: list
        更新交易结果后的list
    :return: trade_num: int
        经过这一根tick撮合后剩余的待交易合约数量
    """
    trade_tick = trade_df_tick.name
    if trade_df_tick['Sell1OrderQty'] >= trade_num:
        trade_list.append([trade_tick, trade_df_tick['Sell1Price'], trade_num])
        df_tick_raw.loc[trade_tick, 'Sell1OrderQty'] -= trade_num
        trade_num = 0
        return trade_list, trade_num
    else:
        trade_list.append([trade_tick, trade_df_tick['Sell1Price'], trade_df_tick['Sell1OrderQty']])
        df_tick_raw.loc[trade_tick, 'Sell1OrderQty'] = 0
        trade_num = trade_num - trade_df_tick['Sell1OrderQty']
    if trade_df_tick['Sell2OrderQty'] >= trade_num:
        trade_list.append([trade_tick, trade_df_tick['Sell2Price'], trade_num])
        df_tick_raw.loc[trade_tick, 'Sell2OrderQty'] -= trade_num
        trade_num = 0
        return trade_list, trade_num
    else:
        trade_list.append([trade_tick, trade_df_tick['Sell2Price'], trade_df_tick['Sell2OrderQty']])
        df_tick_raw.loc[trade_tick, 'Sell2OrderQty'] = 0
        trade_num = trade_num - trade_df_tick['Sell2OrderQty']
    if trade_df_tick['Sell3OrderQty'] >= trade_num:
        trade_list.append([trade_tick, trade_df_tick['Sell3Price'], trade_num])
        df_tick_raw.loc[trade_tick, 'Sell3OrderQty'] -= trade_num
        trade_num = 0
        return trade_list, trade_num
    else:
        trade_list.append([trade_tick, trade_df_tick['Sell3Price'], trade_df_tick['Sell3OrderQty']])
        df_tick_raw.loc[trade_tick, 'Sell3OrderQty'] = 0
        trade_num = trade_num - trade_df_tick['Sell3OrderQty']
    if trade_df_tick['Sell4OrderQty'] >= trade_num:
        trade_list.append([trade_tick, trade_df_tick['Sell4Price'], trade_num])
        df_tick_raw.loc[trade_tick, 'Sell4OrderQty'] -= trade_num
        trade_num = 0
        return trade_list, trade_num
    else:
        trade_list.append([trade_tick, trade_df_tick['Sell4Price'], trade_df_tick['Sell4OrderQty']])
        df_tick_raw.loc[trade_tick, 'Sell4OrderQty'] = 0
        trade_num = trade_num - trade_df_tick['Sell4OrderQty']
    if trade_df_tick['Sell5OrderQty'] >= trade_num:
        trade_list.append([trade_tick, trade_df_tick['Sell5Price'], trade_num])
        df_tick_raw.loc[trade_tick, 'Sell5OrderQty'] -= trade_num
        trade_num = 0
        return trade_list, trade_num
    else:
        trade_list.append([trade_tick, trade_df_tick['Sell5Price'], trade_df_tick['Sell5OrderQty']])
        trade_num = trade_num - trade_df_tick['Sell5OrderQty']
        df_tick_raw.loc[trade_tick, 'Sell5OrderQty'] = 0
        return trade_list, trade_num


def daily_future_trade(df_tick, df_future):
    """
    根据当天的下单需求进行撮合
    :param df_tick: pd.dataframe
        包含股指期货tick信息的dataframe
    :param df_future: pd.dataframe
        包含股指期货下单需求的dataframe
    :return: trade_list: list
        包含交易结果后的list
    """
    trade_list = []
    time2_range = [(df_tick.index > i).tolist().index(1) for i in df_future.index]  # 得到每一笔待撮合交易的时间戳位于原始tick数据中的位置
    for i, i_num in enumerate(df_future['num']):
        df_tick_temp = df_tick.iloc[time2_range[i]:]
        j = 0
        while (i_num > 0) & (j < df_tick_temp.shape[0]):
            df_tick_temp1 = df_tick_temp.iloc[j]
            trade_list, i_num = per_tick_trade(df_tick, df_tick_temp1, trade_list, i_num)
            j = j + 1
    return trade_list
